# =============================================================================
# outputs.tf  (infra/02-rede)
# -----------------------------------------------------------------------------
# O QUE FAZ: mostra no fim os dados da rede.
# PORQUÊ: os ids das sub-redes vão ser precisos mais tarde (Kubernetes).
# =============================================================================

output "vpc_id" {
  description = "Identificador da VPC criada"
  value       = aws_vpc.principal.id
}

output "vpc_cidr" {
  description = "Intervalo de IPs da VPC"
  value       = aws_vpc.principal.cidr_block
}

# O "[*]" (splat) recolhe o id de TODAS as repetições do "count" numa lista.
output "ids_subredes_publicas" {
  description = "Ids das sub-redes públicas"
  value       = aws_subnet.publica[*].id
}

output "ids_subredes_privadas" {
  description = "Ids das sub-redes privadas"
  value       = aws_subnet.privada[*].id
}

output "id_internet_gateway" {
  description = "Id do internet gateway"
  value       = aws_internet_gateway.principal.id
}
