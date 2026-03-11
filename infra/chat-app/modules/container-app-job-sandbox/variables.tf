variable "name" {
  description = "Name of the container app job"
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

variable "container_app_environment_id" {
  description = "ID of the Container Apps environment"
  type        = string
}

variable "managed_identity_id" {
  description = "ID of the user-assigned managed identity"
  type        = string
}

variable "acr_login_server" {
  description = "ACR login server URL"
  type        = string
}

variable "image_name" {
  description = "Container image name"
  type        = string
  default     = "epi-geo-sandbox"
}

variable "image_tag" {
  description = "Container image tag"
  type        = string
  default     = "latest"
}

variable "cpu" {
  description = "CPU allocation"
  type        = number
  default     = 0.5
}

variable "memory" {
  description = "Memory allocation"
  type        = string
  default     = "1Gi"
}

variable "timeout_seconds" {
  description = "Job execution timeout in seconds"
  type        = number
  default     = 60
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
