output "fqdn" {
  value = azurerm_container_app.backend.ingress[0].fqdn
}

output "url" {
  value = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
}

output "id" {
  value = azurerm_container_app.backend.id
}
