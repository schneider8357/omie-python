"""
Cliente para a Omie API.

Documentação da API: https://developer.omie.com.br/service-list/
Uso:

>>> import omie
>>> api = omie.OmieClient(app_key, app_secret)
>>> res = api.get(omie.ListarEtapasPedido, {
...     "nPagina": 2,
...     "nRegPorPagina": 10,
... })
"""
import json

import requests
from cachetools import cachedmethod, TTLCache

import omie.methods
from omie.methods import OmieMethod
from omie.exceptions import OmieClientError, OmieAPIError
from omie.schemas import OmieSchema


# TODO: mode for always retry request: if it fails retry X times?
# or parse faultstring, get timestamp and schedule?
# TODO: make requests asynchronous
# TODO: test cachedmethod lock in simultaneous calls scenario

class OmieClient:
    """
    Cliente para a Omie API.

    É de EXTREMA IMPORTÂNCIA que os valores da app_key e app_secret NÃO sejam
    armazenados no seu código Python. Por gentileza, utilize a biblioteca
    `python-dotenv`, e em caso de dúvidas, confira os exemplos no diretório
    examples, como o `./examples/listar_etapas_pedido.py`.

    Uso: api = OmieClient(app_key, app_secret)

    `app_key` é a app_key do Omie
    `app_secret` é a app_secret do Omie
    `prefix` o prefixo das requests, padrão é "https://app.omie.com.br/api/v1/"
    `cache_ttl` é o tempo de cache das respostas da api, caso utilize
        use_cache=True em suas requests.

    """
    def __init__(self, app_key: str, app_secret: str, prefix='https://app.omie.com.br/api/v1/', cache_ttl=60):
        if app_key is None or app_secret is None:
            raise OmieClientError("app_key e app_secret não podem ser None")
        self.app_key = app_key
        self.app_secret = app_secret
        self.prefix = prefix if prefix.endswith("/") else prefix + "/"
        self.cache = TTLCache(maxsize=1024, ttl=cache_ttl)

    @cachedmethod(lambda self: self.cache)
    def _request_with_cache(self, method: str, url: str, data=None) -> requests.Response:
        """
        Envia request para a Omie API e armazena a resposta no cache.

        O parametro `json` deve ser hashable. De preferência um frozendict.
        """
        headers = {"Content-type": "application/json"} if data else None
        return requests.request(method, url, data=data, headers=headers, allow_redirects=False)

    def get(self, method: OmieMethod, data: OmieSchema, use_cache=True, return_json=True):
        """
        Pegar dados da Omie API.
        Ponto importante: apesar de o client PEGAR dados, é feito uma request POST.
        a API do Omie possui esse comportamento, pois os dados de filtro são enviados
        no payload do POST (json).

        `method` deve ser um dos métodos do omie, como por exemplo
            'ConsultarPedido' ou 'ConsultarProjeto'. Consulte o arquivo
            methods.py para exemplos.
        `data` deve ser os dados a serem enviados para o omie. Pode ser
            dict ou OmieSchema. Ver schemas.py.
        `use_cache` caso seja True, armazena a resposta da request em cache.
        `return_json` caso seja False para que o retorno seja o objeto da response

        raises `OmieAPIError` or `OmieClientError`
        """
        if isinstance(method, str):
            method = omie.methods.method_name_to_class(method)
        elif not issubclass(method, OmieMethod):
            raise TypeError(f"Parametro `method` deve ser string ou OmieMethod, não {type(method)}")
        if method.kind != omie.methods.GET:
            raise OmieClientError(f"O método {method} não é do tipo GET.")
        if isinstance(data, dict):
            data = method.schema(**data)
        elif not isinstance(data, OmieSchema):
            raise TypeError(f"Parametro `data` deve ser dict ou OmieSchema, não {type(data)}")
        data = data.model_dump(exclude_none=True)
        json_data = {
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'call': method.name,
            'param': [data]
        }
        url = self.prefix + method.path + "/"
        if use_cache == True:
            response = self._request_with_cache("POST", url, json.dumps(json_data))
        else:
            response = requests.post(url, json=json_data, allow_redirects=False)
        if return_json == False:
            return response
        resp_json = response.json()
        if 'faultstring' in resp_json or 'faultcode' in resp_json:
            exc = OmieAPIError(faultcode=resp_json.get('faultcode'), faultstring=resp_json.get('faultstring'))
            exc.json = resp_json
            raise exc
        return resp_json
