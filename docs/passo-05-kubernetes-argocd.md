# Passo 05 – Kubernetes e ArgoCD (GitOps)

**Objetivo:** perceber o que é o Kubernetes e porque se usa, correr a aplicação da loja num cluster local (kind) e, no fim, deixar o ArgoCD a manter o cluster igual ao que está no Git (GitOps).

**Partes deste passo:**

- A. Teoria, instalação do kind e do kubectl, e criar o cluster ✅
- B. Pôr a aplicação no cluster: namespace, Deployments e Services (por fazer)
- C. Configuração e segredos, sondas de saúde, limites de recursos e segurança (por fazer)
- D. ArgoCD: GitOps a vigiar a pasta `k8s/` (por fazer)
- E. Fecho: documentação, limpeza e commit (por fazer)

---

## 1. Teoria

### 1.1 O problema que o Kubernetes resolve

Com o Docker Compose, a aplicação corre numa única máquina. Isso chega para aprender, mas em produção há problemas:

- **Se um contentor morre**, ninguém o volta a arrancar (a não ser que o configures à mão).
- **Se a máquina morre**, cai tudo.
- **Escalar** (ter 3 cópias da API em vez de 1) é manual.
- **Atualizar** a aplicação sem a desligar não é simples.

O **Kubernetes** (abreviado K8s) é um **orquestrador de contentores**: gere os contentores por ti, em várias máquinas, e mantém-nos a funcionar.

### 1.2 A ideia central: dizes o que queres, ele mantém

O Kubernetes é **declarativo** (como o Terraform). Não dizes "arranca este contentor"; dizes **"quero sempre 2 cópias da API a correr"**. O Kubernetes compara continuamente o que **queres** com o que **existe** e corrige a diferença. A isto chama-se **ciclo de reconciliação**.

Exemplo: pedes 2 cópias, uma morre, o Kubernetes repara que só há 1 e cria outra. Tu não fizeste nada.

### 1.3 As peças

| Conceito | Analogia | O que é |
|---|---|---|
| **Cluster** | A empresa toda | O conjunto de máquinas geridas pelo Kubernetes |
| **Node (nó)** | Um armazém | Uma máquina do cluster onde correm contentores |
| **Control plane** | A direção | O "cérebro" que decide onde e o que corre |
| **Pod** | Uma caixa | A menor unidade: um ou mais contentores que vivem juntos |
| **Deployment** | A encomenda | Diz quantas cópias (réplicas) de um Pod queres e como as atualizar |
| **Service** | O número de telefone fixo | Dá um endereço estável a um grupo de Pods (que mudam de IP) e reparte o tráfego |
| **Namespace** | As pastas | Separa recursos dentro do cluster (ex.: `loja`, `argocd`) |
| **ConfigMap** | A folha de configuração | Configuração não sensível (URLs, opções) |
| **Secret** | O cofre | Valores sensíveis (palavras-passe) |
| **Manifest** | A planta | Ficheiro YAML que descreve um recurso |
| **kubectl** | O telecomando | Ferramenta de linha de comandos para falar com o cluster |

### 1.4 Do Docker Compose para o Kubernetes

O que fizemos no `docker-compose.yml` tem equivalente:

| Docker Compose | Kubernetes |
|---|---|
| `services:` (cada serviço) | **Deployment** (corre os contentores) + **Service** (dá o endereço) |
| Nome do serviço como *hostname* (`api`, `db`) | O nome do **Service** funciona como hostname dentro do namespace |
| `ports: "8080:8080"` | Service do tipo **NodePort** (ou Ingress) |
| `.env` | **ConfigMap** (não sensível) e **Secret** (sensível) |
| `healthcheck` | **Sondas** (*probes*) `liveness` e `readiness` |
| `depends_on: service_healthy` | Sonda `readiness`: o Service só envia tráfego a Pods prontos |
| `volumes:` | **PersistentVolume** (volume que sobrevive ao Pod) |

### 1.5 As duas sondas de saúde

Já temos os dois endpoints certos na API:

