variable "name" {
  description = "Name of the static web app"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region (Static Web Apps supports: westus2, centralus, eastus2, westeurope, eastasia)"
  type        = string
  default     = "westeurope"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
