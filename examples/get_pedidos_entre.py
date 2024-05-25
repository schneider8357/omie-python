"""
examples/get_pedidos_entre.py

Uso:

$ python3 examples/get_pedidos_entre.py 20/05/2024 22/05/2024

arquivo gerado: itens_pedidos_vendas_20_05_2024_ate_22_05_2024.csv


Obs.: O parâmetro retornar_itens=True denota que os dados de cada item
dos pedidos serão retornados ao invés dos dados de cada pedido.
O parâmetro etapas=["20","50","60","70"] define quais etapas serão buscadas.
"""
import os
import sys

import pandas as pd
from dotenv import load_dotenv

import omie


load_dotenv()


api = omie.OmieClient(
    os.getenv('OMIE_APP_KEY'),
    os.getenv('OMIE_APP_SECRET'),
    cache_ttl=300,
)

def get_pedidos_entre(data_inicio: str, data_fim: str, codigo_etapa: str = None) -> list:
    pedidos = []

    res = api.get_all(omie.ListarEtapasPedido, {
        "dDtInicial": data_inicio,
        "dDtFinal": data_fim,
        "cEtapa": codigo_etapa,
    })
    for p in res:
        pedidos.append({
            "numero_pedido": p["cNumero"],
            "codigo_etapa": codigo_etapa,
            "codigo_pedido": p["nCodPed"],
            "data_inclusao": p.get("info", {}).get("dInc"),
            "data_aprovacao_financeiro": p["dDtEtapa"],
        })
    return pedidos

def get_dados_completos_item(item: dict):
    return {
        "codigo_item": item.get('ide').get('codigo_item'),
        "codigo_produto": item["produto"]["codigo_produto"],
        "cfop": item["produto"]["cfop"],
        "descricao": item["produto"]["descricao"],
        "valor_unitario": item["produto"]["valor_unitario"],
    }

def get_dados_completos_pedido(num_ped: int, retornar_itens=False) -> dict:
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
        p["valor_total_pedido"] = dados_pedido["pedido_venda_produto"]["total_pedido"].get("valor_total_pedido")
        if p["valor_total_pedido"] is None:
            print(f"WARN: {num_ped}: faltando 'valor_total_pedido'")
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
    if retornar_itens:
        p["itens"] = [get_dados_completos_item(item) for item in dados_pedido["pedido_venda_produto"]["det"]]
    return p



def report_pedidos_entre(data_inicio, data_fim=None, etapas=[], retornar_itens=False):
    if data_fim == None:
        data_fim = data_inicio
    pedidos_mes = []
    for codigo_etapa in etapas:
        pedidos_mes += get_pedidos_entre(data_inicio, data_fim, codigo_etapa=codigo_etapa)

    pedidos_mes_completos = {}
    for p in pedidos_mes:
        try:
            pedidos_mes_completos[p["numero_pedido"]] = p
            pedidos_mes_completos[p["numero_pedido"]] |= get_dados_completos_pedido(p["numero_pedido"], retornar_itens=retornar_itens)
        except omie.OmieAPIError as exc:
            if exc.faultcode == "SOAP-ENV:Client-8020":
                print(f"ERROR: Alguma coisa falhou na camada de cache. {p=}")
                raise exc
        except Exception as exc:
            print(f"ERROR: erro ao obter pedido {p}: {exc}")

    if retornar_itens:
        itens_pedidos = []
        for p in pedidos_mes_completos.values():
            for item in p.get("itens", []):
                itens_pedidos.append(p|item)
        df = pd.DataFrame(itens_pedidos)
        filename = f"itens_pedidos_vendas_{data_inicio}_ate_{data_fim}.csv".replace("/", "_")
    else:
        df = pd.DataFrame(pedidos_mes_completos.values())
        filename = f"pedidos_vendas_{data_inicio}_ate_{data_fim}.csv".replace("/", "_")
    df.to_csv(filename)
    return filename

if __name__ == "__main__":
    data_inicio = sys.argv[1]
    data_fim = sys.argv[2] if len(sys.argv) >= 3 else data_inicio
    print("arquivo gerado:", report_pedidos_entre(data_inicio, data_fim=data_fim, retornar_itens=True, etapas=["20","50","60","70"]))
