"""Flask application factory"""
from flask import Flask
from pathlib import Path
from app.config import Config


def create_app(config_class=Config):
    """Create and configure Flask application"""
    # Get the project root directory (parent of app/)
    project_root = Path(__file__).parent.parent
    
    # Create Flask app with explicit template and static folders
    app = Flask(
        __name__,
        template_folder=str(project_root / 'templates'),
        static_folder=str(project_root / 'static')
    )
    app.config.from_object(config_class)
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app

