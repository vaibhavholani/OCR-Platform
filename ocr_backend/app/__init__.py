from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import inspect, text
import secrets
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
    from .api import user_routes, document_routes, export_routes, template_routes, ocr_routes, enum_routes, tally_routes, credit_routes
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(document_routes.bp)
    app.register_blueprint(export_routes.bp)
    app.register_blueprint(template_routes.bp)
    app.register_blueprint(ocr_routes.bp)
    app.register_blueprint(enum_routes.bp)
    app.register_blueprint(tally_routes.bp)
    app.register_blueprint(credit_routes.credit_bp)
    
    # Create database tables and handle migrations on first request
    with app.app_context():
        db.create_all()
        # Auto-migrate credit system fields
        try:
            inspector = inspect(db.engine)
            if inspector.has_table('users'):
                columns = {col['name'] for col in inspector.get_columns('users')}
                
                # Add credit system fields if they don't exist
                if 'credits_remaining' not in columns:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN credits_remaining INTEGER DEFAULT 10 NOT NULL'))
                    app.logger.info("Added credits_remaining column to users table")
                
                if 'plan_type' not in columns:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN plan_type VARCHAR(20) DEFAULT "free" NOT NULL'))
                    app.logger.info("Added plan_type column to users table")
                
                db.session.commit()
                
                # Initialize credit values for existing users without credits
                from .models import User
                users_without_credits = User.query.filter(
                    (User.credits_remaining == None) | (User.credits_remaining < 0)
                ).all()
                
                for user in users_without_credits:
                    user.credits_remaining = 10  # Default free credits
                    user.plan_type = 'free'
                
                if users_without_credits:
                    db.session.commit()
                    app.logger.info(f"Initialized credits for {len(users_without_credits)} existing users")
                    
        except Exception as e:
            # Avoid crashing the app if migration fails; continue startup
            app.logger.error(f"Error during credit system migration: {e}")
            db.session.rollback()
    
    return app 