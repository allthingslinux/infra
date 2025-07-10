#!/usr/bin/env python3
"""
All Things Linux Infrastructure CLI
Unified command-line interface for all infrastructure operations
"""

import click
from rich.console import Console

# Import all command modules at the top
from .commands.deploy import cli as deploy_group
from .commands.diagrams import cli as diagrams_command
from .commands.docs import cli as docs_command
from .commands.lint import cli as lint_command
from .commands.update_collections import cli as update_collections_command

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="atl")
def cli():
    """All Things Linux Infrastructure CLI

    Unified command-line interface for managing ATL infrastructure.

    Commands are organized into logical groups:
    - Infrastructure: deploy, plan, apply, destroy
    - Quality: lint, check
    - Docs: docs, diagrams
    - Utils: update-collections

    Use 'atl <group> --help' for more details on each command group.
    """
    pass


# === Infrastructure Commands ===


@cli.group(name="infra")
def infra():
    """Infrastructure management commands (Terraform + Ansible)"""
    pass


# Add all deploy commands to the infra group
for command_name, command in deploy_group.commands.items():
    infra.add_command(command, name=command_name)


# === Quality Commands ===


@cli.group(name="quality")
def quality():
    """Code quality and linting commands"""
    pass


quality.add_command(lint_command, name="lint")


# === Documentation Commands ===


@cli.group(name="docs")
def docs():
    """Documentation and diagram generation"""
    pass


docs.add_command(docs_command, name="build")
docs.add_command(diagrams_command, name="diagrams")


# === Utility Commands ===


@cli.group(name="utils")
def utils():
    """Utility and maintenance commands"""
    pass


utils.add_command(update_collections_command, name="update-collections")


@utils.command(name="cleanup-logs")
@click.option(
    "--max-files",
    "-n",
    type=int,
    default=5,
    help="Maximum log files to keep per tool type",
)
@click.option(
    "--max-age", "-a", type=int, default=7, help="Maximum age of log files in days"
)
@click.option(
    "--dry-run",
    "-d",
    is_flag=True,
    help="Show what would be cleaned up without doing it",
)
def cleanup_logs(max_files, max_age, dry_run):
    """Clean up old log files"""
    from pathlib import Path

    from .common.logging import LogCleaner

    log_dir = Path.cwd() / "logs"

    if not log_dir.exists():
        console.print("No logs directory found", style="yellow")
        return

    # Count current log files
    log_files = list(log_dir.glob("*.log"))
    if not log_files:
        console.print("No log files found to clean up", style="green")
        return

    console.print(f"Found {len(log_files)} log files in {log_dir}")

    if dry_run:
        console.print(
            f"[dim]Would clean up logs older than {max_age} days and keep only {max_files} files per tool type[/dim]"
        )
        # Show what would be cleaned
        cleaner = LogCleaner(log_dir)

        # Get log groups for display
        import re

        log_groups = {}
        for log_file in log_files:
            match = re.match(r"^([^-]+)-\d{8}_\d{6}\.log$", log_file.name)
            if match:
                tool_name = match.group(1)
                if tool_name not in log_groups:
                    log_groups[tool_name] = []
                log_groups[tool_name].append(log_file)

        for tool_name, files in log_groups.items():
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            console.print(f"  [blue]{tool_name}[/blue]: {len(files)} files")
            if len(files) > max_files:
                console.print(
                    f"    [dim]Would remove {len(files) - max_files} older files[/dim]"
                )
    else:
        cleaner = LogCleaner(log_dir)
        files_removed = cleaner.cleanup_logs(max_files, max_age)

        if files_removed > 0:
            console.print(f"✅ Cleaned up {files_removed} log files", style="green")
        else:
            console.print("No old log files to clean up", style="green")


# === Quick Access Commands ===


@cli.command()
@click.option(
    "--environment",
    "-e",
    default="development",
    help="Target environment (development/staging/production)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be deployed")
@click.option(
    "--target",
    "-t",
    default="all",
    type=click.Choice(["all", "infrastructure", "domains", "domain"]),
    help="Deployment target",
)
@click.option("--domain-name", help="Domain name for domain-specific deployment")
@click.option("--ansible-only", is_flag=True, help="Run only Ansible configuration")
@click.option("--terraform-only", is_flag=True, help="Run only Terraform provisioning")
def plan(
    environment, verbose, dry_run, target, domain_name, ansible_only, terraform_only
):
    """Quick plan command (equivalent to 'atl infra plan')"""
    from .commands.deploy import plan as deploy_plan

    ctx = click.Context(deploy_plan)
    ctx.obj = {"environment": environment, "verbose": verbose, "dry_run": dry_run}

    ctx.invoke(
        deploy_plan,
        target=target,
        domain_name=domain_name,
        ansible_only=ansible_only,
        terraform_only=terraform_only,
    )


