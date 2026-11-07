# =============================================================================
# rede.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: divide a VPC em sub-redes públicas e privadas, liga as públicas
#            à internet e define as rotas.
# PORQUÊ: servidores expostos (balanceadores) ficam em sub-redes públicas;
#         coisas que não devem ser acessíveis da internet (bases de dados)
#         ficam em sub-redes privadas.
#
# DECISÃO DE CUSTO: NÃO criamos NAT Gateway. Cobra por hora e os créditos são
#   limitados. Consequência: as sub-redes privadas existem mas não têm saída
#   para a internet. Para este projeto (kind local, EKS só em sessões curtas)
#   é aceitável.
#
# Tudo o que está neste ficheiro é gratuito.
# =============================================================================

# --- Zonas de disponibilidade ------------------------------------------------
# DATA SOURCE (só lê, não cria): pergunta à AWS que zonas (datacenters) estão
# disponíveis na região. Em vez de escrever "eu-north-1a" à mão, o código
# adapta-se se mudares de região.
data "aws_availability_zones" "disponiveis" {
  state = "available"
}

# --- Sub-redes públicas ------------------------------------------------------
# "count" repete o recurso: com 2 intervalos na lista, cria 2 sub-redes.
# "count.index" é o número da repetição (0, 1) e escolhe o intervalo e a zona.
resource "aws_subnet" "publica" {
  count = length(var.cidrs_subredes_publicas)

  vpc_id            = aws_vpc.principal.id
  cidr_block        = var.cidrs_subredes_publicas[count.index]
  availability_zone = data.aws_availability_zones.disponiveis.names[count.index]

  # Servidores lançados aqui recebem automaticamente um IP público.
  map_public_ip_on_launch = true

  tags = {
    Name = "plataforma-cloud-qa-publica-${count.index + 1}"

    # Etiqueta que o Kubernetes na AWS usa para saber onde pôr balanceadores
    # expostos à internet. Não faz nada agora; fica pronta para o Passo 5.
    "kubernetes.io/role/elb" = "1"
  }
}

# --- Sub-redes privadas ------------------------------------------------------
resource "aws_subnet" "privada" {
  count = length(var.cidrs_subredes_privadas)

  vpc_id            = aws_vpc.principal.id
  cidr_block        = var.cidrs_subredes_privadas[count.index]
  availability_zone = data.aws_availability_zones.disponiveis.names[count.index]

  # Sem IP público automático: ficam fechadas à internet.
  map_public_ip_on_launch = false

  tags = {
    Name = "plataforma-cloud-qa-privada-${count.index + 1}"

    # Equivalente ao anterior, para balanceadores internos.
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# --- Internet Gateway --------------------------------------------------------
# A "porta" da VPC para a internet. Sem ela, nada entra nem sai.
# Existir não chega: é preciso uma rota a apontar para ela (mais abaixo).
resource "aws_internet_gateway" "principal" {
  vpc_id = aws_vpc.principal.id

  tags = {
    Name = "plataforma-cloud-qa"
  }
}

# --- Tabela de rotas pública -------------------------------------------------
# Uma tabela de rotas é a lista de "para onde vai o tráfego".
# A regra 0.0.0.0/0 significa "qualquer destino que não seja da própria VPC"
# e manda-o para o internet gateway. É ISTO que torna uma sub-rede "pública".
resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.principal.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.principal.id
  }

  tags = {
    Name = "plataforma-cloud-qa-publica"
  }
}

# Uma tabela só vale para as sub-redes a que for associada.
resource "aws_route_table_association" "publica" {
  count = length(aws_subnet.publica)

  subnet_id      = aws_subnet.publica[count.index].id
  route_table_id = aws_route_table.publica.id
}

# --- Tabela de rotas privada -------------------------------------------------
# Sem nenhuma regra para a internet: só tem a rota local (dentro da VPC), que
# a AWS cria sozinha. É isto que torna uma sub-rede "privada".
resource "aws_route_table" "privada" {
  vpc_id = aws_vpc.principal.id

  tags = {
    Name = "plataforma-cloud-qa-privada"
  }
}

resource "aws_route_table_association" "privada" {
  count = length(aws_subnet.privada)

  subnet_id      = aws_subnet.privada[count.index].id
  route_table_id = aws_route_table.privada.id
}
