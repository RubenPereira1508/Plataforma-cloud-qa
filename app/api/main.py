"""
main.py – API da Loja (Projeto A)

O que faz:
    Expõe uma API HTTP simples para gerir produtos de uma loja, guardando os
    dados numa base de dados PostgreSQL.

Porque existe:
    Precisamos de uma aplicação pequena e controlada, fácil de perceber de
    ponta a ponta. Assim o foco do projeto fica na infraestrutura, na pipeline
    e nos testes, e não em código complexo.

Estado atual (Passo 2.3):
    Os produtos vivem no PostgreSQL. Se o contentor da API reiniciar, os dados
    mantêm-se (a base de dados guarda-os num volume do Docker).

Configuração:
    A ligação à base de dados vem da variável de ambiente DATABASE_URL.
    NUNCA escrevemos a palavra-passe no código: ela vem de fora (ficheiro .env
    no Compose; mais tarde, de um gestor de segredos na AWS).
"""

import os
import time
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException, Path
from psycopg.rows import dict_row
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, ConfigDict, Field

# -----------------------------------------------------------------------------
# Ligação à base de dados
# -----------------------------------------------------------------------------
# os.environ[...] falha logo ao arrancar se a variável não existir. É
# intencional: é melhor a aplicação nem arrancar do que correr mal configurada.
DATABASE_URL = os.environ["DATABASE_URL"]


def ligar() -> psycopg.Connection:
    """Abre uma ligação nova à base de dados.

    row_factory=dict_row faz com que cada linha venha como dicionário
    ({"id": 1, "nome": "..."}), o que combina bem com os modelos do Pydantic.

    Nota: abrir uma ligação por pedido é simples e chega para aprender.
    Em produção usar-se-ia um "pool" de ligações reutilizáveis.
    """
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def preparar_base_de_dados(tentativas: int = 10, espera: float = 2.0) -> None:
    """Cria a tabela (se não existir) e insere produtos iniciais (se estiver vazia).

    Porque há tentativas repetidas?
        Quando tudo arranca ao mesmo tempo (docker compose up), a base de dados
        pode ainda não estar pronta a aceitar ligações. Em vez de a API falhar
        de imediato, tenta de novo algumas vezes. É um padrão comum em sistemas
        distribuídos (retry).
    """
    for tentativa in range(1, tentativas + 1):
        try:
            # "with" confirma (commit) a transação no fim e fecha a ligação.
            with ligar() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS produtos (
                        id    SERIAL PRIMARY KEY,
                        nome  VARCHAR(100) NOT NULL,
                        preco NUMERIC(10, 2) NOT NULL CHECK (preco > 0)
                    )
                    """
                )
                total = conn.execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]
                if total == 0:
                    conn.execute(
                        "INSERT INTO produtos (nome, preco) VALUES (%s, %s), (%s, %s)",
                        ("Teclado mecânico", 49.90, "Rato sem fios", 19.90),
                    )
            return
        except psycopg.OperationalError:
            if tentativa == tentativas:
                raise  # esgotámos as tentativas: deixa o erro rebentar
            time.sleep(espera)


# -----------------------------------------------------------------------------
# A aplicação
# -----------------------------------------------------------------------------
@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Código que corre ao arrancar (antes do yield) e ao desligar (depois)."""
    preparar_base_de_dados()
    yield


app = FastAPI(
    title="API da Loja",
    description="API de exemplo usada no projeto Plataforma Cloud + QA.",
    version="0.3.0",
    lifespan=ciclo_de_vida,
)


# -----------------------------------------------------------------------------
# Métricas (Passo 6, Parte C)
# -----------------------------------------------------------------------------
# O Instrumentator mede cada pedido (número, código de resposta, duração) e
# cria o endereço /metrics, onde o Prometheus vai buscar os números.
# excluded_handlers: ignoramos /saude, /pronto e /metrics para que as sondas do
# Kubernetes e as leituras do Prometheus não encham os gráficos com tráfego
# que não é de clientes. include_in_schema=False esconde /metrics da
# documentação automática (/docs).
Instrumentator(excluded_handlers=["/saude", "/pronto", "/metrics"]).instrument(app).expose(
    app, include_in_schema=False
)


