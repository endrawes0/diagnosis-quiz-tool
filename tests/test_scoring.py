"""
Unit tests for the Scoring class.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.modules.scoring import Scoring, ScoringMode, ExportFormat, QuestionResult, PerformanceStats


class TestScoring:
    """Test cases for Scoring class."""

    def test_init_strict_mode(self):
        """Test Scoring initialization with strict mode."""
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        assert scoring.scoring_mode == ScoringMode.STRICT
        assert scoring.partial_credit_config is not None
        assert scoring.quiz_data is None
        assert scoring.user_answers == {}
        assert scoring.question_results == []

    def test_init_lenient_mode(self):
        """Test Scoring initialization with lenient mode."""
        scoring = Scoring(scoring_mode=ScoringMode.LENIENT)
        assert scoring.scoring_mode == ScoringMode.LENIENT

    def test_init_partial_mode(self):
        """Test Scoring initialization with partial credit mode."""
        custom_config = {
            'category_match_bonus': 0.3,
            'age_group_match_bonus': 0.2,
            'complexity_match_bonus': 0.15,
            'similarity_threshold': 0.8
        }
        scoring = Scoring(scoring_mode=ScoringMode.PARTIAL, partial_credit_config=custom_config)
        assert scoring.scoring_mode == ScoringMode.PARTIAL
        assert scoring.partial_credit_config == custom_config

    def test_start_quiz_session_success(self, scoring_strict, sample_quiz_data):
        """Test successful quiz session start."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        assert scoring_strict.quiz_data == sample_quiz_data
        assert scoring_strict.user_answers == {}
        assert scoring_strict.question_results == []
        assert scoring_strict.session_start_time is not None
        assert len(scoring_strict.question_start_times) == 0

    def test_start_quiz_session_invalid_data(self, scoring_strict):
        """Test quiz session start with invalid data."""
        invalid_data = {"invalid": "data"}
        
        with pytest.raises(ValueError, match="Missing required key"):
            scoring_strict.start_quiz_session(invalid_data)

    def test_start_quiz_session_no_questions(self, scoring_strict):
        """Test quiz session start with no questions."""
        invalid_data = {
            "quiz_metadata": {"total_questions": 0},
            "questions": []
        }
        
        with pytest.raises(ValueError, match="Quiz must contain at least one question"):
            scoring_strict.start_quiz_session(invalid_data)

    def test_record_answer_success(self, scoring_strict, sample_quiz_data):
        """Test successful answer recording."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        scoring_strict.record_answer(1, "Major Depressive Disorder", 45.5)
        
        assert 1 in scoring_strict.user_answers
        assert scoring_strict.user_answers[1]["answer"] == "Major Depressive Disorder"
        assert scoring_strict.user_answers[1]["time_spent"] == 45.5
        assert "timestamp" in scoring_strict.user_answers[1]

    def test_record_answer_no_session(self, scoring_strict):
        """Test answer recording without active session."""
        with pytest.raises(ValueError, match="Quiz session not started"):
            scoring_strict.record_answer(1, "Test Answer")

    def test_record_answer_invalid_question_number(self, scoring_strict, sample_quiz_data):
        """Test answer recording with invalid question number."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        with pytest.raises(ValueError, match="Invalid question number"):
            scoring_strict.record_answer(99, "Test Answer")

    def test_record_answer_auto_time_calculation(self, scoring_strict, sample_quiz_data):
        """Test answer recording with automatic time calculation."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        # Start timer for question
        scoring_strict.start_question_timer(1)
        
        # Simulate some time passing
        with patch('src.modules.scoring.datetime') as mock_datetime:
            start_time = datetime.now()
            mock_datetime.now.return_value = start_time + timedelta(seconds=30)
            
            scoring_strict.record_answer(1, "Test Answer")
            
            assert scoring_strict.user_answers[1]["time_spent"] == 30.0

    def test_start_question_timer(self, scoring_strict, sample_quiz_data):
        """Test starting question timer."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        scoring_strict.start_question_timer(1)
        
        assert 1 in scoring_strict.question_start_times
        assert isinstance(scoring_strict.question_start_times[1], datetime)

    def test_start_question_timer_no_session(self, scoring_strict):
        """Test starting question timer without active session."""
        with pytest.raises(ValueError, match="Quiz session not started"):
            scoring_strict.start_question_timer(1)

    def test_calculate_scores_strict_mode(self, scoring_strict, sample_quiz_data):
        """Test score calculation in strict mode."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        # Record some answers
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.record_answer(2, "Wrong Answer", 45.0)
        
        stats = scoring_strict.calculate_scores()
        
        assert isinstance(stats, PerformanceStats)
        assert stats.total_questions == 2
        assert stats.correct_answers == 1
        assert stats.incorrect_answers == 1
        assert stats.total_score == 1.0
        assert stats.max_possible_score == 2.0
        assert stats.percentage_score == 50.0

    def test_calculate_scores_lenient_mode(self, scoring_lenient, sample_quiz_data):
        """Test score calculation in lenient mode."""
        scoring_lenient.start_quiz_session(sample_quiz_data)
        
        # Record similar but not exact answer
        scoring_lenient.record_answer(1, "major depressive disorder", 30.0)  # Different case
        scoring_lenient.record_answer(2, "Generalized Anxiety", 45.0)  # Partial match
        
        stats = scoring_lenient.calculate_scores()
        
        # Should get credit for both due to lenient matching
        assert stats.correct_answers == 2
        assert stats.total_score == 2.0

    def test_calculate_scores_partial_mode(self, scoring_partial, sample_quiz_data):
        """Test score calculation in partial credit mode."""
        scoring_partial.start_quiz_session(sample_quiz_data)
        
        # Record answers that might get partial credit
        scoring_partial.record_answer(1, "Depression", 30.0)  # Similar
        scoring_partial.record_answer(2, "Wrong", 45.0)  # Wrong
        
        stats = scoring_partial.calculate_scores()
        
        assert isinstance(stats, PerformanceStats)
        assert 0 < stats.total_score <= 2.0  # Should get some partial credit

    def test_calculate_scores_no_session(self, scoring_strict):
        """Test score calculation without active session."""
        with pytest.raises(ValueError, match="Quiz session not started"):
            scoring_strict.calculate_scores()

    def test_unanswered_questions(self, scoring_strict, sample_quiz_data):
        """Test handling of unanswered questions."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        # Only answer one question out of two
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        
        stats = scoring_strict.calculate_scores()
        
        assert stats.total_questions == 2
        assert stats.correct_answers == 1
        assert stats.incorrect_answers == 1  # Unanswered counts as incorrect

    def test_evaluate_strict_correct(self, scoring_strict):
        """Test strict evaluation with correct answer."""
        is_correct, score, feedback = scoring_strict._evaluate_strict(
            "Major Depressive Disorder", "Major Depressive Disorder"
        )
        
        assert is_correct is True
        assert score == 1.0
        assert "Correct" in feedback

    def test_evaluate_strict_incorrect(self, scoring_strict):
        """Test strict evaluation with incorrect answer."""
        is_correct, score, feedback = scoring_strict._evaluate_strict(
            "Wrong Answer", "Major Depressive Disorder"
        )
        
        assert is_correct is False
        assert score == 0.0
        assert "Incorrect" in feedback

    def test_evaluate_lenient_exact_match(self, scoring_lenient):
        """Test lenient evaluation with exact match."""
        is_correct, score, feedback = scoring_lenient._evaluate_lenient(
            "Major Depressive Disorder", "Major Depressive Disorder"
        )
        
        assert is_correct is True
        assert score == 1.0

    def test_evaluate_lenient_case_insensitive(self, scoring_lenient):
        """Test lenient evaluation with case difference."""
        is_correct, score, feedback = scoring_lenient._evaluate_lenient(
            "major depressive disorder", "Major Depressive Disorder"
        )
        
        assert is_correct is True
        assert score == 1.0

    def test_evaluate_lenient_word_overlap(self, scoring_lenient):
        """Test lenient evaluation with word overlap."""
        is_correct, score, feedback = scoring_lenient._evaluate_lenient(
            "Major Depression", "Major Depressive Disorder"
        )
        
        assert is_correct is True
        assert score == 1.0

    def test_evaluate_lenient_no_match(self, scoring_lenient):
        """Test lenient evaluation with no match."""
        is_correct, score, feedback = scoring_lenient._evaluate_lenient(
            "Completely Wrong", "Major Depressive Disorder"
        )
        
        assert is_correct is False
        assert score == 0.0

    def test_evaluate_partial_exact_match(self, scoring_partial):
        """Test partial evaluation with exact match."""
        question = {
            "case_metadata": {"category": "mood_disorders"}
        }
        
        is_correct, score, feedback, reason = scoring_partial._evaluate_partial(
            "Major Depressive Disorder", "Major Depressive Disorder", question
        )
        
        assert is_correct is True
        assert score == 1.0
        assert reason is None

    def test_evaluate_partial_category_match(self, scoring_partial):
        """Test partial evaluation with category match."""
        question = {
            "case_metadata": {"category": "mood_disorders"}
        }
        
        is_correct, score, feedback, reason = scoring_partial._evaluate_partial(
            "Some mood problem", "Major Depressive Disorder", question
        )
        
        assert is_correct is False
        assert score > 0
        assert "mood" in reason.lower()

    def test_calculate_diagnosis_similarity(self, scoring_strict):
        """Test diagnosis similarity calculation."""
        # Exact match
        similarity = scoring_strict._calculate_diagnosis_similarity(
            "Major Depressive Disorder", "Major Depressive Disorder"
        )
        assert similarity == 1.0
        
        # Partial match
        similarity = scoring_strict._calculate_diagnosis_similarity(
            "Major Depression", "Major Depressive Disorder"
        )
        assert 0 < similarity < 1.0
        
        # No match
        similarity = scoring_strict._calculate_diagnosis_similarity(
            "Anxiety Disorder", "Major Depressive Disorder"
        )
        assert similarity == 0.0

    def test_diagnosis_similarity_caching(self, scoring_strict):
        """Test that diagnosis similarity is cached."""
        # Calculate similarity twice
        similarity1 = scoring_strict._calculate_diagnosis_similarity(
            "Test A", "Test B"
        )
        similarity2 = scoring_strict._calculate_diagnosis_similarity(
            "Test A", "Test B"
        )
        
        assert similarity1 == similarity2
        # Should be cached
        assert ("test a", "test b") in scoring_strict._diagnosis_similarity_cache

    def test_performance_stats_generation(self, scoring_strict, sample_quiz_data):
        """Test comprehensive performance statistics generation."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        # Record answers with varying times
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.record_answer(2, "Generalized Anxiety Disorder", 60.0)
        
        stats = scoring_strict.calculate_scores()
        
        assert stats.total_questions == 2
        assert stats.correct_answers == 2
        assert stats.total_score == 2.0
        assert stats.average_time_per_question == 45.0
        assert stats.total_time_spent == 90.0
        
        # Check category performance
        assert "mood_disorders" in stats.category_performance
        assert "anxiety_disorders" in stats.category_performance
        
        # Check complexity performance
        assert "basic" in stats.complexity_performance
        assert "intermediate" in stats.complexity_performance

    def test_category_performance_calculation(self, scoring_strict):
        """Test category-specific performance calculation."""
        # Create mock results
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Wrong",
                correct_answer="Correct", is_correct=False, score=0.0, max_score=1.0,
                time_spent=60.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Incorrect"
            ),
            QuestionResult(
                question_number=3, case_id="TEST-003", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=45.0, category="anxiety_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            )
        ]
        
        category_stats = scoring_strict._calculate_category_performance()
        
        # Mood disorders: 1/2 correct (50%)
        assert category_stats["mood_disorders"]["total"] == 2
        assert category_stats["mood_disorders"]["correct"] == 1
        assert category_stats["mood_disorders"]["accuracy"] == 50.0
        assert category_stats["mood_disorders"]["average_score"] == 0.5
        assert category_stats["mood_disorders"]["average_time"] == 45.0
        
        # Anxiety disorders: 1/1 correct (100%)
        assert category_stats["anxiety_disorders"]["total"] == 1
        assert category_stats["anxiety_disorders"]["correct"] == 1
        assert category_stats["anxiety_disorders"]["accuracy"] == 100.0

    def test_complexity_performance_calculation(self, scoring_strict):
        """Test complexity-specific performance calculation."""
        # Create mock results
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Wrong",
                correct_answer="Correct", is_correct=False, score=0.0, max_score=1.0,
                time_spent=90.0, category="mood_disorders", age_group="adult",
                complexity="advanced", feedback="Incorrect"
            )
        ]
        
        complexity_stats = scoring_strict._calculate_complexity_performance()
        
        # Basic: 1/1 correct (100%)
        assert complexity_stats["basic"]["total"] == 1
        assert complexity_stats["basic"]["correct"] == 1
        assert complexity_stats["basic"]["accuracy"] == 100.0
        
        # Advanced: 0/1 correct (0%)
        assert complexity_stats["advanced"]["total"] == 1
        assert complexity_stats["advanced"]["correct"] == 0
        assert complexity_stats["advanced"]["accuracy"] == 0.0

    def test_age_group_performance_calculation(self, scoring_strict):
        """Test age group-specific performance calculation."""
        # Create mock results
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=45.0, category="mood_disorders", age_group="adolescent",
                complexity="basic", feedback="Correct"
            )
        ]
        
        age_group_stats = scoring_strict._calculate_age_group_performance()
        
        # Adult: 1/1 correct (100%)
        assert age_group_stats["adult"]["total"] == 1
        assert age_group_stats["adult"]["correct"] == 1
        assert age_group_stats["adult"]["accuracy"] == 100.0
        
        # Adolescent: 1/1 correct (100%)
        assert age_group_stats["adolescent"]["total"] == 1
        assert age_group_stats["adolescent"]["correct"] == 1
        assert age_group_stats["adolescent"]["accuracy"] == 100.0

    def test_difficulty_analysis(self, scoring_strict):
        """Test difficulty analysis functionality."""
        # Create mock results with varying scores
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Wrong",
                correct_answer="Correct", is_correct=False, score=0.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Incorrect"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Wrong",
                correct_answer="Correct", is_correct=False, score=0.2, max_score=1.0,
                time_spent=45.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Partial"
            ),
            QuestionResult(
                question_number=3, case_id="TEST-003", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=60.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            )
        ]
        
        difficulty = scoring_strict._analyze_difficulty()
        
        assert "most_difficult_questions" in difficulty
        assert "easiest_questions" in difficulty
        assert "average_difficulty_score" in difficulty
        
        # Most difficult should be the ones with lowest scores
        most_difficult = difficulty["most_difficult_questions"]
        assert len(most_difficult) <= 3
        assert most_difficult[0]["score"] == 0.0  # Lowest score first

    def test_time_analysis(self, scoring_strict):
        """Test time pattern analysis."""
        # Create mock results with varying times
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=15.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=150.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=3, case_id="TEST-003", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=45.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            )
        ]
        
        time_analysis = scoring_strict._analyze_time_patterns()
        
        assert time_analysis["fastest_question_time"] == 15.0
        assert time_analysis["slowest_question_time"] == 150.0
        assert time_analysis["median_time"] == 45.0
        assert time_analysis["questions_under_30_seconds"] == 1
        assert time_analysis["questions_over_2_minutes"] == 1

    def test_standard_deviation_calculation(self, scoring_strict):
        """Test standard deviation calculation."""
        values = [10, 20, 30, 40, 50]
        std_dev = scoring_strict._calculate_std_dev(values)
        
        # Standard deviation of [10, 20, 30, 40, 50] should be ~14.14
        assert abs(std_dev - 14.14) < 0.1

    def test_time_efficiency_calculation(self, scoring_strict):
        """Test time efficiency score calculation."""
        # Create mock results
        scoring_strict.question_results = [
            QuestionResult(
                question_number=1, case_id="TEST-001", user_answer="Correct",
                correct_answer="Correct", is_correct=True, score=1.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Correct"
            ),
            QuestionResult(
                question_number=2, case_id="TEST-002", user_answer="Wrong",
                correct_answer="Correct", is_correct=False, score=0.0, max_score=1.0,
                time_spent=30.0, category="mood_disorders", age_group="adult",
                complexity="basic", feedback="Incorrect"
            )
        ]
        
        efficiency = scoring_strict._calculate_time_efficiency()
        
        assert 0 <= efficiency <= 100

    def test_get_detailed_feedback(self, scoring_strict, sample_quiz_data):
        """Test detailed feedback generation."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.calculate_scores()
        
        feedback = scoring_strict.get_detailed_feedback()
        
        assert isinstance(feedback, list)
        assert len(feedback) == 2
        
        first_feedback = feedback[0]
        assert first_feedback["question_number"] == 1
        assert first_feedback["user_answer"] == "Major Depressive Disorder"
        assert first_feedback["correct_answer"] == "Major Depressive Disorder"
        assert first_feedback["is_correct"] is True
        assert first_feedback["score"] == 1.0

    def test_export_json(self, scoring_strict, sample_quiz_data):
        """Test JSON export functionality."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.calculate_scores()
        
        json_export = scoring_strict.export_results(ExportFormat.JSON)
        
        assert isinstance(json_export, str)
        parsed = json.loads(json_export)
        
        assert "session_info" in parsed
        assert "summary" in parsed
        assert "performance_analysis" in parsed
        assert "detailed_feedback" in parsed

    def test_export_csv(self, scoring_strict, sample_quiz_data):
        """Test CSV export functionality."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.calculate_scores()
        
        csv_export = scoring_strict.export_results(ExportFormat.CSV)
        
        assert isinstance(csv_export, str)
        lines = csv_export.strip().split('\n')
        
        # Should have summary and detailed sections
        assert "SUMMARY" in csv_export
        assert "DETAILED RESULTS" in csv_export
        assert "Metric,Value" in csv_export

    def test_export_text(self, scoring_strict, sample_quiz_data):
        """Test text export functionality."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.calculate_scores()
        
        text_export = scoring_strict.export_results(ExportFormat.TEXT)
        
        assert isinstance(text_export, str)
        assert "QUIZ RESULTS REPORT" in text_export
        assert "SUMMARY" in text_export
        assert "PERFORMANCE BY CATEGORY" in text_export

    def test_export_html(self, scoring_strict, sample_quiz_data):
        """Test HTML export functionality."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.calculate_scores()
        
        html_export = scoring_strict.export_results(ExportFormat.HTML)
        
        assert isinstance(html_export, str)
        assert "<!DOCTYPE html>" in html_export
        assert "<title>Quiz Results Report</title>" in html_export
        assert "Quiz Results Report" in html_export

    def test_export_no_results(self, scoring_strict):
        """Test export when no results available."""
        with pytest.raises(ValueError, match="No results to export"):
            scoring_strict.export_results(ExportFormat.JSON)

    def test_export_unsupported_format(self, scoring_strict, sample_quiz_data):
        """Test export with unsupported format."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.calculate_scores()
        
        with pytest.raises(ValueError, match="Unsupported export format"):
            scoring_strict.export_results("unsupported")

    def test_get_performance_report(self, scoring_strict, sample_quiz_data):
        """Test comprehensive performance report generation."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Major Depressive Disorder", 30.0)
        scoring_strict.record_answer(2, "Wrong Answer", 45.0)
        scoring_strict.calculate_scores()
        
        report = scoring_strict.get_performance_report()
        
        assert "session_summary" in report
        assert "performance_metrics" in report
        assert "detailed_feedback" in report
        assert "recommendations" in report
        assert "strengths" in report
        assert "areas_for_improvement" in report
        
        assert report["session_summary"]["percentage_score"] == 50.0

    def test_generate_recommendations(self, scoring_strict):
        """Test recommendation generation based on performance."""
        # Create mock stats for poor performance
        stats = PerformanceStats(
            total_questions=10, correct_answers=4, incorrect_answers=6,
            total_score=4.0, max_possible_score=10.0, percentage_score=40.0,
            average_time_per_question=150.0, total_time_spent=1500.0,
            category_performance={}, complexity_performance={}, age_group_performance={},
            difficulty_analysis={}, time_analysis={"questions_over_2_minutes": 8}
        )
        
        recommendations = scoring_strict._generate_recommendations(stats)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("fundamental diagnostic criteria" in rec for rec in recommendations)
        assert any("time management" in rec for rec in recommendations)

    def test_identify_strengths(self, scoring_strict):
        """Test strength identification."""
        # Create mock stats with good performance
        stats = PerformanceStats(
            total_questions=10, correct_answers=9, incorrect_answers=1,
            total_score=9.0, max_possible_score=10.0, percentage_score=90.0,
            average_time_per_question=45.0, total_time_spent=450.0,
            category_performance={"mood_disorders": {"accuracy": 90.0}},
            complexity_performance={"basic": {"accuracy": 95.0}},
            age_group_performance={}, difficulty_analysis={},
            time_analysis={"time_efficiency_score": 80.0}
        )
        
        strengths = scoring_strict._identify_strengths(stats)
        
        assert isinstance(strengths, list)
        assert any("excellent diagnostic accuracy" in strength for strength in strengths)
        assert any("mood_disorders" in strength for strength in strengths)

    def test_identify_weaknesses(self, scoring_strict):
        """Test weakness identification."""
        # Create mock stats with poor performance
        stats = PerformanceStats(
            total_questions=10, correct_answers=4, incorrect_answers=6,
            total_score=4.0, max_possible_score=10.0, percentage_score=40.0,
            average_time_per_question=150.0, total_time_spent=1500.0,
            category_performance={"anxiety_disorders": {"accuracy": 30.0}},
            complexity_performance={"advanced": {"accuracy": 20.0}},
            age_group_performance={}, difficulty_analysis={},
            time_analysis={"time_efficiency_score": 20.0}
        )
        
        weaknesses = scoring_strict._identify_weaknesses(stats)
        
        assert isinstance(weaknesses, list)
        assert any("diagnostic accuracy" in weakness for weakness in weaknesses)
        assert any("anxiety_disorders" in weakness for weakness in weaknesses)

    def test_reset_session(self, scoring_strict, sample_quiz_data):
        """Test session reset functionality."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Test Answer", 30.0)
        scoring_strict.calculate_scores()
        
        # Verify session is active
        assert scoring_strict.quiz_data is not None
        assert len(scoring_strict.user_answers) > 0
        assert len(scoring_strict.question_results) > 0
        
        # Reset session
        scoring_strict.reset_session()
        
        # Verify session is reset
        assert scoring_strict.quiz_data is None
        assert scoring_strict.user_answers == {}
        assert scoring_strict.question_results == []
        assert scoring_strict.session_start_time is None
        assert len(scoring_strict.question_start_times) == 0

    def test_get_session_summary_active(self, scoring_strict, sample_quiz_data):
        """Test session summary for active session."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.record_answer(1, "Test Answer", 30.0)
        
        summary = scoring_strict.get_session_summary()
        
        assert summary["status"] == "Active session"
        assert summary["scoring_mode"] == "strict"
        assert summary["total_questions"] == 2
        assert summary["answered_questions"] == 1
        assert summary["unanswered_questions"] == 1
        assert "session_start" in summary
        assert "session_duration" in summary

    def test_get_session_summary_no_session(self, scoring_strict):
        """Test session summary when no active session."""
        summary = scoring_strict.get_session_summary()
        
        assert summary["status"] == "No active session"

    def test_logging_setup(self, scoring_strict):
        """Test that logging is properly set up."""
        assert scoring_strict.logger is not None
        assert len(scoring_strict.logger.handlers) > 0

    def test_error_handling_in_export(self, scoring_strict, sample_quiz_data):
        """Test error handling in export methods."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        scoring_strict.calculate_scores()
        
        # Mock a method to raise an exception
        with patch.object(scoring_strict, '_generate_performance_stats', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Failed to export results"):
                scoring_strict.export_results(ExportFormat.JSON)

    def test_partial_credit_edge_cases(self, scoring_partial):
        """Test partial credit edge cases."""
        question = {
            "case_metadata": {"category": "mood_disorders"}
        }
        
        # Test with empty user answer
        is_correct, score, feedback, reason = scoring_partial._evaluate_partial(
            "", "Major Depressive Disorder", question
        )
        
        assert is_correct is False
        assert score == 0.0

    def test_time_calculation_edge_cases(self, scoring_strict, sample_quiz_data):
        """Test time calculation edge cases."""
        scoring_strict.start_quiz_session(sample_quiz_data)
        
        # Record answer without starting timer
        scoring_strict.record_answer(1, "Test Answer")
        
        # Should use 0.0 as default time
        assert scoring_strict.user_answers[1]["time_spent"] == 0.0