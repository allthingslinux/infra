# Cloudflare Integration Guide

This guide explains how to integrate Cloudflare DNS and CDN services with your Terraform + Hetzner Cloud infrastructure.

## Overview

Cloudflare provides:

- **DNS Management**: Authoritative DNS for your domain
- **CDN**: Global content delivery network
- **Security**: DDoS protection, firewall, rate limiting
- **SSL/TLS**: Free SSL certificates and encryption
- **Performance**: Caching, compression, optimization

Your setup manages both Hetzner Cloud infrastructure AND Cloudflare services through Terraform.

## Prerequisites

### 1. Cloudflare Account Setup

1. **Create Cloudflare account**: [Sign up at Cloudflare](https://dash.cloudflare.com/sign-up)
2. **Add your domain**: Follow Cloudflare's domain setup wizard
3. **Update nameservers**: Point your domain to Cloudflare nameservers
4. **Verify DNS**: Ensure your domain is active in Cloudflare

### 2. API Token Creation

1. Go to [Cloudflare API Tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click "Create Token"
3. Use "Custom token" with these permissions:
   - **Zone**: `Zone:Read` (for all zones)
   - **Zone**: `Zone Settings:Edit` (for your domain)
   - **DNS**: `DNS:Edit` (for your domain)
4. Add zone resource: `Include - Zone - yourdomain.com`
5. Copy the token (you won't see it again!)

### 3. Environment Variables

```bash
export CLOUDFLARE_API_TOKEN="your-cloudflare-api-token"
export HCLOUD_TOKEN="your-hetzner-token"
```

## Configuration

### Domain Setup

Update your environment configurations with your domain:

```hcl
# terraform/environments/production/terraform.tfvars
domain_name = "allthingslinux.org"  # Your actual domain
```

### Dynamic DNS Integration

The integration automatically creates DNS records for your services based on the `domains.yml` configuration. Each enabled domain gets:

- Main domain record (e.g., `atl.wiki` → server IP)
- Subdomain records (e.g., `nextcloud.atl.tools` → server IP)
- Environment-specific records for staging (e.g., `staging.atl.wiki`)
- Automatic Cloudflare proxy configuration per domain settings

## DNS Records Created

### Automatic DNS Records

The Terraform configuration automatically creates:

**Server Records** (for each server):

- `web-01.development.allthingslinux.org` → Hetzner server IP
- `app-01.development.allthingslinux.org` → Hetzner server IP
- `db-01.development.allthingslinux.org` → Hetzner server IP

**Environment Subdomains**:

- `development.allthingslinux.org` → Load balancer or first web server
- `staging.allthingslinux.org` → Load balancer or first web server
- `allthingslinux.org` (production only) → Load balancer or primary web server

**Service Subdomains**:

- `wiki.allthingslinux.org` (production)
- `wiki.staging.allthingslinux.org` (staging)
- `wiki.development.allthingslinux.org` (development)

### Environment-Specific Behavior

**Development**:

- All services get `.development` subdomain
- Lower TTL (60s) for faster changes
- No proxying (direct connection)
- Relaxed security settings

**Staging**:

- All services get `.staging` subdomain
- Standard TTL (300s)
- Proxying enabled for most services
- Medium security settings

**Production**:

- Services get main domain (e.g., `wiki.allthingslinux.org`)
- Standard TTL (300s)
- Full proxying and security features
- Strict SSL settings

## Security Features

### SSL/TLS Configuration

**Staging**: `full` - End-to-end encryption with self-signed certificates OK
**Production**: `strict` - End-to-end encryption with valid certificates required

### Firewall Rules

Automatically configured:

- Block high threat score requests
- Challenge suspicious traffic
- Rate limiting for API endpoints

### Security Levels

- **Staging**: `medium` - Balanced security and access
- **Production**: `high` - Maximum security protection

## Performance Features

### Caching

**Static Assets**:

- 24-hour edge cache for CSS, JS, images
- Automatic compression (Brotli, Gzip)
- Minification for HTML, CSS, JS

**API Endpoints**:

- 5-minute cache for API responses (configurable)
- Cache bypass for admin endpoints

### Rate Limiting

Configurable rate limits:

- 100 requests per minute per IP for API endpoints
- Customizable per environment
- Different actions: simulate, challenge, block

## Deployment

### Standard Deployment

```bash
# Set environment variables
export HCLOUD_TOKEN="your-hetzner-token"
export CLOUDFLARE_API_TOKEN="your-cloudflare-token"

# Deploy infrastructure + DNS
./scripts/terraform-deploy.sh -e staging -a apply
```

### Verification

After deployment, verify DNS records:

```bash
# Check DNS propagation
dig staging.atl.wiki
dig @8.8.8.8 staging.atl.tools

# Check Cloudflare proxy status
curl -I https://staging.atl.wiki
```

Look for Cloudflare headers:

- `cf-ray`: Cloudflare request ID
- `cf-cache-status`: Cache status
- `server: cloudflare`: Proxied through Cloudflare

## Advanced Features

### Load Balancing & Health Checks

**Resources:**

- `cloudflare_load_balancer` - Global load balancing with geographic steering
- `cloudflare_load_balancer_pool` - Origin server pools with health checks
- `cloudflare_healthcheck` - Standalone health monitoring

**Benefits:**

- Global traffic distribution
- Automatic failover
- Health-based routing
- Regional steering

### Zero Trust Security

**Resources:**

- `cloudflare_access_application` - Application-level access control
- `cloudflare_access_policy` - Identity-based policies
- `cloudflare_teams_rule` - Network-level filtering

**Benefits:**

- Identity-based access control
- No VPN required
- Granular permissions
- Audit logs

### Edge Computing

**Resources:**

- `cloudflare_worker_script` - Serverless functions at the edge
- `cloudflare_worker_route` - Request routing to workers
- `cloudflare_pages_project` - Static site hosting

**Benefits:**

- Ultra-low latency
- Reduce server load
- A/B testing capabilities
- Custom logic at edge

## Customization

### Adding New Services

1. **Update domains.yml**:

```yaml
domains:
  new_service:
    enabled: true
    domain: "new.allthingslinux.org"
    server:
      type: "cx21"
      location: "ash"
    services:
      - docker
      - nginx
```

2. **Deploy changes**:

```bash
./scripts/terraform-deploy.sh -e staging -a apply
```

### Custom DNS Records

Add manual DNS records in `terraform/cloudflare.tf`:

```hcl
resource "cloudflare_record" "custom_cname" {
  zone_id = data.cloudflare_zone.main.id
  name    = "custom"
  value   = "external-service.com"
  type    = "CNAME"
  proxied = false
}
```

### Page Rules

Customize caching and redirects:

```hcl
resource "cloudflare_page_rule" "redirect_old_urls" {
  zone_id  = data.cloudflare_zone.main.id
  target   = "${var.domain_name}/old-path/*"
  priority = 1

  actions {
    forwarding_url {
      url         = "https://${var.domain_name}/new-path/$1"
      status_code = 301
    }
  }
}
```

## Monitoring

### Cloudflare Analytics

Monitor through Cloudflare dashboard:

- Traffic analytics
- Security events
- Performance metrics
- Cache hit ratio

### Terraform State

Check current DNS configuration:

```bash
cd terraform
terraform show | grep cloudflare_record
terraform output cloudflare
```

## Troubleshooting

### Common Issues

**DNS not updating**:

```bash
# Check zone status
terraform show | grep zone_id

# Force DNS propagation check
dig +trace staging.atl.wiki
```

**SSL errors**:

- Verify SSL mode matches server configuration
- Check certificate validity on origin server
- Ensure proper SSL/TLS settings in Cloudflare

**Proxy issues**:

- Verify proxy status (orange vs gray cloud)
- Check if service supports proxying
- Review firewall rules and security settings

### Token Issues

**Invalid token**:

```bash
# Test token
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

**Insufficient permissions**:

- Verify token has correct permissions
- Check zone access in token configuration

## Best Practices

### Security

1. **Use strict SSL** in production
2. **Enable security features** progressively
3. **Monitor security events** regularly
4. **Keep tokens secure** and rotate regularly

### Performance

1. **Enable caching** for static content
2. **Use compression** (Brotli/Gzip)
3. **Optimize images** through Cloudflare
4. **Monitor cache hit ratios**

### Operations

1. **Test in staging** before production
2. **Use staging** for configuration validation
3. **Monitor DNS changes** during deployments
4. **Keep backups** of DNS configurations

## Cost Considerations

**Cloudflare Free Plan includes**:

- DNS management
- DDoS protection
- SSL certificates
- CDN with global PoPs
- Basic caching and compression

**Paid plans add**:

- Advanced security features
- Better analytics
- Custom page rules
- Priority support

For All Things Linux (non-profit), Cloudflare offers:

- [Cloudflare for Nonprofits](https://www.cloudflare.com/nonprofits/)
- Free Pro and Business plan features

## Resources

- [Cloudflare Terraform Provider Docs](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs)
- [Cloudflare for Good (Nonprofits)](https://www.cloudflare.com/nonprofits/)
- [Cloudflare Learning Center](https://www.cloudflare.com/learning/)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/)
