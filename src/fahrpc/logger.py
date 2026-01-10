"""
Logging module for FAHRPC
Handles timestamped error logging with optional filtering and logging levels
"""

import logging
import sys
import time
from logging.handlers import RotatingFileHandler


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
    Set up timestamped error logging to file with logging levels.

    Args:
        log_file: Path to the log file
        suppress_warnings: Whether to suppress asyncio warnings

    Returns:
        Configured logger instance
    """
    sys.stderr = TimestampedFileWriter(
        open(log_file, "a"),
        suppress_warnings=suppress_warnings
    )

    # Create a logging instance
    logger = logging.getLogger('FAHRPC')
    logger.setLevel(logging.DEBUG)

    # Create rotating file handler
    handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)

    # Create formatter with timestamps
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
