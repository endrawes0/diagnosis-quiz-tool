"""
Cases API routes.
Handles case browsing, searching, and filtering.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

cases_bp = Blueprint('cases', __name__)


@cases_bp.route('/', methods=['GET'])
def browse_cases():
    """
    Browse cases with optional filtering.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - category: Filter by category
    - age_group: Filter by age group
    - complexity: Filter by complexity
    - diagnosis: Filter by diagnosis
    - limit: Number of cases to return (default: 20)
    - offset: Offset for pagination (default: 0)
    - sort: Sort field (created_at, difficulty, category)
    - order: Sort order (asc, desc)
    
    Response:
    {
        "cases": [...],
        "total_count": 150,
        "filters_applied": {...},
        "pagination": {...}
    }
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        age_group = request.args.get('age_group')
        complexity = request.args.get('complexity')
        diagnosis = request.args.get('diagnosis')
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100
        offset = max(int(request.args.get('offset', 0)), 0)
        sort = request.args.get('sort', 'case_id')
        order = request.args.get('order', 'asc')
        
        # Get data loader
        data_loader = current_app.data_loader
        
        # Build filter parameters
        filter_params = {}
        if category:
            filter_params['category'] = category.split(',') if ',' in category else category
        if age_group:
            filter_params['age_group'] = age_group.split(',') if ',' in age_group else age_group
        if complexity:
            filter_params['complexity'] = complexity.split(',') if ',' in complexity else complexity
        if diagnosis:
            filter_params['diagnosis'] = diagnosis.split(',') if ',' in diagnosis else diagnosis
        
        # Get filtered cases
        filtered_cases = data_loader.get_filtered_cases(**filter_params)
        
        # Apply sorting
        if sort == 'difficulty':
            difficulty_order = {'basic': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
            filtered_cases.sort(key=lambda x: difficulty_order.get(x.get('complexity', 'basic'), 1))
        elif sort == 'category':
            filtered_cases.sort(key=lambda x: x.get('category', ''))
        elif sort == 'age_group':
            age_order = {'child': 1, 'adolescent': 2, 'adult': 3, 'older_adult': 4}
            filtered_cases.sort(key=lambda x: age_order.get(x.get('age_group', 'adult'), 3))
        else:  # case_id or default
            filtered_cases.sort(key=lambda x: x.get('case_id', ''))
        
        # Apply sort order
        if order == 'desc':
            filtered_cases.reverse()
        
        # Apply pagination
        total_count = len(filtered_cases)
        paginated_cases = filtered_cases[offset:offset + limit]
        
        # Format case data for API response
        cases_response = []
        for case in paginated_cases:
            case_data = {
                'case_id': case.get('case_id'),
                'category': case.get('category'),
                'age_group': case.get('age_group'),
                'complexity': case.get('complexity'),
                'diagnosis': case.get('diagnosis'),
                'narrative_preview': case.get('narrative', '')[:200] + '...' if len(case.get('narrative', '')) > 200 else case.get('narrative', ''),
                'mse_preview': case.get('MSE', '')[:150] + '...' if len(case.get('MSE', '')) > 150 else case.get('MSE', '')
            }
            cases_response.append(case_data)
        
        return jsonify({
            'cases': cases_response,
            'total_count': total_count,
            'filters_applied': filter_params,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'sort_info': {
                'sort_by': sort,
                'order': order
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Case browsing error: {str(e)}")
        return jsonify({
            'error': 'Failed to browse cases',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/<case_id>', methods=['GET'])
def get_case(case_id):
    """
    Get specific case details.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "case_id": "string",
        "category": "string",
        "age_group": "string",
        "complexity": "string",
        "diagnosis": "string",
        "narrative": "string",
        "MSE": "string"
    }
    """
    try:
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get case by ID
        case = data_loader.get_case_by_id(case_id)
        
        if not case:
            return jsonify({
                'error': 'Case not found',
                'message': f'Case with ID {case_id} not found'
            }), 404
        
        # Get diagnosis details
        diagnosis_details = data_loader.get_diagnosis_by_name(case.get('diagnosis', ''))
        
        return jsonify({
            'case_id': case.get('case_id'),
            'category': case.get('category'),
            'age_group': case.get('age_group'),
            'complexity': case.get('complexity'),
            'diagnosis': case.get('diagnosis'),
            'diagnosis_details': diagnosis_details,
            'narrative': case.get('narrative'),
            'MSE': case.get('MSE'),
            'retrieved_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get case error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve case',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/search', methods=['GET'])
@jwt_required()
def search_cases():
    """
    Search cases by text query.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - q: Search query
    - category: Filter by category
    - age_group: Filter by age group
    - complexity: Filter by complexity
    - limit: Number of results to return (default: 20)
    - offset: Offset for pagination (default: 0)
    
    Response:
    {
        "cases": [...],
        "total_count": 25,
        "search_query": "string",
        "pagination": {...}
    }
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        category = request.args.get('category')
        age_group = request.args.get('age_group')
        complexity = request.args.get('complexity')
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        
        if not query:
            return jsonify({
                'error': 'Missing search query',
                'message': 'Search query parameter "q" is required'
            }), 400
        
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get all cases first (simplified approach)
        # In a real implementation, you'd use proper text search
        all_cases = data_loader.get_filtered_cases(
            category=category,
            age_group=age_group,
            complexity=complexity
        )
        
        # Simple text search (case-insensitive)
        query_lower = query.lower()
        matching_cases = []
        
        for case in all_cases:
            # Search in narrative, MSE, diagnosis, and category
            searchable_text = ' '.join([
                case.get('narrative', ''),
                case.get('MSE', ''),
                case.get('diagnosis', ''),
                case.get('category', ''),
                case.get('case_id', '')
            ]).lower()
            
            if query_lower in searchable_text:
                matching_cases.append(case)
        
        # Sort by relevance (simplified - just put exact matches first)
        matching_cases.sort(key=lambda x: (
            query_lower in x.get('case_id', '').lower(),
            query_lower in x.get('diagnosis', '').lower(),
            query_lower in x.get('category', '').lower()
        ), reverse=True)
        
        # Apply pagination
        total_count = len(matching_cases)
        paginated_cases = matching_cases[offset:offset + limit]
        
        # Format case data
        cases_response = []
        for case in paginated_cases:
            case_data = {
                'case_id': case.get('case_id'),
                'category': case.get('category'),
                'age_group': case.get('age_group'),
                'complexity': case.get('complexity'),
                'diagnosis': case.get('diagnosis'),
                'narrative_preview': case.get('narrative', '')[:200] + '...' if len(case.get('narrative', '')) > 200 else case.get('narrative', ''),
                'relevance_score': _calculate_relevance_score(query, case)
            }
            cases_response.append(case_data)
        
        return jsonify({
            'cases': cases_response,
            'total_count': total_count,
            'search_query': query,
            'filters_applied': {
                'category': category,
                'age_group': age_group,
                'complexity': complexity
            },
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Case search error: {str(e)}")
        return jsonify({
            'error': 'Failed to search cases',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all available case categories.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "categories": [...],
        "count": 15
    }
    """
    try:
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get all categories
        categories = data_loader.get_categories()
        
        # Get case counts for each category
        category_counts = {}
        for category in categories:
            cases_in_category = data_loader.get_filtered_cases(category=category)
            category_counts[category] = len(cases_in_category)
        
        # Format response
        categories_response = []
        for category in categories:
            categories_response.append({
                'name': category,
                'case_count': category_counts.get(category, 0),
                'display_name': category.replace('_', ' ').title()
            })
        
        # Sort by case count (descending)
        categories_response.sort(key=lambda x: x['case_count'], reverse=True)
        
        return jsonify({
            'categories': categories_response,
            'count': len(categories_response)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get categories error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve categories',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/age-groups', methods=['GET'])
def get_age_groups():
    """
    Get all available age groups.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "age_groups": [...],
        "count": 4
    }
    """
    try:
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get all age groups
        age_groups = data_loader.get_age_groups()
        
        # Get case counts for each age group
        age_group_counts = {}
        for age_group in age_groups:
            cases_in_age_group = data_loader.get_filtered_cases(age_group=age_group)
            age_group_counts[age_group] = len(cases_in_age_group)
        
        # Format response
        age_groups_response = []
        for age_group in age_groups:
            age_groups_response.append({
                'name': age_group,
                'case_count': age_group_counts.get(age_group, 0),
                'display_name': age_group.replace('_', ' ').title()
            })
        
        # Sort by case count (descending)
        age_groups_response.sort(key=lambda x: x['case_count'], reverse=True)
        
        return jsonify({
            'age_groups': age_groups_response,
            'count': len(age_groups_response)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get age groups error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve age groups',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/complexity-levels', methods=['GET'])
def get_complexity_levels():
    """
    Get all available complexity levels.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "complexity_levels": [...],
        "count": 4
    }
    """
    try:
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get all complexity levels
        complexity_levels = data_loader.get_complexity_levels()
        
        # Get case counts for each complexity level
        complexity_counts = {}
        for complexity in complexity_levels:
            cases_in_complexity = data_loader.get_filtered_cases(complexity=complexity)
            complexity_counts[complexity] = len(cases_in_complexity)
        
        # Format response
        complexity_response = []
        for complexity in complexity_levels:
            complexity_response.append({
                'name': complexity,
                'case_count': complexity_counts.get(complexity, 0),
                'display_name': complexity.replace('_', ' ').title(),
                'difficulty_order': _get_difficulty_order(complexity)
            })
        
        # Sort by difficulty order
        complexity_response.sort(key=lambda x: x['difficulty_order'])
        
        return jsonify({
            'complexity_levels': complexity_response,
            'count': len(complexity_response)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get complexity levels error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve complexity levels',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/diagnoses', methods=['GET'])
@jwt_required()
def get_diagnoses():
    """
    Get all available diagnoses.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - category: Filter by category
    - limit: Number of results to return (default: 50)
    
    Response:
    {
        "diagnoses": [...],
        "total_count": 150
    }
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        limit = min(int(request.args.get('limit', 50)), 200)
        
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get all diagnoses
        all_diagnoses = data_loader.load_diagnoses()
        
        # Filter by category if specified
        if category:
            diagnoses = [d for d in all_diagnoses if d.get('category') == category]
        else:
            diagnoses = all_diagnoses
        
        # Format response
        diagnoses_response = []
        for diagnosis in diagnoses[:limit]:
            diagnosis_data = {
                'name': diagnosis.get('name'),
                'category': diagnosis.get('category'),
                'prevalence_rate': diagnosis.get('prevalence_rate'),
                'criteria_summary': diagnosis.get('criteria_summary', '')[:200] + '...' if len(diagnosis.get('criteria_summary', '')) > 200 else diagnosis.get('criteria_summary', '')
            }
            diagnoses_response.append(diagnosis_data)
        
        return jsonify({
            'diagnoses': diagnoses_response,
            'total_count': len(diagnoses),
            'filters_applied': {
                'category': category
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get diagnoses error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve diagnoses',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/random', methods=['GET'])
@jwt_required()
def get_random_cases():
    """
    Get random cases for practice.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - count: Number of cases to return (default: 5)
    - category: Filter by category
    - complexity: Filter by complexity
    - exclude_seen: Exclude cases user has already completed
    
    Response:
    {
        "cases": [...],
        "count": 5
    }
    """
    try:
        # Get query parameters
        count = min(int(request.args.get('count', 5)), 20)
        category = request.args.get('category')
        complexity = request.args.get('complexity')
        exclude_seen = request.args.get('exclude_seen', 'false').lower() == 'true'
        
        # Get user profile if excluding seen cases
        user_id = get_jwt_identity()
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        
        # Get data loader
        data_loader = current_app.data_loader
        
        # Get filtered cases
        filtered_cases = data_loader.get_filtered_cases(
            category=category,
            complexity=complexity
        )
        
        # Exclude seen cases if requested
        if exclude_seen and profile:
            seen_case_ids = {case.case_id for case in profile.completed_cases}
            filtered_cases = [case for case in filtered_cases if case.get('case_id') not in seen_case_ids]
        
        # Randomly select cases
        import random
        if len(filtered_cases) <= count:
            selected_cases = filtered_cases
        else:
            selected_cases = random.sample(filtered_cases, count)
        
        # Format response
        cases_response = []
        for case in selected_cases:
            case_data = {
                'case_id': case.get('case_id'),
                'category': case.get('category'),
                'age_group': case.get('age_group'),
                'complexity': case.get('complexity'),
                'diagnosis': case.get('diagnosis'),
                'narrative_preview': case.get('narrative', '')[:200] + '...' if len(case.get('narrative', '')) > 200 else case.get('narrative', '')
            }
            cases_response.append(case_data)
        
        return jsonify({
            'cases': cases_response,
            'count': len(cases_response),
            'filters_applied': {
                'category': category,
                'complexity': complexity,
                'exclude_seen': exclude_seen
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get random cases error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve random cases',
            'message': 'An unexpected error occurred'
        }), 500


def _calculate_relevance_score(query, case):
    """Calculate a simple relevance score for search results."""
    query_lower = query.lower()
    score = 0
    
    # Exact match in case ID
    if query_lower in case.get('case_id', '').lower():
        score += 10
    
    # Exact match in diagnosis
    if query_lower in case.get('diagnosis', '').lower():
        score += 8
    
    # Exact match in category
    if query_lower in case.get('category', '').lower():
        score += 6
    
    # Partial matches in narrative
    narrative_words = case.get('narrative', '').lower().split()
    query_words = query_lower.split()
    for query_word in query_words:
        if query_word in narrative_words:
            score += 2
    
    return score


@cases_bp.route('/<case_id>/bookmark', methods=['POST'])
@jwt_required()
def update_bookmark(case_id):
    """
    Update bookmark status for a case.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body:
    {
        "bookmarked": true
    }
    
    Response:
    {
        "success": true,
        "bookmarked": true
    }
    """
    try:
        data = request.get_json()
        if not data or 'bookmarked' not in data:
            return jsonify({
                'error': 'Missing bookmark status',
                'message': 'Bookmarked status is required'
            }), 400
        
        bookmarked = data['bookmarked']
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Update bookmark status
        profile = user_manager.load_user(user_id)
        if profile:
            if bookmarked:
                if case_id not in profile.bookmarked_cases:
                    profile.bookmarked_cases.append(case_id)
            else:
                if case_id in profile.bookmarked_cases:
                    profile.bookmarked_cases.remove(case_id)
            
            user_manager.save_user(profile)
        
        return jsonify({
            'success': True,
            'bookmarked': bookmarked
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update bookmark error: {str(e)}")
        return jsonify({
            'error': 'Failed to update bookmark',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/<case_id>/notes', methods=['POST'])
@jwt_required()
def update_notes(case_id):
    """
    Update notes for a case.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body:
    {
        "notes": "User notes here..."
    }
    
    Response:
    {
        "success": true,
        "notes": "User notes here..."
    }
    """
    try:
        data = request.get_json()
        if not data or 'notes' not in data:
            return jsonify({
                'error': 'Missing notes',
                'message': 'Notes content is required'
            }), 400
        
        notes = data['notes']
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Update notes
        profile = user_manager.load_user(user_id)
        if profile:
            if not profile.case_notes:
                profile.case_notes = {}
            profile.case_notes[case_id] = notes
            user_manager.save_user(profile)
        
        return jsonify({
            'success': True,
            'notes': notes
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update notes error: {str(e)}")
        return jsonify({
            'error': 'Failed to update notes',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/<case_id>/progress', methods=['GET'])
@jwt_required()
def get_case_progress(case_id):
    """
    Get user progress for a specific case.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "case_id": "string",
        "completed": false,
        "score": null,
        "attempts": 0,
        "last_attempt": null,
        "bookmarked": false,
        "notes": ""
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Get user profile
        profile = user_manager.load_user(user_id)
        
        if not profile:
            return jsonify({
                'case_id': case_id,
                'completed': False,
                'score': None,
                'attempts': 0,
                'last_attempt': None,
                'bookmarked': False,
                'notes': ''
            }), 200
        
        # Find case progress
        case_progress = None
        for completed_case in profile.completed_cases:
            if completed_case.case_id == case_id:
                case_progress = completed_case
                break
        
        return jsonify({
            'case_id': case_id,
            'completed': case_progress is not None,
            'score': case_progress.score if case_progress else None,
            'attempts': case_progress.attempts if case_progress else 0,
            'last_attempt': case_progress.completed_at.isoformat() if case_progress and case_progress.completed_at else None,
            'bookmarked': case_id in profile.bookmarked_cases,
            'notes': profile.case_notes.get(case_id, '') if profile.case_notes else ''
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get case progress error: {str(e)}")
        return jsonify({
            'error': 'Failed to get case progress',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/<case_id>/progress', methods=['PUT'])
@jwt_required()
def update_case_progress(case_id):
    """
    Update user progress for a specific case.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Body:
    {
        "score": 85,
        "attempts": 2,
        "completed": true
    }
    
    Response:
    {
        "success": true,
        "progress": {...}
    }
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Get user profile
        profile = user_manager.load_user(user_id)
        
        if not profile:
            return jsonify({
                'error': 'User profile not found',
                'message': 'Unable to find user profile'
            }), 404
        
        # Update or create case progress
        from datetime import datetime
        case_progress = None
        for i, completed_case in enumerate(profile.completed_cases):
            if completed_case.case_id == case_id:
                case_progress = completed_case
                if data.get('score') is not None:
                    case_progress.score = data['score']
                if data.get('attempts') is not None:
                    case_progress.attempts = data['attempts']
                if data.get('completed'):
                    case_progress.completed_at = datetime.now()
                break
        
        if not case_progress and data.get('completed'):
            # Create new progress entry
            try:
                from modules.user_manager import CompletedCase
                case_progress = CompletedCase(
                    case_id=case_id,
                    score=data.get('score', 0),
                    attempts=data.get('attempts', 1),
                    completed_at=datetime.now()
                )
            except ImportError:
                # Fallback if CompletedCase is not available
                case_progress = type('CompletedCase', (), {
                    'case_id': case_id,
                    'score': data.get('score', 0),
                    'attempts': data.get('attempts', 1),
                    'completed_at': datetime.now()
                })()
            profile.completed_cases.append(case_progress)
        
        user_manager.save_user(profile)
        
        return jsonify({
            'success': True,
            'progress': {
                'case_id': case_id,
                'completed': case_progress is not None,
                'score': case_progress.score if case_progress else None,
                'attempts': case_progress.attempts if case_progress else 0,
                'last_attempt': case_progress.completed_at.isoformat() if case_progress and case_progress.completed_at else None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Update case progress error: {str(e)}")
        return jsonify({
            'error': 'Failed to update case progress',
            'message': 'An unexpected error occurred'
        }), 500


@cases_bp.route('/user/progress', methods=['GET'])
@jwt_required()
def get_user_cases_progress():
    """
    Get progress for all cases for the current user.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - limit: Number of cases to return (default: 50)
    - offset: Offset for pagination (default: 0)
    
    Response:
    {
        "progress": [...],
        "total_count": 25,
        "pagination": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 50)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        
        # Get user manager
        user_manager = current_app.user_manager
        
        # Get user profile
        profile = user_manager.load_user(user_id)
        
        if not profile:
            return jsonify({
                'progress': [],
                'total_count': 0,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': False
                }
            }), 200
        
        # Build progress list
        progress_list = []
        for completed_case in profile.completed_cases:
            progress_list.append({
                'case_id': completed_case.case_id,
                'completed': True,
                'score': completed_case.score,
                'attempts': completed_case.attempts,
                'last_attempt': completed_case.completed_at.isoformat() if completed_case.completed_at else None,
                'bookmarked': completed_case.case_id in profile.bookmarked_cases,
                'notes': profile.case_notes.get(completed_case.case_id, '') if profile.case_notes else ''
            })
        
        # Add bookmarked cases that aren't completed
        for case_id in profile.bookmarked_cases:
            if not any(p['case_id'] == case_id for p in progress_list):
                progress_list.append({
                    'case_id': case_id,
                    'completed': False,
                    'score': None,
                    'attempts': 0,
                    'last_attempt': None,
                    'bookmarked': True,
                    'notes': profile.case_notes.get(case_id, '') if profile.case_notes else ''
                })
        
        # Sort by last attempt (most recent first)
        progress_list.sort(key=lambda x: x['last_attempt'] or '', reverse=True)
        
        # Apply pagination
        total_count = len(progress_list)
        paginated_progress = progress_list[offset:offset + limit]
        
        return jsonify({
            'progress': paginated_progress,
            'total_count': total_count,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user cases progress error: {str(e)}")
        return jsonify({
            'error': 'Failed to get user progress',
            'message': 'An unexpected error occurred'
        }), 500


def _get_difficulty_order(complexity):
    """Get numeric order for complexity levels."""
    order_map = {
        'basic': 1,
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3,
        'expert': 4,
        'high': 3
    }
    return order_map.get(complexity.lower(), 2)