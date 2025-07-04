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
  default     = "ubuntu-22.04"
}

variable "backup_enabled" {
  description = "Whether to enable backup server"
  type        = bool
  default     = true
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

variable "domain_name" {
  description = "Domain name managed by Cloudflare"
  type        = string
}

variable "dns_ttl" {
  description = "DNS TTL for records"
  type        = number
  default     = 300
}

variable "cloudflare_proxy_enabled" {
  description = "Enable Cloudflare proxy (orange cloud)"
  type        = bool
  default     = true
}

variable "cloudflare_ssl_mode" {
  description = "SSL mode (off, flexible, full, strict)"
  type        = string
  default     = "full"
}

variable "cloudflare_always_https" {
  description = "Always use HTTPS"
  type        = bool
  default     = true
}

variable "cloudflare_security_level" {
  description = "Security level (essentially_off, low, medium, high, under_attack)"
  type        = string
  default     = "medium"
}

variable "enable_wildcard_dns" {
  description = "Enable wildcard DNS record"
  type        = bool
  default     = false
}

variable "enable_api_caching" {
  description = "Enable API endpoint caching"
  type        = bool
  default     = false
}

variable "enable_rate_limiting" {
  description = "Enable rate limiting"
  type        = bool
  default     = true
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
