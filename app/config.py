"""
=== app/config.py ===
Application configuration.

Laravel equivalent: The config/ directory (config/app.php, config/database.php, etc.)
Plus the .env file loading (which Laravel does automatically via Dotenv).
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load .env file — Laravel does this automatically, Flask needs this line.
load_dotenv()


class Config:
    """
    Configuration class. Each attribute becomes a config value.

    Laravel equivalent of accessing config:
      Laravel:  config('app.key')        → Flask: app.config['SECRET_KEY']
      Laravel:  env('DB_CONNECTION')      → Flask: os.environ.get('DATABASE_URL')
    """

    # ── App Settings ──────────────────────────────────────────────
    # SECRET_KEY is like APP_KEY in Laravel — used for session encryption etc.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')

    # ── Database Settings ─────────────────────────────────────────
    # Laravel: DB_CONNECTION=sqlite in .env + config/database.php
    # Flask-SQLAlchemy uses a single connection string instead.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

    # Disable a feature that wastes memory (not needed)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT Settings ──────────────────────────────────────────────
    # Laravel Sanctum/Passport token config equivalent
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-jwt-secret')

    # Token expires in 1 hour (like token expiration in Sanctum)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
