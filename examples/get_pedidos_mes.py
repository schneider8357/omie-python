import os

import pandas as pd
from dotenv import load_dotenv

import omie


load_dotenv()


api = omie.OmieClient(
    os.getenv('OMIE_APP_KEY'),
    os.getenv('OMIE_APP_SECRET'),
)

def get_pedidos_entre(data_inicio: str, data_fim: str) -> list:
    pedidos = []

    res = api.get(omie.ListarEtapasPedido, {
        "nPagina": 1,
        "nRegPorPagina": 1,
        "dDtInicial": data_inicio,
        "dDtFinal": data_fim,
        "cEtapa": 20,
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
            "cEtapa": 20,
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
    dados_pedido = api.get(omie.ConsultarPedido, {"numero_pedido": num_ped})
    if "pedido_venda_produto" not in dados_pedido:
        print(f"WARN: {num_ped} faltando 'pedido_venda_produto'")
        return dados_pedido
    if "total_pedido" in dados_pedido["pedido_venda_produto"]:
        p["valor_mercadorias"] = dados_pedido["pedido_venda_produto"]["total_pedido"].get("valor_mercadorias")
        if p["valor_mercadorias"] is None:
            print(f"WARN: {num_ped}: faltando 'valor_mercadorias'")
    if "informacoes_adicionais" not in dados_pedido["pedido_venda_produto"]:
        print(f"WARN: {num_ped} faltando 'informacoes_adicionais'")
        return dados_pedido
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


pedidos_mes = get_pedidos_entre("01/03/2024","31/03/2024")

pedidos_mes_completos = {}
for p in pedidos_mes:
    try:
        pedidos_mes_completos[p["numero_pedido"]] = p
        pedidos_mes_completos[p["numero_pedido"]] |= get_dados_completos_pedido(p["numero_pedido"])
    except Exception as exc:
        print(f"ERROR: erro ao obter pedido {p}: {exc}")

df = pd.DataFrame(pedidos_mes_completos.values())
df.to_csv("pedidos_vendas_03_2024.csv")
