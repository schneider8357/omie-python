import json
import os

from dotenv import load_dotenv

import omie

load_dotenv()

app_key = os.getenv('OMIE_APP_KEY')
app_secret = os.getenv('OMIE_APP_SECRET')

api = omie.OmieClient(app_key, app_secret)

res = api.get(omie.ListarEtapasFaturamento, {
    'pagina': 1,
    'registros_por_pagina': 100,
})

try:
    print(json.dumps(res, indent=2))
except:
    print(res)
