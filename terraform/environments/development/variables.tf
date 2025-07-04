variable "hetzner_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
  default     = null
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key file"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "allowed_ssh_ips" {
  description = "List of IP addresses allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Development default - should be restricted
}

variable "enable_monitoring" {
  description = "Enable monitoring services"
  type        = bool
  default     = false # Disabled in development to save costs
}

variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = false # Disabled in development to save costs
}
