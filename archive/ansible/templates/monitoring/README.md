# Monitoring Infrastructure

This directory contains monitoring and observability configurations for the All Things Linux infrastructure.

## Directory Structure

```
monitoring/
├── config/                    # Monitoring configuration files
│   ├── prometheus.yml        # Prometheus configuration
│   ├── grafana.yml           # Grafana configuration
│   └── alertmanager.yml      # AlertManager configuration
├── templates/                 # Jinja2 templates for Ansible
│   └── docker-compose.yml.j2 # Docker Compose template
├── grafana/                   # Grafana-specific configurations
│   └── grafana.ini.j2        # Grafana INI configuration
├── prometheus/                # Prometheus-specific configurations
│   └── prometheus.yml.j2     # Prometheus YAML configuration
├── alerting/                  # Alerting rules and configurations
│   └── rules.yml             # Alert rules
└── README.md                 # This file
```

## Integration with Ansible

Monitoring configurations are integrated with Ansible through:

- **group_vars/services/monitoring.yml** - Service-level monitoring variables
- **playbooks/monitoring/** - Monitoring deployment playbooks
- **templates/** - Jinja2 templates for dynamic configuration

## Configuration Sources

1. **Static Configs**: Direct configuration files in `config/`
2. **Templates**: Jinja2 templates in `templates/`
3. **Ansible Variables**: Service-specific variables in group_vars
4. **Dynamic Discovery**: Service discovery through Ansible inventory

## Usage

### Deploy Monitoring Stack

```bash
ansible-playbook -i ansible/inventories/dynamic.py ansible/playbooks/monitoring/deploy-stack.yml
```

### Configure Alerts

```bash
ansible-playbook -i ansible/inventories/dynamic.py ansible/playbooks/monitoring/configure-alerts.yml
```

### Update Monitoring Config

```bash
ansible-playbook -i ansible/inventories/dynamic.py ansible/playbooks/monitoring/update-config.yml
```
