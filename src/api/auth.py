"""
Authentication API routes.
Handles user registration, login, logout, and token management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "confirm_password": "string"
    }
    
    Response:
    {
        "message": "User registered successfully",
        "user_id": "string",
        "access_token": "string",
        "refresh_token": "string"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password', 'confirm_password']):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'username, email, password, and confirm_password are required'
            }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        confirm_password = data['confirm_password']
        
        # Validate input
        if len(username) < 3:
            return jsonify({
                'error': 'Invalid username',
                'message': 'Username must be at least 3 characters long'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400
        
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({
                'error': 'Invalid password',
                'message': password_message
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'error': 'Password mismatch',
                'message': 'Passwords do not match'
            }), 400
        
        # Create user
        user_manager = current_app.user_manager
        profile, message = user_manager.create_user(username, password)
        
        if not profile:
            return jsonify({
                'error': 'Registration failed',
                'message': message
            }), 400
        
        # Store email in profile (extend user profile to include email)
        profile.email = email
        
        # Save profile with email
        user_manager.save_user(profile)
        
        # Create tokens
        access_token = create_access_token(identity=profile.user_id)
        refresh_token = create_refresh_token(identity=profile.user_id)
        
        # Start session
        profile.start_session()
        user_manager.save_user(profile)
        
        current_app.logger.info(f"User registered: {username} ({profile.user_id})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': profile.user_id,
            'username': profile.username,
            'email': email,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'created_at': profile.created_at.isoformat()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Registration failed',
            'message': 'An unexpected error occurred during registration'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login.
    
    Request Body:
    {
        "username": "string",
        "password": "string"
    }
    
    Response:
    {
        "message": "Login successful",
        "user_id": "string",
        "access_token": "string",
        "refresh_token": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({
                'error': 'Missing credentials',
                'message': 'username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Authenticate user
        user_manager = current_app.user_manager
        profile = user_manager.authenticate_user(username, password)
        
        if not profile:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid username or password'
            }), 401
        
        # Check if account is locked
        if profile.locked_until and datetime.now() < profile.locked_until:
            return jsonify({
                'error': 'Account locked',
                'message': f'Account is locked until {profile.locked_until.strftime("%Y-%m-%d %H:%M:%S")}'
            }), 423
        
        # Create tokens
        access_token = create_access_token(identity=profile.user_id)
        refresh_token = create_refresh_token(identity=profile.user_id)
        
        # Get session info
        session_stats = profile.end_session()
        profile.start_session()
        user_manager.save_user(profile)
        
        current_app.logger.info(f"User logged in: {username} ({profile.user_id})")
        
        return jsonify({
            'message': 'Login successful',
            'user_id': profile.user_id,
            'username': profile.username,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'last_login': profile.last_login.isoformat() if profile.last_login else None,
            'session_id': profile.session_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'message': 'An unexpected error occurred during login'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    User logout.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "message": "Logout successful"
    }
    """
    try:
        user_id = get_jwt_identity()
        user_manager = current_app.user_manager
        
        # Find and end user session
        for session_id, profile in list(user_manager.active_sessions.items()):
            if profile.user_id == user_id:
                session_stats = user_manager.end_session(session_id)
                current_app.logger.info(f"User logged out: {profile.username} ({user_id})")
                return jsonify({
                    'message': 'Logout successful',
                    'session_stats': session_stats
                }), 200
        
        return jsonify({
            'message': 'Logout successful',
            'note': 'No active session found'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'Logout failed',
            'message': 'An unexpected error occurred during logout'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh JWT access token.
    
    Headers:
    Authorization: Bearer <refresh_token>
    
    Response:
    {
        "access_token": "string"
    }
    """
    try:
        user_id = get_jwt_identity()
        user_manager = current_app.user_manager
        
        # Verify user still exists
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'The user associated with this token no longer exists'
            }), 404
        
        # Create new access token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'Token refresh failed',
            'message': 'An unexpected error occurred during token refresh'
        }), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify JWT token and get user info.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "valid": true,
        "user_id": "string",
        "username": "string"
    }
    """
    try:
        user_id = get_jwt_identity()
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'valid': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'valid': True,
            'user_id': profile.user_id,
            'username': profile.username,
            'last_login': profile.last_login.isoformat() if profile.last_login else None,
            'is_active': profile.is_active
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'Token verification failed'
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "current_password": "string",
        "new_password": "string",
        "confirm_password": "string"
    }
    
    Response:
    {
        "message": "Password changed successfully"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not all(k in data for k in ['current_password', 'new_password', 'confirm_password']):
            return jsonify({
                'error': 'Missing required fields',
                'message': 'current_password, new_password, and confirm_password are required'
            }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        
        # Validate new password
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'error': 'Invalid password',
                'message': password_message
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                'error': 'Password mismatch',
                'message': 'New passwords do not match'
            }), 400
        
        # Load user profile
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Verify current password
        if not profile.verify_password(current_password):
            return jsonify({
                'error': 'Invalid password',
                'message': 'Current password is incorrect'
            }), 401
        
        # Set new password
        profile.set_password(new_password)
        user_manager.save_user(profile)
        
        current_app.logger.info(f"Password changed for user: {profile.username} ({user_id})")
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'error': 'Password change failed',
            'message': 'An unexpected error occurred during password change'
        }), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Initiate password reset process.
    
    Request Body:
    {
        "email": "string"
    }
    
    Response:
    {
        "message": "Password reset email sent"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'error': 'Missing email',
                'message': 'Email address is required'
            }), 400
        
        email = data['email'].strip().lower()
        
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email',
                'message': 'Please provide a valid email address'
            }), 400
        
        # For now, just return a success message
        # In a real implementation, you would:
        # 1. Find user by email
        # 2. Generate reset token
        # 3. Send reset email
        # 4. Store token with expiration
        
        current_app.logger.info(f"Password reset requested for email: {email}")
        
        return jsonify({
            'message': 'Password reset instructions have been sent to your email address',
            'note': 'This is a demo implementation. In production, an actual email would be sent.'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({
            'error': 'Password reset failed',
            'message': 'An unexpected error occurred'
        }), 500