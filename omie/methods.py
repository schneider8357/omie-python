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
    schema: schemas.OmieSchema
    response_schema: schemas.OmieSchema

class OmieListMethod(OmieMethod):
    page_num_field = None
    regs_per_page_field = None
    resp_total_regs_field = None
    resp_array_field = None

class ConsultarPedido(OmieMethod):
    kind = GET
    name = "ConsultarPedido"
    path = "produtos/pedido"
    schema = schemas.PvpConsultarRequest

class StatusPedido(OmieMethod):
    kind = GET
    name = "StatusPedido"
    path = "produtos/pedido"
    schema = schemas.PvpStatusRequest

class ListarPedidos(OmieListMethod):
    kind = GET
    name = "ListarPedidos"
    path = "produtos/pedido"
    page_num_field = "pagina"
    regs_per_page_field = "registros_por_pagina"
    schema = schemas.PvpListarRequest
    response_schema = schemas.PvpListarResponse
    resp_total_regs_field = "total_de_registros"
    resp_array_field = "pedido_venda_produto"

class ListarEtapasPedido(OmieListMethod):
    kind = GET
    name = "ListarEtapasPedido"
    path = "produtos/pedidoetapas"
    page_num_field = "nPagina"
    regs_per_page_field = "nRegPorPagina"
    schema = schemas.PEtapaListarRequest
    resp_total_regs_field = "nTotRegistros"
    resp_array_field = "etapasPedido"

class ListarEtapasFaturamento(OmieListMethod):
    kind = GET
    name = "ListarEtapasFaturamento"
    path = "produtos/etapafat"
    page_num_field = "pagina"
    regs_per_page_field = "registros_por_pagina"
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


class ListarOS(OmieListMethod):
    kind = GET
    name = "ListarOS"
    path = "servicos/os"
    page_num_field = "pagina"
    regs_per_page_field = "registros_por_pagina"
    schema = schemas.OsListarRequest
    resp_total_regs_field = "total_de_registros"
    resp_array_field = "osCadastro"


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
