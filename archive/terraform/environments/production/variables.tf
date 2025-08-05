variable "hetzner_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "allowed_ips" {
  description = "List of IP addresses allowed to access the infrastructure"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Configure appropriately for production
}

variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = true # Enabled in production
}
