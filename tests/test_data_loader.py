"""
Unit tests for the DataLoader class.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.modules.data_loader import DataLoader
from jsonschema import ValidationError


class TestDataLoader:
    """Test cases for DataLoader class."""

    def test_init_default_path(self):
        """Test DataLoader initialization with default path."""
        loader = DataLoader()
        expected_path = Path(__file__).parent.parent.parent / "data"
        assert loader.data_dir == expected_path
        assert loader.schemas_dir == expected_path / "schemas"

    def test_init_custom_path(self, temp_data_dir):
        """Test DataLoader initialization with custom path."""
        loader = DataLoader(str(temp_data_dir))
        assert loader.data_dir == temp_data_dir
        assert loader.schemas_dir == temp_data_dir / "schemas"

    def test_load_schema_success(self, data_loader):
        """Test successful schema loading."""
        schema = data_loader._load_schema("case_schema")
        assert isinstance(schema, dict)
        assert "type" in schema
        assert schema["type"] == "array"

    def test_load_schema_cached(self, data_loader):
        """Test that schemas are cached after first load."""
        schema1 = data_loader._load_schema("case_schema")
        schema2 = data_loader._load_schema("case_schema")
        assert schema1 is schema2  # Should be the same object due to caching

    def test_load_schema_not_found(self, data_loader):
        """Test loading non-existent schema file."""
        with pytest.raises(FileNotFoundError):
            data_loader._load_schema("nonexistent_schema")

    def test_load_schema_invalid_json(self, data_loader):
        """Test loading schema file with invalid JSON."""
        # Create a temporary invalid JSON file
        invalid_schema_path = data_loader.schemas_dir / "invalid_schema.json"
        invalid_schema_path.write_text("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            data_loader._load_schema("invalid_schema")

    def test_validate_data_success(self, data_loader):
        """Test successful data validation."""
        schema = {"type": "string"}
        data = "test string"
        assert data_loader._validate_data(data, schema) is True

    def test_validate_data_failure(self, data_loader):
        """Test data validation failure."""
        schema = {"type": "string"}
        data = 123  # Not a string
        with pytest.raises(ValidationError):
            data_loader._validate_data(data, schema)

    def test_validate_invalid_schema(self, data_loader):
        """Test validation with invalid schema."""
        invalid_schema = {"type": "invalid_type"}
        data = "test"
        with pytest.raises(ValidationError):
            data_loader._validate_data(data, invalid_schema)

    def test_load_json_file_success(self, data_loader):
        """Test successful JSON file loading."""
        # Create a temporary JSON file
        test_file = data_loader.data_dir / "test.json"
        test_data = {"test": "data"}
        test_file.write_text(json.dumps(test_data))
        
        loaded_data = data_loader._load_json_file(test_file)
        assert loaded_data == test_data

    def test_load_json_file_not_found(self, data_loader):
        """Test loading non-existent JSON file."""
        non_existent_file = data_loader.data_dir / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            data_loader._load_json_file(non_existent_file)

    def test_load_json_file_invalid_json(self, data_loader):
        """Test loading JSON file with invalid JSON."""
        invalid_file = data_loader.data_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        with pytest.raises(json.JSONDecodeError):
            data_loader._load_json_file(invalid_file)

    def test_load_cases_success(self, data_loader):
        """Test successful cases loading."""
        cases = data_loader.load_cases()
        assert isinstance(cases, list)
        assert len(cases) > 0
        
        # Check structure of first case
        case = cases[0]
        required_fields = ['case_id', 'category', 'age_group', 'diagnosis', 'narrative', 'MSE', 'complexity']
        for field in required_fields:
            assert field in case

    def test_load_cases_cached(self, data_loader):
        """Test that cases are cached after first load."""
        cases1 = data_loader.load_cases()
        cases2 = data_loader.load_cases()
        assert cases1 is cases2  # Should be the same object due to caching

    def test_load_cases_force_reload(self, data_loader):
        """Test force reload bypasses cache."""
        cases1 = data_loader.load_cases()
        cases2 = data_loader.load_cases(force_reload=True)
        assert cases1 is not cases2  # Should be different objects

    def test_load_cases_invalid_structure(self, temp_data_dir):
        """Test loading cases with invalid structure."""
        # Create invalid cases file
        cases_file = temp_data_dir / "cases.json"
        cases_file.write_text('{"not": "a list"}')  # Should be a list
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(ValidationError):
            loader.load_cases()

    def test_load_cases_missing_required_fields(self, temp_data_dir):
        """Test loading cases with missing required fields."""
        invalid_cases = [
            {
                "case_id": "TEST-001",
                "category": "mood_disorders"
                # Missing other required fields
            }
        ]
        
        cases_file = temp_data_dir / "cases.json"
        cases_file.write_text(json.dumps(invalid_cases))
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(ValidationError):
            loader.load_cases()

    def test_load_cases_invalid_field_types(self, temp_data_dir):
        """Test loading cases with invalid field types."""
        invalid_cases = [
            {
                "case_id": 123,  # Should be string
                "category": "mood_disorders",
                "age_group": "adult",
                "diagnosis": "Test Diagnosis",
                "narrative": "Test narrative",
                "MSE": "Test MSE",
                "complexity": "basic"
            }
        ]
        
        cases_file = temp_data_dir / "cases.json"
        cases_file.write_text(json.dumps(invalid_cases))
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(ValidationError):
            loader.load_cases()

    def test_load_diagnoses_success(self, data_loader):
        """Test successful diagnoses loading."""
        diagnoses = data_loader.load_diagnoses()
        assert isinstance(diagnoses, list)
        assert len(diagnoses) > 0
        
        # Check structure of first diagnosis
        diagnosis = diagnoses[0]
        required_fields = ['name', 'category', 'criteria_summary', 'prevalence_rate']
        for field in required_fields:
            assert field in diagnosis

    def test_load_diagnoses_cached(self, data_loader):
        """Test that diagnoses are cached after first load."""
        diagnoses1 = data_loader.load_diagnoses()
        diagnoses2 = data_loader.load_diagnoses()
        assert diagnoses1 is diagnoses2  # Should be the same object due to caching

    def test_load_diagnoses_force_reload(self, data_loader):
        """Test force reload bypasses cache."""
        diagnoses1 = data_loader.load_diagnoses()
        diagnoses2 = data_loader.load_diagnoses(force_reload=True)
        assert diagnoses1 is not diagnoses2  # Should be different objects

    def test_load_diagnoses_invalid_structure(self, temp_data_dir):
        """Test loading diagnoses with invalid structure."""
        diagnoses_file = temp_data_dir / "diagnoses.json"
        diagnoses_file.write_text('{"not": "a list"}')  # Should be a list
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(ValidationError):
            loader.load_diagnoses()

    def test_load_diagnoses_missing_required_fields(self, temp_data_dir):
        """Test loading diagnoses with missing required fields."""
        invalid_diagnoses = [
            {
                "name": "Test Disorder",
                "category": "test_category"
                # Missing other required fields
            }
        ]
        
        diagnoses_file = temp_data_dir / "diagnoses.json"
        diagnoses_file.write_text(json.dumps(invalid_diagnoses))
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(ValidationError):
            loader.load_diagnoses()

    def test_load_config_success(self, data_loader):
        """Test successful config loading."""
        config = data_loader.load_config()
        assert isinstance(config, dict)
        assert "num_choices" in config
        assert "shuffle" in config
        assert "filters" in config

    def test_load_config_not_found(self, temp_data_dir):
        """Test loading config when file doesn't exist (should use default)."""
        # Remove config file
        config_file = temp_data_dir / "config.json"
        if config_file.exists():
            config_file.unlink()
        
        loader = DataLoader(str(temp_data_dir))
        config = loader.load_config()
        
        # Should return default config
        assert isinstance(config, dict)
        assert "num_choices" in config

    def test_load_config_invalid_json(self, temp_data_dir):
        """Test loading config with invalid JSON."""
        config_file = temp_data_dir / "config.json"
        config_file.write_text("{ invalid json }")
        
        loader = DataLoader(str(temp_data_dir))
        with pytest.raises(json.JSONDecodeError):
            loader.load_config()

    def test_get_filtered_cases_by_category(self, data_loader):
        """Test filtering cases by category."""
        filtered = data_loader.get_filtered_cases(category="mood_disorders")
        assert all(case["category"] == "mood_disorders" for case in filtered)

    def test_get_filtered_cases_by_multiple_categories(self, data_loader):
        """Test filtering cases by multiple categories."""
        categories = ["mood_disorders", "anxiety_disorders"]
        filtered = data_loader.get_filtered_cases(category=categories)
        assert all(case["category"] in categories for case in filtered)

    def test_get_filtered_cases_by_age_group(self, data_loader):
        """Test filtering cases by age group."""
        filtered = data_loader.get_filtered_cases(age_group="adult")
        assert all(case["age_group"] == "adult" for case in filtered)

    def test_get_filtered_cases_by_complexity(self, data_loader):
        """Test filtering cases by complexity."""
        filtered = data_loader.get_filtered_cases(complexity="basic")
        assert all(case["complexity"] == "basic" for case in filtered)

    def test_get_filtered_cases_by_diagnosis(self, data_loader):
        """Test filtering cases by diagnosis."""
        filtered = data_loader.get_filtered_cases(diagnosis="Major Depressive Disorder")
        assert all(case["diagnosis"] == "Major Depressive Disorder" for case in filtered)

    def test_get_filtered_cases_by_case_id(self, data_loader):
        """Test filtering cases by case ID."""
        filtered = data_loader.get_filtered_cases(case_id="TEST-001")
        assert len(filtered) == 1
        assert filtered[0]["case_id"] == "TEST-001"

    def test_get_filtered_cases_exclude_category(self, data_loader):
        """Test excluding cases by category."""
        filtered = data_loader.get_filtered_cases(exclude_category="mood_disorders")
        assert all(case["category"] != "mood_disorders" for case in filtered)

    def test_get_filtered_cases_multiple_filters(self, data_loader):
        """Test filtering with multiple criteria."""
        filtered = data_loader.get_filtered_cases(
            category="mood_disorders",
            age_group="adult",
            complexity="basic"
        )
        for case in filtered:
            assert case["category"] == "mood_disorders"
            assert case["age_group"] == "adult"
            assert case["complexity"] == "basic"

    def test_get_filtered_cases_no_matches(self, data_loader):
        """Test filtering with no matching cases."""
        filtered = data_loader.get_filtered_cases(category="nonexistent_category")
        assert len(filtered) == 0

    def test_get_case_by_id_found(self, data_loader):
        """Test getting a specific case by ID."""
        case = data_loader.get_case_by_id("TEST-001")
        assert case is not None
        assert case["case_id"] == "TEST-001"

    def test_get_case_by_id_not_found(self, data_loader):
        """Test getting a non-existent case by ID."""
        case = data_loader.get_case_by_id("NONEXISTENT")
        assert case is None

    def test_get_diagnosis_by_name_found(self, data_loader):
        """Test getting a specific diagnosis by name."""
        diagnosis = data_loader.get_diagnosis_by_name("Major Depressive Disorder")
        assert diagnosis is not None
        assert diagnosis["name"] == "Major Depressive Disorder"

    def test_get_diagnosis_by_name_not_found(self, data_loader):
        """Test getting a non-existent diagnosis by name."""
        diagnosis = data_loader.get_diagnosis_by_name("Nonexistent Disorder")
        assert diagnosis is None

    def test_get_categories(self, data_loader):
        """Test getting all unique categories."""
        categories = data_loader.get_categories()
        assert isinstance(categories, list)
        assert "mood_disorders" in categories
        assert "anxiety_disorders" in categories

    def test_get_age_groups(self, data_loader):
        """Test getting all unique age groups."""
        age_groups = data_loader.get_age_groups()
        assert isinstance(age_groups, list)
        assert "adult" in age_groups
        assert "adolescent" in age_groups

    def test_get_complexity_levels(self, data_loader):
        """Test getting all unique complexity levels."""
        complexities = data_loader.get_complexity_levels()
        assert isinstance(complexities, list)
        assert "basic" in complexities
        assert "intermediate" in complexities

    def test_clear_cache(self, data_loader):
        """Test clearing the cache."""
        # Load some data to populate cache
        data_loader.load_cases()
        data_loader.load_diagnoses()
        data_loader.load_config()
        
        # Clear cache
        data_loader.clear_cache()
        
        # Cache should be empty
        assert data_loader._cases_cache is None
        assert data_loader._diagnoses_cache is None
        assert data_loader._config_cache is None
        assert len(data_loader._schemas_cache) == 0

    def test_get_data_summary(self, data_loader):
        """Test getting data summary."""
        summary = data_loader.get_data_summary()
        
        assert isinstance(summary, dict)
        assert "total_cases" in summary
        assert "total_diagnoses" in summary
        assert "categories" in summary
        assert "age_groups" in summary
        assert "complexity_levels" in summary
        assert "cases_by_category" in summary
        assert "cases_by_age_group" in summary
        assert "cases_by_complexity" in summary
        
        assert summary["total_cases"] > 0
        assert summary["total_diagnoses"] > 0

    def test_get_data_summary_force_reload(self, data_loader):
        """Test getting data summary with force reload."""
        summary1 = data_loader.get_data_summary()
        summary2 = data_loader.get_data_summary(force_reload=True)
        
        # Should have same structure but potentially different objects
        assert summary1["total_cases"] == summary2["total_cases"]
        assert summary1["total_diagnoses"] == summary2["total_diagnoses"]

    def test_to_list_helper_function(self, data_loader):
        """Test the internal to_list helper function."""
        # Test with None
        result = data_loader._DataLoader__to_list(None)
        assert result is None
        
        # Test with string
        result = data_loader._DataLoader__to_list("test")
        assert result == ["test"]
        
        # Test with list
        result = data_loader._DataLoader__to_list(["test1", "test2"])
        assert result == ["test1", "test2"]

    def test_logging_setup(self, data_loader):
        """Test that logging is properly set up."""
        assert data_loader.logger is not None
        assert len(data_loader.logger.handlers) > 0

    def test_error_handling_in_get_filtered_cases(self, data_loader):
        """Test error handling in get_filtered_cases method."""
        # Mock load_cases to raise an exception
        with patch.object(data_loader, 'load_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_filtered_cases()

    def test_error_handling_in_get_case_by_id(self, data_loader):
        """Test error handling in get_case_by_id method."""
        # Mock get_filtered_cases to raise an exception
        with patch.object(data_loader, 'get_filtered_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_case_by_id("TEST-001")

    def test_error_handling_in_get_diagnosis_by_name(self, data_loader):
        """Test error handling in get_diagnosis_by_name method."""
        # Mock load_diagnoses to raise an exception
        with patch.object(data_loader, 'load_diagnoses', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_diagnosis_by_name("Test Diagnosis")

    def test_error_handling_in_get_categories(self, data_loader):
        """Test error handling in get_categories method."""
        # Mock load_cases to raise an exception
        with patch.object(data_loader, 'load_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_categories()

    def test_error_handling_in_get_age_groups(self, data_loader):
        """Test error handling in get_age_groups method."""
        # Mock load_cases to raise an exception
        with patch.object(data_loader, 'load_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_age_groups()

    def test_error_handling_in_get_complexity_levels(self, data_loader):
        """Test error handling in get_complexity_levels method."""
        # Mock load_cases to raise an exception
        with patch.object(data_loader, 'load_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_complexity_levels()

    def test_error_handling_in_get_data_summary(self, data_loader):
        """Test error handling in get_data_summary method."""
        # Mock load_cases to raise an exception
        with patch.object(data_loader, 'load_cases', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                data_loader.get_data_summary()