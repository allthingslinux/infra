variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key for server access"
  type        = string
}

variable "domain" {
  description = "Base domain for the infrastructure"
  type        = string
  default     = "atl.services"
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Hetzner Cloud region"
  type        = string
  default     = "fsn1"
}

variable "server_type" {
  description = "Default server type"
  type        = string
  default     = "cpx21"
}

variable "private_network_cidr" {
  description = "CIDR block for the private network"
  type        = string
  default     = "10.0.1.0/24"
}