| Sonda | Pergunta | Endpoint | Se falhar |
|---|---|---|---|
| **liveness** | "Estás vivo?" | `/saude` | O Kubernetes **reinicia** o contentor |
| **readiness** | "Estás pronto para receber tráfego?" | `/pronto` | O Kubernetes **deixa de enviar tráfego** (mas não reinicia) |

Foi por isto que separámos `/saude` e `/pronto` no Passo 2.

### 1.6 Porquê kind e não EKS

| | **kind** | **EKS** (Kubernetes da AWS) |
|---|---|---|
| O que é | Kubernetes dentro de contentores Docker, no teu computador | Kubernetes gerido pela AWS |
| Custo | Gratuito | O control plane cobra por hora (cerca de 0,10 $/hora; confirmar na página de preços) |
| Para quê | Aprender e desenvolver | Produção |

Por isso desenvolvemos tudo em kind e usamos o EKS só em sessões curtas, se chegarmos a isso (registado como decisão no README). Os manifests são os mesmos nos dois.

### 1.7 kubectl e contextos

O `kubectl` fala com **um cluster de cada vez**, o chamado **contexto atual**. O kind cria o contexto `kind-plataforma`. Quando houver mais do que um cluster (por exemplo, o EKS), é fácil aplicar um comando no cluster errado; por isso o hábito é confirmar com:

```bash
kubectl config current-context
```

### 1.8 Memória

O kind corre o cluster dentro do Docker, por isso gasta memória do computador. Recomenda-se dar pelo menos 4 GB ao Docker Desktop (nas definições, em *Resources*, ou no ficheiro `.wslconfig` se usares WSL 2). Se o portátil ficar lento, apaga-se o cluster e recria-se quando for preciso; é descartável.

---

## 2. Prática

### Parte A – Instalar o kind e o kubectl e criar o cluster ✅

**1. Confirma que o Docker está a correr** (Docker Desktop aberto):

```bash
docker version
```

Tem de mostrar `Client` e `Server`. Se só mostrar o `Client`, abre o Docker Desktop e espera que arranque.

**2. Instala o kind e o kubectl** (PowerShell):

```powershell
winget install -e --id Kubernetes.kind
winget install -e --id Kubernetes.kubectl
```

**Fecha o terminal e abre outro** (para o Windows reconhecer os comandos novos). Confirma:

```powershell
kind version
kubectl version --client
```

> **Nota:** o Docker Desktop pode ter instalado o seu próprio `kubectl`. Se o `kubectl version --client` mostrar uma versão antiga ou der erro, é por esse conflito; diz-me e resolvemos.

**3. Cria o ficheiro `k8s/kind-cluster.yaml`** (já comentado) na raiz do projeto.

**4. Cria o cluster** (na raiz do projeto):

```bash
kind create cluster --name plataforma --config k8s/kind-cluster.yaml
```

Na primeira vez descarrega a imagem do nó, por isso pode demorar alguns minutos.

**5. Verifica que está vivo:**

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

- `current-context` deve dizer `kind-plataforma`.
- `get nodes` deve mostrar um nó `plataforma-control-plane` em estado `Ready`.
- `get pods -A` lista os Pods de todos os namespaces. Os do `kube-system` são o próprio Kubernetes a funcionar (DNS, rede, etc.); devem estar `Running`.

**6. Vê o nó no Docker Desktop.** Em *Containers* aparece um contentor `plataforma-control-plane`: o "servidor" Kubernetes é, literalmente, um contentor Docker.

**7. (Para perceberes que é descartável)**

```bash
kind delete cluster --name plataforma
```

Apaga o cluster todo. Só faz isto se quiseres treinar o ciclo; depois volta a criá-lo com o comando do ponto 4.

**Resultado.** Logo a seguir à criação o nó aparece `NotReady` e alguns Pods `Pending`: é normal, porque o cluster ainda está a configurar a rede. Alguns minutos depois:

