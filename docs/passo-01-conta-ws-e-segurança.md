# Passo 01 – Conta AWS segura, repositório Git, IAM, orçamento e CLI

**Objetivo:** ter uma conta AWS pronta e segura para trabalhar, um repositório Git para guardar o projeto, alertas de custo e a linha de comandos configurada.

**Duração estimada:** 2 a 3 horas.

**Partes deste passo:**

1. Criar a conta AWS (plano gratuito)
2. Proteger a conta de login com verificação em dois passos
3. Criar o repositório Git e enviar a documentação
4. Criar o utilizador IAM de trabalho
5. Criar o orçamento com alertas
6. Instalar e testar a AWS CLI

---

## 1. Teoria

### 1.1 O que é a cloud?

Cloud computing é o acesso, a pedido e através da internet, a recursos informáticos (computação, armazenamento, bases de dados, redes), pagando apenas pelo que se usa. As vantagens principais são a rapidez de criação de recursos, a escala flexível e a ausência de investimento inicial em hardware.

Os três modelos de serviço:

- **IaaS:** alugas a infraestrutura (máquinas virtuais, redes). Exemplo: EC2.
- **PaaS:** alugas uma plataforma onde só colocas o código. Exemplo: Elastic Beanstalk.
- **SaaS:** usas o software já pronto. Exemplo: Gmail.

### 1.2 Regiões e zonas de disponibilidade

A AWS divide-se em **regiões** (zonas geográficas). Cada região tem várias **zonas de disponibilidade (AZ)**, que são centros de dados isolados entre si, mas ligados por redes rápidas. Se uma AZ falhar, os recursos noutra AZ continuam a funcionar.

Neste projeto usamos **`eu-north-1` (Estocolmo)**, a região em que o projeto AWS foi criado. A regra importante é **usar sempre a mesma região** na consola, na AWS CLI e no Terraform. Criar recursos numa região e procurá-los noutra é um erro muito comum.

### 1.3 Modelo de responsabilidade partilhada

- A **AWS** cuida da segurança *da* cloud: edifícios, hardware, rede física.
- **Tu** cuidas da segurança *na* cloud: quem tem acesso, como configuras os recursos, que dados guardas.

Quase todos os incidentes de segurança na cloud vêm de más configurações do cliente, não de falhas da AWS.

### 1.4 A nova experiência de registo da AWS: projetos

A conta deste projeto foi criada com a **nova experiência de registo** da AWS, que difere da clássica:

- Entras com uma conta **Google, GitHub ou Apple** (neste caso, GitHub), em vez de criares um email e palavra-passe próprios da AWS.
- A AWS cria automaticamente um **projeto**, que contém uma conta AWS onde crias os recursos e as definições de partilha com colaboradores.
- O nome do projeto é **gerado pela AWS** (no nosso caso, "Caffeine Driven Development") e pode ser mudado quando quiseres.
- A região do projeto é escolhida pela AWS.
- Cada projeto traz funções (*roles*) criadas automaticamente (`AWSServiceRole...`). Não é preciso mexer nelas.

**Consequência de segurança:** como entras através do GitHub, quem controlar a tua conta GitHub controla a tua conta AWS e os teus repositórios. Por isso o 2FA do GitHub é a primeira linha de defesa.

### 1.5 Verificação em dois passos (2FA/MFA)

Uma palavra-passe sozinha pode ser roubada, adivinhada ou apanhada num site falso. O 2FA acrescenta um segundo fator (por exemplo, uma aprovação no telemóvel), e sem ele um atacante não entra, mesmo com a palavra-passe.

Boa prática: guardar os **códigos de recuperação** num sítio seguro e, se possível, ter um segundo método registado.

### 1.6 IAM (Identity and Access Management)

Conceitos essenciais:

- **Utilizador IAM:** identidade para o trabalho diário, com permissões limitadas.
- **Política:** documento JSON que lista o que é permitido ou negado.
- **Papel (Role):** conjunto de permissões que pode ser assumido temporariamente por pessoas ou serviços (vamos usá-los muito mais à frente).
- **Menor privilégio:** dar só as permissões necessárias.

