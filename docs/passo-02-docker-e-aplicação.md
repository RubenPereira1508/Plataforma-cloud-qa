# Passo 02 – Docker e a aplicação da loja

**Objetivo:** perceber o que são contentores, construir a nossa própria imagem Docker e pôr a API da loja a correr no teu computador.

**Partes deste passo:**

- A. Primeiros contentores (`hello-world`, `nginx`) ✅
- B. Construir a imagem da API e correr o contentor ✅
- C. Juntar uma base de dados PostgreSQL com Docker Compose ✅
- D. Frontend simples com nginx

---

## 1. Teoria

### 1.1 O que é um contentor?

Um contentor é uma "caixa" que leva uma aplicação **e tudo o que ela precisa para correr** (bibliotecas, configurações). Corre da mesma forma no teu portátil, no de um colega ou num servidor na AWS. Resolve o clássico "no meu computador funciona".

### 1.2 Contentor vs máquina virtual

Uma máquina virtual leva um sistema operativo inteiro. Um contentor **partilha o sistema operativo** do computador e só isola a aplicação. Por isso é muito mais leve e arranca em segundos.

### 1.3 Os quatro conceitos essenciais

| Conceito | Analogia | O que é |
|---|---|---|
| **Imagem** | A receita de um bolo | Modelo só de leitura, com a aplicação e tudo o que precisa |
| **Contentor** | O bolo feito | Uma imagem em execução |
| **Dockerfile** | O papel onde escreves a receita | Ficheiro com as instruções para construir uma imagem |
| **Registry** | Uma biblioteca de receitas | Onde se guardam imagens (Docker Hub; mais tarde, o ECR da AWS) |

### 1.4 Camadas e cache

Cada instrução do Dockerfile cria uma **camada**. O Docker guarda-as em cache. Se uma camada não mudou, reaproveita-a. Por isso se coloca primeiro o que muda pouco (instalar dependências) e só depois o que muda muito (o código). Resultado: construções muito mais rápidas.

### 1.5 Portas

Um contentor tem a sua própria rede. Para o aceder a partir do teu computador, **publicas** uma porta com `-p PORTA_TEU_PC:PORTA_CONTENTOR`. Exemplo: `-p 8000:8000`.

### 1.6 Boas práticas que aplicamos já

- **Imagem base pequena** (`python:3.12-slim`): menos tamanho e menos superfície de ataque.
- **Não correr como root:** um utilizador sem poderes dentro do contentor.
- **`.dockerignore`:** impede que segredos ou lixo entrem na imagem.
- **Health check:** o Docker (e mais tarde o Kubernetes) consegue perguntar se a aplicação está viva.

### 1.7 A API da loja

É uma API em Python (FastAPI) com 4 endpoints:

| Método | Endereço | O que faz |
|---|---|---|
| GET | `/saude` | Diz se a API está viva |
| GET | `/produtos` | Lista os produtos |
| GET | `/produtos/{id}` | Devolve um produto (ou 404) |
| POST | `/produtos` | Cria um produto (ou 422 se os dados forem inválidos) |

Neste momento os dados ficam em memória. No Passo C passamos para PostgreSQL.

**Porque uma aplicação própria e não uma já feita?** Para perceberes cada peça. Além disso, uma aplicação controlada por nós permite criar testes e falhas à medida no Projeto B.

### 1.8 Porque precisamos de uma base de dados

Os contentores são **descartáveis**: podem ser apagados e recriados a qualquer momento. Tudo o que está dentro do contentor perde-se com ele. Por isso os dados importantes ficam numa **base de dados**, e esta guarda-os num **volume**, uma pasta gerida pelo Docker que sobrevive aos contentores.

### 1.9 Docker Compose

Em vez de escreveres vários `docker run` compridos, descreves tudo num ficheiro `docker-compose.yml`: que contentores existem, como se ligam e que configuração levam. Um só comando (`docker compose up`) arranca tudo.

