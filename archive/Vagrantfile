# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support version 2).
Vagrant.configure("2") do |config|
  # Disable the vbguest plugin to prevent errors
  config.vbguest.auto_update = false

  # Use a generic Ubuntu 24.04 box
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.box_check_update = false

  # Sync the entire project folder to /vagrant on the guest
  config.vm.synced_folder ".", "/vagrant", disabled: false

  # Fix DNS resolution in Ubuntu 22.04+
  config.vm.provision "shell", run: "always", privileged: true, inline: <<-SHELL
    if [ -f /etc/systemd/resolved.conf ]; then
      # Disable and stop the resolved service
      systemctl disable systemd-resolved.service
      systemctl stop systemd-resolved
      # Remove the symlink and create a new resolv.conf
      rm /etc/resolv.conf
      echo "nameserver 8.8.8.8" > /etc/resolv.conf
      echo "nameserver 1.1.1.1" >> /etc/resolv.conf
    fi
  SHELL

  # Load domain configuration
  require 'yaml'
  domains_config = YAML.load_file('configs/domains.yml')

  # Get target group from environment variable, default to 'core'
  target_group = ENV['VAGRANT_GROUP'] || 'core'
  puts "==> Targeting VM group: #{target_group}"

  # Base IP for the private network
  base_ip = "192.168.156"
  ip_counter = 10

  # Helper to configure a VM
  define_vm = lambda do |machine, vm_name, ip|
    machine.vm.hostname = vm_name
    machine.vm.network "private_network", ip: ip

    # Configure provider-specific settings
    machine.vm.provider "virtualbox" do |v|
      v.memory = 2048
      v.cpus = 1
      v.name = vm_name
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    end

    machine.vm.provider "vmware_desktop" do |v|
      v.memory = 2048
      v.cpus = 1
      v.linked_clone = false
    end

    machine.vm.provider "vmware_workstation" do |v|
      v.memory = 2048
      v.cpus = 1
      v.linked_clone = false
    end
  end

  # Create VMs from the domain configuration
  all_items = domains_config['domains'].merge(domains_config['shared_infrastructure'])
  ansible_groups = {}

  all_items.each do |name, item|
    next unless item['enabled']
    next if target_group != 'all' && item['group'] != target_group

    created_vm_names = []

    if item.key?('server')
      hostname = item['domain'] || item['services']&.first || name
      count = item['server']['count'] || 1

      count.times do |i|
        vm_name = count > 1 ? "#{hostname}-#{i + 1}" : hostname
        safe_vm_name = vm_name.gsub('_', '-')
        created_vm_names << safe_vm_name
        config.vm.define safe_vm_name do |machine|
          define_vm.call(machine, safe_vm_name, "#{base_ip}.#{ip_counter}")
          ip_counter += 1
        end
      end
    elsif item.key?('servers')
      item['servers'].each_with_index do |server, i|
        role = server['role'] || i
        safe_vm_name = "#{name.gsub('_', '-')}-#{role}"
        created_vm_names << safe_vm_name
        config.vm.define safe_vm_name do |machine|
          define_vm.call(machine, safe_vm_name, "#{base_ip}.#{ip_counter}")
          ip_counter += 1
        end
      end
    end

    # If this item provides the 'coredns' service, add the created VMs to the 'dns_servers' group
    if item['services']&.include?('coredns')
      ansible_groups['dns_servers'] ||= []
      ansible_groups['dns_servers'].concat(created_vm_names)
    end
  end

  config.vm.provision "ansible", run: "once" do |ansible|
    ansible.playbook = "vagrant.yml"
    ansible.compatibility_mode = "2.0"
    ansible.extra_vars = {
      ansible_user: 'vagrant',
      ansible_python_interpreter: '/usr/bin/python3',
      internal_network_prefix: '192.168.156.'
    }
    ansible.groups = ansible_groups
  end
end
