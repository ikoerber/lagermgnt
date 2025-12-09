import logging
import os
from datetime import datetime

def setup_logger(name: str = 'lagerverwaltung', level: str = 'INFO') -> logging.Logger:
    """
    Konfiguriert strukturiertes Logging für die Lagerverwaltung
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Log-Level aus Environment Variable oder Parameter
    log_level = os.getenv('LOG_LEVEL', level).upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Formatter für strukturierte Logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler für Logs
    log_dir = os.getenv('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'lagerverwaltung_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error File Handler für kritische Fehler
    error_handler = logging.FileHandler(
        os.path.join(log_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info(f"Logger '{name}' erfolgreich konfiguriert mit Level {log_level}")
    return logger

# Standard Logger für die Anwendung
app_logger = setup_logger()