import logging

def setup_logger(name: str):
    """Utility to get standard structured loggers."""
    logger = logging.getLogger(name)
    return logger
