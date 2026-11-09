"""
test_20_validacao.py – validação e casos limite da API (Passo 7, Parte D)

O que faz:
    Tenta "partir" a API com dados inválidos, valores nos limites e pedidos
    mal formados, e verifica que ela RECUSA com um erro claro (e não aceita
    lixo nem rebenta).

Porque existe:
    O caminho feliz (Parte C) mostra que a API funciona quando tudo corre bem.
    É nos erros e nos limites que costumam estar os defeitos. Pensar assim,
    "o que acontece se...", é a parte central do trabalho de QA.

Técnicas usadas:
    - PARAMETRIZAÇÃO: o mesmo teste corre com vários valores (uma linha por
      caso), em vez de copiar o teste 10 vezes.
    - ANÁLISE DE VALORES-LIMITE: testar o último valor válido e o primeiro
      inválido de cada regra (100 e 101 caracteres, id 2147483647 e 2147483648).
    - XFAIL ESTRITO: ver o aviso mais abaixo.

Códigos que esperamos:
    422 = o pedido está bem formado mas os dados são inválidos (o FastAPI
          responde assim sozinho, com a lista de erros em "detail").
    404 = o recurso não existe.   405 = método não permitido para esse endereço.
"""

import pytest

from conftest import nome_unico

# Todos os testes deste ficheiro levam a etiqueta "validacao".
pytestmark = pytest.mark.validacao

PRECO_VALIDO = 5.0


def criar(cliente, **campos):
    """Atalho: POST /produtos com os campos dados (nome único por omissão)."""
    corpo = {"nome": nome_unico(), "preco": PRECO_VALIDO}
    corpo.update(campos)
    return cliente.post("/produtos", json=corpo)


def campos_com_erro(resposta):
    """Devolve os nomes dos campos que o FastAPI diz estarem errados.

    Um erro 422 vem como: {"detail": [{"loc": ["body", "preco"], ...}]}.
    "loc" diz ONDE está o erro; é a parte final que nos interessa.
    """
    return {erro["loc"][-1] for erro in resposta.json()["detail"]}


# -----------------------------------------------------------------------------
# Criar produto: nome inválido
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "nome",
    [
        pytest.param("", id="vazio"),
        pytest.param("x" * 101, id="101-caracteres"),
        pytest.param(None, id="nulo"),
        pytest.param(123, id="numero-em-vez-de-texto"),
        pytest.param(["a"], id="lista-em-vez-de-texto"),
    ],
)
def test_nome_invalido_devolve_422_e_aponta_o_campo(cliente, nome):
    resposta = criar(cliente, nome=nome)

    assert resposta.status_code == 422
    assert "nome" in campos_com_erro(resposta)


# -----------------------------------------------------------------------------
# Criar produto: preço inválido
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "preco",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negativo"),
        pytest.param(-0.01, id="negativo-pequeno"),
        pytest.param("abc", id="texto"),
        pytest.param(None, id="nulo"),
        pytest.param([5], id="lista"),
    ],
)
def test_preco_invalido_devolve_422_e_aponta_o_campo(cliente, preco):
    resposta = criar(cliente, preco=preco)

    assert resposta.status_code == 422
    assert "preco" in campos_com_erro(resposta)


# -----------------------------------------------------------------------------
# Criar produto: corpo mal formado ou incompleto
# -----------------------------------------------------------------------------
def test_corpo_vazio_aponta_os_dois_campos_em_falta(cliente):
    resposta = cliente.post("/produtos", json={})

    assert resposta.status_code == 422
    assert campos_com_erro(resposta) == {"nome", "preco"}


def test_sem_corpo_nenhum_devolve_422(cliente):
    resposta = cliente.post("/produtos")

    assert resposta.status_code == 422


def test_json_mal_formado_devolve_422(cliente):
    """O corpo diz ser JSON mas está cortado a meio."""
    resposta = cliente.post(
        "/produtos",
        content=b'{"nome": "x", "preco": ',
        headers={"Content-Type": "application/json"},
    )

    assert resposta.status_code == 422


def test_pedido_recusado_nao_cria_nada(cliente):
    """Um 422 não pode deixar lixo: o produto recusado não aparece na lista.

    Usa-se um nome único e procura-se na lista (não se contam produtos).
    """
    nome = nome_unico()

    resposta = criar(cliente, nome=nome, preco=-5)
    nomes = [p["nome"] for p in cliente.get("/produtos").json()]

    assert resposta.status_code == 422
    assert nome not in nomes


# -----------------------------------------------------------------------------
# Valores-limite que DEVEM ser aceites
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "tamanho",
    [pytest.param(1, id="1-caractere"), pytest.param(100, id="100-caracteres")],
)
def test_nome_nos_limites_validos_e_aceite(cliente, tamanho):
    nome = nome_unico()[:8].ljust(tamanho, "n")[:tamanho]

    resposta = criar(cliente, nome=nome)

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == nome


