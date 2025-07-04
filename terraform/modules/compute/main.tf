terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

# Create servers
resource "hcloud_server" "servers" {
  for_each = var.servers

  name        = "${var.name}-${each.key}-${var.environment}"
  image       = coalesce(each.value.image, var.image)
  server_type = coalesce(each.value.server_type, var.server_type)
  location    = coalesce(each.value.location, var.location)
  ssh_keys    = var.ssh_key_ids

  # Enable backups based on environment
  backups = var.enable_backups

  # Startup script
  user_data = templatefile("${path.module}/templates/cloud-init.yml", {
    hostname = "${var.name}-${each.key}-${var.environment}"
  })

  labels = merge(
    var.tags,
    each.value.labels,
    {
      Environment = var.environment
      Module      = "compute"
      Name        = "${var.name}-${each.key}-${var.environment}"
      Role        = each.key
    }
  )

  # Prevent destruction of production servers
  lifecycle {
    prevent_destroy = false # Set to true for production
  }
}

# Attach servers to private network
resource "hcloud_server_network" "server_networks" {
  for_each = var.servers

  server_id  = hcloud_server.servers[each.key].id
  network_id = var.network_id
}
