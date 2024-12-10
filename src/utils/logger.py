"""Logging utilities for SEO data collector."""
import logging
import os
from typing import Optional

def setup_logger(
    name: str,
    level: str = "INFO",
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Set up logger with specified configuration.
    
    Args:
        name: Logger name
        level: Logging level
        log_format: Log message format
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        # Create log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
