# =============================================================================
# outputs.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: mostra no fim os dados da VPC.
# =============================================================================

output "vpc_id" {
  description = "Identificador da VPC criada"
  value       = aws_vpc.principal.id
}

output "vpc_cidr" {
  description = "Intervalo de IPs da VPC"
  value       = aws_vpc.principal.cidr_block
}
