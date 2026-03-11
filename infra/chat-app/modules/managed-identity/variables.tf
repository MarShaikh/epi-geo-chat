variable "name" {
  description = "Name of the managed identity"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "key_vault_id" {
  description = "ID of the Key Vault to grant Secrets User access"
  type        = string
}

variable "openai_account_id" {
  description = "ID of the Azure OpenAI account to grant user access"
  type        = string
}

variable "acr_id" {
  description = "ID of the Container Registry to grant AcrPull access"
  type        = string
}

variable "geocatalog_id" {
  description = "ID of the GeoCatalog resource to grant Reader access"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
