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
  #   key    = "development/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Configure Hetzner provider
provider "hcloud" {
  token = var.hetzner_token
}

# Local values for consistent naming and tagging
locals {
  environment = "development"
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

  ip_range = "10.1.0.0/16" # Development uses 10.1.x.x

  subnets = {
    web = {
      ip_range = "10.1.1.0/24"
      zone     = "eu-central-1"
    }
    app = {
      ip_range = "10.1.2.0/24"
      zone     = "eu-central-1"
    }
    data = {
      ip_range = "10.1.3.0/24"
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

  # Development allows broader access for testing
  allowed_ips = ["0.0.0.0/0"]
  ssh_port    = 22
  web_ports   = [80, 443, 8080, 3000] # Include dev ports

  custom_rules = [
    {
      direction   = "in"
      port        = "5432"
      protocol    = "tcp"
      source_ips  = ["10.1.0.0/16"]
      description = "PostgreSQL from internal network"
    },
    {
      direction   = "in"
      port        = "6379"
      protocol    = "tcp"
      source_ips  = ["10.1.0.0/16"]
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

  network_id  = module.network.network_id
  subnet_id   = module.network.subnet_ids["web"]
  ssh_key_ids = [module.network.ssh_key_id]

  # Development uses smaller, cheaper instances
  server_type = "cx11" # 1 vCPU, 2 GB RAM
  location    = "nbg1" # Nuremberg

  servers = {
    web = {
      server_type = "cx11"
      labels = {
        Role = "web-server"
        Tier = "frontend"
      }
    }
    app = {
      server_type = "cx21" # Slightly larger for app server
      labels = {
        Role = "app-server"
        Tier = "backend"
      }
    }
  }

  enable_backups = false # Save costs in development

  tags = local.common_tags
}
