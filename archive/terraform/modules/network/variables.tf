variable "name" {
  description = "Name prefix for network resources"
  type        = string
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
}

variable "network_zone" {
  description = "Hetzner network zone"
  type        = string
  default     = "eu-central"
}

variable "ip_range" {
  description = "IP range for the private network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnets" {
  description = "Map of subnets to create"
  type = map(object({
    ip_range = string
    zone     = string
  }))
  default = {
    web = {
      ip_range = "10.0.1.0/24"
      zone     = "eu-central-1"
    }
    app = {
      ip_range = "10.0.2.0/24"
      zone     = "eu-central-1"
    }
    data = {
      ip_range = "10.0.3.0/24"
      zone     = "eu-central-1"
    }
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
