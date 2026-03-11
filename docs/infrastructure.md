# Azure Infrastructure

## Overview

The application runs on Azure with infrastructure managed via Terraform. The setup spans two Terraform root modules (`infra/chat-app/` and `infra/vector-store/`) and references several pre-existing Azure resources shared with the broader geospatial platform.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Azure (West Europe)                                                     │
│                                                                          │
│  ┌──────────────┐     ┌──────────────────┐     ┌────────────────┐        │
│  │ Static Web   │────►│ Backend          │────►│ ChromaDB       │        │
│  │ App          │     │ Container App    │     │ Container App  │        │
│  │ (frontend)   │     │ :8000            │     │ :8000          │        │
│  └──────────────┘     └──┬───┬───┬───┬───┘     └────────────────┘        │
│                          │   │   │   │                 │                 │
│                          │   │   │   │          Azure File Share         │
│                          │   │   │   │          (persistent data)        │
│               ┌──────────┘   │   │   └──────────────┐                    │
│               │              │   │                  │                    │
│               ▼              ▼   ▼                  ▼                    │
│        ┌───────────┐  ┌──────────────┐        ┌──────────────┐           │
│        │ Key Vault │  │ Sandbox      │        │ GeoCatalog   │           │
│        │ (secrets) │  │ CA Job       │        │ (STAC API)   │           │
│        └───────────┘  └──────────────┘        └──────────────┘           │
│                                                                          │
│        ┌───────────┐  ┌──────────────┐        ┌──────────────┐           │
│        │ ACR       │  │ Azure Maps   │        │ Azure OpenAI │           │
│        │ (images)  │  │ (geocoding)  │        │ (Sweden Cntl)│           │
│        └───────────┘  └──────────────┘        └──────────────┘           │
└──────────────────────────────────────────────────────────────────────────┘
```

## Pre-existing Resources

These resources are **not** managed by Terraform. They were created manually and are shared with the broader platform.

| Resource | Name | Region | Notes |
|---|---|---|---|
| Resource Group | `rg_mpcp` | West Europe | Shared with broader geospatial platform |
| Azure OpenAI | `OpenAIResourceSwedenCentral` | Sweden Central | GPT-4o, GlobalStandard SKU |
| Azure Maps | `epi-geo` | - | Gen2, G2 SKU. Used for geocoding |
| Key Vault | `geoKv` | West Europe | Stores API keys and connection strings |
| Storage Account | `mpcpstorageaccount` | West Europe | Hosts file shares and Terraform state |
| Container Apps Environment | `epi-geo-container-env` | West Europe | Shared environment for all container apps |
| Application Insights | Geo Chat application | - | Via Azure Monitor / OpenTelemetry |

## Terraform Structure

### State Backend

Both root modules store state in Azure Blob Storage:

- **Storage Account:** `mpcpstorageaccount`
- **Container:** `tfstate`
- **State keys:**
  - `chat-app.terraform.tfstate`
  - `vector-store.terraform.tfstate`

### `infra/chat-app/` — Main Application

This root module creates all resources for the chat application using six modules:

| Module | Azure Resource | Name |
|---|---|---|
| `container-registry` | Container Registry | `epigeochatacr` (Basic SKU) |
| `managed-identity` | User-assigned Managed Identity | `epi-geo-chat-identity` |
| `key-vault` | Key Vault Secrets (3) | `azure-openai-api-key`, `azure-maps-subscription-key`, `appinsights-connection-string` |
| `container-app-backend` | Container App | `epi-geo-chat-backend` (1–3 replicas) |
| `container-app-job-sandbox` | Container App Job | `epi-geo-chat-sandbox` (manual trigger) |
| `static-web-app` | Static Web App | `epi-geo-chat-frontend` (Standard tier) |

The managed identity is granted four RBAC roles:

- **Key Vault Secrets User** on `geoKv`
- **Cognitive Services OpenAI User** on `OpenAIResourceSwedenCentral`
- **AcrPull** on `epigeochatacr`
- **GeoCatalog Reader** on the GeoCatalog resource

#### Secret Management

Sensitive values are never stored in `.tfvars` files. They are passed at apply time via environment variables:

```bash
export TF_VAR_openai_api_key="..."
export TF_VAR_maps_subscription_key="..."
export TF_VAR_appinsights_connection_string="..."
terraform apply -var-file=environments/dev.tfvars
```

Terraform creates `azurerm_key_vault_secret` resources in the existing Key Vault. The backend container app references these secrets via versionless `key_vault_secret_id` URIs, authenticated through the managed identity.

#### Environment Configuration

Two environment files exist under `infra/chat-app/environments/`:

| Setting | `dev.tfvars` | `prod.tfvars` |
|---|---|---|
| `log_level` | `DEBUG` | `INFO` |
| CORS origins | Includes `localhost:5173` | SWA hostname only |
| ChromaDB FQDN | External FQDN | Internal FQDN |

### `infra/vector-store/` — ChromaDB

A simpler root module managing the vector database:

- **Azure File Share** (`geo-chat-chromadb`, 102400 GB quota) for persistent storage
- **Container App Environment Storage** (`epi-geo-chromadb`) — the mount alias used by the container app
- **Container App** (`chromadb-vector-store`) running `chromadb/chroma:latest` (0.5 CPU, 1 Gi memory, single replica)

These resources were originally created manually, then imported into Terraform state.

## Container Images

Images are built using `az acr build` (cloud build on linux/amd64) and pushed to `epigeochatacr`:

```bash
# Backend
az acr build --registry epigeochatacr \
  --image epi-geo-backend:latest \
  --file Dockerfile .

