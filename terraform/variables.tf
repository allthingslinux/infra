variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "allthingslinux"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
}

variable "public_key_path" {
  description = "Path to the public SSH key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "server_image" {
  description = "Server image to use for all servers"
  type        = string
  default     = "ubuntu-24.04"
}

variable "network_cidr" {
  description = "CIDR block for the main network"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  description = "CIDR block for the subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "network_zone" {
  description = "Network zone for the subnet"
  type        = string
  default     = "eu-central"
}

variable "allowed_ssh_ips" {
  description = "List of IP addresses allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Restrict this in production
}

# Domain-based server configurations
# Note: Server configurations are now defined in domains.yml
# This provides a single source of truth for all infrastructure

variable "load_balancer_enabled" {
  description = "Whether to create a load balancer"
  type        = bool
  default     = false
}

variable "load_balancer_type" {
  description = "Type of load balancer"
  type        = string
  default     = "lb11"
}

# Cloudflare variables
variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
  sensitive   = true
}

variable "dns_ttl" {
  description = "DNS TTL for records"
  type        = number
  default     = 300
}

variable "enable_api_caching" {
  description = "Enable API endpoint caching"
  type        = bool
  default     = false
}

variable "enable_origin_ca" {
  description = "Enable Cloudflare Origin CA certificate"
  type        = bool
  default     = false
}

variable "csr_content" {
  description = "CSR content for Origin CA certificate"
  type        = string
  default     = ""
}

# Note: Domain configurations are now defined in domains.yml
# This provides a single source of truth for all domain infrastructure

variable "server_locations" {
  description = "List of server locations"
  type        = list(string)
  default     = []
}
