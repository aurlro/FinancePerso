import logging
import os

# Create logger with standard configuration
def setup_logger(name):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler with formatting
        c_handler = logging.StreamHandler()
        c_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_formatter)
        
        logger.addHandler(c_handler)
        
        # Optional: File handler
        # f_handler = logging.FileHandler('finance_perso.log')
        # f_handler.setFormatter(c_formatter)
        # logger.addHandler(f_handler)
        
    return logger

# Default logger instance
logger = setup_logger("FinancePerso")
