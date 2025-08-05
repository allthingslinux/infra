# Minimal User Management System

## Overview

A simple, modern user management system using official Ansible collections and best practices. This system provides basic RBAC functionality without over-engineering.

## Features

- **3 roles**: Senior Sysadmin, Sysadmin, Junior Sysadmin
- **Official collections**: Uses `ansible.builtin`, `ansible.posix`, `community.general`
- **Emergency access**: Simple script for critical situations
- **Audit logging**: Basic security monitoring
- **On-call management**: Clear escalation paths

## Team Structure

### Roles

1. **Senior Sysadmin** (`senior_sysadmin`)
   - Full sudo access
   - Emergency access capability
   - On-call responsibility
   - All server access

2. **Sysadmin** (`sysadmin`)
   - No sudo access (use emergency access when needed)
   - Operational access to application/infrastructure servers
   - Secondary on-call

3. **Junior Sysadmin** (`jr_sysadmin`)
   - Limited access to development/staging servers
   - Monitoring access only
   - Shadow on-call

## Usage

### Setup

```bash
# Install required collections
ansible-galaxy collection install -r ansible/collections/requirements.yml

# Deploy user management
ansible-playbook -i inventories/dynamic.py ansible/playbooks/users/setup-users.yml
```

### Emergency Access

```bash
# Grant emergency access (senior team members only)
sudo emergency_access "Database outage - immediate intervention required"
```

### Adding Users

Edit `ansible/group_vars/users.yml`:

```yaml
team_members:
  - username: new_user
    role: sysadmin
    sudo: false
    on_call: false
    ssh_keys:
      - "{{ vault_ssh_key_new_user }}"
    groups:
      - systems_team
    projects: ["monitoring"]
```

Then redeploy:

```bash
ansible-playbook -i inventories/dynamic.py ansible/playbooks/users/setup-users.yml
```

## Security

### SSH Keys

- Uses `ansible.posix.authorized_key` for key management
- Exclusive key deployment (replaces all keys)
- 90-day rotation recommended

### Sudo Access

- Only senior team members have sudo
- Emergency access available for critical situations
- All sudo usage is audited

### Audit Logging

- Monitors sudo changes
- Tracks emergency access
- Logs user management activities

## Collections Used

### `ansible.builtin`

- `user`: User account management
- `group`: Group management
- `lineinfile`: Sudo configuration
- `file`: Directory and file management
- `template`: Configuration file generation
- `service`: Service management

### `ansible.posix`

- `authorized_key`: SSH key management

### `community.general`

- Additional utilities for advanced use cases

## File Structure

```
ansible/
├── group_vars/
│   └── users.yml              # User definitions
├── playbooks/
│   └── users/
│       ├── setup-users.yml    # Main playbook
│       └── templates/
│           ├── emergency_access.sh.j2
│           └── audit_rules.j2
└── collections/
    └── requirements.yml       # Collection requirements
```

## Benefits

### Simplicity

- Only 3 roles instead of complex hierarchies
- Uses official Ansible collections
- Easy to understand and maintain

### Security

- Principle of least privilege
- Emergency access for critical situations
- Comprehensive audit logging

### Maintainability

- Standard Ansible patterns
- Official collections ensure compatibility
- Clear documentation and examples

## Comparison with Complex Systems

| Aspect | Complex RBAC | Minimal System |
|--------|-------------|----------------|
| Roles | 15+ roles | 3 roles |
| Collections | Custom/unofficial | Official only |
| Maintenance | High overhead | Low overhead |
| Learning curve | Steep | Gentle |
| Emergency access | Complex approval | Simple script |

This minimal approach focuses on what actually matters for a systems team: clear roles, practical access, emergency procedures, and maintainability.
