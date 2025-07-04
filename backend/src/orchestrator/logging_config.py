# orchestrator/logging_config.py
import logging
import sys
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Format the message
        return super().format(record)


def setup_logging(
    service_name: str = "orchestrator",
    log_level: str = "INFO",
    include_timestamps: bool = True,
    include_module: bool = True
) -> logging.Logger:
    """
    Set up comprehensive logging for the service
    
    Args:
        service_name: Name of the service (e.g., "orchestrator", "worker")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        include_timestamps: Whether to include timestamps in log messages
        include_module: Whether to include module names in log messages
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)
    
    # Create formatter
    format_parts = []
    if include_timestamps:
        format_parts.append("%(asctime)s")
    
    format_parts.extend([
        "[%(levelname)s]",
        f"[{service_name.upper()}]"
    ])
    
    if include_module:
        format_parts.append("%(name)s")
    
    format_parts.append("%(message)s")
    
    format_string = " - ".join(format_parts)
    formatter = ColoredFormatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def create_job_logger(job_id: int, base_logger: Optional[logging.Logger] = None) -> logging.Logger:
    """
    Create a job-specific logger that includes job ID in all messages
    
    Args:
        job_id: The job ID to include in log messages
        base_logger: Base logger to derive from (optional)
    
    Returns:
        Job-specific logger
    """
    logger_name = f"job_{job_id}"
    job_logger = logging.getLogger(logger_name)
    
    if base_logger:
        job_logger.setLevel(base_logger.level)
        
        # Copy handlers from base logger
        for handler in base_logger.handlers:
            job_logger.addHandler(handler)
    else:
        job_logger = setup_logging(f"job_{job_id}")
    
    return job_logger


# Create module-level loggers
orchestrator_logger = setup_logging("orchestrator", log_level="DEBUG")
worker_logger = setup_logging("worker", log_level="DEBUG")
progress_logger = setup_logging("progress", log_level="DEBUG")
websocket_logger = setup_logging("websocket", log_level="DEBUG")