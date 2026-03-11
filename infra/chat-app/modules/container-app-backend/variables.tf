variable "name" {
  description = "Name of the container app"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "container_app_environment_id" {
  description = "ID of the Container Apps environment"
  type        = string
}

variable "managed_identity_id" {
  description = "ID of the user-assigned managed identity"
  type        = string
}

variable "managed_identity_client_id" {
  description = "Client ID of the user-assigned managed identity"
  type        = string
}

variable "acr_login_server" {
  description = "ACR login server URL"
  type        = string
}

variable "image_name" {
  description = "Container image name (without registry prefix)"
  type        = string
  default     = "epi-geo-backend"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "cpu" {
  description = "CPU allocation"
  type        = number
  default     = 1.0
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "2Gi"
}

variable "min_replicas" {
  description = "Minimum number of replicas"
  type        = number
  default     = 1
}

variable "max_replicas" {
  description = "Maximum number of replicas"
  type        = number
  default     = 3
}

variable "environment" {
  description = "Environment name (development, production)"
  type        = string
}

variable "cors_origins" {
  description = "Comma-separated CORS origins"
  type        = string
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
}

# Azure OpenAI
variable "azure_openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  type        = string
}

variable "azure_openai_api_version" {
  description = "Azure OpenAI API version"
  type        = string
  default     = "2025-03-01-preview"
}

variable "azure_openai_deployment_name" {
  description = "Azure OpenAI chat deployment name"
  type        = string
  default     = "gpt-4o"
}

variable "azure_openai_embedding_deployment" {
  description = "Azure OpenAI embedding deployment name"
  type        = string
  default     = "text-embedding-3-large"
}

# GeoCatalog
variable "geocatalog_url" {
  description = "GeoCatalog STAC API URL"
  type        = string
}

variable "geocatalog_scope" {
  description = "GeoCatalog authentication scope"
  type        = string
}

# ChromaDB
variable "chroma_client_url" {
  description = "ChromaDB client URL (internal FQDN)"
  type        = string
}

# Azure AI Project
variable "azure_ai_project_endpoint" {
  description = "Azure AI project endpoint"
  type        = string
  default     = ""
}

# Key Vault secret IDs
variable "kv_secret_openai_api_key_id" {
  description = "Key Vault secret ID for Azure OpenAI API key"
  type        = string
}

variable "kv_secret_maps_key_id" {
  description = "Key Vault secret ID for Azure Maps subscription key"
  type        = string
}

variable "kv_secret_appinsights_id" {
  description = "Key Vault secret ID for Application Insights connection string"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
