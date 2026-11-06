# Passo 03 – Terraform: infraestrutura como código

**Objetivo:** perceber o que é infraestrutura como código, aprender o ciclo do Terraform (`init`, `plan`, `apply`, `destroy`) e começar a criar a base da plataforma na AWS (estado remoto e rede).

**Partes deste passo:**

- A. Teoria e instalação do Terraform ✅
- B. Primeiro recurso: um bucket S3 de teste
- C. Estado remoto (bucket S3 para o *state*) (por fazer)
- D. Rede: VPC, sub-redes e internet gateway (por fazer)
- E. Fecho: outputs, destroy, documentação e commit (por fazer)

---

## 1. Teoria

### 1.1 Declarativo: descrever o resultado, não os passos

Há duas formas de pedir a alguém que construa uma casa:

- **Dar instruções passo a passo** ("compra tijolos, faz as fundações..."). Se a casa já existir pela metade, as instruções falham ou duplicam coisas.
- **Entregar a planta** ("quero uma casa com estes quartos"). Quem constrói vê o que já existe e faz só o que falta.

O Terraform funciona com a planta. Escreves o que queres que exista e ele descobre o que falta criar, alterar ou apagar. Chama-se programação **declarativa**.

### 1.2 Porquê Terraform e não consola, CLI ou outras ferramentas

| Forma | Problema para um projeto como este |
|---|---|
| Consola (cliques) | Não deixa registo e não se repete igual |
| AWS CLI (comandos) | Boa para tarefas pontuais, difícil de manter e desfazer |
| SDKs (código) | Demasiado trabalho para descrever infraestrutura |
| CloudFormation / CDK | Faz o mesmo, mas só funciona na AWS |
| **Terraform** | Infraestrutura como código, versionada no Git, reprodutível, funciona em várias clouds e é muito pedida no mercado |

### 1.3 As peças

| Conceito | Analogia | O que é |
|---|---|---|
| **Provider** | O tradutor | Plugin que sabe falar com uma plataforma (o `aws` fala com a AWS) |
| **Resource** | Um item da planta | Algo a criar (bucket, sub-rede, servidor) |
| **Data source** | Uma consulta | Lê informação que já existe, sem criar nada |
| **Variable** | Um campo a preencher | Valor que se pode mudar sem mexer no resto |
| **Output** | O recibo | Informação mostrada no fim |
| **Module** | Um bloco reutilizável | Conjunto de recursos que se usa várias vezes |
| **State** | A memória | Ficheiro onde o Terraform regista o que criou |

### 1.4 O ciclo de trabalho

```
terraform init  →  terraform plan  →  terraform apply  →  terraform destroy
```

| Comando | O que faz |
|---|---|
| `terraform init` | Prepara a pasta e descarrega os providers. Corre-se uma vez por projeto (e quando mudam os providers). |
| `terraform fmt` | Formata os ficheiros no estilo padrão. |
| `terraform validate` | Verifica se o código está bem escrito (sem ligar à AWS). |
| `terraform plan` | **Simula**: mostra o que seria criado (`+`), alterado (`~`) ou apagado (`-`). Não muda nada. |
| `terraform apply` | **Executa** o plano, depois de escreveres `yes`. |
| `terraform destroy` | Apaga tudo o que o Terraform criou nessa pasta. |

**Regra de ouro:** ler sempre o `plan` antes do `apply`.

### 1.5 O state

O state é o "caderno de memória" do Terraform: guarda quais recursos ele criou e as suas propriedades. Sem ele, o Terraform não saberia o que já existe.

- **Não vai para o Git:** pode conter dados sensíveis (está no `.gitignore`).
- **Não deve ficar só no teu portátil:** se o perderes, o Terraform "esquece" o que criou e os recursos ficam na AWS a gastar sem controlo.
- **Estado remoto:** guarda-se num bucket S3 cifrado, com versões e sem acesso público (Parte C).
- **Bloqueio (lock):** evita que duas execuções (tu e a pipeline, por exemplo) alterem o estado em simultâneo.

### 1.6 Idempotência e drift

- **Idempotente:** correr o `apply` duas vezes seguidas não muda nada à segunda, porque já está tudo como descrito.
- **Drift:** se alguém mudar algo à mão na consola, o `plan` seguinte mostra a diferença entre o código e a realidade. Por isso não se mexe à mão no que o Terraform gere.

### 1.7 Como se lê um ficheiro `.tf`

```hcl
provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "meu_bucket" {
  bucket = "nome-unico-do-bucket"
}
```

A estrutura é `tipo "nome_do_tipo" "nome_interno" { propriedades }`. O Terraform lê todos os `.tf` da pasta. Por convenção: `versions.tf` (versões), `main.tf` (recursos), `variables.tf` (entradas) e `outputs.tf` (saídas).

Um recurso pode **referir** outro (`aws_s3_bucket.teste.id`). É assim que o Terraform percebe a ordem: cria primeiro o que é referido.

### 1.8 O ficheiro `.terraform.lock.hcl`

Criado pelo `terraform init`, fixa as versões exatas dos providers usados. **Deve ir para o Git**, para que toda a gente (e a pipeline) use exatamente as mesmas. A pasta `.terraform/`, essa, não vai.

### 1.9 Custos e regras de segurança

| Recurso | Custo |
|---|---|
| VPC, sub-redes, internet gateway, tabelas de rotas, security groups | Gratuitos |
| Bucket S3 (poucos ficheiros) | Praticamente nada |
| NAT Gateway, EKS, instâncias EC2 | **Cobram por hora** |

