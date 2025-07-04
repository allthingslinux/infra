terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

# Create firewall for SSH access
resource "hcloud_firewall" "ssh" {
  name = "${var.name}-ssh-${var.environment}"

  rule {
    direction  = "in"
    port       = var.ssh_port
    protocol   = "tcp"
    source_ips = var.allowed_ips
  }

  labels = merge(var.tags, {
    Environment = var.environment
    Module      = "security"
    Purpose     = "ssh-access"
  })
}

# Create firewall for web traffic
resource "hcloud_firewall" "web" {
  name = "${var.name}-web-${var.environment}"

  # HTTP and HTTPS rules
  dynamic "rule" {
    for_each = var.web_ports
    content {
      direction  = "in"
      port       = rule.value
      protocol   = "tcp"
      source_ips = ["0.0.0.0/0", "::/0"]
    }
  }

  labels = merge(var.tags, {
    Environment = var.environment
    Module      = "security"
    Purpose     = "web-traffic"
  })
}

# Create firewall for custom rules
resource "hcloud_firewall" "custom" {
  count = length(var.custom_rules) > 0 ? 1 : 0
  name  = "${var.name}-custom-${var.environment}"

  dynamic "rule" {
    for_each = var.custom_rules
    content {
      direction  = rule.value.direction
      port       = rule.value.port
      protocol   = rule.value.protocol
      source_ips = rule.value.source_ips
    }
  }

  labels = merge(var.tags, {
    Environment = var.environment
    Module      = "security"
    Purpose     = "custom-rules"
  })
}
