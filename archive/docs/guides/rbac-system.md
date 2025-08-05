# Modern RBAC System

## Overview

The All Things Linux infrastructure uses a modern, principle-based Role-Based Access Control (RBAC) system that follows industry best practices. This system replaces the previous organization-specific roles with a more flexible, scalable approach based on security principles.

## Core Principles

### Security Principles

The RBAC system is built around these fundamental security principles:

- **Least Privilege**: Users get minimum access needed for their role
- **Separation of Duties**: Critical operations require multiple approvals
- **Defense in Depth**: Multiple layers of security controls
- **Time-bound Access**: Access expires automatically
- **Just-in-Time**: Access granted only when needed
- **Zero Trust**: Never trust, always verify

## Role Categories

### Infrastructure Roles

#### Platform Engineer

- **Level**: Senior
- **Principles**: Least Privilege, Defense in Depth
- **Access**: Full infrastructure management
- **Constraints**: MFA required, approval for critical changes
- **Sudo**: Full access

#### Site Reliability Engineer

- **Level**: Senior
- **Principles**: Least Privilege, Time-bound Access
- **Access**: Monitoring, incident response, reliability engineering
- **Constraints**: On-call only, emergency access, 12h time limit
- **Sudo**: Limited (service management only)

#### Cloud Engineer

- **Level**: Mid
- **Principles**: Least Privilege
- **Access**: Cloud infrastructure and automation
- **Constraints**: Environment restricted, approval for production
- **Sudo**: None

### Application Development Roles

#### Senior Developer

- **Level**: Senior
- **Principles**: Least Privilege
- **Access**: Full-stack development with deployment
- **Constraints**: Environment restricted, approval for production
- **Sudo**: None

#### Developer

- **Level**: Mid
- **Principles**: Least Privilege
- **Access**: Application development and testing
- **Constraints**: Environment restricted, read-only production
- **Sudo**: None

#### Frontend Developer

- **Level**: Mid
- **Principles**: Least Privilege
- **Access**: Frontend development and UI deployment
- **Constraints**: Environment restricted, approval for production
- **Sudo**: None

### Operations Roles

#### Operations Manager

- **Level**: Senior
- **Principles**: Separation of Duties
- **Access**: Operations oversight and team management
- **Constraints**: Business hours only, read-only
- **Sudo**: None

#### Support Engineer

- **Level**: Mid
- **Principles**: Least Privilege
- **Access**: Technical support and user assistance
- **Constraints**: Customer data only, no infrastructure access
- **Sudo**: None

### Security Roles

#### Security Engineer

- **Level**: Senior
- **Principles**: Defense in Depth, Zero Trust
- **Access**: Security implementation and monitoring
- **Constraints**: MFA required, approval for critical changes
- **Sudo**: Full access

#### Compliance Analyst

- **Level**: Mid
- **Principles**: Separation of Duties
- **Access**: Compliance monitoring and reporting
- **Constraints**: Read-only, business hours only
- **Sudo**: None

### Business Roles

#### Business Manager

- **Level**: Senior
- **Principles**: Separation of Duties
- **Access**: Business oversight and resource management
- **Constraints**: Business hours only, no technical access
- **Sudo**: None

#### Content Manager

- **Level**: Mid
- **Principles**: Least Privilege
- **Access**: Content and documentation management
- **Constraints**: Content only, approval for sensitive content
- **Sudo**: None

## Access Control Matrix

### Infrastructure Services

| Role | Access Level |
|------|-------------|
| Platform Engineer | Full Access |
| Site Reliability Engineer | Monitor, Respond |
| Cloud Engineer | Deploy, Configure |
| Security Engineer | Audit, Secure |
| Operations Manager | Oversight |
| Business Manager | Reports |

### Application Services

| Role | Access Level |
|------|-------------|
| Platform Engineer | Full Access |
| Senior Developer | Deploy, Manage |
| Developer | Develop, Test |
| Frontend Developer | Deploy Frontend |
| Site Reliability Engineer | Monitor, Rollback |
| Security Engineer | Audit, Secure |

### Database Services

| Role | Access Level |
|------|-------------|
| Platform Engineer | Full Access |
| Senior Developer | Read/Write |
| Developer | Read |
| Site Reliability Engineer | Monitor, Backup |
| Security Engineer | Audit, Secure |

### Monitoring Services

| Role | Access Level |
|------|-------------|
| Platform Engineer | Full Access |
| Site Reliability Engineer | Full Access |
| Operations Manager | Oversight |
| Security Engineer | Audit |
| Compliance Analyst | Compliance |

## Time-based Access Control

### Access Windows

- **Business Hours**: 09:00-17:00
- **On-Call**: 24/7
- **Emergency**: Immediate
- **Temporary**: Max 8h

### Role-specific Constraints

- **Business Manager**: Business hours only
- **Operations Manager**: Business hours only
- **Compliance Analyst**: Business hours only
- **Site Reliability Engineer**: 24/7 with logging

## Approval Workflows

### Production Deployment

- **Required Approvers**: Platform Engineer, Site Reliability Engineer
- **Max Approval Time**: 2h
- **Emergency Bypass**: Platform Engineer

### Security Changes

- **Required Approvers**: Security Engineer, Platform Engineer
- **Max Approval Time**: 4h
- **Emergency Bypass**: Security Engineer

### Budget Changes

- **Required Approvers**: Business Manager, Operations Manager
- **Max Approval Time**: 24h
- **Emergency Bypass**: Business Manager

## Implementation

### Configuration Files

#### RBAC Configuration (`ansible/group_vars/rbac.yml`)

