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
from pydantic import BaseModel, Field

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
    version="0.2.0",
    lifespan=ciclo_de_vida,
)


# -----------------------------------------------------------------------------
# Modelos de dados
# -----------------------------------------------------------------------------
# Os modelos do Pydantic descrevem a "forma" dos dados e VALIDAM-nos
# automaticamente. Se alguém enviar um preço negativo, o FastAPI responde
# com erro 422 sem precisarmos de escrever código para isso.
class ProdutoNovo(BaseModel):
    """Dados que o cliente envia para criar um produto."""

    nome: str = Field(min_length=1, max_length=100, description="Nome do produto")
    preco: float = Field(gt=0, description="Preço em euros (tem de ser maior que 0)")


class Produto(ProdutoNovo):
    """Produto guardado: os mesmos campos, mais o identificador."""

    id: int


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