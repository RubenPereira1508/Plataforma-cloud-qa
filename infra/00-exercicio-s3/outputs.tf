# =============================================================================
# outputs.tf – o que o Terraform mostra no fim
# -----------------------------------------------------------------------------
# O que faz: define valores que aparecem depois do `apply` (e que podes
# consultar com `terraform output`).
# Porque existe: para veres o resultado sem ir à consola, e (mais tarde) para
# passar informação de um módulo para outro.
# =============================================================================

output "nome_do_bucket" {
  description = "Nome do bucket S3 criado."
  value       = aws_s3_bucket.teste.bucket
}

output "regiao_usada" {
  description = "Região onde o bucket foi criado."
  value       = var.regiao
}

output "conta_aws" {
  description = "Número da conta AWS em que o Terraform está a trabalhar (confirmação)."
  value       = data.aws_caller_identity.atual.account_id
}
