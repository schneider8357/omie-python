"""
Classes dos schemas da API Omie, disponíveis em https://developer.omie.com.br/service-list/.

O schema define como devem ser os dados JSON de uma request, ou
como será a estrutura dos dados JSON de uma resposta da API Omie.
Um detalhe para se atentar: o tipo no Omie é definido em camelCase,
porém foram transcritos para PascalCase. Por exemplo, o tipo
pvpConsultarRequest foi reescrito como PvpConsultarRequest, com
o "P" maiúsculo.
"""
from typing import List, Optional

from pydantic import BaseModel


class OmieSchema(BaseModel):
    """Todos os schemas da Omie API devem ser subclasses desta classe.
    
    O `BaseModel` do pydantic irá validar os tipos e a obrigatoriedade
    dos campos. Então, pode-se gerar o JSON para o payload da request
    POST com o classmethod `schema.model_dump()`.
    Veja mais: https://docs.pydantic.dev/latest/concepts/models/
    """
    pass

class PvpConsultarRequest(OmieSchema):
    """Ref: /api/v1/produtos/pedido/#pvpConsultarRequest"""
    codigo_pedido: Optional[int] = None
    codigo_pedido_integracao: Optional[str] = None
    numero_pedido: Optional[str] = None

class PvpStatusRequest(OmieSchema):
    """Ref: /api/v1/produtos/pedido/#pvpStatusRequest"""
    codigo_pedido: Optional[int] = None
    codigo_pedido_integracao: Optional[str] = None

class PvpListarRequest(OmieSchema):
    """Ref: /api/v1/produtos/pedido/#pvpListarRequest"""
    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    apenas_importado_api: Optional[str] = None
    ordenar_por: Optional[str] = None
    ordem_decrescente: Optional[str] = None
    filtrar_por_data_de: Optional[str] = None
    filtrar_por_data_ate: Optional[str] = None
    filtrar_por_hora_de: Optional[str] = None
    filtrar_por_hora_ate: Optional[str] = None
    numero_pedido_de: Optional[int] = None
    numero_pedido_ate: Optional[int] = None
    etapa: Optional[str] = None

class PedidoVendaProduto(OmieSchema):

    class PvpProduto(OmieSchema):
        codigo_produto: int
        codigo_produto_integracao: str
        codigo: str
        descricao: str
        cfop: str
        ncm: str
        ean: str
        unidade: str
        quantidade: float
        valor_unitario: float
        codigo_tabela_preco: int
        valor_mercadoria: float
        tipo_desconto: str
        percentual_desconto: float
        valor_desconto: float
        valor_deducao: float
        valor_icms_desonerado: float
        motivo_icms_desonerado: str
        valor_total: float
        indicador_escala: str
        cnpj_fabricante: str
        kit: str
        componente_kit: str
        codigo_item_kit: int
        reservado: str

    class PvpDet(OmieSchema):
        ide: Optional[dict] = None
        produto: Optional[dict] = None
        observacao: Optional[dict] = None
        inf_adic: Optional[dict] = None
        imposto: Optional[dict] = None
        rastreabilidade: Optional[dict] = None
        combustivel: Optional[dict] = None

    cabecalho: Optional[dict] = None
    departamentos: Optional[list] = None
    frete: Optional[dict] = None
    informacoes_adicionais: Optional[dict] = None
    lista_parcelas: Optional[dict] = None
    observacoes: Optional[dict] = None
    det: List[PvpDet]
    market_place: Optional[dict] = None
    total_pedido: Optional[dict] = None
    infoCadastro: Optional[dict] = None
    exportacao: Optional[dict] = None
    lancamentos: Optional[dict] = None

class PvpListarResponse(OmieSchema):
    pagina: int
    total_de_paginas: int
    registros: int
    total_de_registros: int
    pedido_venda_produto: List[PedidoVendaProduto]

class PEtapaListarRequest(OmieSchema):
    """Ref: /api/v1/produtos/pedidoetapas/#pEtapaListarRequest"""
    nPagina: Optional[int] = None
    nRegPorPagina: Optional[int] = None
    cOrdenarPor: Optional[str] = None
    cOrdemDecrescente: Optional[str] = None
    dDtInicial: Optional[str] = None
    dDtFinal: Optional[str] = None
    cHrInicial: Optional[str] = None
    cHrFinal: Optional[str] = None
    nCodPed: Optional[int] = None
    cCodIntPed: Optional[str] = None
    cEtapa: Optional[str] = None

class EtaproListarRequest(OmieSchema):
    """Ref: https://app.omie.com.br/api/v1/produtos/etapafat/#etaproListarRequest"""
    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    ordenar_por: Optional[str] = None
    ordem_decrescente: Optional[str] = None

class VendConsultarRequest(OmieSchema):
    """Ref: https://app.omie.com.br/api/v1/geral/vendedores/#vendConsultarRequest"""
    codigo: Optional[int] = None # Código do vendedor.
    codInt: Optional[str] = None # Código de Integração do vendedor.

