"""
Configuration file for Global Trust Bank Loan Workflow System
Supports multiple environments: Development, Production, Testing
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings"""
    
    # Application Settings
    APP_NAME = "Global Trust Bank - Loan Workflow System"
    APP_VERSION = "1.0.0"
    
    # Secret Key (change in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Azure Cosmos DB Configuration
    COSMOS_API_BASE_URL = os.environ.get(
        'COSMOS_API_BASE_URL', 
        'https://cosmosdb-api-h3f2fnbth2dccaed.eastus2-01.azurewebsites.net'
    )
    COSMOS_API_TIMEOUT = int(os.environ.get('COSMOS_API_TIMEOUT', 30))
    
    # Flask Settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    DOCUMENTS_FOLDER = 'Documents'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # AI Agent Configuration
    AGENT_PROCESSING_TIMEOUT = int(os.environ.get('AGENT_PROCESSING_TIMEOUT', 60))
    ENABLE_AUTO_PROCESS = os.environ.get('ENABLE_AUTO_PROCESS', 'true').lower() == 'true'
    
    # Application Feature Flags
    ENABLE_COSMOS_INTEGRATION = os.environ.get('ENABLE_COSMOS_INTEGRATION', 'true').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Development Server
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE = False
    
    # Enable detailed logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        print("🔧 Running in DEVELOPMENT mode")


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production Server (Azure Web App)
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 8000))
    
    # Strict security settings
    SESSION_COOKIE_SECURE = True
    
    # Production logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Ensure secret key is set in production
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            import warnings
            warnings.warn("SECRET_KEY is not set! Using default key is insecure.")



# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    return config.get(env, config['default'])
