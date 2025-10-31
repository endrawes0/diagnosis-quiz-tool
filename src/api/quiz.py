"""
Quiz API routes.
Handles quiz generation, submission, and history management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
import random

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """
    Generate a new quiz based on configuration.

    Headers:
    Authorization: Bearer <access_token>

    Request Body:
    {
        "num_questions": 10,
        "num_choices": 4,
        "categories": ["Depressive Disorders", "Anxiety Disorders", "Schizophrenia Spectrum and Other Psychotic Disorders"],
        "age_groups": ["adult", "adolescent"],
        "complexities": ["basic", "intermediate"],
        "adaptive_mode": true,
        "differential_mode": false,
        "multi_case_matching": false,
        "shuffle": true
    }

    Response:
    {
        "quiz_id": "string",
        "quiz_data": {...},
        "generated_at": "timestamp"
    }
    """
    try:
        # For local usage, skip authentication and user progress
        user_id = "anonymous"  # For logging purposes
        data = request.get_json()

        current_app.logger.info(f"Quiz generation request received: {data}")

        if not data:
            data = {}
            current_app.logger.warning("No JSON data received, using defaults")

        # Set up quiz generator without user progress for local usage
        quiz_generator = current_app.quiz_generator
        quiz_generator.user_progress = None

        # Validate configuration
        config = {
            'num_questions': min(data.get('num_questions', 10), 50),  # Max 50 questions
            'num_choices': min(max(data.get('num_choices', 4), 2), 6),  # 2-6 choices
            'categories': data.get('categories', []),
            'age_groups': data.get('age_groups', []),
            'complexities': data.get('complexities', []),
            'difficulty_tiers': data.get('difficulty_tiers', []),
            'clinical_specifiers': data.get('clinical_specifiers', []),
            'course_specifiers': data.get('course_specifiers', []),
            'symptom_variants': data.get('symptom_variants', []),
            'diagnoses': data.get('diagnoses', []),
            'exclude_categories': data.get('exclude_categories', []),
            'exclude_age_groups': data.get('exclude_age_groups', []),
            'exclude_complexities': data.get('exclude_complexities', []),
            'exclude_difficulty_tiers': data.get('exclude_difficulty_tiers', []),
            'exclude_clinical_specifiers': data.get('exclude_clinical_specifiers', []),
            'exclude_course_specifiers': data.get('exclude_course_specifiers', []),
            'exclude_symptom_variants': data.get('exclude_symptom_variants', []),
            'exclude_diagnoses': data.get('exclude_diagnoses', []),
            'adaptive_mode': data.get('adaptive_mode', False),
            'differential_mode': data.get('differential_mode', False),
            'multi_case_matching': data.get('multi_case_matching', False),
            'streak_sequencing': data.get('streak_sequencing', False),
            'time_adjustment': data.get('time_adjustment', False),
            'bonus_xp_opportunities': data.get('bonus_xp_opportunities', False),
            'shuffle': data.get('shuffle', True),
            'seed': data.get('seed'),  # For reproducible quizzes
            'untimed_mode': data.get('untimed_mode', False)
        }

        current_app.logger.info(f"Using config: {config}")

        # Generate quiz
        current_app.logger.info("Starting quiz generation...")
        quiz_data = quiz_generator.generate_quiz(config)
        current_app.logger.info(f"Quiz generated successfully with {len(quiz_data.get('questions', []))} questions")

        # Generate unique quiz ID
        quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"

        # Store quiz data (in a real implementation, you'd use a database)
        # For now, we'll return the quiz data directly

        current_app.logger.info(f"Quiz generated for user {user_id}: {quiz_id}")

        return jsonify({
            'quiz_id': quiz_id,
            'quiz_data': quiz_data,
            'generated_at': datetime.now().isoformat(),
            'config_used': config
        }), 201

    except ValueError as e:
        current_app.logger.error(f"Quiz generation validation error: {str(e)}")
        return jsonify({
            'error': 'Quiz generation failed',
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Quiz generation error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Quiz generation failed',
            'message': 'An unexpected error occurred during quiz generation',
            'details': str(e) if current_app.debug else None
        }), 500


@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    """
    Submit quiz answers for scoring.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "quiz_id": "string",
        "answers": [
            {
                "question_number": 1,
                "selected_answer": "string",
                "time_taken": 45
            }
        ],
        "total_time": 300,
        "quiz_config": {...}
    }
    
    Response:
    {
        "score": {...},
        "xp_earned": 150,
        "achievements_unlocked": [...],
        "recommendations": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'answers' not in data:
            return jsonify({
                'error': 'Missing answers',
                'message': 'Quiz answers are required'
            }), 400
        
        quiz_id = data.get('quiz_id', f"quiz_{uuid.uuid4().hex[:8]}")
        answers = data['answers']
        total_time = data.get('total_time', 0)
        quiz_config = data.get('quiz_config', {})
        
        # Get user profile
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Score the quiz
        scoring_engine = current_app.scoring_engine
        quiz_generator = current_app.quiz_generator
        
        # For each answer, calculate score and XP
        total_xp = 0
        results = []
        correct_count = 0
        
        for answer in answers:
            question_num = answer.get('question_number', 0)
            selected_answer = answer.get('selected_answer', '')
            time_taken = answer.get('time_taken', 0)

            # In a real implementation, you'd retrieve the actual question data
            # For now, we'll simulate scoring
            is_correct = answer.get('is_correct', False)  # This would come from quiz data

            question_xp = 0
            if is_correct:
                correct_count += 1
                # Calculate XP based on time and difficulty
                base_xp = 10
                time_bonus = max(0, 5 - time_taken // 30)  # Bonus for fast answers
                question_xp = base_xp + time_bonus
                total_xp += question_xp

            results.append({
                'question_number': question_num,
                'selected_answer': selected_answer,
                'is_correct': is_correct,
                'time_taken': time_taken,
                'xp_earned': question_xp
            })
        
        # Calculate overall score
        total_questions = len(answers)
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        score_data = {
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'accuracy': accuracy,
            'total_time': total_time,
            'average_time_per_question': total_time / total_questions if total_questions > 0 else 0,
            'total_xp': total_xp,
            'results': results
        }
        
        # Update user profile
        for result in results:
            case_result = {
                'case_id': f"case_{result['question_number']}",
                'xp_earned': result['xp_earned'],
                'accuracy': 100 if result['is_correct'] else 0,
                'time_taken': result['time_taken'],
                'is_correct': result['is_correct'],
                'difficulty': quiz_config.get('complexities', ['basic'])[0],
                'category': quiz_config.get('categories', ['general'])[0]
            }
            profile.add_completed_case(case_result)
        
        # Add XP to user progress
        profile.progress.add_xp(total_xp, "quiz_completion")
        
        # Check for achievements
        achievements_unlocked = []
        if accuracy >= 90:
            achievements_unlocked.append({
                'id': 'perfect_score',
                'name': 'Perfect Score',
                'description': 'Achieved 90% or higher accuracy'
            })
        
        if correct_count == total_questions and total_questions >= 10:
            achievements_unlocked.append({
                'id': 'quiz_master',
                'name': 'Quiz Master',
                'description': 'Completed a 10+ question quiz with 100% accuracy'
            })
        
        # Generate recommendations
        recommendations = []
        if accuracy < 70:
            recommendations.append({
                'type': 'practice',
                'message': 'Consider reviewing the categories where you struggled',
                'categories': ['Depressive Disorders', 'Anxiety Disorders']  # Would be calculated
            })
        
        # Save user profile
        user_manager.save_user(profile)
        
        current_app.logger.info(f"Quiz submitted for user {user_id}: {quiz_id}, Score: {accuracy:.1f}%")
        
        return jsonify({
            'quiz_id': quiz_id,
            'score': score_data,
            'xp_earned': total_xp,
            'achievements_unlocked': achievements_unlocked,
            'recommendations': recommendations,
            'submitted_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Quiz submission error: {str(e)}")
        return jsonify({
            'error': 'Quiz submission failed',
            'message': 'An unexpected error occurred during quiz submission'
        }), 500


@quiz_bp.route('/history', methods=['GET'])
@jwt_required()
def get_quiz_history():
    """
    Get user's quiz history.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - limit: Number of quizzes to return (default: 10)
    - offset: Offset for pagination (default: 0)
    
    Response:
    {
        "quizzes": [...],
        "total_count": 25,
        "pagination": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 10)), 100)  # Max 100
        offset = max(int(request.args.get('offset', 0)), 0)
        
        # Get user profile
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Get completed cases (which represent quiz attempts)
        completed_cases = profile.get_recent_cases(limit + offset)
        
        # Group cases into quiz sessions (simplified approach)
        # In a real implementation, you'd have proper quiz session tracking
        quizzes = []
        for i, case in enumerate(completed_cases[offset:offset + limit]):
            quiz_summary = {
                'quiz_id': f"quiz_session_{case.completed_at.strftime('%Y%m%d_%H%M%S')}",
                'completed_at': case.completed_at.isoformat(),
                'total_questions': 1,  # Simplified - each case is one question
                'correct_answers': 1 if case.is_correct else 0,
                'accuracy': 100 if case.is_correct else 0,
                'total_time': case.time_taken,
                'xp_earned': case.xp_earned,
                'difficulty': case.difficulty,
                'category': case.category
            }
            quizzes.append(quiz_summary)
        
        return jsonify({
            'quizzes': quizzes,
            'total_count': len(profile.completed_cases),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < len(profile.completed_cases)
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Quiz history error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve quiz history',
            'message': 'An unexpected error occurred'
        }), 500


@quiz_bp.route('/<quiz_id>/answer', methods=['POST'])
def submit_answer(quiz_id):
    """
    Submit an individual answer for a quiz question.

    Request Body for regular questions:
    {
        "question_id": 1,
        "answer": "selected_option"
    }

    Request Body for multi-case matching:
    {
        "question_id": 1,
        "answer": {"case1": {"id": 0, "text": "Diagnosis A"}, "case2": {"id": 1, "text": "Diagnosis B"}, ...}
    }

    Response:
    {
        "correct": true,
        "feedback": "Correct! Well done.",
        "xp_earned": 10
    }
    """
    try:
        data = request.get_json()

        if not data or 'question_id' not in data or 'answer' not in data:
            return jsonify({
                'error': 'Missing data',
                'message': 'question_id and answer are required'
            }), 400

        question_id = data['question_id']
        answer = data['answer']

        # Handle multi-case matching answers
        if isinstance(answer, dict) and any(isinstance(v, dict) and 'text' in v for v in answer.values()):
            # This is a multi-case matching answer
            # In a real implementation, you'd validate against stored quiz data
            # For now, simulate success for multi-case (validation happens on frontend)
            is_correct = True
            feedback = "Multi-case matching submitted successfully. Results will be shown."
            xp_earned = 15  # Higher XP for multi-case questions
        else:
            # Regular single-answer question
            # In a real implementation, you'd validate against stored quiz data
            # For now, simulate basic response
            is_correct = random.choice([True, False])  # Placeholder logic
            feedback = "Correct! Well done." if is_correct else "Incorrect. Review the case details."
            xp_earned = 10 if is_correct else 0

        return jsonify({
            'correct': is_correct,
            'feedback': feedback,
            'xp_earned': xp_earned
        }), 200

    except Exception as e:
        current_app.logger.error(f"Submit answer error: {str(e)}")
        return jsonify({
            'error': 'Failed to submit answer',
            'message': 'An unexpected error occurred'
        }), 500


@quiz_bp.route('/<quiz_id>/results', methods=['GET'])
def get_quiz_results(quiz_id):
    """
    Get results for a completed quiz.

    Response:
    {
        "quiz_id": "string",
        "score": 85,
        "total_questions": 10,
        "correct_answers": 8,
        "time_taken": 450,
        "xp_earned": 80,
        "results": [...]
    }
    """
    try:
        # In a real implementation, you'd retrieve results from database
        # For now, simulate results
        total_questions = 10
        correct_answers = random.randint(6, 10)
        score = int((correct_answers / total_questions) * 100)
        time_taken = random.randint(300, 600)
        xp_earned = correct_answers * 10

        results = []
        for i in range(total_questions):
            results.append({
                'question_number': i + 1,
                'correct': i < correct_answers,
                'time_taken': time_taken // total_questions,
                'xp_earned': 10 if i < correct_answers else 0
            })

        return jsonify({
            'quiz_id': quiz_id,
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'time_taken': time_taken,
            'xp_earned': xp_earned,
            'results': results
        }), 200

    except Exception as e:
        current_app.logger.error(f"Get quiz results error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve quiz results',
            'message': 'An unexpected error occurred'
        }), 500


@quiz_bp.route('/<quiz_id>', methods=['GET'])
@jwt_required()
def get_quiz(quiz_id):
    """
    Get specific quiz details.

    Headers:
    Authorization: Bearer <access_token>

    Response:
    {
        "quiz_id": "string",
        "quiz_data": {...},
        "created_at": "timestamp"
    }
    """
    try:
        user_id = get_jwt_identity()

        # In a real implementation, you'd retrieve the quiz from a database
        # For now, we'll return a not found response
        return jsonify({
            'error': 'Quiz not found',
            'message': 'The requested quiz could not be found'
        }), 404

    except Exception as e:
        current_app.logger.error(f"Get quiz error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve quiz',
            'message': 'An unexpected error occurred'
        }), 500


@quiz_bp.route('/adaptive-config', methods=['GET'])
@jwt_required()
def get_adaptive_config():
    """
    Get adaptive quiz configuration based on user performance.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "recommended_config": {...},
        "weak_areas": [...],
        "strength_areas": [...]
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user profile
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'message': 'User profile not found'
            }), 404
        
        # Analyze user performance
        recent_performance = profile.progress.performance_metrics.recent_performance
        specialties = profile.progress.specialties
        
        # Identify weak and strong areas
        weak_areas = []
        strength_areas = []
        
        for category, proficiency in specialties.items():
            if proficiency.accuracy < 70:
                weak_areas.append({
                    'category': category,
                    'accuracy': proficiency.accuracy,
                    'recommended_focus': True
                })
            elif proficiency.accuracy >= 85:
                strength_areas.append({
                    'category': category,
                    'accuracy': proficiency.accuracy,
                    'mastery_level': proficiency.level
                })
        
        # Generate recommended configuration
        recommended_config = {
            'num_questions': 10,
            'adaptive_mode': True,
            'categories': [area['category'] for area in weak_areas[:3]] if weak_areas else [],
            'complexities': ['basic', 'intermediate'] if profile.progress.level < 5 else ['intermediate', 'advanced'],
            'focus_on_weaknesses': len(weak_areas) > 0
        }
        
        return jsonify({
            'recommended_config': recommended_config,
            'weak_areas': weak_areas,
            'strength_areas': strength_areas,
            'current_level': profile.progress.level,
            'overall_accuracy': profile.statistics.overall_accuracy
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Adaptive config error: {str(e)}")
        return jsonify({
            'error': 'Failed to generate adaptive configuration',
            'message': 'An unexpected error occurred'
        }), 500


@quiz_bp.route('/combination', methods=['POST'])
@jwt_required()
def generate_combination_quiz():
    """
    Generate a case combination quiz for differential diagnosis practice.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Request Body:
    {
        "num_combinations": 5,
        "cases_per_combination": 2,
        "combination_type": "similar"
    }
    
    Response:
    {
        "quiz_id": "string",
        "quiz_data": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            data = {}
        
        # Get user profile
        user_manager = current_app.user_manager
        profile = user_manager.load_user(user_id)
        
        # Set up quiz generator
        quiz_generator = current_app.quiz_generator
        quiz_generator.user_progress = profile.progress if profile else None
        
        # Configuration for combination quiz
        config = {
            'num_combinations': min(data.get('num_combinations', 5), 10),
            'cases_per_combination': min(max(data.get('cases_per_combination', 2), 2), 4),
            'combination_type': data.get('combination_type', 'similar'),
            'categories': data.get('categories', []),
            'complexities': data.get('complexities', ['intermediate', 'advanced'])
        }
        
        # Generate combination quiz
        quiz_data = quiz_generator.generate_case_combination_quiz(config)
        
        # Generate quiz ID
        quiz_id = f"combo_quiz_{uuid.uuid4().hex[:8]}"
        
        current_app.logger.info(f"Combination quiz generated for user {user_id}: {quiz_id}")
        
        return jsonify({
            'quiz_id': quiz_id,
            'quiz_data': quiz_data,
            'generated_at': datetime.now().isoformat(),
            'config_used': config
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Combination quiz generation error: {str(e)}")
        return jsonify({
            'error': 'Combination quiz generation failed',
            'message': 'An unexpected error occurred'
        }), 500