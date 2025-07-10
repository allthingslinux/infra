#!/usr/bin/env python3
"""
All Things Linux Infrastructure Linting Script
Unified linting orchestrator that delegates to specialized tools
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console

from ..common.config import ConfigManager
from ..common.logging import InfraLogger


class LintManager:
    """Unified linting orchestrator

    This class coordinates multiple linting tools, each using their own
    configuration files:

    - ansible-lint: Uses .ansible-lint config
    - ruff: Uses pyproject.toml config
    - yamllint: Uses .yamllint.yml config
    - terraform: Uses terraform fmt/validate + .tflint.hcl
    - shell: Uses shellcheck + shfmt

    Each tool handles its own file discovery and exclusion patterns.
    """

    def __init__(self, project_root: Path, logger: InfraLogger):
        self.project_root = project_root
        self.logger = logger
        self.console = Console()
        self.config_manager = ConfigManager(project_root, logger)

    def check_prerequisites(self) -> dict[str, bool]:
        """Check if all linting tools are available"""
        self.logger.info("Checking linting tool prerequisites...")

        tools = {
            "uv": "uv",  # Main dependency manager
            "ansible-lint": "ansible-lint",
            "ruff": "ruff",
            "yamllint": "yamllint",
            "python-terraform": "python",  # python-terraform is a Python package
            "tflint": "tflint",  # Available via tflint-py package
            "shellcheck": "shellcheck",
            "shfmt": "shfmt",
        }

        available = {}
        for tool_name, command in tools.items():
            available[tool_name] = self._command_exists(command)
            if available[tool_name]:
                self.logger.debug(f"✅ {tool_name} available")
            else:
                self.logger.debug(f"❌ {tool_name} not found")

        # Show summary
        available_count = sum(available.values())
        total_count = len(tools)
        self.logger.info(f"Available tools: {available_count}/{total_count}")

        return available

    def run_all_linters(
        self,
        target: str = "all",
        verbose: bool = False,
        fix: bool = False,
        strict: bool = False,
    ) -> bool:
        """Run targeted linters based on the target parameter"""
        self.logger.info("Starting comprehensive linting...")

        # Check prerequisites but don't store unused result
        self.check_prerequisites()
        overall_success = True
        results = {}

        # Define all available linters
        all_linters = [
            ("Python (ruff)", self.run_ruff_lint),
            ("YAML (yamllint)", self.run_yaml_lint),
            ("Ansible (ansible-lint)", self.run_ansible_lint),
            ("Terraform (terraform)", self.run_terraform_lint),
            ("Shell (shellcheck)", self.run_shell_lint),
            ("Markdown (pymarkdown)", self.run_markdown_lint),
        ]

        # Filter linters based on target
        if target == "all":
            linters = all_linters
        elif target == "python":
            linters = [("Python (ruff)", self.run_ruff_lint)]
        elif target == "markdown":
            linters = [("Markdown (pymarkdown)", self.run_markdown_lint)]
        elif target in ["playbooks", "inventories", "roles"]:
            # These are Ansible-specific targets
            linters = [("Ansible (ansible-lint)", self.run_ansible_lint)]
        else:
            self.logger.error(f"Unknown target: {target}")
            return False

        # Run selected linters
        for linter_name, linter_func in linters:
            self.logger.info(f"Running {linter_name}...")
            try:
                success = linter_func(target, verbose, fix, strict)
                results[linter_name] = success
                if not success:
                    overall_success = False
                    self.logger.error(f"❌ {linter_name} failed")
                else:
                    self.logger.success(f"✅ {linter_name} passed")
            except Exception as e:
                self.logger.error(f"❌ {linter_name} error: {e}")
                results[linter_name] = False
                overall_success = False

        # Summary
        self._print_summary(results, overall_success)
        return overall_success

    def run_ruff_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run ruff Python linting via uv"""
        cmd = ["uv", "run", "ruff", "check"]
        if fix:
            cmd.append("--fix")
        if verbose:
            cmd.append("--verbose")

        # Add target paths for Python files
        if target == "all":
            cmd.append("scripts/")
        elif target == "python":
            cmd.append("scripts/")

        return self._run_command(cmd, "ruff")

    def run_yaml_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run yamllint YAML linting via uv"""
        # Only scan project directories, not glob patterns
        paths_to_scan = [
            "ansible/",
            "configs/",
            "docs/",
            "terraform/",
            "monitoring/",
            ".github/",
        ]

        cmd = ["uv", "run", "yamllint"] + paths_to_scan
        if strict:
            cmd.append("--strict")

        return self._run_command(cmd, "yamllint")

    def run_ansible_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run ansible-lint using .ansible-lint configuration via uv"""
        cmd = ["uv", "run", "ansible-lint", "--config-file=.ansible-lint"]

        if verbose:
            cmd.append("-v")
        if fix:
            cmd.append("--fix")
        if strict:
            cmd.append("--strict")

        # Add specific paths for targeted linting
        if target == "playbooks":
            cmd.append("ansible/playbooks/")
        elif target == "roles":
            cmd.append("ansible/roles/")
        elif target == "inventories":
            cmd.append("ansible/inventories/")
        else:
            # For "all", scan the entire ansible directory
            cmd.append("ansible/")

        return self._run_command(cmd, "ansible-lint")

    def run_terraform_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run terraform fmt, validate, and tflint using python-terraform and uv"""
        success = True

        # Use python-terraform via uv run python for terraform operations
        try:
            # Terraform fmt
            fmt_script = f"""