# Sandbox
az acr build --registry epigeochatacr \
  --image epi-geo-sandbox:latest \
  --file src/code_executor/docker/Dockerfile \
  src/code_executor/docker/
```

Images must exist in ACR **before** running `terraform apply` for the first time, since the container app and job reference them at creation.

## CI/CD

GitHub Actions (`.github/workflows/deploy.yml`) automates the deployment pipeline:

```
test ──► build-backend  ─┐
         build-sandbox  ─┤──► deploy-backend
         build-frontend ─┘    deploy-frontend
```

- **Trigger:** Push to `main` or manual `workflow_dispatch`
- **Authentication:** Workload identity federation (OIDC) — no stored service principal secrets
- **Required repo secrets:** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `SWA_DEPLOYMENT_TOKEN`
- **Image tags:** Short commit SHA + `latest`

## Deploying from Scratch

1. **Build and push images** to ACR (see [Container Images](#container-images) above)
2. **Apply vector-store infra:**
   ```bash
   cd infra/vector-store
   terraform init
   terraform apply
   ```
3. **Apply chat-app infra** (with secrets as env vars):
   ```bash
   cd infra/chat-app
   terraform init
   export TF_VAR_openai_api_key="..."
   export TF_VAR_maps_subscription_key="..."
   export TF_VAR_appinsights_connection_string="..."
   terraform apply -var-file=environments/dev.tfvars
   ```
4. **Deploy frontend:**
   ```bash
   cd frontend
   npm ci && npm run build
   npx @azure/static-web-apps-cli deploy dist/
   ```

If a container app is stuck in a **Failed** provisioning state from a prior attempt, delete it before re-applying:

```bash
az containerapp delete --name epi-geo-chat-backend --resource-group rg_mpcp --yes
az containerapp job delete --name epi-geo-chat-sandbox --resource-group rg_mpcp --yes
```

## External Service Integrations

### GeoCatalog (STAC API)

The backend connects to an Azure GeoCatalog instance to discover and query geospatial datasets via the [STAC](https://stacspec.org/) API. The `GeoCatalogClient` (`src/stac/catalog_client.py`) supports listing collections, searching items by bounding box and time range, and retrieving individual items.

**Authentication** uses `DefaultAzureCredential` with the managed identity. The credential acquires a token scoped to the GeoCatalog resource, which is passed as a Bearer token in each request.

**Configuration** is provided via two environment variables set on the backend container app:

| Env Var | Value |
|---|---|
| `GEOCATALOG_URL` | `https://geospatialdm.fmd9dgfcd2fab5hw.westeurope.geocatalog.spatio.azure.com` |
| `GEOCATALOG_SCOPE` | `6388acc4-795e-43a9-a320-33075c1eb83b/.default` |

The managed identity is granted the **GeoCatalog Reader** role on the GeoCatalog resource, which allows read-only access to collections and items.

GeoCatalog data is also indexed into the ChromaDB vector store for RAG-based collection discovery (see `src/rag/vector_store.py`).

### Artifact Store

The sandbox container app job executes user-generated Python code and produces output artifacts (PNG charts, HTML maps, CSV files). These are stored by the `ArtifactStore` (`src/code_executor/artifact_store.py`) on the local filesystem at `/tmp/epi-geo-artifacts` with a 60-minute TTL.

This is file-based and ephemeral — artifacts are lost when the backend container restarts. Migrating to Azure Blob Storage is listed under [Planned Work](#planned-work) to make artifacts durable.

## Planned Work

- Make ChromaDB ingress internal-only
- Refactor sandbox to use Container Apps Jobs API instead of Docker socket
- Set up monitoring alerts (error rate > 5%, P95 latency > 10s, container restarts)
- Migrate `ArtifactStore` to Blob Storage
- Azure Front Door for custom domain and WAF
- Managed identity auth for Azure OpenAI (replacing API key)
