"""
test_10_produtos_funcional.py – testes funcionais dos produtos (Passo 7, Parte C)

O que faz:
    Verifica o comportamento NORMAL da API de produtos (o "caminho feliz") e os
    erros mais comuns (produto que não existe).

Porque existe:
    É o contrato descrito no doc do Passo 7 (secção 1.8) transformado em
    verificações automáticas. Se alguém alterar a API e partir uma destas
    regras, estes testes falham logo.

Regras que respeitam o que combinámos (secção 1.9 do doc):
    - cada teste usa o SEU produto (fixture "produto", com nome único);
    - nenhum teste assume quantos produtos existem na base de dados.
"""

import pytest

from conftest import nome_unico

# Todos os testes deste ficheiro levam a etiqueta "funcional".
pytestmark = pytest.mark.funcional

# Identificador válido (dentro dos limites da API) mas que nunca existirá: é o
# maior inteiro de 32 bits. A tabela usa SERIAL, que só chega aqui após 2 mil
# milhões de inserções.
ID_INEXISTENTE = 2_147_483_647


# -----------------------------------------------------------------------------
# Criar produtos (POST /produtos)
# -----------------------------------------------------------------------------
def test_criar_produto_devolve_201_e_o_produto_com_id(cliente):
    """Criar com dados válidos responde 201 e devolve o produto com um id."""
    nome = nome_unico()

    resposta = cliente.post("/produtos", json={"nome": nome, "preco": 19.99})

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == nome
    assert corpo["preco"] == 19.99
    assert isinstance(corpo["id"], int)  # o id foi gerado pela base de dados


def test_resposta_de_criar_tem_exatamente_os_campos_esperados(produto):
    """O produto só tem id, nome e preco (nada a mais, nada a menos).

    Porquê verificar isto: se um dia a API passar a devolver um campo interno
    (por exemplo, uma data ou uma chave), quem consome pode ficar dependente
    dele sem ninguém reparar.
    """
    assert set(produto.keys()) == {"id", "nome", "preco"}


def test_criar_dois_produtos_da_ids_diferentes(cliente):
    """Dois produtos criados seguidos nunca partilham o mesmo id."""
    primeiro = cliente.post("/produtos", json={"nome": nome_unico(), "preco": 1}).json()
    segundo = cliente.post("/produtos", json={"nome": nome_unico(), "preco": 1}).json()

    assert primeiro["id"] != segundo["id"]
    assert segundo["id"] > primeiro["id"]  # o SERIAL só cresce


def test_preco_minimo_aceite_e_um_centimo(cliente):
    """O menor preço válido (0.01) é aceite e volta igual."""
    resposta = cliente.post("/produtos", json={"nome": nome_unico(), "preco": 0.01})

    assert resposta.status_code == 201
    assert resposta.json()["preco"] == 0.01


def test_nome_com_acentos_e_simbolos_e_guardado_tal_como_veio(cliente):
    """Texto com acentos, cedilha e euro não se estraga (codificação UTF-8)."""
    nome = f"Ração açucarada 100% € {nome_unico()}"

    criado = cliente.post("/produtos", json={"nome": nome, "preco": 3}).json()
    lido = cliente.get(f"/produtos/{criado['id']}").json()

    assert lido["nome"] == nome


# -----------------------------------------------------------------------------
# Ler produtos (GET /produtos e GET /produtos/{id})
# -----------------------------------------------------------------------------
def test_produto_criado_pode_ser_lido_pelo_id(cliente, produto):
    """O que se cria fica guardado: criar e depois obter dá os mesmos dados."""
    resposta = cliente.get(f"/produtos/{produto['id']}")

    assert resposta.status_code == 200
    assert resposta.json() == produto


def test_produto_criado_aparece_na_lista(cliente, produto):
    """O produto criado está na lista de todos os produtos.

    Procuramos o NOSSO produto na lista; não verificamos quantos há.
    """
    resposta = cliente.get("/produtos")

    assert resposta.status_code == 200
    ids = [p["id"] for p in resposta.json()]
    assert produto["id"] in ids


def test_lista_vem_ordenada_por_id(cliente, produto):
    """A API ordena a lista por id (ORDER BY id), por isso é previsível."""
    ids = [p["id"] for p in cliente.get("/produtos").json()]

    assert ids == sorted(ids)


def test_cada_item_da_lista_tem_os_campos_esperados(cliente, produto):
    """Todos os itens da lista têm id, nome e preco (mesmo os de outros testes)."""
    for item in cliente.get("/produtos").json():
        assert set(item.keys()) == {"id", "nome", "preco"}


# -----------------------------------------------------------------------------
# Erros: produto que não existe
# -----------------------------------------------------------------------------
def test_produto_inexistente_devolve_404(cliente):
    """Pedir um id que não existe responde 404 e diz porquê."""
    resposta = cliente.get(f"/produtos/{ID_INEXISTENTE}")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Produto não encontrado"}


def test_respostas_da_api_sao_json(cliente, produto):
    """Sucesso e erro respondem com JSON (e não HTML ou texto solto)."""
    sucesso = cliente.get(f"/produtos/{produto['id']}")
    erro = cliente.get(f"/produtos/{ID_INEXISTENTE}")

    assert sucesso.headers["content-type"].startswith("application/json")
    assert erro.headers["content-type"].startswith("application/json")
