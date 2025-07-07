from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize config-specific settings
    config_class.init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from .api import user_routes, document_routes, export_routes, template_routes, ocr_routes, enum_routes
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(document_routes.bp)
    app.register_blueprint(export_routes.bp)
    app.register_blueprint(template_routes.bp)
    app.register_blueprint(ocr_routes.bp)
    app.register_blueprint(enum_routes.bp)
    
    # Create database tables on first request
    with app.app_context():
        db.create_all()
    
    return app 