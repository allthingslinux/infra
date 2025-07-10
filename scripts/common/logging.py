"""Logging utilities for infrastructure scripts"""

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text


class LogCleaner:
    """Handles cleanup of old log files"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir

    def cleanup_logs(self, max_files_per_type: int = 10, max_age_days: int = 30):
        """Clean up old log files

        Args:
            max_files_per_type: Maximum number of log files to keep per tool type
            max_age_days: Maximum age of log files in days

        Returns:
            int: Number of files removed
        """
        if not self.log_dir.exists():
            return 0

        # Group log files by type (tool name)
        log_groups = {}
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        for log_file in self.log_dir.glob("*.log"):
            # Extract tool name from filename (e.g., "deploy-20250704_052731.log" -> "deploy")
            match = re.match(r"^([^-]+)-\d{8}_\d{6}\.log$", log_file.name)
            if match:
                tool_name = match.group(1)
                if tool_name not in log_groups:
                    log_groups[tool_name] = []
                log_groups[tool_name].append(log_file)

        files_removed = 0

        # Clean up each tool's logs
        for _tool_name, log_files in log_groups.items():
            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Remove files beyond the limit
            if len(log_files) > max_files_per_type:
                for log_file in log_files[max_files_per_type:]:
                    try:
                        log_file.unlink()
                        files_removed += 1
                    except OSError:
                        pass  # File might be in use or already deleted

            # Remove old files
            for log_file in log_files[:max_files_per_type]:  # Only check recent files
                try:
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        log_file.unlink()
                        files_removed += 1
                except OSError:
                    pass

        # Also clean up any orphaned log report files
        for report_file in self.log_dir.glob("*-report-*.txt"):
            try:
                file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                if file_time < cutoff_date:
                    report_file.unlink()
                    files_removed += 1
            except OSError:
                pass

        return files_removed


class InfraLogger:
    """Logger for infrastructure operations with rich output"""

    def __init__(
        self, name: str, log_dir: Path | None = None, auto_cleanup: bool = True
    ):
        self.console = Console()
        self.name = name

        # Setup log directory
        if log_dir:
            self.log_dir = log_dir
        else:
            self.log_dir = Path.cwd() / "logs"

        self.log_dir.mkdir(exist_ok=True)

        # Auto-cleanup old logs
        if auto_cleanup:
            cleaner = LogCleaner(self.log_dir)
            cleaner.cleanup_logs(max_files_per_type=5, max_age_days=7)

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"{name}-{timestamp}.log"

        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Rich console handler
        console_handler = RichHandler(
            console=self.console, show_time=True, show_path=False, rich_tracebacks=True
        )
        console_handler.setLevel(logging.INFO)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)

    def warn(self, message: str):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)

    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

    def success(self, message: str):
        """Log success message with green styling"""
        self.console.print(f"✅ {message}", style="green")
        self.logger.info(f"SUCCESS: {message}")

    def banner(self, title: str, subtitle: str = ""):
        """Display a banner"""
        if subtitle:
            text = Text(f"{title}\n{subtitle}", justify="center")
        else:
            text = Text(title, justify="center")

        panel = Panel(
            text,
            title="All Things Linux",
            subtitle="Infrastructure Management",
            border_style="blue",
        )
        self.console.print(panel)

    def table_start(self, title: str):
        """Start a table output"""
        self.console.print(f"\n[bold blue]{title}[/bold blue]")

    def table_row(self, key: str, value: str, status: str = "enabled"):
        """Print a table row"""
        if status == "enabled":
            self.console.print(f"  [green]•[/green] {key} -> {value}")
        else:
            self.console.print(f"  [yellow]•[/yellow] {key} -> {value} ({status})")

    @staticmethod
    def cleanup_logs(
        log_dir: Path | None = None,
        max_files_per_type: int = 5,
        max_age_days: int = 7,
    ):
        """Manually clean up log files"""
        if log_dir is None:
            log_dir = Path.cwd() / "logs"

        cleaner = LogCleaner(log_dir)
        return cleaner.cleanup_logs(max_files_per_type, max_age_days)
