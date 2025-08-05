# Ansible Group Variables Structure

This directory follows a **Service-Based Hybrid Approach** for organizing Ansible variables.

## Directory Structure

```
group_vars/
├── all.yml                           # Global variables for all hosts
├── domains_config.yml                # Centralized domains.yml loader
├── environments/                     # Environment-specific variables
│   └── production.yml               # Production environment overrides
├── services/                        # Service group variables
│   ├── core.yml                     # Core infrastructure services
│   ├── apps.yml                     # Application services
│   ├── monitoring.yml               # Monitoring services
│   ├── infrastructure.yml           # Infrastructure services
│   ├── user_roles.yml              # User role definitions
│   └── users.yml                   # User management system
└── domains/                         # Domain-specific variables
    ├── atl_services.yml            # atl.services domain
    ├── atl_tools.yml               # atl.tools domain
    ├── atl_chat.yml                # atl.chat domain
    └── atl_dev.yml                 # atl.dev domain
```

## Variable Precedence

1. **host_vars** (highest priority)
2. **domains/** (domain-specific overrides)
3. **services/** (service group variables)
4. **environments/** (environment-specific variables)
5. **all.yml** (global variables)

## File Descriptions

### Root Level

- **all.yml**: Global Ansible variables that apply to all hosts
- **domains_config.yml**: Loader for centralized domains.yml configuration

### Environments

- **environments/production.yml**: Production environment overrides

### Services

- **services/core.yml**: Core infrastructure services (atl_services)
- **services/apps.yml**: Application services (atl_tools, atl_chat, atl_wiki)
- **services/monitoring.yml**: Monitoring and observability services
- **services/infrastructure.yml**: Infrastructure services (docker, nginx, postfix, dns)
- **services/user_roles.yml**: User role definitions and access levels
- **services/users.yml**: User management system and team members

### Domains

- **domains/atl_services.yml**: atl.services domain configuration
- **domains/atl_tools.yml**: atl.tools domain configuration
- **domains/atl_chat.yml**: atl.chat domain configuration
- **domains/atl_dev.yml**: atl.dev domain configuration

## Integration with Existing Systems

- Server specifications come from `domains.yml` → Terraform → dynamic inventory
- This structure provides Ansible-specific configurations that work with the existing infrastructure
- Domain files complement but don't duplicate the domains.yml configuration
