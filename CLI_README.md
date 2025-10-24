# Diagnosis Quiz Tool CLI

A professional command-line interface for generating and taking diagnosis quizzes.

## Installation

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Generate a Quiz

Generate a quiz based on a configuration file:

```bash
python3 src/ui/cli.py generate --config example_config.json --output quiz.txt --format text --seed 42
```

Options:
- `--config, -c`: Path to configuration JSON file (required)
- `--output, -o`: Output file path (required)  
- `--format, -f`: Output format - text, json, or csv (default: text)
- `--seed, -s`: Random seed for reproducible quizzes (optional)

### Take an Interactive Quiz

Take an interactive quiz session:

```bash
python3 src/ui/cli.py take --questions 5 --interactive --seed 123
```

Options:
- `--config, -c`: Path to configuration JSON file (optional)
- `--questions, -q`: Number of questions (default: 10)
- `--interactive, -i`: Run in interactive mode (default: True)
- `--seed, -s`: Random seed for reproducible quizzes (optional)

### Validate Data Files

Validate the data files in a directory:

```bash
python3 src/ui/cli.py validate --data-path data
```

Options:
- `--data-path, -d`: Path to data directory to validate (required)

## Configuration File Format

The configuration file should be in JSON format:

```json
{
  "num_questions": 10,
  "num_choices": 4,
  "shuffle": true,
  "categories": [
    "Depressive Disorders",
    "Anxiety Disorders"
  ],
  "age_groups": ["adult", "adolescent"],
  "complexities": ["moderate", "high"]
}
```

## Features

- **Professional UI**: Colored output with progress indicators
- **Interactive Mode**: Answer questions with immediate feedback
- **Multiple Formats**: Export quizzes as text, JSON, or CSV
- **Data Validation**: Comprehensive validation of data files
- **Reproducible**: Use seeds for consistent quiz generation
- **Error Handling**: User-friendly error messages and validation

## Examples

1. Generate a 5-question quiz:
```bash
python3 src/ui/cli.py generate --config example_config.json --output quick_quiz.txt --questions 5
```

2. Take a quick interactive quiz:
```bash
python3 src/ui/cli.py take --questions 3
```

3. Validate your data:
```bash
python3 src/ui/cli.py validate --data-path data
```