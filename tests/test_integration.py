"""
Integration tests for the diagnosis quiz tool.
Tests the full workflow from data loading through quiz generation and scoring.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.modules.data_loader import DataLoader
from src.modules.quiz_generator import QuizGenerator
from src.modules.scoring import Scoring, ScoringMode, ExportFormat


class TestIntegration:
    """Integration tests for the complete quiz workflow."""

    def test_full_workflow_strict_scoring(self, temp_data_dir):
        """Test complete workflow with strict scoring mode."""
        # Initialize components
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Load data
        cases = data_loader.load_cases()
        diagnoses = data_loader.load_diagnoses()
        config = data_loader.load_config()
        
        assert len(cases) > 0
        assert len(diagnoses) > 0
        assert isinstance(config, dict)
        
        # Generate quiz
        quiz_config = {
            "num_questions": 2,
            "num_choices": 4,
            "categories": ["mood_disorders", "anxiety_disorders"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        assert "quiz_metadata" in quiz_data
        assert "questions" in quiz_data
        assert len(quiz_data["questions"]) == 2
        
        # Start scoring session
        scoring.start_quiz_session(quiz_data)
        
        # Record answers
        for question in quiz_data["questions"]:
            question_num = question["question_number"]
            correct_answer = question["correct_answer"]
            
            # Record timing
            scoring.start_question_timer(question_num)
            
            # Record answer (correct for first, wrong for second)
            if question_num == 1:
                scoring.record_answer(question_num, correct_answer, 30.0)
            else:
                scoring.record_answer(question_num, "Wrong Answer", 45.0)
        
        # Calculate scores
        stats = scoring.calculate_scores()
        
        assert stats.total_questions == 2
        assert stats.correct_answers == 1
        assert stats.incorrect_answers == 1
        assert stats.total_score == 1.0
        assert stats.percentage_score == 50.0
        
        # Export results
        json_export = scoring.export_results(ExportFormat.JSON)
        assert isinstance(json_export, str)
        
        text_export = scoring.export_results(ExportFormat.TEXT)
        assert isinstance(text_export, str)
        
        csv_export = scoring.export_results(ExportFormat.CSV)
        assert isinstance(csv_export, str)

    def test_full_workflow_lenient_scoring(self, temp_data_dir):
        """Test complete workflow with lenient scoring mode."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.LENIENT)
        
        # Generate quiz
        quiz_config = {
            "num_questions": 2,
            "num_choices": 4,
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Record answers with variations that should be accepted in lenient mode
        for i, question in enumerate(quiz_data["questions"]):
            question_num = question["question_number"]
            correct_answer = question["correct_answer"]
            
            # Use case variations and partial matches
            if i == 0:
                # Lower case version
                user_answer = correct_answer.lower()
            else:
                # Partial match
                user_answer = correct_answer.split()[0]  # First word only
            
            scoring.record_answer(question_num, user_answer, 30.0)
        
        # Calculate scores
        stats = scoring.calculate_scores()
        
        # Should get credit for both due to lenient matching
        assert stats.correct_answers == 2
        assert stats.total_score == 2.0
        assert stats.percentage_score == 100.0

    def test_full_workflow_partial_scoring(self, temp_data_dir):
        """Test complete workflow with partial credit scoring mode."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.PARTIAL)
        
        # Generate quiz
        quiz_config = {
            "num_questions": 2,
            "num_choices": 4,
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Record answers that might get partial credit
        for question in quiz_data["questions"]:
            question_num = question["question_number"]
            correct_answer = question["correct_answer"]
            
            # Use category-related terms for partial credit
            if "mood" in correct_answer.lower():
                user_answer = "Some mood problem"
            elif "anxiety" in correct_answer.lower():
                user_answer = "Anxiety issue"
            else:
                user_answer = "Wrong answer"
            
            scoring.record_answer(question_num, user_answer, 30.0)
        
        # Calculate scores
        stats = scoring.calculate_scores()
        
        # Should get some partial credit
        assert 0 < stats.total_score <= 2.0
        assert stats.percentage_score > 0

    def test_quiz_generation_with_filters(self, temp_data_dir):
        """Test quiz generation with various filters."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        # Test category filtering
        quiz_config = {
            "num_questions": 1,
            "categories": ["mood_disorders"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        assert len(quiz_data["questions"]) == 1
        question = quiz_data["questions"][0]
        assert question["case_metadata"]["category"] == "mood_disorders"
        
        # Test age group filtering
        quiz_config = {
            "num_questions": 1,
            "age_groups": ["adult"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        question = quiz_data["questions"][0]
        assert question["case_metadata"]["age_group"] == "adult"
        
        # Test complexity filtering
        quiz_config = {
            "num_questions": 1,
            "complexities": ["basic"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        question = quiz_data["questions"][0]
        assert question["case_metadata"]["complexity"] == "basic"

    def test_quiz_generation_with_exclusions(self, temp_data_dir):
        """Test quiz generation with exclusion filters."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        # Exclude mood disorders
        quiz_config = {
            "num_questions": 2,
            "exclude_categories": ["mood_disorders"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        for question in quiz_data["questions"]:
            assert question["case_metadata"]["category"] != "mood_disorders"

    def test_different_quiz_formats(self, temp_data_dir):
        """Test different quiz output formats."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        quiz_config = {
            "num_questions": 1,
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        # Test text format
        text_format = quiz_generator.format_quiz(quiz_data, 'text')
        assert isinstance(text_format, str)
        assert "DIAGNOSIS QUIZ" in text_format
        
        # Test JSON format
        json_format = quiz_generator.format_quiz(quiz_data, 'json')
        assert isinstance(json_format, str)
        parsed = json.loads(json_format)
        assert parsed == quiz_data
        
        # Test CSV format
        csv_format = quiz_generator.format_quiz(quiz_data, 'csv')
        assert isinstance(csv_format, str)
        assert "Question_Number" in csv_format
        
        # Test answer key
        answer_key = quiz_generator.get_answer_key(quiz_data)
        assert isinstance(answer_key, str)
        assert "ANSWER KEY" in answer_key

    def test_performance_analysis_integration(self, temp_data_dir):
        """Test performance analysis integration."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Generate quiz with multiple questions
        quiz_config = {
            "num_questions": 3,
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Record answers with varying performance
        answers = ["Correct", "Wrong", "Correct"]
        times = [30.0, 120.0, 45.0]
        
        for i, question in enumerate(quiz_data["questions"]):
            question_num = question["question_number"]
            correct_answer = question["correct_answer"]
            
            if i < len(answers):
                user_answer = correct_answer if answers[i] == "Correct" else "Wrong Answer"
                scoring.record_answer(question_num, user_answer, times[i])
        
        # Calculate and analyze performance
        stats = scoring.calculate_scores()
        report = scoring.get_performance_report()
        
        # Verify performance analysis
        assert "session_summary" in report
        assert "performance_metrics" in report
        assert "recommendations" in report
        assert "strengths" in report
        assert "areas_for_improvement" in report
        
        # Check category performance
        assert len(stats.category_performance) > 0
        
        # Check time analysis
        assert stats.time_analysis["fastest_question_time"] <= stats.time_analysis["slowest_question_time"]

    def test_error_handling_integration(self, temp_data_dir):
        """Test error handling across the integrated workflow."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Test invalid quiz configuration
        with pytest.raises(ValueError, match="No cases match"):
            quiz_generator.generate_quiz({"categories": ["nonexistent"]})
        
        # Test scoring without session
        with pytest.raises(ValueError, match="Quiz session not started"):
            scoring.record_answer(1, "Test")
        
        # Test scoring with invalid question number
        quiz_config = {"num_questions": 1, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        with pytest.raises(ValueError, match="Invalid question number"):
            scoring.record_answer(99, "Test")

    def test_data_consistency_integration(self, temp_data_dir):
        """Test data consistency across components."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        # Get filtered cases directly
        filtered_cases = data_loader.get_filtered_cases(category="mood_disorders")
        
        # Generate quiz with same filter
        quiz_config = {
            "num_questions": len(filtered_cases),
            "categories": ["mood_disorders"],
            "shuffle": False,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        # Verify consistency
        assert len(quiz_data["questions"]) == len(filtered_cases)
        
        quiz_case_ids = {q["case_id"] for q in quiz_data["questions"]}
        filtered_case_ids = {c["case_id"] for c in filtered_cases}
        
        # Quiz case IDs should be subset of filtered case IDs
        assert quiz_case_ids.issubset(filtered_case_ids)

    def test_caching_integration(self, temp_data_dir):
        """Test caching behavior across components."""
        data_loader = DataLoader(str(temp_data_dir))
        
        # Load data multiple times
        cases1 = data_loader.load_cases()
        cases2 = data_loader.load_cases()
        
        # Should be cached (same object)
        assert cases1 is cases2
        
        # Force reload
        cases3 = data_loader.load_cases(force_reload=True)
        
        # Should be different object
        assert cases1 is not cases3
        
        # But content should be same
        assert cases1 == cases3

    def test_large_quiz_generation(self, temp_data_dir):
        """Test generating larger quizzes."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        # Get all available cases
        all_cases = data_loader.load_cases()
        
        # Request more questions than available
        quiz_config = {
            "num_questions": len(all_cases) + 10,
            "shuffle": True,
            "seed": 42
        }
        
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        # Should use all available cases
        assert len(quiz_data["questions"]) == len(all_cases)
        
        # All questions should be unique
        case_ids = [q["case_id"] for q in quiz_data["questions"]]
        assert len(case_ids) == len(set(case_ids))

    def test_concurrent_sessions(self, temp_data_dir):
        """Test multiple concurrent scoring sessions."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        # Generate quiz data
        quiz_config = {"num_questions": 2, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        # Create multiple scoring instances
        scoring1 = Scoring(scoring_mode=ScoringMode.STRICT)
        scoring2 = Scoring(scoringMode=ScoringMode.LENIENT)
        
        # Start sessions
        scoring1.start_quiz_session(quiz_data)
        scoring2.start_quiz_session(quiz_data)
        
        # Record different answers
        scoring1.record_answer(1, "Correct Answer 1", 30.0)
        scoring2.record_answer(1, "correct answer 1", 30.0)  # Case variation
        
        # Calculate scores
        stats1 = scoring1.calculate_scores()
        stats2 = scoring2.calculate_scores()
        
        # Results should be different due to different scoring modes
        assert stats1.total_score != stats2.total_score or stats1.correct_answers != stats2.correct_answers

    def test_export_format_consistency(self, temp_data_dir):
        """Test consistency across different export formats."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Generate and complete quiz
        quiz_config = {"num_questions": 2, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        for question in quiz_data["questions"]:
            scoring.record_answer(question["question_number"], question["correct_answer"], 30.0)
        
        stats = scoring.calculate_scores()
        
        # Export in all formats
        json_export = scoring.export_results(ExportFormat.JSON)
        text_export = scoring.export_results(ExportFormat.TEXT)
        csv_export = scoring.export_results(ExportFormat.CSV)
        html_export = scoring.export_results(ExportFormat.HTML)
        
        # All should be strings
        assert all(isinstance(export, str) for export in [json_export, text_export, csv_export, html_export])
        
        # JSON should be parseable
        json_data = json.loads(json_export)
        assert json_data["summary"]["total_questions"] == 2
        assert json_data["summary"]["correct_answers"] == 2

    def test_workflow_with_real_data_validation(self, temp_data_dir):
        """Test workflow with real data validation scenarios."""
        data_loader = DataLoader(str(temp_data_dir))
        
        # Test data summary
        summary = data_loader.get_data_summary()
        assert summary["total_cases"] > 0
        assert summary["total_diagnoses"] > 0
        assert len(summary["categories"]) > 0
        
        # Test filtering combinations
        filtered = data_loader.get_filtered_cases(
            category="mood_disorders",
            age_group="adult",
            complexity="basic"
        )
        
        # All filtered cases should match criteria
        for case in filtered:
            assert case["category"] == "mood_disorders"
            assert case["age_group"] == "adult"
            assert case["complexity"] == "basic"

    def test_memory_efficiency_large_dataset(self, temp_data_dir):
        """Test memory efficiency with larger datasets."""
        data_loader = DataLoader(str(temp_data_dir))
        
        # Load data multiple times to test caching
        for _ in range(10):
            cases = data_loader.load_cases()
            diagnoses = data_loader.load_diagnoses()
            assert len(cases) > 0
            assert len(diagnoses) > 0
        
        # Cache should prevent memory bloat
        assert data_loader._cases_cache is not None
        assert data_loader._diagnoses_cache is not None

    def test_edge_case_empty_results(self, temp_data_dir):
        """Test edge cases with empty results."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Generate quiz
        quiz_config = {"num_questions": 2, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Don't record any answers
        stats = scoring.calculate_scores()
        
        # Should handle unanswered questions
        assert stats.total_questions == 2
        assert stats.correct_answers == 0
        assert stats.incorrect_answers == 2
        assert stats.total_score == 0.0

    def test_reproducible_quizzes(self, temp_data_dir):
        """Test quiz reproducibility with seeds."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        
        quiz_config = {
            "num_questions": 2,
            "shuffle": True,
            "seed": 12345
        }
        
        # Generate quiz twice with same seed
        quiz1 = quiz_generator.generate_quiz(quiz_config)
        quiz2 = quiz_generator.generate_quiz(quiz_config)
        
        # Should be identical
        assert quiz1["questions"][0]["case_id"] == quiz2["questions"][0]["case_id"]
        assert quiz1["questions"][1]["case_id"] == quiz2["questions"][1]["case_id"]

    def test_detailed_feedback_integration(self, temp_data_dir):
        """Test detailed feedback integration."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.PARTIAL)
        
        # Generate quiz
        quiz_config = {"num_questions": 2, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Record mixed answers
        for i, question in enumerate(quiz_data["questions"]):
            question_num = question["question_number"]
            correct_answer = question["correct_answer"]
            
            if i == 0:
                user_answer = correct_answer  # Correct
            else:
                user_answer = "Partial answer"  # Partial credit
            
            scoring.record_answer(question_num, user_answer, 30.0)
        
        # Get detailed feedback
        feedback = scoring.get_detailed_feedback()
        
        assert len(feedback) == 2
        assert feedback[0]["is_correct"] is True
        assert feedback[1]["is_correct"] is False
        assert feedback[1]["score"] > 0  # Partial credit

    def test_performance_report_completeness(self, temp_data_dir):
        """Test completeness of performance reports."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Generate and complete quiz
        quiz_config = {"num_questions": 3, "shuffle": False, "seed": 42}
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        scoring.start_quiz_session(quiz_data)
        
        # Record answers
        for question in quiz_data["questions"]:
            scoring.record_answer(question["question_number"], question["correct_answer"], 30.0)
        
        # Generate comprehensive report
        report = scoring.get_performance_report()
        
        # Verify all sections are present
        required_sections = [
            "session_summary", "performance_metrics", "detailed_feedback",
            "recommendations", "strengths", "areas_for_improvement"
        ]
        
        for section in required_sections:
            assert section in report
            assert report[section] is not None

    def test_workflow_robustness(self, temp_data_dir):
        """Test workflow robustness under various conditions."""
        data_loader = DataLoader(str(temp_data_dir))
        quiz_generator = QuizGenerator(data_loader)
        scoring = Scoring(scoring_mode=ScoringMode.STRICT)
        
        # Test with minimal configuration
        minimal_config = {"num_questions": 1}
        quiz_data = quiz_generator.generate_quiz(minimal_config)
        assert len(quiz_data["questions"]) == 1
        
        # Test with maximal configuration
        maximal_config = {
            "num_questions": 2,
            "num_choices": 4,
            "categories": ["mood_disorders", "anxiety_disorders"],
            "age_groups": ["adult", "adolescent"],
            "complexities": ["basic", "intermediate"],
            "shuffle": True,
            "seed": 42
        }
        quiz_data = quiz_generator.generate_quiz(maximal_config)
        assert len(quiz_data["questions"]) == 2
        
        # Test scoring session robustness
        scoring.start_quiz_session(quiz_data)
        
        # Record answers in random order
        questions = quiz_data["questions"]
        for question in questions:
            scoring.record_answer(question["question_number"], question["correct_answer"], 30.0)
        
        stats = scoring.calculate_scores()
        assert stats.total_score == 2.0