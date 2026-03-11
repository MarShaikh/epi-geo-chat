output "id" {
  value = data.azurerm_key_vault.this.id
}

output "vault_uri" {
  value = data.azurerm_key_vault.this.vault_uri
}

# Versionless secret IDs for Container App secret references
output "secret_id_openai_api_key" {
  value = azurerm_key_vault_secret.openai_api_key.versionless_id
}

output "secret_id_maps_subscription_key" {
  value = azurerm_key_vault_secret.maps_subscription_key.versionless_id
}

output "secret_id_appinsights_connection_string" {
  value = azurerm_key_vault_secret.appinsights_connection_string.versionless_id
}
