# All Things Linux - Infrastructure Guide

Welcome to the infrastructure guide for All Things Linux. This document provides a high-level overview of our infrastructure philosophy, technology stack, and operational principles.

## Philosophy

Our infrastructure is built on the following core principles:

- **Automation First**: All infrastructure is managed as code. Manual changes are prohibited.
- **Security by Design**: Security is integrated into every layer of the stack.
- **Cost Optimization**: We strive to use resources efficiently and minimize costs.
- **Open Source**: We use and contribute to open-source software wherever possible.

## Technology Stack

Our infrastructure is built on a modern, cloud-native technology stack:

| Component | Technology |
|---|---|
| **Cloud Provider**| [Hetzner Cloud](../integrations/hetzner.md) |
| **DNS & CDN** | [Cloudflare](../integrations/cloudflare.md) |
| **IaC** | Terraform |
| **Automation** | Ansible |
| **Container** | Docker |
| **CI/CD** | GitHub Actions |

For more details on each component, refer to the respective documentation in the integrations section.

## 🏗️ Infrastructure Overview

Our infrastructure is **data-driven** and **dynamic**, with all configuration managed through `domains.yml`. This approach provides:

- **Single source of truth** for all infrastructure
- **Dynamic generation** of servers, DNS, and configurations
- **Environment consistency** across development, staging, and production
- **Easy scaling** and modification

## 📋 Domain Management

### Understanding domains.yml

The `domains.yml` file defines your entire infrastructure:

```yaml
domains:
  atl_wiki:
    enabled: true                    # Deploy this domain
    required: false                  # Can be disabled
    external: false                  # Runs on our infrastructure
    domain: "atl.wiki"               # Actual domain name

    # Server configuration
    server:
      type: "cx31"                   # Hetzner server type
      location: "ash"                # Server location
      count: 1                       # Number of servers

    # Services to deploy
    services:
      - docker
      - nginx
      - mediawiki

    # DNS subdomains
    subdomains:
      - api
      - admin

    # Optional features
    features:
      ssl: true
      backup: true
      monitoring: true

    # Network configuration
    network:
      subnet: "172.20.0.0/16"

    # Custom ports
    ports:
      - 8080
      - 9000
```

### Adding a New Domain

1. **Edit domains.yml**:

```yaml
domains:
  new_service:
    enabled: true
    domain: "new.allthingslinux.org"
    server:
      type: "cx21"
      location: "ash"
      count: 1
    services:
      - docker
      - nginx
    subdomains:
      - api
    features:
      ssl: true
      backup: true
```

2. **Deploy the domain**:

```bash
# Plan infrastructure changes
./scripts/deploy-dynamic.sh infrastructure plan

# Apply infrastructure
./scripts/deploy-dynamic.sh infrastructure apply

# Configure the domain
./scripts/deploy-dynamic.sh domain new_service
```

3. **Verify deployment**:

```bash
# Check domain status
./scripts/deploy-dynamic.sh config

# Test connectivity
dig new.allthingslinux.org
curl -I https://new.allthingslinux.org
```

### Modifying Existing Domains

#### Scale Up Server Resources

```yaml
domains:
  atl_wiki:
    server:
      type: "cx41"  # Upgrade from cx31 to cx41 (4 vCPU, 16GB)
      count: 2      # Add a second server
```

```bash
# Apply changes
./scripts/deploy-dynamic.sh infrastructure plan
./scripts/deploy-dynamic.sh infrastructure apply
```

#### Add New Services

```yaml
domains:
  atl_tools:
    services:
      - docker
      - nginx
      - nextcloud
      - redis      # Add Redis
      - postgresql # Add PostgreSQL
```

```bash
# Deploy new services
./scripts/deploy-dynamic.sh domain atl_tools --tags redis,postgresql
```

#### Add Subdomains

```yaml
domains:
  atl_dev:
    subdomains:
      - api
      - admin
      - docs       # Add documentation subdomain
      - status     # Add status page
```

```bash
# Update DNS and configuration
./scripts/deploy-dynamic.sh domain atl_dev
```

### Removing Domains

#### Temporary Disable

```bash
# Disable domain (keeps configuration)
./scripts/deploy-dynamic.sh disable atl_dev
```

This sets `enabled: false` in domains.yml and removes the domain from active infrastructure.

#### Permanent Removal

1. **Backup data** (if needed):

```bash
# Backup before removal
ansible atl_dev_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/backup.sh"
```

2. **Disable and remove**:

```bash
# Disable domain
./scripts/deploy-dynamic.sh disable atl_dev

# Remove from infrastructure
./scripts/deploy-dynamic.sh infrastructure plan
./scripts/deploy-dynamic.sh infrastructure apply
```

3. **Clean up configuration**:

```yaml
# Remove from domains.yml
domains:
  # atl_dev: removed
```

## 🔧 Server Management

### Server Types and Sizing

| Type | vCPU | RAM | Storage | Use Case | Monthly Cost |
|------|------|-----|---------|----------|--------------|
| cx11 | 1 | 2GB | 20GB | Development, testing | ~€3.29 |
| cx21 | 2 | 4GB | 40GB | Small services | ~€5.83 |
| cx31 | 2 | 8GB | 80GB | Medium workloads | ~€10.05 |
| cx41 | 4 | 16GB | 160GB | Production services | ~€18.49 |
| cx51 | 8 | 32GB | 240GB | High-performance apps | ~€35.37 |

### Vertical Scaling (Resize Servers)

```yaml
# In domains.yml - upgrade server type
domains:
  atl_wiki:
    server:
      type: "cx41"  # Upgrade from cx31
```

