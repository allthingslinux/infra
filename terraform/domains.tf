# Dynamic Domain-Based Infrastructure
# This file generates all infrastructure from domains.yml automatically

# Load domain configuration from YAML
locals {
  domains_config = yamldecode(file("${path.root}/../configs/domains.yml"))

  # Extract only enabled domains that aren't external
  enabled_domains = {
    for name, config in local.domains_config.domains : name => config
    if config.enabled == true && !lookup(config, "external", false)
  }

  # Extract enabled shared infrastructure
  enabled_shared = {
    for name, config in local.domains_config.shared_infrastructure : name => config
    if config.enabled == true
  }

  # Global settings
  global = local.domains_config.global
}

# Generate servers dynamically for each enabled domain
resource "hcloud_server" "domains" {
  for_each = local.enabled_domains

  name         = "${local.global.project_name}-${each.key}-${local.global.environment}"
  image        = var.server_image
  server_type  = each.value.server.type
  location     = each.value.server.location
  ssh_keys     = [hcloud_ssh_key.default.id]
  firewall_ids = [hcloud_firewall.main.id]

  labels = {
    project     = local.global.project_name
    environment = local.global.environment
    managed_by  = "terraform"
    domain      = each.value.domain
    role        = each.key
    services    = join(",", each.value.services)
  }

  network {
    network_id = hcloud_network.main.id
    ip         = each.value.network.ip
  }

  user_data = templatefile("${path.module}/templates/cloud-init.yml", {
    hostname       = "${local.global.project_name}-${each.key}-${local.global.environment}"
    ansible_user   = local.global.default_user
    domain         = each.value.domain
    server_role    = each.key
    docker_enabled = true
    services       = each.value.services
  })
}

# Generate shared infrastructure servers dynamically
resource "hcloud_server" "shared" {
  for_each = local.enabled_shared

  name         = "${local.global.project_name}-${each.key}-${local.global.environment}"
  image        = var.server_image
  server_type  = each.value.server.type
  location     = each.value.server.location
  ssh_keys     = [hcloud_ssh_key.default.id]
  firewall_ids = [hcloud_firewall.main.id]

  labels = {
    project     = local.global.project_name
    environment = local.global.environment
    managed_by  = "terraform"
    role        = each.key
    shared      = "true"
    services    = join(",", each.value.services)
  }

  network {
    network_id = hcloud_network.main.id
    ip         = "10.${local.global.environment == "production" ? "0" : "1"}.${length(local.enabled_domains) + index(keys(local.enabled_shared), each.key) + 1}.10"
  }

  user_data = templatefile("${path.module}/templates/cloud-init.yml", {
    hostname       = "${local.global.project_name}-${each.key}-${local.global.environment}"
    ansible_user   = local.global.default_user
    domain         = lookup(each.value, "domain", "${each.key}.${local.global.project_name}.local")
    server_role    = each.key
    docker_enabled = true
    services       = each.value.services
  })
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

# Generate DNS records dynamically
resource "cloudflare_dns_record" "domain_main" {
  for_each = {
    for name, config in local.enabled_domains : name => config
    if config.domain != null
  }

  zone_id = cloudflare_zone.domains[each.value.domain].id
  name    = local.global.environment == "production" ? "@" : local.global.environment
  content = hcloud_server.domains[each.key].ipv4_address
  type    = "A"
  ttl     = var.dns_ttl
  proxied = local.global.cloudflare_proxy

  comment = "${each.key} - ${local.global.environment} - Managed by Terraform"



  tags = [
    "terraform",
    local.global.project_name,
    local.global.environment,
    each.key
  ]
}

# Generate subdomain records dynamically
resource "cloudflare_dns_record" "domain_subdomains" {
  for_each = {
    for pair in flatten([
      for domain_name, config in local.enabled_domains : [
        for subdomain in lookup(config, "subdomains", []) : {
          domain_key = domain_name
          subdomain  = subdomain
          domain     = config.domain
          server_ip  = hcloud_server.domains[domain_name].ipv4_address
        }
      ]
    ]) : "${pair.domain_key}-${pair.subdomain}" => pair
  }

  zone_id = cloudflare_zone.domains[each.value.domain].id
  name    = local.global.environment == "production" ? each.value.subdomain : "${each.value.subdomain}.${local.global.environment}"
  content = each.value.server_ip
  type    = "A"
  ttl     = var.dns_ttl
  proxied = each.value.subdomain != "mail" ? local.global.cloudflare_proxy : false

  comment = "${each.value.domain_key} ${each.value.subdomain} - Managed by Terraform"

  tags = [
    "terraform",
    local.global.project_name,
    local.global.environment,
    each.value.domain_key,
    each.value.subdomain
  ]
}

# Manage zones as resources (import existing zones)
resource "cloudflare_zone" "domains" {
  for_each = toset([
    for name, config in local.enabled_domains : config.domain
    if config.domain != null
  ])

  name = each.value
  account = {
    id = var.cloudflare_account_id
  }
  type   = "full" # Required: full or partial
  paused = false  # Optional: Zone pausing
}

# Page rules for API caching (applied to domains that have API services)
resource "cloudflare_page_rule" "api_cache" {
  for_each = var.enable_api_caching ? {
    for name, config in local.enabled_domains : name => config
    if config.domain != null && contains(lookup(config, "services", []), "api")
  } : {}

  zone_id  = cloudflare_zone.domains[each.value.domain].id
  target   = "${local.global.environment == "production" ? "" : "${local.global.environment}."}${each.value.domain}/api/*"
  priority = 1
  status   = "active"

  actions = {
    cache_level    = "cache_everything"
    edge_cache_ttl = 300
  }
}

# Origin CA certificate for end-to-end encryption (covers all domains dynamically)
resource "cloudflare_origin_ca_certificate" "main" {
  count = var.enable_origin_ca ? 1 : 0

  csr = var.csr_content
  hostnames = flatten([
    # Generate hostnames dynamically from domains.yml
    for name, config in local.enabled_domains : [
      config.domain,
      "*.${config.domain}"
    ] if config.domain != null
  ])
  request_type       = "origin-rsa"
  requested_validity = 365

  lifecycle {
    create_before_destroy = true
  }
}