def test_preco_maximo_da_base_de_dados_e_aceite(cliente):
    """A coluna é NUMERIC(10, 2): o maior valor possível é 99999999.99."""
    resposta = criar(cliente, preco=99999999.99)

    assert resposta.status_code == 201
    assert resposta.json()["preco"] == 99999999.99


# -----------------------------------------------------------------------------
# Segurança básica: o que o cliente envia nunca é executado nem obedecido
# -----------------------------------------------------------------------------
def test_injecao_de_sql_no_nome_e_guardada_como_texto(cliente):
    """A API usa parâmetros (%s), por isso o SQL malicioso é só texto."""
    nome = f"'; DROP TABLE produtos;-- {nome_unico()}"

    criado = criar(cliente, nome=nome)
    lista = cliente.get("/produtos")

    assert criado.status_code == 201
    assert criado.json()["nome"] == nome  # guardado tal e qual, sem ser executado
    assert lista.status_code == 200  # a tabela continua a existir


def test_cliente_nao_consegue_escolher_o_id(cliente):
    """Campos a mais são ignorados: o id é sempre gerado pela base de dados.

    Se a API aceitasse o "id" enviado, alguém podia sobrescrever produtos
    alheios (vulnerabilidade chamada "mass assignment").
    """
    resposta = criar(cliente, id=987654321, extra="ignorado")

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] != 987654321
    assert "extra" not in corpo


# -----------------------------------------------------------------------------
# Identificadores inválidos no endereço (GET /produtos/{id})
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "identificador",
    [
        pytest.param("0", id="zero"),
        pytest.param("-1", id="negativo"),
        pytest.param("2147483648", id="acima-do-maximo"),
        pytest.param("99999999999999999999", id="enorme"),
        pytest.param("abc", id="texto"),
        pytest.param("1.5", id="decimal"),
    ],
)
def test_identificador_invalido_devolve_422(cliente, identificador):
    resposta = cliente.get(f"/produtos/{identificador}")

    assert resposta.status_code == 422


# -----------------------------------------------------------------------------
# Métodos e endereços que não existem
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "metodo, caminho",
    [
        pytest.param("DELETE", "/produtos/1", id="apagar-produto"),
        pytest.param("PUT", "/produtos/1", id="atualizar-produto"),
        pytest.param("PUT", "/produtos", id="substituir-lista"),
        pytest.param("POST", "/produtos/1", id="criar-com-id"),
    ],
)
def test_metodo_nao_suportado_devolve_405(cliente, metodo, caminho):
    """A API só oferece GET e POST nos produtos (não há DELETE nem PUT)."""
    resposta = cliente.request(metodo, caminho)

    assert resposta.status_code == 405


def test_endereco_desconhecido_devolve_404(cliente):
    resposta = cliente.get("/isto-nao-existe")

    assert resposta.status_code == 404


# -----------------------------------------------------------------------------
# DEFEITOS CONHECIDOS (xfail estrito)
# -----------------------------------------------------------------------------
# Estes três testes descrevem o comportamento CORRETO e hoje FALHAM, porque a
# API tem defeitos. Foram suspeitos ao ler o código (a validação do FastAPI só
# exige "preco > 0", mas a base de dados NUMERIC(10, 2) tem regras extras que
# a API não verifica à entrada) e CONFIRMADOS a 2026-11-09 com
# "pytest --runxfail", que mostra o código de resposta real de cada um.
# Ver a secção "Defeitos encontrados" no doc do Passo 7.
#
# "xfail" quer dizer "falha esperada: sabemos que isto falha hoje". Com
# strict=True:
#   - se o teste FALHAR (o defeito existe)  -> aparece como "xfailed" (OK,
#     defeito documentado, a suite continua verde);
#   - se o teste PASSAR (a API foi corrigida) -> a suite FALHA a avisar que o
#     marcador xfail já não faz sentido e deve ser removido.
# Assim os defeitos ficam registados no código e ninguém os esquece.
@pytest.mark.xfail(
    strict=True,
    reason="DEF-01: preço acima de 99999999.99 passa a validação mas a base "
    "de dados rejeita (overflow) e a API responde 500 em vez de 422",
)
def test_preco_acima_do_limite_da_base_de_dados_devolve_422(cliente):
    resposta = criar(cliente, preco=1_000_000_000)

    assert resposta.status_code == 422


@pytest.mark.xfail(
    strict=True,
    reason="DEF-02: 0.001 passa 'preco > 0' mas a base arredonda para 0.00 "
    "e viola o CHECK (preco > 0); a API responde 500 em vez de 422",
)
def test_preco_que_arredonda_para_zero_devolve_422(cliente):
    resposta = criar(cliente, preco=0.001)

    assert resposta.status_code == 422


@pytest.mark.xfail(
    strict=True,
    reason="DEF-03: o nome só com espaços passa min_length=1 e a API responde "
    "201; na prática é um nome vazio e devia ser recusado com 422",
)
def test_nome_so_com_espacos_devolve_422(cliente):
    resposta = criar(cliente, nome="   ")

    assert resposta.status_code == 422