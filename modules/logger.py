import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logger(name):
    """Create logger with console and file handlers."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        c_handler = logging.StreamHandler()
        c_handler.setFormatter(formatter)
        logger.addHandler(c_handler)
        
        # File handler with rotation (max 5MB, keep 3 backups)
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            f_handler = RotatingFileHandler(
                LOG_FILE, 
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            f_handler.setFormatter(formatter)
            logger.addHandler(f_handler)
        except (OSError, IOError) as e:
            # If file logging fails, at least keep console logging
            print(f"Warning: Could not setup file logging: {e}")
        
    return logger

# Default logger instance
logger = setup_logger("FinancePerso")