```
kind-plataforma

NAME                       STATUS   ROLES           AGE     VERSION
plataforma-control-plane   Ready    control-plane   3m45s   v1.37.0

NAMESPACE            NAME                                               READY   STATUS
kube-system          coredns-559f6c778d-rx4p8                           1/1     Running
kube-system          coredns-559f6c778d-tpt2s                           1/1     Running
kube-system          etcd-plataforma-control-plane                      1/1     Running
kube-system          kindnet-9dscj                                      1/1     Running
kube-system          kube-apiserver-plataforma-control-plane            1/1     Running
kube-system          kube-controller-manager-plataforma-control-plane   1/1     Running
kube-system          kube-proxy-pth74                                   1/1     Running
kube-system          kube-scheduler-plataforma-control-plane            1/1     Running
local-path-storage   local-path-provisioner-75f7fc7dc5-nz8mz            1/1     Running
```

Os Pods do `kube-system` são o próprio Kubernetes:

| Pod | Para quê |
|---|---|
| `etcd` | A base de dados do cluster (guarda o estado pretendido) |
| `kube-apiserver` | A porta de entrada: tudo o que se faz com o `kubectl` passa por aqui |
| `kube-controller-manager` | Corre o ciclo de reconciliação |
| `kube-scheduler` | Decide em que nó corre cada Pod |
| `kube-proxy` e `kindnet` | A rede |
| `coredns` | O DNS (é o que faz o nome de um Service funcionar como hostname) |
| `local-path-provisioner` | Cria os volumes de armazenamento |

O nó é um contentor Docker. No Docker Desktop vê-se a ligação de portas `8081:30080` que definimos no `kind-cluster.yaml` e a porta da API do Kubernetes (`6443` dentro do contentor):

![Nó do kind no Docker Desktop](imagens/passo-05-kind-no-docker-desktop.png)

### Parte B – Pôr a aplicação no cluster (por fazer)

### Parte C – Configuração e segredos, sondas, recursos e segurança (por fazer)

### Parte D – ArgoCD: GitOps (por fazer)

### Parte E – Fecho (por fazer)

---

## 3. Registo do que fizeste

| Tarefa | Feito | Data | Notas |
|---|---|---|---|
| kind e kubectl instalados | ✅ | 2026-11-08 | |
| Cluster `plataforma` criado | ✅ | 2026-11-08 | Kubernetes v1.37.0, um nó |
| `kubectl get nodes` mostra o nó `Ready` | ✅ | 2026-11-08 | |
| Print do Docker Desktop guardado | ✅ | 2026-11-08 | `passo-05-kind-no-docker-desktop.png` |
| Commit e push da Parte A | ☐ | | |

## 4. Para a entrevista

**O que é o Kubernetes e porque se usa em vez de só Docker Compose?**
É um orquestrador de contentores: mantém o número pretendido de cópias, reinicia o que falha, reparte tráfego e permite atualizar sem parar a aplicação, em várias máquinas. O Compose gere contentores numa só máquina.

**O que quer dizer que o Kubernetes é declarativo?**
Descrevo o estado pretendido (por exemplo, 2 réplicas) e o Kubernetes compara-o continuamente com o estado real e corrige a diferença. Chama-se ciclo de reconciliação.

**Qual é a diferença entre um Pod e um Deployment?**
O Pod é a menor unidade, um ou mais contentores. O Deployment descreve quantas réplicas de um Pod quero e como as atualizar; se um Pod morre, o Deployment cria outro.

**Para que serve um Service?**
Os Pods mudam de IP quando são recriados. O Service dá-lhes um endereço estável e reparte o tráfego pelos Pods saudáveis.

**Qual é a diferença entre as sondas liveness e readiness?**
A liveness pergunta se o contentor está vivo e, se falhar, o Kubernetes reinicia-o. A readiness pergunta se está pronto para receber tráfego e, se falhar, deixa de lhe enviar pedidos, sem o reiniciar.

**Porque usaste kind em vez de EKS?**
O kind corre o Kubernetes em contentores Docker, é gratuito e chega para desenvolver. O EKS é gerido pela AWS e o control plane cobra por hora, por isso fica para sessões curtas. Os manifests são os mesmos.

**O que é um contexto do kubectl e porque é importante verificá-lo?**
É o cluster para onde o kubectl está a enviar os comandos. Se houver vários clusters, convém confirmar o contexto antes de aplicar algo, para não mexer no cluster errado.