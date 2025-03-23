import os
from datetime import timedelta

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = False
    TESTING = False

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///marketplace.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # Logging configuration (disabled for privacy)
    LOGGING_ENABLED = False

    # Bcrypt configuration
    BCRYPT_LOG_ROUNDS = 12  # Higher is more secure but slower

    # Onion service configuration
    PREFERRED_URL_SCHEME = 'http'  # would be set to 'http' for Tor hidden service
    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_marketplace.db'
    LOGGING_ENABLED = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    BCRYPT_LOG_ROUNDS = 4  # Lower for faster tests

class ProductionConfig(Config):
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/marketplace'

    # Enhanced security settings
    BCRYPT_LOG_ROUNDS = 14  # Higher for production

    # Tor/Onion specific settings
    SERVER_NAME = os.environ.get('ONION_ADDRESS')  # Example: 'abcdefghijklmnop.onion'

# Configuration selection
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