# -----------------------------------------------------------------------------
# Modelos de dados
# -----------------------------------------------------------------------------
# Os modelos do Pydantic descrevem a "forma" dos dados e VALIDAM-nos
# automaticamente. Se alguém enviar um preço negativo, o FastAPI responde
# com erro 422 sem precisarmos de escrever código para isso.
# Limites do preço. A coluna da base de dados é NUMERIC(10, 2): 8 dígitos
# antes da vírgula e 2 depois, por isso o maior valor possível é 99999999.99 e
# o menor positivo é 0.01. A API valida isto À ENTRADA; antes só exigia
# "preco > 0", e valores como 1000000000 ou 0.001 passavam a validação e
# rebentavam na base de dados (erro 500). Ver DEF-01 e DEF-02 no doc do Passo 7.
PRECO_MINIMO = 0.01
PRECO_MAXIMO = 99_999_999.99


class ProdutoNovo(BaseModel):
    """Dados que o cliente envia para criar um produto (regras ESTRITAS)."""

    # str_strip_whitespace: retira os espaços do início e do fim ANTES de
    # validar. Assim "   " passa a ter 0 caracteres e é recusado por
    # min_length=1 (DEF-03), e " Rato " é guardado como "Rato".
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1, max_length=100, description="Nome do produto")
    preco: float = Field(
        ge=PRECO_MINIMO,
        le=PRECO_MAXIMO,
        description="Preço em euros (entre 0,01 e 99 999 999,99)",
    )


class Produto(BaseModel):
    """Produto guardado, como a API o DEVOLVE (sem regras de validação).

    Porque NÃO herda de ProdutoNovo: o response_model também valida o que a API
    devolve. Se herdasse as regras estritas, um produto antigo que já está na
    base de dados e não cumpre as regras novas (por exemplo, um nome só com
    espaços criado antes da correção) faria GET /produtos falhar com 500.
    Regra: ser exigente com o que ENTRA, tolerante com o que já está guardado.
    """

    id: int
    nome: str
    preco: float


# Os identificadores são inteiros de 32 bits na base de dados (SERIAL).
# Limitamos o valor aceite no endereço para não rebentar com um número enorme.
ID_MAXIMO = 2_147_483_647


# -----------------------------------------------------------------------------
# Endpoints (os "endereços" da API)
# -----------------------------------------------------------------------------
@app.get("/saude")
def saude() -> dict:
    """Liveness: "o processo está vivo?"

    Rápido e SEM depender da base de dados. Se isto falhar, o orquestrador
    (Docker, Kubernetes) reinicia o contentor.
    """
    return {"estado": "ok"}


@app.get("/pronto")
def pronto() -> dict:
    """Readiness: "estou pronto a receber pedidos?"

    Verifica a ligação à base de dados. Se falhar, responde 503 (serviço
    indisponível). No Kubernetes, isto decide se o tráfego pode ser enviado
    para este contentor, sem o reiniciar.
    """
    try:
        with ligar() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Base de dados indisponível")
    return {"estado": "pronto"}


@app.get("/produtos", response_model=list[Produto])
def listar_produtos() -> list[dict]:
    """Devolve todos os produtos."""
    with ligar() as conn:
        # preco::float8 converte NUMERIC para decimal "normal" (float) no SQL.
        return conn.execute(
            "SELECT id, nome, preco::float8 AS preco FROM produtos ORDER BY id"
        ).fetchall()


@app.get("/produtos/{produto_id}", response_model=Produto)
def obter_produto(produto_id: int = Path(ge=1, le=ID_MAXIMO)) -> dict:
    """Devolve um produto pelo seu identificador (ou 404 se não existir)."""
    with ligar() as conn:
        # %s é um parâmetro: o valor é enviado SEPARADO da instrução SQL.
        # Isto protege contra SQL injection. NUNCA construir SQL com f-strings
        # a partir de dados do utilizador.
        produto = conn.execute(
            "SELECT id, nome, preco::float8 AS preco FROM produtos WHERE id = %s",
            (produto_id,),
        ).fetchone()
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@app.post("/produtos", response_model=Produto, status_code=201)
def criar_produto(novo: ProdutoNovo) -> dict:
    """Cria um produto novo e responde 201 (criado)."""
    with ligar() as conn:
        # RETURNING devolve a linha acabada de criar, já com o id gerado.
        return conn.execute(
            "INSERT INTO produtos (nome, preco) VALUES (%s, %s) "
            "RETURNING id, nome, preco::float8 AS preco",
            (novo.nome, novo.preco),
        ).fetchone()