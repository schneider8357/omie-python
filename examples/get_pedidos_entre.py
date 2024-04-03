import os
import sys

import pandas as pd
from dotenv import load_dotenv

import omie


load_dotenv()


api = omie.OmieClient(
    os.getenv('OMIE_APP_KEY'),
    os.getenv('OMIE_APP_SECRET'),
)

def get_pedidos_entre(data_inicio: str, data_fim: str, codigo_etapa: str = None) -> list:
    pedidos = []

    res = api.get(omie.ListarEtapasPedido, {
        "nPagina": 1,
        "nRegPorPagina": 1,
        "dDtInicial": data_inicio,
        "dDtFinal": data_fim,
        "cEtapa": codigo_etapa,
    })

    total_pedidos = res["nTotRegistros"]

    print(f"foram encontrados {total_pedidos} pedidos")

    registros_por_pag = 100
    paginas = total_pedidos // registros_por_pag
    if (total_pedidos % registros_por_pag):
        paginas += 1

    print(f"total de paginas: {paginas}")

    for pag in range(paginas):
        res = api.get(omie.ListarEtapasPedido, {
            "nPagina": pag+1,
            "nRegPorPagina": registros_por_pag,
            "dDtInicial": data_inicio,
            "dDtFinal": data_fim,
            "cEtapa": codigo_etapa,
        })
        for p in res["etapasPedido"]:
            pedidos.append({
                "numero_pedido": p["cNumero"],
                "codigo_pedido": p["nCodPed"],
                "data_inclusao": p.get("info", {}).get("dInc"),
                "data_aprovacao_financeiro": p["dDtEtapa"],
            })
    return pedidos


def get_dados_completos_pedido(num_ped: int) -> dict:
    p = {}
    try:
        dados_pedido = api.get(omie.ConsultarPedido, {"numero_pedido": num_ped})
    except omie.OmieAPIError as exc:
        if exc.faultcode == "SOAP-ENV:Client-107":
            print(f"WARN: Pulando pedido {p}, erro na API {exc.faultcode}")
            return p
        else:
            raise exc
    except Exception as exc:
        raise exc
    if "pedido_venda_produto" not in dados_pedido:
        print(f"WARN: {num_ped} faltando 'pedido_venda_produto'")
        return p
    if "total_pedido" in dados_pedido["pedido_venda_produto"]:
        p["valor_mercadorias"] = dados_pedido["pedido_venda_produto"]["total_pedido"].get("valor_mercadorias")
        if p["valor_mercadorias"] is None:
            print(f"WARN: {num_ped}: faltando 'valor_mercadorias'")
    if "informacoes_adicionais" not in dados_pedido["pedido_venda_produto"]:
        print(f"WARN: {num_ped} faltando 'informacoes_adicionais'")
        return p
    infos_pedido = dados_pedido["pedido_venda_produto"]["informacoes_adicionais"]
    if "codVend" in infos_pedido:
        p["vendedor"] = api.get(omie.ConsultarVendedor, {"codigo": infos_pedido["codVend"]}).get("nome")
    else:
        print(f"WARN: {num_ped} faltando 'codVend'")
    if "codProj" in infos_pedido:
        p["projeto"] = api.get(omie.ConsultarProjeto, {"codigo": infos_pedido["codProj"]}).get("nome")
    else:
        print(f"WARN: {num_ped} faltando 'codProj'")
    if "contato" in infos_pedido:
        p["cliente_nome"] = infos_pedido["contato"]
    else:
        print(f"WARN: {num_ped} faltando 'contato'")
    if "utilizar_emails" in infos_pedido:
        p["cliente_email"] = infos_pedido["utilizar_emails"]
    else:
        print(f"WARN: {num_ped} faltando 'utilizar_emails'")
    return p

data_inicio = sys.argv[1]
data_fim = sys.argv[2] if len(sys.argv) >= 3 else data_inicio

pedidos_mes = get_pedidos_entre(data_inicio, data_fim, codigo_etapa="20")

pedidos_mes_completos = {}
for p in pedidos_mes:
    try:
        pedidos_mes_completos[p["numero_pedido"]] = p
        pedidos_mes_completos[p["numero_pedido"]] |= get_dados_completos_pedido(p["numero_pedido"])
    except Exception as exc:
        print(f"ERROR: erro ao obter pedido {p}: {exc}")

df = pd.DataFrame(pedidos_mes_completos.values())
filename = f"pedidos_vendas_{data_inicio}_ate_{data_fim}.csv".replace("/", "_")
print("arquivo gerado:", filename)
df.to_csv(filename)

