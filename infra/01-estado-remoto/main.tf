# =============================================================================
# main.tf  (infra/01-estado-remoto)
# -----------------------------------------------------------------------------
# O QUE FAZ: cria o bucket S3 que vai guardar o state das outras pastas.
# PORQUÊ: o state é a "memória" do Terraform. Se ficar só no teu computador
#         e o perderes, o Terraform esquece-se do que criou. Num bucket
#         seguro, com versões, fica protegido e partilhável.
#
# NOTA IMPORTANTE (o problema do ovo e da galinha):
#   Este módulo cria o bucket do state, por isso o PRÓPRIO state deste módulo
#   fica local (não pode ficar num bucket que ainda não existe).
#   Isso é normal e aceite: este módulo quase nunca muda.
# =============================================================================

provider "aws" {
  region = var.regiao

  # Etiquetas automáticas em tudo o que este provider criar.
  default_tags {
    tags = {
      Projeto   = "plataforma-cloud-qa"
      GeridoPor = "terraform"
    }
  }
}

# Sufixo aleatório: o nome de um bucket S3 é único no mundo inteiro.
resource "random_id" "sufixo" {
  byte_length = 4
}

# --- O bucket em si ----------------------------------------------------------
resource "aws_s3_bucket" "estado" {
  bucket = "plataforma-cloud-qa-tfstate-${random_id.sufixo.hex}"

  # Proteção: o Terraform recusa apagar este bucket (nem com destroy).
  # PORQUÊ: se o apagares, perdes a memória de TODA a infraestrutura.
  # (force_destroy NÃO é usado aqui, ao contrário do exercício anterior.)
  lifecycle {
    prevent_destroy = true
  }
}

# --- Versionamento -----------------------------------------------------------
# Guarda todas as versões anteriores do state. Se um apply correr mal e
# estragar o state, voltas à versão anterior. É a tua "cópia de segurança".
resource "aws_s3_bucket_versioning" "estado" {
  bucket = aws_s3_bucket.estado.id

  versioning_configuration {
    status = "Enabled"
  }
}

# --- Encriptação -------------------------------------------------------------
# O state pode conter dados sensíveis, por isso fica encriptado em repouso.
resource "aws_s3_bucket_server_side_encryption_configuration" "estado" {
  bucket = aws_s3_bucket.estado.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# --- Acesso público bloqueado ------------------------------------------------
resource "aws_s3_bucket_public_access_block" "estado" {
  bucket = aws_s3_bucket.estado.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
