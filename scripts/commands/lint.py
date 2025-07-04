#!/usr/bin/env python3
"""
All Things Linux Infrastructure Linting Script
Python version of the bash lint.sh script with enhanced features
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import click
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..common.config import ConfigManager
from ..common.logging import InfraLogger


class LintManager:
    """Manage all linting operations"""

    def __init__(self, project_root: Path, logger: InfraLogger):
        self.project_root = project_root
        self.logger = logger
        self.console = Console()
        self.config_manager = ConfigManager(project_root, logger)

    def check_prerequisites(self) -> bool:
        """Check if all linting tools are available"""
        self.logger.info("Checking prerequisites...")

        # Check ansible-lint
        if not self._command_exists("ansible-lint"):
            self.logger.error("ansible-lint is not installed. Please install it first.")
            self.logger.info("Run: poetry install")
            return False

        # Get ansible-lint version
        try:
            result = subprocess.run(
                ["ansible-lint", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            version = result.stdout.strip().split("\n")[0]
            self.logger.info(f"ansible-lint version: {version}")
        except subprocess.CalledProcessError:
            self.logger.warn("Could not get ansible-lint version")

        self.logger.success("Prerequisites check passed")
        return True

    def run_ansible_lint(
        self,
        target: str,
        verbose: bool = False,
        fix: bool = False,
        strict: bool = False,
        format: str = "auto",
    ) -> bool:
        """Run ansible-lint on specified target"""
        self.logger.info("Running ansible-lint...")

        # Determine target paths
        target_paths = self._get_target_paths(target)
        if not target_paths:
            return False

        # Build command
        cmd = ["ansible-lint"]

        if verbose:
            cmd.append("-v")

        if fix:
            cmd.append("--fix")

        if strict:
            cmd.append("--strict")

        if format != "auto":
            cmd.extend(["--format", format])

        cmd.extend(target_paths)

        self.logger.info(f"Running command: {' '.join(cmd)}")

        # Run ansible-lint
        try:
            os.chdir(self.project_root)
            result = subprocess.run(cmd, check=True)

            self.logger.success("✅ Ansible-lint completed successfully!")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ansible-lint failed with exit code: {e.returncode}")
            return False

    def run_yaml_checks(self) -> bool:
        """Run YAML syntax validation"""
        self.logger.info("Running YAML syntax checks...")

        # Find all YAML files
        yaml_files = self._find_yaml_files()

        if not yaml_files:
            self.logger.warn("No YAML files found")
            return True

        error_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Checking YAML files...", total=len(yaml_files))

            for yaml_file in yaml_files:
                progress.update(task, description=f"Checking {yaml_file.name}")

                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.logger.error(f"YAML syntax error in {yaml_file}: {e}")
                    error_count += 1
                except Exception as e:
                    self.logger.error(f"Error reading {yaml_file}: {e}")
                    error_count += 1

                progress.advance(task)

        if error_count == 0:
            self.logger.success("✅ All YAML files have valid syntax")
            return True
        else:
            self.logger.error(f"❌ Found {error_count} YAML syntax errors")
            return False

    def run_file_checks(self) -> bool:
        """Run basic file checks"""
        self.logger.info("Running basic file checks...")

        issues = 0

        # Check for trailing whitespace
        self.logger.debug("Checking for trailing whitespace...")
        whitespace_files = self._find_files_with_trailing_whitespace()
        if whitespace_files:
            self.logger.warn(
                f"Found {len(whitespace_files)} files with trailing whitespace"
            )
            for file in whitespace_files[:5]:  # Show first 5
                self.logger.debug(f"  {file}")
            if len(whitespace_files) > 5:
                self.logger.debug(f"  ... and {len(whitespace_files) - 5} more")
            issues += len(whitespace_files)

        # Check for executable YAML files
        self.logger.debug("Checking file permissions...")
        executable_yamls = self._find_executable_yaml_files()
        if executable_yamls:
            self.logger.warn(f"Found {len(executable_yamls)} executable YAML files")
            issues += len(executable_yamls)

        if issues == 0:
            self.logger.success("✅ Basic file checks passed")
        else:
            self.logger.warn(f"⚠️  Found {issues} potential file issues")

        return True

    def run_shell_checks(self, fix: bool = False, verbose: bool = False) -> bool:
        """Run shell script checks using shellcheck and shfmt"""
        self.logger.info("Running shell script checks...")

        # Find shell scripts
        shell_scripts = self._find_shell_scripts()

        if not shell_scripts:
            self.logger.debug("No shell scripts found")
            return True

        self.logger.debug(f"Found {len(shell_scripts)} shell scripts")

        # Check if tools are available
        shellcheck_available = self._command_exists("shellcheck")
        shfmt_available = self._command_exists("shfmt")

        if not shellcheck_available:
            self.logger.warn("shellcheck not found, skipping shell script linting")
            return True

        if not shfmt_available:
            self.logger.warn("shfmt not found, skipping shell script formatting")

        errors = 0
        warnings = 0

        # Run checks on each script
        for script in shell_scripts:
            self.logger.debug(f"Checking: {script}")

            # Run shellcheck
            script_errors, script_warnings = self._run_shellcheck(script, verbose)
            errors += script_errors
            warnings += script_warnings

            # Run shfmt if available
            if shfmt_available:
                self._run_shfmt(script, fix)

        # Summary
        if errors == 0 and warnings == 0:
            self.logger.success("✅ All shell scripts passed checks")
            return True
        elif errors == 0:
            self.logger.warn(f"⚠️  Shell scripts have {warnings} warnings")
            return True
        else:
            self.logger.error(
                f"❌ Shell scripts have {errors} errors and {warnings} warnings"
            )
            return False

    def generate_report(self, success: bool) -> Path:
        """Generate a comprehensive lint report"""
        self.logger.info("Generating lint report...")

        log_dir = self.project_root / "logs"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = log_dir / f"lint-report-{timestamp}.txt"

        # Count files
        yaml_count = len(self._find_yaml_files())
        playbook_count = len(list((self.project_root / "playbooks").glob("*.yml")))
        role_count = len(
            [d for d in (self.project_root / "roles").iterdir() if d.is_dir()]
        )

        # Generate report
        report_content = f"""# All Things Linux Infrastructure Lint Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Project: All Things Linux Infrastructure