```bash
# Apply changes (requires server restart)
./scripts/deploy-dynamic.sh infrastructure plan
./scripts/deploy-dynamic.sh infrastructure apply

# Reconfigure services for new resources
./scripts/deploy-dynamic.sh domain atl_wiki
```

### Horizontal Scaling (Add Servers)

```yaml
# Add more servers to a domain
domains:
  atl_tools:
    server:
      count: 3  # Scale from 1 to 3 servers
```

```bash
# Deploy additional servers
./scripts/deploy-dynamic.sh infrastructure apply

# Configure load balancing
./scripts/deploy-dynamic.sh domain atl_tools --tags loadbalancer
```

### Geographic Distribution

```yaml
# Deploy servers in multiple locations
domains:
  atl_services:
    server:
      type: "cx31"
      locations:
        - "ash"    # Ashburn, USA
        - "fsn1"   # Falkenstein, Germany
        - "hel1"   # Helsinki, Finland
      count: 1     # 1 server per location
```

## 🌐 Network Management

### Private Networks

Each domain gets its own private network:

```yaml
domains:
  atl_database:
    network:
      subnet: "172.30.0.0/16"       # Custom subnet
      dns_servers:
        - "1.1.1.1"
        - "8.8.8.8"
```

### Load Balancer Configuration

```yaml
domains:
  atl_web:
    load_balancer:
      enabled: true
      type: "lb11"                   # Load balancer type
      algorithm: "round_robin"       # Or "least_connections"
      health_check:
        protocol: "http"
        port: 80
        path: "/health"
        interval: 10
```

### Firewall Rules

```yaml
domains:
  atl_api:
    firewall:
      rules:
        - port: 8080
          source: "0.0.0.0/0"       # Public access
        - port: 5432
          source: "172.20.0.0/16"   # Database access from private network
        - port: 22
          source: "203.0.113.0/24"  # SSH from office network
```

## 📊 Monitoring and Maintenance

### Health Monitoring

```bash
# Check all domains status
./scripts/deploy-dynamic.sh config

# Monitor system resources
ansible all -i inventories/dynamic.py -a "df -h && free -m"

# Check service status
ansible all -i inventories/dynamic.py -a "docker compose ps"

# Monitor logs
ansible web_servers -i inventories/dynamic.py \
  -a "tail -f /var/log/nginx/access.log"
```

### Automated Monitoring

Enable monitoring in domains.yml:

```yaml
domains:
  atl_production:
    monitoring:
      enabled: true
      critical: true                 # Alert on failures
      metrics:
        - cpu
        - memory
        - disk
        - network
      alerts:
        email: "admin@allthingslinux.org"
        slack: "#infrastructure"
```

### Backup Management

```yaml
domains:
  atl_wiki:
    backup:
      enabled: true
      schedule: "0 2 * * *"          # Daily at 2 AM
      retention: 30                  # Keep 30 days
      destinations:
        - "s3://atl-backups/"
        - "hetzner://volumes/backup"
```

```bash
# Manual backup
ansible atl_wiki_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/backup.sh"

# Restore from backup
ansible atl_wiki_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/restore.sh 2024-01-15"
```

## 🔄 Environment Management

### Environment-Specific Configuration

The same domains.yml works across environments with automatic adjustments:

```yaml
# Environment overrides (automatic)
environments:
  development:
    server_types:
      default: "cx11"               # Smaller servers
    features:
      ssl: false                    # Skip SSL
      monitoring: false             # No monitoring

  staging:
    server_types:
      default: "cx21"               # Medium servers
    features:
      ssl: true                     # Staging SSL
      monitoring: true              # Basic monitoring

  production:
    server_types:
      default: "cx31"               # Production servers
    features:
      ssl: true                     # Full SSL
      monitoring: true              # Full monitoring
      backup: true                  # Automated backups
```

### Promoting Between Environments

```bash
# Test in development
export ATL_ENVIRONMENT=development
./scripts/deploy-dynamic.sh all

# Promote to staging
export ATL_ENVIRONMENT=staging
./scripts/deploy-dynamic.sh all

# Deploy to production
export ATL_ENVIRONMENT=production
./scripts/deploy-dynamic.sh infrastructure plan  # Always plan first
./scripts/deploy-dynamic.sh infrastructure apply
./scripts/deploy-dynamic.sh all
```

## 🚨 Disaster Recovery

### Infrastructure Backup

```bash
# Backup Terraform state
cd terraform
terraform state pull > backups/terraform-state-$(date +%Y%m%d).json

# Backup domains configuration
cp domains.yml backups/domains-$(date +%Y%m%d).yml

# Backup Ansible vault
cp group_vars/all.yml backups/vault-$(date +%Y%m%d).yml
```

### Recovery Procedures

#### Complete Infrastructure Loss

```bash
# 1. Restore configuration
git clone https://github.com/allthingslinux/infra.git
cd infra

# 2. Restore environment variables
export HCLOUD_TOKEN="your-token"
export CLOUDFLARE_API_TOKEN="your-token"

# 3. Deploy infrastructure
./scripts/deploy-dynamic.sh infrastructure apply

# 4. Restore data from backups
ansible all -i inventories/dynamic.py \
  -a "/opt/atl/scripts/restore.sh latest"

# 5. Deploy all services
./scripts/deploy-dynamic.sh all
```

#### Single Domain Recovery

```bash
# 1. Check domain status
./scripts/deploy-dynamic.sh config

# 2. Redeploy infrastructure if needed
./scripts/deploy-dynamic.sh infrastructure apply

# 3. Redeploy domain configuration
./scripts/deploy-dynamic.sh domain atl_wiki

# 4. Restore data if needed
ansible atl_wiki_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/restore.sh"
```

## 📈 Performance Optimization

### Resource Optimization

```
