# Ansible Role: tux (Tux Discord Bot)

This role deploys the Tux Discord bot as a Docker Compose service on the `atl_tools` server.

## Features

- Ensures `/opt/tux-bot` exists
- Deploys `docker-compose.yml`, `.env`, and `settings.yml` from Ansible templates
- Runs the bot using Docker Compose
- No Poetry or Python required on the host

## Usage

Add `tux` to your playbook for the `atl_tools` group:

```yaml
- hosts: atl_tools
  roles:
    - tux
```

## Required Templates

- `docker-compose.yml.j2` (your Compose file)
- `env.j2` (from `.env.example` in the Tux repo)
- `settings.yml.j2` (from `config/settings.yml.example` in the Tux repo)

## Variables

- All secrets and configuration should be provided via Ansible vault or group_vars for the templates.

## References

- See the Tux repo's `.env.example` and `config/settings.yml.example` for required environment and settings variables.
