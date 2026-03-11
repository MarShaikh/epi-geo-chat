variable "name" {
  description = "Name of the existing Key Vault"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

# --------------------------------------------------------------------------
# Secret values — pass via tfvars or TF_VAR_ env vars, never commit plaintext
# --------------------------------------------------------------------------

variable "openai_api_key" {
  description = "Azure OpenAI API key"
  type        = string
  sensitive   = true
}

variable "maps_subscription_key" {
  description = "Azure Maps subscription key"
  type        = string
  sensitive   = true
}

variable "appinsights_connection_string" {
  description = "Application Insights connection string"
  type        = string
  sensitive   = true
}
