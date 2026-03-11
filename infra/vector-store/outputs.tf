output "chromadb_fqdn" {
  description = "ChromaDB Container App FQDN"
  value       = azurerm_container_app.chromadb.ingress[0].fqdn
}

output "chromadb_url" {
  description = "ChromaDB Container App URL"
  value       = "https://${azurerm_container_app.chromadb.ingress[0].fqdn}"
}
