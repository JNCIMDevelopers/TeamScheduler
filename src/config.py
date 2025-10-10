"""
Configuration settings for the Team Scheduler application.
"""

import os


class Settings:
    """Application settings and configuration."""

    # API Configuration
    API_TITLE = "Team Scheduler API"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = "REST API for church team scheduling system"

    # Server Configuration
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # Database Configuration (for future use)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./team_scheduler.db")

    # Scheduling Configuration
    DEFAULT_CONSECUTIVE_ASSIGNMENT_LIMIT = 3
    DEFAULT_ROLE_TIME_WINDOWS = {
        "WORSHIP_LEADER": 4,  # weeks
        "SUNDAY_SCHOOL_TEACHER": 6,
        "EMCEE": 3,
    }

    # Worship Leader Rotation (can be overridden via API)
    DEFAULT_WORSHIP_LEADER_ROTATION = ["Gee", "John", "Sarah", "Michael"]

    # CORS Settings
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Global settings instance
settings = Settings()
