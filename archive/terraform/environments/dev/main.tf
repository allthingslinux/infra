locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "opentofu"
    Project     = "allthingslinux"
  }
}

# Create a new SSH key
resource "hcloud_ssh_key" "default" {
  name       = "atl-${var.environment}-key"
  public_key = var.ssh_public_key
}

# Create private network
resource "hcloud_network" "private_network" {
  name     = "atl-${var.environment}-network"
  ip_range = var.private_network_cidr
}

# Create subnet
resource "hcloud_network_subnet" "private_subnet" {
  network_id   = hcloud_network.private_network.id
  type         = "server"
  network_zone = "eu-central"
  ip_range     = var.private_network_cidr
}

# Create firewall
resource "hcloud_firewall" "default" {
  name = "atl-${var.environment}-firewall"
  
  rule {
    direction  = "in"
    protocol   = "icmp"
    source_ips = ["0.0.0.0/0"]
  }
  
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0"]
  }
  
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0"]
  }
  
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0"]
  }
}

# Create control plane server
resource "hcloud_server" "control_plane" {
  name        = "ctrl1-${var.environment}"
  server_type = var.server_type
  image       = "ubuntu-22.04"
  location    = var.region
  
  ssh_keys = [hcloud_ssh_key.default.id]
  
  network {
    network_id = hcloud_network.private_network.id
    ip         = cidrhost(var.private_network_cidr, 10) # 10.0.1.10
  }
  
  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
  
  labels = merge(local.common_tags, {
    Role = "control-plane"
  })
}

# Attach firewall to control plane
resource "hcloud_firewall_attachment" "control_plane" {
  firewall_id = hcloud_firewall.default.id
  server_ids  = [hcloud_server.control_plane.id]
}

# Output important information
output "control_plane_public_ip" {
  value = hcloud_server.control_plane.ipv4_address
}

output "control_plane_private_ip" {
  value = hcloud_server.control_network.ip
}
