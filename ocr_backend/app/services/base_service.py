from abc import ABC
from .. import db
from flask import current_app

class BaseService(ABC):
    """Base service class with common functionality"""
    
    @staticmethod
    def commit_or_rollback():
        """Safely commit or rollback database changes"""
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return False
    
    @staticmethod
    def log_error(message, exception=None):
        """Centralized error logging"""
        if exception:
            current_app.logger.error(f"{message}: {str(exception)}")
        else:
            current_app.logger.error(message)
    
    @staticmethod
    def log_info(message):
        """Centralized info logging"""
        current_app.logger.info(message)
