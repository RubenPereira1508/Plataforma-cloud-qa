# Glossário

Lista de termos usados no projeto. É atualizada a cada passo.

## Cloud e AWS

| Termo | Significado |
|---|---|
| **Cloud computing** | Uso de recursos informáticos (servidores, armazenamento, redes) alugados a pedido e pagos conforme o consumo, em vez de comprados e instalados localmente. |
| **IaaS / PaaS / SaaS** | Três níveis de serviço. IaaS: alugas infraestrutura (ex.: EC2). PaaS: alugas uma plataforma para correr código (ex.: Elastic Beanstalk). SaaS: usas o software pronto (ex.: Gmail). |
| **Região (Region)** | Zona geográfica com vários centros de dados (ex.: `eu-north-1`, Estocolmo). |
| **Zona de disponibilidade (AZ)** | Centro de dados (ou grupo) isolado dentro de uma região. Distribuir recursos por várias AZ dá resiliência. |
| **Modelo de responsabilidade partilhada** | A AWS é responsável pela segurança *da* cloud (instalações, hardware). Tu és responsável pela segurança *na* cloud (configurações, dados, acessos). |
| **Projeto AWS** | Na nova experiência de registo, um projeto contém uma conta AWS onde crias recursos, mais as definições de partilha com colaboradores. Cria-se automaticamente, com um nome gerado, que podes mudar. |
| **Free plan (plano gratuito)** | Plano sem cobranças além dos créditos. Termina aos 6 meses ou quando os créditos acabam, o que ocorrer primeiro. |
| **Créditos (Free Tier credits)** | Saldo oferecido a contas novas (100 $ à entrada e até 100 $ extra por atividades) que cobre os custos do plano gratuito. |
| **IAM** | *Identity and Access Management*. Serviço que controla quem pode fazer o quê na AWS. |
| **Utilizador IAM** | Identidade para o trabalho diário, com permissões limitadas. |
| **Papel (Role)** | Conjunto de permissões que pode ser assumido temporariamente por pessoas ou serviços. Alguns são criados pela AWS (os `AWSServiceRole...`). |
| **Política (Policy)** | Documento JSON que define permissões (permitir ou negar ações em recursos). |
| **Menor privilégio** | Princípio de dar apenas as permissões estritamente necessárias. |
| **ARN** | *Amazon Resource Name*. Identificador único de um recurso na AWS. |
| **AWS CLI** | Ferramenta de linha de comandos para usar a AWS. |
| **AWS Budgets** | Serviço que permite definir um orçamento e receber alertas quando o gasto se aproxima do limite. |

## Segurança

| Termo | Significado |
|---|---|
| **2FA / MFA** | Verificação em dois passos / autenticação multifator. Um segundo fator (código ou aprovação no telemóvel) além da palavra-passe. |
| **Códigos de recuperação** | Códigos de uso único que permitem recuperar o acesso a uma conta com 2FA se perderes o telemóvel. |
| **Chave de acesso (access key)** | Par de chaves (ID e segredo) que permite a programas, como a CLI, usar a AWS em teu nome. Tratar como palavra-passe. |

## Git e GitHub

| Termo | Significado |
|---|---|
| **Git** | Sistema que guarda o histórico de alterações de ficheiros. |
| **Repositório** | Pasta acompanhada pelo Git, com todo o histórico. |
| **Commit** | "Retrato" guardado do estado dos ficheiros, com uma mensagem a explicar o que mudou. |
| **Push** | Enviar os commits locais para o repositório remoto (GitHub). |
| **Remote / origin** | Endereço do repositório remoto. `origin` é o nome habitual do principal. |
| **Branch (ramo)** | Linha de desenvolvimento. `main` é o ramo principal. |
| **.gitignore** | Ficheiro que lista o que o Git deve ignorar (segredos, ficheiros gerados). |

## DevOps e QA (serão aprofundados nos passos seguintes)

| Termo | Significado |
|---|---|
| **IaC** | Infraestrutura como código. Descrever a infraestrutura em ficheiros versionados (ex.: Terraform). |
| **CI/CD** | Integração e entrega contínuas. Automatizar build, testes e deploy. |
| **GitOps** | Usar o Git como fonte de verdade do estado desejado da infraestrutura e das aplicações. |
| **Quality gate** | Critério automático que bloqueia a entrega se a qualidade não for suficiente (ex.: testes a falhar). |