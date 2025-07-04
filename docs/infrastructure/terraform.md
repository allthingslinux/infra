# Terraform Infrastructure

This document provides an overview of the Terraform infrastructure used in the All Things Linux project.

## 🏗️ **Overview**

Our Terraform configuration manages:

- **Hetzner Cloud Server Provisioning**: Automated server creation with proper sizing and placement
- **Cloudflare DNS Management**: Automated DNS record creation and management
- **Cloudflare CDN Configuration**: Performance optimization and security settings
- **Multi-Environment Support**: Separate configurations for staging and production
- **Integration with Ansible**: Outputs used by Ansible for configuration management

## 📦 **Module Structure**

### Main Configuration (`terraform/`)

The root terraform directory contains the primary infrastructure configuration:

| File | Purpose |
|------|---------|
| `main.tf` | Provider configuration and shared resources |
| `variables.tf` | Variable definitions and descriptions |
| `outputs.tf` | Output values for Ansible integration |
| `domains.tf` | Dynamic infrastructure from domains.yml |
| `load_balancer.tf` | Load balancer configuration |

### Environment Management

- **Staging**: `environments/staging/terraform.tfvars`
- **Production**: `environments/production/terraform.tfvars`

## 🚀 **Key Features**

### Dynamic Domain Management

Infrastructure is dynamically generated from `domains.yml`, providing:

- Single source of truth for all services
- Automatic DNS record creation
- SSL certificate management
- Service-specific configurations

### Hetzner Cloud Integration

- Automated server provisioning
- Network and firewall configuration
- Cloud-init for initial setup
- SSH key management

### Cloudflare Integration

- DNS record management for all services
- SSL/TLS termination and optimization
- Caching and performance optimization
- Security features (DDoS protection, WAF)

## 🛠️ **Usage**

### Prerequisites

- Terraform >= 1.0
- Hetzner Cloud API token
- Cloudflare API token
- Environment-specific `.tfvars` files

### Deployment Commands

```bash
# Initialize Terraform
terraform init

# Plan deployment for staging
terraform plan -var-file="environments/staging/terraform.tfvars"

# Apply changes
terraform apply -var-file="environments/staging/terraform.tfvars"

# Use our automated CLI tool (recommended)
atl apply --target infrastructure
```

## 📊 **Resource Overview**

### Providers Used

| Provider | Version | Purpose |
|----------|---------|---------|
| `hashicorp/hcloud` | ~> 1.45 | Hetzner Cloud resources |
| `cloudflare/cloudflare` | ~> 5.6 | DNS and CDN management |

### Key Resources

#### Hetzner Cloud Resources

- **Servers**: Dynamic server creation based on domains.yml
- **Networks**: Private networking with proper CIDR allocation
- **Load Balancer**: High-availability load balancing
- **Firewall**: Security rules and access control
- **SSH Keys**: Automated key management

#### Cloudflare Resources

- **DNS Zones**: Domain zone management
- **DNS Records**: Automatic A/AAAA record creation
- **Origin Certificates**: SSL certificate automation
- **Page Rules**: Performance and caching optimization

## 🔧 **Integration**

### Ansible Integration

Terraform outputs are consumed by Ansible for:

- Dynamic inventory generation
- Server configuration management
- Service deployment coordination

### CLI Tool Integration

Our infrastructure CLI (`atl infra`) provides:

- Unified infrastructure management
- Environment-aware deployments
- Validation and safety checks
- Rich progress reporting

## 🔍 **Monitoring**

The Terraform configuration includes:

- Resource tagging for monitoring
- Output values for health checks
- Integration with monitoring systems
- Audit logging capabilities

---

> **Note**: This infrastructure is designed to be fully automated and managed through our CLI tools. Manual terraform commands should only be used for debugging or advanced operations.
