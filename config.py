"""
config.py — CricketZone Configuration
Loads all settings from .env file using python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

    # Database — stored in /instance/ folder (not committed to git)
    DATABASE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "instance", "back.db"
    )

    # Flask-Mail
    MAIL_SERVER         = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT           = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS        = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME       = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD       = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "")

    # Admin credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "cricketzone@2026")


class DevelopmentConfig(Config):
    DEBUG   = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG   = False
    TESTING = False


class TestingConfig(Config):
    DEBUG    = False
    TESTING  = True
    DATABASE = ":memory:"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_map.get(env, DevelopmentConfig)