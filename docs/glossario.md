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

## Docker e contentores

| Termo | Significado |
|---|---|
| **Contentor** | Aplicação embrulhada com tudo o que precisa para correr, isolada do resto. Corre igual em qualquer sítio. |
| **Imagem** | Modelo só de leitura a partir do qual se criam contentores. |
| **Dockerfile** | Ficheiro com as instruções para construir uma imagem. |
| **Camada (layer)** | Cada instrução do Dockerfile gera uma camada, guardada em cache para acelerar construções. |
| **Registry** | Sítio onde se guardam e partilham imagens (Docker Hub, ECR da AWS). |
| **Docker daemon** | Motor do Docker que corre em segundo plano e faz o trabalho; o comando `docker` fala com ele. |
| **Porta publicada (`-p`)** | Ligação entre uma porta do teu computador e uma porta do contentor. |
| **.dockerignore** | Lista do que o Docker não deve enviar para a construção da imagem (segredos, lixo). |
| **Health check** | Verificação periódica que pergunta à aplicação se está viva. |
| **API / endpoint** | Interface através da qual programas falam com a aplicação; endpoint é cada "endereço" dessa interface (ex.: `/produtos`). |
| **Docker Compose** | Ferramenta que arranca vários contentores e as suas ligações a partir de um único ficheiro (`docker-compose.yml`). |
| **Volume** | Pasta gerida pelo Docker que sobrevive aos contentores. Serve para guardar dados (ex.: da base de dados). |
| **Variável de ambiente** | Valor de configuração passado a um programa por fora do código (ex.: palavra-passe, endereço da base de dados). |
| **.env** | Ficheiro local com variáveis de ambiente. Nunca vai para o Git. |
| **PostgreSQL** | Base de dados relacional de código aberto. |
| **SQL** | Linguagem para consultar e alterar bases de dados. |
| **SQL injection** | Ataque que mete comandos SQL em dados enviados pelo utilizador. Evita-se usando parâmetros. |
| **Liveness / readiness** | Duas verificações de saúde: "estou vivo?" (reiniciar se falhar) e "estou pronto a receber pedidos?" (retirar tráfego se falhar). |
| **Retry** | Tentar de novo uma operação que falhou, normalmente com uma pausa entre tentativas. |
| **Frontend** | A parte da aplicação que o utilizador vê (página web). |
| **nginx** | Servidor web leve; serve páginas estáticas e pode funcionar como proxy inverso. |
| **Proxy inverso (reverse proxy)** | Servidor que recebe os pedidos e os reencaminha para outros serviços por trás. O cliente só vê um endereço. |
| **CORS** | Regra dos browsers que bloqueia pedidos entre origens (endereços) diferentes, salvo autorização. Com proxy inverso a origem é a mesma. |
| **XSS** | Ataque que injeta código malicioso numa página (ex.: via dados mostrados com innerHTML). Evita-se com textContent e validação. |
| **data-testid** | Atributo HTML que dá aos testes automáticos um ponto de agarre estável. |
| **Swagger / OpenAPI** | OpenAPI é o formato padrão para descrever APIs. Swagger UI é a página interativa gerada a partir dele (em `/docs`), onde se experimentam os endpoints. |
| **Serviço (Compose)** | Cada componente descrito no `docker-compose.yml` (aqui: `db`, `api` e `frontend`). Cada serviço gera um ou mais contentores. |
| **Rede do Compose** | Rede privada criada automaticamente para os contentores do mesmo Compose, onde se encontram pelo nome do serviço. |
| **Máquina virtual (VM)** | Computador simulado, com sistema operativo completo, a correr sobre um hipervisor. Mais pesada e mais isolada do que um contentor. |
| **Código HTTP** | Número que indica o resultado de um pedido: 200 ok, 201 criado, 404 não encontrado, 422 dados inválidos. |

## Terraform

| Termo | Significado |
|---|---|
| **Terraform** | Ferramenta de infraestrutura como código: descreves o que queres em ficheiros `.tf` e ela cria, altera ou apaga os recursos. |
| **Declarativo** | Descrever o resultado pretendido (a "planta"), deixando à ferramenta a decisão dos passos. |
| **Provider** | Plugin que permite ao Terraform falar com uma plataforma (ex.: `aws`). |
| **Resource** | Item de infraestrutura a criar (ex.: um bucket, uma sub-rede). |
| **Data source** | Consulta a informação que já existe, sem criar nada. |
| **Variable / Output** | Valor de entrada configurável / valor mostrado no fim da execução. |
| **Module** | Conjunto de recursos reutilizável. |
| **State** | Ficheiro onde o Terraform regista o que criou. Pode ter dados sensíveis; não vai para o Git. |
| **Estado remoto e lock** | Guardar o state fora do computador (ex.: num bucket S3) e bloquear execuções simultâneas. |
| **`init` / `plan` / `apply` / `destroy`** | Preparar a pasta / simular / executar / apagar tudo o que foi criado. |
| **Idempotência** | Correr o mesmo código várias vezes dá sempre o mesmo resultado, sem duplicar nada. |
| **Drift** | Diferença entre o código e a infraestrutura real (por exemplo, alterações feitas à mão). |
| **`.terraform.lock.hcl`** | Fixa as versões exatas dos providers. Vai para o Git. |
| **Bucket S3** | "Pasta" na cloud da AWS para guardar ficheiros. O nome é único no mundo inteiro. |
| **Tags** | Etiquetas em recursos da cloud, úteis para organização e controlo de custos. |

## DevOps e QA (serão aprofundados nos passos seguintes)

| Termo | Significado |
|---|---|
| **IaC** | Infraestrutura como código. Descrever a infraestrutura em ficheiros versionados (ex.: Terraform). |
| **CI/CD** | Integração e entrega contínuas. Automatizar build, testes e deploy. |
| **GitOps** | Usar o Git como fonte de verdade do estado desejado da infraestrutura e das aplicações. |
| **Quality gate** | Critério automático que bloqueia a entrega se a qualidade não for suficiente (ex.: testes a falhar). |