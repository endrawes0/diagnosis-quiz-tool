"""
Pytest configuration and shared fixtures for the diagnosis quiz tool tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List

from src.modules.data_loader import DataLoader
from src.modules.quiz_generator import QuizGenerator
from src.modules.scoring import Scoring, ScoringMode


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory with sample data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir)
        schemas_dir = data_dir / "schemas"
        schemas_dir.mkdir()
        
        # Sample schema files
        case_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["case_id", "category", "age_group", "diagnosis", "narrative", "MSE", "complexity"],
                "properties": {
                    "case_id": {"type": "string"},
                    "category": {"type": "string"},
                    "age_group": {"type": "string"},
                    "diagnosis": {"type": "string"},
                    "narrative": {"type": "string"},
                    "MSE": {"type": "string"},
                    "complexity": {"type": "string"}
                }
            }
        }
        
        diagnosis_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "category", "criteria_summary", "prevalence_rate"],
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "criteria_summary": {"type": "string"},
                    "prevalence_rate": {"type": "number"}
                }
            }
        }
        
        config_schema = {
            "type": "object",
            "required": ["num_choices", "shuffle", "filters"],
            "properties": {
                "num_choices": {"type": "integer", "minimum": 2, "maximum": 10},
                "shuffle": {"type": "boolean"},
                "filters": {
                    "type": "object",
                    "properties": {
                        "categories": {"type": "array", "items": {"type": "string"}},
                        "age_groups": {"type": "array", "items": {"type": "string"}},
                        "complexities": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
        
        # Write schema files
        (schemas_dir / "case_schema.json").write_text(json.dumps(case_schema, indent=2))
        (schemas_dir / "diagnosis_schema.json").write_text(json.dumps(diagnosis_schema, indent=2))
        (schemas_dir / "config_schema.json").write_text(json.dumps(config_schema, indent=2))
        
        # Sample cases data
        cases_data = [
            {
                "case_id": "TEST-001",
                "category": "mood_disorders",
                "age_group": "adult",
                "diagnosis": "Major Depressive Disorder",
                "narrative": "A 35-year-old patient presents with persistent low mood, anhedonia, and sleep disturbances.",
                "MSE": "Patient appears sad, psychomotor retardation noted, speech is slow and monotone.",
                "complexity": "basic"
            },
            {
                "case_id": "TEST-002",
                "category": "anxiety_disorders",
                "age_group": "adolescent",
                "diagnosis": "Generalized Anxiety Disorder",
                "narrative": "A 16-year-old student reports excessive worry about school performance and health.",
                "MSE": "Patient appears tense, restless, and reports difficulty concentrating.",
                "complexity": "intermediate"
            },
            {
                "case_id": "TEST-003",
                "category": "psychotic_disorders",
                "age_group": "adult",
                "diagnosis": "Schizophrenia",
                "narrative": "A 28-year-old patient presents with auditory hallucinations and delusional thinking.",
                "MSE": "Patient appears disorganized, with inappropriate affect and thought blocking.",
                "complexity": "advanced"
            }
        ]
        
        # Sample diagnoses data
        diagnoses_data = [
            {
                "name": "Major Depressive Disorder",
                "category": "mood_disorders",
                "criteria_summary": "Persistent depressed mood and loss of interest for at least 2 weeks.",
                "prevalence_rate": 0.07
            },
            {
                "name": "Generalized Anxiety Disorder",
                "category": "anxiety_disorders",
                "criteria_summary": "Excessive anxiety and worry occurring more days than not for 6 months.",
                "prevalence_rate": 0.03
            },
            {
                "name": "Schizophrenia",
                "category": "psychotic_disorders",
                "criteria_summary": "Two or more psychotic symptoms for 1 month with functional decline.",
                "prevalence_rate": 0.01
            },
            {
                "name": "Bipolar Disorder",
                "category": "mood_disorders",
                "criteria_summary": "Episodes of mania and depression with periods of normal mood.",
                "prevalence_rate": 0.02
            },
            {
                "name": "Panic Disorder",
                "category": "anxiety_disorders",
                "criteria_summary": "Recurrent unexpected panic attacks with persistent concern about having more.",
                "prevalence_rate": 0.02
            }
        ]
        
        # Sample config data
        config_data = {
            "num_choices": 4,
            "shuffle": True,
            "filters": {
                "categories": ["mood_disorders", "anxiety_disorders", "psychotic_disorders"],
                "age_groups": ["child", "adolescent", "adult", "older_adult"],
                "complexities": ["basic", "intermediate", "advanced"]
            }
        }
        
        # Write data files
        (data_dir / "cases.json").write_text(json.dumps(cases_data, indent=2))
        (data_dir / "diagnoses.json").write_text(json.dumps(diagnoses_data, indent=2))
        (data_dir / "config.json").write_text(json.dumps(config_data, indent=2))
        
        yield data_dir


@pytest.fixture
def sample_cases():
    """Sample cases data for testing."""
    return [
        {
            "case_id": "TEST-001",
            "category": "mood_disorders",
            "age_group": "adult",
            "diagnosis": "Major Depressive Disorder",
            "narrative": "A 35-year-old patient presents with persistent low mood.",
            "MSE": "Patient appears sad with psychomotor retardation.",
            "complexity": "basic"
        },
        {
            "case_id": "TEST-002",
            "category": "anxiety_disorders",
            "age_group": "adolescent",
            "diagnosis": "Generalized Anxiety Disorder",
            "narrative": "A 16-year-old student reports excessive worry.",
            "MSE": "Patient appears tense and restless.",
            "complexity": "intermediate"
        }
    ]


@pytest.fixture
def sample_diagnoses():
    """Sample diagnoses data for testing."""
    return [
        {
            "name": "Major Depressive Disorder",
            "category": "mood_disorders",
            "criteria_summary": "Persistent depressed mood for at least 2 weeks.",
            "prevalence_rate": 0.07
        },
        {
            "name": "Generalized Anxiety Disorder",
            "category": "anxiety_disorders",
            "criteria_summary": "Excessive anxiety and worry for 6 months.",
            "prevalence_rate": 0.03
        },
        {
            "name": "Schizophrenia",
            "category": "psychotic_disorders",
            "criteria_summary": "Psychotic symptoms with functional decline.",
            "prevalence_rate": 0.01
        }
    ]


@pytest.fixture
def sample_quiz_config():
    """Sample quiz configuration for testing."""
    return {
        "num_questions": 5,
        "num_choices": 4,
        "categories": ["mood_disorders", "anxiety_disorders"],
        "age_groups": ["adult", "adolescent"],
        "complexities": ["basic", "intermediate"],
        "shuffle": True,
        "seed": 42
    }


@pytest.fixture
def data_loader(temp_data_dir):
    """DataLoader instance with temporary data directory."""
    return DataLoader(str(temp_data_dir))


@pytest.fixture
def quiz_generator(data_loader):
    """QuizGenerator instance with test data loader."""
    return QuizGenerator(data_loader)


@pytest.fixture
def scoring_strict():
    """Scoring instance with strict mode."""
    return Scoring(scoring_mode=ScoringMode.STRICT)


@pytest.fixture
def scoring_lenient():
    """Scoring instance with lenient mode."""
    return Scoring(scoring_mode=ScoringMode.LENIENT)


@pytest.fixture
def scoring_partial():
    """Scoring instance with partial credit mode."""
    return Scoring(scoring_mode=ScoringMode.PARTIAL)


@pytest.fixture
def sample_quiz_data():
    """Sample quiz data for testing scoring functionality."""
    return {
        "quiz_metadata": {
            "total_questions": 2,
            "num_choices": 4,
            "configuration": {"test": True},
            "generated_at": "2023-01-01T00:00:00"
        },
        "questions": [
            {
                "question_number": 1,
                "case_id": "TEST-001",
                "question_text": "What is the diagnosis for this case?",
                "options": ["Major Depressive Disorder", "Bipolar Disorder", "Anxiety Disorder", "Schizophrenia"],
                "correct_answer": "Major Depressive Disorder",
                "correct_index": 0,
                "case_metadata": {
                    "category": "mood_disorders",
                    "age_group": "adult",
                    "complexity": "basic"
                }
            },
            {
                "question_number": 2,
                "case_id": "TEST-002",
                "question_text": "What is the diagnosis for this case?",
                "options": ["Major Depressive Disorder", "Generalized Anxiety Disorder", "Panic Disorder", "OCD"],
                "correct_answer": "Generalized Anxiety Disorder",
                "correct_index": 1,
                "case_metadata": {
                    "category": "anxiety_disorders",
                    "age_group": "adolescent",
                    "complexity": "intermediate"
                }
            }
        ]
    }


@pytest.fixture
def invalid_cases_data():
    """Invalid cases data for testing error handling."""
    return [
        {
            # Missing required fields
            "case_id": "INVALID-001",
            "category": "mood_disorders"
            # Missing age_group, diagnosis, narrative, MSE, complexity
        },
        {
            # Invalid field types
            "case_id": 123,  # Should be string
            "category": "mood_disorders",
            "age_group": "adult",
            "diagnosis": "Major Depressive Disorder",
            "narrative": "Test narrative",
            "MSE": "Test MSE",
            "complexity": "basic"
        }
    ]


@pytest.fixture
def invalid_diagnoses_data():
    """Invalid diagnoses data for testing error handling."""
    return [
        {
            # Missing required fields
            "name": "Invalid Disorder",
            "category": "test_category"
            # Missing criteria_summary, prevalence_rate
        },
        {
            # Invalid field types
            "name": "Another Invalid Disorder",
            "category": "test_category",
            "criteria_summary": "Test criteria",
            "prevalence_rate": "high"  # Should be number
        }
    ]