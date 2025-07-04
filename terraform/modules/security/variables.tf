variable "name" {
  description = "Name prefix for security resources"
  type        = string
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
}

variable "allowed_ips" {
  description = "List of IP addresses allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Should be restricted in production
}

variable "ssh_port" {
  description = "SSH port to allow"
  type        = number
  default     = 22
}

variable "web_ports" {
  description = "List of web ports to allow"
  type        = list(number)
  default     = [80, 443]
}

variable "custom_rules" {
  description = "Custom firewall rules"
  type = list(object({
    direction   = string
    port        = optional(string)
    protocol    = optional(string, "tcp")
    source_ips  = optional(list(string), [])
    description = optional(string)
  }))
  default = []
}

variable "enable_ddos_protection" {
  description = "Enable DDoS protection"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
