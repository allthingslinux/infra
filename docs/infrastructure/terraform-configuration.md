# Terraform Configuration

## Overview

This document explains the proper Terraform directory structure and configuration to prevent scattered `.terraform` directories and ensure efficient plugin caching.

## Directory Structure

### 🎯 **Root Modules** (Where you run `terraform init`)

```text
terraform/
├── main.tf                           # Main terraform root
├── variables.tf
├── outputs.tf
└── environments/
    ├── development/                  # Development environment root
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── staging/                      # Staging environment root
    │   └── ...
    └── production/                   # Production environment root
        └── ...
```

### 🚫 **Modules** (Reusable components - NEVER run `terraform init` here)

```text
terraform/modules/
├── compute/                          # Reusable compute module
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── network/                          # Reusable network module
│   └── ...
└── security/                        # Reusable security module
    └── ...
```

## Plugin Caching Configuration

### Project-Specific Configuration

Terraform is configured to use a project-local plugin cache directory via `.terraformrc`:

```hcl
# Project-specific Terraform CLI Configuration
plugin_cache_dir = ".terraform-cache"
```

This configuration is automatically used by the `atl deploy` command via the `TF_CLI_CONFIG_FILE` environment variable.

### Benefits

1. **Prevents scattered `.terraform` directories** in modules
2. **Faster initialization** - plugins are downloaded once and reused
3. **Saves disk space** - no duplicate plugin downloads
4. **Cleaner repository** - no `.terraform` directories in modules

### How It Works

1. **First `terraform init`** - Downloads plugins to cache directory
2. **Subsequent `terraform init`** - Uses cached plugins (much faster)
3. **Module directories** - Never get `.terraform` directories
4. **Root directories** - Get `.terraform` directories with symlinks to cache

## Usage Guidelines

### ✅ **Correct Usage with ATL CLI**

```bash
# Use the integrated CLI (recommended)
atl deploy plan -e development
atl deploy apply -e development

# Direct terraform usage (if needed)
cd terraform/environments/development/
terraform init
terraform plan
terraform apply
```

### ❌ **Incorrect Usage**

```bash
# NEVER do this - modules are reusable components, not root modules
cd terraform/modules/compute/
terraform init  # ❌ This will create unnecessary .terraform directories
```

## Troubleshooting

### Cleaning Up Existing `.terraform` Directories

If you have existing `.terraform` directories in modules, clean them up:

```bash
# Remove .terraform directories from modules
find terraform/modules -name ".terraform" -type d -exec rm -rf {} +

# Reinitialize from proper root directories
cd terraform/environments/development/
terraform init
```

### Verifying Plugin Cache

Check that the plugin cache is working:

```bash
# Check project-local cache directory
ls -la .terraform-cache/

# Run deployment and verify it uses cache
atl deploy plan -e development --terraform-only
```

### Cache Directory Location

The project-specific plugin cache directory is located at:

- **Project root**: `.terraform-cache/` (excluded from git via .gitignore)
- **Benefits**: Project isolation, team consistency, no global pollution

## Best Practices

1. **Use the ATL CLI** - Prefer `atl deploy` over direct terraform commands
2. **Only initialize root modules** - Never run `terraform init` in modules
3. **Use project-specific caching** - `.terraformrc` is automatically configured
4. **Clean up periodically** - Remove old cached plugins from `.terraform-cache/`
5. **Document structure** - Make it clear which directories are roots vs modules
6. **Use version constraints** - Pin provider versions in your configurations

## Related Documentation

- [Terraform CLI Configuration](https://developer.hashicorp.com/terraform/cli/config/config-file)
- [Plugin Cache](https://developer.hashicorp.com/terraform/cli/config/config-file#plugin-cache)
- [Terraform Modules](https://developer.hashicorp.com/terraform/language/modules)
