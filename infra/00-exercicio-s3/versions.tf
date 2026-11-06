# =============================================================================
# versions.tf – versões do Terraform e dos providers
# -----------------------------------------------------------------------------
# O que faz: fixa quais versões do Terraform e dos plugins (providers) este
# código aceita.
#
# Porque existe: sem isto, daqui a uns meses uma versão nova de um provider
# podia mudar o comportamento e estragar um código que antes funcionava.
# Fixar versões = resultados previsíveis (boa prática em DevOps).
# =============================================================================

terraform {
  # Versão mínima do próprio Terraform.
  required_version = ">= 1.5"

  required_providers {
    # Provider da AWS: o "tradutor" que sabe criar recursos na AWS.
    aws = {
      source  = "hashicorp/aws"
      # "~> 6.0" significa: aceita 6.x (6.1, 6.2, ...) mas NÃO a 7.0.
      # Atualizações pequenas entram; mudanças grandes ficam de fora.
      version = "~> 6.0"
    }

    # Provider "random": gera valores aleatórios. Vamos usá-lo para dar um
    # nome único ao bucket (os nomes de buckets S3 são únicos no mundo inteiro).
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
