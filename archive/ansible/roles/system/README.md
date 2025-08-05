# System Role

Base system configuration and `/etc` management for All Things Linux infrastructure.

## Description

This role handles fundamental system-level configuration that should be applied to all servers before any application-specific setup. It manages core system files, packages, and settings that form the foundation of a properly configured Linux server.

## Features

- ✅ **Package Management**: Install essential system packages
- ✅ **Hostname & Network**: Configure hostname and `/etc/hosts`
- ✅ **Timezone**: Set system timezone and time synchronization
- ✅ **Locale**: Configure system language and locale settings
- ✅ **SSH Security**: Harden SSH daemon configuration
- ✅ **Kernel Parameters**: Optimize kernel settings via sysctl
- ✅ **Environment Variables**: Set system-wide environment variables
- ✅ **Cron Jobs**: Manage system-level scheduled tasks
- ✅ **Log Rotation**: Configure custom log rotation rules

## Variables

### Required Variables

None - all variables have sensible defaults.

### Optional Variables

```yaml
# System packages to install
system_packages:
  - curl
  - wget
  - git
  - vim

# Timezone configuration
system_timezone: "UTC"

# Locale settings
system_locale: "en_US.UTF-8"
system_language: "en_US:en"

# SSH security settings
system_ssh_port: 22
system_ssh_permit_root_login: false
system_ssh_password_authentication: false
system_ssh_max_auth_tries: 3

# Kernel parameters
system_sysctl_config:
  vm.swappiness: 10
  net.ipv4.ip_forward: 0

# Environment variables
system_environment_vars:
  EDITOR: "vim"
  PAGER: "less"

# Cron jobs
system_cron_jobs:
  - name: "System cleanup"
    minute: "0"
    hour: "2"
    job: "/usr/local/bin/cleanup.sh"
    user: "root"
```

## Usage

### Basic Usage

```yaml
- hosts: all
  roles:
    - system
```

### With Custom Variables

```yaml
- hosts: all
  roles:
    - role: system
      vars:
        system_timezone: "America/New_York"
        system_packages:
          - curl
          - git
          - htop
          - custom-package
```

### With Tags

```yaml
# Install packages only
ansible-playbook playbooks/dynamic-deploy.yml --tags packages

# Configure SSH only
ansible-playbook playbooks/dynamic-deploy.yml --tags ssh

# Skip cron configuration
ansible-playbook playbooks/dynamic-deploy.yml --skip-tags cron
```

## Tags

- `system` - All system configuration tasks
- `packages` - Package installation and management
- `hostname` - Hostname and hosts file configuration
- `timezone` - Timezone configuration
- `locale` - Locale configuration
- `ssh` - SSH daemon configuration
- `sysctl` - Kernel parameter configuration
- `environment` - Environment variable configuration
- `cron` - Cron job management
- `logrotate` - Log rotation configuration

## Dependencies

- `ansible.posix` collection
- `community.general` collection

## Example Playbook

```yaml
---
- name: Configure base system
  hosts: all
  become: true
  roles:
    - role: system
      vars:
        system_timezone: "{{ organization.timezone }}"
        system_packages: "{{ base_packages + role_packages }}"
        system_ssh_port: "{{ security.ssh.port }}"
        system_sysctl_config:
          vm.swappiness: 10
          net.ipv4.ip_forward: 0
          fs.file-max: 65536
```

## Files Created/Modified

- `/etc/hostname` - System hostname
- `/etc/hosts` - Host resolution
- `/etc/timezone` - System timezone
- `/etc/default/locale` - System locale
- `/etc/ssh/sshd_config` - SSH daemon configuration
- `/etc/sysctl.d/99-atl-custom.conf` - Kernel parameters
- `/etc/environment` - System environment variables
- `/etc/profile.d/atl-environment.sh` - ATL-specific environment
- `/etc/logrotate.d/*` - Custom log rotation rules

## Author

ATL Infrastructure Team

## License

MIT
