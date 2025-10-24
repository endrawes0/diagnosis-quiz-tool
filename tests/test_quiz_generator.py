"""
Unit tests for the QuizGenerator class.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

from src.modules.quiz_generator import QuizGenerator


class TestQuizGenerator:
    """Test cases for QuizGenerator class."""

    def test_init(self, data_loader):
        """Test QuizGenerator initialization."""
        generator = QuizGenerator(data_loader)
        assert generator.data_loader is data_loader
        assert generator.logger is not None

    def test_generate_quiz_success(self, quiz_generator, sample_quiz_config):
        """Test successful quiz generation."""
        quiz_data = quiz_generator.generate_quiz(sample_quiz_config)
        
        assert isinstance(quiz_data, dict)
        assert "quiz_metadata" in quiz_data
        assert "questions" in quiz_data
        
        metadata = quiz_data["quiz_metadata"]
        assert "total_questions" in metadata
        assert "num_choices" in metadata
        assert "configuration" in metadata
        assert "generated_at" in metadata
        
        questions = quiz_data["questions"]
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        # Check question structure
        question = questions[0]
        required_fields = [
            'question_number', 'case_id', 'question_text',
            'options', 'correct_answer', 'correct_index', 'case_metadata'
        ]
        for field in required_fields:
            assert field in question

    def test_generate_quiz_with_seed(self, quiz_generator, sample_quiz_config):
        """Test quiz generation with random seed for reproducibility."""
        config_with_seed = sample_quiz_config.copy()
        config_with_seed["seed"] = 42
        
        quiz1 = quiz_generator.generate_quiz(config_with_seed)
        quiz2 = quiz_generator.generate_quiz(config_with_seed)
        
        # Should be identical due to same seed
        assert quiz1["questions"][0]["case_id"] == quiz2["questions"][0]["case_id"]

    def test_generate_quiz_no_matching_cases(self, quiz_generator):
        """Test quiz generation when no cases match criteria."""
        config = {
            "num_questions": 5,
            "categories": ["nonexistent_category"]
        }
        
        with pytest.raises(ValueError, match="No cases match the specified criteria"):
            quiz_generator.generate_quiz(config)

    def test_generate_quiz_fewer_cases_than_requested(self, quiz_generator):
        """Test quiz generation when fewer cases available than requested."""
        config = {
            "num_questions": 100,  # Request more than available
            "categories": ["mood_disorders"]
        }
        
        quiz_data = quiz_generator.generate_quiz(config)
        
        # Should use all available cases
        assert len(quiz_data["questions"]) <= 100

    def test_generate_quiz_default_config(self, quiz_generator):
        """Test quiz generation with minimal configuration."""
        config = {"num_questions": 2}
        
        quiz_data = quiz_generator.generate_quiz(config)
        
        assert len(quiz_data["questions"]) == 2
        assert quiz_data["quiz_metadata"]["num_choices"] == 4  # Default value

    def test_create_question(self, quiz_generator):
        """Test single question creation."""
        case = {
            "case_id": "TEST-001",
            "category": "mood_disorders",
            "age_group": "adult",
            "complexity": "basic",
            "diagnosis": "Major Depressive Disorder",
            "narrative": "Test narrative",
            "MSE": "Test MSE"
        }
        
        diagnosis_by_category = {
            "mood_disorders": ["Major Depressive Disorder", "Bipolar Disorder"],
            "anxiety_disorders": ["Generalized Anxiety Disorder", "Panic Disorder"]
        }
        
        question = quiz_generator._create_question(case, diagnosis_by_category, 4, 1)
        
        assert question["question_number"] == 1
        assert question["case_id"] == "TEST-001"
        assert question["correct_answer"] == "Major Depressive Disorder"
        assert len(question["options"]) == 4
        assert question["correct_index"] in range(4)
        assert "question_text" in question
        assert "case_metadata" in question

    def test_generate_distractors_same_category(self, quiz_generator):
        """Test distractor generation from same category."""
        diagnosis_by_category = {
            "mood_disorders": ["Major Depressive Disorder", "Bipolar Disorder", "Dysthymia"]
        }
        
        distractors = quiz_generator._generate_distractors(
            "Major Depressive Disorder", "mood_disorders", diagnosis_by_category, 2
        )
        
        assert len(distractors) == 2
        assert "Major Depressive Disorder" not in distractors
        assert all(d in diagnosis_by_category["mood_disorders"] for d in distractors)

    def test_generate_distractors_different_categories(self, quiz_generator):
        """Test distractor generation from different categories."""
        diagnosis_by_category = {
            "mood_disorders": ["Major Depressive Disorder"],
            "anxiety_disorders": ["Generalized Anxiety Disorder", "Panic Disorder"],
            "psychotic_disorders": ["Schizophrenia"]
        }
        
        distractors = quiz_generator._generate_distractors(
            "Major Depressive Disorder", "mood_disorders", diagnosis_by_category, 3
        )
        
        assert len(distractors) == 3
        assert "Major Depressive Disorder" not in distractors
        # Should include from other categories when same category doesn't have enough

    def test_generate_distractors_fallback_generic(self, quiz_generator):
        """Test generic distractor fallback when not enough diagnoses available."""
        diagnosis_by_category = {
            "mood_disorders": ["Major Depressive Disorder"]  # Only one diagnosis
        }
        
        distractors = quiz_generator._generate_distractors(
            "Major Depressive Disorder", "mood_disorders", diagnosis_by_category, 2
        )
        
        assert len(distractors) == 2
        assert "Major Depressive Disorder" not in distractors
        # Should include generic distractors

    def test_format_question_text(self, quiz_generator):
        """Test question text formatting."""
        case = {
            "case_id": "TEST-001",
            "age_group": "adult",
            "category": "mood_disorders",
            "narrative": "Patient presents with low mood.",
            "MSE": "Patient appears sad."
        }
        
        question_text = quiz_generator._format_question_text(case)
        
        assert "TEST-001" in question_text
        assert "adult" in question_text
        assert "mood_disorders" in question_text
        assert "Patient presents with low mood." in question_text
        assert "Patient appears sad." in question_text
        assert "most likely diagnosis" in question_text

    def test_format_quiz_text(self, quiz_generator, sample_quiz_data):
        """Test quiz formatting as text."""
        formatted = quiz_generator.format_quiz(sample_quiz_data, 'text')
        
        assert isinstance(formatted, str)
        assert "DIAGNOSIS QUIZ" in formatted
        assert "Question 1" in formatted
        assert "Correct Answer:" in formatted

    def test_format_quiz_json(self, quiz_generator, sample_quiz_data):
        """Test quiz formatting as JSON."""
        formatted = quiz_generator.format_quiz(sample_quiz_data, 'json')
        
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert parsed == sample_quiz_data

    def test_format_quiz_csv(self, quiz_generator, sample_quiz_data):
        """Test quiz formatting as CSV."""
        formatted = quiz_generator.format_quiz(sample_quiz_data, 'csv')
        
        assert isinstance(formatted, str)
        lines = formatted.strip().split('\n')
        assert len(lines) > 1  # Header + at least one question
        assert "Question_Number" in lines[0]
        assert "Case_ID" in lines[0]

    def test_format_quiz_unsupported_format(self, quiz_generator, sample_quiz_data):
        """Test quiz formatting with unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format type"):
            quiz_generator.format_quiz(sample_quiz_data, 'unsupported')

    def test_get_answer_key(self, quiz_generator, sample_quiz_data):
        """Test answer key generation."""
        answer_key = quiz_generator.get_answer_key(sample_quiz_data)
        
        assert isinstance(answer_key, str)
        assert "ANSWER KEY" in answer_key
        assert "Q1:" in answer_key
        assert "Q2:" in answer_key
        assert "Case ID:" in answer_key

    def test_get_timestamp(self, quiz_generator):
        """Test timestamp generation."""
        timestamp = quiz_generator._get_timestamp()
        assert isinstance(timestamp, str)
        # Should be in ISO format
        assert "T" in timestamp

    def test_question_shuffling(self, quiz_generator, sample_quiz_config):
        """Test that questions are shuffled when requested."""
        config_shuffle = sample_quiz_config.copy()
        config_shuffle["shuffle"] = True
        config_shuffle["seed"] = None  # No seed for random shuffling
        
        quiz1 = quiz_generator.generate_quiz(config_shuffle)
        quiz2 = quiz_generator.generate_quiz(config_shuffle)
        
        # Questions should be in different order (most likely)
        # Note: This test might occasionally fail due to random chance
        case_ids1 = [q["case_id"] for q in quiz1["questions"]]
        case_ids2 = [q["case_id"] for q in quiz2["questions"]]
        
        # At least one question should be in different position
        positions_differ = any(
            case_ids1[i] != case_ids2[i] for i in range(len(case_ids1))
        )
        assert positions_differ

    def test_question_no_shuffling(self, quiz_generator, sample_quiz_config):
        """Test that questions are not shuffled when not requested."""
        config_no_shuffle = sample_quiz_config.copy()
        config_no_shuffle["shuffle"] = False
        config_no_shuffle["seed"] = 42
        
        quiz1 = quiz_generator.generate_quiz(config_no_shuffle)
        quiz2 = quiz_generator.generate_quiz(config_no_shuffle)
        
        # Questions should be in same order
        case_ids1 = [q["case_id"] for q in quiz1["questions"]]
        case_ids2 = [q["case_id"] for q in quiz2["questions"]]
        
        assert case_ids1 == case_ids2

    def test_csv_format_different_num_choices(self, quiz_generator):
        """Test CSV formatting with different number of choices."""
        # Create quiz data with 3 choices
        quiz_data = {
            "quiz_metadata": {
                "total_questions": 1,
                "num_choices": 3
            },
            "questions": [
                {
                    "question_number": 1,
                    "case_id": "TEST-001",
                    "question_text": "Test question",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                    "correct_index": 0,
                    "case_metadata": {
                        "category": "test",
                        "age_group": "test",
                        "complexity": "test"
                    }
                }
            ]
        }
        
        csv_output = quiz_generator._format_csv(quiz_data)
        lines = csv_output.strip().split('\n')
        
        # Should have headers for 3 options
        header = lines[0]
        assert "Option_A" in header
        assert "Option_B" in header
        assert "Option_C" in header
        assert "Option_D" not in header

    def test_error_handling_in_generate_quiz(self, quiz_generator):
        """Test error handling in quiz generation."""
        # Mock data_loader to raise an exception
        quiz_generator.data_loader.get_filtered_cases = MagicMock(side_effect=Exception("Test error"))
        
        config = {"num_questions": 5}
        
        with pytest.raises(Exception, match="Test error"):
            quiz_generator.generate_quiz(config)

    def test_error_handling_in_format_quiz(self, quiz_generator):
        """Test error handling in quiz formatting."""
        # Mock format method to raise an exception
        with patch.object(quiz_generator, '_format_text', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Failed to format quiz"):
                quiz_generator.format_quiz({}, 'text')

    def test_error_handling_in_get_answer_key(self, quiz_generator):
        """Test error handling in answer key generation."""
        # Mock to raise an exception
        with patch('builtins.str.join', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Failed to generate answer key"):
                quiz_generator.get_answer_key({})

    def test_logging_setup(self, quiz_generator):
        """Test that logging is properly set up."""
        assert quiz_generator.logger is not None
        assert len(quiz_generator.logger.handlers) > 0

    def test_question_numbering_after_shuffle(self, quiz_generator, sample_quiz_config):
        """Test that question numbers are correctly renumbered after shuffling."""
        config = sample_quiz_config.copy()
        config["num_questions"] = 3
        config["shuffle"] = True
        config["seed"] = 42
        
        quiz_data = quiz_generator.generate_quiz(config)
        questions = quiz_data["questions"]
        
        # Question numbers should be sequential starting from 1
        for i, question in enumerate(questions):
            assert question["question_number"] == i + 1

    def test_correct_answer_index_accuracy(self, quiz_generator):
        """Test that correct_answer_index matches the correct answer position."""
        case = {
            "case_id": "TEST-001",
            "category": "mood_disorders",
            "age_group": "adult",
            "complexity": "basic",
            "diagnosis": "Major Depressive Disorder",
            "narrative": "Test narrative",
            "MSE": "Test MSE"
        }
        
        diagnosis_by_category = {
            "mood_disorders": ["Major Depressive Disorder", "Bipolar Disorder", "Dysthymia", "Cyclothymia"]
        }
        
        question = quiz_generator._create_question(case, diagnosis_by_category, 4, 1)
        
        # The correct answer should be at the specified index
        assert question["options"][question["correct_index"]] == question["correct_answer"]

    def test_case_metadata_inclusion(self, quiz_generator):
        """Test that case metadata is properly included in questions."""
        case = {
            "case_id": "TEST-001",
            "category": "mood_disorders",
            "age_group": "adult",
            "complexity": "basic",
            "diagnosis": "Major Depressive Disorder",
            "narrative": "Test narrative",
            "MSE": "Test MSE"
        }
        
        diagnosis_by_category = {"mood_disorders": ["Major Depressive Disorder", "Bipolar Disorder"]}
        
        question = quiz_generator._create_question(case, diagnosis_by_category, 4, 1)
        
        metadata = question["case_metadata"]
        assert metadata["category"] == "mood_disorders"
        assert metadata["age_group"] == "adult"
        assert metadata["complexity"] == "basic"

    def test_empty_diagnosis_by_category(self, quiz_generator):
        """Test question creation when diagnosis_by_category is empty."""
        case = {
            "case_id": "TEST-001",
            "category": "unknown_category",
            "age_group": "adult",
            "complexity": "basic",
            "diagnosis": "Unknown Disorder",
            "narrative": "Test narrative",
            "MSE": "Test MSE"
        }
        
        diagnosis_by_category = {}  # Empty
        
        question = quiz_generator._create_question(case, diagnosis_by_category, 4, 1)
        
        # Should still create a question with generic distractors
        assert len(question["options"]) == 4
        assert question["correct_answer"] == "Unknown Disorder"

    def test_config_parameter_extraction(self, quiz_generator):
        """Test that config parameters are properly extracted with defaults."""
        config = {
            "num_questions": 5,
            "num_choices": 3,
            "shuffle": False
        }
        
        # Mock the data_loader to avoid actual data loading
        quiz_generator.data_loader.get_filtered_cases = MagicMock(return_value=[
            {
                "case_id": "TEST-001",
                "category": "mood_disorders",
                "age_group": "adult",
                "complexity": "basic",
                "diagnosis": "Major Depressive Disorder",
                "narrative": "Test",
                "MSE": "Test"
            }
        ])
        quiz_generator.data_loader.load_diagnoses = MagicMock(return_value=[
            {"name": "Major Depressive Disorder", "category": "mood_disorders"}
        ])
        
        quiz_data = quiz_generator.generate_quiz(config)
        
        assert quiz_data["quiz_metadata"]["num_choices"] == 3
        assert len(quiz_data["questions"]) == 1  # Only one case available