- Os contentores do mesmo Compose partilham uma **rede privada** e encontram-se pelo **nome do serviço**. Por isso a API fala com `db`, e não com um endereço IP.
- **`depends_on` com `service_healthy`:** a API só arranca depois de a base de dados estar pronta.

### 1.10 Configuração e segredos (variáveis de ambiente)

A palavra-passe da base de dados **não** está no código nem no Compose. Vem de variáveis de ambiente, lidas de um ficheiro `.env` que **não vai para o Git**. O ficheiro `.env.example` vai, como modelo sem segredos. É a mesma ideia que mais tarde aplicamos na AWS com um gestor de segredos.

### 1.11 Liveness vs readiness

| Verificação | Pergunta | Se falhar |
|---|---|---|
| `/saude` (liveness) | "O processo está vivo?" | Reinicia-se o contentor |
| `/pronto` (readiness) | "Estou pronto a receber pedidos (tenho base de dados)?" | Deixa-se de enviar tráfego, sem reiniciar |

Vamos precisar desta distinção no Kubernetes.

### 1.12 SQL injection

Os valores vão para a base de dados como **parâmetros** (`%s`), separados da instrução SQL. Nunca se constrói SQL juntando texto do utilizador, porque alguém podia enviar comandos maliciosos no lugar de um nome.

### 1.13 O frontend e o proxy inverso

O frontend é a parte que o utilizador vê: uma página HTML com JavaScript que pede dados à API. Quem a serve é o **nginx**, um servidor web muito leve.

O nginx faz também de **proxy inverso**: recebe os pedidos do browser e reencaminha os que começam por `/api/` para a API, por dentro da rede do Compose.

| Sem proxy | Com proxy inverso |
|---|---|
| O browser fala com dois endereços (página e API) | O browser fala com um só endereço |
| Problemas de **CORS** (o browser bloqueia pedidos entre origens diferentes) | Sem CORS: a origem é a mesma |
| A API tem de estar exposta ao exterior | A API pode ficar escondida na rede interna |

É a mesma ideia do **Ingress** no Kubernetes e do **Load Balancer** na AWS, que vamos usar mais à frente.

### 1.14 Pensar já nos testes (QA)

A página tem atributos `data-testid` (ex.: `data-testid="botao-criar"`). Os testes automáticos do Projeto B agarram-se a eles em vez de dependerem de textos ou estilos, que mudam com frequência. Os testes ficam assim mais estáveis. Outra boa prática: os dados da API entram na página com `textContent` e não com `innerHTML`, para evitar **XSS** (injeção de código malicioso).

---

## 2. Prática

### Parte A – Primeiros contentores ✅

```bash
docker run hello-world
docker run -d -p 8080:80 --name meu-nginx nginx
docker ps
docker stop meu-nginx
docker rm meu-nginx
```

| Comando | O que faz |
|---|---|
| `docker run IMAGEM` | Cria e arranca um contentor a partir de uma imagem (descarrega-a se não a tiver). |
| `-d` | Corre em segundo plano. |
| `-p 8080:80` | Liga a porta 8080 do teu computador à porta 80 do contentor. |
| `--name` | Dá um nome ao contentor. |
| `docker ps` | Lista os contentores a correr. |
| `docker stop` / `docker rm` | Pára / apaga um contentor. |

### Parte B – Construir a imagem da API e correr

**1. Ficheiros.** Na pasta do projeto, cria `app/api/` com estes 4 ficheiros:

```
app/api/
├── main.py            # código da API
├── requirements.txt   # dependências Python
├── Dockerfile         # receita da imagem
└── .dockerignore      # o que o Docker ignora
```

**2. Construir a imagem** (a partir da raiz do projeto):

```bash
docker build -t loja-api:0.1 app/api
```

- `build`: constrói uma imagem a partir de um Dockerfile.
- `-t loja-api:0.1`: dá-lhe o nome `loja-api` e a etiqueta (versão) `0.1`.
- `app/api`: a pasta onde está o Dockerfile (o "contexto").

Vais ver o Docker a executar cada passo do Dockerfile. Se voltares a correr o comando, as camadas em cache aparecem como `CACHED`.

