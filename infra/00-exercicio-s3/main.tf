# =============================================================================
# main.tf – exercício 1: o primeiro recurso na AWS (bucket S3 de teste)
# -----------------------------------------------------------------------------
# O que faz: cria um bucket S3 de teste, fechado ao público.
#
# Porque existe: serve só para aprenderes o ciclo do Terraform
# (init → plan → apply → destroy) com um recurso simples e barato.
# Este exercício é DESCARTÁVEL: no fim fazemos `terraform destroy`.
# =============================================================================

# -----------------------------------------------------------------------------
# Configuração do provider da AWS
# -----------------------------------------------------------------------------
# O Terraform usa as credenciais que já configuraste com `aws configure`
# (o utilizador admin-estudo). Não escrevemos chaves aqui. NUNCA.
provider "aws" {
  region = var.regiao

  # Etiquetas (tags) aplicadas automaticamente a TODOS os recursos criados.
  # Ajudam a saber a quem pertence cada coisa e a controlar custos.
  default_tags {
    tags = {
      Projeto   = "plataforma-cloud-qa"
      GeridoPor = "terraform"
    }
  }
}

# -----------------------------------------------------------------------------
# Data source: consulta de informação que JÁ existe (não cria nada)
# -----------------------------------------------------------------------------
# Pergunta à AWS "quem sou eu?" (equivale ao `aws sts get-caller-identity`).
# Usamo-lo no output para confirmares que estás na conta certa.
data "aws_caller_identity" "atual" {}

# -----------------------------------------------------------------------------
# Recurso 1: sufixo aleatório
# -----------------------------------------------------------------------------
# Os nomes de buckets S3 são únicos no MUNDO INTEIRO. Juntamos 4 bytes
# aleatórios (8 caracteres em hexadecimal) para evitar colisões com outras
# pessoas. O valor é gerado uma vez e fica guardado no state.
resource "random_id" "sufixo" {
  byte_length = 4
}

# -----------------------------------------------------------------------------
# Recurso 2: o bucket S3
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "teste" {
  # Nome real do bucket na AWS. "${...}" insere o valor de outro recurso.
  # Só minúsculas, números e hífens (regras dos nomes de buckets).
  bucket = "plataforma-cloud-qa-exercicio-${random_id.sufixo.hex}"

  # Permite apagar o bucket mesmo que tenha ficheiros lá dentro.
  # Aceitável num exercício descartável; num bucket com dados reais NÃO se usa.
  force_destroy = true
}

# -----------------------------------------------------------------------------
# Recurso 3: bloquear TODO o acesso público ao bucket
# -----------------------------------------------------------------------------
# Segurança por omissão: um bucket aberto ao público é das falhas de
# configuração mais comuns (e mais graves) na cloud. Aqui fechamos tudo.
# Repara que este recurso REFERE o bucket (aws_s3_bucket.teste.id): é assim
# que o Terraform percebe que o bucket tem de ser criado primeiro.
resource "aws_s3_bucket_public_access_block" "teste" {
  bucket = aws_s3_bucket.teste.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
