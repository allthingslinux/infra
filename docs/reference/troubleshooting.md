# Troubleshooting Guide

This guide covers common issues and solutions for the All Things Linux infrastructure.

## 🚨 Quick Diagnosis

### Health Check Commands

```bash
# Check overall system status
./scripts/deploy-dynamic.sh config

# Test connectivity
ansible all -i inventories/dynamic.py -m ping

# Check services
ansible all -i inventories/dynamic.py -a "systemctl status docker nginx"

# Check resources
ansible all -i inventories/dynamic.py -a "df -h && free -m"
```

## 🔧 Common Issues

### SSH Connection Problems

**Symptoms:** Connection refused, authentication failures

**Solutions:**

1. **Check SSH keys:**

   ```bash
   ssh-add -l
   ssh-add ~/.ssh/atl_infrastructure
   ./scripts/deploy-dynamic.sh all --tags ssh_keys
   ```

2. **Test connectivity:**

   ```bash
   ssh -vvv root@server-ip
   ping server-ip
   ```

3. **Fix firewall:**

   ```bash
   ./scripts/deploy-dynamic.sh all --tags firewall
   ```

### DNS Resolution Issues

**Symptoms:** Domain not resolving, SSL errors

**Solutions:**

1. **Check DNS:**

   ```bash
   dig domain-name
   nslookup domain-name
   ```

2. **Deploy DNS config:**

   ```bash
   ./scripts/deploy-dynamic.sh infrastructure apply
   ```

3. **Verify Cloudflare:**

   ```bash
   curl -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        https://api.cloudflare.com/client/v4/user/tokens/verify
   ```

### SSL Certificate Problems

**Symptoms:** Certificate errors, HTTPS not working

**Solutions:**

1. **Check certificates:**

   ```bash
   ansible web_servers -i inventories/dynamic.py -a "certbot certificates"
   openssl s_client -connect domain-name:443
   ```

2. **Regenerate certificates:**

   ```bash
   ./scripts/deploy-dynamic.sh domain DOMAIN_NAME --tags ssl
   ansible web_servers -i inventories/dynamic.py -a "certbot renew"
   ```

### Docker Issues

**Symptoms:** Containers not starting, Docker daemon errors

**Solutions:**

1. **Check Docker status:**

   ```bash
   ansible all -i inventories/dynamic.py -a "systemctl status docker"
   ansible all -i inventories/dynamic.py -a "docker ps -a"
   ```

2. **Restart Docker:**

   ```bash
   ansible all -i inventories/dynamic.py -a "systemctl restart docker"
   ./scripts/deploy-dynamic.sh all --tags docker
   ```

3. **Check logs:**

   ```bash
   ansible all -i inventories/dynamic.py -a "docker compose logs --tail=50"
   ```

## 📊 Performance Issues

### High Resource Usage

**Diagnosis:**

```bash
# Check CPU and memory
ansible all -i inventories/dynamic.py -a "top -bn1 | head -20"
ansible all -i inventories/dynamic.py -a "free -h"

# Check disk space
ansible all -i inventories/dynamic.py -a "df -h"

# Find resource-intensive processes
ansible all -i inventories/dynamic.py -a "ps aux --sort=-%cpu | head -10"
```

**Solutions:**

1. **Scale up servers:**

   ```yaml
   # Edit domains.yml
   domains:
     domain_name:
       server:
         type: "cx41"  # Upgrade server type
   ```

2. **Clean up resources:**

   ```bash
   # Clean Docker
   ansible all -i inventories/dynamic.py -a "docker system prune -f"

   # Clean logs
   ansible all -i inventories/dynamic.py -a "journalctl --vacuum-time=7d"
   ```

### Disk Space Issues

**Solutions:**

1. **Free up space:**

   ```bash
   # Clean package cache
   ansible all -i inventories/dynamic.py -a "apt autoremove && apt autoclean"

   # Clean old logs
   ansible all -i inventories/dynamic.py -a "find /var/log -name '*.log.*' -delete"
   ```

2. **Add storage:**

   ```yaml
   # Edit domains.yml
   domains:
     domain_name:
       server:
         volumes:
           - name: "data"
             size: 100
             mount_point: "/data"
   ```

## 🌐 Network Issues

### Port Connectivity

**Diagnosis:**

