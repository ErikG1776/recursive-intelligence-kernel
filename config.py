"""
RIK Configuration Management
============================

Centralized configuration for production deployment.
Uses environment variables with sensible defaults.

Usage:
    from config import config

    print(config.DATABASE_URL)
    print(config.AUTO_APPROVE_THRESHOLD)
"""

import os
from typing import List, Optional
from pathlib import Path


class Config:
    """
    Centralized configuration management for RIK.

    All settings can be overridden via environment variables.
    Supports different environments: development, staging, production
    """

    # ============================================================================
    # ENVIRONMENT
    # ============================================================================

    ENVIRONMENT = os.getenv("RIK_ENV", "development")  # development, staging, production
    DEBUG = os.getenv("RIK_DEBUG", "false").lower() == "true"

    # ============================================================================
    # API SERVER
    # ============================================================================

    API_HOST = os.getenv("RIK_API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("RIK_API_PORT", "8000"))
    API_WORKERS = int(os.getenv("RIK_API_WORKERS", "1"))
    # Auto-reload: only enabled in development by default
    API_RELOAD = os.getenv("RIK_API_RELOAD", "true" if Config.ENVIRONMENT == "development" else "false").lower() == "true"

    # API metadata
    API_TITLE = "RIK - Recursive Intelligence Kernel"
    API_VERSION = "5.4.0"
    API_DESCRIPTION = """
## Intelligent Automation with Explainable AI

RIK handles exceptions that break traditional RPA through contextual reasoning
and episodic memory.

### Key Features:
- Exception diagnosis and resolution
- Episodic memory (learns from past cases)
- Explainable decisions (full audit trail)
- 92% automation rate vs 60% traditional RPA

### Use Cases:
- Invoice processing with missing data
- Web scraper selector recovery
- Any RPA workflow with exceptions
    """

    # ============================================================================
    # DATABASE
    # ============================================================================

    DATABASE_URL = os.getenv("RIK_DATABASE_URL", "sqlite:///data/memory.db")
    DATABASE_POOL_SIZE = int(os.getenv("RIK_DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("RIK_DATABASE_MAX_OVERFLOW", "10"))

    # Database backup
    DATABASE_BACKUP_ENABLED = os.getenv("RIK_DATABASE_BACKUP_ENABLED", "false").lower() == "true"
    DATABASE_BACKUP_INTERVAL_HOURS = int(os.getenv("RIK_DATABASE_BACKUP_INTERVAL_HOURS", "24"))

    # ============================================================================
    # SECURITY
    # ============================================================================

    # API Key Authentication
    API_KEY_ENABLED = os.getenv("RIK_API_KEY_ENABLED", "false").lower() == "true"
    API_KEYS = [k.strip() for k in os.getenv("RIK_API_KEYS", "").split(",") if k.strip()]

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RIK_RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS = int(os.getenv("RIK_RATE_LIMIT_REQUESTS", "100"))  # requests
    RATE_LIMIT_PERIOD = int(os.getenv("RIK_RATE_LIMIT_PERIOD", "60"))  # seconds

    # CORS
    CORS_ENABLED = os.getenv("RIK_CORS_ENABLED", "true").lower() == "true"
    CORS_ORIGINS = [o.strip() for o in os.getenv("RIK_CORS_ORIGINS", "*").split(",")]

    # ============================================================================
    # BUSINESS RULES - INVOICE PROCESSING
    # ============================================================================

    # Amount thresholds
    AUTO_APPROVE_THRESHOLD = float(os.getenv("RIK_AUTO_APPROVE_THRESHOLD", "5000.0"))
    REQUIRE_PO_OVER = float(os.getenv("RIK_REQUIRE_PO_OVER", "10000.0"))

    # Trusted vendors (comma-separated list)
    TRUSTED_VENDORS = [
        v.strip() for v in os.getenv(
            "RIK_TRUSTED_VENDORS",
            "Acme Corporation,Microsoft Corporation,Amazon Web Services,Google LLC,Salesforce Inc"
        ).split(",") if v.strip()
    ]

    # Vendor similarity matching
    VENDOR_SIMILARITY_THRESHOLD = float(os.getenv("RIK_VENDOR_SIMILARITY_THRESHOLD", "0.85"))

    # ============================================================================
    # LOGGING
    # ============================================================================

    LOG_LEVEL = os.getenv("RIK_LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = os.getenv("RIK_LOG_FORMAT", "json")  # json or text
    LOG_FILE = os.getenv("RIK_LOG_FILE", "logs/rik.log")
    LOG_FILE_ENABLED = os.getenv("RIK_LOG_FILE_ENABLED", "false").lower() == "true"
    LOG_FILE_MAX_BYTES = int(os.getenv("RIK_LOG_FILE_MAX_BYTES", "10485760"))  # 10MB
    LOG_FILE_BACKUP_COUNT = int(os.getenv("RIK_LOG_FILE_BACKUP_COUNT", "5"))

    # ============================================================================
    # MEMORY & REASONING
    # ============================================================================

    # Memory retrieval
    MEMORY_RETRIEVAL_LIMIT = int(os.getenv("RIK_MEMORY_RETRIEVAL_LIMIT", "10"))
    MEMORY_SIMILARITY_THRESHOLD = float(os.getenv("RIK_MEMORY_SIMILARITY_THRESHOLD", "0.3"))

    # Episode consolidation
    MEMORY_CONSOLIDATION_ENABLED = os.getenv("RIK_MEMORY_CONSOLIDATION_ENABLED", "false").lower() == "true"
    MEMORY_CONSOLIDATION_INTERVAL_HOURS = int(os.getenv("RIK_MEMORY_CONSOLIDATION_INTERVAL_HOURS", "24"))

    # Reasoning confidence thresholds
    REASONING_MIN_CONFIDENCE = float(os.getenv("RIK_REASONING_MIN_CONFIDENCE", "0.7"))
    REASONING_AUTO_APPROVE_CONFIDENCE = float(os.getenv("RIK_REASONING_AUTO_APPROVE_CONFIDENCE", "0.8"))

    # ============================================================================
    # MONITORING & METRICS
    # ============================================================================

    METRICS_ENABLED = os.getenv("RIK_METRICS_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_ENABLED = os.getenv("RIK_HEALTH_CHECK_ENABLED", "true").lower() == "true"

    # ============================================================================
    # PATHS
    # ============================================================================

    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================

    FEATURE_INVOICE_PROCESSING = os.getenv("RIK_FEATURE_INVOICE_PROCESSING", "true").lower() == "true"
    FEATURE_SELECTOR_RECOVERY = os.getenv("RIK_FEATURE_SELECTOR_RECOVERY", "true").lower() == "true"
    FEATURE_MEMORY_LEARNING = os.getenv("RIK_FEATURE_MEMORY_LEARNING", "true").lower() == "true"

    # ============================================================================
    # VALIDATION
    # ============================================================================

    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        errors = []

        # Check required settings
        if cls.API_KEY_ENABLED and not cls.API_KEYS:
            errors.append("API_KEY_ENABLED is true but no API_KEYS provided")

        if cls.AUTO_APPROVE_THRESHOLD < 0:
            errors.append("AUTO_APPROVE_THRESHOLD must be >= 0")

        if cls.VENDOR_SIMILARITY_THRESHOLD < 0 or cls.VENDOR_SIMILARITY_THRESHOLD > 1:
            errors.append("VENDOR_SIMILARITY_THRESHOLD must be between 0 and 1")

        # Check log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of {valid_log_levels}")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def to_dict(cls, include_secrets: bool = False):
        """
        Export configuration as dictionary.

        Args:
            include_secrets: If True, includes API keys and sensitive data

        Returns:
            Dictionary of configuration values
        """
        config_dict = {}

        for key, value in cls.__dict__.items():
            # Skip private attributes and methods
            if key.startswith("_") or callable(value):
                continue

            # Optionally hide secrets
            if not include_secrets and "KEY" in key.upper():
                config_dict[key] = "***REDACTED***"
            else:
                config_dict[key] = value

        return config_dict

    @classmethod
    def print_config(cls, include_secrets: bool = False):
        """Print current configuration (for debugging)"""
        print("=" * 60)
        print(f"RIK Configuration ({cls.ENVIRONMENT})")
        print("=" * 60)

        config_dict = cls.to_dict(include_secrets=include_secrets)

        for key, value in sorted(config_dict.items()):
            print(f"{key:40s} = {value}")

        print("=" * 60)


# Singleton instance
config = Config()

# Validate configuration on import
if __name__ != "__main__":
    try:
        config.validate()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
        print("Fix your environment variables or .env file")


# CLI for testing configuration
if __name__ == "__main__":
    import sys

    if "--secrets" in sys.argv:
        config.print_config(include_secrets=True)
    else:
        config.print_config(include_secrets=False)
        print("\nTo view API keys, run: python config.py --secrets")
