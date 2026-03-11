subscription_id = "53a56e94-45e0-484f-95b7-676b45b31295"
environment     = "production"
log_level       = "INFO"

# CORS — Static Web App URL only
cors_origins = "https://salmon-wave-0f674db03.6.azurestaticapps.net"

# GeoCatalog
geocatalog_url   = "https://geospatialdm.fmd9dgfcd2fab5hw.westeurope.geocatalog.spatio.azure.com"
geocatalog_scope = "6388acc4-795e-43a9-a320-33075c1eb83b/.default"

# ChromaDB FQDN — from the existing Container App
chromadb_fqdn = "chromadb-vector-store.mangopond-219dd1c0.westeurope.azurecontainerapps.io"

# Secret values — pass via environment variables, NOT in this file:
#   export TF_VAR_openai_api_key="..."
#   export TF_VAR_maps_subscription_key="..."
#   export TF_VAR_appinsights_connection_string="..."
