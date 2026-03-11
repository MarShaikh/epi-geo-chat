output "id" {
  value = azurerm_static_web_app.this.id
}

output "default_host_name" {
  value = azurerm_static_web_app.this.default_host_name
}

output "api_key" {
  value     = azurerm_static_web_app.this.api_key
  sensitive = true
}
