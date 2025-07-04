# Load balancer (optional)
resource "hcloud_load_balancer" "main" {
  count              = var.load_balancer_enabled ? 1 : 0
  name               = "${var.project_name}-${var.environment}-lb"
  load_balancer_type = var.load_balancer_type
  location           = "nbg1" # Nuremberg

  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Load balancer network
resource "hcloud_load_balancer_network" "main" {
  count            = var.load_balancer_enabled ? 1 : 0
  load_balancer_id = hcloud_load_balancer.main[0].id
  network_id       = hcloud_network.main.id
  ip               = cidrhost(var.subnet_cidr, 5) # Reserve IP for LB
}

# Load balancer service for HTTP
resource "hcloud_load_balancer_service" "http" {
  count            = var.load_balancer_enabled ? 1 : 0
  load_balancer_id = hcloud_load_balancer.main[0].id
  protocol         = "http"
  listen_port      = 80
  destination_port = 80

  health_check {
    protocol = "http"
    port     = 80
    interval = 15
    timeout  = 10
    retries  = 3
    http {
      path         = "/"
      status_codes = ["2??", "3??"]
    }
  }
}

# Load balancer service for HTTPS
resource "hcloud_load_balancer_service" "https" {
  count            = var.load_balancer_enabled ? 1 : 0
  load_balancer_id = hcloud_load_balancer.main[0].id
  protocol         = "tcp"
  listen_port      = 443
  destination_port = 443

  health_check {
    protocol = "tcp"
    port     = 443
    interval = 15
    timeout  = 10
    retries  = 3
  }
}

# Load balancer targets (attach web servers)
resource "hcloud_load_balancer_target" "web_servers" {
  for_each = var.load_balancer_enabled ? {
    for k, v in local.enabled_domains : k => v if contains(lookup(v, "services", []), "nginx") || contains(lookup(v, "services", []), "web")
  } : {}

  type             = "server"
  load_balancer_id = hcloud_load_balancer.main[0].id
  server_id        = hcloud_server.domains[each.key].id
  use_private_ip   = true
}