import sys
from python_terraform import Terraform
tf = Terraform(working_dir='terraform')
ret_code, stdout, stderr = tf.fmt(check={"True" if not fix else "False"}, recursive=True)
if ret_code != 0:
    print(stderr)
    sys.exit(1)
print('✅ terraform fmt passed')
"""
            if not self._run_command(
                ["uv", "run", "python", "-c", fmt_script], "terraform fmt"
            ):
                success = False

            # Terraform validate
            validate_script = """
import sys
from python_terraform import Terraform
tf = Terraform(working_dir='terraform')
# Initialize terraform
ret_code, stdout, stderr = tf.init(backend=False)
if ret_code != 0:
    print(stderr)
    sys.exit(1)
# Validate terraform
ret_code, stdout, stderr = tf.validate()
if ret_code != 0:
    print(stderr)
    sys.exit(1)
print('✅ terraform validate passed')
"""
            if not self._run_command(
                ["uv", "run", "python", "-c", validate_script], "terraform validate"
            ):
                success = False

        except Exception as e:
            self.logger.error(f"Error running terraform operations: {e}")
            success = False

        # TFLint using uv (tflint-py package)
        # Use absolute path to config file and --chdir due to tflint v0.47+ changes
        config_path = str(self.project_root / ".tflint.hcl")
        if not self._run_command(
            [
                "uv",
                "run",
                "tflint",
                f"--config={config_path}",
                "--chdir=terraform",
                "--recursive",
            ],
            "tflint",
        ):
            success = False

        return success

    def run_shell_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run shellcheck and shfmt on shell scripts using uv"""
        success = True

        # Find shell scripts only in project directories, not third-party collections
        project_dirs = [
            "scripts/",
            "terraform/",
            "docs/",
            "ansible/playbooks/",
            "ansible/roles/",
            "ansible/inventories/",
            ".github/",
        ]

        shell_scripts = []
        for project_dir in project_dirs:
            dir_path = self.project_root / project_dir
            if dir_path.exists():
                shell_scripts.extend(dir_path.rglob("*.sh"))

        if not shell_scripts:
            self.logger.debug("No shell scripts found in project directories")
            return True

        # Run shellcheck via uv
        for script in shell_scripts:
            cmd = ["uv", "run", "shellcheck", str(script)]
            if not self._run_command(cmd, f"shellcheck {script.name}"):
                success = False

        # Run shfmt via uv
        for script in shell_scripts:
            cmd = ["uv", "run", "shfmt", "-i", "2", "-s"]
            if fix:
                cmd.extend(["-w", str(script)])
            else:
                cmd.extend(["-d", str(script)])

            if not self._run_command(cmd, f"shfmt {script.name}"):
                success = False

        return success

    def run_markdown_lint(
        self, target: str, verbose: bool, fix: bool, strict: bool
    ) -> bool:
        """Run pymarkdown linting via uv"""
        # Find markdown files in project directories
        project_dirs = [
            "docs/",
            "README.md",
            "*.md",
            "ansible/",
            "terraform/",
        ]

        markdown_files = []
        for project_dir in project_dirs:
            if project_dir.endswith(".md"):
                md_file = self.project_root / project_dir
                if md_file.exists():
                    markdown_files.append(md_file)
            else:
                dir_path = self.project_root / project_dir
                if dir_path.exists():
                    markdown_files.extend(dir_path.rglob("*.md"))

        if not markdown_files:
            self.logger.debug("No markdown files found in project directories")
            return True

            # Choose between fix and scan based on fix flag
        command = "fix" if fix else "scan"
        cmd = ["uv", "run", "pymarkdown", command] + [str(f) for f in markdown_files]

        # Add verbose flag for scan command (fix doesn't support verbose)
        if verbose and not fix:
            cmd.append("--verbose")
        if strict and not fix:
            cmd.append("--strict")

        # Handle pymarkdown fix mode differently - it returns non-zero when fixes are made
        if fix:
            return self._run_markdown_fix_command(cmd)
        else:
            return self._run_command(cmd, "pymarkdown")

    def _run_command(
        self, cmd: list[str], tool_name: str, cwd: str | None = None
    ) -> bool:
        """Run a command and return success status"""
        try:
            run_cwd = self.project_root / cwd if cwd else self.project_root
            result = subprocess.run(
                cmd, cwd=run_cwd, capture_output=True, text=True, check=True
            )

            if result.stdout.strip():
                self.logger.debug(f"{tool_name} output: {result.stdout.strip()}")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"{tool_name} failed with exit code {e.returncode}")
            if e.stdout:
                self.logger.error(f"stdout: {e.stdout}")
            if e.stderr:
                self.logger.error(f"stderr: {e.stderr}")
            return False

    def _run_markdown_fix_command(self, cmd: list[str]) -> bool:
        """Run pymarkdown fix command and handle its special exit codes

        pymarkdown fix returns:
        - 0: No issues found
        - 1: Issues found but none fixable
        - 2: Errors occurred during processing
        - 3: Issues found and fixed
        """
        try:
            run_cwd = self.project_root
            result = subprocess.run(
                cmd, cwd=run_cwd, capture_output=True, text=True, check=False
            )

            # Log output regardless of exit code
            if result.stdout.strip():
                self.logger.info(f"pymarkdown output: {result.stdout.strip()}")
            if result.stderr.strip():
                self.logger.debug(f"pymarkdown stderr: {result.stderr.strip()}")

            # Handle different exit codes
            if result.returncode == 0:
                self.logger.success("No markdown issues found")
                return True
            elif result.returncode == 3:
                self.logger.success("Markdown issues found and fixed successfully")
                return True
            elif result.returncode == 1:
                self.logger.error("Markdown issues found but could not be auto-fixed")
                return False
            elif result.returncode == 2:
                self.logger.error("Errors occurred during markdown processing")
                return False
            else:
                self.logger.error(
                    f"pymarkdown returned unexpected exit code {result.returncode}"
                )
                return False

        except Exception as e:
            self.logger.error(f"pymarkdown fix failed with exception: {e}")
            return False

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run(["which", command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _print_summary(self, results: dict[str, bool], overall_success: bool):
        """Print linting summary"""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("LINTING SUMMARY")
        self.logger.info("=" * 50)

        for linter_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            self.logger.info(f"{linter_name:25} {status}")

        self.logger.info("=" * 50)
        if overall_success:
            self.logger.success("🎉 ALL LINTERS PASSED!")
        else:
            self.logger.error("💥 SOME LINTERS FAILED!")

    def generate_report(self, results: dict[str, bool], overall_success: bool) -> Path:
        """Generate a comprehensive lint report"""
        self.logger.info("Generating lint report...")

        log_dir = self.project_root / "logs"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = log_dir / f"lint-report-{timestamp}.txt"

        # Generate report
        report_content = f"""# All Things Linux Infrastructure Lint Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Project: All Things Linux Infrastructure
- Status: {"PASSED" if overall_success else "FAILED"}

## Linter Results
"""

        for linter_name, success in results.items():
            status = "PASSED" if success else "FAILED"
            report_content += f"- {linter_name}: {status}\n"

        report_content += """
## Configuration Files
- ansible-lint: .ansible-lint
- ruff: pyproject.toml
- yamllint: .yamllint.yml
- terraform: .tflint.hcl
    - lefthook: .lefthook.yml

## Next Steps
- Review any failed linters above
- Run with --fix flag to auto-fix simple issues
- Check individual tool documentation for advanced options
"""

        report_file.write_text(report_content)
        self.logger.info(f"Report generated: {report_file}")
        return report_file


# Click CLI interface
@click.command()
@click.option(
    "--target",
    "-t",
    type=click.Choice(
        ["all", "playbooks", "inventories", "roles", "python", "markdown"]
    ),
    default="all",
    help="Target to lint (e.g., all, playbooks, inventories, roles, python)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--fix", "-f", is_flag=True, help="Try to auto-fix issues where possible")
@click.option("--strict", is_flag=True, help="Use strict mode (exit on warnings)")
def cli(target, verbose, fix, strict):
    """All Things Linux Infrastructure Linting

    Run comprehensive linting checks on Ansible infrastructure code
    """
    # Initialize
    project_root = Path(__file__).parent.parent.parent
    logger = InfraLogger("lint", project_root / "logs")

    # Show banner
    logger.banner(
        "All Things Linux Infrastructure Linting",
        "Ensuring code quality and best practices",
    )

    # Log configuration
    logger.info(f"Target: {target}")
    logger.info(f"Verbose: {verbose}")
    logger.info(f"Auto-fix: {fix}")
    logger.info(f"Strict mode: {strict}")

    # Initialize lint manager
    lint_manager = LintManager(project_root, logger)

    # Check prerequisites
    lint_manager.check_prerequisites()

    # Run targeted checks
    overall_success = lint_manager.run_all_linters(target, verbose, fix, strict)

    # Final result
    if overall_success:
        logger.success("🎉 All linting checks passed!")
        logger.info("Your Ansible code follows best practices.")
    else:
        logger.error("💥 Linting checks failed!")
        logger.error("Please review and fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    cli()
