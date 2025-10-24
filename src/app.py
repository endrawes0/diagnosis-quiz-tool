"""
Flask application for the Diagnosis Quiz Tool API.
Provides comprehensive REST API endpoints for quiz generation, user management,
case browsing, and analytics.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException
import json
from functools import wraps

# Import modules
from .modules.data_loader import DataLoader
from .modules.quiz_generator import QuizGenerator
from .modules.user_manager import UserManager
from .modules.scoring import Scoring
from .modules.progression import UserProgress

# Import API routes
from .api.auth import auth_bp
from .api.quiz import quiz_bp
from .api.cases import cases_bp
from .api.users import users_bp
from .api.data import data_bp
from .api.achievements import achievements_bp


def create_app(config_name='development'):
    """
    Application factory function.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['REQUIRE_AUTH'] = os.environ.get('REQUIRE_AUTH', 'False').lower() == 'true'
    app.config['DEMO_MODE'] = os.environ.get('DEMO_MODE', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['DATA_DIR'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:8080"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    jwt = JWTManager(app)

    # Create optional auth decorator
    def optional_jwt_required(fn):
        """Decorator that conditionally requires JWT based on REQUIRE_AUTH config."""
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if app.config.get('REQUIRE_AUTH', False):
                # Auth is required - check JWT
                jwt_required()(fn)(*args, **kwargs)
            else:
                # Auth is optional - proceed without JWT check
                return fn(*args, **kwargs)
        return wrapper

    # Make optional_jwt_required available to routes
    app.optional_jwt_required = optional_jwt_required

    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/api.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Diagnosis Quiz Tool API startup')
    
    # Initialize core components
    data_loader = DataLoader(app.config['DATA_DIR'])
    quiz_generator = QuizGenerator(data_loader)
    user_manager = UserManager(app.config['DATA_DIR'])
    scoring_engine = Scoring()
    
    # Store components in app context for access in routes
    app.data_loader = data_loader
    app.quiz_generator = quiz_generator
    app.user_manager = user_manager
    app.scoring_engine = scoring_engine
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(cases_bp, url_prefix='/api/cases')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(data_bp, url_prefix='/api/data')
    app.register_blueprint(achievements_bp, url_prefix='/api/achievements')
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Your session has expired. Please log in again.'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'The provided token is invalid.'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'A valid token is required to access this resource.'
        }), 401
    
    # Global error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions."""
        return jsonify({
            'error': e.name,
            'message': e.description,
            'status_code': e.code
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle unexpected exceptions."""
        app.logger.error(f'Unhandled exception: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }), 500
    
    # Rate limiting decorator
    def rate_limit(max_requests=100, window=3600):
        """Simple rate limiting decorator."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # This is a simplified rate limiter - in production, use Redis or similar
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
                
                # For now, just log the request
                app.logger.info(f"Request from {client_ip} to {request.endpoint}")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'require_auth': app.config.get('REQUIRE_AUTH', False),
            'demo_mode': app.config.get('DEMO_MODE', False),
            'components': {
                'data_loader': 'operational',
                'quiz_generator': 'operational',
                'user_manager': 'operational',
                'scoring_engine': 'operational'
            }
        })

    # Config endpoint for frontend
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get public configuration for frontend."""
        return jsonify({
            'require_auth': app.config.get('REQUIRE_AUTH', False),
            'demo_mode': app.config.get('DEMO_MODE', False),
            'version': '1.0.0',
            'max_file_size': app.config.get('MAX_CONTENT_LENGTH', 16777216)
        })
    
    # API documentation endpoint
    @app.route('/api/docs', methods=['GET'])
    def api_docs():
        """API documentation endpoint."""
        docs = {
            'title': 'Diagnosis Quiz Tool API',
            'version': '1.0.0',
            'description': 'Comprehensive API for diagnosis quiz generation and user management',
            'base_url': '/api',
            'endpoints': {
                'Authentication': {
                    'POST /auth/register': 'Register a new user',
                    'POST /auth/login': 'User login',
                    'POST /auth/logout': 'User logout',
                    'POST /auth/refresh': 'Refresh JWT token'
                },
                'Quiz': {
                    'POST /quiz/generate': 'Generate a new quiz',
                    'POST /quiz/submit': 'Submit quiz answers',
                    'GET /quiz/history': 'Get quiz history',
                    'GET /quiz/<quiz_id>': 'Get specific quiz'
                },
                'Cases': {
                    'GET /cases': 'Browse cases with filters',
                    'GET /cases/<case_id>': 'Get specific case',
                    'GET /cases/search': 'Search cases',
                    'GET /cases/categories': 'Get available categories'
                },
                'Users': {
                    'GET /users/profile': 'Get user profile',
                    'PUT /users/profile': 'Update user profile',
                    'GET /users/progress': 'Get user progress',
                    'GET /users/analytics': 'Get user analytics'
                },
                'Data': {
                    'GET /data/summary': 'Get data summary',
                    'POST /data/upload': 'Upload data files',
                    'GET /data/download/<filename>': 'Download data files'
                },
                'Achievements': {
                    'GET /achievements': 'Get user achievements',
                    'GET /achievements/leaderboard': 'Get leaderboard',
                    'POST /achievements/claim': 'Claim achievement'
                }
            }
        }
        return jsonify(docs)
    
    # File upload validation
    def allowed_file(filename, allowed_extensions=None):
        """Check if file has allowed extension."""
        if allowed_extensions is None:
            allowed_extensions = {'json', 'csv', 'txt', 'pdf'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    # Make utility functions available to routes
    app.allowed_file = allowed_file
    app.rate_limit = rate_limit
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log request information."""
        app.logger.debug(f'Request: {request.method} {request.url}')
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            try:
                app.logger.debug(f'Request JSON: {request.json}')
            except Exception as e:
                app.logger.debug(f'Failed to parse JSON: {e}')
    
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        app.logger.debug(f'Response: {response.status_code}')
        return response
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)