"""
Logging configuration
"""

import logging
import logging.handlers
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    JSON log formatter for structured logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)


def setup_logging():
    """
    Configure application logging
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    if settings.LOG_JSON:
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    
    if settings.LOG_JSON:
        file_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(f"Logging configured: level={settings.LOG_LEVEL}, json={settings.LOG_JSON}")


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class RequestIDFilter(logging.Filter):
    """
    Add request ID to log records
    """
    
    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add request_id to record
        """
        record.request_id = self.request_id or "N/A"
        return True


class UserIDFilter(logging.Filter):
    """
    Add user ID to log records
    """
    
    def __init__(self, user_id: Optional[int] = None):
        super().__init__()
        self.user_id = user_id
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add user_id to record
        """
        record.user_id = self.user_id or "N/A"
        return True


# Export
__all__ = [
    "setup_logging",
    "get_logger",
    "JSONFormatter",
    "RequestIDFilter",
    "UserIDFilter",
]

