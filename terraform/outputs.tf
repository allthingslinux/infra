output "servers" {
  description = "Server information for Ansible inventory"
  value = merge(
    {
      for k, v in hcloud_server.domains : k => {
        id          = v.id
        name        = v.name
        public_ip   = v.ipv4_address
        private_ip  = v.network[0].ip
        server_type = v.server_type
        location    = v.location
        labels      = v.labels
        type        = "domain"
      }
    },
    {
      for k, v in hcloud_server.shared : k => {
        id          = v.id
        name        = v.name
        public_ip   = v.ipv4_address
        private_ip  = v.network[0].ip
        server_type = v.server_type
        location    = v.location
        labels      = v.labels
        type        = "shared"
      }
    }
  )
}

output "network" {
  description = "Network information"
  value = {
    id       = hcloud_network.main.id
    name     = hcloud_network.main.name
    ip_range = hcloud_network.main.ip_range
  }
}

output "ssh_key" {
  description = "SSH key information"
  value = {
    id   = hcloud_ssh_key.default.id
    name = hcloud_ssh_key.default.name
  }
}

output "firewall" {
  description = "Firewall information"
  value = {
    id   = hcloud_firewall.main.id
    name = hcloud_firewall.main.name
  }
}

output "load_balancer" {
  description = "Load balancer information"
  value = var.load_balancer_enabled ? {
    id         = hcloud_load_balancer.main[0].id
    name       = hcloud_load_balancer.main[0].name
    public_ip  = hcloud_load_balancer.main[0].ipv4
    private_ip = hcloud_load_balancer_network.main[0].ip
  } : null
}

output "cloudflare" {
  description = "Cloudflare configuration information"
  value = {
    domains = {
      for domain_key in keys(local.enabled_domains) : domain_key => {
        domain = local.enabled_domains[domain_key].domain
        zones  = try(cloudflare_zone.domains[local.enabled_domains[domain_key].domain].id, null)
      }
    }
    dns_records = merge(
      try({
        for k, v in cloudflare_dns_record.domain_main : k => {
          name    = v.name
          value   = v.content
          fqdn    = v.hostname
          proxied = v.proxied
        }
      }, {}),
      try({
        for k, v in cloudflare_dns_record.domain_subdomains : k => {
          name    = v.name
          value   = v.content
          fqdn    = v.hostname
          proxied = v.proxied
        }
      }, {})
    )
  }
  sensitive = false
}

# Output dynamic inventory for Ansible
output "ansible_inventory" {
  description = "Dynamically generated Ansible inventory from domains.yml"
  value = {
    all = {
      children = merge(
        # Domain groups
        {
          for name, config in local.enabled_domains : name => {
            hosts = {
              "${local.global.project_name}-${name}-${local.global.environment}" = {
                ansible_host = hcloud_server.domains[name].ipv4_address
                ansible_user = local.global.default_user
                private_ip   = hcloud_server.domains[name].network[0].ip
                domain       = config.domain
                server_role  = name
                services     = config.services
                subdomains   = lookup(config, "subdomains", [])
                monitoring   = lookup(config, "monitoring", {})
                features     = lookup(config, "features", {})
              }
            }
          }
        },
        # Shared infrastructure groups
        {
          for name, config in local.enabled_shared : name => {
            hosts = {
              "${local.global.project_name}-${name}-${local.global.environment}" = {
                ansible_host = hcloud_server.shared[name].ipv4_address
                ansible_user = local.global.default_user
                private_ip   = hcloud_server.shared[name].network[0].ip
                server_role  = name
                services     = config.services
                shared       = true
              }
            }
          }
        }
      )
    }
  }
}