```yaml
# Core security principles
security_principles:
  least_privilege: "Users get minimum access needed for their role"
  separation_of_duties: "Critical operations require multiple approvals"
  defense_in_depth: "Multiple layers of security controls"
  time_bound_access: "Access expires automatically"
  just_in_time: "Access granted only when needed"
  zero_trust: "Never trust, always verify"

# Role definitions with principles and constraints
infrastructure_roles:
  platform_engineer:
    description: "Full infrastructure management and platform engineering"
    level: "senior"
    principles: ["least_privilege", "defense_in_depth"]
    permissions:
      - infrastructure:full_access
      - security:manage
      - monitoring:full_access
      - deployment:manage
    constraints:
      - mfa_required: true
      - approval_required: ["security:critical"]
      - audit_logging: true
```

#### User Configuration

```yaml
# Example user configuration
rbac_users:
  - username: john_doe
    primary_role: platform_engineer
    additional_roles: []
    ssh_public_key: "{{ vault_ssh_key_john_doe }}"
    ssh_access: ["all"]
    migration_note: "Migrated from administrator role"
    old_role: administrator
```

### Deployment

#### Deploy RBAC System

```bash
# Deploy the new RBAC system
ansible-playbook ansible/playbooks/users/rbac-management.yml

# Check RBAC status
ansible all -i ansible/inventories/dynamic.py -a "id -nG"
```

#### User Management

```bash
# Add new users to RBAC system
# Edit ansible/group_vars/rbac-users.yml to add users
ansible-playbook ansible/playbooks/users/rbac-management.yml

# Remove user access
# Remove user from rbac_users list and redeploy
ansible-playbook ansible/playbooks/users/rbac-management.yml
```

## Monitoring and Compliance

### Audit Logging

- **Login Logging**: All SSH connections
- **Command Logging**: All commands executed
- **File Access Logging**: Critical file access
- **Privilege Escalation**: Sudo usage tracking
- **Retention**: 365 days
- **Automated Alerts**: Security events

### Compliance Reporting

```bash
# Generate compliance report
/usr/local/bin/rbac-compliance-report.sh

# View audit logs
tail -f /var/log/rbac/audit.log
```

### Access Monitoring

```bash
# Check current user access
/usr/local/bin/rbac-audit-access.sh

# Monitor role assignments
grep "rbac-" /etc/group
```

## Best Practices

### Role Assignment

1. **Start with Least Privilege**: Assign minimum access needed
2. **Review Regularly**: Quarterly access reviews
3. **Document Changes**: All role changes must be documented
4. **Test in Development**: Always test new roles in dev first

### Security Controls

1. **MFA for High-Privilege Roles**: Platform Engineer, Security Engineer
2. **Time-bound Access**: Temporary access with automatic expiration
3. **Approval Workflows**: Critical changes require approval
4. **Audit Logging**: Comprehensive logging of all access

### Compliance

1. **Regular Audits**: Monthly access audits
2. **Principle Validation**: Quarterly principle compliance checks
3. **Documentation**: Maintain up-to-date role documentation
4. **Training**: Regular security training for all users

## Troubleshooting

### Common Issues

#### Access Denied

```bash
# Check user roles
id -nG username

# Check SSH configuration
grep "rbac-" /etc/ssh/sshd_config

# Check time-based restrictions
/usr/local/bin/rbac-time-check.sh
```

#### Role Assignment Issues

```bash
# Check user roles
id -nG username

# Verify role assignments
grep -r "rbac_users" ansible/group_vars/rbac-users.yml
```

#### Audit Issues

```bash
# Check audit logs
tail -f /var/log/rbac/audit.log

# Verify audit configuration
grep -r "audit" /etc/rbac/
```

## User Management Guide

### Adding New Users

1. **Create User Configuration**

   ```bash
   # Edit ansible/group_vars/rbac-users.yml
   # Add new user with appropriate role
   ```

2. **Example User Configuration**

   ```yaml
   rbac_users:
     - username: john_doe
       primary_role: platform_engineer
       additional_roles: []
       ssh_public_key: "{{ vault_ssh_key_john_doe }}"
       ssh_access: ["all"]
   ```

3. **Test in Development**

   ```bash
   ansible-playbook ansible/playbooks/users/rbac-management.yml --limit dev
   ```

4. **Deploy to Production**

   ```bash
   ansible-playbook ansible/playbooks/users/rbac-management.yml
   ```

5. **Monitor and Adjust**
   - Monitor access patterns
   - Adjust permissions as needed
   - Update documentation

### Role Assignment Reference

| Role | Description | Access Level |
|------|-------------|-------------|
| platform_engineer | Full infrastructure management | Full Access |
| site_reliability_engineer | Monitoring and reliability | Monitor, Respond |
| cloud_engineer | Cloud infrastructure and automation | Deploy, Configure |
| senior_developer | Full-stack development with deployment | Deploy, Manage |
| developer | Application development and testing | Develop, Test |
| frontend_developer | Frontend development and UI deployment | Deploy Frontend |
| operations_manager | Operations oversight and team management | Oversight |
| support_engineer | Technical support and user assistance | Support |
| security_engineer | Security implementation and monitoring | Audit, Secure |
| compliance_analyst | Compliance monitoring and reporting | Compliance |
| business_manager | Business oversight and resource management | Reports |
| content_manager | Content and documentation management | Content |

## Future Enhancements

### Planned Features

- **Just-in-Time Access**: Temporary access provisioning
- **Attribute-Based Access Control**: Dynamic permissions based on context
- **Integration with Identity Providers**: SSO integration
- **Advanced Analytics**: Access pattern analysis
- **Automated Compliance**: Real-time compliance monitoring

### Continuous Improvement

- **Regular Reviews**: Quarterly principle compliance reviews
- **User Feedback**: Regular user feedback collection
- **Industry Alignment**: Stay current with industry best practices
- **Security Updates**: Regular security principle updates
