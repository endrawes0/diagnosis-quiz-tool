# DataLoader Class

The `DataLoader` class provides robust loading and validation of JSON data files for the diagnosis quiz tool.

## Features

- **JSON Schema Validation**: Validates data against schemas in `data/schemas/`
- **Caching**: Avoids reloading files multiple times
- **Flexible Filtering**: Filter cases by category, age group, complexity, diagnosis, and case ID
- **Error Handling**: Graceful handling of file not found and validation errors
- **Logging**: Comprehensive logging for debugging and monitoring

## Usage

```python
from src.modules.data_loader import DataLoader

# Initialize the loader
loader = DataLoader()

# Load data
cases = loader.load_cases()
diagnoses = loader.load_diagnoses()
config = loader.load_config()

# Filter cases
adult_cases = loader.get_filtered_cases(age_group="adult")
mood_cases = loader.get_filtered_cases(category="mood_disorders")
complex_cases = loader.get_filtered_cases(complexity="advanced")

# Get specific data
case = loader.get_case_by_id("case_001")
diagnosis = loader.get_diagnosis_by_name("Major Depressive Disorder")

# Get summary statistics
summary = loader.get_data_summary()
```

## Methods

### Core Loading Methods
- `load_cases(force_reload=False)`: Load and validate cases data
- `load_diagnoses(force_reload=False)`: Load and validate diagnoses data  
- `load_config(force_reload=False)`: Load and validate configuration data

### Filtering Methods
- `get_filtered_cases(**criteria)`: Filter cases by various criteria
- `get_case_by_id(case_id)`: Get a specific case by ID
- `get_diagnosis_by_name(name)`: Get a specific diagnosis by name

### Utility Methods
- `get_categories()`: Get all unique categories
- `get_age_groups()`: Get all unique age groups
- `get_complexity_levels()`: Get all unique complexity levels
- `get_data_summary()`: Get summary statistics
- `clear_cache()`: Clear all cached data

## Filtering Criteria

The `get_filtered_cases()` method accepts the following parameters:

**Inclusion criteria:**
- `category`: Single category or list of categories
- `age_group`: Single age group or list of age groups  
- `complexity`: Single complexity level or list of complexity levels
- `diagnosis`: Single diagnosis name or list of diagnosis names
- `case_id`: Single case ID or list of case IDs

**Exclusion criteria:**
- `exclude_category`: Categories to exclude
- `exclude_age_group`: Age groups to exclude
- `exclude_complexity`: Complexity levels to exclude
- `exclude_diagnosis`: Diagnoses to exclude
- `exclude_case_id`: Case IDs to exclude

## Error Handling

The DataLoader handles various error conditions gracefully:
- Missing files are logged and appropriate exceptions raised
- Validation errors provide detailed context about what failed
- Type errors are caught and reported with helpful messages
- The loader can work with missing config files by using defaults

## Caching

Data is cached after first load to improve performance:
- Use `force_reload=True` to bypass cache
- Use `clear_cache()` to manually clear all cached data
- Cache is automatically used for subsequent calls

## Logging

The DataLoader uses Python's logging module:
- Logs are written to console by default
- Different log levels for different types of events
- Detailed error messages for troubleshooting