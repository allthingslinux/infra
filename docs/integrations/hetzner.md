# Hetzner Cloud Integration Guide

This guide explains how to use the integrated Terraform + Ansible setup for managing All Things Linux infrastructure on Hetzner Cloud.

## Overview

Our infrastructure setup uses:

- **Terraform** for provisioning Hetzner Cloud resources (servers, networks, load balancers)
- **Ansible** for configuring and managing the provisioned infrastructure
- **uv** for dependency management
- **Environment isolation** for development, staging, and production

## Prerequisites

### 1. Hetzner Cloud Account and API Token

1. Create a Hetzner Cloud account at [console.hetzner.cloud](https://console.hetzner.cloud/)
2. Create a new project for All Things Linux
3. Generate an API token:
   - Go to Security → API Tokens
   - Create a new token with Read & Write permissions
   - Save the token securely

### 2. SSH Key Setup

Ensure you have an SSH key pair:

```bash
# Generate a new SSH key if you don't have one
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# The public key will be automatically uploaded to Hetzner Cloud
```

### 3. Environment Variables

Set your Hetzner Cloud API token:

```bash
export HCLOUD_TOKEN="your-hetzner-cloud-api-token"
```

## Directory Structure

```text
terraform/
├── main.tf                           # Main Terraform configuration
├── variables.tf                      # Variable definitions
├── domains.tf                        # Dynamic server resources
├── load_balancer.tf                  # Load balancer configuration
├── outputs.tf                        # Outputs for Ansible
├── templates/
│   └── cloud-init.yml               # Server initialization template
└── environments/
    ├── development/
    │   └── terraform.tfvars         # Development configuration
    ├── staging/
    │   └── terraform.tfvars         # Staging configuration
    └── production/
        └── terraform.tfvars         # Production configuration
```

## Infrastructure Environments

### Development Environment

- **Purpose**: Local development and testing
- **Resources**: 3 servers (web, app, db)
- **Server Types**: cx11 (1 vCPU, 2GB) to cx21 (2 vCPU, 4GB)
- **Load Balancer**: Disabled
- **Network**: 10.0.0.0/16

### Staging Environment

- **Purpose**: Pre-production testing
- **Resources**: 4 servers with redundancy
- **Server Types**: cx21 (2 vCPU, 4GB) to cx31 (2 vCPU, 8GB)
- **Load Balancer**: Enabled (lb11)
- **Network**: 10.1.0.0/16

### Production Environment

- **Purpose**: Live production workloads
- **Resources**: 7 servers with full redundancy
- **Server Types**: cx31 (2 vCPU, 8GB) to cx51 (8 vCPU, 32GB)
- **Load Balancer**: Enabled (lb21)
- **Network**: 10.2.0.0/16

## Available Server Types

| Type | vCPU | RAM | Storage | Monthly Cost (EUR) |
|------|------|-----|---------|-------------------|
| cx11 | 1    | 2GB | 20GB   | ~3.29             |
| cx21 | 2    | 4GB | 40GB   | ~5.83             |
| cx31 | 2    | 8GB | 80GB   | ~10.05            |
| cx41 | 4    | 16GB| 160GB  | ~18.49            |
| cx51 | 8    | 32GB| 240GB  | ~35.37            |

## Available Locations

- **nbg1**: Nuremberg, Germany
- **fsn1**: Falkenstein, Germany
- **hel1**: Helsinki, Finland
- **ash**: Ashburn, Virginia, USA

## Deployment Commands

### Quick Start

```bash
# 1. Set up your environment
export HCLOUD_TOKEN="your-token-here"

# 2. Ensure uv environment is active
source .venv/bin/activate  # or use uv run for each command

# 3. Plan development infrastructure
./scripts/terraform-deploy.sh -e development

# 4. Deploy development infrastructure
./scripts/terraform-deploy.sh -e development -a apply

# 5. Deploy staging (with auto-approve)
./scripts/terraform-deploy.sh -e staging -a apply -y
```

### Detailed Commands

#### Planning Changes

```bash
# Plan changes for any environment (uv will auto-activate)
./scripts/terraform-deploy.sh -e development
./scripts/terraform-deploy.sh -e staging
./scripts/terraform-deploy.sh -e production
```

#### Applying Changes

```bash
# Apply with manual approval
./scripts/terraform-deploy.sh -e development -a apply

# Apply with auto-approval (use carefully!)
./scripts/terraform-deploy.sh -e staging -a apply -y
```

#### Configuration-Only Updates

```bash
# Run only Ansible on existing infrastructure
./scripts/terraform-deploy.sh -e development --ansible-only
```

#### Infrastructure-Only Updates

```bash
# Run only Terraform (skip Ansible configuration)
./scripts/terraform-deploy.sh -e staging --terraform-only
```

#### Destroying Infrastructure

```bash
# Destroy environment (with confirmation)
./scripts/terraform-deploy.sh -e development -a destroy

# Destroy with auto-approval
./scripts/terraform-deploy.sh -e development -a destroy -y
```

## Customizing Server Configuration

### Dynamic Configuration via domains.yml

The modern approach uses `domains.yml` for configuration:

```yaml
domains:
  example_domain:
    enabled: true
    domain: "example.allthingslinux.org"
    server:
      type: "cx31"           # 2 vCPU, 8GB RAM
      location: "ash"        # Ashburn, Virginia
      count: 2              # Number of servers
    services:
      - docker
      - nginx
      - monitoring
    features:
      ssl: true
      backup: true
```

### Environment-Specific Overrides

Edit the environment-specific `terraform.tfvars` files:

```hcl
# terraform/environments/development/terraform.tfvars

# Override server types for development
server_type_overrides = {
  web = "cx11"    # Smaller for development
  app = "cx21"    # Medium for testing
  db  = "cx31"    # Larger for data
}
```

### Adding Custom Volumes

```hcl
# Add additional storage volumes
volumes = {
  data_volume = {
    name = "app-data"
    size = 50
    server = "app"
  }
}
```

## Security Considerations

### SSH Access

**Development**: Open to all IPs (0.0.0.0/0)
**Production**: Restrict to specific IPs in `terraform.tfvars`:

```hcl
allowed_ssh_ips = [
  "203.0.113.0/24",  # Office network
  "198.51.100.5/32"  # Admin home IP
]
```

### Firewall Rules

The Terraform configuration automatically creates:

- SSH access on port 22
- HTTP/HTTPS access on ports 80/443
- Internal network communication
- Custom rules as needed

### API Token Security

- Store `HCLOUD_TOKEN` securely (never commit to git)
- Use different tokens for different environments
- Rotate tokens regularly
- Use read-only tokens where possible

## Ansible Integration

### Dynamic Inventory

The Terraform deployment automatically generates Ansible inventory:

```json
{
  "all": {
    "children": {
      "hetzner": {
        "hosts": {
          "allthingslinux-development-web": {
            "ansible_host": "1.2.3.4",
            "ansible_user": "root",
            "private_ip": "10.0.1.10",
            "role": "web",
            "environment": "development"
          }
        }
      }
    }
  }
}
```

### Running Ansible Manually

```bash
# Using the generated inventory (with uv)
uv run ansible-playbook \
  -i inventories/development/terraform_inventory.json \
  -e "environment=development" \
  playbooks/dynamic-deploy.yml

# Using the dynamic inventory script
uv run ansible-playbook \
  -i inventories/dynamic.py \
  -e "environment=development" \
  playbooks/dynamic-deploy.yml
```

## Monitoring and Maintenance

### Checking Infrastructure Status

```bash
# View current infrastructure
cd terraform
terraform workspace select development
terraform show

# Check server status in Hetzner Console
# https://console.hetzner.cloud/
```

### Cost Monitoring

- Monitor costs in Hetzner Console
- Development environment: ~€15-20/month
- Staging environment: ~€40-60/month
- Production environment: ~€150-200/month

### Backup Strategy

- Database volumes are automatically backed up
- Consider additional backup automation with Ansible
- Use Hetzner's snapshot feature for system backups

## Troubleshooting

### Common Issues

#### "HCLOUD_TOKEN not set"

```bash
export HCLOUD_TOKEN="your-token-here"
```

#### "SSH connection failed"

- Check if your SSH key is correct
- Verify firewall rules allow your IP
- Wait for cloud-init to complete (~2-3 minutes)

#### "Terraform state locked"

```bash
cd terraform
terraform force-unlock LOCK_ID
```

#### "Inventory file not found"

- Run `terraform apply` first
- Check that the environment name is correct

### Getting Help

1. Check Hetzner Cloud documentation: <https://docs.hetzner.cloud/>
2. Terraform Hetzner provider docs: <https://registry.terraform.io/providers/hetznercloud/hcloud/>
3. Open an issue in the repository

## Migration from Existing Infrastructure

If you have existing servers, you can import them into Terraform:

```bash
# Import existing server
terraform import hcloud_server.servers["web"] 12345

# Import existing network
terraform import hcloud_network.main 67890
```

## Cost Optimization Tips

1. **Right-size your servers**: Start small and scale up as needed
2. **Use volumes for data**: Cheaper than larger server storage
3. **Leverage multiple locations**: Better performance and redundancy
4. **Monitor usage**: Use Hetzner's cost tracking tools
5. **Automate shutdown**: For development environments

## Resources

- [Hetzner Cloud API Documentation](https://docs.hetzner.cloud/)
- [Terraform Hetzner Provider](https://registry.terraform.io/providers/hetznercloud/hcloud/)
- [Hetzner Cloud Console](https://console.hetzner.cloud/)
- [Hetzner Cloud Community](https://community.hetzner.com/)
