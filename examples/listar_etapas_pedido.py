import os

from dotenv import load_dotenv

import omie


load_dotenv()

app_key = os.getenv('OMIE_APP_KEY')
app_secret = os.getenv('OMIE_APP_SECRET')
print(f"usando app_key {app_key[0:5]}...")
print(f"usando app_secret {app_secret[0:8]}...")

api = omie.OmieClient(app_key, app_secret)

data = {
    "nPagina": 2,
    "nRegPorPagina": 1,
}

res = api.get(omie.ListarEtapasPedido, data, return_json=False, use_cache=True)
print("status HTTP da resposta:", res.status_code)
print("conteúdo da resposta:", res.json())
