# Passo 07 – Estratégia de testes e testes da API

**Objetivo:** começar o Projeto B (Quality Engineering). Primeiro decidir **o que** se testa e **porquê** (estratégia), depois escrever testes automáticos da API da loja com `pytest`.

**Partes deste passo:**

- A. Estratégia de testes ✅
- B. Ambiente de testes e teste de fumo ✅
- C. Testes funcionais: caminho feliz e erros ✅
- D. Validação e casos limite, com 3 defeitos encontrados ✅
- E. Fecho (por fazer)

---

## 1. Teoria

### 1.1 O que é testar, e porquê automatizar

Testar é verificar que o software faz o que deve e **não** faz o que não deve. Um teste automático é código que faz essa verificação sozinho e dá sempre o mesmo resultado: passou ou falhou.

Automatizar compensa porque, a cada alteração (uma biblioteca nova, uma correção, um `git push`), os testes voltam a correr em segundos e dizem se algo que funcionava deixou de funcionar. A isto chama-se **teste de regressão**.

### 1.2 Níveis de teste e onde entram no projeto

Cada nível responde a uma pergunta diferente e usa uma ferramenta diferente:

| Nível | Pergunta | Ferramenta | Passo |
|---|---|---|---|
| **API (funcional)** | A API responde como está combinado, incluindo nos erros? | `pytest` + `httpx` | **7 (este)** |
| **Contrato** | Quem consome a API e quem a fornece continuam de acordo? | Pact | 8 |
| **Interface (E2E)** | A loja funciona no browser, de ponta a ponta? | Playwright | 8 |
| **Desempenho** | Aguenta carga? Quão rápida é? | k6 | 8 |
| **Segurança** | Tem vulnerabilidades conhecidas? | OWASP ZAP, Trivy | 8 e 4 |
| **Resiliência (caos)** | Recupera quando algo falha? | Falhas provocadas no Kubernetes | 9 |

Hoje só começamos pelo primeiro.

### 1.3 A pirâmide de testes

A regra prática é ter **muitos testes rápidos e baratos** na base e **poucos lentos e caros** no topo:

```text
          /  E2E (browser)  \        poucos: lentos, frágeis, caros
         /  Contrato, API    \       a camada do meio
        /  Unitários          \      muitos: rápidos, precisos
```

Os testes de API ficam no meio e têm uma boa relação custo-benefício: correm em milissegundos, verificam o comportamento real (HTTP, validação, base de dados) e não dependem de um browser.

### 1.4 Testes de caixa-preta

Os nossos testes **não importam o código da API**: fazem pedidos HTTP a uma API em execução, como um cliente real, e verificam as respostas. Vantagens: o mesmo teste serve para a API no Docker Compose e no Kubernetes (muda só o endereço), e não ficam presos aos detalhes internos do código.

### 1.5 Riscos da loja e o que cobre cada teste

Pensar em riscos antes de escrever testes evita testar o que é óbvio e esquecer o que importa.

| Risco | Exemplo | Resposta esperada | Parte |
|---|---|---|---|
| API indisponível ou sem base de dados | A API arranca mas a DB está em baixo | `/saude` 200, `/pronto` 503 | B |
| Produto inexistente | `GET /produtos/999999` | 404 com mensagem | C |
| Criar produto válido | `POST /produtos` com nome e preço | 201 e produto com `id` | C |
| O que se cria fica guardado | Criar e depois obter pelo `id` | Mesmos dados | C |
| Preço inválido | Preço 0, negativo ou texto | 422 | D |
| Nome inválido | Vazio ou com mais de 100 caracteres | 422 | D |
| Identificador absurdo | `GET /produtos/0`, `/-1`, `/9999999999` | 422 (fora dos limites) | D |
| Campos em falta ou tipo errado | Corpo vazio, JSON inválido | 422 | D |
| Injeção de SQL | Nome com `'; DROP TABLE produtos;--` | Guardado como texto, nada se parte | D |

### 1.6 O que torna um teste bom

- **Independente:** não depende de outro teste ter corrido antes.
- **Determinístico:** dá sempre o mesmo resultado nas mesmas condições.
- **Uma razão para falhar:** verifica uma coisa. Quando falha, sabe-se logo o quê.
- **Nome que explica:** `test_criar_produto_com_preco_negativo_devolve_422` diz tudo sem ler o código.
- **Estrutura Arrange, Act, Assert:** preparar, fazer **uma** ação, verificar com `assert`.

