# Configuration Reference

This reference documents all configuration options for the All Things Linux infrastructure.

## 🎯 domains.yml Structure

The `domains.yml` file is the single source of truth for your infrastructure configuration.

### Basic Domain Structure

```yaml
domains:
  domain_name:
    enabled: true
    domain: "example.com"
    server:
      type: "cx31"
      location: "ash"
      count: 1
    services:
      - docker
      - nginx
```

## 🖥️ Server Configuration

### Server Types

| Type | vCPU | RAM | Storage | Monthly Cost (EUR) |
|------|------|-----|---------|-------------------|
| cx11 | 1 | 2GB | 20GB | ~3.29 |
| cx21 | 2 | 4GB | 40GB | ~5.83 |
| cx31 | 2 | 8GB | 80GB | ~10.05 |
| cx41 | 4 | 16GB | 160GB | ~18.49 |
| cx51 | 8 | 32GB | 240GB | ~35.37 |

### Server Locations

| Code | Location | Country |
|------|----------|---------|
| ash | Ashburn | United States |
| fsn1 | Falkenstein | Germany |
| nbg1 | Nuremberg | Germany |
| hel1 | Helsinki | Finland |

### Full Server Configuration

```yaml
domains:
  example_domain:
    server:
      type: "cx31"
      location: "ash"
      count: 1
      image: "ubuntu-22.04"
      ssh_keys:
        - "default"
      labels:
        environment: "production"
      volumes:
        - name: "data"
          size: 50
          mount_point: "/data"
```

## 🌐 Network Configuration

```yaml
domains:
  example_domain:
    network:
      subnet: "172.20.0.0/16"
      dns_servers:
        - "1.1.1.1"
        - "8.8.8.8"

    firewall:
      rules:
        - port: 80
          source: "0.0.0.0/0"
        - port: 443
          source: "0.0.0.0/0"
        - port: 22
          source: "203.0.113.0/24"
```

## 🔧 Services Configuration

### Available Services

```yaml
services:
  # Core services
  - docker
  - nginx
  - ssl

  # Databases
  - postgresql
  - mysql
  - redis
  - mongodb

  # Applications
  - mediawiki
  - nextcloud
  - discourse
  - ghost

  # Monitoring
  - prometheus
  - grafana
  - loki
```

## 🌍 DNS Configuration

```yaml
domains:
  example_domain:
    domain: "example.allthingslinux.org"
    dns:
      ttl: 300
      proxied: true
    subdomains:
      - api
      - admin
      - docs
```

## 🔒 SSL Configuration

```yaml
domains:
  example_domain:
    ssl:
      enabled: true
      provider: "letsencrypt"
      force_https: true
      hsts: true
```

## 🎛️ Features Configuration

```yaml
domains:
  example_domain:
    features:
      ssl: true
      firewall: true
      caching: true
      backup: true
      monitoring: true
```

## 📊 Monitoring Configuration

```yaml
domains:
  example_domain:
    monitoring:
      enabled: true
      critical: false
      metrics:
        - cpu
        - memory
        - disk
        - network
      alerts:
        email: "admin@allthingslinux.org"
        slack: "#infrastructure"
```

## 🔧 Environment Configuration

```yaml
environments:
  development:
    defaults:
      server_type: "cx11"
      ssl: false
      monitoring: false

  production:
    defaults:
      server_type: "cx31"
      ssl: true
      monitoring: true
      backup: true
```

## 📋 Complete Example

```yaml
domains:
  atl_wiki:
    enabled: true
    domain: "atl.wiki"

    server:
      type: "cx31"
      location: "ash"
      count: 1

    services:
      - docker
      - nginx
      - postgresql
      - mediawiki
      - ssl

    dns:
      ttl: 300
      proxied: true

    subdomains:
      - api
      - admin

    ssl:
      enabled: true
      provider: "letsencrypt"
      force_https: true

    features:
      ssl: true
      firewall: true
      backup: true
      monitoring: true

    monitoring:
      enabled: true
      critical: true
      alerts:
        email: "wiki-admin@allthingslinux.org"
```

## 📝 Validation

```bash
# Validate configuration
./scripts/lint.sh domains.yml

# Test configuration
./scripts/deploy-dynamic.sh config
```

This configuration reference provides comprehensive documentation for all available options. Use it to understand and customize your infrastructure configuration.
