terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.63"
    }
  }

  backend "azurerm" {
    # Configure via backend config file or CLI args:
    #   terraform init -backend-config=environments/dev.backend.hcl
    resource_group_name  = "rg_mpcp"
    storage_account_name = "mpcpstorageaccount"
    container_name       = "tfstate"
    key                  = "chat-app.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# --------------------------------------------------------------------------
# Data sources — reference existing resources
# --------------------------------------------------------------------------

data "azurerm_resource_group" "this" {
  name = var.resource_group_name
}

data "azurerm_container_app_environment" "this" {
  name                = var.container_app_environment_name
  resource_group_name = var.resource_group_name
}

data "azurerm_cognitive_account" "openai" {
  name                = var.openai_account_name
  resource_group_name = var.resource_group_name
}

# --------------------------------------------------------------------------
# Modules
# --------------------------------------------------------------------------

module "acr" {
  source = "./modules/container-registry"

  name                = var.acr_name
  resource_group_name = var.resource_group_name
  location            = data.azurerm_resource_group.this.location
  tags                = var.tags
}

module "key_vault" {
  source = "./modules/key-vault"

  name                = var.key_vault_name
  resource_group_name = var.resource_group_name

  # Secret values — pass via TF_VAR_ env vars, never commit plaintext
  openai_api_key                = var.openai_api_key
  maps_subscription_key         = var.maps_subscription_key
  appinsights_connection_string = var.appinsights_connection_string
}

module "managed_identity" {
  source = "./modules/managed-identity"

  name                = "${var.project_name}-identity"
  resource_group_name = var.resource_group_name
  location            = data.azurerm_resource_group.this.location
  key_vault_id        = module.key_vault.id
  openai_account_id   = data.azurerm_cognitive_account.openai.id
  acr_id              = module.acr.id
  geocatalog_id       = var.geocatalog_resource_id
  tags                = var.tags
}

module "backend" {
  source = "./modules/container-app-backend"

  name                         = "${var.project_name}-backend"
  resource_group_name          = var.resource_group_name
  container_app_environment_id = data.azurerm_container_app_environment.this.id
  managed_identity_id          = module.managed_identity.id
  managed_identity_client_id   = module.managed_identity.client_id
  acr_login_server             = module.acr.login_server
  image_tag                    = var.backend_image_tag
  environment                  = var.environment
  cors_origins                 = var.cors_origins
  log_level                    = var.log_level

  # Azure OpenAI
  azure_openai_endpoint             = data.azurerm_cognitive_account.openai.endpoint
  azure_openai_api_version          = var.azure_openai_api_version
  azure_openai_deployment_name      = var.azure_openai_deployment_name
  azure_openai_embedding_deployment = var.azure_openai_embedding_deployment

  # GeoCatalog
  geocatalog_url   = var.geocatalog_url
  geocatalog_scope = var.geocatalog_scope

  # ChromaDB — internal FQDN from the existing container app
  chroma_client_url = "https://${var.chromadb_fqdn}"

  # Azure AI Project
  azure_ai_project_endpoint = var.azure_ai_project_endpoint

  # Key Vault secret IDs (versionless URIs from the key-vault module)
  kv_secret_openai_api_key_id = module.key_vault.secret_id_openai_api_key
  kv_secret_maps_key_id       = module.key_vault.secret_id_maps_subscription_key
  kv_secret_appinsights_id    = module.key_vault.secret_id_appinsights_connection_string

  tags = var.tags
}

module "sandbox_job" {
  source = "./modules/container-app-job-sandbox"

  name                         = "${var.project_name}-sandbox"
  resource_group_name          = var.resource_group_name
  location                     = data.azurerm_resource_group.this.location
  container_app_environment_id = data.azurerm_container_app_environment.this.id
  managed_identity_id          = module.managed_identity.id
  acr_login_server             = module.acr.login_server
  image_tag                    = var.sandbox_image_tag
  tags                         = var.tags
}

module "static_web_app" {
  source = "./modules/static-web-app"

  name                = "${var.project_name}-frontend"
  resource_group_name = var.resource_group_name
  location            = data.azurerm_resource_group.this.location
  tags                = var.tags
}
