# Reference the existing Key Vault — do not create a new one
data "azurerm_key_vault" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
}

# --------------------------------------------------------------------------
# Secrets
# --------------------------------------------------------------------------

resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "azure-openai-api-key"
  value        = var.openai_api_key
  key_vault_id = data.azurerm_key_vault.this.id
}

resource "azurerm_key_vault_secret" "maps_subscription_key" {
  name         = "azure-maps-subscription-key"
  value        = var.maps_subscription_key
  key_vault_id = data.azurerm_key_vault.this.id
}

resource "azurerm_key_vault_secret" "appinsights_connection_string" {
  name         = "appinsights-connection-string"
  value        = var.appinsights_connection_string
  key_vault_id = data.azurerm_key_vault.this.id
}
