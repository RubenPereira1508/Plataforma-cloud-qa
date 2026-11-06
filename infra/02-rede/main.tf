# =============================================================================
# main.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: cria a VPC, a rede privada do projeto dentro da AWS.
# PORQUÊ: tudo o que vem a seguir (servidores, Kubernetes, bases de dados)
#         vive dentro de uma rede. A VPC é gratuita.
# NOTA: por agora só criamos a VPC. As sub-redes, o internet gateway e as
#       rotas ficam para a Parte D.
# =============================================================================

provider "aws" {
  region = var.regiao

  default_tags {
    tags = {
      Projeto   = "plataforma-cloud-qa"
      GeridoPor = "terraform"
    }
  }
}

# --- A VPC -------------------------------------------------------------------
resource "aws_vpc" "principal" {
  cidr_block = var.cidr_vpc

  # Permitem que os recursos dentro da VPC usem nomes DNS (necessário para
  # o Kubernetes e outros serviços mais à frente).
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "plataforma-cloud-qa"
  }
}