- Linting Tool: ansible-lint
- Target: All playbooks and configuration files
- Status: {"PASSED" if success else "FAILED"}

## Files Checked
- {yaml_count} YAML files
- {playbook_count} playbooks
- {role_count} roles

## Log Files
- Check logs directory for detailed output

## Next Steps
- Review any warnings or errors above
- Run 'atl lint --fix' to auto-fix simple issues
- Update .ansible-lint configuration as needed
- Ensure all team members run linting before commits
"""

        report_file.write_text(report_content)
        self.logger.info(f"Report generated: {report_file}")

        return report_file

    def cleanup_old_reports(self):
        """Clean up old lint logs and reports (keep only 5 most recent)"""
        log_dir = self.project_root / "logs"

        # Clean up old lint logs
        lint_logs = sorted(log_dir.glob("lint-*.log"))
        for old_log in lint_logs[:-5]:  # Keep last 5
            old_log.unlink()

        # Clean up old reports
        lint_reports = sorted(log_dir.glob("lint-report-*.txt"))
        for old_report in lint_reports[:-5]:  # Keep last 5
            old_report.unlink()

    def _get_target_paths(self, target: str) -> List[str]:
        """Get target paths based on target type"""
        if target == "all":
            return ["playbooks/", "roles/", "tasks/"]
        elif target == "playbooks":
            return ["playbooks/"]
        elif target == "inventories":
            return ["inventories/"]
        elif target == "roles":
            return ["roles/"]
        else:
            self.logger.error(f"Unknown target: {target}")
            return []

    def _find_yaml_files(self) -> List[Path]:
        """Find all YAML files in the project"""
        yaml_files = []
        exclude_dirs = {
            ".git",
            "logs",
            ".venv",
            ".ansible",
            "node_modules",
            ".cache",
            "secrets",
        }

        for pattern in ["*.yml", "*.yaml"]:
            for file in self.project_root.rglob(pattern):
                # Skip excluded directories
                if any(part in exclude_dirs for part in file.parts):
                    continue
                yaml_files.append(file)

        return sorted(yaml_files)

    def _find_files_with_trailing_whitespace(self) -> List[Path]:
        """Find files with trailing whitespace"""
        files_with_whitespace = []

        for yml_file in self._find_yaml_files():
            try:
                with open(yml_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        if line.rstrip() != line.rstrip("\n"):
                            files_with_whitespace.append(yml_file)
                            break
            except Exception:
                continue

        return files_with_whitespace

    def _find_executable_yaml_files(self) -> List[Path]:
        """Find YAML files that are executable"""
        executable_files = []

        for yml_file in self._find_yaml_files():
            if yml_file.stat().st_mode & 0o111:  # Check if executable
                executable_files.append(yml_file)

        return executable_files

    def _find_shell_scripts(self) -> List[Path]:
        """Find all shell scripts"""
        scripts_dir = self.project_root / "scripts"
        return sorted(scripts_dir.glob("*.sh"))

    def _run_shellcheck(self, script: Path, verbose: bool) -> Tuple[int, int]:
        """Run shellcheck on a script and return (errors, warnings)"""
        try:
            result = subprocess.run(
                ["shellcheck", str(script)], capture_output=True, text=True, check=True
            )
            self.logger.debug(f"✅ {script.name}: shellcheck passed")
            return 0, 0

        except subprocess.CalledProcessError as e:
            output = e.stdout + e.stderr

            # Count errors and warnings
            errors = output.count("error:")
            warnings = output.count("warning:")

            if errors > 0:
                self.logger.error(
                    f"❌ {script.name}: shellcheck found {errors} errors, {warnings} warnings"
                )
            else:
                self.logger.warn(
                    f"⚠️  {script.name}: shellcheck found {warnings} warnings"
                )

            # Show detailed output if verbose or errors
            if verbose or errors > 0:
                for line in output.split("\n"):
                    if line.strip():
                        self.logger.debug(f"  {line}")

            return errors, warnings

    def _run_shfmt(self, script: Path, fix: bool):
        """Run shfmt on a script"""
        try:
            if fix:
                # Format the script
                subprocess.run(
                    ["shfmt", "-w", "-s", "-i", "4", str(script)],
                    check=True,
                    capture_output=True,
                )
                self.logger.debug(f"✅ {script.name}: formatted")
            else:
                # Just check formatting
                subprocess.run(
                    ["shfmt", "-d", "-s", "-i", "4", str(script)],
                    check=True,
                    capture_output=True,
                )
        except subprocess.CalledProcessError:
            if fix:
                self.logger.warn(f"⚠️  {script.name}: formatting failed")
            else:
                self.logger.warn(
                    f"⚠️  {script.name}: needs formatting (run with --fix to format)"
                )

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists"""
        try:
            subprocess.run(["which", command], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False


# Click CLI interface
@click.command()
@click.option(
    "--target",
    "-t",
    type=click.Choice(["all", "playbooks", "inventories", "roles"]),
    default="all",
    help="Target to lint",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--fix", "-f", is_flag=True, help="Try to auto-fix issues where possible")
@click.option("--strict", is_flag=True, help="Use strict mode (exit on warnings)")
@click.option(
    "--format",
    type=click.Choice(["auto", "json", "codeclimate", "sarif"]),
    default="auto",
    help="Output format for ansible-lint",
)
def cli(target, verbose, fix, strict, format):
    """All Things Linux Infrastructure Linting

    Run comprehensive linting checks on Ansible infrastructure code
    """
    # Initialize
    project_root = Path(__file__).parent.parent
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
    if not lint_manager.check_prerequisites():
        sys.exit(1)

    overall_success = True

    # Run all checks
    logger.info("Starting comprehensive linting checks...")

    # YAML syntax checks
    if not lint_manager.run_yaml_checks():
        overall_success = False

    # Basic file checks
    if not lint_manager.run_file_checks():
        overall_success = False

    # Shell script checks
    if not lint_manager.run_shell_checks(fix, verbose):
        overall_success = False

    # Ansible lint
    if not lint_manager.run_ansible_lint(target, verbose, fix, strict, format):
        overall_success = False

    # Generate report
    lint_manager.generate_report(overall_success)

    # Cleanup old reports
    lint_manager.cleanup_old_reports()

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
