# Diagnosis Quiz Tool

A professional tool for creating and managing psychological disorder diagnosis quizzes, designed to help psychology and mental health students practice their diagnostic skills through interactive DSM-5 based case learning.

## 🎓 **For Students: Easy Setup!**

**Non-programmer?** No problem! See **[EASY_INSTALL.md](EASY_INSTALL.md)** for step-by-step instructions with no coding experience needed.

**Quick Start**: Just run `./START_APP.sh` (Mac/Linux) or `START_APP.bat` (Windows) after setup!

## 🎯 Project Overview

The Diagnosis Quiz Tool is a comprehensive Python application that generates realistic psychiatric clinical case quizzes from structured data. It supports DSM-5 psychiatric diagnostic categories, provides multiple difficulty levels, and offers both interactive and non-interactive quiz modes. The tool uses JSON Schema validation to ensure data integrity and provides detailed performance analytics.

## 🤖 AI-Assisted Development

This project was developed with **significant assistance from multiple AI coding assistants**, with **[OpenCode](https://github.com/OpenCodeDev/OpenCode) as the primary development assistant**. [ChatGPT](https://chat.openai.com) contributed to conceptualization and content, while [Claude](https://claude.ai) handled productionization and deployment. The project demonstrates modern AI-assisted software development practices through iterative human-AI collaboration.

See [ATTRIBUTION.md](ATTRIBUTION.md) for detailed credits and development methodology.

**Human Creator**: Andrew Haddad - Project vision, requirements, validation, and final decisions
**Primary AI Assistant**: [OpenCode](https://github.com/OpenCodeDev/OpenCode) - Core architecture, implementation, and development
**License**: MIT (see [LICENSE](LICENSE))

### Key Features

- **🏥 Realistic Clinical Cases**: Based on actual clinical presentations and mental status examinations
- **🎚️ Multiple Difficulty Levels**: Basic, intermediate, and advanced complexity levels
- **📊 Comprehensive Analytics**: Detailed performance tracking and feedback
- **🎨 Professional UI**: Colored terminal output with progress indicators
- **📝 Multiple Output Formats**: Text, JSON, and CSV export options
- **🔧 Flexible Configuration**: Extensive customization options for quiz generation
- **✅ Data Validation**: JSON Schema validation for all data files
- **🎲 Reproducible Results**: Seed-based randomization for consistent testing

## 📋 Features List

### Core Functionality
- **Quiz Generation**: Create quizzes from clinical case data
- **Interactive Sessions**: Take quizzes with immediate feedback
- **Data Validation**: Comprehensive validation of case and diagnosis data
- **Performance Analytics**: Detailed scoring and performance analysis
- **Multiple Export Formats**: Text, JSON, CSV, and HTML output

### Quiz Customization
- **Category Filtering**: Select specific diagnostic categories
- **Age Group Targeting**: Choose from child, adolescent, adult, older adult
- **Complexity Levels**: Basic, intermediate, and advanced difficulty
- **Question Count**: Configurable number of questions
- **Answer Options**: Customizable number of multiple-choice options
- **Randomization**: Optional shuffling of questions and answers

### Scoring Modes
- **Strict Scoring**: Exact match required for correct answers
- **Lenient Scoring**: Partial credit for close answers
- **Partial Credit**: Graded scoring based on answer accuracy

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd diagnosis_quiz_tool

# Install required packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r test_requirements.txt
```

### Development Setup

```bash
# Install in development mode
pip install -e .

# Run tests to verify installation
python -m pytest tests/ -v
```

## 💻 Usage Examples

### Basic Commands

#### Generate a Quiz
```bash
# Generate a quiz using configuration file
python3 src/ui/cli.py generate --config example_config.json --output quiz.txt --format text --seed 42

# Generate a JSON format quiz
python3 src/ui/cli.py generate --config example_config.json --output quiz.json --format json

# Generate a CSV quiz for analysis
python3 src/ui/cli.py generate --config example_config.json --output quiz.csv --format csv
```

#### Take an Interactive Quiz
```bash
# Take a 10-question interactive quiz
python3 src/ui/cli.py take --questions 10 --interactive

# Take a quiz with specific configuration
python3 src/ui/cli.py take --config example_config.json --questions 5 --seed 123

# Non-interactive mode (just display questions)
python3 src/ui/cli.py take --questions 3 --interactive=false
```

#### Validate Data Files
```bash
# Validate default data directory
python3 src/ui/cli.py validate --data-path data

# Validate custom data directory
python3 src/ui/cli.py validate --data-path /path/to/your/data
```

### Advanced Usage Examples

#### Custom Quiz Generation
```bash
# Generate a quiz with specific settings
python3 src/ui/cli.py generate \
  --config custom_config.json \
  --output specialized_quiz.txt \
  --format text \
  --seed 2024
```

#### Batch Quiz Generation
```bash
# Generate multiple quizzes with different seeds
for seed in 1001 1002 1003; do
  python3 src/ui/cli.py generate \
    --config example_config.json \
    --output "quiz_${seed}.txt" \
    --format text \
    --seed $seed
done
```

## ⚙️ Configuration Options

### Configuration File Structure

Create a JSON configuration file to customize quiz generation:

```json
{
  "num_questions": 10,
  "num_choices": 4,
  "shuffle": true,
  "filters": {
    "categories": [
      "Depressive Disorders",
      "Anxiety Disorders",
      "Schizophrenia Spectrum and Other Psychotic Disorders"
    ],
    "age_groups": ["adult", "adolescent"],
    "complexities": ["basic", "intermediate"],
    "specifics": [
      "Major Depressive Disorder",
      "Generalized Anxiety Disorder"
    ],
    "exclude_specifics": ["Schizophrenia"],
    "prevalence_weighting": true,
    "max_cases": 15
  },
  "quiz_settings": {
    "time_limit": 120,
    "show_feedback": true,
    "show_explanations": true,
    "allow_review": true,
    "passing_score": 70
  },
  "display_settings": {
    "theme": "light",
    "font_size": "medium",
    "show_progress": true,
    "show_timer": true
  }
}
```

### Configuration Parameters

#### Basic Settings
- `num_questions`: Number of questions to generate (2-50)
- `num_choices`: Number of answer choices per question (2-10)
- `shuffle`: Whether to randomize question and answer order

#### Filter Settings
- `categories`: Diagnostic categories to include
- `age_groups`: Age groups to target
- `complexities`: Difficulty levels to include
- `specifics`: Specific diagnoses or case IDs to include
- `exclude_specifics`: Diagnoses or cases to exclude
- `prevalence_weighting`: Weight selection by prevalence rates
- `max_cases`: Maximum number of cases to consider

#### Quiz Settings
- `time_limit`: Time limit per question in seconds
- `show_feedback`: Show immediate feedback after answers
- `show_explanations`: Display detailed explanations
- `allow_review`: Allow reviewing answers before submission
- `passing_score`: Minimum percentage to pass

#### Display Settings
- `theme`: UI theme (light, dark, auto)
- `font_size`: Text size (small, medium, large)
- `show_progress`: Display progress bar
- `show_timer`: Show countdown timer

## 📊 Data Format Documentation

### Case Data Structure

Each clinical case follows this JSON structure:

```json
{
  "case_id": "case_001",
  "category": "mood_disorders",
  "age_group": "adult",
  "diagnosis": "Major Depressive Disorder",
  "narrative": "Sarah is a 28-year-old female who presents with 8 weeks of persistent sadness, anhedonia, and significant functional impairment...",
  "MSE": {
    "appearance": "Appears tired, disheveled clothing",
    "behavior": "Psychomotor retardation, minimal eye contact",
    "speech": "Slow, low volume, monotonous",
    "mood": "Reports feeling 'sad and empty'",
    "affect": "Dysphoric, constricted range",
    "thought_process": "Linear but slow",
    "thought_content": "Hopelessness, passive suicidal ideation",
    "cognition": "Oriented x3, concentration impaired",
    "insight": "Limited insight",
    "judgment": "Poor judgment regarding self-care"
  },
  "complexity": "basic",
  "prevalence_weight": 0.07,
  "symptom_variants": [
    "Atypical features with increased appetite",
    "Melancholic features with early morning awakening"
  ]
}
```

### Diagnosis Data Structure

```json
{
  "name": "Major Depressive Disorder",
  "category": "Depressive Disorders",
  "criteria_summary": "Five or more depressive symptoms present during the same 2-week period...",
  "prevalence_rate": 7.1,
  "icd_code": "F32.9",
  "dsm_code": "296.20",
  "differential_diagnoses": [
    "Persistent Depressive Disorder",
    "Adjustment Disorder with Depressed Mood",
    "Bipolar Disorder"
  ],
  "key_features": [
    "Depressed mood most of the day",
    "Markedly diminished interest or pleasure",
    "Significant weight loss or gain"
  ],
  "age_specific_notes": {
    "child": "Irritability may be more prominent than sadness",
    "adolescent": "Often presents with academic decline",
    "adult": "Typically presents with work-related difficulties",
    "older_adult": "May present with somatic complaints"
  }
}
```

### Supported Categories

- `Depressive Disorders`
- `Schizophrenia Spectrum and Other Psychotic Disorders`
- `Anxiety Disorders`
- `Personality Disorders`
- `Substance-Related and Addictive Disorders`
- `Neurodevelopmental Disorders`
- `Trauma- and Stressor-Related Disorders`
- `Feeding and Eating Disorders`
- `Obsessive-Compulsive and Related Disorders`
- `Somatic Symptom and Related Disorders`
- `Sleep-Wake Disorders`
- `Sexual Dysfunctions`
- `Gender Dysphoria`
- `Disruptive, Impulse-Control, and Conduct Disorders`
- `Neurocognitive Disorders`

### Age Groups

- `child` (0-12 years)
- `adolescent` (13-17 years)
- `adult` (18-64 years)
- `older_adult` (65+ years)

### Complexity Levels

- `basic`: Clear presentation, common diagnoses
- `intermediate`: Some complexity, multiple considerations
- `advanced`: Complex presentations, rare conditions

## 🧪 Development Setup and Testing

### Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd diagnosis_quiz_tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r test_requirements.txt
pip install -e .
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_data_loader.py -v

# Run with parallel execution
python -m pytest tests/ -n auto

# Quick smoke test (no dependencies)
python3 smoke_test.py
```

### Test Structure

The test suite includes:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Memory and efficiency testing
- **Error Handling Tests**: Exception and edge case testing

### Code Quality

```bash
# Run linting (if configured)
flake8 src/

# Run type checking (if configured)
mypy src/

# Run security checks (if configured)
bandit -r src/
```

## 🤝 Contributing Guidelines

### How to Contribute

1. **Fork the Repository**: Create a fork of the project
2. **Create a Branch**: Use descriptive branch names
3. **Make Changes**: Implement your feature or fix
4. **Add Tests**: Ensure comprehensive test coverage
5. **Run Tests**: Verify all tests pass
6. **Submit Pull Request**: Provide clear description of changes

### Code Standards

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Include docstrings for all functions
- **Type Hints**: Use type annotations where appropriate
- **Testing**: Maintain test coverage above 90%
- **Commits**: Use clear, descriptive commit messages

### Adding New Features

1. **Design**: Plan the feature and its interface
2. **Implement**: Write clean, well-documented code
3. **Test**: Add comprehensive tests
4. **Document**: Update README and documentation
5. **Review**: Ensure code quality standards

### Bug Reports

When reporting bugs, include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed reproduction steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, etc.

## 📄 License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ❗ Liability and warranty disclaimed

## 📝 Examples of Generated Quizzes

### Text Format Example

```
DIAGNOSIS QUIZ
==============

Question 1 of 10

A 35-year-old male presents with 6 weeks of persistent low mood, loss of interest in activities, and significant weight loss. He reports difficulty sleeping, feelings of worthlessness, and has trouble concentrating at work. He denies any substance use and has no significant medical history.

Mental Status Examination: Well-groomed, appears stated age. Cooperative with appropriate eye contact. Speech is normal rate and volume, coherent. Reports feeling "depressed and hopeless." Affect is constricted and congruent with mood. Thought process is logical and goal-directed. No suicidal ideation or hallucinations. Alert and oriented x4, memory intact. Fair insight into depressive symptoms. Appropriate judgment.

A. Major Depressive Disorder
B. Generalized Anxiety Disorder
C. Bipolar Disorder
D. Adjustment Disorder

Correct Answer: A. Major Depressive Disorder

Case ID: case_001
Category: mood_disorders
Complexity: basic
```

### JSON Format Example

```json
{
  "quiz_metadata": {
    "total_questions": 10,
    "num_choices": 4,
    "categories": ["Depressive Disorders", "Anxiety Disorders"],
    "age_groups": ["adult"],
    "complexities": ["basic", "intermediate"],
    "generated_at": "2024-01-15T10:30:00Z",
    "seed": 42
  },
  "questions": [
    {
      "question_number": 1,
      "question_text": "A 35-year-old male presents with 6 weeks of persistent low mood...",
      "options": [
        "Major Depressive Disorder",
        "Generalized Anxiety Disorder", 
        "Bipolar Disorder",
        "Adjustment Disorder"
      ],
      "correct_answer": "Major Depressive Disorder",
      "correct_index": 0,
      "case_id": "case_001",
      "case_metadata": {
        "category": "Depressive Disorders",
        "age_group": "adult",
        "complexity": "basic"
      }
    }
  ]
}
```

### CSV Format Example

```csv
question_number,question_text,option_a,option_b,option_c,option_d,correct_answer,correct_index,case_id,category,age_group,complexity
1,"A 35-year-old male presents...","Major Depressive Disorder","Generalized Anxiety Disorder","Bipolar Disorder","Adjustment Disorder","Major Depressive Disorder",0,case_001,Depressive Disorders,adult,basic
```

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure you're in the project directory
cd diagnosis_quiz_tool

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Data Validation Errors
```bash
# Validate your data files
python3 src/ui/cli.py validate --data-path data

# Check JSON syntax
python -m json.tool data/cases.json
```

#### Permission Errors
```bash
# Make CLI executable
chmod +x src/ui/cli.py

# Check file permissions
ls -la src/ui/cli.py
```

### Getting Help

- **Documentation**: Check this README and inline documentation
- **Issues**: Report bugs on the project issue tracker
- **Tests**: Run test suite for debugging
- **Logs**: Check error messages for specific issues

## 📚 Additional Resources

### Clinical References
- **DSM-5**: Diagnostic and Statistical Manual of Mental Disorders (5th Edition)
- **ICD-11**: International Classification of Diseases (Mental Health Section)
- **Clinical Guidelines**: Current psychiatric and psychological practice guidelines

### Technical Documentation
- **JSON Schema**: Data validation schemas in `data/schemas/`
- **API Documentation**: Inline code documentation
- **Test Examples**: Comprehensive test suite in `tests/`

---

**Diagnosis Quiz Tool** - Enhancing psychology and mental health education through interactive DSM-5 case-based learning.

## 📄 License & Attribution

- **License**: MIT License (see [LICENSE](LICENSE))
- **Copyright**: © 2025 Andrew Haddad
- **AI Attribution**: See [ATTRIBUTION.md](ATTRIBUTION.md) for detailed credits

This project was developed with significant AI assistance. Full transparency about the development process is provided in the attribution document.

## 📮 Contact

**Creator**: Andrew Haddad
**Email**: me@andrewwhaddad.com
**GitHub**: https://github.com/endrawes0/diagnosis-quiz-tool

For questions, issues, or contributions, please visit the project repository.