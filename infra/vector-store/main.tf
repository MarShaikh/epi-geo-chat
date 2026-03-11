terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.63"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg_mpcp"
    storage_account_name = "mpcpstorageaccount"
    container_name       = "tfstate"
    key                  = "vector-store.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# --------------------------------------------------------------------------
# Data sources
# --------------------------------------------------------------------------

data "azurerm_container_app_environment" "this" {
  name                = var.container_app_environment_name
  resource_group_name = var.resource_group_name
}

data "azurerm_storage_account" "this" {
  name                = var.storage_account_name
  resource_group_name = var.resource_group_name
}

# --------------------------------------------------------------------------
# Azure File Share for ChromaDB persistence
# --------------------------------------------------------------------------

resource "azurerm_storage_share" "chromadb" {
  name               = "geo-chat-chromadb"
  storage_account_id = data.azurerm_storage_account.this.id
  quota              = 102400 # GB — matches existing share
}

# --------------------------------------------------------------------------
# Container Apps Environment storage mount
# --------------------------------------------------------------------------

resource "azurerm_container_app_environment_storage" "chromadb" {
  name                         = "epi-geo-chromadb"
  container_app_environment_id = data.azurerm_container_app_environment.this.id
  account_name                 = data.azurerm_storage_account.this.name
  access_key                   = data.azurerm_storage_account.this.primary_access_key
  share_name                   = azurerm_storage_share.chromadb.name
  access_mode                  = "ReadWrite"
}

# --------------------------------------------------------------------------
# ChromaDB Container App
# --------------------------------------------------------------------------

resource "azurerm_container_app" "chromadb" {
  name                         = "chromadb-vector-store"
  container_app_environment_id = data.azurerm_container_app_environment.this.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  max_inactive_revisions       = 100
  workload_profile_name        = "Consumption"

  ingress {
    external_enabled = var.ingress_external
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "chromadb"
      image  = "chromadb/chroma:latest"
      cpu    = 0.5
      memory = "1Gi"

      volume_mounts {
        name = "chromadb-volume"
        path = "/chroma/chroma"
      }
    }

    volume {
      name         = "chromadb-volume"
      storage_type = "AzureFile"
      storage_name = azurerm_container_app_environment_storage.chromadb.name
    }
  }

  tags = var.tags
}
