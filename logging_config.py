"""
RIK Logging Configuration
=========================

Professional structured logging for production deployments.

Features:
- JSON-formatted logs (machine-parsable)
- Request ID tracking (trace requests through system)
- Performance timing
- Contextual metadata
- File rotation
- Multiple handlers (console, file)

Usage:
    from logging_config import get_logger

    logger = get_logger(__name__)
    logger.info("Processing invoice", extra={"invoice_id": "INV-123", "amount": 5000})
"""

import logging
import logging.handlers
import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from config import config


# ============================================================================
# STRUCTURED JSON FORMATTER
# ============================================================================

class JSONFormatter(logging.Formatter):
    """
    Format log records as JSON for easy parsing by log aggregators
    (Splunk, DataDog, CloudWatch, etc.)
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Includes:
        - timestamp (ISO 8601)
        - level (INFO, ERROR, etc.)
        - logger name
        - message
        - any extra fields passed via extra={}
        - exception info if present
        """

        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add thread/process info for debugging concurrency issues
        if config.DEBUG:
            log_data["thread_id"] = record.thread
            log_data["thread_name"] = record.threadName
            log_data["process_id"] = record.process

        # Add extra fields (anything passed via extra={})
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.

    Format: [TIMESTAMP] [LEVEL] [logger] message {extra_fields}
    """

    def __init__(self):
        super().__init__(
            fmt="[%(asctime)s] [%(levelname)8s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        """Format with extra fields appended"""
        base_message = super().format(record)

        # Append extra fields if present
        if hasattr(record, "extra_fields") and record.extra_fields:
            extra_str = " ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            base_message += f" {{{extra_str}}}"

        return base_message


# ============================================================================
# CUSTOM LOGGER ADAPTER
# ============================================================================

class StructuredLogger(logging.LoggerAdapter):
    """
    Enhanced logger that automatically captures extra context.

    Adds:
    - Request ID tracking
    - Automatic field extraction from extra={}
    - Performance timing helpers
    """

    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
        self.request_id = None

    def set_request_id(self, request_id: str):
        """Set request ID for tracking across log statements"""
        self.request_id = request_id
        self.extra["request_id"] = request_id

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log call to add extra fields.

        Moves extra={} dict to record for JSON formatter to pick up.
        """
        # Add request ID if set
        if self.request_id:
            if "extra" not in kwargs:
                kwargs["extra"] = {}
            kwargs["extra"]["request_id"] = self.request_id

        # Restructure extra fields for JSON formatter
        if "extra" in kwargs:
            extra_fields = kwargs["extra"].copy()
            # Create custom attribute that JSON formatter will use
            kwargs["extra"] = {"extra_fields": extra_fields}

        return msg, kwargs


# ============================================================================
# LOGGER FACTORY
# ============================================================================

def setup_logging():
    """
    Configure root logger with handlers based on config.

    Called once at application startup.
    """

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))

    # Clear any existing handlers
    root_logger.handlers = []

    # Choose formatter based on config
    if config.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    root_logger.addHandler(console_handler)

    # File handler (optional, for production)
    if config.LOG_FILE_ENABLED:
        # Ensure log directory exists
        config.LOGS_DIR.mkdir(exist_ok=True)

        # Rotating file handler (prevents disk fill)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.LOG_FILE,
            maxBytes=config.LOG_FILE_MAX_BYTES,
            backupCount=config.LOG_FILE_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        root_logger.addHandler(file_handler)

    # Log startup message
    logger = get_logger("rik.startup")
    logger.info(
        f"Logging configured",
        extra={
            "environment": config.ENVIRONMENT,
            "log_level": config.LOG_LEVEL,
            "log_format": config.LOG_FORMAT,
            "log_file_enabled": config.LOG_FILE_ENABLED,
        }
    )


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Processing invoice", extra={"invoice_id": "INV-123"})

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger)


# ============================================================================
# PERFORMANCE TIMING HELPER
# ============================================================================

class LogTimer:
    """
    Context manager for logging operation duration.

    Usage:
        with LogTimer(logger, "Processing invoice", invoice_id="INV-123"):
            # ... do work ...
            pass

        # Logs: "Processing invoice completed in 0.045s"
    """

    def __init__(self, logger: StructuredLogger, operation: str, **extra):
        self.logger = logger
        self.operation = operation
        self.extra = extra
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"{self.operation} started", extra=self.extra)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        log_extra = {**self.extra, "duration_seconds": duration}

        if exc_type is None:
            self.logger.info(
                f"{self.operation} completed",
                extra=log_extra
            )
        else:
            self.logger.error(
                f"{self.operation} failed",
                extra=log_extra,
                exc_info=(exc_type, exc_val, exc_tb)
            )


# ============================================================================
# REQUEST ID MIDDLEWARE (for FastAPI)
# ============================================================================

def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return str(uuid.uuid4())


# ============================================================================
# INITIALIZATION
# ============================================================================

# Set up logging on module import
setup_logging()


# ============================================================================
# CLI for testing logging
# ============================================================================

if __name__ == "__main__":
    # Test logger
    logger = get_logger("rik.test")

    logger.debug("This is a debug message")
    logger.info("Processing started", extra={"invoice_id": "INV-123", "amount": 5000})
    logger.warning("Amount over threshold", extra={"amount": 15000, "threshold": 10000})

    # Test timing
    import time
    with LogTimer(logger, "Expensive operation", operation_type="database_query"):
        time.sleep(0.1)  # Simulate work

    # Test error logging
    try:
        raise ValueError("Something went wrong!")
    except ValueError:
        logger.error("Error occurred", exc_info=True, extra={"context": "test"})

    print("\n✅ Logging test complete. Check output above.")
    print(f"   Log format: {config.LOG_FORMAT}")
    print(f"   Log level: {config.LOG_LEVEL}")
    if config.LOG_FILE_ENABLED:
        print(f"   Log file: {config.LOG_FILE}")
