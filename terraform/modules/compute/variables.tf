variable "name" {
  description = "Name prefix for compute resources"
  type        = string
}

variable "environment" {
  description = "Environment name (production, staging, development)"
  type        = string
}

variable "server_type" {
  description = "Type of server to create"
  type        = string
  default     = "cx11"
}

variable "image" {
  description = "Server image to use"
  type        = string
  default     = "ubuntu-24.04"
}

variable "location" {
  description = "Server location"
  type        = string
  default     = "nbg1"
}

variable "network_id" {
  description = "ID of the network to attach servers to"
  type        = string
}

variable "ssh_key_ids" {
  description = "List of SSH key IDs to attach to servers"
  type        = list(string)
}

variable "servers" {
  description = "Map of servers to create"
  type = map(object({
    server_type = optional(string)
    location    = optional(string)
    image       = optional(string)
    labels      = optional(map(string), {})
  }))
  default = {}
}

variable "enable_backups" {
  description = "Enable backups for servers"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
