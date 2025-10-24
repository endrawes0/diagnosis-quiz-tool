#!/usr/bin/env python3
"""
Command-line interface for the diagnosis quiz tool using Click.
Provides commands for generating, taking, and validating quizzes.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import random

import click
from click import echo, style, secho, confirm

# Add the project root to the path to import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.modules.data_loader import DataLoader
    from src.modules.quiz_generator import QuizGenerator
except ImportError:
    # Fallback for different execution contexts
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from modules.data_loader import DataLoader
    from modules.quiz_generator import QuizGenerator


class ColoredFormatter:
    """Helper class for consistent colored output."""
    
    @staticmethod
    def success(message: str) -> None:
        """Print success message in green."""
        secho(f"✓ {message}", fg='green', bold=True)
    
    @staticmethod
    def error(message: str) -> None:
        """Print error message in red."""
        secho(f"✗ {message}", fg='red', bold=True)
    
    @staticmethod
    def warning(message: str) -> None:
        """Print warning message in yellow."""
        secho(f"⚠ {message}", fg='yellow', bold=True)
    
    @staticmethod
    def info(message: str) -> None:
        """Print info message in blue."""
        secho(f"ℹ {message}", fg='blue', bold=True)
    
    @staticmethod
    def header(message: str) -> None:
        """Print header message in cyan."""
        secho(f"\n{message}", fg='cyan', bold=True)
    
    @staticmethod
    def question(message: str) -> None:
        """Print question in white."""
        secho(message, fg='white', bold=True)
    
    @staticmethod
    def option(text: str, is_correct: bool = False) -> None:
        """Print option with appropriate color."""
        if is_correct:
            secho(f"✓ {text}", fg='green', bold=True)
        else:
            echo(f"  {text}")


class ProgressBar:
    """Simple progress bar for quiz taking."""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, increment: int = 1) -> None:
        """Update progress bar."""
        self.current += increment
        self._display()
    
    def _display(self) -> None:
        """Display the progress bar."""
        filled = int(self.width * self.current / self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        percent = int(100 * self.current / self.total)
        echo(f"\r[{bar}] {percent}% ({self.current}/{self.total})", nl=False)


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        ColoredFormatter.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        ColoredFormatter.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


def save_quiz_to_file(quiz_data: Dict[str, Any], output_path: str, format_type: str) -> None:
    """Save quiz data to file in specified format."""
    try:
        generator = QuizGenerator(DataLoader())
        formatted_quiz = generator.format_quiz(quiz_data, format_type)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_quiz)
        
        ColoredFormatter.success(f"Quiz saved to {output_path}")
    except Exception as e:
        ColoredFormatter.error(f"Failed to save quiz: {e}")
        sys.exit(1)


def validate_data_path(data_path: str) -> bool:
    """Validate that the data path contains required files."""
    data_dir = Path(data_path)
    
    if not data_dir.exists():
        ColoredFormatter.error(f"Data directory does not exist: {data_path}")
        return False
    
    required_files = ['cases.json', 'diagnoses.json']
    missing_files = []
    
    for file_name in required_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        ColoredFormatter.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    return True


@click.group()
@click.version_option(version='1.0.0', prog_name='Diagnosis Quiz Tool')
def cli():
    """
    Diagnosis Quiz Tool - A command-line tool for generating and taking diagnosis quizzes.
    
    This tool helps medical students and professionals practice diagnosis skills through
    interactive quizzes based on clinical cases and mental status examinations.
    """
    pass


@cli.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to configuration JSON file')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output file path for the generated quiz')
@click.option('--format', '-f', 'format_type', 
              type=click.Choice(['text', 'json', 'csv'], case_sensitive=False),
              default='text', help='Output format (default: text)')
@click.option('--seed', '-s', type=int,
              help='Random seed for reproducible quiz generation')
def generate(config: str, output: str, format_type: str, seed: Optional[int]):
    """Generate a quiz based on configuration settings."""
    ColoredFormatter.header("🎯 Generating Quiz")
    
    try:
        # Load configuration
        ColoredFormatter.info(f"Loading configuration from {config}")
        quiz_config = load_config_file(config)
        
        # Add seed to config if provided
        if seed is not None:
            quiz_config['seed'] = seed
            ColoredFormatter.info(f"Using random seed: {seed}")
        
        # Initialize data loader and quiz generator
        data_loader = DataLoader()
        quiz_generator = QuizGenerator(data_loader)
        
        # Generate quiz
        ColoredFormatter.info("Generating quiz questions...")
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        # Save quiz to file
        save_quiz_to_file(quiz_data, output, format_type.lower())
        
        # Display summary
        metadata = quiz_data['quiz_metadata']
        ColoredFormatter.success(f"Generated quiz with {metadata['total_questions']} questions")
        ColoredFormatter.info(f"Choices per question: {metadata['num_choices']}")
        ColoredFormatter.info(f"Output format: {format_type.upper()}")
        
    except Exception as e:
        ColoredFormatter.error(f"Failed to generate quiz: {e}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to configuration JSON file')
@click.option('--questions', '-q', type=int, default=10,
              help='Number of questions to include (default: 10)')
@click.option('--interactive', '-i', is_flag=True, default=True,
              help='Run in interactive mode (default: True)')
@click.option('--seed', '-s', type=int,
              help='Random seed for reproducible quiz generation')
def take(config: Optional[str], questions: int, interactive: bool, seed: Optional[int]):
    """Take an interactive quiz session."""
    ColoredFormatter.header("📝 Starting Quiz Session")
    
    try:
        # Load configuration
        if config:
            ColoredFormatter.info(f"Loading configuration from {config}")
            quiz_config = load_config_file(config)
        else:
            # Use default configuration
            quiz_config = {
                'num_questions': questions,
                'num_choices': 4,
                'shuffle': True,
                'categories': None,
                'age_groups': None,
                'complexities': None
            }
        
        # Override questions count if specified
        if questions != 10:
            quiz_config['num_questions'] = questions
        
        # Add seed to config if provided
        if seed is not None:
            quiz_config['seed'] = seed
            ColoredFormatter.info(f"Using random seed: {seed}")
        
        # Initialize data loader and quiz generator
        data_loader = DataLoader()
        quiz_generator = QuizGenerator(data_loader)
        
        # Generate quiz
        ColoredFormatter.info("Generating quiz questions...")
        quiz_data = quiz_generator.generate_quiz(quiz_config)
        
        if not interactive:
            # Non-interactive mode - just show the quiz
            formatted_quiz = quiz_generator.format_quiz(quiz_data, 'text')
            echo(formatted_quiz)
            return
        
        # Interactive quiz session
        ColoredFormatter.success("Quiz generated! Starting interactive session...")
        echo()
        
        score = 0
        total_questions = len(quiz_data['questions'])
        progress_bar = ProgressBar(total_questions)
        
        for i, question in enumerate(quiz_data['questions']):
            # Display question header
            ColoredFormatter.header(f"Question {question['question_number']} of {total_questions}")
            progress_bar.update()
            echo()
            
            # Display question text
            ColoredFormatter.question(question['question_text'])
            echo()
            
            # Display options
            for j, option in enumerate(question['options']):
                letter = chr(65 + j)  # A, B, C, D, etc.
                echo(f"  {letter}. {option}")
            echo()
            
            # Get user answer
            while True:
                try:
                    answer = click.prompt(
                        "Your answer (enter letter)", 
                        type=click.Choice([chr(65 + i) for i in range(len(question['options']))]),
                        show_choices=False
                    )
                    break
                except click.Abort:
                    ColoredFormatter.warning("Quiz cancelled by user")
                    sys.exit(0)
            
            # Check answer
            answer_index = ord(answer) - 65
            is_correct = answer_index == question['correct_index']
            
            if is_correct:
                score += 1
                ColoredFormatter.success("Correct! ✓")
            else:
                correct_letter = chr(65 + question['correct_index'])
                ColoredFormatter.error(f"Incorrect. The correct answer is {correct_letter}: {question['correct_answer']}")
            
            # Show case metadata
            echo(f"  Case ID: {question['case_id']}")
            echo(f"  Category: {question['case_metadata']['category']}")
            echo(f"  Complexity: {question['case_metadata']['complexity']}")
            echo()
            
            # Ask if user wants to continue
            if i < total_questions - 1:
                if not confirm("Continue to next question?", default=True):
                    break
        
        # Show final results
        ColoredFormatter.header("🏆 Quiz Complete!")
        percentage = (score / total_questions) * 100
        echo()
        
        if percentage >= 80:
            ColoredFormatter.success(f"Excellent! You scored {score}/{total_questions} ({percentage:.1f}%)")
        elif percentage >= 60:
            ColoredFormatter.info(f"Good job! You scored {score}/{total_questions} ({percentage:.1f}%)")
        else:
            ColoredFormatter.warning(f"You scored {score}/{total_questions} ({percentage:.1f}%) - keep practicing!")
        
        # Show answer key
        echo()
        ColoredFormatter.header("📋 Answer Key")
        answer_key = quiz_generator.get_answer_key(quiz_data)
        echo(answer_key)
        
    except KeyboardInterrupt:
        ColoredFormatter.warning("\nQuiz interrupted by user")
        sys.exit(0)
    except Exception as e:
        ColoredFormatter.error(f"Failed to run quiz: {e}")
        sys.exit(1)


@cli.command()
@click.option('--data-path', '-d', type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=True, help='Path to data directory to validate')
def validate(data_path: str):
    """Validate data files in the specified directory."""
    ColoredFormatter.header("🔍 Validating Data Files")
    
    try:
        # Validate data path structure
        if not validate_data_path(data_path):
            sys.exit(1)
        
        ColoredFormatter.success("Data directory structure is valid")
        
        # Initialize data loader with custom path
        data_loader = DataLoader(data_path)
        
        # Validate cases
        ColoredFormatter.info("Validating cases.json...")
        try:
            cases = data_loader.load_cases()
            ColoredFormatter.success(f"Loaded {len(cases)} valid cases")
        except Exception as e:
            ColoredFormatter.error(f"Cases validation failed: {e}")
            sys.exit(1)
        
        # Validate diagnoses
        ColoredFormatter.info("Validating diagnoses.json...")
        try:
            diagnoses = data_loader.load_diagnoses()
            ColoredFormatter.success(f"Loaded {len(diagnoses)} valid diagnoses")
        except Exception as e:
            ColoredFormatter.error(f"Diagnoses validation failed: {e}")
            sys.exit(1)
        
        # Try to load config (optional)
        ColoredFormatter.info("Checking config.json (optional)...")
        try:
            config = data_loader.load_config()
            ColoredFormatter.success("Configuration file is valid")
        except Exception as e:
            ColoredFormatter.warning(f"Configuration file issue (not critical): {e}")
        
        # Show data summary
        ColoredFormatter.header("📊 Data Summary")
        summary = data_loader.get_data_summary()
        
        echo(f"Total cases: {summary['total_cases']}")
        echo(f"Total diagnoses: {summary['total_diagnoses']}")
        echo()
        
        echo("Categories:")
        for category in summary['categories']:
            count = summary['cases_by_category'].get(category, 0)
            echo(f"  • {category}: {count} cases")
        
        echo()
        echo("Age groups:")
        for age_group in summary['age_groups']:
            count = summary['cases_by_age_group'].get(age_group, 0)
            echo(f"  • {age_group}: {count} cases")
        
        echo()
        echo("Complexity levels:")
        for complexity in summary['complexity_levels']:
            count = summary['cases_by_complexity'].get(complexity, 0)
            echo(f"  • {complexity}: {count} cases")
        
        ColoredFormatter.success("Data validation completed successfully!")
        
    except Exception as e:
        ColoredFormatter.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()