"""
examples/get_dre.py

Produz um relatório DRE com base no período especificado.

Uso:

$ python3 examples/get_dre.py 01/05/2024 31/05/2024
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

def get_categoria(cod_categoria):
    dados_categoria = api.get(omie.ConsultarCategoria, {"codigo": cod_categoria})
    return dados_categoria

def get_dados_conta(conta: dict, tipo: str):
    dados_conta = {
        k: conta.get(k) for k in (
            "codigo_projeto",
            "codigo_categoria",
            "codigo_vendedor",
            "valor_documento",
            "data_emissao",
            "data_previsao",
            "data_vencimento",
            "status_titulo",
        )
    }
    if tipo == "pagar":
        dados_conta["data_entrada"] = conta.get("data_entrada")
    elif tipo == "receber":
        dados_conta["data_entrada"] = conta.get("data_registro")
    dados_conta["impostos_retidos"] = sum((
        conta.get("valor_pis", 0),
        conta.get("valor_cofins", 0),
        conta.get("valor_csll", 0),
        conta.get("valor_ir", 0),
        conta.get("valor_iss", 0),
        conta.get("valor_inss", 0),
    ))
    return dados_conta

def get_dados_categoria(codigo):
    dados_categoria = {}
    categoria = get_categoria(str(codigo))
    dados_categoria["nome_categoria"] = categoria.get("descricao")
    grupo = get_categoria(str(categoria.get("categoria_superior")))
    dados_categoria["grupo_categoria"] = grupo.get("descricao")
    dados_categoria["codigo_grupo_categoria"] = grupo.get("codigo")
    return dados_categoria

def get_contas_pagar(data_inicio: str, data_fim: str) -> list:
    res = api.get_all(omie.ListarContasPagar, {
        "filtrar_por_registro_de": data_inicio,
        "filtrar_por_registro_ate": data_fim,
    })
    contas = []
    for conta in res:
        dados_conta = get_dados_conta(conta, tipo="pagar")
        if len(conta["categorias"]) == 1:
            dados_conta |= get_dados_categoria(conta["codigo_categoria"])
            contas.append(dados_conta)
            continue
        elif len(conta["categorias"]) > 1:
            for categoria in conta["categorias"]:
                nova_conta = {} | dados_conta
                nova_conta["codigo_categoria"] = categoria["codigo_categoria"]
                nova_conta["valor_documento"] = categoria["valor"]
                nova_conta |= get_dados_categoria(nova_conta["codigo_categoria"])
                contas.append(nova_conta)
        else:
            raise ValueError(f"Conta sem codigo_categoria :{conta}")
    return contas    


def get_contas_receber(data_inicio: str, data_fim: str) -> list:
    res = api.get_all(omie.ListarContasReceber, {
        "filtrar_por_registro_de": data_inicio,
        "filtrar_por_registro_ate": data_fim,
    })
    contas = []
    for conta in res:
        dados_conta = get_dados_conta(conta, tipo="receber")
        if len(conta["categorias"]) == 1:
            dados_conta |= get_dados_categoria(conta["codigo_categoria"])
            contas.append(dados_conta)
            continue
        elif len(conta["categorias"]) > 1:
            for categoria in conta["categorias"]:
                nova_conta = {} | dados_conta
                nova_conta["codigo_categoria"] = categoria["codigo_categoria"]
                nova_conta["valor_documento"] = categoria["valor"]
                nova_conta |= get_dados_categoria(nova_conta["codigo_categoria"])
                contas.append(nova_conta)
        else:
            raise ValueError(f"Conta sem codigo_categoria :{conta}")
    return contas

def report_dre(data_inicio, data_fim=None):
    if data_fim == None:
        data_fim = data_inicio
    contas_pagar = get_contas_pagar(data_inicio, data_fim)

    df_dre = pd.DataFrame(columns=['TIPO', 'CODIGO_GRUPO', 'GRUPO', 'CODIGO_CATEGORIA','CATEGORIA','DATA_EMISSAO', 'DATA_ENTRADA', 'DATA_PREVISAO', 'DATA_VENCIMENTO', 'CODIGO_VENDEDOR', 'VALOR_CONTA','IMPOSTOS_RETIDOS', 'STATUS'])#'PAGO_OU_RECEBIDO', 'A_PAGAR_OU_RECEBER'])
    for conta in contas_pagar:
        df_dre.loc[len(df_dre)] = (
            2, 
            conta["codigo_grupo_categoria"],
            conta["grupo_categoria"],
            conta["codigo_categoria"],
            conta["nome_categoria"],
            conta["data_emissao"],
            conta["data_entrada"],
            conta["data_previsao"],
            conta["data_vencimento"],
            conta["codigo_vendedor"],
            0 - conta["valor_documento"],
            0 - conta["impostos_retidos"],
            conta["status_titulo"],
            # conta["pago_ou_recebido"], 
            # conta["a_pagar_ou_receber"]
        )
    contas_receber = get_contas_receber(data_inicio, data_fim)
    
    for conta in contas_receber:
        df_dre.loc[len(df_dre)] = (
            1, 
            conta["codigo_grupo_categoria"],
            conta["grupo_categoria"], 
            conta["codigo_categoria"],
            conta["nome_categoria"], 
            conta["data_emissao"], 
            conta["data_entrada"],
            conta["data_previsao"],
            conta["data_vencimento"],
            conta["codigo_vendedor"],
            conta["valor_documento"], 
            conta["impostos_retidos"], 
            conta["status_titulo"],
            # conta["pago_ou_recebido"], 
            # conta["a_pagar_ou_receber"]
        )
    return df_dre

    

if __name__ == "__main__":
    data_inicio = sys.argv[1]
    data_fim = sys.argv[2] if len(sys.argv) >= 3 else data_inicio
    filename = f"relatorio_dre_{data_inicio}_ate_{data_fim}.csv".replace("/", "_")
    df_dre = report_dre(data_inicio, data_fim=data_fim)
    df_dre.to_csv(filename)
    print("arquivo gerado:", filename)
