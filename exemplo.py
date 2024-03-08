import json
import os

from dotenv import load_dotenv

import omie

load_dotenv()

empresa = "CAV"

app_key = os.getenv(empresa + '_KEY')
app_secret = os.getenv(empresa + '_SECRET')

data = {
    "numero_pedido": 1002,
}
res = omie.get(omie.consultar_pedido, data, app_key, app_secret)


try:
    codigo_pedido = res['pedido_venda_produto']['cabecalho']['codigo_pedido']
except:
    print(res)
    exit(1)

print(f"O código do pedido de número {data['numero_pedido']} é {codigo_pedido}")


data = {
    "nCodPed": codigo_pedido,
}
res = omie.get(omie.listar_etapas_pedido, data, app_key, app_secret)

try:
    raise
    print(json.dumps([x["cEtapa"]+","+x["dDtEtapa"] for x in res["etapasPedido"] if True or x["cEtapa"] in ("10", "20")], indent=2))
except:
    print(res)