Exemplo de política que permite apenas ler objetos de um bucket S3:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::nome-do-bucket/*"
    }
  ]
}
```

Nota: neste passo damos `AdministratorAccess` ao utilizador de estudo por simplicidade. Nos passos de Terraform e CI/CD vamos reduzir permissões e usar papéis, que é o que se espera numa vaga de DevOps.

### 1.7 Git e GitHub

- **Git** guarda o histórico de alterações dos ficheiros. **GitHub** aloja repositórios Git na internet.
- Um **commit** é um retrato do estado dos ficheiros, com uma mensagem a explicar o que mudou.
- O **push** envia os commits locais para o GitHub.
- O ficheiro **`.gitignore`** lista o que o Git deve ignorar. É a nossa rede de segurança contra enviar segredos por engano.

---

## 2. Prática

### Parte 1 – Criar a conta AWS ✅

1. Criaste a conta em https://aws.amazon.com/free, entrando com o GitHub.
2. Ficou ativo o **plano gratuito**, com 100 $ de créditos e 183 dias.

### Parte 2 – Proteger o login ✅

1. No GitHub: **Settings → Password and authentication**.
2. Verifica que o 2FA está ativo (neste caso, via GitHub Mobile).
3. Descarrega e guarda os **códigos de recuperação**. Idealmente, adiciona um segundo método (app de autenticação ou passkey).

### Parte 3 – Criar o repositório e enviar a documentação ✅

1. No GitHub, cria um repositório **privado** e **vazio** (sem README, .gitignore ou licença) chamado `plataforma-cloud-qa`.
2. Cria no teu computador a pasta `plataforma-cloud-qa`, com esta estrutura:

   ```
   plataforma-cloud-qa/
   ├── .gitignore
   ├── README.md
   └── docs/
       ├── glossario.md
       └── passo-01-conta-aws-e-seguranca.md
   ```

3. Abre a pasta no VS Code, abre o terminal integrado e corre:

   ```bash
   git init
   git branch -M main
   git remote add origin https://github.com/RubenPereira1508/Plataforma-cloud-qa.git
   git add .
   git commit -m "docs: estrutura inicial e passo 01"
   git push -u origin main
   ```

4. Confirma no GitHub que o README aparece formatado.

O que faz cada comando:

| Comando | O que faz |
|---|---|
| `git init` | Transforma a pasta num repositório Git. |
| `git branch -M main` | Dá o nome `main` ao ramo principal. |
| `git remote add origin ...` | Liga a pasta ao repositório do GitHub. |
| `git add .` | Prepara todos os ficheiros para o commit. |
| `git commit -m "..."` | Guarda o retrato dos ficheiros com uma mensagem. |
| `git push -u origin main` | Envia o commit para o GitHub. |

### Parte 4 – Criar o utilizador IAM de trabalho ✅

> A consola desta conta tem um aspeto diferente do habitual. Se algum nome de menu não coincidir, regista aqui o que encontraste.

1. Na barra de pesquisa da consola, procura **IAM** e abre o serviço.
2. No menu da esquerda, escolhe **IAM users** e depois **Create user**.
3. Nome sugerido: `admin-estudo`.
4. **Não** atives o acesso à consola: entras na consola pelo GitHub, e este utilizador serve apenas para a linha de comandos (CLI e Terraform).
5. Em permissões, escolhe **Attach policies directly** e marca a política chamada exatamente **`AdministratorAccess`** (tipo *AWS managed - job function*). Cuidado com as variantes com sufixo (por exemplo `AdministratorAccess-Amplify`), que não são as pretendidas: usa a caixa de pesquisa e confirma o nome completo. Isto é só para a fase de estudo.
6. Cria o utilizador e confirma, no separador **Permissions**, que a política aparece ligada.

### Parte 5 – Orçamento e controlo de custos (opcional)

1. Abre **Billing** (pelo botão "Manage billing" ou pesquisando "Budgets").
2. Cria um **orçamento de custo mensal** com um valor baixo (por exemplo, 5 USD) e o teu email para os alertas.
3. Confirma em **Billing → Credits** quantos créditos tens e quando expiram. Algumas atividades de arranque dão créditos adicionais; confirma lá quais.

**O que encontrámos na prática:** nesta nova experiência, a página **Faturamento** das Configurações da AWS mostra o saldo (0,00 $), o plano (Gratuito), os dias restantes (182), os créditos (100 $) e o custo por projeto, mas **não** permite criar orçamentos. O plano gratuito **não cobra além dos créditos**: quando acabam, a conta fecha. Só passas a pagar se escolheres **Atualizar** (upgrade), por isso não o faças. O serviço AWS Budgets, se estiver disponível na consola principal, serve como camada extra, mas não é obrigatório.

### Parte 6 – Instalar e configurar a AWS CLI ✅

1. Instala a AWS CLI v2 seguindo as instruções oficiais para o teu sistema operativo.
2. No utilizador IAM `admin-estudo`, cria uma chave de acesso para a CLI (separador de credenciais de segurança).
3. Corre:

   ```bash
   aws configure
   ```

   e preenche a chave de acesso, a chave secreta, a região `eu-north-1` e o formato `json`.

   No fim, a CLI pergunta se queres configurar *skills* e o servidor MCP da AWS para agentes de programação com IA. É opcional e altera configurações de outras ferramentas; respondemos `n` (agora não).

4. Valida que funciona:

   ```bash
   aws sts get-caller-identity
   ```

   O resultado deve mostrar o teu `UserId`, o número da conta e o ARN do utilizador `admin-estudo`. Este resultado não é secreto. **Resultado obtido:** o `Arn` termina em `user/admin-estudo`, por isso a CLI está a autenticar-se como o utilizador certo.

**Atenção:** nunca guardes chaves de acesso em ficheiros do repositório. Se uma chave for exposta, desativa-a e cria outra de imediato. Mais à frente vamos substituir chaves estáticas por papéis temporários (OIDC) na pipeline.

---

## 3. Registo do que fizeste

| Tarefa | Feito | Data | Notas |
|---|---|---|---|
| Conta AWS criada (plano gratuito, login GitHub) | ✅ | 2026-11-05 | 100 $ de créditos, 183 dias |
| 2FA no GitHub | ✅ | 2026-11-05 | Via GitHub Mobile |
| Códigos de recuperação guardados | ☐ | | |
| Repositório criado e primeiro push | ✅ | 2026-11-05 | Repositório privado `Plataforma-cloud-qa` |
| Utilizador IAM `admin-estudo` | ✅ | 2026-11-05 | Sem acesso à consola; política `AdministratorAccess` |
| Orçamento com alertas | ☐ | | Opcional: o plano gratuito não cobra além dos créditos |
| Créditos verificados em Billing | ✅ | 2026-11-05 | 100 $, 182 dias |
| AWS CLI configurada e validada | ✅ | 2026-11-05 | `aws sts get-caller-identity` devolve `admin-estudo` |
| EKS disponível no plano gratuito? | ☐ | | |

## 4. Para a entrevista

**Como proteges uma conta AWS nova?**
Ativo MFA, não uso a conta principal no dia a dia, crio utilizadores com permissões mínimas, protejo as chaves de acesso e configuro alertas de custo.

**O que é o modelo de responsabilidade partilhada?**
A AWS protege a infraestrutura (a cloud em si: hardware, centros de dados, rede física). Eu sou responsável pelo que faço nela: configurações, acessos e dados.

**Porque é que se usa menor privilégio?**
Para dar a cada pessoa ou programa só as permissões necessárias à sua tarefa. Se uma chave for comprometida ou alguém se enganar, o impacto fica limitado.

**Como controlas custos na cloud?**
Defino orçamentos com alertas, acompanho os gastos, uso recursos do tamanho certo e destruo o que não é preciso. Em projetos de estudo, uso o plano gratuito.

**Como evitas expor segredos num repositório Git?**
Uso `.gitignore`, guardo segredos em gestores próprios (Secrets Manager, Secrets do GitHub), uso scanners de segredos antes do commit e, se algum vazar, revogo-o de imediato. Apagar o commit não chega, porque o segredo fica no histórico.