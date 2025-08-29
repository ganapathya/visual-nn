"""
Configuration settings for Visual Neural Network application.
"""

import os

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5001))
    
    # Image processing settings
    MAX_IMAGE_SIZE = 1024 * 1024 * 5  # 5MB max image size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Development settings
    AUTO_RELOAD = DEBUG

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    AUTO_RELOAD = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    AUTO_RELOAD = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Ensure secret key is set in production
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
