# Passo 04 – CI/CD com GitHub Actions

**Objetivo:** automatizar as verificações do projeto. A cada `push`, uma pipeline valida o Terraform, constrói as imagens Docker e procura vulnerabilidades, sem ninguém ter de correr comandos à mão.

**Partes deste passo:**

- A. Teoria e primeira pipeline: verificar o Terraform (em curso)
- B. Construir as imagens Docker na pipeline (por fazer)
- C. Procurar vulnerabilidades com o Trivy (por fazer)
- D. Ligar a pipeline à AWS sem chaves (OIDC) e publicar imagens no ECR (por fazer)
- E. Fecho: proteção da branch, documentação e commit (por fazer)

---

## 1. Teoria

### 1.1 O problema que a pipeline resolve

Até agora, para saber se o código estava bem, corrias os comandos tu (`terraform validate`, `docker compose up`...). Isso tem dois problemas:

- **Esquecimento:** um dia não corres, e o erro segue para a frente.
- **"Na minha máquina funciona":** o teu computador não é igual ao de outra pessoa.

Uma pipeline corre as verificações **automaticamente**, sempre da mesma forma, numa máquina limpa. Se algo falhar, vês logo.

### 1.2 CI e CD

| Sigla | Significa | O que faz |
|---|---|---|
| **CI** | Integração contínua | A cada alteração, verifica automaticamente (formato, validação, testes, build) |
| **CD** | Entrega (ou *deploy*) contínua | Depois de verificar, publica ou instala automaticamente |

Neste passo começamos pela **CI**. A parte de CD (publicar no Kubernetes) vem no Passo 5, com o ArgoCD.

### 1.3 As peças do GitHub Actions

| Conceito | Analogia | O que é |
|---|---|---|
| **Workflow** | A receita completa | Ficheiro `.yml` em `.github/workflows/` que descreve a pipeline |
| **Evento (`on`)** | O gatilho | O que a faz arrancar (um `push`, um pull request, uma hora marcada) |
| **Job** | Uma tarefa | Um grupo de passos que corre numa máquina. Jobs diferentes correm em paralelo |
| **Step** | Um passo | Um comando (`run`) ou uma ação pronta (`uses`) |
| **Runner** | A máquina emprestada | O computador (aqui `ubuntu-latest`) que o GitHub arranca para correr o job e deita fora no fim |
| **Action** | Uma peça pronta | Passo reutilizável feito por outros (ex.: `actions/checkout` descarrega o código) |
| **Matrix** | A fotocopiadora | Corre o mesmo job várias vezes com valores diferentes |
| **Secret** | O cofre | Valor sensível guardado no GitHub, que não aparece nos logs |

### 1.4 Porquê começar sem a AWS

A primeira pipeline só **lê** o código: verifica o formato e valida. Não precisa de chaves da AWS, por isso não há segredos em jogo. Mais tarde, para publicar imagens no ECR, ligamos a pipeline à AWS de forma segura (OIDC), sem guardar chaves no GitHub.

### 1.5 Menor privilégio também aqui

O workflow declara `permissions: contents: read`: só pode ler o repositório. Se um passo for comprometido (por exemplo, uma action de terceiros), não consegue escrever nada. É o mesmo princípio do IAM.

---

## 2. Prática

### Parte A – Teoria e primeira pipeline: verificar o Terraform

O ficheiro `.github/workflows/ci.yml` tem dois jobs:

| Job | O que faz |
|---|---|
| `formato-terraform` | `terraform fmt -check`: falha se algum ficheiro `.tf` estiver mal formatado |
| `validar-terraform` | Corre `init -backend=false` e `validate` em cada uma das três pastas (com *matrix*) |

O `-backend=false` evita ligar ao bucket do state, por isso não são precisas credenciais.

**1. Cria a pasta e o ficheiro.** Na raiz do projeto, cria `.github/workflows/` e coloca lá o `ci.yml`.

**2. Guarda no Git e envia:**

```bash
git status
git add .
git commit -m "ci: pipeline que verifica formato e valida o Terraform"
git push
```

**3. Vê a pipeline a correr.** No GitHub, abre o repositório e vai ao separador **Actions**. Vais ver o workflow **CI** a correr. Clica nele para ver os jobs. Deve ficar tudo a verde (4 jobs: 1 de formato e 3 de validação).

**4. Provoca uma falha de propósito** (para perceber que a pipeline serve de alguma coisa). No `infra/02-rede/variables.tf`, estraga o alinhamento: apaga os espaços à volta de um `=`. Faz commit e push. O job de formato deve ficar a **vermelho**, e o log mostra a diferença. Depois corrige com `terraform fmt -recursive infra`, faz novo commit, e volta a verde.

**Prints desta parte:**

| Quando | O que mostrar | Nome sugerido |
|---|---|---|
| Pipeline a verde | O separador Actions com a execução e os jobs em verde | `passo-04-pipeline-verde.png` |
| Falha provocada | O job de formato a vermelho, com o log da diferença | `passo-04-pipeline-falha-formato.png` |

### Parte B – Construir as imagens Docker na pipeline (por fazer)

### Parte C – Procurar vulnerabilidades com o Trivy (por fazer)

### Parte D – Ligar a pipeline à AWS sem chaves (OIDC) e publicar imagens no ECR (por fazer)

### Parte E – Fecho (por fazer)

---

## 3. Registo do que fizeste

| Tarefa | Feito | Data | Notas |
|---|---|---|---|
| Workflow `ci.yml` criado e enviado | ☐ | | |
| Pipeline a verde (4 jobs) | ☐ | | |
| Falha de formato provocada e corrigida | ☐ | | |
| Prints guardados | ☐ | | |
| Commit e push | ☐ | | |

## 4. Para a entrevista

**O que é CI/CD e porque se usa?**
CI é verificar automaticamente cada alteração (formato, testes, build). CD é publicar ou instalar automaticamente depois de verificar. Reduz erros humanos e dá feedback rápido.

**Qual é a diferença entre um job e um step?**
Um job é um grupo de passos que corre numa máquina. Um step é um passo individual, um comando ou uma action. Jobs diferentes correm em paralelo; os steps de um job correm em sequência.

**O que é um runner?**
A máquina onde o job corre. No GitHub, é uma máquina temporária que é criada para o job e destruída no fim.

**Para que serve uma matrix?**
Para correr o mesmo job várias vezes com valores diferentes (aqui, uma vez por pasta do Terraform), sem copiar o código.

**Porque se define `permissions: contents: read`?**
Aplica o menor privilégio: o workflow só pode ler o repositório, por isso um passo comprometido não consegue alterar nada.

**Porque se usa `terraform init -backend=false` na pipeline?**
Para validar o código sem ligar ao state remoto, e por isso sem precisar de credenciais da AWS.
