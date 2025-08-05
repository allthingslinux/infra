# Local Development Environment

This guide provides instructions for setting up and using the local development environment, which is managed by Vagrant and provisioned with Ansible. This allows for consistent and reproducible testing of infrastructure changes on your local machine before deploying to staging or production.

## Prerequisites

Before you begin, you must have the following software installed on your workstation:

1. **[Vagrant](https://www.vagrantup.com/downloads)**: A tool for building and managing virtual machine environments.
2. **A Virtualization Provider**: Vagrant uses a provider to run the virtual machines. You can use either VirtualBox (free) or VMware (commercial).

   * **VirtualBox (Default)**: Download and install from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads).
   * **VMware Workstation/Fusion**: If you prefer to use VMware, you must purchase and install the [Vagrant VMware Desktop Plugin](https://www.vagrantup.com/vmware/index.html).

## Setup and Usage

The development environment consists of a small, representative subset of the production infrastructure:

* `atl-dev-tools`: A generic application server.
* `atl-dev-db`: A database server.
* `atl-dev-dns`: A CoreDNS server for internal name resolution.

### Bringing the Environment Up

1. **Navigate to the project root directory:**
    Open your terminal and `cd` into the root of this repository.

2. **Start the Vagrant environment:**
    Run the following command:

    ```sh
    vagrant up
    ```

    By default, this will use the VirtualBox provider.

    **To use VMware**, first ensure you have the plugin installed, then run the `up` command with the `--provider` flag:

    ```sh
    vagrant up --provider=vmware_desktop
    ```

    This command will perform the following actions:

   * Download the `bento/ubuntu-24.04` base image if it's not already on your system.
   * Create the three virtual machines defined in the `Vagrantfile`.
   * Configure the private network for the VMs.
   * Automatically run the `ansible` provisioner, which executes the `vagrant.yml` playbook to configure the VMs.

### Accessing the Machines

You can SSH into any of the running virtual machines directly from the project root:

```sh
# SSH into the tools server
vagrant ssh atl-dev-tools

# SSH into the database server
vagrant ssh atl-dev-db

# SSH into the DNS server
vagrant ssh atl-dev-dns
```

The provider is automatically detected for other commands like `ssh`, `halt`, and `destroy`.

Inside the VMs, the entire project directory is mounted at `/vagrant`.

### Provisioning

Ansible provisioning runs automatically the first time you run `vagrant up`. If you make changes to the Ansible roles or the `vagrant.yml` playbook and want to re-apply them to the running VMs, you can run:

```sh
vagrant provision
```

### Managing the Environment

* **Check Status**: To see the status of your Vagrant machines:

  ```sh
  vagrant status
  ```

* **Stopping the Environment**: To stop the machines without deleting them (they can be quickly resumed):

  ```sh
  vagrant halt
  ```

* **Destroying the Environment**: To completely delete the virtual machines and all their resources. This is useful for starting fresh.

  ```sh
  vagrant destroy -f
  ```
