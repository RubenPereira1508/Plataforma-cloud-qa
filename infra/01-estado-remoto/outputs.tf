# =============================================================================
# outputs.tf  (infra/01-estado-remoto)
# -----------------------------------------------------------------------------
# O QUE FAZ: mostra no fim o nome do bucket do state.
# PORQUÊ: vais precisar deste nome para o configurar como "backend" nas
#         outras pastas (a rede/VPC, por exemplo).
# =============================================================================

output "nome_do_bucket_estado" {
  description = "Nome do bucket S3 onde fica o state remoto"
  value       = aws_s3_bucket.estado.id
}

output "regiao_usada" {
  description = "Região onde o bucket foi criado"
  value       = var.regiao
}
