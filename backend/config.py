import os
import secrets
from datetime import timedelta

class Config:
    """Application configuration with secure defaults"""
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_HOURS', '1')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_DAYS', '7')))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'lagerverwaltung.db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Server Configuration
    DEBUG = os.getenv('FLASK_ENV', 'production') == 'development'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    @classmethod
    def get_config(cls):
        """Get configuration instance"""
        return cls()
    
    def __repr__(self):
        return f"<Config DEBUG={self.DEBUG} PORT={self.PORT}>"

# Environment-specific configurations
class DevelopmentConfig(Config):
    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Longer for development

class ProductionConfig(Config):
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # Shorter for production

class TestConfig(Config):
    DEBUG = True
    DATABASE_URL = ':memory:'  # In-memory database for tests
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)

# Configuration factory
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentConfig()
    elif env == 'testing':
        return TestConfig()
    else:
        return ProductionConfig()