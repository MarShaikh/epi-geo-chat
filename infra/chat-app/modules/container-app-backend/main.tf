resource "azurerm_container_app" "backend" {
  name                         = var.name
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"

  identity {
    type         = "UserAssigned"
    identity_ids = [var.managed_identity_id]
  }

  registry {
    server   = var.acr_login_server
    identity = var.managed_identity_id
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = "backend"
      image  = "${var.acr_login_server}/${var.image_name}:${var.image_tag}"
      cpu    = var.cpu
      memory = var.memory

      # Azure OpenAI
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = var.azure_openai_endpoint
      }
      env {
        name        = "AZURE_OPENAI_API_KEY"
        secret_name = "azure-openai-api-key"
      }
      env {
        name  = "AZURE_OPENAI_API_VERSION"
        value = var.azure_openai_api_version
      }
      env {
        name  = "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"
        value = var.azure_openai_deployment_name
      }
      env {
        name  = "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        value = var.azure_openai_embedding_deployment
      }

      # Azure Maps
      env {
        name        = "AZURE_MAPS_SUBSCRIPTION_KEY"
        secret_name = "azure-maps-subscription-key"
      }

      # Managed Identity
      env {
        name  = "AZURE_CLIENT_ID"
        value = var.managed_identity_client_id
      }

      # GeoCatalog
      env {
        name  = "GEOCATALOG_URL"
        value = var.geocatalog_url
      }
      env {
        name  = "GEOCATALOG_SCOPE"
        value = var.geocatalog_scope
      }

      # ChromaDB
      env {
        name  = "CHROMA_CLIENT_URL"
        value = var.chroma_client_url
      }

      # Azure AI Project
      env {
        name  = "AZURE_AI_PROJECT_ENDPOINT"
        value = var.azure_ai_project_endpoint
      }

      # Observability
      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "appinsights-connection-string"
      }
      env {
        name  = "ENABLE_OTEL"
        value = "true"
      }
      env {
        name  = "ENABLE_INSTRUMENTATION"
        value = "true"
      }

      # App config
      env {
        name  = "API_ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "API_CORS_ORIGINS"
        value = var.cors_origins
      }
      env {
        name  = "LOG_LEVEL"
        value = var.log_level
      }
      env {
        name  = "TOKENIZERS_PARALLELISM"
        value = "false"
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }

      readiness_probe {
        transport = "HTTP"
        path      = "/health"
        port      = 8000
      }
    }

    http_scale_rule {
      name                = "http-concurrency"
      concurrent_requests = "50"
    }
  }

  secret {
    name                = "azure-openai-api-key"
    key_vault_secret_id = var.kv_secret_openai_api_key_id
    identity            = var.managed_identity_id
  }

  secret {
    name                = "azure-maps-subscription-key"
    key_vault_secret_id = var.kv_secret_maps_key_id
    identity            = var.managed_identity_id
  }

  secret {
    name                = "appinsights-connection-string"
    key_vault_secret_id = var.kv_secret_appinsights_id
    identity            = var.managed_identity_id
  }

  tags = var.tags
}
