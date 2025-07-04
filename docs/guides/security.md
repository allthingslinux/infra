# Security Operations Guide

This guide covers security best practices, hardening procedures, monitoring, and incident response for the All Things Linux infrastructure.

## 🔒 Security Overview

Our security approach follows **defense in depth** principles with multiple layers of protection:

- **Infrastructure Security**: Server hardening, network isolation
- **Application Security**: Secure configurations, input validation
- **Data Security**: Encryption, backup protection
- **Access Control**: SSH keys, role-based permissions
- **Monitoring**: Real-time threat detection, log analysis

## 🛡️ Infrastructure Hardening

### Automated Security Hardening

Our Ansible roles automatically apply security hardening:

```bash
# Deploy security hardening to all servers
./scripts/deploy-dynamic.sh all --tags security

# Apply hardening to specific domains
./scripts/deploy-dynamic.sh domain atl_wiki --tags hardening

# Run security-only deployment
./scripts/deploy-dynamic.sh all --tags firewall,ssh,ssl
```

### SSH Security

#### SSH Configuration

Automatically configured through Ansible:

```yaml
# In roles/system/tasks/subtasks/ssh.yml
ssh_config:
  PermitRootLogin: "yes"              # Required for automation
  PasswordAuthentication: "no"        # Key-only authentication
  PubkeyAuthentication: "yes"         # Enable key authentication
  Protocol: "2"                       # SSH protocol 2 only
  MaxAuthTries: 3                     # Limit authentication attempts
  ClientAliveInterval: 300            # Keep-alive for long sessions
  ClientAliveCountMax: 2              # Maximum keep-alive probes
```

#### SSH Key Management

```bash
# Generate secure SSH keys
ssh-keygen -t ed25519 -a 100 -f ~/.ssh/atl_infrastructure

# Add keys to servers (automated in deployment)
ansible all -i inventories/dynamic.py \
  -m authorized_key \
  -a "user=root key='{{ lookup('file', '~/.ssh/atl_infrastructure.pub') }}'"

# Rotate SSH keys
./scripts/deploy-dynamic.sh all --tags ssh_keys

# Audit SSH access
ansible all -i inventories/dynamic.py -a "last -20"
```

### Firewall Configuration

#### Automated Firewall Rules

```yaml
# In domains.yml - custom firewall rules
domains:
  atl_web:
    firewall:
      rules:
        - port: 80
          source: "0.0.0.0/0"         # Public HTTP
        - port: 443
          source: "0.0.0.0/0"         # Public HTTPS
        - port: 22
          source: "203.0.113.0/24"    # SSH from office
        - port: 5432
          source: "172.20.0.0/16"     # Database internal only
```

#### Manual Firewall Management

```bash
# Check current firewall status
ansible all -i inventories/dynamic.py -a "ufw status verbose"

# Apply firewall rules
./scripts/deploy-dynamic.sh all --tags firewall

# Test firewall connectivity
ansible web_servers -i inventories/dynamic.py \
  -a "nc -zv localhost 80"
```

### SSL/TLS Security

#### Certificate Management

```yaml
# SSL configuration in domains.yml
domains:
  atl_services:
    ssl:
      enabled: true
      certificate_type: "letsencrypt"   # Or "custom"
      force_https: true                 # Redirect HTTP to HTTPS
      hsts: true                        # HTTP Strict Transport Security
      ocsp_stapling: true               # OCSP stapling
```

#### SSL Deployment and Monitoring

```bash
# Deploy SSL certificates
./scripts/deploy-dynamic.sh all --tags ssl

# Check certificate status
ansible web_servers -i inventories/dynamic.py \
  -a "certbot certificates"

# Test SSL configuration
openssl s_client -connect atl.wiki:443 -servername atl.wiki

# Check certificate expiration
ansible web_servers -i inventories/dynamic.py \
  -a "openssl x509 -in /etc/ssl/certs/atl.wiki.crt -noout -dates"
```

## 🔐 Access Control

### User Management

#### Staff Access Configuration

```yaml
# In group_vars/staff.yml
staff_users:
  - username: admin
    ssh_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5..."
    sudo: true
    groups:
      - sudo
      - docker

  - username: developer
    ssh_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5..."
    sudo: false
    groups:
      - docker
```

#### Deploy Staff Access

```bash
# Deploy staff configurations
./scripts/deploy-dynamic.sh all --tags users

# Add new staff member
# 1. Edit group_vars/staff.yml
# 2. Deploy changes
./scripts/deploy-dynamic.sh all --tags users

# Remove staff access
# 1. Remove from group_vars/staff.yml
# 2. Deploy changes (automatically removes access)
./scripts/deploy-dynamic.sh all --tags users
```

### Role-Based Access

#### Service-Specific Access

```yaml
# Grant access to specific services only
domains:
  atl_database:
    access_groups:
      - database_admins
      - backup_operators
    restricted: true              # No general admin access

  atl_wiki:
    access_groups:
      - wiki_editors
      - content_moderators
    public_access: true           # Public read access
```

