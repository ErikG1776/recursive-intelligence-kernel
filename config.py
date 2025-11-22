"""
config.py | Recursive Intelligence Algorithm (RIA) v5.0
--------------------------------------------------------
Centralized configuration for database paths, constants, and settings.
"""

import os
import logging
from pathlib import Path

# ==========================================================
# === Project Paths ========================================
# ==========================================================
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "memory.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# ==========================================================
# === Database Settings ====================================
# ==========================================================
DB_TIMEOUT = 30
DB_ISOLATION_LEVEL = None  # Manual transaction control

# ==========================================================
# === Algorithm Parameters =================================
# ==========================================================
DBSCAN_EPS = 0.7
DBSCAN_MIN_SAMPLES = 2
TFIDF_SIM_THRESHOLD = 0.7
DEFAULT_TASK_TIMEOUT = 30

# ==========================================================
# === Logging Configuration ================================
# ==========================================================
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = os.environ.get("RIK_LOG_LEVEL", "INFO")

def setup_logging(name: str = "rik") -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    return logger

# ==========================================================
# === API Settings =========================================
# ==========================================================
API_HOST = os.environ.get("RIK_API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("RIK_API_PORT", "8000"))
