"""
Users API routes.
Handles user profile management, progress tracking, and analytics.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from dataclasses import asdict

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile information.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "user_id": "string",
        "username": "string",
        "created_at": "timestamp",
        "last_login": "timestamp",
        "level": 5,
        "total_xp": 1250,
        "xp_to_next_level": 250,
        "completed_cases_count": 45,
        "achievements_count": 12,
        "current_streak": 7,
        "longest_streak": 15,
        "overall_accuracy": 78.5,
        "favorite_category": "mood_disorders",
        "preferences": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Get profile summary
        profile_summary = profile.get_profile_summary()
        
        return jsonify(profile_summary), 200
        
    except Exception as e:
        current_app.logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve profile',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile information.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "username": "string",
        "preferences": {
            "difficulty_preference": "mixed",
            "focus_areas": ["mood_disorders"],
            "notifications": true,
            "timer_enabled": true,
            "theme": "default",
            "language": "en"
        }
    }
    
    Response:
    {
        "message": "Profile updated successfully",
        "updated_fields": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Profile update data is required'
            }), 400
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        updated_fields = []
        
        # Update username if provided
        if 'username' in data:
            new_username = data['username'].strip()
            if len(new_username) < 3:
                return jsonify({
                    'error': 'Invalid username',
                    'message': 'Username must be at least 3 characters long'
                }), 400
            
            profile.username = new_username
            updated_fields.append('username')
        
        # Update preferences if provided
        if 'preferences' in data:
            preferences = data['preferences']
            if isinstance(preferences, dict):
                profile.update_preferences(preferences)
                updated_fields.append('preferences')
        
        # Save updated profile
        if user_manager.save_user(profile):
            current_app.logger.info(f"Profile updated for user {user_id}: {updated_fields}")
            
            return jsonify({
                'message': 'Profile updated successfully',
                'updated_fields': updated_fields,
                'updated_at': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'error': 'Update failed',
                'message': 'Failed to save profile changes'
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Update profile error: {str(e)}")
        return jsonify({
            'error': 'Failed to update profile',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    """
    Get detailed user progress information.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "level": 5,
        "total_xp": 1250,
        "xp_to_next_level": 250,
        "xp_progress_percentage": 83.3,
        "streak_data": {
            "current_streak": 7,
            "longest_streak": 15,
            "streak_multiplier": 1.5
        },
        "specialties": {
            "mood_disorders": {
                "level": 7,
                "accuracy": 85.2,
                "cases_completed": 25
            }
        },
        "unlock_status": {
            "unlocked_difficulties": ["basic", "intermediate", "advanced"],
            "unlocked_categories": [...]
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Get progress data
        progress = profile.progress
        
        # Format progress data
        progress_data = {
            'level': progress.level,
            'total_xp': progress.total_xp,
            'xp_to_next_level': progress.xp_to_next_level,
            'xp_progress_percentage': (progress.total_xp / (progress.total_xp + progress.xp_to_next_level)) * 100 if progress.xp_to_next_level > 0 else 100,
            'streak_data': {
                'current_streak': progress.streak_data.current_streak,
                'longest_streak': progress.streak_data.longest_streak,
                'streak_multiplier': progress.streak_data.streak_multiplier,
                'last_streak_update': progress.streak_data.last_streak_update.isoformat() if progress.streak_data.last_streak_update else None
            },
            'specialties': {},
            'unlock_status': {
                'unlocked_difficulties': list(progress.unlock_status.unlocked_difficulties),
                'unlocked_categories': list(progress.unlock_status.unlocked_categories)
            },
            'performance_metrics': {
                'recent_performance': progress.performance_metrics.recent_performance,
                'average_accuracy': progress.performance_metrics.average_accuracy,
                'total_cases_completed': progress.performance_metrics.total_cases_completed
            }
        }
        
        # Format specialties
        for category, proficiency in progress.specialties.items():
            progress_data['specialties'][category] = {
                'level': proficiency.level,
                'accuracy': proficiency.accuracy,
                'cases_completed': proficiency.cases_completed,
                'total_time_spent': proficiency.total_time_spent,
                'average_time_per_case': proficiency.average_time_per_case
            }
        
        return jsonify(progress_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Get progress error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve progress',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """
    Get detailed user analytics and insights.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - period: Time period for analytics (week, month, quarter, year, all)
    - category: Filter by specific category
    
    Response:
    {
        "period": "month",
        "performance_trends": [...],
        "category_performance": {...},
        "difficulty_progression": [...],
        "time_analysis": {...},
        "recommendations": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        period = request.args.get('period', 'month')
        category_filter = request.args.get('category')
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Calculate date range based on period
        now = datetime.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'quarter':
            start_date = now - timedelta(days=90)
        elif period == 'year':
            start_date = now - timedelta(days=365)
        else:  # all
            start_date = None
        
        # Filter completed cases by period and category
        completed_cases = profile.completed_cases
        if start_date:
            completed_cases = [case for case in completed_cases if case.completed_at >= start_date]
        if category_filter:
            completed_cases = [case for case in completed_cases if case.category == category_filter]
        
        # Calculate analytics
        analytics = {
            'period': period,
            'category_filter': category_filter,
            'summary': {
                'total_cases': len(completed_cases),
                'correct_answers': sum(1 for case in completed_cases if case.is_correct),
                'overall_accuracy': (sum(1 for case in completed_cases if case.is_correct) / len(completed_cases) * 100) if completed_cases else 0,
                'total_xp_earned': sum(case.xp_earned for case in completed_cases),
                'average_time_per_case': sum(case.time_taken for case in completed_cases) / len(completed_cases) if completed_cases else 0
            },
            'performance_trends': _calculate_performance_trends(completed_cases),
            'category_performance': _calculate_category_performance(completed_cases),
            'difficulty_progression': _calculate_difficulty_progression(completed_cases),
            'time_analysis': _calculate_time_analysis(completed_cases),
            'recommendations': _generate_recommendations(profile, completed_cases)
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        current_app.logger.error(f"Get analytics error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve analytics',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    Get user statistics and achievements.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "basic_stats": {...},
        "performance_stats": {...},
        "achievement_stats": {...},
        "comparison_stats": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Calculate statistics
        statistics = {
            'basic_stats': {
                'user_id': profile.user_id,
                'username': profile.username,
                'created_at': profile.created_at.isoformat(),
                'last_login': profile.last_login.isoformat() if profile.last_login else None,
                'total_session_time': profile.statistics.total_session_time,
                'sessions_completed': profile.statistics.sessions_completed
            },
            'performance_stats': {
                'total_cases_attempted': profile.statistics.total_cases_attempted,
                'total_correct': profile.statistics.total_correct,
                'overall_accuracy': profile.statistics.overall_accuracy,
                'average_time_per_case': profile.statistics.average_time_per_case,
                'favorite_category': profile.statistics.favorite_category
            },
            'progress_stats': {
                'current_level': profile.progress.level,
                'total_xp': profile.progress.total_xp,
                'xp_to_next_level': profile.progress.xp_to_next_level,
                'current_streak': profile.progress.streak_data.current_streak,
                'longest_streak': profile.progress.streak_data.longest_streak,
                'achievements_earned': len(profile.progress.earned_achievements)
            },
            'specialty_stats': {}
        }
        
        # Add specialty statistics
        for category, proficiency in profile.progress.specialties.items():
            statistics['specialty_stats'][category] = {
                'level': proficiency.level,
                'accuracy': proficiency.accuracy,
                'cases_completed': proficiency.cases_completed,
                'total_time_spent': proficiency.total_time_spent
            }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        current_app.logger.error(f"Get statistics error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/history', methods=['GET'])
@jwt_required()
def get_case_history():
    """
    Get user's case completion history.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - limit: Number of cases to return (default: 20)
    - offset: Offset for pagination (default: 0)
    - category: Filter by category
    - difficulty: Filter by difficulty
    - correct_only: Show only correct answers (true/false)
    
    Response:
    {
        "cases": [...],
        "total_count": 150,
        "pagination": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        correct_only = request.args.get('correct_only', 'false').lower() == 'true'
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Get completed cases
        completed_cases = profile.completed_cases
        
        # Apply filters
        if category:
            completed_cases = [case for case in completed_cases if case.category == category]
        if difficulty:
            completed_cases = [case for case in completed_cases if case.difficulty == difficulty]
        if correct_only:
            completed_cases = [case for case in completed_cases if case.is_correct]
        
        # Sort by completion date (newest first)
        completed_cases.sort(key=lambda x: x.completed_at, reverse=True)
        
        # Apply pagination
        total_count = len(completed_cases)
        paginated_cases = completed_cases[offset:offset + limit]
        
        # Format case data
        cases_response = []
        for case in paginated_cases:
            case_data = {
                'case_id': case.case_id,
                'completed_at': case.completed_at.isoformat(),
                'xp_earned': case.xp_earned,
                'accuracy': case.accuracy,
                'time_taken': case.time_taken,
                'attempts': case.attempts,
                'difficulty': case.difficulty,
                'category': case.category,
                'is_correct': case.is_correct
            }
            cases_response.append(case_data)
        
        return jsonify({
            'cases': cases_response,
            'total_count': total_count,
            'filters_applied': {
                'category': category,
                'difficulty': difficulty,
                'correct_only': correct_only
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get case history error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve case history',
            'message': 'An unexpected error occurred'
        }), 500


@users_bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    """
    Export user data for backup or migration.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - format: Export format (json, csv)
    
    Response:
    {
        "export_data": {...},
        "exported_at": "timestamp",
        "format": "json"
    }
    """
    try:
        user_id = get_jwt_identity()
        export_format = request.args.get('format', 'json')
        
        if export_format not in ['json', 'csv']:
            return jsonify({
                'error': 'Invalid format',
                'message': 'Export format must be json or csv'
            }), 400
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Export data
        export_data = profile.export_data()
        
        current_app.logger.info(f"Data exported for user {user_id}")
        
        return jsonify({
            'export_data': export_data,
            'exported_at': datetime.now().isoformat(),
            'format': export_format
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Export data error: {str(e)}")
        return jsonify({
            'error': 'Failed to export data',
            'message': 'An unexpected error occurred'
        }), 500


def _calculate_performance_trends(completed_cases):
    """Calculate performance trends over time."""
    if not completed_cases:
        return []
    
    # Group by week
    from collections import defaultdict
    weekly_data = defaultdict(lambda: {'correct': 0, 'total': 0, 'xp': 0})
    
    for case in completed_cases:
        week_key = case.completed_at.strftime('%Y-W%U')
        weekly_data[week_key]['total'] += 1
        if case.is_correct:
            weekly_data[week_key]['correct'] += 1
        weekly_data[week_key]['xp'] += case.xp_earned
    
    # Convert to list and sort
    trends = []
    for week, data in sorted(weekly_data.items()):
        trends.append({
            'week': week,
            'accuracy': (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0,
            'cases_completed': data['total'],
            'xp_earned': data['xp']
        })
    
    return trends


def _calculate_category_performance(completed_cases):
    """Calculate performance by category."""
    from collections import defaultdict
    category_data = defaultdict(lambda: {'correct': 0, 'total': 0, 'time': 0, 'xp': 0})
    
    for case in completed_cases:
        category_data[case.category]['total'] += 1
        if case.is_correct:
            category_data[case.category]['correct'] += 1
        category_data[case.category]['time'] += case.time_taken
        category_data[case.category]['xp'] += case.xp_earned
    
    # Convert to dict with percentages
    performance = {}
    for category, data in category_data.items():
        performance[category] = {
            'accuracy': (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0,
            'cases_completed': data['total'],
            'average_time': data['time'] / data['total'] if data['total'] > 0 else 0,
            'total_xp': data['xp']
        }
    
    return performance


def _calculate_difficulty_progression(completed_cases):
    """Calculate performance by difficulty level."""
    from collections import defaultdict
    difficulty_data = defaultdict(lambda: {'correct': 0, 'total': 0, 'xp': 0})
    
    for case in completed_cases:
        difficulty_data[case.difficulty]['total'] += 1
        if case.is_correct:
            difficulty_data[case.difficulty]['correct'] += 1
        difficulty_data[case.difficulty]['xp'] += case.xp_earned
    
    # Convert to dict
    progression = {}
    for difficulty, data in difficulty_data.items():
        progression[difficulty] = {
            'accuracy': (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0,
            'cases_completed': data['total'],
            'total_xp': data['xp']
        }
    
    return progression


def _calculate_time_analysis(completed_cases):
    """Analyze time performance."""
    if not completed_cases:
        return {}
    
    times = [case.time_taken for case in completed_cases]
    
    return {
        'average_time': sum(times) / len(times),
        'fastest_time': min(times),
        'slowest_time': max(times),
        'median_time': sorted(times)[len(times) // 2],
        'time_distribution': {
            'under_30s': len([t for t in times if t < 30]),
            '30s_to_60s': len([t for t in times if 30 <= t < 60]),
            '60s_to_120s': len([t for t in times if 60 <= t < 120]),
            'over_120s': len([t for t in times if t >= 120])
        }
    }


def _generate_recommendations(profile, completed_cases):
    """Generate personalized recommendations."""
    recommendations = []
    
    # Analyze weak areas
    category_performance = _calculate_category_performance(completed_cases)
    weak_categories = [cat for cat, perf in category_performance.items() if perf['accuracy'] < 70]
    
    if weak_categories:
        recommendations.append({
            'type': 'practice',
            'priority': 'high',
            'message': f'Focus on improving performance in: {", ".join(weak_categories)}',
            'categories': weak_categories
        })
    
    # Time-based recommendations
    if completed_cases:
        avg_time = sum(case.time_taken for case in completed_cases) / len(completed_cases)
        if avg_time > 120:
            recommendations.append({
                'type': 'speed',
                'priority': 'medium',
                'message': 'Consider working on improving your response time',
                'suggestion': 'Practice with timed sessions to build speed'
            })
    
    # Streak recommendations
    if profile.progress.streak_data.current_streak >= 5:
        recommendations.append({
            'type': 'maintain',
            'priority': 'low',
            'message': f'Great job! Maintain your {profile.progress.streak_data.current_streak}-day streak',
            'encouragement': 'Keep up the excellent work!'
        })
    
    return recommendations