#### Sudo Privileges

```bash
# Check sudo access
ansible all -i inventories/dynamic.py -a "sudo -l"

# Audit sudo usage
ansible all -i inventories/dynamic.py \
  -a "grep sudo /var/log/auth.log | tail -20"
```

## 📊 Security Monitoring

### Automated Monitoring

#### Security Monitoring Configuration

```yaml
# In domains.yml - enable security monitoring
domains:
  production_services:
    monitoring:
      security:
        enabled: true
        failed_logins: true          # Monitor failed SSH attempts
        privilege_escalation: true   # Monitor sudo usage
        file_integrity: true         # Monitor critical file changes
        network_connections: true    # Monitor network activity
      alerts:
        email: "security@allthingslinux.org"
        slack: "#security-alerts"
```

#### Deploy Security Monitoring

```bash
# Deploy monitoring stack
./scripts/deploy-dynamic.sh all --tags monitoring,security

# Check monitoring status
ansible all -i inventories/dynamic.py \
  -a "systemctl status fail2ban"

# View security logs
ansible all -i inventories/dynamic.py \
  -a "tail -f /var/log/auth.log"
```

### Log Analysis

#### Centralized Logging

```bash
# Check system logs
ansible all -i inventories/dynamic.py \
  -a "journalctl -n 50 --no-pager"

# Monitor failed login attempts
ansible all -i inventories/dynamic.py \
  -a "grep 'Failed password' /var/log/auth.log | tail -10"

# Check for privilege escalation
ansible all -i inventories/dynamic.py \
  -a "grep 'sudo:' /var/log/auth.log | tail -10"

# Monitor network connections
ansible all -i inventories/dynamic.py \
  -a "netstat -tuln"
```

#### Security Scanning

```bash
# Run security scans
./scripts/deploy-dynamic.sh all --tags security_scan

# Check for vulnerabilities
ansible all -i inventories/dynamic.py \
  -a "apt list --upgradable"

# Scan for malware (if enabled)
ansible all -i inventories/dynamic.py \
  -a "clamscan -r /home /var/www"
```

## 🚨 Incident Response

### Immediate Response Procedures

#### Security Incident Detection

```bash
# Check for active threats
ansible all -i inventories/dynamic.py \
  -a "ps aux | grep -E '(nc|netcat|nmap|curl|wget)'"

# Monitor active connections
ansible all -i inventories/dynamic.py \
  -a "ss -tuln | grep ESTABLISHED"

# Check for unauthorized users
ansible all -i inventories/dynamic.py \
  -a "who"
```

#### Immediate Containment

```bash
# Isolate compromised server
ansible compromised_server -i inventories/dynamic.py \
  -a "ufw deny in && ufw deny out"

# Disable user accounts if needed
ansible all -i inventories/dynamic.py \
  -a "usermod -L suspicious_user"

# Stop suspicious services
ansible all -i inventories/dynamic.py \
  -a "systemctl stop suspicious_service"
```

### Investigation Procedures

#### Evidence Collection

```bash
# Collect system information
ansible affected_servers -i inventories/dynamic.py \
  -a "uname -a; uptime; last -20" > incident_$(date +%Y%m%d)_sysinfo.log

# Collect process information
ansible affected_servers -i inventories/dynamic.py \
  -a "ps auxwww" > incident_$(date +%Y%m%d)_processes.log

# Collect network information
ansible affected_servers -i inventories/dynamic.py \
  -a "netstat -tuln; ss -tuln" > incident_$(date +%Y%m%d)_network.log

# Collect log files
ansible affected_servers -i inventories/dynamic.py \
  -m fetch -a "src=/var/log/auth.log dest=./incident_logs/"
```

#### Forensic Analysis

```bash
# Check file modifications
ansible all -i inventories/dynamic.py \
  -a "find /etc /var/www -type f -mtime -1"

# Check for new files
ansible all -i inventories/dynamic.py \
  -a "find / -type f -newer /etc/passwd 2>/dev/null"

# Analyze login patterns
ansible all -i inventories/dynamic.py \
  -a "grep 'sshd' /var/log/auth.log | grep 'Accepted'"
```

### Recovery Procedures

#### System Recovery

```bash
# Rebuild compromised servers
./scripts/deploy-dynamic.sh infrastructure apply --target compromised_servers

# Restore from clean backup
ansible compromised_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/restore.sh clean_backup_date"

# Redeploy all configurations
./scripts/deploy-dynamic.sh all --limit compromised_servers

# Verify system integrity
./scripts/deploy-dynamic.sh all --tags security,verification
```

#### Access Review

```bash
# Rotate all SSH keys
ssh-keygen -t ed25519 -f ~/.ssh/atl_infrastructure_new
./scripts/deploy-dynamic.sh all --tags ssh_keys --extra-vars "ssh_key_file=~/.ssh/atl_infrastructure_new.pub"

# Review and update staff access
# Edit group_vars/staff.yml
./scripts/deploy-dynamic.sh all --tags users

# Change all service passwords
ansible-vault edit group_vars/all.yml
./scripts/deploy-dynamic.sh all --tags passwords
```

