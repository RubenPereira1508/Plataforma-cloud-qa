# =============================================================================
# variables.tf  (infra/01-estado-remoto)
# -----------------------------------------------------------------------------
# O QUE FAZ: define os valores que se podem mudar sem mexer no main.tf.
# =============================================================================

variable "regiao" {
  description = "Região AWS onde fica o bucket do state"
  type        = string
  default     = "eu-north-1" # Estocolmo, a mesma do resto do projeto
}
