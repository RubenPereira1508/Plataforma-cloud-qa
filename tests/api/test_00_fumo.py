"""
test_00_fumo.py – testes de fumo da API (Passo 7)

O que faz:
    Verifica o mínimo: a API está viva, está pronta e consegue listar produtos.

Porque existe:
    Um "teste de fumo" responde à pergunta "vale a pena correr os outros
    testes?". Se estes falham, a API está avariada ou mal arrancada, e os
    restantes testes só iriam produzir ruído. O nome vem do hardware: ligar a
    placa e ver se deita fumo.

Estrutura de cada teste (Arrange, Act, Assert):
    1) preparar o que for preciso;
    2) fazer UMA ação (o pedido HTTP);
    3) verificar o resultado com "assert".
"""

import pytest

# Todos os testes deste ficheiro levam a etiqueta "fumo".
pytestmark = pytest.mark.fumo


def test_saude_responde_ok(cliente):
    """GET /saude (liveness): o processo está vivo."""
    resposta = cliente.get("/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"estado": "ok"}


def test_pronto_responde_ok(cliente):
    """GET /pronto (readiness): a API consegue falar com a base de dados."""
    resposta = cliente.get("/pronto")

    assert resposta.status_code == 200
    assert resposta.json() == {"estado": "pronto"}


def test_listar_produtos_devolve_uma_lista(cliente):
    """GET /produtos: responde 200 e devolve uma lista (não um objeto)."""
    resposta = cliente.get("/produtos")

    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