**3. Ver a imagem criada:**

```bash
docker images
```

**4. Correr o contentor:**

```bash
docker run -d -p 8000:8000 --name loja-api loja-api:0.1
```

**5. Testar.** No browser:

- `http://localhost:8000/saude` deve mostrar `{"estado":"ok"}`.
- `http://localhost:8000/produtos` deve mostrar 2 produtos.
- `http://localhost:8000/docs` abre a documentação interativa. Experimenta criar um produto no `POST /produtos` e tenta enviar um preço negativo para veres o erro 422.

**6. Ver os registos (logs) e o estado de saúde:**

```bash
docker logs loja-api
docker ps
```

Na coluna `STATUS` deve aparecer `healthy` passado cerca de 30 segundos.

**7. Experiência para perceberes que os dados estão em memória:**

```bash
docker restart loja-api
```

Os produtos que criaste desaparecem. É por isso que vamos precisar de uma base de dados.

**8. Limpar:**

```bash
docker stop loja-api
docker rm loja-api
```

### Parte C – PostgreSQL com Docker Compose

**1. Ficheiros novos e alterados:**

```
.
├── docker-compose.yml        # novo (raiz do projeto)
├── .env.example              # novo (raiz do projeto)
├── .gitignore                # atualizado (exceção para o .env.example)
└── app/api/
    ├── main.py               # atualizado (agora usa PostgreSQL)
    └── requirements.txt      # atualizado (driver psycopg)
```

**2. Pára e remove o contentor antigo** (ocupa a porta 8000):

```bash
docker stop loja-api
docker rm loja-api
```

**3. Cria o teu `.env`** a partir do modelo e edita a palavra-passe:

```powershell
Copy-Item .env.example .env
```

Abre o `.env` no VS Code e muda `POSTGRES_PASSWORD` para uma palavra-passe tua. Confirma, com `git status`, que o `.env` **não** aparece como ficheiro a adicionar.

**4. Arranca tudo:**

```bash
docker compose up -d --build
docker compose ps
docker compose logs api
```

Deves ver os serviços `db` e `api` com estado `healthy`/`running`.

**5. Testa** em `http://localhost:8000/docs`: lista os produtos, cria um novo e experimenta também `GET /pronto`.

**6. A prova de que os dados persistem:**

```bash
docker compose restart api
```

Volta a listar os produtos: **o que criaste continua lá**. Depois vai mais longe:

```bash
docker compose down
docker compose up -d
```

`down` apaga os contentores, mas o **volume** fica, por isso os dados continuam lá.

**7. Espreitar a base de dados por dentro:**

```bash
docker compose exec db psql -U loja -d loja -c "SELECT * FROM produtos;"
```

(Se mudaste `POSTGRES_USER` ou `POSTGRES_DB` no `.env`, usa os teus valores.)

**8. Apagar também os dados (só para experimentar):**

```bash
docker compose down -v
```

O `-v` apaga os volumes. Ao arrancar de novo, a base de dados volta vazia (a API recria os 2 produtos iniciais).

| Comando | O que faz |
|---|---|
| `docker compose up -d --build` | Constrói as imagens e arranca tudo em segundo plano |
| `docker compose ps` | Mostra o estado dos serviços |
| `docker compose logs api` | Mostra os registos de um serviço |
| `docker compose exec db ...` | Corre um comando dentro de um contentor em execução |
| `docker compose down` | Para e remove contentores (o volume fica) |
| `docker compose down -v` | Idem, e apaga também os volumes (perdes os dados) |

### Parte D – Frontend com nginx

**1. Ficheiros novos** (cria a pasta `app/frontend/`):

```
app/frontend/
├── index.html        # a página (HTML + CSS + JavaScript)
├── nginx.conf        # serve a página e reencaminha /api para a API
├── Dockerfile        # imagem do frontend
└── .dockerignore
```

E **substitui** o `docker-compose.yml` da raiz pelo novo (tem um terceiro serviço, `frontend`).

