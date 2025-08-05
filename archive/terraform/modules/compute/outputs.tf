output "server_ids" {
  description = "Map of server names to their IDs"
  value = {
    for name, server in hcloud_server.servers : name => server.id
  }
}

output "server_names" {
  description = "Map of server names to their full names"
  value = {
    for name, server in hcloud_server.servers : name => server.name
  }
}

output "server_public_ips" {
  description = "Map of server names to their public IP addresses"
  value = {
    for name, server in hcloud_server.servers : name => server.ipv4_address
  }
}

output "server_private_ips" {
  description = "Map of server names to their private IP addresses"
  value = {
    for name, network in hcloud_server_network.server_networks : name => network.ip
  }
}

output "server_info" {
  description = "Complete server information"
  value = {
    for name, server in hcloud_server.servers : name => {
      id             = server.id
      name           = server.name
      public_ip      = server.ipv4_address
      private_ip     = hcloud_server_network.server_networks[name].ip
      server_type    = server.server_type
      location       = server.location
      image          = server.image
      status         = server.status
      backup_enabled = server.backups
    }
  }
}
