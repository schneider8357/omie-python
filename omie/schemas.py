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
    codigo: int
    codInt: str

class ProjConsultarRequest(OmieSchema):
    """Ref: https://app.omie.com.br/api/v1/geral/projetos/#projConsultarRequest"""
    codigo: int	# Código do projeto.
    codInt: str # Código de Integração do projeto.