Regras que seguimos:

1. Só criamos o que o passo pede.
2. Evitamos o que cobra por hora até ser mesmo preciso.
3. Lemos o `plan` antes do `apply`.
4. No fim de cada sessão: `terraform destroy` e verificação de que não ficou nada ligado.
5. Tudo na mesma região (`eu-north-1`).

---

## 2. Prática

### Parte A – Instalar o Terraform ✅

```powershell
winget install Hashicorp.Terraform
terraform -version
```

No VS Code, instala a extensão **HashiCorp Terraform**.

### Parte B – Primeiro recurso: um bucket S3 de teste

**1. Ficheiros.** Cria a pasta `infra/00-exercicio-s3/` com 4 ficheiros:

```
infra/00-exercicio-s3/
├── versions.tf    # versões do Terraform e dos providers
├── main.tf        # provider, data source e recursos
├── variables.tf   # variável da região
└── outputs.tf     # o que é mostrado no fim
```

O que o código cria:

| Recurso | Para quê |
|---|---|
| `random_id.sufixo` | Sufixo aleatório, porque os nomes de buckets S3 são únicos no mundo |
| `aws_s3_bucket.teste` | O bucket em si |
| `aws_s3_bucket_public_access_block.teste` | Fecha todo o acesso público ao bucket |

**2. Entrar na pasta e preparar:**

```bash
cd infra/00-exercicio-s3
terraform init
terraform fmt
terraform validate
```

O `init` descarrega os providers `aws` e `random` e cria a pasta `.terraform/` e o ficheiro `.terraform.lock.hcl`. O `validate` deve dizer `Success! The configuration is valid.`

**3. Ver o plano (sem criar nada):**

```bash
terraform plan
```

Lê o resultado. Deves ver 3 recursos com `+` (a criar) e no fim `Plan: 3 to add, 0 to change, 0 to destroy.` Repara que alguns valores aparecem como `(known after apply)`: só se sabem depois de criados.

**4. Criar:**

```bash
terraform apply
```

Escreve `yes` quando pedir. No fim aparecem os **outputs** (nome do bucket, região e número da conta).

**5. Confirmar na AWS (de duas formas):**

```bash
aws s3 ls
terraform output
```

O bucket deve aparecer na lista. Podes também vê-lo na consola, em S3 (com a região `eu-north-1`).

**6. Provar a idempotência:**

```bash
terraform plan
```

Deve dizer `No changes. Your infrastructure matches the configuration.`

**7. Destruir:**

```bash
terraform destroy
```

Lê o que vai apagar, escreve `yes`, e confirma com `aws s3 ls` que o bucket desapareceu.

**8. Guardar no Git** (volta primeiro à raiz do projeto):

```bash
cd ../..
git status
git add .
git commit -m "feat: exercício de Terraform com bucket S3"
git push
```

No `git status` confirma que **não** aparecem a pasta `.terraform/` nem ficheiros `.tfstate`, e que o `.terraform.lock.hcl` **aparece** (esse deve ir).

**Prova visual:** o bucket criado pelo Terraform, visto na consola AWS (S3, região Europa/Estocolmo). A data de criação (16:03:58) coincide com o momento do `apply`.

![Bucket S3 criado pelo Terraform, visto na consola AWS](imagens/passo-03-bucket-s3-consola.png)

### Parte C – Estado remoto (por fazer)

### Parte D – Rede: VPC (por fazer)

### Parte E – Fecho (por fazer)

---

## 3. Registo do que fizeste

| Tarefa | Feito | Data | Notas |
|---|---|---|---|
| Terraform instalado | ✅ | 2026-11-05 | |
| `init`, `validate` e `plan` do exercício | ✅ | 2026-11-05 | Plano: 3 a criar, 0 a alterar, 0 a apagar |
| `apply`: bucket criado | ✅ | 2026-11-06 | 3 recursos criados |
| Bucket visto com `aws s3 ls` e na consola | ✅ | 2026-11-06 | Imagem em `docs/imagens/` |
| `plan` sem alterações (idempotência) | ✅ | | |
| `destroy`: bucket removido | ✅ | | |
| Commit e push | ✅ | | |

## 4. Para a entrevista

**O que é infraestrutura como código e porque se usa?**
É descrever a infraestrutura em ficheiros versionados, em vez de a criar à mão. Torna-a reprodutível, revisável e fácil de destruir e recriar.

**Qual é a diferença entre programação declarativa e imperativa?**
Na declarativa descrevo o resultado pretendido e a ferramenta decide os passos (Terraform). Na imperativa descrevo os passos, um a um.

**Qual é a diferença entre `terraform plan` e `terraform apply`?**
O `plan` simula e mostra o que mudaria, sem alterar nada. O `apply` executa as mudanças. Lê-se sempre o `plan` antes de aplicar.

**O que é o state do Terraform e porque se guarda remotamente?**
É o registo do que o Terraform criou. Guarda-se remotamente (por exemplo, num bucket S3 cifrado e com versões) para não se perder, para poder ser partilhado e para evitar execuções simultâneas com bloqueio. Não vai para o Git porque pode conter dados sensíveis.

**O que é drift e como se deteta?**
É a diferença entre o código e a infraestrutura real, por exemplo quando alguém muda algo à mão. Deteta-se com o `terraform plan`.

**O que é um provider?**
Um plugin que permite ao Terraform falar com uma plataforma (AWS, Azure, etc.).

**Para que serve o `.terraform.lock.hcl`?**
Fixa as versões exatas dos providers, para que todos usem as mesmas. Vai para o Git.