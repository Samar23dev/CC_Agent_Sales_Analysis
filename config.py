"""
GroMo AI Sales Coach - Configuration Settings

This module contains configuration settings for the application.
It supports different environments (development, testing, production)
and loads environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Base configuration."""
    
    # API settings
    API_VERSION = '1.0.0'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-gromo-ai-coach')
    DEBUG = False
    TESTING = False
    
    # Database settings
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.environ.get('DB_NAME', 'gromo_ai_coach')
    
    # Model settings
    MODEL_DIR = os.environ.get('MODEL_DIR', 'models')
    
    # Output settings
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
    
    # Flask-specific settings
    SESSION_TYPE = 'filesystem'
    CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use test database
    DB_NAME = 'gromo_ai_coach_test'


class ProductionConfig(Config):
    """Production configuration."""
    # Ensure SECRET_KEY is set in environment for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Set production database URI
    MONGODB_URI = os.environ.get('MONGODB_URI')
    DB_NAME = os.environ.get('DB_NAME', 'gromo_ai_coach_prod')
    
    # Set model directory
    MODEL_DIR = os.environ.get('MODEL_DIR', '/app/models')
    
    # Set output directory
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', '/app/output')


# Select config based on environment
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Set default configuration to development
env = os.environ.get('FLASK_ENV', 'development')
Config = config_map.get(env, DevelopmentConfig)
