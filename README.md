# Plataforma Cloud-Native + Quality Engineering

Projeto de portfólio para vagas de **Cloud/DevOps** e **QA**, desenvolvido por passos e documentado em português de Portugal.

## Visão geral

O projeto tem duas partes ligadas entre si:

- **Projeto A – Plataforma cloud-native (Cloud/DevOps):** infraestrutura como código (Terraform) na AWS, pipeline CI/CD (GitHub Actions), GitOps (ArgoCD), Kubernetes, observabilidade (Prometheus, Grafana, Loki) e segurança.
- **Projeto B – Quality Engineering (QA):** estratégia de testes, testes de API, contract testing, E2E (Playwright), performance (k6), segurança (OWASP ZAP), chaos testing e quality gates na pipeline.

O Projeto B testa a aplicação que o Projeto A coloca em produção. Por isso vivem no mesmo repositório.

## Como este repositório está organizado

Cada passo tem **teoria** (para perceber o porquê), **prática** (para fazer) e **perguntas de entrevista** (para treinar a explicar o que se fez). As pastas vão sendo criadas à medida que cada passo as exige.

```
.
├── README.md            # este ficheiro: visão geral, índice e decisões
├── .gitignore           # ficheiros que o Git não deve guardar (segredos, etc.)
├── .env.example         # modelo da configuração local (o .env real não vai para o Git)
├── docker-compose.yml   # (Passo 2) arranca frontend + API + base de dados localmente
├── docs/                # documentação de cada passo e glossário
│   └── imagens/         # prints importantes (consola AWS, resultados, diagramas)
├── .github/workflows/   # (Passo 4) pipelines CI/CD e execução de testes
├── app/                 # (Passo 2) aplicação da loja: api/ (Python) e frontend/ (nginx)
├── infra/               # (Passo 3) Terraform
│   ├── 00-exercicio-s3/     # exercício de aprendizagem (bucket de teste, já destruído)
│   ├── 01-estado-remoto/    # bucket S3 que guarda o state das outras pastas
│   └── 02-rede/             # VPC e (Parte D) sub-redes, rotas; state no bucket
├── k8s/                 # (Passo 5) manifests, Helm e ArgoCD
├── observabilidade/     # (Passo 6) Prometheus, Grafana, Loki
└── qa/                  # (Passos 7 a 9) testes de API, E2E, k6, Pact, chaos
```

## Índice dos passos

| Passo | Tema | Estado |
|---|---|---|
| 01 | Conta AWS segura, repositório Git, IAM, orçamento e CLI | Concluído |
| 02 | Docker e a aplicação da loja (local) | Concluído |
| 03 | Terraform: estado remoto e rede (VPC) | Em curso (partes A, B e C feitas; faltam D e E) |
| 04 | CI/CD com GitHub Actions e scans de segurança | Por fazer |
| 05 | Kubernetes e ArgoCD (GitOps) | Por fazer |
| 06 | Observabilidade e segredos | Por fazer |
| 07 | Estratégia de testes e testes de API | Por fazer |
| 08 | Contract testing, E2E, performance e quality gates | Por fazer |
| 09 | Chaos testing, relatórios e demo final | Por fazer |

## Calendário

Início a 5 de novembro de 2026. Conclusão até 30 de novembro de 2026.

## Convenções do projeto

Estas regras aplicam-se a todos os ficheiros do repositório:

1. **Língua:** português de Portugal em documentação e comentários.
2. **Cabeçalho em cada ficheiro** (Terraform, YAML, scripts, testes, Dockerfiles): uma nota inicial a dizer o que o ficheiro faz e porque existe.
3. **Comentários que explicam o porquê**, e não só o quê. Cada bloco ou linha menos óbvia explica a razão da escolha e, quando faz sentido, a alternativa descartada.
4. **Um documento por passo** em `docs/`, com teoria, prática, registo do que foi feito e perguntas de entrevista.
5. **Glossário vivo** em `docs/glossario.md`, atualizado a cada passo.
6. **Segredos nunca entram no Git.** Chaves, palavras-passe e ficheiros `.env` ficam fora do repositório (ver `.gitignore`). Se uma chave for exposta por engano, desativa-se de imediato e cria-se outra.
7. **Decisões importantes ficam registadas** na tabela abaixo.
8. **Prints só do que importa:** a consola AWS, resultados visuais e diagramas guardam-se em `docs/imagens/` com o nome `passo-NN-descricao.png`. O output de terminal entra no documento como texto (só as linhas-chave), nunca como imagem. Nenhum print mostra chaves, palavras-passe ou tokens.

## Registo de decisões

| Data | Decisão | Motivo |
|---|---|---|
| 2026-11-05 | Usar AWS | Créditos gratuitos para contas novas e grande procura no mercado |
| 2026-11-05 | Desenvolver em kind (local) e usar EKS só em sessões curtas | O control plane do EKS tem custo por hora; os créditos são limitados |
| 2026-11-05 | Usar a região `eu-north-1` (Estocolmo) | Foi a região atribuída ao projeto AWS; tem os serviços necessários. Usar sempre a mesma região |
| 2026-11-05 | Conta AWS criada com a nova experiência (login via GitHub) | Acesso protegido pela conta GitHub, por isso o 2FA do GitHub é obrigatório |
| 2026-11-05 | Um único repositório para os Projetos A e B | O B testa a aplicação do A e a pipeline é partilhada |
| 2026-11-05 | Aplicação própria (FastAPI + PostgreSQL + frontend simples) em vez de um fork de uma app grande | Mais fácil de perceber peça a peça, mais leve no portátil e permite criar falhas controladas para o QA |
| 2026-11-06 | Guardar o state do Terraform num bucket S3 (backend remoto) com versionamento, encriptação e `prevent_destroy` | O state é a memória do Terraform; num bucket protegido não se perde, é partilhável pela pipeline e tem histórico de versões |
| 2026-11-06 | Bloqueio do state com `use_lockfile` (nativo do S3, Terraform 1.10 ou superior) em vez de DynamoDB | Menos recursos para gerir e o mesmo efeito: impede dois `apply` em simultâneo |
| 2026-11-06 | O state da pasta `01-estado-remoto` fica local | O bucket tem de existir antes de poder guardar state (ovo e galinha); a pasta quase nunca muda |
| 2026-11-06 | Rede sem NAT Gateway | O NAT Gateway cobra por hora e os créditos são limitados |
| 2026-11-06 | Não mexer na VPC por omissão da AWS | Não é gerida pelo Terraform; o projeto usa a sua própria VPC |