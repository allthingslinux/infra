# Ansible Templates

This directory contains all Jinja2 templates used by Ansible playbooks and roles.

## Directory Structure

```
templates/
├── monitoring/                  # Monitoring and observability templates
│   ├── alertmanager/           # AlertManager configurations
│   ├── grafana/                # Grafana configurations
│   ├── prometheus/             # Prometheus configurations
│   ├── alerting-rules.yml.j2   # Alert rules
│   ├── health-check.sh.j2      # Health check scripts
│   ├── loki-config.yml.j2      # Loki configuration
│   ├── promtail-config.yml.j2  # Promtail configuration
│   ├── service-discovery.yml.j2 # Service discovery
│   ├── service-monitoring.yml.j2 # Service monitoring
│   ├── prometheus.yml.j2       # Prometheus main config
│   ├── alertmanager.yml.j2     # AlertManager main config
│   ├── docker-compose.yml.j2   # Monitoring stack compose
│   └── README.md              # Monitoring templates docs
├── services/                    # Service-specific templates
│   ├── atl_services-compose.yml.j2  # ATL Services compose
│   ├── atl_services.env.j2          # ATL Services environment
│   ├── atl_services-monitoring.yml.j2 # ATL Services monitoring
│   ├── atl_tools-compose.yml.j2      # ATL Tools compose
│   ├── atl_tools.env.j2              # ATL Tools environment
│   ├── atl_tools-monitoring.yml.j2   # ATL Tools monitoring
│   ├── atl_chat-compose.yml.j2       # ATL Chat compose
│   ├── atl_chat.env.j2               # ATL Chat environment
│   ├── atl_chat-monitoring.yml.j2    # ATL Chat monitoring
│   ├── atl_dev-compose.yml.j2        # ATL Dev compose
│   ├── atl_dev.env.j2                # ATL Dev environment
│   ├── atl_dev-monitoring.yml.j2     # ATL Dev monitoring
│   ├── atl_wiki-compose.yml.j2       # ATL Wiki compose
│   ├── atl_wiki.env.j2               # ATL Wiki environment
│   └── atl_wiki-monitoring.yml.j2    # ATL Wiki monitoring
├── infrastructure/              # Infrastructure templates
│   ├── jail.local.j2           # Fail2ban configuration
│   ├── audit_rules.j2          # Audit rules
│   ├── emergency_access.sh.j2   # Emergency access script
│   ├── 50unattended-upgrades.j2 # Unattended upgrades
│   ├── alert-rules.yml.j2      # Infrastructure alerts
│   ├── borgmatic-config.yaml.j2 # Backup configuration
│   ├── database-cluster-compose.yml.j2 # Database cluster
│   ├── database-cluster.env.j2  # Database environment
│   └── monitoring-compose.yml.j2 # Infrastructure monitoring
└── README.md                   # This file
```

## Template Categories

### Monitoring Templates

All monitoring and observability related templates:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notification
- **Loki**: Log aggregation
- **Promtail**: Log shipping
- **Health Checks**: Service health monitoring

### Service Templates

Templates for application services:

- **ATL Services**: Core infrastructure services (nginx-proxy-manager, authentik, etc.)
- **ATL Tools**: Application services (nextcloud, gitea, vaultwarden, etc.)
- **ATL Chat**: Communication services (prosody, ergo-irc, etc.)
- **ATL Dev**: Development environment (code-server, ssh-server, etc.)
- **ATL Wiki**: Documentation platform (mediawiki, elasticsearch, etc.)

### Infrastructure Templates

Templates for infrastructure components:

- **Security**: Fail2ban, audit rules, emergency access
- **Backup**: Borgmatic configuration
- **Database**: Database cluster configurations
- **System**: Unattended upgrades, monitoring
- **Network**: Firewall, routing configurations

## Usage

### In Playbooks

```yaml
- name: Deploy monitoring configuration
  template:
    src: monitoring/prometheus.yml.j2
    dest: /etc/prometheus/prometheus.yml
```

### In Roles

```yaml
- name: Configure service
  template:
    src: "{{ role_path }}/templates/service.conf.j2"
    dest: /etc/service/service.conf
```

## Template Organization

- **Consolidated Location**: All templates are now in one place
- **Categorized**: Templates organized by function (monitoring, services, infrastructure)
- **No Duplication**: Single source for each template type
- **Clear Separation**: Role templates stay in roles, shared templates here
- **No Scattered Templates**: All playbook templates moved to main templates directory

## Notes

- **Role Templates**: Stay in `ansible/roles/*/templates/` for role-specific templates
- **Shared Templates**: Use this directory for templates shared across multiple playbooks
- **Consistent Naming**: All templates use `.j2` extension
- **Documentation**: Each template category has its own README
- **Consolidated**: No more templates scattered across playbook directories