## 🔍 Security Auditing

### Regular Security Audits

#### Automated Security Checks

```bash
# Run comprehensive security audit
./scripts/deploy-dynamic.sh all --tags security_audit

# Check for configuration drift
ansible all -i inventories/dynamic.py \
  -a "lynis audit system"

# Verify file integrity
ansible all -i inventories/dynamic.py \
  -a "aide --check"
```

#### Manual Security Review

```bash
# Review user accounts
ansible all -i inventories/dynamic.py \
  -a "cat /etc/passwd | grep -v nologin"

# Check sudo configuration
ansible all -i inventories/dynamic.py \
  -a "cat /etc/sudoers.d/*"

# Review cron jobs
ansible all -i inventories/dynamic.py \
  -a "crontab -l; cat /etc/cron.d/*"

# Check services
ansible all -i inventories/dynamic.py \
  -a "systemctl list-units --type=service --state=running"
```

### Compliance Monitoring

#### Security Compliance

```yaml
# Compliance configuration
security_compliance:
  standards:
    - CIS                           # CIS Benchmarks
    - NIST                          # NIST Cybersecurity Framework
  automated_checks: true
  reporting:
    frequency: "weekly"
    recipients:
      - "security@allthingslinux.org"
```

#### Compliance Reporting

```bash
# Generate compliance report
./scripts/deploy-dynamic.sh all --tags compliance_report

# Export security metrics
ansible all -i inventories/dynamic.py \
  -a "/opt/atl/scripts/security_metrics.sh" > security_report_$(date +%Y%m%d).json
```

## 🔄 Security Maintenance

### Regular Security Tasks

#### Weekly Security Tasks

```bash
# Update security patches
ansible all -i inventories/dynamic.py \
  -a "apt update && apt upgrade -y"

# Rotate log files
ansible all -i inventories/dynamic.py \
  -a "logrotate -f /etc/logrotate.conf"

# Review security logs
ansible all -i inventories/dynamic.py \
  -a "grep -i 'failed\|error\|denied' /var/log/auth.log | tail -50"
```

#### Monthly Security Tasks

```bash
# Full security hardening review
./scripts/deploy-dynamic.sh all --tags security

# Certificate renewal check
ansible web_servers -i inventories/dynamic.py \
  -a "certbot renew --dry-run"

# Security backup verification
ansible backup_servers -i inventories/dynamic.py \
  -a "/opt/atl/scripts/verify_backup_integrity.sh"
```

### Security Configuration Updates

#### Security Policy Updates

```yaml
# Update security policies in domains.yml
domains:
  all_services:
    security:
      password_policy:
        min_length: 12
        require_special: true
        require_numbers: true
      session_timeout: 3600
      failed_login_limit: 5
      lockout_duration: 900
```

#### Deploy Security Updates

```bash
# Apply security configuration changes
./scripts/deploy-dynamic.sh all --tags security

# Verify security settings
ansible all -i inventories/dynamic.py \
  -a "grep -E '(PasswordAuth|PubkeyAuth|PermitRoot)' /etc/ssh/sshd_config"
```

## 📋 Security Checklist

### Daily Security Checks

- [ ] Monitor failed login attempts
- [ ] Check system resource usage
- [ ] Review active connections
- [ ] Verify backup completion
- [ ] Check certificate status

### Weekly Security Tasks

- [ ] Apply security updates
- [ ] Review access logs
- [ ] Audit user accounts
- [ ] Test incident response procedures
- [ ] Update threat intelligence

### Monthly Security Reviews

- [ ] Comprehensive security audit
- [ ] Update security documentation
- [ ] Review and test backup restoration
- [ ] Security training and awareness
- [ ] Compliance reporting

## 📚 Security Resources

### Internal Resources

- [Configuration Reference](../reference/configuration.md) - Security settings
- [Troubleshooting Guide](../reference/troubleshooting.md) - Security issues
- [Development Guide](development.md) - Secure development practices

### External Resources

- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Security Guidelines](https://owasp.org/)
- [Linux Security Hardening](https://linux-audit.com/)

## 🚨 Emergency Contacts

### Security Team Contacts

- **Security Lead**: <security@allthingslinux.org>
- **Emergency Hotline**: [Emergency contact information]
- **Incident Response Team**: <incident@allthingslinux.org>
- **Slack Channel**: #security-alerts

### Escalation Procedures

1. **Level 1**: Minor security issues - Team lead
2. **Level 2**: Moderate threats - Security team
3. **Level 3**: Major incidents - All hands, external support
4. **Level 4**: Critical compromise - Emergency response, law enforcement

Remember: **Security is everyone's responsibility**. Report suspicious activity immediately and follow established procedures.
