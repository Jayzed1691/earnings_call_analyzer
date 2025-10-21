"""
Logging configuration for Earnings Call Analyzer

Provides structured logging with:
- Console output for development
- File rotation for production
- Different log levels
- Performance tracking
"""
import logging
import logging.handlers
from pathlib import Path
from config.settings import settings


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    console_output: bool = True
) -> None:
    """
    Configure application-wide logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional, defaults to data/logs/analyzer.log)
        console_output: Whether to output to console (default: True)
    """
    # Determine log level
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory
    log_dir = settings.DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Default log file
    if log_file is None:
        log_file = log_dir / "analyzer.log"
    else:
        log_file = Path(log_file)

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(
            detailed_formatter if settings.DEBUG_MODE else simple_formatter
        )
        root_logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Set lower log level for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

    # Log startup message
    root_logger.info("="*80)
    root_logger.info("Earnings Call Analyzer - Logging Initialized")
    root_logger.info(f"Log Level: {level}")
    root_logger.info(f"Log File: {log_file}")
    root_logger.info("="*80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """
    Context manager for logging performance metrics

    Usage:
        with PerformanceLogger("sentiment_analysis"):
            # ... code to measure ...
            pass
    """

    def __init__(self, operation: str, logger: logging.Logger = None):
        """
        Initialize performance logger

        Args:
            operation: Name of operation being measured
            logger: Logger to use (default: root logger)
        """
        self.operation = operation
        self.logger = logger or logging.getLogger()
        self.start_time = None

    def __enter__(self):
        """Start timing"""
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration"""
        import time
        duration = time.time() - self.start_time

        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} in {duration:.2f}s")
        else:
            self.logger.error(
                f"Failed: {self.operation} after {duration:.2f}s - {exc_val}"
            )

        return False  # Don't suppress exceptions
