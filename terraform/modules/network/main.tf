terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

# Create private network
resource "hcloud_network" "main" {
  name     = "${var.name}-${var.environment}"
  ip_range = var.ip_range
  labels = merge(var.tags, {
    Environment = var.environment
    Module      = "network"
    Name        = "${var.name}-${var.environment}"
  })
}

# Create network subnets
resource "hcloud_network_subnet" "subnets" {
  for_each = var.subnets

  network_id   = hcloud_network.main.id
  type         = "cloud"
  network_zone = var.network_zone
  ip_range     = each.value.ip_range
}

# Create SSH key for instances
resource "hcloud_ssh_key" "default" {
  name       = "${var.name}-${var.environment}-key"
  public_key = file("~/.ssh/id_rsa.pub")
  labels = merge(var.tags, {
    Environment = var.environment
    Module      = "network"
  })
}
