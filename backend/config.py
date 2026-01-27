"""
Configuration module for the Data Broker application.
Handles environment setup, database connection, and application settings.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 * 1024  # 5GB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'json', 'xml', 'mp3', 'wav', 'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png', 'gif'}
    
    # Refinement pipeline settings
    QUALITY_SCORE_THRESHOLD = 0.5  # Minimum quality score (0-1)
    DEDUPLICATION_SIMILARITY_THRESHOLD = 0.95
    
    # Storage settings - NOTE: These are placeholders for cloud integration
    # In production, integrate with AWS S3, Google Cloud Storage, or Azure Blob Storage
    COLD_STORAGE_PATH = os.environ.get('COLD_STORAGE_PATH') or 'cold_storage'
    USE_CLOUD_STORAGE = os.environ.get('USE_CLOUD_STORAGE', 'false').lower() == 'true'
    
    # Cloud storage configuration (AWS S3 example)
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///data_broker.db'


class ProductionConfig(Config):
    """Production configuration with security settings."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/data_broker'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary for easy switching
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the appropriate config class based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
