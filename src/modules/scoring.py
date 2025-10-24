import json
import csv
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from io import StringIO
from enum import Enum
from dataclasses import dataclass, asdict


class ScoringMode(Enum):
    """Scoring modes for different evaluation approaches."""
    STRICT = "strict"
    LENIENT = "lenient"
    PARTIAL = "partial"


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    CSV = "csv"
    TEXT = "text"
    HTML = "html"


@dataclass
class QuestionResult:
    """Result data for a single question."""
    question_number: int
    case_id: str
    user_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    score: float
    max_score: float
    time_spent: float
    category: str
    age_group: str
    complexity: str
    feedback: str
    partial_credit_reason: Optional[str] = None


@dataclass
class PerformanceStats:
    """Performance statistics for a quiz session."""
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    total_score: float
    max_possible_score: float
    percentage_score: float
    average_time_per_question: float
    total_time_spent: float
    category_performance: Dict[str, Dict[str, Any]]
    complexity_performance: Dict[str, Dict[str, Any]]
    age_group_performance: Dict[str, Dict[str, Any]]
    difficulty_analysis: Dict[str, Any]
    time_analysis: Dict[str, Any]


class Scoring:
    """
    Comprehensive scoring system for diagnosis quizzes with detailed analytics,
    multiple scoring modes, export capabilities, and gamified progression.
    """
    
    def __init__(self, scoring_mode: ScoringMode = ScoringMode.STRICT, 
                 partial_credit_config: Optional[Dict[str, Any]] = None,
                 user_progress: Optional[Any] = None):
        """
        Initialize the Scoring system.
        
        Args:
            scoring_mode: Scoring mode (strict, lenient, partial)
            partial_credit_config: Configuration for partial credit scoring
        """
        self.scoring_mode = scoring_mode
        self.partial_credit_config = partial_credit_config or {
            'category_match_bonus': 0.25,
            'age_group_match_bonus': 0.15,
            'complexity_match_bonus': 0.10,
            'similarity_threshold': 0.7
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Setup logging if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Internal state
        self.quiz_data: Optional[Dict[str, Any]] = None
        self.user_answers: Dict[int, Dict[str, Any]] = {}
        self.question_results: List[QuestionResult] = []
        self.session_start_time: Optional[datetime] = None
        self.question_start_times: Dict[int, datetime] = {}
        
        # Diagnosis similarity cache for partial credit
        self._diagnosis_similarity_cache: Dict[Tuple[str, str], float] = {}
        
        # Progression system integration
        self.user_progress = user_progress
        self.session_xp_earned = 0
        self.achievements_awarded: List[str] = []
    
    def start_quiz_session(self, quiz_data: Dict[str, Any]) -> None:
        """
        Start a new quiz scoring session.
        
        Args:
            quiz_data: Quiz data dictionary from QuizGenerator
            
        Raises:
            ValueError: If quiz_data is invalid
        """
        try:
            self._validate_quiz_data(quiz_data)
            self.quiz_data = quiz_data
            self.user_answers = {}
            self.question_results = []
            self.session_start_time = datetime.now()
            self.question_start_times = {}
            self._diagnosis_similarity_cache = {}
            
            self.logger.info(f"Started quiz session with {len(quiz_data['questions'])} questions")
            
        except Exception as e:
            self.logger.error(f"Failed to start quiz session: {e}")
            raise
    
    def record_answer(self, question_number: int, user_answer: str, 
                     answer_time: Optional[float] = None) -> None:
        """
        Record a user's answer for a question.
        
        Args:
            question_number: Question number (1-based)
            user_answer: User's answer string
            answer_time: Time spent on question in seconds (auto-calculated if None)
            
        Raises:
            ValueError: If quiz session not started or question number invalid
        """
        if not self.quiz_data:
            raise ValueError("Quiz session not started. Call start_quiz_session() first.")
        
        if question_number < 1 or question_number > len(self.quiz_data['questions']):
            raise ValueError(f"Invalid question number: {question_number}")
        
        try:
            # Calculate time spent if not provided
            if answer_time is None:
                if question_number in self.question_start_times:
                    answer_time = (datetime.now() - self.question_start_times[question_number]).total_seconds()
                else:
                    answer_time = 0.0
                    self.logger.warning(f"No start time recorded for question {question_number}, using 0.0")
            
            # Store the answer
            self.user_answers[question_number] = {
                'answer': user_answer,
                'time_spent': answer_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.debug(f"Recorded answer for question {question_number}: {user_answer}")
            
        except Exception as e:
            self.logger.error(f"Failed to record answer for question {question_number}: {e}")
            raise
    
    def start_question_timer(self, question_number: int) -> None:
        """
        Start timing for a specific question.
        
        Args:
            question_number: Question number (1-based)
        """
        if not self.quiz_data:
            raise ValueError("Quiz session not started. Call start_quiz_session() first.")
        
        self.question_start_times[question_number] = datetime.now()
        self.logger.debug(f"Started timer for question {question_number}")
    
    def calculate_scores(self) -> PerformanceStats:
        """
        Calculate scores and generate performance statistics with progression integration.
        
        Returns:
            PerformanceStats object with comprehensive scoring data
            
        Raises:
            ValueError: If quiz session not started
        """
        if not self.quiz_data:
            raise ValueError("Quiz session not started. Call start_quiz_session() first.")
        
        try:
            self._evaluate_all_questions()
            stats = self._generate_performance_stats()
            
            # Update progression system if available
            if self.user_progress:
                self._update_progression_system(stats)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate scores: {e}")
            raise
    
    def _validate_quiz_data(self, quiz_data: Dict[str, Any]) -> None:
        """Validate quiz data structure."""
        required_keys = ['quiz_metadata', 'questions']
        for key in required_keys:
            if key not in quiz_data:
                raise ValueError(f"Missing required key in quiz_data: {key}")
        
        if not isinstance(quiz_data['questions'], list):
            raise ValueError("quiz_data['questions'] must be a list")
        
        if len(quiz_data['questions']) == 0:
            raise ValueError("Quiz must contain at least one question")
        
        # Validate each question
        for i, question in enumerate(quiz_data['questions']):
            required_question_keys = [
                'question_number', 'case_id', 'question_text', 
                'options', 'correct_answer', 'correct_index', 'case_metadata'
            ]
            for key in required_question_keys:
                if key not in question:
                    raise ValueError(f"Question {i+1} missing required key: {key}")
    
    def _evaluate_all_questions(self) -> None:
        """Evaluate all answered questions and generate results."""
        self.question_results = []
        
        if not self.quiz_data or 'questions' not in self.quiz_data:
            raise ValueError("Invalid quiz data: no questions available")
        
        for question in self.quiz_data['questions']:
            q_num = question['question_number']
            
            if q_num not in self.user_answers:
                # User didn't answer this question
                result = self._create_unanswered_result(question)
            else:
                # User answered this question
                user_answer_data = self.user_answers[q_num]
                result = self._evaluate_question(question, user_answer_data)
            
            self.question_results.append(result)
    
    def _evaluate_question(self, question: Dict[str, Any], 
                          user_answer_data: Dict[str, Any]) -> QuestionResult:
        """Evaluate a single answered question."""
        user_answer = user_answer_data['answer']
        correct_answer = question['correct_answer']
        time_spent = user_answer_data['time_spent']
        
        # Determine correctness and score based on scoring mode
        partial_reason = None
        if self.scoring_mode == ScoringMode.STRICT:
            is_correct, score, feedback = self._evaluate_strict(user_answer, correct_answer)
        elif self.scoring_mode == ScoringMode.LENIENT:
            is_correct, score, feedback = self._evaluate_lenient(user_answer, correct_answer)
        elif self.scoring_mode == ScoringMode.PARTIAL:
            is_correct, score, feedback, partial_reason = self._evaluate_partial(
                user_answer, correct_answer, question
            )
        else:
            raise ValueError(f"Unsupported scoring mode: {self.scoring_mode}")
        
        return QuestionResult(
            question_number=question['question_number'],
            case_id=question['case_id'],
            user_answer=user_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            score=score,
            max_score=1.0,
            time_spent=time_spent,
            category=question['case_metadata']['category'],
            age_group=question['case_metadata']['age_group'],
            complexity=question['case_metadata']['complexity'],
            feedback=feedback,
            partial_credit_reason=partial_reason
        )
    
    def _create_unanswered_result(self, question: Dict[str, Any]) -> QuestionResult:
        """Create a result for an unanswered question."""
        return QuestionResult(
            question_number=question['question_number'],
            case_id=question['case_id'],
            user_answer=None,
            correct_answer=question['correct_answer'],
            is_correct=False,
            score=0.0,
            max_score=1.0,
            time_spent=0.0,
            category=question['case_metadata']['category'],
            age_group=question['case_metadata']['age_group'],
            complexity=question['case_metadata']['complexity'],
            feedback="Question not answered"
        )
    
    def _evaluate_strict(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str]:
        """Strict evaluation - exact match required."""
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        score = 1.0 if is_correct else 0.0
        
        if is_correct:
            feedback = "Correct! Well done."
        else:
            feedback = f"Incorrect. The correct answer is: {correct_answer}"
        
        return is_correct, score, feedback
    
    def _evaluate_lenient(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str]:
        """Lenient evaluation - allows for minor variations."""
        user_clean = user_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        # Check for exact match
        if user_clean == correct_clean:
            return True, 1.0, "Correct! Well done."
        
        # Check for partial match (contains key words)
        user_words = set(user_clean.split())
        correct_words = set(correct_clean.split())
        
        # If user answer contains most of the correct words, consider it correct
        if correct_words and user_words:
            overlap = len(user_words & correct_words)
            similarity = overlap / len(correct_words)
            
            if similarity >= 0.8:  # 80% word overlap
                return True, 1.0, f"Correct! (Recognized similarity to: {correct_answer})"
        
        return False, 0.0, f"Incorrect. The correct answer is: {correct_answer}"
    
    def _evaluate_partial(self, user_answer: str, correct_answer: str, 
                         question: Dict[str, Any]) -> Tuple[bool, float, str, Optional[str]]:
        """Partial credit evaluation with multiple scoring factors."""
        user_clean = user_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        # Check for exact match first
        if user_clean == correct_clean:
            return True, 1.0, "Correct! Well done.", None
        
        score = 0.0
        partial_reasons = []
        
        # Category match bonus (simplified - just check if user answer contains category keywords)
        correct_category = question['case_metadata']['category']
        category_keywords = correct_category.split('_')
        for keyword in category_keywords:
            if keyword in user_clean:
                score += self.partial_credit_config['category_match_bonus']
                partial_reasons.append(f"Correct category: {correct_category}")
                break
        
        # Similarity-based partial credit
        similarity = self._calculate_diagnosis_similarity(user_answer, correct_answer)
        if similarity >= self.partial_credit_config['similarity_threshold']:
            partial_score = similarity * 0.5  # Max 0.5 points for similarity
            score += partial_score
            partial_reasons.append(f"Similar diagnosis ({similarity:.2f})")
        
        # Cap at 1.0
        score = min(score, 1.0)
        
        partial_reason = '; '.join(partial_reasons) if partial_reasons else None
        
        if score > 0:
            feedback = f"Partial credit ({score:.2f}/1.0). {', '.join(partial_reasons)}. Correct answer: {correct_answer}"
            return False, score, feedback, partial_reason
        else:
            feedback = f"Incorrect. The correct answer is: {correct_answer}"
            return False, 0.0, feedback, None
    
    def _calculate_diagnosis_similarity(self, diagnosis1: str, diagnosis2: str) -> float:
        """Calculate similarity between two diagnosis names."""
        cache_key = (diagnosis1.lower(), diagnosis2.lower())
        
        if cache_key in self._diagnosis_similarity_cache:
            return self._diagnosis_similarity_cache[cache_key]
        
        # Simple word-based similarity
        words1 = set(diagnosis1.lower().split())
        words2 = set(diagnosis2.lower().split())
        
        if not words1 or not words2:
            similarity = 0.0
        else:
            intersection = words1 & words2
            union = words1 | words2
            similarity = len(intersection) / len(union) if union else 0.0
        
        self._diagnosis_similarity_cache[cache_key] = similarity
        return similarity
    
    def _generate_performance_stats(self) -> PerformanceStats:
        """Generate comprehensive performance statistics."""
        total_questions = len(self.question_results)
        correct_answers = sum(1 for r in self.question_results if r.is_correct)
        incorrect_answers = total_questions - correct_answers
        total_score = sum(r.score for r in self.question_results)
        max_possible_score = total_questions * 1.0
        percentage_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0.0
        
        total_time_spent = sum(r.time_spent for r in self.question_results)
        average_time_per_question = total_time_spent / total_questions if total_questions > 0 else 0.0
        
        # Category performance
        category_performance = self._calculate_category_performance()
        
        # Complexity performance
        complexity_performance = self._calculate_complexity_performance()
        
        # Age group performance
        age_group_performance = self._calculate_age_group_performance()
        
        # Difficulty analysis
        difficulty_analysis = self._analyze_difficulty()
        
        # Time analysis
        time_analysis = self._analyze_time_patterns()
        
        return PerformanceStats(
            total_questions=total_questions,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            total_score=total_score,
            max_possible_score=max_possible_score,
            percentage_score=percentage_score,
            average_time_per_question=average_time_per_question,
            total_time_spent=total_time_spent,
            category_performance=category_performance,
            complexity_performance=complexity_performance,
            age_group_performance=age_group_performance,
            difficulty_analysis=difficulty_analysis,
            time_analysis=time_analysis
        )
    
    def _calculate_category_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance by diagnostic category."""
        category_stats = {}
        
        for result in self.question_results:
            category = result.category
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'time': 0.0
                }
            
            stats = category_stats[category]
            stats['total'] += 1
            if result.is_correct:
                stats['correct'] += 1
            stats['score'] += result.score
            stats['time'] += result.time_spent
        
        # Calculate percentages and averages
        for category, stats in category_stats.items():
            stats['accuracy'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            stats['average_score'] = stats['score'] / stats['total'] if stats['total'] > 0 else 0.0
            stats['average_time'] = stats['time'] / stats['total'] if stats['total'] > 0 else 0.0
        
        return category_stats
    
    def _calculate_complexity_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance by complexity level."""
        complexity_stats = {}
        
        for result in self.question_results:
            complexity = result.complexity
            if complexity not in complexity_stats:
                complexity_stats[complexity] = {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'time': 0.0
                }
            
            stats = complexity_stats[complexity]
            stats['total'] += 1
            if result.is_correct:
                stats['correct'] += 1
            stats['score'] += result.score
            stats['time'] += result.time_spent
        
        # Calculate percentages and averages
        for complexity, stats in complexity_stats.items():
            stats['accuracy'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            stats['average_score'] = stats['score'] / stats['total'] if stats['total'] > 0 else 0.0
            stats['average_time'] = stats['time'] / stats['total'] if stats['total'] > 0 else 0.0
        
        return complexity_stats
    
    def _calculate_age_group_performance(self) -> Dict[str, Dict[str, Any]]:
        """Calculate performance by age group."""
        age_group_stats = {}
        
        for result in self.question_results:
            age_group = result.age_group
            if age_group not in age_group_stats:
                age_group_stats[age_group] = {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'time': 0.0
                }
            
            stats = age_group_stats[age_group]
            stats['total'] += 1
            if result.is_correct:
                stats['correct'] += 1
            stats['score'] += result.score
            stats['time'] += result.time_spent
        
        # Calculate percentages and averages
        for age_group, stats in age_group_stats.items():
            stats['accuracy'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
            stats['average_score'] = stats['score'] / stats['total'] if stats['total'] > 0 else 0.0
            stats['average_time'] = stats['time'] / stats['total'] if stats['total'] > 0 else 0.0
        
        return age_group_stats
    
    def _analyze_difficulty(self) -> Dict[str, Any]:
        """Analyze question difficulty based on performance."""
        if not self.question_results:
            return {}
        
        # Sort questions by score (ascending = most difficult)
        sorted_results = sorted(self.question_results, key=lambda r: r.score)
        
        most_difficult = sorted_results[:3]  # Top 3 most difficult
        easiest = sorted_results[-3:]  # Top 3 easiest
        
        return {
            'most_difficult_questions': [
                {
                    'question_number': r.question_number,
                    'case_id': r.case_id,
                    'score': r.score,
                    'category': r.category,
                    'complexity': r.complexity
                }
                for r in most_difficult
            ],
            'easiest_questions': [
                {
                    'question_number': r.question_number,
                    'case_id': r.case_id,
                    'score': r.score,
                    'category': r.category,
                    'complexity': r.complexity
                }
                for r in reversed(easiest)
            ],
            'average_difficulty_score': sum(r.score for r in self.question_results) / len(self.question_results)
        }
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze time patterns and efficiency."""
        if not self.question_results:
            return {}
        
        times = [r.time_spent for r in self.question_results]
        
        # Calculate percentiles
        sorted_times = sorted(times)
        n = len(sorted_times)
        
        return {
            'fastest_question_time': min(times),
            'slowest_question_time': max(times),
            'median_time': sorted_times[n // 2] if n > 0 else 0.0,
            'time_std_dev': self._calculate_std_dev(times),
            'time_efficiency_score': self._calculate_time_efficiency(),
            'questions_under_30_seconds': sum(1 for t in times if t < 30),
            'questions_over_2_minutes': sum(1 for t in times if t > 120)
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _calculate_time_efficiency(self) -> float:
        """Calculate time efficiency score (higher is better)."""
        if not self.question_results:
            return 0.0
        
        # Efficiency = average accuracy / average time (normalized)
        avg_accuracy = sum(1 for r in self.question_results if r.is_correct) / len(self.question_results)
        avg_time = sum(r.time_spent for r in self.question_results) / len(self.question_results)
        
        if avg_time == 0:
            return 0.0
        
        # Normalize time (assuming 60 seconds is optimal per question)
        normalized_time = min(avg_time / 60.0, 2.0)  # Cap at 2x optimal time
        
        efficiency = avg_accuracy / normalized_time
        return min(efficiency * 100, 100.0)  # Cap at 100
    
    def get_detailed_feedback(self) -> List[Dict[str, Any]]:
        """
        Get detailed feedback for each question.
        
        Returns:
            List of detailed feedback dictionaries
        """
        if not self.question_results:
            return []
        
        feedback_list = []
        
        for result in self.question_results:
            feedback = {
                'question_number': result.question_number,
                'case_id': result.case_id,
                'user_answer': result.user_answer,
                'correct_answer': result.correct_answer,
                'is_correct': result.is_correct,
                'score': result.score,
                'max_score': result.max_score,
                'time_spent': result.time_spent,
                'feedback': result.feedback,
                'category': result.category,
                'complexity': result.complexity,
                'age_group': result.age_group
            }
            
            if result.partial_credit_reason:
                feedback['partial_credit_reason'] = result.partial_credit_reason
            
            feedback_list.append(feedback)
        
        return feedback_list
    
    def export_results(self, format_type: ExportFormat, 
                      include_detailed_feedback: bool = True) -> str:
        """
        Export results in various formats.
        
        Args:
            format_type: Export format (JSON, CSV, TEXT, HTML)
            include_detailed_feedback: Whether to include detailed feedback
            
        Returns:
            Formatted results string
            
        Raises:
            ValueError: If format_type not supported or no results to export
        """
        if not self.question_results:
            raise ValueError("No results to export. Calculate scores first.")
        
        try:
            if format_type == ExportFormat.JSON:
                return self._export_json(include_detailed_feedback)
            elif format_type == ExportFormat.CSV:
                return self._export_csv(include_detailed_feedback)
            elif format_type == ExportFormat.TEXT:
                return self._export_text(include_detailed_feedback)
            elif format_type == ExportFormat.HTML:
                return self._export_html(include_detailed_feedback)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to export results as {format_type}: {e}")
            raise
    
    def _export_json(self, include_detailed_feedback: bool) -> str:
        """Export results as JSON."""
        stats = self._generate_performance_stats()
        
        export_data: Dict[str, Any] = {
            'session_info': {
                'scoring_mode': self.scoring_mode.value,
                'session_start': self.session_start_time.isoformat() if self.session_start_time else None,
                'export_timestamp': datetime.now().isoformat(),
                'total_questions': stats.total_questions
            },
            'summary': {
                'correct_answers': stats.correct_answers,
                'incorrect_answers': stats.incorrect_answers,
                'total_score': stats.total_score,
                'max_possible_score': stats.max_possible_score,
                'percentage_score': stats.percentage_score,
                'average_time_per_question': stats.average_time_per_question,
                'total_time_spent': stats.total_time_spent
            },
            'performance_analysis': {
                'category_performance': stats.category_performance,
                'complexity_performance': stats.complexity_performance,
                'age_group_performance': stats.age_group_performance,
                'difficulty_analysis': stats.difficulty_analysis,
                'time_analysis': stats.time_analysis
            }
        }
        
        if include_detailed_feedback:
            export_data['detailed_feedback'] = self.get_detailed_feedback()
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _export_csv(self, include_detailed_feedback: bool) -> str:
        """Export results as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write summary section
        writer.writerow(['SUMMARY'])
        stats = self._generate_performance_stats()
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Questions', stats.total_questions])
        writer.writerow(['Correct Answers', stats.correct_answers])
        writer.writerow(['Incorrect Answers', stats.incorrect_answers])
        writer.writerow(['Total Score', f"{stats.total_score:.2f}"])
        writer.writerow(['Max Possible Score', stats.max_possible_score])
        writer.writerow(['Percentage Score', f"{stats.percentage_score:.2f}%"])
        writer.writerow(['Average Time per Question', f"{stats.average_time_per_question:.2f}s"])
        writer.writerow(['Total Time Spent', f"{stats.total_time_spent:.2f}s"])
        writer.writerow([])
        
        # Write detailed results
        if include_detailed_feedback:
            writer.writerow(['DETAILED RESULTS'])
            header = [
                'Question_Number', 'Case_ID', 'User_Answer', 'Correct_Answer',
                'Is_Correct', 'Score', 'Max_Score', 'Time_Spent',
                'Category', 'Age_Group', 'Complexity', 'Feedback'
            ]
            writer.writerow(header)
            
            for result in self.question_results:
                row = [
                    result.question_number,
                    result.case_id,
                    result.user_answer or '',
                    result.correct_answer,
                    result.is_correct,
                    f"{result.score:.2f}",
                    result.max_score,
                    f"{result.time_spent:.2f}",
                    result.category,
                    result.age_group,
                    result.complexity,
                    result.feedback
                ]
                writer.writerow(row)
        
        return output.getvalue()
    
    def _export_text(self, include_detailed_feedback: bool) -> str:
        """Export results as formatted text."""
        stats = self._generate_performance_stats()
        
        output = []
        output.append("=" * 80)
        output.append("QUIZ RESULTS REPORT")
        output.append("=" * 80)
        output.append(f"Scoring Mode: {self.scoring_mode.value.upper()}")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # Summary section
        output.append("SUMMARY")
        output.append("-" * 40)
        output.append(f"Total Questions: {stats.total_questions}")
        output.append(f"Correct Answers: {stats.correct_answers}")
        output.append(f"Incorrect Answers: {stats.incorrect_answers}")
        output.append(f"Score: {stats.total_score:.2f}/{stats.max_possible_score:.2f}")
        output.append(f"Percentage: {stats.percentage_score:.2f}%")
        output.append(f"Average Time per Question: {stats.average_time_per_question:.2f}s")
        output.append(f"Total Time: {stats.total_time_spent:.2f}s")
        output.append("")
        
        # Performance by category
        if stats.category_performance:
            output.append("PERFORMANCE BY CATEGORY")
            output.append("-" * 40)
            for category, data in stats.category_performance.items():
                output.append(f"{category.replace('_', ' ').title()}:")
                output.append(f"  Accuracy: {data['accuracy']:.1f}% ({data['correct']}/{data['total']})")
                output.append(f"  Avg Score: {data['average_score']:.2f}")
                output.append(f"  Avg Time: {data['average_time']:.1f}s")
                output.append("")
        
        # Performance by complexity
        if stats.complexity_performance:
            output.append("PERFORMANCE BY COMPLEXITY")
            output.append("-" * 40)
            for complexity, data in stats.complexity_performance.items():
                output.append(f"{complexity.title()}:")
                output.append(f"  Accuracy: {data['accuracy']:.1f}% ({data['correct']}/{data['total']})")
                output.append(f"  Avg Score: {data['average_score']:.2f}")
                output.append(f"  Avg Time: {data['average_time']:.1f}s")
                output.append("")
        
        # Detailed feedback
        if include_detailed_feedback:
            output.append("DETAILED FEEDBACK")
            output.append("-" * 40)
            for result in self.question_results:
                output.append(f"Question {result.question_number} (Case: {result.case_id})")
                output.append(f"  Your Answer: {result.user_answer or 'Not answered'}")
                output.append(f"  Correct Answer: {result.correct_answer}")
                output.append(f"  Score: {result.score:.2f}/{result.max_score:.2f}")
                output.append(f"  Time: {result.time_spent:.1f}s")
                output.append(f"  Feedback: {result.feedback}")
                if result.partial_credit_reason:
                    output.append(f"  Partial Credit: {result.partial_credit_reason}")
                output.append("")
        
        output.append("=" * 80)
        return "\n".join(output)
    
    def _export_html(self, include_detailed_feedback: bool) -> str:
        """Export results as HTML."""
        stats = self._generate_performance_stats()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Results Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .performance-section {{ margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .correct {{ background-color: #d4edda; }}
        .incorrect {{ background-color: #f8d7da; }}
        .partial {{ background-color: #fff3cd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Quiz Results Report</h1>
        <p><strong>Scoring Mode:</strong> {self.scoring_mode.value.upper()}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Questions:</strong> {stats.total_questions}</p>
        <p><strong>Correct Answers:</strong> {stats.correct_answers}</p>
        <p><strong>Incorrect Answers:</strong> {stats.incorrect_answers}</p>
        <p><strong>Score:</strong> {stats.total_score:.2f}/{stats.max_possible_score:.2f}</p>
        <p><strong>Percentage:</strong> {stats.percentage_score:.2f}%</p>
        <p><strong>Average Time per Question:</strong> {stats.average_time_per_question:.2f}s</p>
        <p><strong>Total Time:</strong> {stats.total_time_spent:.2f}s</p>
    </div>
"""
        
        # Category performance table
        if stats.category_performance:
            html += """
    <div class="performance-section">
        <h2>Performance by Category</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Accuracy</th>
                <th>Average Score</th>
                <th>Average Time</th>
            </tr>
"""
            for category, data in stats.category_performance.items():
                html += f"""
            <tr>
                <td>{category.replace('_', ' ').title()}</td>
                <td>{data['accuracy']:.1f}%</td>
                <td>{data['average_score']:.2f}</td>
                <td>{data['average_time']:.1f}s</td>
            </tr>
"""
            html += """
        </table>
    </div>
"""
        
        # Detailed feedback
        if include_detailed_feedback:
            html += """
    <div class="performance-section">
        <h2>Detailed Feedback</h2>
        <table>
            <tr>
                <th>Question</th>
                <th>Case ID</th>
                <th>Your Answer</th>
                <th>Correct Answer</th>
                <th>Score</th>
                <th>Time</th>
                <th>Feedback</th>
            </tr>
"""
            for result in self.question_results:
                css_class = "correct" if result.is_correct else ("partial" if 0 < result.score < 1 else "incorrect")
                html += f"""
            <tr class="{css_class}">
                <td>{result.question_number}</td>
                <td>{result.case_id}</td>
                <td>{result.user_answer or 'Not answered'}</td>
                <td>{result.correct_answer}</td>
                <td>{result.score:.2f}/{result.max_score:.2f}</td>
                <td>{result.time_spent:.1f}s</td>
                <td>{result.feedback}</td>
            </tr>
"""
            html += """
        </table>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary containing all performance data and recommendations
        """
        if not self.question_results:
            raise ValueError("No results available. Calculate scores first.")
        
        stats = self._generate_performance_stats()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(stats)
        
        return {
            'session_summary': {
                'scoring_mode': self.scoring_mode.value,
                'total_questions': stats.total_questions,
                'percentage_score': stats.percentage_score,
                'time_efficiency': stats.time_analysis.get('time_efficiency_score', 0)
            },
            'performance_metrics': asdict(stats),
            'detailed_feedback': self.get_detailed_feedback(),
            'recommendations': recommendations,
            'strengths': self._identify_strengths(stats),
            'areas_for_improvement': self._identify_weaknesses(stats)
        }
    
    def _generate_recommendations(self, stats: PerformanceStats) -> List[str]:
        """Generate personalized recommendations based on performance."""
        recommendations = []
        
        # Overall performance recommendations
        if stats.percentage_score < 60:
            recommendations.append("Consider reviewing fundamental diagnostic criteria and case presentations.")
        elif stats.percentage_score < 80:
            recommendations.append("Good performance! Focus on differential diagnosis to improve further.")
        else:
            recommendations.append("Excellent performance! Consider advanced cases or time-based challenges.")
        
        # Category-specific recommendations
        for category, data in stats.category_performance.items():
            if data['accuracy'] < 50:
                recommendations.append(f"Review {category.replace('_', ' ')} cases - accuracy is {data['accuracy']:.1f}%")
        
        # Time-based recommendations
        if stats.time_analysis.get('questions_over_2_minutes', 0) > stats.total_questions * 0.3:
            recommendations.append("Practice time management - many questions took over 2 minutes.")
        elif stats.time_analysis.get('questions_under_30_seconds', 0) > stats.total_questions * 0.3:
            recommendations.append("Consider spending more time on each question for better accuracy.")
        
        # Complexity-based recommendations
        for complexity, data in stats.complexity_performance.items():
            if data['accuracy'] < 60 and complexity == 'advanced':
                recommendations.append("Build foundation with basic and intermediate cases before attempting advanced ones.")
        
        return recommendations
    
    def _identify_strengths(self, stats: PerformanceStats) -> List[str]:
        """Identify areas of strength based on performance."""
        strengths = []
        
        # Category strengths
        for category, data in stats.category_performance.items():
            if data['accuracy'] >= 80:
                strengths.append(f"Strong performance in {category.replace('_', ' ')} ({data['accuracy']:.1f}% accuracy)")
        
        # Complexity strengths
        for complexity, data in stats.complexity_performance.items():
            if data['accuracy'] >= 80:
                strengths.append(f"Excellent with {complexity} complexity cases")
        
        # Time efficiency
        if stats.time_analysis.get('time_efficiency_score', 0) >= 70:
            strengths.append("Good time management during the quiz")
        
        # Overall performance
        if stats.percentage_score >= 85:
            strengths.append("Overall excellent diagnostic accuracy")
        
        return strengths
    
    def _identify_weaknesses(self, stats: PerformanceStats) -> List[str]:
        """Identify areas for improvement based on performance."""
        weaknesses = []
        
        # Category weaknesses
        for category, data in stats.category_performance.items():
            if data['accuracy'] < 60:
                weaknesses.append(f"Needs improvement in {category.replace('_', ' ')} ({data['accuracy']:.1f}% accuracy)")
        
        # Complexity weaknesses
        for complexity, data in stats.complexity_performance.items():
            if data['accuracy'] < 60:
                weaknesses.append(f"Struggles with {complexity} complexity cases")
        
        # Time issues
        if stats.time_analysis.get('time_efficiency_score', 0) < 40:
            weaknesses.append("Time management needs improvement")
        
        # Overall performance
        if stats.percentage_score < 60:
            weaknesses.append("Overall diagnostic accuracy needs improvement")
        
        return weaknesses
    
    def _update_progression_system(self, stats: PerformanceStats) -> None:
        """
        Update the progression system with quiz results.
        
        Args:
            stats: Performance statistics from the quiz
        """
        if not self.user_progress:
            return
        
        try:
            # Calculate XP for the session
            session_xp = self._calculate_session_xp(stats)
            
            # Add XP to user progress
            total_xp, leveled_up, new_achievements = self.user_progress.add_xp(session_xp, "quiz_session")
            self.session_xp_earned = session_xp
            
            if leveled_up:
                self.logger.info(f"User leveled up to {self.user_progress.level}")
            
            # Update streaks
            for result in self.question_results:
                streak, multiplier = self.user_progress.update_streak(result.is_correct)
                
                # Update specialty proficiency
                self.user_progress.update_specialty_proficiency(
                    result.category,
                    result.is_correct,
                    result.time_spent,
                    int(result.score * 10)  # Convert score to XP
                )
                
                # Update performance metrics
                case_result = {
                    'is_correct': result.is_correct,
                    'time_taken': result.time_spent,
                    'category': result.category,
                    'difficulty': result.complexity
                }
                self.user_progress.update_performance_metrics(case_result)
            
            # Check for new achievements
            self._check_session_achievements(stats)
            
        except Exception as e:
            self.logger.error(f"Failed to update progression system: {e}")
    
    def _calculate_session_xp(self, stats: PerformanceStats) -> int:
        """
        Calculate XP earned for the session based on performance.
        
        Args:
            stats: Performance statistics
            
        Returns:
            XP amount earned
        """
        base_xp = int(stats.total_score * 10)  # Base XP from score
        
        # Accuracy bonus
        accuracy_bonus = 0
        if stats.percentage_score >= 100:
            accuracy_bonus = int(base_xp * 0.5)  # 50% bonus for perfect
        elif stats.percentage_score >= 90:
            accuracy_bonus = int(base_xp * 0.25)  # 25% bonus for excellent
        elif stats.percentage_score >= 80:
            accuracy_bonus = int(base_xp * 0.1)   # 10% bonus for good
        
        # Time bonus
        time_bonus = 0
        if stats.average_time_per_question < 30:  # Under 30 seconds per question
            time_bonus = int(base_xp * 0.2)  # 20% time bonus
        elif stats.average_time_per_question < 60:  # Under 1 minute per question
            time_bonus = int(base_xp * 0.1)  # 10% time bonus
        
        # Difficulty bonus
        difficulty_bonus = 0
        for complexity, data in stats.complexity_performance.items():
            if complexity == 'advanced' and data['accuracy'] >= 80:
                difficulty_bonus += int(base_xp * 0.15)
            elif complexity == 'expert' and data['accuracy'] >= 70:
                difficulty_bonus += int(base_xp * 0.25)
        
        # Streak multiplier
        streak_multiplier = 1.0
        if self.user_progress:
            streak_multiplier = self.user_progress.streak_data.streak_multiplier
        
        total_xp = int((base_xp + accuracy_bonus + time_bonus + difficulty_bonus) * streak_multiplier)
        return max(total_xp, 10)  # Minimum 10 XP per session
    
    def _check_session_achievements(self, stats: PerformanceStats) -> None:
        """
        Check for session-based achievements.
        
        Args:
            stats: Performance statistics
        """
        if not self.user_progress:
            return
        
        achievements_to_check = []
        
        # First case completion
        if stats.total_questions >= 1 and not any(ea.achievement_id == 'first_case' for ea in self.user_progress.earned_achievements):
            achievements_to_check.append('first_case')
        
        # Speed achievements
        fast_cases = sum(1 for r in self.question_results if r.time_spent < 120 and r.is_correct)
        if fast_cases >= 5 and not any(ea.achievement_id == 'speed_demon' for ea in self.user_progress.earned_achievements):
            achievements_to_check.append('speed_demon')
        
        # Perfect session
        if stats.percentage_score == 100 and stats.total_questions >= 5:
            achievements_to_check.append('perfectionist')
        
        # Check and award achievements
        for achievement_id in achievements_to_check:
            if self.user_progress.award_achievement(achievement_id):
                self.achievements_awarded.append(achievement_id)
                self.logger.info(f"Awarded achievement: {achievement_id}")
    
    def get_session_progression_report(self) -> Dict[str, Any]:
        """
        Get a detailed progression report for the current session.
        
        Returns:
            Dictionary containing session progression data
        """
        if not self.user_progress:
            return {'error': 'No progression system available'}
        
        return {
            'session_xp_earned': self.session_xp_earned,
            'achievements_awarded': self.achievements_awarded,
            'current_level': self.user_progress.level,
            'total_xp': self.user_progress.total_xp,
            'xp_to_next_level': self.user_progress.xp_to_next_level,
            'current_streak': self.user_progress.streak_data.current_streak,
            'streak_multiplier': self.user_progress.streak_data.streak_multiplier,
            'specialty_progress': {
                cat: {
                    'level': prof.level,
                    'accuracy': prof.accuracy,
                    'cases_completed': prof.cases_completed
                }
                for cat, prof in self.user_progress.specialties.items()
            },
            'unlocked_difficulties': list(self.user_progress.unlock_status.unlocked_difficulties),
            'next_difficulty_recommendation': self.user_progress.calculate_adaptive_difficulty(
                self.user_progress.performance_metrics.recent_performance[-10:] if self.user_progress.performance_metrics.recent_performance else []
            )
        }
    
    def calculate_clinical_accuracy_score(self, user_answer: str, correct_answer: str, 
                                        specifiers: Optional[Dict[str, Any]] = None) -> Tuple[float, str]:
        """
        Calculate clinical accuracy score with partial credit for specifiers.
        
        Args:
            user_answer: User's diagnosis answer
            correct_answer: Correct diagnosis
            specifiers: Dictionary of required specifiers and their importance
            
        Returns:
            Tuple of (score, feedback)
        """
        if not specifiers:
            # Fall back to regular evaluation
            if self.scoring_mode == ScoringMode.STRICT:
                return self._evaluate_strict(user_answer, correct_answer)[1:3]
            elif self.scoring_mode == ScoringMode.LENIENT:
                return self._evaluate_lenient(user_answer, correct_answer)[1:3]
            else:
                return self._evaluate_partial(user_answer, correct_answer, {})[1:3]
        
        # Clinical accuracy scoring with specifiers
        base_score = 0.0
        feedback_parts = []
        
        # Check main diagnosis
        user_clean = user_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        if user_clean == correct_clean:
            base_score = 0.7  # 70% for correct main diagnosis
            feedback_parts.append("Correct main diagnosis")
        else:
            # Check for partial match
            similarity = self._calculate_diagnosis_similarity(user_answer, correct_answer)
            if similarity >= 0.8:
                base_score = 0.5  # 50% for very similar diagnosis
                feedback_parts.append(f"Similar diagnosis ({similarity:.0%} match)")
            elif similarity >= 0.6:
                base_score = 0.3  # 30% for somewhat similar diagnosis
                feedback_parts.append(f"Partially similar diagnosis ({similarity:.0%} match)")
            else:
                feedback_parts.append("Incorrect main diagnosis")
        
        # Check specifiers
        specifier_score = 0.0
        matched_specifiers = 0
        total_specifiers = len(specifiers)
        
        for specifier, importance in specifiers.items():
            if specifier.lower() in user_clean:
                specifier_score += importance
                matched_specifiers += 1
                feedback_parts.append(f"Correct specifier: {specifier}")
        
        # Combine scores
        if total_specifiers > 0:
            specifier_percentage = specifier_score / sum(specifiers.values())
            total_score = base_score + (specifier_percentage * 0.3)  # Specifiers worth 30%
        else:
            total_score = base_score
        
        total_score = min(total_score, 1.0)
        
        feedback = "; ".join(feedback_parts)
        if total_score < 1.0:
            feedback += f". Correct answer: {correct_answer}"
        
        return total_score, feedback
    
    def reset_session(self) -> None:
        """Reset the current scoring session."""
        self.quiz_data = None
        self.user_answers = {}
        self.question_results = []
        self.session_start_time = None
        self.question_start_times = {}
        self._diagnosis_similarity_cache = {}
        self.session_xp_earned = 0
        self.achievements_awarded = []
        
        self.logger.info("Quiz scoring session reset")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a quick summary of the current session.
        
        Returns:
            Dictionary with session summary information
        """
        if not self.quiz_data:
            return {'status': 'No active session'}
        
        answered_questions = len(self.user_answers)
        total_questions = len(self.quiz_data['questions'])
        
        return {
            'status': 'Active session',
            'scoring_mode': self.scoring_mode.value,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'unanswered_questions': total_questions - answered_questions,
            'session_start': self.session_start_time.isoformat() if self.session_start_time else None,
            'session_duration': (datetime.now() - self.session_start_time).total_seconds() if self.session_start_time else 0
        }