"""Classes das exceptions da biblioteca"""

class OmieClientError(Exception):
    """Representa um erro no OmieClient, sem relação direta com a API"""
    ...

class OmieAPIError(Exception):
    """Representa um erro na API do Omie, por exemplo requests duplicadas"""
    def __init__(self, msg=None, faultcode=None, faultstring=None, *args, **kwargs):
        self.faultcode = faultcode
        self.faultstring = faultstring
        if msg is None:
            msg = f"Erro no omie: faultcode='{self.faultcode}' - faultstring='{self.faultstring}'"
        self.msg = msg
        super().__init__(msg, *args, **kwargs)