### 1.7 pytest e httpx

- **pytest** descobre as funções chamadas `test_*`, corre-as e resume o resultado.
- **Fixture:** preparação reutilizável que um teste pede pelo nome (aqui, `cliente`, o cliente HTTP já apontado para a API). Define-se em `conftest.py`.
- **Parametrização** (`@pytest.mark.parametrize`): o mesmo teste corre com vários valores de entrada, sem repetir código. Útil na Parte D.
- **Marcadores** (`@pytest.mark.fumo`): etiquetas para escolher que testes correr (`pytest -m fumo`).
- **httpx:** o cliente HTTP que faz os pedidos (`cliente.get("/produtos")`).

### 1.8 O comportamento combinado da API

Isto é o "contrato" que os testes verificam (vem do código em `app/api/main.py`):

| Pedido | Sucesso | Erros |
|---|---|---|
| `GET /saude` | 200 `{"estado": "ok"}` | n/a |
| `GET /pronto` | 200 `{"estado": "pronto"}` | 503 se a base de dados falhar |
| `GET /produtos` | 200 e lista de produtos | n/a |
| `GET /produtos/{id}` | 200 e o produto | 404 se não existe; 422 se `id` não estiver entre 1 e 2 147 483 647 |
| `POST /produtos` | 201 e o produto criado (com `id`) | 422 se o nome tiver menos de 1 ou mais de 100 caracteres, ou se o preço não for maior que 0 |

### 1.9 Limitação conhecida: a API não tem DELETE

Os produtos criados pelos testes **ficam** na base de dados. Duas consequências, que desenhámos para tratar:

1. Cada teste usa **nomes únicos** (`teste-3f9a1c2b`) para encontrar o seu produto, sem depender do que ficou de execuções anteriores.
2. Os testes **não assumem quantos produtos existem** (nunca verificam "a lista tem exatamente 2").

Para uma base limpa, `docker compose down -v` apaga o volume do Compose.

---

## 2. Prática

### Parte A – Estratégia ✅

Está escrita acima: níveis de teste, pirâmide, riscos da loja e contrato da API. É o mapa dos Passos 7, 8 e 9.

### Parte B – Ambiente de testes e teste de fumo ✅

**Ficheiros novos em `tests/api/`** (todos comentados):

| Ficheiro | Para que serve |
|---|---|
| `requirements-test.txt` | `pytest` e `httpx`. Separado do `requirements.txt` da API para o pytest não ir dentro da imagem Docker |
| `pytest.ini` | Opções por omissão e marcadores (`fumo`, `funcional`, `validacao`) |
| `conftest.py` | Fixture `cliente`, endereço da API (variável `API_URL`), verificação prévia de que a API responde, gerador de nomes únicos |
| `test_00_fumo.py` | Três testes de fumo: `/saude`, `/pronto`, `GET /produtos` |

**Passos** (Docker Desktop ligado):

```powershell
cd C:\dev\Plataforma-cloud-qa
python --version
```

Precisa de Python 3.10 ou superior. Se o comando não existir, instala-se em python.org (marcando "Add python.exe to PATH"). Depois arranca-se a loja no Compose (a API fica em `localhost:8000`) e prepara-se o ambiente de testes:

```powershell
docker compose up -d --build
cd tests\api
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-test.txt
.\.venv\Scripts\python -m pytest -v
```

Notas:
- `python -m venv .venv` cria um **ambiente virtual**: uma cópia isolada do Python onde as bibliotecas dos testes ficam instaladas, sem tocar no Python do sistema. A pasta `.venv/` já está no `.gitignore`.
- Usa-se `.\.venv\Scripts\python` em vez de ativar o ambiente, porque a ativação (`Activate.ps1`) pode ser bloqueada pela política de scripts do PowerShell.
- `-m pytest -v` corre o pytest com o modo detalhado (um teste por linha).

Resultado (a instalação trouxe `pytest 9.2.0` e `httpx 0.28.1`; o Python era o 3.14.7):

```text
platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\dev\Plataforma-cloud-qa\tests\api
configfile: pytest.ini
collected 3 items

test_00_fumo.py::test_saude_responde_ok PASSED                         [ 33%]
test_00_fumo.py::test_pronto_responde_ok PASSED                        [ 66%]
test_00_fumo.py::test_listar_produtos_devolve_uma_lista PASSED         [100%]

============================= 3 passed in 0.20s =============================
```

