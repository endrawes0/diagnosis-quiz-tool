# Test Suite for Diagnosis Quiz Tool

This directory contains comprehensive unit tests for the diagnosis quiz tool.

## Test Files

### 1. `test_data_loader.py`
Tests for the `DataLoader` class including:
- **Loading functionality**: Loading cases, diagnoses, and configuration
- **Validation**: JSON schema validation and data integrity checks
- **Filtering**: Various filtering options (category, age group, complexity, etc.)
- **Caching**: Cache behavior and force reload functionality
- **Error handling**: Invalid data, missing files, malformed JSON
- **Utility methods**: Getting categories, age groups, complexity levels, data summary

**Coverage**: 50+ test methods covering all public and private methods

### 2. `test_quiz_generator.py`
Tests for the `QuizGenerator` class including:
- **Quiz generation**: Creating quizzes with various configurations
- **Question creation**: Individual question formatting and structure
- **Distractor generation**: Creating plausible incorrect answers
- **Formatting**: Text, JSON, and CSV output formats
- **Answer key generation**: Creating answer keys for quizzes
- **Shuffling**: Question and option randomization
- **Reproducibility**: Seed-based quiz generation
- **Error handling**: Invalid configurations, edge cases

**Coverage**: 40+ test methods covering all functionality

### 3. `test_scoring.py`
Tests for the `Scoring` class including:
- **Scoring modes**: Strict, lenient, and partial credit evaluation
- **Session management**: Starting sessions, recording answers, timing
- **Score calculation**: Comprehensive performance statistics
- **Performance analysis**: Category, complexity, and age group performance
- **Export functionality**: JSON, CSV, text, and HTML export formats
- **Feedback generation**: Detailed feedback and recommendations
- **Time analysis**: Time efficiency and pattern analysis
- **Error handling**: Invalid sessions, malformed data

**Coverage**: 60+ test methods covering all scoring functionality

### 4. `test_integration.py`
Integration tests for the complete workflow:
- **Full workflow**: End-to-end testing from data loading to scoring
- **Component interaction**: Testing how modules work together
- **Data consistency**: Ensuring data integrity across components
- **Performance testing**: Large datasets and memory efficiency
- **Edge cases**: Error conditions and boundary testing
- **Real-world scenarios**: Practical usage patterns

**Coverage**: 20+ integration test scenarios

## Test Fixtures (`conftest.py`)

The test suite uses comprehensive fixtures:

### Data Fixtures
- `temp_data_dir`: Creates temporary directory with sample data
- `sample_cases`: Sample case data for testing
- `sample_diagnoses`: Sample diagnosis data for testing
- `sample_quiz_config`: Sample quiz configuration
- `sample_quiz_data`: Sample generated quiz data

### Component Fixtures
- `data_loader`: DataLoader instance with test data
- `quiz_generator`: QuizGenerator instance with test data loader
- `scoring_strict`: Scoring instance in strict mode
- `scoring_lenient`: Scoring instance in lenient mode
- `scoring_partial`: Scoring instance in partial credit mode

### Error Fixtures
- `invalid_cases_data`: Invalid case data for error testing
- `invalid_diagnoses_data`: Invalid diagnosis data for error testing

## Running Tests

### With pytest (recommended)
```bash
pip install pytest
python -m pytest tests/ -v
```

### Without pytest (simple test runner)
```bash
python3 simple_test.py
```

### Test Categories
- **Unit tests**: Individual component testing
- **Integration tests**: Full workflow testing
- **Error handling tests**: Exception and edge case testing
- **Performance tests**: Memory and efficiency testing

## Test Coverage

The test suite provides comprehensive coverage:

### DataLoader
- ✅ All public methods
- ✅ All private methods
- ✅ Error conditions
- ✅ Edge cases
- ✅ Caching behavior

### QuizGenerator
- ✅ All public methods
- ✅ All private methods
- ✅ All output formats
- ✅ Configuration options
- ✅ Error handling

### Scoring
- ✅ All scoring modes
- ✅ All export formats
- ✅ Performance analysis
- ✅ Session management
- ✅ Error handling

### Integration
- ✅ End-to-end workflows
- ✅ Component interaction
- ✅ Data consistency
- ✅ Performance scenarios

## Test Data

The test suite uses realistic but minimal test data:
- 3 sample cases covering different categories
- 5 sample diagnoses across categories
- Complete schema definitions
- Various configuration options

## Error Testing

Comprehensive error testing includes:
- Missing files and directories
- Invalid JSON structure
- Schema validation failures
- Invalid configuration parameters
- Edge cases and boundary conditions
- Memory and performance limits

## Performance Testing

The test suite includes performance testing for:
- Large dataset handling
- Memory efficiency
- Caching effectiveness
- Concurrent session handling
- Export performance with large results

## Best Practices

The test suite follows testing best practices:
- **AAA pattern**: Arrange, Act, Assert
- **Descriptive test names**: Clear indication of what's being tested
- **Isolation**: Tests don't depend on each other
- **Comprehensive coverage**: Testing success and failure cases
- **Mocking**: Using mocks for external dependencies
- **Fixtures**: Reusable test setup and data

## Continuous Integration

These tests are designed to run in CI/CD environments:
- No external dependencies required
- Fast execution time
- Clear pass/fail indicators
- Comprehensive coverage reporting
- Cross-platform compatibility

## Future Enhancements

Potential test improvements:
- Property-based testing with Hypothesis
- Performance benchmarking
- Load testing for concurrent users
- Browser-based UI testing
- API endpoint testing
- Database integration testing