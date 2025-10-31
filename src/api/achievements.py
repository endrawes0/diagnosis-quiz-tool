"""
Achievements API routes.
Handles achievement tracking, leaderboards, and progression rewards.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import json

achievements_bp = Blueprint('achievements', __name__)


@achievements_bp.route('/', methods=['GET'])
@jwt_required()
def get_achievements():
    """
    Get user's achievements and progress.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - category: Filter by achievement category
    - status: Filter by status (earned, unearned, in_progress)
    
    Response:
    {
        "achievements": [...],
        "summary": {
            "total_achievements": 50,
            "earned_achievements": 12,
            "in_progress_achievements": 8,
            "completion_percentage": 24.0
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        category = request.args.get('category')
        status = request.args.get('status')
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Get all available achievements
        all_achievements = _get_all_achievements()
        
        # Get user's earned achievements
        earned_achievement_ids = set(profile.progress.earned_achievements)
        
        # Filter and format achievements
        achievements_response = []
        for achievement in all_achievements:
            # Apply filters
            if category and achievement.get('category') != category:
                continue
            
            is_earned = achievement['id'] in earned_achievement_ids
            if status and status == 'earned' and not is_earned:
                continue
            if status and status == 'unearned' and is_earned:
                continue
            
            # Calculate progress
            progress_data = _calculate_achievement_progress(profile, achievement)
            
            achievement_data = {
                'id': achievement['id'],
                'name': achievement['name'],
                'description': achievement['description'],
                'category': achievement['category'],
                'difficulty': achievement.get('difficulty', 'medium'),
                'xp_reward': achievement.get('xp_reward', 50),
                'is_earned': is_earned,
                'earned_at': profile.progress.achievement_earn_times.get(achievement['id'], None),
                'progress': progress_data,
                'icon': achievement.get('icon', '🏆'),
                'requirements': achievement.get('requirements', {})
            }
            
            # Add to in_progress filter logic
            if status == 'in_progress':
                if is_earned or progress_data['percentage'] == 0:
                    continue
            
            achievements_response.append(achievement_data)
        
        # Calculate summary
        total_achievements = len(all_achievements)
        earned_count = len(earned_achievement_ids)
        in_progress_count = len([a for a in achievements_response if a['progress']['percentage'] > 0 and not a['is_earned']])
        
        summary = {
            'total_achievements': total_achievements,
            'earned_achievements': earned_count,
            'in_progress_achievements': in_progress_count,
            'completion_percentage': (earned_count / total_achievements * 100) if total_achievements > 0 else 0
        }
        
        return jsonify({
            'achievements': achievements_response,
            'summary': summary,
            'filters_applied': {
                'category': category,
                'status': status
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get achievements error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve achievements',
            'message': 'An unexpected error occurred'
        }), 500


@achievements_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """
    Get achievement leaderboard.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - type: Leaderboard type (xp, achievements, streak, accuracy)
    - period: Time period (week, month, all_time)
    - limit: Number of entries to return (default: 50)
    
    Response:
    {
        "leaderboard_type": "xp",
        "period": "month",
        "entries": [...],
        "user_rank": 15
    }
    """
    try:
        user_id = get_jwt_identity()
        leaderboard_type = request.args.get('type', 'xp')
        period = request.args.get('period', 'all_time')
        limit = min(int(request.args.get('limit', 50)), 100)
        
        if leaderboard_type not in ['xp', 'achievements', 'streak', 'accuracy']:
            return jsonify({
                'error': 'Invalid leaderboard type',
                'message': 'Type must be xp, achievements, streak, or accuracy'
            }), 400
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Get all users
        all_users = user_manager.get_all_users()
        
        # Build leaderboard entries
        leaderboard_entries = []
        user_rank = None
        
        for user_info in all_users:
            # Load user profile
            profile = user_manager.load_user(user_info['user_id'])
            if not profile:
                continue
            
            # Calculate leaderboard value based on type
            if leaderboard_type == 'xp':
                value = profile.progress.total_xp
            elif leaderboard_type == 'achievements':
                value = len(profile.progress.earned_achievements)
            elif leaderboard_type == 'streak':
                value = profile.progress.streak_data.current_streak
            elif leaderboard_type == 'accuracy':
                value = profile.statistics.overall_accuracy
            
            entry = {
                'user_id': profile.user_id,
                'username': profile.username,
                'value': value,
                'level': profile.progress.level,
                'last_login': profile.last_login.isoformat() if profile.last_login else None
            }
            
            leaderboard_entries.append(entry)
            
            # Track current user's rank
            if profile.user_id == user_id:
                user_rank = len(leaderboard_entries)
        
        # Sort leaderboard (descending by value)
        leaderboard_entries.sort(key=lambda x: x['value'], reverse=True)
        
        # Recalculate user rank after sorting
        for i, entry in enumerate(leaderboard_entries):
            if entry['user_id'] == user_id:
                user_rank = i + 1
                break
        
        # Apply limit
        leaderboard_entries = leaderboard_entries[:limit]
        
        # Add rank to entries
        for i, entry in enumerate(leaderboard_entries):
            entry['rank'] = i + 1
        
        return jsonify({
            'leaderboard_type': leaderboard_type,
            'period': period,
            'entries': leaderboard_entries,
            'user_rank': user_rank,
            'total_users': len(all_users),
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get leaderboard error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve leaderboard',
            'message': 'An unexpected error occurred'
        }), 500


@achievements_bp.route('/claim', methods=['POST'])
@jwt_required()
def claim_achievement():
    """
    Claim an achievement reward.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "achievement_id": "string"
    }
    
    Response:
    {
        "message": "Achievement claimed successfully",
        "xp_awarded": 100,
        "achievement": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'achievement_id' not in data:
            return jsonify({
                'error': 'Missing achievement ID',
                'message': 'achievement_id is required'
            }), 400
        
        achievement_id = data['achievement_id']
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Load user profile
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Check if achievement is already earned
        if achievement_id in profile.progress.earned_achievements:
            return jsonify({
                'error': 'Already earned',
                'message': 'This achievement has already been claimed'
            }), 400
        
        # Get achievement details
        all_achievements = _get_all_achievements()
        achievement = next((a for a in all_achievements if a['id'] == achievement_id), None)
        
        if not achievement:
            return jsonify({
                'error': 'Achievement not found',
                'message': 'The specified achievement does not exist'
            }), 404
        
        # Check if requirements are met
        progress_data = _calculate_achievement_progress(profile, achievement)
        if progress_data['percentage'] < 100:
            return jsonify({
                'error': 'Requirements not met',
                'message': 'You have not yet met the requirements for this achievement',
                'current_progress': progress_data
            }), 400
        
        # Award achievement
        profile.progress.earned_achievements.append(achievement_id)
        profile.progress.achievement_earn_times[achievement_id] = datetime.now()
        
        # Award XP
        xp_reward = achievement.get('xp_reward', 50)
        profile.progress.add_xp(xp_reward, "achievement")
        
        # Save profile
        user_manager.save_user(profile)
        
        current_app.logger.info(f"Achievement claimed by user {user_id}: {achievement_id}")
        
        return jsonify({
            'message': 'Achievement claimed successfully',
            'xp_awarded': xp_reward,
            'achievement': {
                'id': achievement['id'],
                'name': achievement['name'],
                'description': achievement['description'],
                'category': achievement['category'],
                'xp_reward': xp_reward
            },
            'claimed_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Claim achievement error: {str(e)}")
        return jsonify({
            'error': 'Failed to claim achievement',
            'message': 'An unexpected error occurred'
        }), 500


@achievements_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_achievement_categories():
    """
    Get all achievement categories.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "categories": [...],
        "count": 8
    }
    """
    try:
        # Get all achievements
        all_achievements = _get_all_achievements()
        
        # Extract unique categories
        categories = {}
        for achievement in all_achievements:
            category = achievement.get('category', 'general')
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'display_name': category.replace('_', ' ').title(),
                    'description': _get_category_description(category),
                    'icon': _get_category_icon(category),
                    'achievement_count': 0
                }
            categories[category]['achievement_count'] += 1
        
        # Convert to list and sort
        categories_list = list(categories.values())
        categories_list.sort(key=lambda x: x['achievement_count'], reverse=True)
        
        return jsonify({
            'categories': categories_list,
            'count': len(categories_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get achievement categories error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve achievement categories',
            'message': 'An unexpected error occurred'
        }), 500


@achievements_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_achievement_notifications():
    """
    Get achievement notifications and recent unlocks.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "recent_unlocks": [...],
        "upcoming_achievements": [...],
        "milestone_progress": [...]
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
        
        # Get recent unlocks (last 7 days)
        recent_unlocks = []
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        all_achievements = _get_all_achievements()
        for achievement_id, earn_time in profile.progress.achievement_earn_times.items():
            if earn_time and earn_time >= seven_days_ago:
                achievement = next((a for a in all_achievements if a['id'] == achievement_id), None)
                if achievement:
                    recent_unlocks.append({
                        'achievement_id': achievement_id,
                        'name': achievement['name'],
                        'description': achievement['description'],
                        'xp_reward': achievement.get('xp_reward', 50),
                        'earned_at': earn_time.isoformat(),
                        'category': achievement.get('category', 'general')
                    })
        
        # Sort recent unlocks by earn time (newest first)
        recent_unlocks.sort(key=lambda x: x['earned_at'], reverse=True)
        
        # Get upcoming achievements (close to completion)
        upcoming_achievements = []
        for achievement in all_achievements:
            if achievement['id'] not in profile.progress.earned_achievements:
                progress_data = _calculate_achievement_progress(profile, achievement)
                if progress_data['percentage'] >= 75:  # Close to completion
                    upcoming_achievements.append({
                        'achievement_id': achievement['id'],
                        'name': achievement['name'],
                        'description': achievement['description'],
                        'progress': progress_data,
                        'category': achievement.get('category', 'general')
                    })
        
        # Sort by progress percentage (highest first)
        upcoming_achievements.sort(key=lambda x: x['progress']['percentage'], reverse=True)
        upcoming_achievements = upcoming_achievements[:5]  # Top 5 upcoming
        
        # Get milestone progress
        milestone_progress = _calculate_milestone_progress(profile)
        
        return jsonify({
            'recent_unlocks': recent_unlocks,
            'upcoming_achievements': upcoming_achievements,
            'milestone_progress': milestone_progress,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get achievement notifications error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve achievement notifications',
            'message': 'An unexpected error occurred'
        }), 500


def _get_all_achievements():
    """Get all available achievements."""
    return [
        {
            'id': 'first_case',
            'name': 'First Steps',
            'description': 'Complete your first case',
            'category': 'general',
            'difficulty': 'easy',
            'xp_reward': 25,
            'requirements': {'cases_completed': 1}
        },
        {
            'id': 'ten_cases',
            'name': 'Getting Started',
            'description': 'Complete 10 cases',
            'category': 'general',
            'difficulty': 'easy',
            'xp_reward': 50,
            'requirements': {'cases_completed': 10}
        },
        {
            'id': 'hundred_cases',
            'name': 'Dedicated Learner',
            'description': 'Complete 100 cases',
            'category': 'general',
            'difficulty': 'medium',
            'xp_reward': 200,
            'requirements': {'cases_completed': 100}
        },
        {
            'id': 'perfect_score',
            'name': 'Perfect Score',
            'description': 'Achieve 100% accuracy in a quiz',
            'category': 'performance',
            'difficulty': 'medium',
            'xp_reward': 100,
            'requirements': {'perfect_quiz': True}
        },
        {
            'id': 'speed_demon',
            'name': 'Speed Demon',
            'description': 'Complete 10 cases with average time under 30 seconds',
            'category': 'performance',
            'difficulty': 'hard',
            'xp_reward': 150,
            'requirements': {'speed_achievement': True}
        },
        {
            'id': 'streak_warrior',
            'name': 'Streak Warrior',
            'description': 'Maintain a 7-day streak',
            'category': 'consistency',
            'difficulty': 'medium',
            'xp_reward': 100,
            'requirements': {'streak_days': 7}
        },
        {
            'id': 'category_master',
            'name': 'Category Master',
            'description': 'Master a specific category (level 10)',
            'category': 'specialization',
            'difficulty': 'hard',
            'xp_reward': 250,
            'requirements': {'category_level': 10}
        },
        {
            'id': 'xp_collector',
            'name': 'XP Collector',
            'description': 'Earn 1000 total XP',
            'category': 'progression',
            'difficulty': 'medium',
            'xp_reward': 100,
            'requirements': {'total_xp': 1000}
        }
    ]


def _calculate_achievement_progress(profile, achievement):
    """Calculate progress for an achievement."""
    requirements = achievement.get('requirements', {})
    progress = {'percentage': 0, 'current': 0, 'required': 1, 'details': {}}
    
    if 'cases_completed' in requirements:
        current = len(profile.completed_cases)
        required = requirements['cases_completed']
        progress['current'] = current
        progress['required'] = required
        progress['percentage'] = min(100, (current / required) * 100)
        progress['details']['cases_completed'] = f"{current}/{required}"
    
    elif 'perfect_quiz' in requirements:
        # Check if user has any perfect quizzes
        perfect_quizzes = 0
        # This would require tracking quiz sessions
        progress['current'] = perfect_quizzes
        progress['required'] = 1
        progress['percentage'] = 100 if perfect_quizzes > 0 else 0
        progress['details']['perfect_quizzes'] = f"{perfect_quizzes}/1"
    
    elif 'speed_achievement' in requirements:
        # Check fast cases
        fast_cases = len([case for case in profile.completed_cases if case.time_taken < 30])
        progress['current'] = fast_cases
        progress['required'] = 10
        progress['percentage'] = min(100, (fast_cases / 10) * 100)
        progress['details']['fast_cases'] = f"{fast_cases}/10"
    
    elif 'streak_days' in requirements:
        current_streak = profile.progress.streak_data.current_streak
        required = requirements['streak_days']
        progress['current'] = current_streak
        progress['required'] = required
        progress['percentage'] = min(100, (current_streak / required) * 100)
        progress['details']['streak_days'] = f"{current_streak}/{required}"
    
    elif 'category_level' in requirements:
        max_category_level = 0
        for proficiency in profile.progress.specialties.values():
            max_category_level = max(max_category_level, proficiency.level)
        
        required = requirements['category_level']
        progress['current'] = max_category_level
        progress['required'] = required
        progress['percentage'] = min(100, (max_category_level / required) * 100)
        progress['details']['max_category_level'] = f"{max_category_level}/{required}"
    
    elif 'total_xp' in requirements:
        current_xp = profile.progress.total_xp
        required = requirements['total_xp']
        progress['current'] = current_xp
        progress['required'] = required
        progress['percentage'] = min(100, (current_xp / required) * 100)
        progress['details']['total_xp'] = f"{current_xp}/{required}"
    
    return progress


def _get_category_description(category):
    """Get description for achievement category."""
    descriptions = {
        'general': 'General achievements for overall progress',
        'performance': 'Achievements related to quiz performance',
        'consistency': 'Achievements for regular practice',
        'specialization': 'Achievements for mastering specific categories',
        'progression': 'Achievements for leveling and XP milestones'
    }
    return descriptions.get(category, 'Achievements in this category')


def _get_category_icon(category):
    """Get icon for achievement category."""
    icons = {
        'general': '🏆',
        'performance': '⚡',
        'consistency': '📅',
        'specialization': '🎯',
        'progression': '📈'
    }
    return icons.get(category, '🏆')


def _calculate_milestone_progress(profile):
    """Calculate progress towards major milestones."""
    milestones = [
        {
            'name': 'Level 10',
            'description': 'Reach level 10',
            'current': profile.progress.level,
            'required': 10,
            'percentage': min(100, (profile.progress.level / 10) * 100)
        },
        {
            'name': '500 XP',
            'description': 'Earn 500 total XP',
            'current': profile.progress.total_xp,
            'required': 500,
            'percentage': min(100, (profile.progress.total_xp / 500) * 100)
        },
        {
            'name': '50 Cases',
            'description': 'Complete 50 cases',
            'current': len(profile.completed_cases),
            'required': 50,
            'percentage': min(100, (len(profile.completed_cases) / 50) * 100)
        },
        {
            'name': '10 Achievements',
            'description': 'Earn 10 achievements',
            'current': len(profile.progress.earned_achievements),
            'required': 10,
            'percentage': min(100, (len(profile.progress.earned_achievements) / 10) * 100)
        }
    ]
    
    return milestones