O pytest leu o `pytest.ini` (`configfile: pytest.ini`) e a API respondeu à verificação prévia do `conftest.py`.

### Parte C – Testes funcionais ✅

**Ficheiros:** `tests/api/test_10_produtos_funcional.py` (11 testes) e uma fixture nova no `conftest.py`, `produto`, que cria um produto com nome único e o entrega ao teste. Cada teste recebe o seu produto, por isso são independentes.

**O que verificam:**

| Grupo | Verificações |
|---|---|
| Criar | `POST /produtos` responde 201 com o produto e um `id`; a resposta só tem `id`, `nome` e `preco`; dois produtos têm ids diferentes e crescentes; o preço mínimo (0,01) é aceite; nomes com acentos e `€` voltam iguais |
| Ler | O que se cria pode ser lido pelo `id`; aparece na lista; a lista vem ordenada por `id`; todos os itens têm os campos certos |
| Erros | Um `id` que não existe dá 404 com `Produto não encontrado`; sucesso e erro respondem com JSON |

Resultado:

```text
collected 14 items
... (3 de fumo + 11 funcionais)
============================= 14 passed in 1.37s =============================
```

### Parte D – Validação e casos limite ✅

**Ficheiro:** `tests/api/test_20_validacao.py` (16 funções de teste, 34 execuções com a parametrização). A ideia é tentar partir a API: é nos erros e nos limites que costumam estar os defeitos.

**Técnicas usadas:**

- **Parametrização** (`@pytest.mark.parametrize`): o mesmo teste corre com vários valores de entrada, uma linha por caso.
- **Análise de valores-limite:** o último valor válido e o primeiro inválido de cada regra (nome com 100 e 101 caracteres, `id` 2147483647 e 2147483648).
- **`xfail` estrito:** documenta um defeito conhecido sem deixar a suite vermelha, e avisa quando for corrigido (ver abaixo).

| Grupo | Verificações |
|---|---|
| Nome inválido | Vazio, 101 caracteres, nulo, número, lista: 422 a apontar o campo `nome` |
| Preço inválido | Zero, negativo, texto, nulo, lista: 422 a apontar o campo `preco` |
| Corpo mal formado | `{}` (aponta os dois campos em falta), sem corpo, JSON cortado: 422; um pedido recusado não deixa produto na base de dados |
| Limites válidos | Nome com 1 e 100 caracteres; preço máximo `99999999.99` |
| Segurança básica | Injeção de SQL no nome fica como texto e a tabela continua a existir; um `id` enviado pelo cliente é ignorado (evita *mass assignment*) |
| Identificadores | `0`, `-1`, `2147483648`, um número enorme, `abc`, `1.5`: todos 422 |
| Métodos e endereços | `DELETE`, `PUT` e `POST` em endereços que não os suportam: 405; endereço desconhecido: 404 |

**Resultado:**

```text
collected 48 items
...
========================== 45 passed, 3 xfailed in 3.36s ==========================
```

#### Defeitos encontrados

Ao ler o código suspeitei de três defeitos: a validação da API só exige `preco > 0`, mas a base de dados tem regras próprias (`NUMERIC(10, 2)` e `CHECK (preco > 0)`) que a API não verifica à entrada. Escrevi os testes com o comportamento **correto** e marquei-os `xfail` estrito.

O `xfail` só prova que o teste falha, não **porquê**. Para registar o que a API faz de facto, correu-se o pytest com o marcador desligado:

```powershell
.\.venv\Scripts\python -m pytest --runxfail -k "acima_do_limite or arredonda or so_com_espacos"
```

```text
E  assert 500 == 422     (preço 1 000 000 000)
E  assert 500 == 422     (preço 0.001)
E  assert 201 == 422     (nome "   ")
```

| ID | Defeito | Passos | Esperado | Obtido | Gravidade |
|---|---|---|---|---|---|
| DEF-01 | Preço acima do limite da base de dados rebenta a API | `POST /produtos` com `preco: 1000000000` | 422 a indicar o limite | **500 Internal Server Error** (a base de dados rejeita por overflow e o erro não é tratado) | Média |
| DEF-02 | Preço que arredonda para zero rebenta a API | `POST /produtos` com `preco: 0.001` | 422 | **500** (a base arredonda para 0.00 e viola o `CHECK (preco > 0)`) | Média |
| DEF-03 | Nome só com espaços é aceite | `POST /produtos` com `nome: "   "` | 422 | **201 Created** (tem 3 caracteres, passa `min_length=1`) | Baixa |