class ProjConsultarRequest(OmieSchema):
    """Ref: https://app.omie.com.br/api/v1/geral/projetos/#projConsultarRequest"""
    codigo: Optional[int] = None # Código do projeto.
    codInt: Optional[str] = None # Código de Integração do projeto.


class OsListarRequest(OmieSchema):

    class OsFiltrarPorCodigo(OmieSchema):
        nCodOS: int
        cCodIntOS: str

    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    apenas_importado_api: Optional[str] = None
    ordenar_por: Optional[str] = None
    ordem_decrescente: Optional[str] = None
    filtrar_por_data_de: Optional[str] = None
    filtrar_por_data_ate: Optional[str] = None
    filtrar_apenas_inclusao: Optional[str] = None
    filtrar_apenas_alteracao: Optional[str] = None
    filtrar_por_codigo: Optional[List[OsFiltrarPorCodigo]] = None
    filtrar_por_status: Optional[str] = None
    filtrar_por_etapa: Optional[str] = None
    filtrar_por_cliente: Optional[int] = None
    filtrar_por_data_previsao_de: Optional[str] = None
    filtrar_por_data_previsao_ate: Optional[str] = None
    filtrar_por_data_faturamento_de: Optional[str] = None
    filtrar_por_data_faturamento_ate: Optional[str] = None
    filtrar_por_data_cancelamento_de: Optional[str] = None
    filtrar_por_data_cancelamento_ate: Optional[str] = None
    ordem_descrescente: Optional[str] = None
    cExibirDespesas: Optional[str] = None
    cExibirProdutos: Optional[str] = None
    cTipoFat: Optional[str] = None

class CategoriaConsultar(OmieSchema):
    codigo: str

class CategoriaListRequest(OmieSchema):
    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    filtrar_apenas_ativo: Optional[str] = None
    filtrar_por_tipo: Optional[str] = None

class DadosDRE(OmieSchema):
    codigoDRE: str
    descricaoDRE: str
    naoExibirDRE: str
    nivelDRE: int
    sinalDRE: str
    totalizaDRE: str

class CategoriaCadastro(OmieSchema):
    codigo: str
    descricao: str
    descricao_padrao: str
    conta_inativa: str
    definida_pelo_usuario: str
    id_conta_contabil: int
    tag_conta_contabil: str
    conta_despesa: str
    nao_exibir: str
    natureza: str
    conta_receita: str
    totalizadora: str
    transferencia: str
    codigo_dre: str
    categoria_superior: str
    dadosDRE: List[DadosDRE]

class LcpListarRequest(OmieSchema):
    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    apenas_importado_api: Optional[str] = None
    ordenar_por: Optional[str] = None
    ordem_descrescente: Optional[str] = None
    filtrar_por_data_de: Optional[str] = None
    filtrar_por_data_ate: Optional[str] = None
    filtrar_apenas_inclusao: Optional[str] = None
    filtrar_apenas_alteracao: Optional[str] = None
    filtrar_por_emissao_de: Optional[str] = None
    filtrar_por_registro_de: Optional[str] = None
    filtrar_por_emissao_ate: Optional[str] = None
    filtrar_por_registro_ate: Optional[str] = None
    filtrar_conta_corrente: Optional[int] = None
    filtrar_cliente: Optional[int] = None
    filtrar_por_cpf_cnpj: Optional[str] = None
    filtrar_por_status: Optional[str] = None
    filtrar_por_projeto: Optional[int] = None
    filtrar_por_vendedor: Optional[int] = None
    filtrar_apenas_titulos_em_aberto: Optional[str] = None
    exibir_obs: Optional[str] = None

class LcrListarRequest(OmieSchema):
    pagina: Optional[int] = None
    registros_por_pagina: Optional[int] = None
    apenas_importado_api: Optional[str] = None
    ordenar_por: Optional[str] = None
    ordem_descrescente: Optional[str] = None
    filtrar_por_data_de: Optional[str] = None
    filtrar_por_data_ate: Optional[str] = None
    filtrar_apenas_inclusao: Optional[str] = None
    filtrar_apenas_alteracao: Optional[str] = None
    filtrar_por_emissao_de: Optional[str] = None
    filtrar_por_registro_de: Optional[str] = None
    filtrar_por_emissao_ate: Optional[str] = None
    filtrar_por_registro_ate: Optional[str] = None
    filtrar_conta_corrente: Optional[int] = None
    filtrar_apenas_titulos_em_aberto: Optional[str] = None
    filtrar_cliente: Optional[int] = None
    filtrar_por_status: Optional[str] = None
    filtrar_por_cpf_cnpj: Optional[str] = None
    filtrar_por_projeto: Optional[int] = None
    filtrar_por_vendedor: Optional[int] = None
    exibir_obs: Optional[str] = None