```bash
# Check listening ports
ansible all -i inventories/dynamic.py -a "netstat -tuln | grep :80"

# Test connectivity
nc -zv server-ip 80

# Check firewall
ansible all -i inventories/dynamic.py -a "ufw status verbose"
```

**Solutions:**

1. **Open ports:**

   ```bash
   ./scripts/deploy-dynamic.sh all --tags firewall
   ansible all -i inventories/dynamic.py -a "ufw allow 80/tcp"
   ```

2. **Restart services:**

   ```bash
   ./scripts/deploy-dynamic.sh all --tags restart
   ansible all -i inventories/dynamic.py -a "systemctl restart nginx"
   ```

## 🔒 Security Issues

### Access Control

**Diagnosis:**

```bash
# Check SSH keys
ssh-add -l

# Check user permissions
ansible all -i inventories/dynamic.py -a "sudo -l"

# Check file permissions
ansible all -i inventories/dynamic.py -a "ls -la /problematic/path"
```

**Solutions:**

1. **Fix SSH keys:**

   ```bash
   ssh-add ~/.ssh/atl_infrastructure
   ./scripts/deploy-dynamic.sh all --tags ssh_keys
   ```

2. **Fix permissions:**

   ```bash
   ./scripts/deploy-dynamic.sh all --tags users
   ansible all -i inventories/dynamic.py -a "chown -R user:group /path"
   ```

## 🛠️ Development Issues

### Linting Failures

**Diagnosis:**

```bash
# Run linting
./scripts/lint.sh --verbose

# Check specific tools
./scripts/lint.sh --ansible-lint
```

**Solutions:**

1. **Auto-fix issues:**

   ```bash
   ./scripts/lint.sh --fix
   ./scripts/setup-hooks.sh --update
   ```

2. **Ignore specific rules:**

   ```bash
   # Add to .ansible-lint-ignore
   echo "filename rule_name # reason" >> .ansible-lint-ignore
   ```

### Pre-commit Hooks

**Solutions:**

1. **Reinstall hooks:**

   ```bash
   ./scripts/setup-hooks.sh --force
   pre-commit install
   ```

2. **Skip hooks temporarily:**

   ```bash
   git commit --no-verify
   ```

## 📋 Emergency Procedures

### Quick Recovery

```bash
# Emergency service restart
ansible all -i inventories/dynamic.py -a "systemctl restart docker nginx"

# Emergency deployment
./scripts/deploy-dynamic.sh all --force

# Quick health check
ansible all -i inventories/dynamic.py -m ping

# Check system status
ansible all -i inventories/dynamic.py -a "systemctl status"
```

### System Recovery

```bash
# Rebuild infrastructure
./scripts/deploy-dynamic.sh infrastructure apply

# Restore from backup
ansible all -i inventories/dynamic.py -a "/opt/atl/scripts/restore.sh"

# Redeploy everything
./scripts/deploy-dynamic.sh all
```

## 🔍 Log Analysis

### Finding Errors

```bash
# System errors
ansible all -i inventories/dynamic.py -a "journalctl -p err --no-pager -n 50"

# Application errors
ansible all -i inventories/dynamic.py -a "grep -i 'error\|failed' /var/log/syslog"

# Service logs
ansible web_servers -i inventories/dynamic.py -a "tail -f /var/log/nginx/error.log"
```

### Common Log Locations

- System logs: `/var/log/syslog`, `journalctl`
- Nginx logs: `/var/log/nginx/`
- Docker logs: `docker compose logs`
- Application logs: `/var/log/applications/`

## 📞 Getting Help

### Information to Gather

1. **Environment info:**

   ```bash
   ./scripts/deploy-dynamic.sh config
   ansible --version
   ```

2. **Error messages:**

   ```bash
   tail -100 logs/deploy-$(date +%Y%m%d).log
   ```

3. **System status:**

   ```bash
   ansible all -i inventories/dynamic.py -a "uptime && df -h"
   ```

### Emergency Contacts

- **Team Chat**: #infrastructure
- **Email**: <infrastructure@allthingslinux.org>
- **Emergency**: Follow on-call procedures

### Before Asking for Help

1. Check this troubleshooting guide
2. Review recent changes in git
3. Test in development environment
4. Gather relevant information
5. Try basic fixes first

Remember: When in doubt, ask for help before making changes in production!
