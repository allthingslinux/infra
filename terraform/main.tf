terraform {
  required_version = ">= 1.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.6"
    }
  }
}

# Configure the Hetzner Cloud Provider
provider "hcloud" {
  token = var.hcloud_token
}

# Configure the Cloudflare Provider
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Data sources for available server types and images
data "hcloud_server_types" "available" {}
data "hcloud_images" "ubuntu" {
  with_selector = "name==ubuntu-22.04"
}

# SSH Key for server access
resource "hcloud_ssh_key" "default" {
  name       = "${var.project_name}-${var.environment}"
  public_key = file(var.public_key_path)
  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Network for the project
resource "hcloud_network" "main" {
  name     = "${var.project_name}-${var.environment}-network"
  ip_range = var.network_cidr
  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Subnet for servers
resource "hcloud_network_subnet" "main" {
  type         = "cloud"
  network_id   = hcloud_network.main.id
  network_zone = var.network_zone
  ip_range     = var.subnet_cidr
}

# Firewall for basic security
resource "hcloud_firewall" "main" {
  name = "${var.project_name}-${var.environment}-firewall"
  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }

  # SSH access
  rule {
    direction  = "in"
    port       = "22"
    protocol   = "tcp"
    source_ips = var.allowed_ssh_ips
  }

  # HTTP/HTTPS for web servers
  rule {
    direction  = "in"
    port       = "80"
    protocol   = "tcp"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  rule {
    direction  = "in"
    port       = "443"
    protocol   = "tcp"
    source_ips = ["0.0.0.0/0", "::/0"]
  }

  # Internal network communication
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "any"
    source_ips = [var.network_cidr]
  }

  rule {
    direction  = "in"
    protocol   = "udp"
    port       = "any"
    source_ips = [var.network_cidr]
  }

  rule {
    direction  = "in"
    protocol   = "icmp"
    source_ips = [var.network_cidr]
  }
}
