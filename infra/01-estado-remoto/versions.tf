# =============================================================================
# versions.tf  (infra/01-estado-remoto)
# -----------------------------------------------------------------------------
# O QUE FAZ: fixa as versões do Terraform e dos providers deste módulo.
# PORQUÊ: para o código dar o mesmo resultado hoje e daqui a um ano.
#         Este módulo cria o "cofre" (bucket S3) onde, a partir da Parte C,
#         vai ficar guardado o state das restantes pastas do projeto.
# =============================================================================

terraform {
  # 1.10 é a primeira versão com bloqueio nativo no S3 (use_lockfile),
  # que vamos usar no passo seguinte. Antes era preciso uma tabela DynamoDB.
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