@cli.command()
@click.option(
    "--environment",
    "-e",
    default="development",
    help="Target environment (development/staging/production)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", "-d", is_flag=True, help="Show what would be deployed")
@click.option(
    "--target",
    "-t",
    default="all",
    type=click.Choice(["all", "infrastructure", "domains", "domain"]),
    help="Deployment target",
)
@click.option("--domain-name", help="Domain name for domain-specific deployment")
@click.option("--auto-approve", "-y", is_flag=True, help="Auto-approve changes")
@click.option("--ansible-only", is_flag=True, help="Run only Ansible configuration")
@click.option("--terraform-only", is_flag=True, help="Run only Terraform provisioning")
def apply(
    environment,
    verbose,
    dry_run,
    target,
    domain_name,
    auto_approve,
    ansible_only,
    terraform_only,
):
    """Quick apply command (equivalent to 'atl infra apply')"""
    from .commands.deploy import apply as deploy_apply

    ctx = click.Context(deploy_apply)
    ctx.obj = {"environment": environment, "verbose": verbose, "dry_run": dry_run}

    ctx.invoke(
        deploy_apply,
        target=target,
        domain_name=domain_name,
        auto_approve=auto_approve,
        ansible_only=ansible_only,
        terraform_only=terraform_only,
    )


@cli.command()
@click.option(
    "--target",
    "-t",
    type=click.Choice(
        ["all", "playbooks", "inventories", "roles", "python", "markdown"]
    ),
    default="all",
    help="Target to lint",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--fix", "-f", is_flag=True, help="Try to auto-fix issues where possible")
@click.option("--strict", is_flag=True, help="Use strict mode (exit on warnings)")
def lint(target, verbose, fix, strict):
    """Quick lint command (equivalent to 'atl quality lint')"""
    from .commands.lint import cli as lint_cli

    ctx = click.Context(lint_cli)
    ctx.invoke(lint_cli, target=target, verbose=verbose, fix=fix, strict=strict)


# === Help and Info Commands ===


@cli.command()
def info():
    """Show ATL CLI information and available commands"""
    console.print()
    console.print("[bold blue]All Things Linux Infrastructure CLI[/bold blue]")
    console.print()
    console.print("[bold]Available Command Groups:[/bold]")
    console.print(
        "  [cyan]infra[/cyan]     - Infrastructure management (Terraform + Ansible)"
    )
    console.print("    • plan, apply, destroy, check, enable, disable, config")
    console.print("  [cyan]quality[/cyan]   - Code quality and linting")
    console.print("    • lint")
    console.print("  [cyan]docs[/cyan]      - Documentation and diagrams")
    console.print("    • build, diagrams")
    console.print("  [cyan]utils[/cyan]     - Utility and maintenance commands")
    console.print("    • update-collections, cleanup-logs")
    console.print()
    console.print("[bold]Quick Access Commands:[/bold]")
    console.print("  [green]plan[/green]      - Plan infrastructure changes")
    console.print("  [green]apply[/green]     - Apply infrastructure changes")
    console.print("  [green]lint[/green]      - Run Ansible linting")
    console.print()
    console.print("[bold]Examples:[/bold]")
    console.print("  atl plan                          # Plan infrastructure changes")
    console.print(
        "  atl apply -y                      # Apply changes with auto-approve"
    )
    console.print("  atl infra destroy                 # Destroy infrastructure")
    console.print("  atl quality lint --fix            # Run linting with auto-fix")
    console.print("  atl docs build --serve            # Build and serve documentation")
    console.print("  atl utils update-collections      # Update Ansible collections")
    console.print("  atl utils cleanup-logs            # Clean up old log files")
    console.print()
    console.print("Use 'atl <command> --help' for detailed help on any command.")


@cli.command()
def status():
    """Show infrastructure status and health checks"""
    console.print()
    console.print("[bold blue]ATL Infrastructure Status[/bold blue]")
    console.print()

    # Check if tools are available
    import shutil

    tools = {
        "Terraform": "terraform",
        "Ansible": "ansible",
        "Ansible Playbook": "ansible-playbook",
        "Docker": "docker",
        "uv": "uv",
    }

    console.print("[bold]Tool Availability:[/bold]")
    for tool_name, tool_cmd in tools.items():
        if shutil.which(tool_cmd):
            console.print(f"  ✅ {tool_name}")
        else:
            console.print(f"  ❌ {tool_name} (not found)")

    console.print()
    console.print("Use 'atl info' for available commands.")


if __name__ == "__main__":
    cli()
