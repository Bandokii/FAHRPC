"""
Logger Module for FAHRPC
=======================

Provides enhanced logging capabilities with timestamped entries,
module context, and full stack traces for debugging.

Features:
    - Timestamped log entries [YYYY-MM-DD HH:MM:SS]
    - Module and function context (module.function():line)
    - Log level indicators (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Full exception stack traces for error debugging
    - Rotating file handler (10MB max, 5 backups)
    - Asyncio warning suppression (configurable)
    - stderr redirection with timestamps

Log File Location:
    Windows: %LOCALAPPDATA%\\Bandokii\\fahrpc\\fah_error_log.txt
    macOS:   ~/Library/Application Support/fahrpc/fah_error_log.txt
    Linux:   ~/.config/fahrpc/fah_error_log.txt

Example usage:
    >>> from fahrpc.logger import setup_error_logging
    >>> logger = setup_error_logging("/path/to/logfile.txt")
    >>> logger.info("Application started")
    >>> logger.error("Something went wrong", exc_info=True)
"""

import logging
import sys
import time
import traceback
from logging.handlers import RotatingFileHandler

from fahrpc.config import APP_NAME


class ModuleContextFormatter(logging.Formatter):
    """Custom formatter that includes module context and enhanced error details."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with module context, timestamps, and stack traces."""
        # Use the record's built-in attributes for accurate caller info
        # These are captured by the logging module at the point of the log call
        module_name = record.module if record.module else record.name
        function_name = record.funcName
        line_number = record.lineno

        # Format timestamp
        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(record.created))

        # Build base message
        level_name = record.levelname
        message = record.getMessage()

        # Build the log line with module context
        log_line = (
            f"{timestamp} [{level_name:8s}] {module_name}.{function_name}():"
            f"{line_number} - {message}"
        )

        # Add exception info with full traceback if present
        if record.exc_info:
            exc_type, exc_value, exc_tb = record.exc_info
            if exc_tb:
                log_line += f"\n[EXCEPTION] {exc_type.__name__}: {exc_value}"
                log_line += "\n[STACK TRACE]:\n"
                log_line += "".join(traceback.format_tb(exc_tb))

        return log_line


class TimestampedFileWriter:
    """Wrapper that adds timestamps to error log entries."""

    def __init__(self, file: object, suppress_warnings: bool = True) -> None:
        self.file = file
        self.at_line_start = True
        self.suppressing = False
        self.suppress_lines_remaining = 0
        self.suppress_warnings = suppress_warnings

        self.suppress_keywords = [
            "I/O operation on closed pipe",
            "_ProactorBasePipeTransport",
            "proactor_events.py",
            "windows_utils.py",
            "unclosed transport",
            "ResourceWarning",
            "deallocator",
            "__del__",
            "_sock.fileno()"
        ]

    def write(self, text: str) -> None:
        if text:
            # Check if we should suppress this text
            if self.suppress_warnings:
                if any(keyword in text for keyword in self.suppress_keywords):
                    self.suppressing = True
                    self.suppress_lines_remaining = 15
                    return

                if self.suppressing:
                    self.suppress_lines_remaining -= 1
                    if self.suppress_lines_remaining <= 0:
                        self.suppressing = False
                    return

            # Write with timestamps
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line or (i < len(lines) - 1):
                    if self.at_line_start and line:
                        timestamp = time.strftime('[%Y-%m-%d %H:%M:%S] ')
                        self.file.write(timestamp + line)
                        self.at_line_start = False
                    else:
                        self.file.write(line)

                    if i < len(lines) - 1:
                        self.file.write('\n')
                        self.at_line_start = True
            self.file.flush()

    def flush(self) -> None:
        """Flush the file buffer."""
        self.file.flush()

def setup_error_logging(log_file: str, suppress_warnings: bool = True) -> logging.Logger:
    """
    Set up enhanced error logging with module context, timestamps, and stack traces.

    Features:
    - Timestamps on all log entries
    - Module and function context (module.function():line_number)
    - Full exception stack traces for errors
    - Log level indicators (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Rotating file handler (10MB per file, keeps 5 backups)
    - Separate stderr capture with timestamps
    - Asyncio warning suppression (optional)

    Args:
        log_file: Path to the log file
        suppress_warnings: Whether to suppress asyncio warnings (default: True)

    Returns:
        Configured logger instance
    """
    # Capture stderr with timestamps
    # Note: File handle is stored in TimestampedFileWriter for proper lifecycle management
    stderr_file = open(log_file, "a")
    sys.stderr = TimestampedFileWriter(
        stderr_file,
        suppress_warnings=suppress_warnings
    )

    # Create main logger instance
    logger = logging.getLogger(APP_NAME.upper())
    logger.setLevel(logging.DEBUG)

    # Create rotating file handler (10MB max, 5 backup files)
    handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
    handler.setLevel(logging.DEBUG)

    # Apply custom formatter with module context and stack traces
    formatter = ModuleContextFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Also add a console handler for critical errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Log startup message with metadata
    logger.info("=" * 80)
    logger.info("FAHRPC Logging Initialized")
    logger.info("=" * 80)
    logger.debug(f"Log file: {log_file}")
    logger.debug("Max file size: 10 MB with 5 backups")
    logger.debug("Log level: DEBUG (all messages captured)")
    logger.info("=" * 80)

    return logger
