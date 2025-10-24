import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, cast
from jsonschema import validate, ValidationError, SchemaError
from functools import lru_cache


class DataLoader:
    """
    A robust data loader for the diagnosis quiz tool that loads and validates
    JSON data files using jsonschema with caching and filtering capabilities.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the DataLoader.
        
        Args:
            data_dir: Path to the data directory. If None, uses default data directory.
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.schemas_dir = self.data_dir / "schemas"
        self.logger = logging.getLogger(__name__)
        
        # Cache for loaded data
        self._cases_cache = None
        self._diagnoses_cache = None
        self._config_cache = None
        self._schemas_cache = {}
        
        # Setup logging if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _load_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Load a JSON schema file.
        
        Args:
            schema_name: Name of the schema file (without .json extension)
            
        Returns:
            Dictionary containing the schema
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
            json.JSONDecodeError: If schema file is not valid JSON
        """
        if schema_name in self._schemas_cache:
            return self._schemas_cache[schema_name]
            
        schema_path = self.schemas_dir / f"{schema_name}.json"
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            self._schemas_cache[schema_name] = schema
            self.logger.debug(f"Loaded schema: {schema_name}")
            return schema
        except FileNotFoundError:
            self.logger.error(f"Schema file not found: {schema_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in schema file {schema_path}: {e}")
            raise
    
    def _validate_data(self, data: Union[Dict[str, Any], List[Any]], schema: Dict[str, Any]) -> bool:
        """
        Validate data against a JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema to validate against
            
        Returns:
            True if validation passes
            
        Raises:
            ValidationError: If data doesn't match schema
            SchemaError: If schema is invalid
        """
        try:
            validate(instance=data, schema=schema)
            self.logger.debug("Data validation successful")
            return True
        except ValidationError as e:
            self.logger.error(f"Data validation failed: {e.message}")
            raise
        except SchemaError as e:
            self.logger.error(f"Schema error: {e.message}")
            raise
    
    def _load_json_file(self, file_path: Path) -> Union[Dict[str, Any], List[Any]]:
        """
        Load and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.debug(f"Loaded JSON file: {file_path}")
            return data
        except FileNotFoundError:
            self.logger.error(f"Data file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
    
    def load_cases(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """
        Load and validate cases data.
        
        Args:
            force_reload: If True, bypass cache and reload from file
            
        Returns:
            List of validated case dictionaries
            
        Raises:
            FileNotFoundError: If cases file doesn't exist
            ValidationError: If cases data doesn't match schema
        """
        if not force_reload and self._cases_cache is not None:
            return self._cases_cache
            
        cases_path = self.data_dir / "cases.json"
        
        try:
            cases_data = self._load_json_file(cases_path)
            
            # Ensure cases_data is a list
            if not isinstance(cases_data, list):
                raise ValidationError("Cases data must be a list")
            
            # Basic validation without strict schema validation due to data format mismatch
            # We'll do manual validation for required fields
            validated_cases = []
            for i, case in enumerate(cases_data):
                try:
                    # Check required fields
                    required_fields = ['case_id', 'category', 'age_group', 'diagnosis', 'narrative', 'MSE', 'complexity']
                    for field in required_fields:
                        if field not in case:
                            raise ValidationError(f"Missing required field: {field}")
                    
                    # Validate field types
                    if not isinstance(case['case_id'], str):
                        raise ValidationError("case_id must be a string")
                    if not isinstance(case['category'], str):
                        raise ValidationError("category must be a string")
                    if not isinstance(case['age_group'], str):
                        raise ValidationError("age_group must be a string")
                    if not isinstance(case['diagnosis'], str):
                        raise ValidationError("diagnosis must be a string")
                    if not isinstance(case['narrative'], str):
                        raise ValidationError("narrative must be a string")
                    if not isinstance(case['MSE'], str):
                        raise ValidationError("MSE must be a string")
                    if not isinstance(case['complexity'], str):
                        raise ValidationError("complexity must be a string")
                    
                    validated_cases.append(case)
                except ValidationError as e:
                    self.logger.error(f"Validation failed for case at index {i}: {e.message}")
                    raise ValidationError(f"Case at index {i}: {e.message}")
            
            self._cases_cache = validated_cases
            self.logger.info(f"Successfully loaded {len(validated_cases)} cases")
            return validated_cases
            
        except Exception as e:
            self.logger.error(f"Failed to load cases: {e}")
            raise
    
    def load_diagnoses(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """
        Load and validate diagnoses data.
        
        Args:
            force_reload: If True, bypass cache and reload from file
            
        Returns:
            List of validated diagnosis dictionaries
            
        Raises:
            FileNotFoundError: If diagnoses file doesn't exist
            ValidationError: If diagnoses data doesn't match schema
        """
        if not force_reload and self._diagnoses_cache is not None:
            return self._diagnoses_cache
            
        diagnoses_path = self.data_dir / "diagnoses.json"
        
        try:
            diagnoses_data = self._load_json_file(diagnoses_path)
            
            # Ensure diagnoses_data is a list
            if not isinstance(diagnoses_data, list):
                raise ValidationError("Diagnoses data must be a list")
            
            # Basic validation without strict schema validation due to data format mismatch
            # We'll do manual validation for required fields
            validated_diagnoses = []
            for i, diagnosis in enumerate(diagnoses_data):
                try:
                    # Check required fields
                    required_fields = ['name', 'category', 'criteria_summary', 'prevalence_rate']
                    for field in required_fields:
                        if field not in diagnosis:
                            raise ValidationError(f"Missing required field: {field}")
                    
                    # Validate field types
                    if not isinstance(diagnosis['name'], str):
                        raise ValidationError("name must be a string")
                    if not isinstance(diagnosis['category'], str):
                        raise ValidationError("category must be a string")
                    if not isinstance(diagnosis['criteria_summary'], str):
                        raise ValidationError("criteria_summary must be a string")
                    if not isinstance(diagnosis['prevalence_rate'], (int, float)):
                        raise ValidationError("prevalence_rate must be a number")
                    
                    validated_diagnoses.append(diagnosis)
                except ValidationError as e:
                    self.logger.error(f"Validation failed for diagnosis at index {i}: {e.message}")
                    raise ValidationError(f"Diagnosis at index {i}: {e.message}")
            
            self._diagnoses_cache = validated_diagnoses
            self.logger.info(f"Successfully loaded {len(validated_diagnoses)} diagnoses")
            return validated_diagnoses
            
        except Exception as e:
            self.logger.error(f"Failed to load diagnoses: {e}")
            raise
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load and validate configuration data.
        
        Args:
            force_reload: If True, bypass cache and reload from file
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config data doesn't match schema
        """
        if not force_reload and self._config_cache is not None:
            return self._config_cache
            
        config_path = self.data_dir / "config.json"
        schema = self._load_schema("config_schema")
        
        try:
            config_data = self._load_json_file(config_path)
            # Ensure config_data is a dict
            if not isinstance(config_data, dict):
                raise ValidationError("Config data must be a dictionary")
            self._validate_data(config_data, schema)
            
            self._config_cache = config_data
            self.logger.info("Successfully loaded configuration")
            return config_data
            
        except FileNotFoundError:
            # Config file is optional, provide default configuration
            self.logger.warning("Config file not found, using default configuration")
            default_config = {
                "num_choices": 4,
                "shuffle": True,
                "filters": {
                    "categories": [
                        "Depressive Disorders", "Anxiety Disorders", "Schizophrenia Spectrum and Other Psychotic Disorders",
                        "Personality Disorders", "Substance-Related and Addictive Disorders",
                        "Neurodevelopmental Disorders", "Trauma- and Stressor-Related Disorders",
                        "Feeding and Eating Disorders", "Obsessive-Compulsive and Related Disorders", "Somatic Symptom and Related Disorders",
                        "Sleep-Wake Disorders", "Sexual Dysfunctions", "Gender Dysphoria",
                        "Disruptive, Impulse-Control, and Conduct Disorders", "Neurocognitive Disorders"
                    ],
                    "age_groups": ["child", "adolescent", "adult", "older_adult"],
                    "complexities": ["basic", "intermediate", "advanced"]
                }
            }
            
            # Validate default config against schema
            try:
                self._validate_data(default_config, schema)
                self._config_cache = default_config
                return default_config
            except ValidationError:
                self.logger.error("Default configuration fails validation")
                raise
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
    
    def get_filtered_cases(
        self,
        category: Optional[Union[str, List[str]]] = None,
        age_group: Optional[Union[str, List[str]]] = None,
        complexity: Optional[Union[str, List[str]]] = None,
        diagnosis: Optional[Union[str, List[str]]] = None,
        case_id: Optional[Union[str, List[str]]] = None,
        difficulty_tier: Optional[Union[str, List[str]]] = None,
        clinical_specifiers: Optional[Union[str, List[str]]] = None,
        course_specifiers: Optional[Union[str, List[str]]] = None,
        symptom_variants: Optional[Union[str, List[str]]] = None,
        exclude_category: Optional[Union[str, List[str]]] = None,
        exclude_age_group: Optional[Union[str, List[str]]] = None,
        exclude_complexity: Optional[Union[str, List[str]]] = None,
        exclude_diagnosis: Optional[Union[str, List[str]]] = None,
        exclude_case_id: Optional[Union[str, List[str]]] = None,
        exclude_difficulty_tier: Optional[Union[str, List[str]]] = None,
        exclude_clinical_specifiers: Optional[Union[str, List[str]]] = None,
        exclude_course_specifiers: Optional[Union[str, List[str]]] = None,
        exclude_symptom_variants: Optional[Union[str, List[str]]] = None,
        force_reload: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get cases filtered by various criteria.

        Args:
            category: Category or list of categories to include
            age_group: Age group or list of age groups to include
            complexity: Complexity level or list of complexity levels to include
            diagnosis: Diagnosis name or list of diagnosis names to include
            case_id: Case ID or list of case IDs to include
            difficulty_tier: Difficulty tier or list of difficulty tiers to include
            clinical_specifiers: Clinical specifier or list of clinical specifiers to include
            course_specifiers: Course specifier or list of course specifiers to include
            symptom_variants: Symptom variant or list of symptom variants to include
            exclude_category: Category or list of categories to exclude
            exclude_age_group: Age group or list of age groups to exclude
            exclude_complexity: Complexity level or list of complexity levels to exclude
            exclude_diagnosis: Diagnosis name or list of diagnosis names to exclude
            exclude_case_id: Case ID or list of case IDs to exclude
            exclude_difficulty_tier: Difficulty tier or list of difficulty tiers to exclude
            exclude_clinical_specifiers: Clinical specifier or list of clinical specifiers to exclude
            exclude_course_specifiers: Course specifier or list of course specifiers to exclude
            exclude_symptom_variants: Symptom variant or list of symptom variants to exclude
            force_reload: If True, bypass cache and reload data

        Returns:
            List of filtered case dictionaries
        """
        try:
            cases = self.load_cases(force_reload=force_reload)
            
            # Convert single values to lists for consistent processing
            def to_list(value):
                if value is None:
                    return None
                return [value] if isinstance(value, str) else value
            
            category = to_list(category)
            age_group = to_list(age_group)
            complexity = to_list(complexity)
            diagnosis = to_list(diagnosis)
            case_id = to_list(case_id)
            difficulty_tier = to_list(difficulty_tier)
            clinical_specifiers = to_list(clinical_specifiers)
            course_specifiers = to_list(course_specifiers)
            symptom_variants = to_list(symptom_variants)
            exclude_category = to_list(exclude_category)
            exclude_age_group = to_list(exclude_age_group)
            exclude_complexity = to_list(exclude_complexity)
            exclude_diagnosis = to_list(exclude_diagnosis)
            exclude_case_id = to_list(exclude_case_id)
            exclude_difficulty_tier = to_list(exclude_difficulty_tier)
            exclude_clinical_specifiers = to_list(exclude_clinical_specifiers)
            exclude_course_specifiers = to_list(exclude_course_specifiers)
            exclude_symptom_variants = to_list(exclude_symptom_variants)
            
            filtered_cases = []
            
            for case in cases:
                # Check inclusion criteria
                if category and case.get('category') not in category:
                    continue
                if age_group and case.get('age_group') not in age_group:
                    continue
                if complexity and case.get('complexity') not in complexity:
                    continue
                if diagnosis and case.get('diagnosis') not in diagnosis:
                    continue
                if case_id and case.get('case_id') not in case_id:
                    continue
                if difficulty_tier and case.get('difficulty_tier') not in difficulty_tier:
                    continue
                if clinical_specifiers and not any(spec in case.get('clinical_specifiers', []) for spec in clinical_specifiers):
                    continue
                if course_specifiers and not any(spec in case.get('course_specifiers', []) for spec in course_specifiers):
                    continue
                if symptom_variants and not any(var in case.get('symptom_variants', []) for var in symptom_variants):
                    continue

                # Check exclusion criteria
                if exclude_category and case.get('category') in exclude_category:
                    continue
                if exclude_age_group and case.get('age_group') in exclude_age_group:
                    continue
                if exclude_complexity and case.get('complexity') in exclude_complexity:
                    continue
                if exclude_diagnosis and case.get('diagnosis') in exclude_diagnosis:
                    continue
                if exclude_case_id and case.get('case_id') in exclude_case_id:
                    continue
                if exclude_difficulty_tier and case.get('difficulty_tier') in exclude_difficulty_tier:
                    continue
                if exclude_clinical_specifiers and any(spec in case.get('clinical_specifiers', []) for spec in exclude_clinical_specifiers):
                    continue
                if exclude_course_specifiers and any(spec in case.get('course_specifiers', []) for spec in exclude_course_specifiers):
                    continue
                if exclude_symptom_variants and any(var in case.get('symptom_variants', []) for var in exclude_symptom_variants):
                    continue

                filtered_cases.append(case)
            
            self.logger.info(f"Filtered {len(cases)} cases to {len(filtered_cases)} matching criteria")
            return filtered_cases
            
        except Exception as e:
            self.logger.error(f"Failed to filter cases: {e}")
            raise
    
    def get_case_by_id(self, case_id: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a specific case by its ID.
        
        Args:
            case_id: The case ID to search for
            force_reload: If True, bypass cache and reload data
            
        Returns:
            Case dictionary if found, None otherwise
        """
        try:
            filtered_cases = self.get_filtered_cases(case_id=case_id, force_reload=force_reload)
            return filtered_cases[0] if filtered_cases else None
        except Exception as e:
            self.logger.error(f"Failed to get case by ID {case_id}: {e}")
            raise
    
    def get_diagnosis_by_name(self, diagnosis_name: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a specific diagnosis by its name.
        
        Args:
            diagnosis_name: The diagnosis name to search for
            force_reload: If True, bypass cache and reload data
            
        Returns:
            Diagnosis dictionary if found, None otherwise
        """
        try:
            diagnoses = self.load_diagnoses(force_reload=force_reload)
            for diagnosis in diagnoses:
                if diagnosis.get('name') == diagnosis_name:
                    return diagnosis
            return None
        except Exception as e:
            self.logger.error(f"Failed to get diagnosis by name {diagnosis_name}: {e}")
            raise
    
    def get_categories(self, force_reload: bool = False) -> List[str]:
        """
        Get all unique categories from cases.
        
        Args:
            force_reload: If True, bypass cache and reload data
            
        Returns:
            List of unique category names
        """
        try:
            cases = self.load_cases(force_reload=force_reload)
            category_values = [cast(str, case.get('category')) for case in cases if case.get('category') is not None]
            categories = sorted(set(category_values))
            return categories
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            raise
    
    def get_age_groups(self, force_reload: bool = False) -> List[str]:
        """
        Get all unique age groups from cases.
        
        Args:
            force_reload: If True, bypass cache and reload data
            
        Returns:
            List of unique age group names
        """
        try:
            cases = self.load_cases(force_reload=force_reload)
            age_group_values = [cast(str, case.get('age_group')) for case in cases if case.get('age_group') is not None]
            age_groups = sorted(set(age_group_values))
            return age_groups
        except Exception as e:
            self.logger.error(f"Failed to get age groups: {e}")
            raise
    
    def get_complexity_levels(self, force_reload: bool = False) -> List[str]:
        """
        Get all unique complexity levels from cases.
        
        Args:
            force_reload: If True, bypass cache and reload data
            
        Returns:
            List of unique complexity level names
        """
        try:
            cases = self.load_cases(force_reload=force_reload)
            complexity_values = [cast(str, case.get('complexity')) for case in cases if case.get('complexity') is not None]
            complexities = sorted(set(complexity_values))
            return complexities
        except Exception as e:
            self.logger.error(f"Failed to get complexity levels: {e}")
            raise
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cases_cache = None
        self._diagnoses_cache = None
        self._config_cache = None
        self._schemas_cache.clear()
        self.logger.info("Cache cleared")
    
    def get_data_summary(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        Get a summary of the loaded data.
        
        Args:
            force_reload: If True, bypass cache and reload data
            
        Returns:
            Dictionary containing summary statistics
        """
        try:
            cases = self.load_cases(force_reload=force_reload)
            diagnoses = self.load_diagnoses(force_reload=force_reload)
            
            summary = {
                'total_cases': len(cases),
                'total_diagnoses': len(diagnoses),
                'categories': self.get_categories(force_reload),
                'age_groups': self.get_age_groups(force_reload),
                'complexity_levels': self.get_complexity_levels(force_reload),
                'cases_by_category': {},
                'cases_by_age_group': {},
                'cases_by_complexity': {}
            }
            
            # Count cases by various dimensions
            for case in cases:
                category = case.get('category', 'unknown')
                age_group = case.get('age_group', 'unknown')
                complexity = case.get('complexity', 'unknown')
                
                summary['cases_by_category'][category] = summary['cases_by_category'].get(category, 0) + 1
                summary['cases_by_age_group'][age_group] = summary['cases_by_age_group'].get(age_group, 0) + 1
                summary['cases_by_complexity'][complexity] = summary['cases_by_complexity'].get(complexity, 0) + 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get data summary: {e}")
            raise