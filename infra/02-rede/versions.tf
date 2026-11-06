# =============================================================================
# versions.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: fixa as versões e diz ONDE o Terraform guarda o state (backend).
# PORQUÊ: a partir daqui o state deixa de ficar no teu computador e passa a
#         viver no bucket S3 criado em infra/01-estado-remoto.
# =============================================================================

terraform {
  required_version = ">= 1.10"

  # --- O BACKEND: a "casa" do state -----------------------------------------
  # IMPORTANTE: o bloco backend NÃO aceita variáveis. Os valores têm de ser
  # escritos à mão (é uma limitação do Terraform).
  backend "s3" {
    # Nome do bucket criado na pasta 01-estado-remoto.
    bucket = "plataforma-cloud-qa-tfstate-32b867e4"

    # "Caminho" do ficheiro dentro do bucket. Cada pasta do projeto usa uma
    # chave diferente, para os states não se misturarem.
    key = "rede/terraform.tfstate"

    region = "eu-north-1"

    # Encripta o ficheiro do state ao guardá-lo.
    encrypt = true

    # Bloqueio nativo do S3: impede dois "apply" ao mesmo tempo no mesmo state.
    # (Antes era preciso uma tabela DynamoDB; desde o Terraform 1.10 já não.)
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
