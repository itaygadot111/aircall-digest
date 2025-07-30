"""
Logging configuration for the AI Competitive Intelligence Agent
"""

import logging
import sys
from datetime import datetime

def setup_logger(name: str = "ai_agent", verbose: bool = False):
    """Setup and configure logger"""
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create file handler
    file_handler = logging.FileHandler(f"agent_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger