variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Existing resource group name"
  type        = string
  default     = "rg_mpcp"
}

variable "container_app_environment_name" {
  description = "Name of the existing Container Apps environment"
  type        = string
  default     = "epi-geo-container-env"
}

variable "storage_account_name" {
  description = "Name of the existing storage account"
  type        = string
  default     = "mpcpstorageaccount"
}

variable "ingress_external" {
  description = "Whether ChromaDB ingress is externally accessible. Set to false in production."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    project = "epi-geo-chat"
    service = "vector-store"
  }
}
