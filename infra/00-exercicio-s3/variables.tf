# =============================================================================
# variables.tf – valores de entrada do código
# -----------------------------------------------------------------------------
# O que faz: declara as "variáveis" que podes mudar sem mexer no resto do código.
# Porque existe: evita repetir valores (como a região) em vários sítios. Se
# mudares aqui, muda em todo o lado.
# =============================================================================

variable "regiao" {
  description = "Região da AWS onde os recursos são criados."
  type        = string
  # Valor por omissão: a nossa região de trabalho. Lembra-te: usar SEMPRE a mesma.
  default     = "eu-north-1"
}
