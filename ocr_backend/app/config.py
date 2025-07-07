import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # SQLite database configuration
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/ocr_platform.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Upload folder for documents
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    
    # Maximum file size (16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'ocr_platform.log')
    
    # OCR configuration
    DEFAULT_OCR_CONFIDENCE = 0.8
    MAX_RETRY_ATTEMPTS = 3
    
    # Gemini API configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config-specific settings"""
        # Create upload directory if it doesn't exist
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(app.config['LOG_FILE']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if app.config['LOG_FILE']:
                file_handler = RotatingFileHandler(
                    app.config['LOG_FILE'], 
                    maxBytes=10240000, 
                    backupCount=10
                )
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
                
            app.logger.setLevel(logging.INFO)
            app.logger.info('OCR Platform startup') 