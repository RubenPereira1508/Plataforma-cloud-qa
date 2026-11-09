"""
conftest.py – peças partilhadas por todos os testes da API (Passo 7)

O que faz:
    Define as "fixtures" do pytest: preparação reutilizável que os testes
    pedem pelo nome. O pytest carrega este ficheiro automaticamente.

Porque existe:
    Sem isto, cada teste teria de repetir "qual é o endereço da API?" e
    "cria o cliente HTTP". Num único sítio fica mais simples de manter.

Contra o que corre:
    Os testes são "de caixa-preta": falam com a API em execução, por HTTP,
    tal como um cliente real, sem importar o código dela. Por isso o mesmo
    teste serve para a API no Docker Compose e no Kubernetes; basta mudar a
    variável de ambiente API_URL.

        Compose (omissão):  http://localhost:8000
        Kubernetes:         API_URL=http://localhost:8000 com
                            "kubectl port-forward svc/api -n loja 8000:8000"
"""

import os
import uuid

import httpx
import pytest

# Endereço da API a testar. Vem do ambiente; se não existir, assume o Compose.
API_URL = os.environ.get("API_URL", "http://localhost:8000")


def pytest_sessionstart(session):
    """Corre ANTES de todos os testes: confirma que a API responde.

    Porquê: se a API estiver desligada, 30 testes a falhar com erros de ligação
    escondem a causa real. É melhor parar logo com uma mensagem clara.
    """
    try:
        httpx.get(f"{API_URL}/saude", timeout=5)
    except httpx.HTTPError as erro:
        pytest.exit(
            f"A API não responde em {API_URL} ({erro.__class__.__name__}).\n"
            "Arranca-a (docker compose up -d --build) ou define API_URL.",
            returncode=2,
        )


@pytest.fixture(scope="session")
def cliente():
    """Cliente HTTP já apontado para a API (uma única ligação para toda a sessão).

    base_url: nos testes escreve-se só o caminho ("/produtos"), não o endereço
    completo.
    timeout=5: se a API não responder em 5 segundos, o teste falha em vez de
    ficar preso para sempre.
    """
    with httpx.Client(base_url=API_URL, timeout=5) as c:
        yield c


def nome_unico(prefixo: str = "teste") -> str:
    """Gera um nome que não colide com outros produtos.

    Porquê: a API não tem DELETE, por isso os produtos criados pelos testes
    ficam na base de dados. Com nomes únicos, cada teste encontra o SEU produto
    sem depender do estado deixado por execuções anteriores. O prefixo
    "teste-" também permite identificá-los facilmente.
    """
    return f"{prefixo}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def produto(cliente):
    """Cria um produto novo e devolve-o (o JSON que a API respondeu).

    Porquê uma fixture: vários testes precisam de "um produto que existe".
    Em vez de cada um o criar à mão, pedem "produto" e recebem um já criado,
    com nome único. Cada teste obtém o SEU produto, por isso são independentes
    uns dos outros.

    O "assert" aqui garante que a PREPARAÇÃO correu bem: se a criação falhar,
    o teste falha logo com uma mensagem a dizer que o problema foi a
    preparação, e não o que o teste queria verificar.
    """
    corpo = {"nome": nome_unico(), "preco": 12.5}
    resposta = cliente.post("/produtos", json=corpo)
    assert resposta.status_code == 201, f"A preparação falhou: {resposta.text}"
    return resposta.json()