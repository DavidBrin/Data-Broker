"""
Main Flask application initialization and configuration.
Sets up database, routes, and middleware.
"""
from flask import Flask
from flask_cors import CORS
from config import get_config
from models import db
from routes import (
    auth_routes,
    dataset_routes,
    refinement_routes,
    package_routes,
    marketplace_routes,
)


def create_app(config_name: str = None):
    """
    Application factory function.
    Creates and configures the Flask application.
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS for frontend
    
    # Create database tables within app context
    with app.app_context():
        db.create_all()
    
    # Register blueprints (route modules)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(dataset_routes.bp)
    app.register_blueprint(refinement_routes.bp)
    app.register_blueprint(package_routes.bp)
    app.register_blueprint(marketplace_routes.bp)
    
    # Add root endpoint
    @app.route('/')
    def index():
        return {
            'name': 'Data Broker API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'datasets': '/api/datasets',
                'refinement': '/api/refinement',
                'packages': '/api/packages',
                'marketplace': '/api/marketplace',
            }
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
