"""
Métodos da API Omie, disponíveis em https://developer.omie.com.br/service-list/.
"""
from omie import schemas, exceptions

GET = "GET"
POST = "POST"

class OmieMethod:
    kind: str
    name: str
    path: str
    schema: dict

class ConsultarPedido(OmieMethod):
    kind = GET
    name = "ConsultarPedido"
    path = "produtos/pedido"
    schema = schemas.PvpConsultarRequest

class ListarEtapasPedido(OmieMethod):
    kind = GET
    name = "ListarEtapasPedido"
    path = "produtos/pedidoetapas"
    schema = schemas.PEtapaListarRequest

class ListarEtapasFaturamento(OmieMethod):
    kind = GET
    name = "ListarEtapasFaturamento"
    path = "produtos/etapafat"
    schema = schemas.EtaproListarRequest

class ConsultarVendedor(OmieMethod):
    kind = GET
    name = "ConsultarVendedor"
    path = "geral/vendedores"
    schema = schemas.VendConsultarRequest

class ConsultarProjeto(OmieMethod):
    kind = GET
    name = "ConsultarProjeto"
    path = "geral/projetos"
    schema = schemas.ProjConsultarRequest

# TODO add mais métodos
...



name_to_class = {
    method.name: method for method in (
        ConsultarPedido,
        ListarEtapasPedido,
    )
}

def method_name_to_class(method: str) -> OmieMethod:
    """Retorna a classe do método associada a um nome.
    
    Esta função é útil caso o usuário desta biblioteca
    prefira passar os nomes dos métodos ao invés da classe,
    exemplo:

    >>> api = OmieClient(app_key, app_secret)
    >>> res = api.get("ListarEtapasPedido", {
    ...     "nPagina": 2,
    ...     "nRegPorPagina": 1,
    ... })
    """
    try:
        name_to_class[method]
    except KeyError:
        raise exceptions.OmieClientError(f"Método não encontrado {method}")
