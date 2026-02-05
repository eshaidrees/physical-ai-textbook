import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
import json
import os
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format for better monitoring
    """
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'conversation_id'):
            log_entry['conversation_id'] = record.conversation_id

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging with both console and file handlers
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Create formatters
    detailed_formatter = CustomFormatter()
    simple_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (with rotation)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    # Set specific log levels for third-party libraries to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("qdrant_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger
    """
    return logging.getLogger(name)


class LogMetadata:
    """
    Context manager for adding metadata to logs
    """
    def __init__(self, **kwargs):
        self.metadata = kwargs
        self.logger = logging.getLogger()

    def __enter__(self):
        # Add metadata to the logger context
        for key, value in self.metadata.items():
            setattr(self.logger, key, value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove metadata from the logger context
        for key in self.metadata.keys():
            if hasattr(self.logger, key):
                delattr(self.logger, key)


# Global logger instance
app_logger = setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_file=os.getenv('LOG_FILE', 'logs/app.log')
)


def log_api_call(endpoint: str, method: str, response_time: float, status_code: int, user_id: Optional[str] = None):
    """
    Log API calls with relevant metadata
    """
    extra = {
        'endpoint': endpoint,
        'method': method,
        'response_time': response_time,
        'status_code': status_code
    }

    if user_id:
        extra['user_id'] = user_id

    app_logger.info(f"API call to {endpoint}", extra=extra)


def log_search_query(query: str, results_count: int, response_time: float, conversation_id: Optional[str] = None):
    """
    Log search queries with relevant metadata
    """
    extra = {
        'query_length': len(query),
        'results_count': results_count,
        'response_time': response_time
    }

    if conversation_id:
        extra['conversation_id'] = conversation_id

    app_logger.info(f"Search query: {query[:50]}...", extra=extra)


def log_error(error: Exception, context: str = ""):
    """
    Log errors with context
    """
    app_logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_performance(event: str, duration: float, **kwargs):
    """
    Log performance metrics
    """
    extra = {
        'event': event,
        'duration': duration,
        **kwargs
    }

    app_logger.info(f"Performance: {event}", extra=extra)


# Set up default log directory
os.makedirs('logs', exist_ok=True)