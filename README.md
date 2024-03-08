# omie-python
Interface simples em Python para a Omie API.

Este projeto está em fase de testes, portanto algumas coisas podem quebrar inesperadamente.


## Quickstart

Instalação:

```
git clone https://github.com/schneider8357/omie-python
cd omie-python
pip install -r requirements.txt
```

Crie um arquivo .env para armazenar a sua app_key e secret_key:

```
OMIE_APP_KEY='3833xxxxxxx'
OMIE_APP_SECRET='fed2xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

Utilização:

```python
api = omie.OmieClient(app_key, app_secret)

data = {
    "nPagina": 2,
    "nRegPorPagina": 1,
}
```

> [!IMPORTANT]  
> Não deixe as suas chaves app_key e app_secret no seu código! Ao invés disso, utilize a biblioteca python-dotenv


## Methods

Consulte os métodos no arquivo `omie/methods.py`

Os métodos já implementados são: 

- **ConsultarPedido**
- **ListarEtapasPedido**
- **ListarEtapasFaturamento**
- **ConsultarVendedor**
- **ConsultarProjeto**

Ainda faltam implementar, pelo menos:
- **AlterarProduto**
- **ConsultarCliente**
- **ListarCenarios**
- **ListarClientes**
- **ListarLocaisEstoque**
- **ListarImpostosCenario**
- **ListarPosEstoque**
- **ListarProdutos**
- **ListarTabelaItens**
- **ListarTabelasPreco**

## Schemas

O schema é uma forma de validar os dados que serão enviados para a Omie API.
Para esta validação, a biblioteca pydantic é utilizada. Ela valida os tipos
dos dados e exporta os modelos para JSON. Confira os exemplos em `omie/schemas.py`.

