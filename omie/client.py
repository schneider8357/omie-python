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
import math

import requests
from cachetools import cachedmethod, TTLCache, keys

import omie.methods
from omie.methods import OmieMethod, OmieListMethod
from omie.exceptions import OmieClientError, OmieAPIError
from omie.schemas import OmieSchema


# TODO: mode for always retry request: if it fails retry X times?
# or parse faultstring, get timestamp and schedule?
# TODO: make requests asynchronous
# TODO: test cachedmethod lock in simultaneous calls scenario

def request_cache_key(self, method, url, data=None, session=None):
    return keys.hashkey(method, url, data)

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
        if not app_key or not app_secret:
            raise OmieClientError("faltando app_key ou app_secret")
        self.app_key = app_key
        self.app_secret = app_secret
        self.prefix = prefix if prefix.endswith("/") else prefix + "/"
        self.cache = TTLCache(maxsize=1024, ttl=cache_ttl)

    @cachedmethod(lambda self: self.cache, key=request_cache_key)
    def _request_with_cache(self, method: str, url: str, data=None, session=None) -> requests.Response:
        """
        Envia request para a Omie API e armazena a resposta no cache.

        O parametro `json` deve ser hashable. De preferência um frozendict.
        """
        headers = {"Content-type": "application/json"} if data else None
        if session is None:
            session = requests.Session()
        print(f"not caching request {url} {data=}") # TODO add logger
        return session.request(method, url, data=data, headers=headers, allow_redirects=False)

    def get(self, method: OmieMethod, data: OmieSchema, use_cache=True, return_json=True, session=None) -> dict:
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
        `session` requests.Session, permite reaproveitar uma session entre requests

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
        if session is None:
            session = requests.Session()
        if use_cache == True:
            response = self._request_with_cache("POST", url, json.dumps(json_data), session=session)
        else:
            response = requests.post(url, json=json_data, allow_redirects=False, session=session)
        if return_json == False:
            return response
        resp_json = response.json()
        if 'faultstring' in resp_json or 'faultcode' in resp_json:
            exc = OmieAPIError(faultcode=resp_json.get('faultcode'), faultstring=resp_json.get('faultstring'))
            exc.json = resp_json
            raise exc
        return resp_json

    def get_all(self, method: OmieListMethod, data: OmieSchema, use_cache=True, records_per_page=100, retries=3, timeout=30):
        """
        Pegar todos dados de uma lista da Omie API.
        Alguns métodos do Omie retornam uma lista de informações
        em páginas. O propósito do `get_all()` é retornar os dados
        de todas as páginas existentes, de um determinado filtro.
        Funciona apenas para requests de listagem.

        `method` deve ser um dos métodos do omie do tipo List
        `data` deve ser os dados a serem enviados para o omie (OmieSchema).
        `use_cache` caso seja True, armazena a resposta da request em cache.
        `return_json` caso seja False para que o retorno seja o objeto da response
        `records_per_page` indica quantos registros serão baixados a cada request
        `retries` número de tentativas para cada request
        `timeout` timeout de cada request

        raises `OmieAPIError` or `OmieClientError`
        """
        if isinstance(method, str):
            method = omie.methods.method_name_to_class(method)
        elif not issubclass(method, OmieMethod):
            raise TypeError(f"Parametro `method` deve ser string ou OmieMethod, não {type(method)}")
        if method.kind != omie.methods.GET:
            raise OmieClientError(f"O método {method} não é do tipo GET.")
        if method.page_num_field is None:
            raise OmieClientError(f"O método {method} não possui paginação.")
        if isinstance(data, dict):
            data = method.schema(**data)
        elif not isinstance(data, OmieSchema):
            raise TypeError(f"Parametro `data` deve ser dict ou OmieSchema, não {type(data)}")
        data = data.model_dump(exclude_none=True)
        data[method.page_num_field] = 1
        data[method.regs_per_page_field] = 1
        session = requests.Session()
        first = self.get(method, data, use_cache=use_cache, return_json=True, session=session)
        total_regs = first.get(method.resp_total_regs_field)
        if not total_regs:
            raise OmieAPIError("Nao foram encontrados registros para o filtro aplicado")
        resp_list = []
        total_pages = math.ceil(total_regs / records_per_page)
        for pag in range(total_pages):
            resp = self.get(
                method, 
                data | {
                    method.resp_total_regs_field: pag,
                    method.regs_per_page_field: records_per_page
                },
                use_cache=use_cache,
                return_json=True,
                session=session,
            )
            resp_list += resp.get(method.resp_array_field)
        return resp_list
