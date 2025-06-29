import os
from pathlib import Path

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