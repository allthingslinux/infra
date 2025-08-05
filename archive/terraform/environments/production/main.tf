terraform {
  required_version = ">= 1.6"

  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }

  # Backend configuration - uncomment and configure for remote state
  # backend "s3" {
  #   bucket = "atl-terraform-state"
  #   key    = "production/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Configure Hetzner provider
provider "hcloud" {
  token = var.hetzner_token
}

# Local values for consistent naming and tagging
locals {
  environment = "production"
  project     = "atl"

  common_tags = {
    Environment = local.environment
    Project     = local.project
    ManagedBy   = "terraform"
    Repository  = "allthingslinux/infra"
  }
}

# Create network infrastructure
module "network" {
  source = "../../modules/network"

  name        = local.project
  environment = local.environment

  ip_range = "10.0.0.0/16" # Production uses 10.0.x.x

  subnets = {
    web = {
      ip_range = "10.0.1.0/24"
      zone     = "eu-central-1"
    }
    app = {
      ip_range = "10.0.2.0/24"
      zone     = "eu-central-1"
    }
    data = {
      ip_range = "10.0.3.0/24"
      zone     = "eu-central-1"
    }
  }

  tags = local.common_tags
}

# Create security groups
module "security" {
  source = "../../modules/security"

  name        = local.project
  environment = local.environment

  # Production has stricter access controls
  allowed_ips = var.allowed_ips
  ssh_port    = 22
  web_ports   = [80, 443] # Production only standard ports

  custom_rules = [
    {
      direction   = "in"
      port        = "5432"
      protocol    = "tcp"
      source_ips  = ["10.0.0.0/16"]
      description = "PostgreSQL from internal network"
    },
    {
      direction   = "in"
      port        = "6379"
      protocol    = "tcp"
      source_ips  = ["10.0.0.0/16"]
      description = "Redis from internal network"
    }
  ]

  tags = local.common_tags
}

# Create compute instances
module "compute" {
  source = "../../modules/compute"

  name        = local.project
  environment = local.environment

  network_id = module.network.network_id

  ssh_key_ids = [module.network.ssh_key_id]

  # Server types come from domains.yml - no hardcoding here
  # Each domain defines its own server type in config/domains.yml
  server_type = "cx31" # Default fallback - should be overridden by domains.yml
  location    = "ash"  # Ashburn

  servers = {
    web = {
      server_type = "cx31" # Should come from domains.yml
      labels = {
        Role = "web-server"
        Tier = "frontend"
      }
    }
    app = {
      server_type = "cx31" # Should come from domains.yml
      labels = {
        Role = "app-server"
        Tier = "backend"
      }
    }
  }

  enable_backups = true # Enable backups in production

  tags = local.common_tags
}
