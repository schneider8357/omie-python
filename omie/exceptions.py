"""Classes das exceptions da biblioteca"""

class OmieClientError(BaseException):
    """Representa um erro no OmieClient, sem relação direta com a API"""
    ...

class OmieAPIError(BaseException):
    """Representa um erro na API do Omie, por exemplo requests duplicadas"""
    ...