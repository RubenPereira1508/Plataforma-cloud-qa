# =============================================================================
# variables.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: valores que se podem mudar sem mexer no main.tf.
# =============================================================================

variable "regiao" {
  description = "Região AWS onde fica a rede"
  type        = string
  default     = "eu-north-1" # Estocolmo
}

variable "cidr_vpc" {
  description = "Intervalo de endereços IP privados da VPC"
  type        = string
  default     = "10.0.0.0/16" # 65 536 endereços; mais do que suficiente
}
