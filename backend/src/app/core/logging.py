import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Path for the log file
LOG_FILE_PATH = LOG_DIR / "app.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Default logging level (Debug, Info, Warning, Error, Critical)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout), # Console output
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"), # File output
    ],
)

# Export logger instance
logger = logging.getLogger(__name__)