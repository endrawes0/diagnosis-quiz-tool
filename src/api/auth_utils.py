"""
Authentication utilities for optional JWT support.
Provides decorators that conditionally require authentication based on app config.
"""

from functools import wraps
from flask import current_app, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError


def optional_jwt_required():
    """
    Decorator that conditionally requires JWT based on REQUIRE_AUTH config.

    If REQUIRE_AUTH=False, allows requests without JWT tokens.
    If REQUIRE_AUTH=True, enforces JWT authentication.

    Usage:
        @optional_jwt_required()
        def my_endpoint():
            user_id = get_current_user_id()  # Returns 'anonymous' if no auth
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_app.config.get('REQUIRE_AUTH', False):
                # Auth is required - verify JWT
                try:
                    verify_jwt_in_request()
                except NoAuthorizationError:
                    return jsonify({
                        'error': 'Authorization required',
                        'message': 'This endpoint requires authentication. Please log in.'
                    }), 401
            else:
                # Auth is optional - allow through without JWT
                pass

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user_id():
    """
    Get the current user ID from JWT or return 'anonymous' if auth is disabled.

    Returns:
        str: User ID from JWT token, or 'anonymous' if auth is disabled
    """
    if current_app.config.get('REQUIRE_AUTH', False):
        try:
            return get_jwt_identity()
        except:
            return 'anonymous'
    else:
        # Auth disabled - return anonymous user
        return 'anonymous'


def get_current_username():
    """
    Get the current username or return 'Anonymous User' if auth is disabled.

    Returns:
        str: Username from session/database, or 'Anonymous User'
    """
    user_id = get_current_user_id()
    if user_id == 'anonymous':
        return 'Anonymous User'

    # Try to get username from user manager
    try:
        user_manager = current_app.user_manager
        user = user_manager.get_user(user_id)
        return user.username if user else user_id
    except:
        return user_id
