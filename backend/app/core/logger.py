import sys
import json
from loguru import logger
from ..core.config import settings

class InterceptHandler:
    """Intercept standard logging messages to Loguru"""
    def write(self, message):
        if message.strip() != "\n":
            logger.debug(message.strip())
    
    def flush(self):
        pass

# Configure loguru
logger.remove()

# Add console logging
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Optionally add file logging in production
if settings.ENVIRONMENT == "production":
    logger.add(
        "logs/app.log",
        rotation="100 MB",
        retention="30 days",
        level=settings.LOG_LEVEL,
        enqueue=True,
        compression="zip"
    )

# Intercept standard logging
import logging
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
