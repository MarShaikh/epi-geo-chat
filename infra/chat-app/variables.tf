variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Existing resource group name"
  type        = string
  default     = "rg_mpcp"
}

variable "project_name" {
  description = "Project name used as prefix for resources"
  type        = string
  default     = "epi-geo-chat"
}

variable "environment" {
  description = "Environment name (development, production)"
  type        = string
  default     = "development"
}

# --------------------------------------------------------------------------
# Existing resource references
# --------------------------------------------------------------------------

variable "container_app_environment_name" {
  description = "Name of the existing Container Apps environment"
  type        = string
  default     = "epi-geo-container-env"
}

variable "openai_account_name" {
  description = "Name of the existing Azure OpenAI account"
  type        = string
  default     = "OpenAIResourceSwedenCentral"
}

variable "key_vault_name" {
  description = "Name of the existing Key Vault"
  type        = string
  default     = "geoKv"
}

variable "acr_name" {
  description = "Name for the Container Registry"
  type        = string
  default     = "epigeochatacr"
}

variable "geocatalog_resource_id" {
  description = "Full resource ID of the GeoCatalog"
  type        = string
  default     = "/subscriptions/53a56e94-45e0-484f-95b7-676b45b31295/resourceGroups/rg_mpcp/providers/Microsoft.Orbital/geoCatalogs/geospatialDM"
}

# --------------------------------------------------------------------------
# Container images
# --------------------------------------------------------------------------

variable "backend_image_tag" {
  description = "Backend container image tag"
  type        = string
  default     = "latest"
}

variable "sandbox_image_tag" {
  description = "Sandbox container image tag"
  type        = string
  default     = "latest"
}

# --------------------------------------------------------------------------
# Application config
# --------------------------------------------------------------------------

variable "cors_origins" {
  description = "Comma-separated CORS allowed origins"
  type        = string
}

variable "log_level" {
  description = "Application log level"
  type        = string
  default     = "INFO"
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

variable "geocatalog_url" {
  description = "GeoCatalog STAC API URL"
  type        = string
}

variable "geocatalog_scope" {
  description = "GeoCatalog authentication scope"
  type        = string
}

variable "chromadb_fqdn" {
  description = "ChromaDB Container App FQDN (internal or external)"
  type        = string
}

variable "azure_ai_project_endpoint" {
  description = "Azure AI project endpoint"
  type        = string
  default     = ""
}

# --------------------------------------------------------------------------
# Secret values — pass via TF_VAR_ env vars, never commit plaintext
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

# --------------------------------------------------------------------------
# Tags
# --------------------------------------------------------------------------

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    project = "epi-geo-chat"
  }
}
