#!/usr/bin/env python3
"""
Dynamic Ansible Inventory for All Things Linux Infrastructure
Generates inventory from domains.yml configuration and integrates with Terraform outputs for IP addresses
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def load_domains_config():
    """Load configuration from domains.yml"""
    script_dir = Path(__file__).parent
    domains_file = script_dir.parent.parent / "configs" / "domains.yml"

    if not domains_file.exists():
        print(f"ERROR: domains.yml not found at {domains_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(domains_file) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse domains.yml: {e}", file=sys.stderr)
        sys.exit(1)


def load_terraform_inventory():
    """Load Terraform ansible_inventory output if available"""
    script_dir = Path(__file__).parent
    terraform_dir = script_dir.parent / "terraform"

    if not terraform_dir.exists():
        return None

    try:
        # Try to get Terraform output
        result = subprocess.run(
            ["terraform", "output", "-json", "ansible_inventory"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            terraform_output = json.loads(result.stdout)
            # The output is JSON-encoded, so we need to decode it
            return json.loads(terraform_output)
        else:
            print(
                f"DEBUG: Terraform output not available: {result.stderr}",
                file=sys.stderr,
            )
            return None

    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        json.JSONDecodeError,
        FileNotFoundError,
    ) as e:
        print(f"DEBUG: Could not load Terraform inventory: {e}", file=sys.stderr)
        return None


def load_vagrant_inventory():
    """Load inventory from Vagrant if available"""
    try:
        # Check if vagrant is installed
        subprocess.run(
            ["vagrant", "--version"], capture_output=True, check=True, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    try:
        # Get status of all machines
        status_result = subprocess.run(
            ["vagrant", "status", "--machine-readable"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
            env=dict(os.environ, VAGRANT_GROUP="all"),
        )

        running_vms = set()
        for line in status_result.stdout.strip().split("\n"):
            parts = line.split(",")
            if len(parts) >= 4 and parts[2] == "state" and parts[3] == "running":
                running_vms.add(parts[1])

        if not running_vms:
            return None

        # Get ssh-config for running machines
        ssh_config_result = subprocess.run(
            ["vagrant", "ssh-config"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
            env=dict(os.environ, VAGRANT_GROUP="all"),
        )

        vagrant_inventory = {}
        current_host = None
        for line in ssh_config_result.stdout.strip().split("\n"):
            line = line.strip()
            if line.startswith("Host "):
                current_host = line.split(" ")[1]
                if current_host in running_vms:
                    vagrant_inventory[current_host] = {}
                else:
                    current_host = None  # This is not a running vm
            elif current_host and line and " " in line:
                key, value = line.split(" ", 1)
                vagrant_inventory[current_host][key.lower()] = value

        # Remap to what ansible expects
        for host, config in vagrant_inventory.items():
            if "hostname" in config:
                vagrant_inventory[host]["ansible_host"] = config["hostname"]
            if "user" in config:
                vagrant_inventory[host]["ansible_user"] = config["user"]
            if "identityfile" in config:
                vagrant_inventory[host]["ansible_ssh_private_key_file"] = config[
                    "identityfile"
                ].strip('"')
            if "port" in config:
                vagrant_inventory[host]["ansible_port"] = config["port"]
            # Force the python interpreter for vagrant hosts
            vagrant_inventory[host]["ansible_python_interpreter"] = "/usr/bin/python3"

        return vagrant_inventory

    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ) as e:
        print(f"DEBUG: Could not load Vagrant inventory: {e}", file=sys.stderr)
        return None


def generate_inventory():
    """Generate Ansible inventory from domains.yml and integrate with Terraform and Vagrant"""
    config = load_domains_config()
    terraform_inventory = load_terraform_inventory()
    vagrant_inventory = load_vagrant_inventory()

    inventory = {"_meta": {"hostvars": {}}, "all": {"children": []}}

    # Environment (default to production)
    environment = config.get("global", {}).get("environment", "production")
    project_name = config.get("global", {}).get("project_name", "allthingslinux")

    inventory_source = None
    if terraform_inventory:
        inventory_source = "terraform"
    elif vagrant_inventory:
        inventory_source = "vagrant"

    all_items = config.get("domains", {}) | config.get("shared_infrastructure", {})

    for name, item in all_items.items():
        if not item.get("enabled", False) or item.get("external"):
            continue

        hosts = []
        # Logic from Vagrantfile
        if "server" in item:
            hostname = (
                item.get("domain")
                or (item.get("services") and item["services"][0])
                or name
            )
            count = item.get("server", {}).get("count", 1)
            if count > 1:
                for i in range(count):
                    hosts.append(f"{hostname.replace('_', '-')}-{i + 1}")
            else:
                hosts.append(hostname.replace("_", "-"))
        elif "servers" in item:
            for server in item.get("servers", []):
                role = server.get("role")
                if role:
                    hosts.append(f"{name.replace('_', '-')}-{role}")

        if not hosts:
            continue

        inventory[name] = {"hosts": hosts}
        if name not in inventory["all"]["children"]:
            inventory["all"]["children"].append(name)

        for server_name in hosts:
            host_vars = {
                "ansible_user": config.get("global", {}).get("default_user", "ansible"),
                "server_role": name,
                "deployment_environment": environment,
                "project": project_name,
            }
            host_vars.update(item)

            if (
                inventory_source == "vagrant"
                and vagrant_inventory
                and server_name in vagrant_inventory
            ):
                host_vars.update(vagrant_inventory[server_name])
            elif inventory_source == "terraform" and terraform_inventory:
                children = terraform_inventory.get("all", {}).get("children", {})
                if children and name in children:
                    tf_host_data = (
                        children.get(name, {}).get("hosts", {}).get(server_name, {})
                    )
                    if tf_host_data:
                        host_vars.update(tf_host_data)

            inventory["_meta"]["hostvars"][server_name] = host_vars

    # Create service-based groups for easier targeting
    service_groups = {}
    for host_name, host_vars in inventory["_meta"]["hostvars"].items():
        for service in host_vars.get("services", []):
            service_group = f"service_{service.replace('-', '_')}"
            if service_group not in service_groups:
                service_groups[service_group] = {"hosts": []}
            service_groups[service_group]["hosts"].append(host_name)

    # Add service groups to inventory
    for group_name, group_data in service_groups.items():
        inventory[group_name] = group_data
        if group_name not in inventory["all"]["children"]:
            inventory["all"]["children"].append(group_name)

    # Create environment-based groups
    env_group_name = f"env_{environment}"
    inventory[env_group_name] = {"hosts": list(inventory["_meta"]["hostvars"].keys())}
    if env_group_name not in inventory["all"]["children"]:
        inventory["all"]["children"].append(env_group_name)

    # Create role-based groups
    role_groups = {}
    for host_name, host_vars in inventory["_meta"]["hostvars"].items():
        role = host_vars.get("server_role", "unknown")
        role_group = f"role_{role}"
        if role_group not in role_groups:
            role_groups[role_group] = {"hosts": []}
        role_groups[role_group]["hosts"].append(host_name)

    # Add role groups to inventory
    for group_name, group_data in role_groups.items():
        inventory[group_name] = group_data
        if group_name not in inventory["all"]["children"]:
            inventory["all"]["children"].append(group_name)

    return inventory


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Dynamic Ansible Inventory")
    parser.add_argument("--list", action="store_true", help="List all hosts")
    parser.add_argument("--host", help="Get host variables")

    args = parser.parse_args()

    if args.list:
        inventory = generate_inventory()
        print(json.dumps(inventory, indent=2))
    elif args.host:
        # For individual host queries, return the host vars
        inventory = generate_inventory()
        host_vars = inventory.get("_meta", {}).get("hostvars", {}).get(args.host, {})
        print(json.dumps(host_vars, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