**Porque a gravidade:** um 500 num dado que o cliente pode enviar é um defeito de robustez (mostra um erro interno em vez de uma mensagem útil), e pode ser provocado por qualquer pessoa. Um nome vazio na prática é um problema de qualidade dos dados.

**Correção possível (por fazer):** no modelo `ProdutoNovo`, `preco` com `ge=0.01, le=99999999.99` (resolve DEF-01 e DEF-02, porque 0.001 fica abaixo de 0.01) e `nome` com remoção de espaços antes de validar (resolve DEF-03). Quando se corrigir, os três testes passam a verde, o `xfail` estrito faz a suite falhar a avisar, e remove-se o marcador.

**Efeito secundário a ter em conta:** o teste do nome só com espaços cria mesmo um produto "   " na base de dados, e a API não tem `DELETE`. Para uma base limpa: `docker compose down -v`.

## 3. Registo do que fizeste

| Tarefa | Estado | Data | Notas |
|---|---|---|---|
| Estratégia de testes escrita (Parte A) | ✅ | 2026-11-09 | |
| Python instalado e verificado | ✅ | 2026-11-09 | 3.14.7 |
| Ambiente virtual e dependências instaladas | ✅ | 2026-11-09 | |
| 3 testes de fumo a passar | ✅ | 2026-11-09 | |
| Commit e push da Parte B | ☐ | | |
| C: 11 testes funcionais a passar | ✅ | 2026-11-09 | `14 passed` |
| D: testes de validação e casos limite | ✅ | 2026-11-09 | `45 passed, 3 xfailed` |
| D: 3 defeitos confirmados com `--runxfail` | ✅ | 2026-11-09 | DEF-01 (500), DEF-02 (500), DEF-03 (201) |
| Commit e push das Partes C e D | ☐ | | |

## 4. Para a entrevista

**Porque se começa pela estratégia e não pelos testes?**
Para decidir o que se testa a partir dos riscos do sistema, em vez de testar só o que é fácil. A estratégia diz que nível de teste cobre cada risco e evita lacunas e repetição.

**O que é a pirâmide de testes?**
A regra de ter muitos testes rápidos e baratos na base (unitários), alguns no meio (API, contrato) e poucos no topo (browser de ponta a ponta), porque os do topo são lentos, caros e frágeis.

**O que é um teste de fumo?**
Uma verificação mínima e rápida de que o sistema está vivo e responde. Se falhar, não vale a pena correr os restantes testes.

**Porque são testes de caixa-preta?**
Porque falam com a API por HTTP, como um cliente real, sem importar o código dela. O mesmo teste serve para a API no Compose e no Kubernetes.

**Como lidaste com a API não ter DELETE?**
Cada teste usa nomes únicos e nunca assume quantos produtos existem, por isso não depende de dados de execuções anteriores.

**Como testaste a validação da API?**
Com parametrização e análise de valores-limite: nome vazio, com 100 e 101 caracteres, preço zero, negativo, texto e nulo, identificadores `0`, `-1` e acima do máximo de 32 bits, corpo vazio ou cortado, métodos não suportados e injeção de SQL.

**Encontraste algum defeito?**
Três. Um preço acima de 99999999.99 e um preço de 0.001 rebentavam a API com um 500 (a validação deixa passar e a base de dados rejeita), e um nome só com espaços era aceite com 201. Suspeitei ao ler o código, escrevi os testes com o comportamento correto, marquei-os `xfail` estrito e confirmei os códigos reais com `--runxfail`.

**O que é um `xfail` estrito e para que serve?**
Marca um teste que se sabe que falha por um defeito conhecido. A suite continua verde com o defeito documentado, e se a API for corrigida o teste passa e a suite falha a avisar que o marcador deve ser removido. É a diferença entre documentar um defeito e escondê-lo.

**O que é *mass assignment* e como o testaste?**
Quando a API aceita campos que o cliente não devia controlar (como o `id`). Enviei um `id` no corpo e verifiquei que o produto criado tinha outro, gerado pela base de dados.