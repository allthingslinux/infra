# Host Variables (host_vars)

This directory contains **host-specific variable overrides** that apply to individual hosts.

## When to Use host_vars

**Most of the time, you DON'T need host_vars.** Use them only for:

### 1. Emergency Overrides

```yaml
# host_vars/web01.yml
emergency_maintenance: true
maintenance_reason: "Database migration in progress"
maintenance_until: "2024-01-15T18:00:00Z"
```

### 2. Host-Specific Configurations

```yaml
# host_vars/db01.yml
database_config:
  max_connections: 2000  # This specific DB needs more connections
  memory_limit: "8GB"    # This server has more RAM
  backup_schedule: "hourly"  # Critical DB needs hourly backups
```

### 3. Hardware-Specific Settings

```yaml
# host_vars/storage01.yml
disk_config:
  raid_level: "raid10"
  ssd_cache: true
  storage_pool: "fast_ssd"
```

### 4. Geographic/Location-Specific

```yaml
# host_vars/us-east-web01.yml
location_config:
  timezone: "America/New_York"
  backup_location: "us-east-1"
  cdn_region: "us-east"
```

### 5. Testing/Development Overrides

```yaml
# host_vars/test-web01.yml
test_config:
  debug_mode: true
  log_level: "DEBUG"
  mock_external_apis: true
```

## Variable Precedence

host_vars have the **highest priority** in Ansible:

1. **host_vars** (highest priority) ← **This directory**
2. **domains/** (domain-specific overrides)
3. **services/** (service group variables)
4. **environments/** (environment-specific variables)
5. **all.yml** (global variables)

## File Naming Convention

Files should be named after the **exact hostname**:

```
host_vars/
├── atl-services-01.yml    # For host: atl-services-01
├── atl-tools-01.yml       # For host: atl-tools-01
├── db01.yml               # For host: db01
└── web01.yml              # For host: web01
```

## Best Practices

### ✅ DO

- Use for **true host-specific** configurations
- Keep files **minimal and focused**
- Document **why** the override is needed
- Use for **emergency situations**

### ❌ DON'T

- Duplicate group_vars configurations
- Use for configurations that apply to multiple hosts
- Put server specifications (use domains.yml + Terraform)
- Use for environment-wide settings

## Example Usage

```yaml
# host_vars/atl-services-01.yml
---
# Emergency maintenance mode
emergency_maintenance: true
maintenance_reason: "SSL certificate renewal"
maintenance_until: "2024-01-15T18:00:00Z"

# Host-specific monitoring
monitoring_config:
  custom_checks:
    - name: "custom_ssl_check"
      command: "check_ssl_cert"
      interval: "5m"

# Override service configuration for this specific host
nginx_config:
  worker_processes: 8  # This host has more CPU cores
  max_connections: 2048
```

## When NOT to Use host_vars

- **Server specifications** → Use `domains.yml` + Terraform
- **Environment settings** → Use `environments/`
- **Service configurations** → Use `services/`
- **Domain configurations** → Use `domains/`
- **Global settings** → Use `all.yml`

## Integration with Your Infrastructure

Your dynamic inventory system already handles host grouping based on `domains.yml`. Only use host_vars when you need to **override** those group-based configurations for specific hosts.

**Rule of thumb**: If you're tempted to create a host_vars file, first ask: "Could this be handled by group_vars instead?"
