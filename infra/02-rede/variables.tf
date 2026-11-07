# =============================================================================
# variables.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: valores que se podem mudar sem mexer no resto do código.
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

# --- Sub-redes (Parte D) -----------------------------------------------------
# Cada sub-rede é um pedaço do intervalo da VPC. Usamos /24 (256 endereços).
# A AWS reserva 5 endereços por sub-rede, por isso ficam 251 utilizáveis.
# São listas com 2 elementos: uma sub-rede por zona de disponibilidade (AZ),
# para a rede continuar a funcionar se um datacenter falhar.

variable "cidrs_subredes_publicas" {
  description = "Intervalos das sub-redes públicas (uma por zona de disponibilidade)"
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "cidrs_subredes_privadas" {
  description = "Intervalos das sub-redes privadas (uma por zona de disponibilidade)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}