**2. Arranca tudo** (reconstrói e junta o frontend):

```bash
docker compose up -d --build
docker compose ps
```

Deves ver 3 serviços: `db`, `api` e `frontend`, todos `healthy` ao fim de uns 30 segundos.

**3. Abre a loja:** `http://localhost:8080`

**4. Experimenta:**
- Vê a lista de produtos (vêm da base de dados, através da API).
- Cria um produto pelo formulário e confirma que aparece na lista.
- Tenta criar um com **preço negativo**: deve aparecer uma mensagem de erro (é a validação da API, o erro 422).
- Recarrega a página: os produtos continuam lá.

**5. Vê o proxy a funcionar.** Abre `http://localhost:8080/api/produtos` no browser: é a API, mas acedida **através do nginx**. Compara com `http://localhost:8000/produtos` (acesso direto): a resposta é a mesma.

**6. Vê o que cada contentor registou:**

```bash
docker compose logs frontend
docker compose logs api
```

No `frontend` aparecem os pedidos do browser, e na `api` os que o nginx reencaminhou.

**7. Guarda no GitHub:**

```bash
git status
git add .
git commit -m "feat: frontend com nginx e proxy para a API"
git push
```


---

## 3. Autoavaliação

1. Qual é a diferença entre uma imagem e um contentor?
2. Porque é que no Dockerfile copiamos o `requirements.txt` e instalamos as dependências **antes** de copiar o `main.py`?
3. O que significa `-p 8000:8000` no `docker run`?
4. Porque é que a aplicação usa `--host 0.0.0.0` e não `127.0.0.1`?
5. Porque é que o contentor não corre como `root`?
6. Porque é que os produtos desapareciam quando o contentor reiniciava, e porque deixaram de desaparecer?
7. O que é um volume e qual a diferença entre `docker compose down` e `docker compose down -v`?
8. Porque é que a API usa `db` como endereço da base de dados?
9. Porque é que a palavra-passe está num `.env` e não no `docker-compose.yml`? O que vai e o que não vai para o Git?
10. Qual é a diferença entre `/saude` e `/pronto`?
11. O que é um proxy inverso e que vantagens tem aqui?
12. Porque é que o frontend fala com `/api` e não diretamente com `localhost:8000`?
13. Porque é que a página usa `textContent` em vez de `innerHTML`?

---

## 4. Registo do que fizeste

| Tarefa | Feito | Data | Notas |
|---|---|---|---|
| Docker Desktop instalado | ✅ | 2026-11-05 | |
| `hello-world` e `nginx` | ✅ | 2026-11-05 | |
| Imagem `loja-api:0.1` construída | ✅ | 2026-11-05 | |
| API a responder em `localhost:8000` | ✅ | 2026-11-05 | Swagger em `/docs` |
| Health check `healthy` | ✅ | 2026-11-05 | |
| Dados perdem-se ao reiniciar (confirmado) | ✅ | 2026-11-05 | Com a versão em memória |
| `.env` criado (fora do Git) | ✅ | 2026-11-05 | |
| `docker compose up` com API + PostgreSQL | ✅ | 2026-11-05 | |
| Dados persistem após restart | ✅ | 2026-11-05 | |
| Frontend a funcionar em `localhost:8080` | ☐ | | |
| Proxy `/api` a funcionar | ☐ | | |
| Commit e push do Passo 2 | ☐ | | |

## 5. Para a entrevista

- O que é um contentor e em que difere de uma máquina virtual?
- O que é um Dockerfile e como funciona a cache de camadas?
- Porque é que não se deve correr um contentor como root?
- Para que serve um health check?
- Como é que evitas que segredos entrem numa imagem Docker?
- Qual é a diferença entre liveness e readiness?
- Porque é que os dados de uma base de dados num contentor ficam num volume?
- O que é SQL injection e como se evita?
- O que é um proxy inverso? Qual a diferença para um proxy normal?
- O que é CORS e como se evita ou resolve?
- O que é XSS e como se previne?