"""
GroMo AI Sales Coach - Flask Application Entry Point

This module initializes the Flask application and registers the API routes.
It serves as the main entry point for the GroMo AI Sales Coach API.

The API allows GroMo app developers to integrate AI-powered sales coaching
features directly into the GroMo app, helping agents maximize their performance
and earnings.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from api.routes import register_routes
from config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register API routes
    register_routes(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'The requested resource was not found',
            'code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'message': 'An internal server error occurred',
            'code': 500
        }), 500
    
    # Root endpoint for API health check
    @app.route('/')
    def index():
        return jsonify({
            'status': 'success',
            'message': 'GroMo AI Sales Coach API is running',
            'version': app.config.get('API_VERSION', '1.0.0')
        })
    
    return app


if __name__ == '__main__':
    # Create and run the application
    app = create_app()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(
        host='0.0.0.0',  # Make server publicly available
        port=port,
        debug=app.config.get('DEBUG', False)
    )
