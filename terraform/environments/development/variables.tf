variable "hetzner_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}









variable "enable_backups" {
  description = "Enable automated backups"
  type        = bool
  default     = false # Disabled in development to save costs
}
