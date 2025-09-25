# HandlerLogGuru.py
from loguru import logger
import sys
import os

# Remove default Loguru handlers
logger.remove()

# Define log directory
log_directory = "logs"

# Create the log directory if it does not exist
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Define log formats based on environment
if not os.getenv("DEBUG", "False") == "True":
    log_format_general = (
        "{time:YYYY-MM-DD HH:mm:ss} {level} | {message} | {name}:{line} | {function}"
    )
    log_format_debug = (
        "<green>{level}</green>:\t  {message} | {name}:{line} | <cyan>{function}</cyan>"
    )
    log_file_path = os.path.join(log_directory, "{time}.log")
else:
    log_format_general = (
        "{time:YYYY-MM-DD HH:mm:ss} {level} | {message} | {name}:{line} | {function}"
    )
    log_format_debug = "<green>{level}</green>:\t  {message} | {file.path}:{line} | <cyan>{function}</cyan>"
    log_file_path = os.path.join(log_directory, "dev.log")


# Django-compatible LOGGING configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "intercept": {
            "class": "core.log_handler.InterceptHandler",  # Reference the handler correctly
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["intercept"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

logger.remove()


# Add file logger with detailed configuration
logger.add(
    log_file_path,
    rotation="20 MB",
    retention="3 months",
    format=log_format_general,
    colorize=False,
    backtrace=True,
    diagnose=True,
    level="DEBUG",
    compression="zip",
)

# Add console logger
logger.add(
    sys.stdout,
    level="DEBUG",
    format=log_format_debug,
    colorize=True,  # Enable color output in the terminal
)

# Custom logging level
logger.level("TL", no=38, color="<cyan>", icon="🔧")

# Initialize Loguru
logger.info("Loguru Initialized......")
