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
    from .api import user_routes, document_routes, export_routes, template_routes, ocr_routes, enum_routes, tally_routes
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(document_routes.bp)
    app.register_blueprint(export_routes.bp)
    app.register_blueprint(template_routes.bp)
    app.register_blueprint(ocr_routes.bp)
    app.register_blueprint(enum_routes.bp)
    app.register_blueprint(tally_routes.bp)
    
    # Create database tables on first request
    with app.app_context():
        db.create_all()
        # Ensure users.api_key column exists and is populated
        try:
            inspector = inspect(db.engine)
            if inspector.has_table('users'):
                columns = {col['name'] for col in inspector.get_columns('users')}
                if 'api_key' not in columns:
                    # Add api_key column
                    db.session.execute(text('ALTER TABLE users ADD COLUMN api_key VARCHAR(32)'))
                    db.session.commit()

                # Backfill api_key values for existing users where NULL or empty
                from .models import User
                existing_keys = set(
                    k for (k,) in db.session.execute(text('SELECT api_key FROM users WHERE api_key IS NOT NULL'))
                )
                users_without_key = User.query.filter((User.api_key == None) | (User.api_key == '')).all()  # noqa: E711
                for user in users_without_key:
                    new_key = secrets.token_hex(16)
                    while new_key in existing_keys:
                        new_key = secrets.token_hex(16)
                    user.api_key = new_key
                    existing_keys.add(new_key)
                if users_without_key:
                    db.session.commit()

                # Ensure a unique index on api_key exists (SQLite compatible)
                existing_indexes = {idx['name'] for idx in inspector.get_indexes('users')}
                desired_index_name = 'ux_users_api_key'
                if desired_index_name not in existing_indexes:
                    try:
                        db.session.execute(text('CREATE UNIQUE INDEX ux_users_api_key ON users (api_key)'))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        except Exception:
            # Avoid crashing the app if introspection/DDL fails; continue startup
            db.session.rollback()
    
    return app 