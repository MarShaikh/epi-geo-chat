output "acr_login_server" {
  description = "ACR login server URL"
  value       = module.acr.login_server
}

output "backend_url" {
  description = "Backend Container App URL"
  value       = module.backend.url
}

output "backend_fqdn" {
  description = "Backend Container App FQDN"
  value       = module.backend.fqdn
}

output "frontend_url" {
  description = "Static Web App URL"
  value       = "https://${module.static_web_app.default_host_name}"
}

output "frontend_api_key" {
  description = "Static Web App deployment token"
  value       = module.static_web_app.api_key
  sensitive   = true
}

output "managed_identity_client_id" {
  description = "Managed identity client ID"
  value       = module.managed_identity.client_id
}

output "sandbox_job_name" {
  description = "Sandbox Container App Job name"
  value       = module.sandbox_job.name
}
