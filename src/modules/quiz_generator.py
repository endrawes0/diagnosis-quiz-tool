import json
import csv
import random
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from io import StringIO
from datetime import datetime, timedelta


class QuizGenerator:
    """
    A flexible quiz generator that creates multiple choice quizzes from case data
    with adaptive selection and combination logic.
    """
    
    def __init__(self, data_loader, user_progress=None):
        """
        Initialize the QuizGenerator with a DataLoader instance and optional UserProgress.
        
        Args:
            data_loader: An instance of DataLoader to access case and diagnosis data
            user_progress: Optional UserProgress instance for adaptive features
        """
        self.data_loader = data_loader
        self.user_progress = user_progress
        self.logger = logging.getLogger(__name__)
        
        # Clinical similarity mapping for smart distractor selection
        self.clinical_similarity_map = {
            'Depressive Disorders': ['Major Depressive Disorder', 'Persistent Depressive Disorder', 'Disruptive Mood Dysregulation Disorder'],
            'Anxiety Disorders': ['Generalized Anxiety Disorder', 'Panic Disorder', 'Social Anxiety Disorder', 'Specific Phobia'],
            'Schizophrenia Spectrum and Other Psychotic Disorders': ['Schizophrenia', 'Schizoaffective Disorder', 'Brief Psychotic Disorder', 'Delusional Disorder'],
            'Personality Disorders': ['Borderline Personality Disorder', 'Narcissistic Personality Disorder', 'Antisocial Personality Disorder', 'Avoidant Personality Disorder'],
            'Substance-Related and Addictive Disorders': ['Alcohol Use Disorder', 'Opioid Use Disorder', 'Stimulant Use Disorder', 'Cannabis Use Disorder'],
            'Neurodevelopmental Disorders': ['Attention-Deficit/Hyperactivity Disorder', 'Autism Spectrum Disorder', 'Intellectual Disability', 'Specific Learning Disorder']
        }
        
        # Difficulty tier definitions
        self.difficulty_tiers = {
            'easy': {'xp_multiplier': 1.0, 'time_bonus_threshold': 120, 'accuracy_threshold': 60},
            'moderate': {'xp_multiplier': 1.5, 'time_bonus_threshold': 90, 'accuracy_threshold': 75},
            'high': {'xp_multiplier': 2.0, 'time_bonus_threshold': 60, 'accuracy_threshold': 85},
            # Keep backward compatibility
            'beginner': {'xp_multiplier': 1.0, 'time_bonus_threshold': 120, 'accuracy_threshold': 60},
            'intermediate': {'xp_multiplier': 1.5, 'time_bonus_threshold': 90, 'accuracy_threshold': 75},
            'advanced': {'xp_multiplier': 2.0, 'time_bonus_threshold': 60, 'accuracy_threshold': 85},
            'expert': {'xp_multiplier': 3.0, 'time_bonus_threshold': 45, 'accuracy_threshold': 90}
        }
        
        # Map between different difficulty naming systems
        self.difficulty_mapping = {
            'beginner': 'easy',
            'intermediate': 'moderate', 
            'advanced': 'high',
            'expert': 'high'
        }
        
        # Setup logging if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def generate_quiz(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quiz based on the provided configuration with adaptive features.
        
        Args:
            config: Dictionary containing quiz configuration options:
                - num_questions: Number of questions to generate (default: 10)
                - num_choices: Number of multiple choice options (default: 4)
                - categories: List of categories to include (optional)
                - age_groups: List of age groups to include (optional)
                - complexities: List of complexity levels to include (optional)
                - diagnoses: List of specific diagnoses to include (optional)
                - shuffle: Whether to randomize question order (default: True)
                - seed: Random seed for reproducible quizzes (optional)
                - exclude_categories: Categories to exclude (optional)
                - exclude_age_groups: Age groups to exclude (optional)
                - exclude_complexities: Complexity levels to exclude (optional)
                - exclude_diagnoses: Diagnoses to exclude (optional)
                - adaptive_mode: Enable adaptive difficulty selection (default: False)
                - differential_mode: Enable differential diagnosis questions (default: False)
                - multi_case_matching: Enable multi-case matching questions (default: False)
                - streak_sequencing: Enable streak-based question sequencing (default: False)
                - time_adjustment: Enable time-based difficulty adjustments (default: False)
                - bonus_xp_opportunities: Enable bonus XP opportunities (default: False)
        
        Returns:
            Dictionary containing structured quiz data with questions, options, and answers
        """
        try:
            # Set random seed if provided
            if 'seed' in config:
                random.seed(config['seed'])
            
            # Extract configuration parameters with defaults
            num_questions = config.get('num_questions', 10)
            num_choices = config.get('num_choices', 4)
            shuffle = config.get('shuffle', True)
            adaptive_mode = config.get('adaptive_mode', False)
            differential_mode = config.get('differential_mode', False)
            multi_case_matching = config.get('multi_case_matching', False)
            streak_sequencing = config.get('streak_sequencing', False)
            time_adjustment = config.get('time_adjustment', False)
            bonus_xp_opportunities = config.get('bonus_xp_opportunities', False)
            
            # Apply adaptive difficulty selection if enabled
            if adaptive_mode and self.user_progress:
                complexities = self._get_adaptive_complexities()
                config['complexities'] = complexities
                self.logger.info(f"Adaptive mode enabled, using complexities: {complexities}")
            
            # Apply difficulty tier filtering with unlock requirements
            if self.user_progress:
                unlocked_difficulties = self._get_unlocked_difficulties()
                if config.get('complexities'):
                    config['complexities'] = [c for c in config['complexities'] if c in unlocked_difficulties]
                else:
                    config['complexities'] = unlocked_difficulties
            
            # Get filtered cases based on configuration
            filtered_cases = self.data_loader.get_filtered_cases(
                category=config.get('categories'),
                age_group=config.get('age_groups'),
                complexity=config.get('complexities'),
                diagnosis=config.get('diagnoses'),
                difficulty_tier=config.get('difficulty_tiers'),
                clinical_specifiers=config.get('clinical_specifiers'),
                course_specifiers=config.get('course_specifiers'),
                symptom_variants=config.get('symptom_variants'),
                exclude_category=config.get('exclude_categories'),
                exclude_age_group=config.get('exclude_age_groups'),
                exclude_complexity=config.get('exclude_complexities'),
                exclude_diagnosis=config.get('exclude_diagnoses'),
                exclude_difficulty_tier=config.get('exclude_difficulty_tiers'),
                exclude_clinical_specifiers=config.get('exclude_clinical_specifiers'),
                exclude_course_specifiers=config.get('exclude_course_specifiers'),
                exclude_symptom_variants=config.get('exclude_symptom_variants')
            )
            
            if not filtered_cases:
                raise ValueError("No cases match the specified criteria")
            
            if len(filtered_cases) < num_questions:
                self.logger.warning(
                    f"Requested {num_questions} questions but only {len(filtered_cases)} cases available. "
                    f"Using all available cases."
                )
                num_questions = len(filtered_cases)
            
            # For multi-case matching, we need more cases since each question uses multiple cases
            if multi_case_matching:
                cases_needed = num_questions * 3  # 3 cases per question
                if len(filtered_cases) < cases_needed:
                    self.logger.warning(
                        f"Requested {num_questions} multi-case questions but only {len(filtered_cases)} cases available. "
                        f"Need {cases_needed} cases. Using {len(filtered_cases) // 3} questions instead."
                    )
                    num_questions = len(filtered_cases) // 3
                    cases_needed = num_questions * 3
            else:
                cases_needed = num_questions

            if len(filtered_cases) < cases_needed:
                self.logger.warning(
                    f"Requested {cases_needed} cases but only {len(filtered_cases)} cases available. "
                    f"Using all available cases."
                )
                cases_needed = len(filtered_cases)
                if multi_case_matching:
                    num_questions = cases_needed // 3

            # Apply adaptive case selection
            if adaptive_mode and self.user_progress:
                selected_cases = self._adaptive_case_selection(filtered_cases, cases_needed)
            elif streak_sequencing and self.user_progress:
                selected_cases = self._streak_based_sequencing(filtered_cases, cases_needed)
            else:
                selected_cases = random.sample(filtered_cases, cases_needed)

            # Load all diagnoses for distractor generation
            all_diagnoses = self.data_loader.load_diagnoses()
            diagnosis_by_category = {}
            for diagnosis in all_diagnoses:
                category = diagnosis.get('category', 'Unknown')
                if category not in diagnosis_by_category:
                    diagnosis_by_category[category] = []
                diagnosis_by_category[category].append(diagnosis['name'])

            # Generate questions
            questions = []
            if multi_case_matching:
                # Generate multi-case matching questions
                # Each question contains multiple cases to match to diagnoses
                cases_per_question = 3  # Fixed at 3 for now
                for i in range(0, len(selected_cases), cases_per_question):
                    case_group = selected_cases[i:i + cases_per_question]
                    if len(case_group) >= 3:  # Only create if we have enough cases
                        question = self._create_multi_case_matching_question(
                            case_group, i // cases_per_question + 1
                        )
                        questions.append(question)
            else:
                for i, case in enumerate(selected_cases):
                    if differential_mode:
                        question = self._create_differential_question(
                            case, diagnosis_by_category, num_choices, i + 1
                        )
                    else:
                        question = self._create_question(
                            case, diagnosis_by_category, num_choices, i + 1
                        )

                    # Add bonus XP opportunities if enabled
                    if bonus_xp_opportunities:
                        question = self._add_bonus_xp_opportunities(question, case)

                    # Add time-based difficulty adjustments if enabled
                    if time_adjustment:
                        question = self._add_time_based_adjustments(question, case)

                    questions.append(question)
            
            # Shuffle questions if requested
            if shuffle:
                random.shuffle(questions)
                # Renumber questions after shuffling
                for i, question in enumerate(questions):
                    question['question_number'] = i + 1
            
            quiz_data = {
                'quiz_metadata': {
                    'total_questions': len(questions),
                    'num_choices': num_choices,
                    'configuration': config,
                    'generated_at': self._get_timestamp(),
                    'adaptive_features': {
                        'adaptive_mode': adaptive_mode,
                        'differential_mode': differential_mode,
                        'multi_case_matching': multi_case_matching,
                        'streak_sequencing': streak_sequencing,
                        'time_adjustment': time_adjustment,
                        'bonus_xp_opportunities': bonus_xp_opportunities
                    }
                },
                'questions': questions
            }
            
            self.logger.info(f"Successfully generated quiz with {len(questions)} questions")
            return quiz_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate quiz: {e}")
            raise
    
    def _create_question(self, case: Dict[str, Any], diagnosis_by_category: Dict[str, List[str]], 
                        num_choices: int, question_number: int) -> Dict[str, Any]:
        """
        Create a single question from a case with clinical specifiers support.
        
        Args:
            case: Case dictionary
            diagnosis_by_category: Dictionary mapping categories to diagnosis lists
            num_choices: Number of multiple choice options
            question_number: Question number for labeling
        
        Returns:
            Dictionary containing question data
        """
        correct_answer = case['diagnosis']
        case_category = case.get('category', 'Unknown')
        
        # Generate distractors
        distractors = self._generate_distractors(
            correct_answer, case_category, diagnosis_by_category, num_choices - 1
        )
        
        # Add clinical specifiers to options
        enhanced_options = self._add_clinical_specifiers([correct_answer] + distractors, case)
        
        # Combine correct answer with distractors and shuffle
        all_options = enhanced_options
        random.shuffle(all_options)

        # Convert options to objects with id and text
        options_objects = []
        for i, option in enumerate(all_options):
            options_objects.append({
                'id': i,
                'text': option
            })

        # Find the index of the correct answer
        correct_index = next(i for i, option in enumerate(all_options) if option.startswith(correct_answer))

        # Format the question text
        question_text = self._format_question_text(case)

        # Generate explanation and reference
        explanation = self._generate_explanation(case, correct_answer)
        reference = self._generate_reference(case)

        return {
            'question_number': question_number,
            'case_id': case['case_id'],
            'question_text': question_text,
            'question_type': 'standard',
            'options': options_objects,
            'correct_answer': correct_answer,
            'correct_index': correct_index,
            'explanation': explanation,
            'reference': reference,
            'case_metadata': {
                'category': case.get('category'),
                'age_group': case.get('age_group'),
                'complexity': case.get('complexity')
            }
        }
    
    def _add_clinical_specifiers(self, options: List[str], case: Dict[str, Any]) -> List[str]:
        """
        Add clinical specifiers to answer options for enhanced realism.
        
        Args:
            options: List of diagnosis names
            case: Case dictionary for context
            
        Returns:
            List of enhanced options with clinical specifiers
        """
        enhanced_options = []
        age_group = case.get('age_group', 'adult')
        category = case.get('category', 'unknown')
        
        specifier_map = {
            'Depressive Disorders': {
                'child': ['with onset in childhood', 'pediatric onset'],
                'adolescent': ['with onset in adolescence', 'teenage onset'],
                'adult': ['with anxious distress', 'with mixed features', 'with melancholic features'],
                'older_adult': ['late onset', 'with vascular contributions']
            },
            'Anxiety Disorders': {
                'child': ['separation type', 'school refusal'],
                'adolescent': ['social type', 'performance type'],
                'adult': ['generalized type', 'with panic attacks'],
                'older_adult': ['late onset', 'with medical comorbidity']
            },
            'Schizophrenia Spectrum and Other Psychotic Disorders': {
                'child': ['childhood onset', 'early onset'],
                'adolescent': ['adolescent onset', 'with disorganized features'],
                'adult': ['paranoid type', 'disorganized type', 'catatonic type'],
                'older_adult': ['late onset', 'with cognitive decline']
            }
        }
        
        for option in options:
            # Randomly decide whether to add a specifier (30% chance)
            if random.random() < 0.3 and category in specifier_map and age_group in specifier_map[category]:
                specifiers = specifier_map[category][age_group]
                specifier = random.choice(specifiers)
                enhanced_option = f"{option}, {specifier}"
            else:
                enhanced_option = option
            
            enhanced_options.append(enhanced_option)
        
        return enhanced_options
    
    def _generate_distractors(self, correct_answer: str, case_category: str, 
                            diagnosis_by_category: Dict[str, List[str]], 
                            num_distractors: int) -> List[str]:
        """
        Generate distractor options for a multiple choice question.
        
        Args:
            correct_answer: The correct diagnosis
            case_category: Category of the case
            diagnosis_by_category: Dictionary mapping categories to diagnosis lists
            num_distractors: Number of distractors needed
        
        Returns:
            List of distractor diagnosis names
        """
        distractors = []
        
        # Try to get distractors from the same category first
        same_category_diagnoses = diagnosis_by_category.get(case_category, [])
        same_category_distractors = [
            d for d in same_category_diagnoses 
            if d != correct_answer
        ]
        
        # Shuffle same category distractors
        random.shuffle(same_category_distractors)
        
        # Add same category distractors first
        for distractor in same_category_distractors:
            if len(distractors) >= num_distractors:
                break
            distractors.append(distractor)
        
        # If we need more distractors, get from other categories
        if len(distractors) < num_distractors:
            all_diagnoses = []
            for category, diagnoses in diagnosis_by_category.items():
                if category != case_category:
                    all_diagnoses.extend(diagnoses)
            
            # Remove correct answer and already used distractors
            remaining_diagnoses = [
                d for d in all_diagnoses 
                if d != correct_answer and d not in distractors
            ]
            
            random.shuffle(remaining_diagnoses)
            
            for distractor in remaining_diagnoses:
                if len(distractors) >= num_distractors:
                    break
                distractors.append(distractor)
        
        # If still not enough distractors (edge case), create generic ones
        while len(distractors) < num_distractors:
            generic_distractors = [
                "Other Neurodevelopmental Disorder",
                "Other Mood Disorder", 
                "Other Anxiety Disorder",
                "Other Psychotic Disorder",
                "Other Personality Disorder"
            ]
            
            for generic in generic_distractors:
                if generic != correct_answer and generic not in distractors:
                    distractors.append(generic)
                    break
            
            if len(distractors) >= num_distractors:
                break
        
        return distractors[:num_distractors]
    
    def _format_question_text(self, case: Dict[str, Any]) -> str:
        """
        Format the question text with case narrative and MSE.
        
        Args:
            case: Case dictionary
        
        Returns:
            Formatted question text
        """
        question_text = f"""Clinical Presentation:
{case.get('narrative', '')}

Mental Status Examination:
{case.get('MSE', '')}

Based on the clinical presentation and mental status examination, what is the most likely diagnosis?"""
        
        return question_text
    
    def format_quiz(self, quiz_data: Dict[str, Any], format_type: str = 'text') -> str:
        """
        Format quiz data into different output formats.
        
        Args:
            quiz_data: Quiz data dictionary from generate_quiz
            format_type: Output format ('text', 'json', 'csv')
        
        Returns:
            Formatted quiz string
        """
        try:
            if format_type.lower() == 'json':
                return self._format_json(quiz_data)
            elif format_type.lower() == 'csv':
                return self._format_csv(quiz_data)
            elif format_type.lower() == 'text':
                return self._format_text(quiz_data)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to format quiz as {format_type}: {e}")
            raise
    
    def _format_text(self, quiz_data: Dict[str, Any]) -> str:
        """Format quiz as readable text."""
        output = []
        metadata = quiz_data['quiz_metadata']
        
        output.append("=" * 80)
        output.append("DIAGNOSIS QUIZ")
        output.append("=" * 80)
        output.append(f"Total Questions: {metadata['total_questions']}")
        output.append(f"Choices per Question: {metadata['num_choices']}")
        output.append(f"Generated: {metadata['generated_at']}")
        output.append("")
        
        for question in quiz_data['questions']:
            output.append(f"Question {question['question_number']}")
            output.append("-" * 40)
            output.append(question['question_text'])
            output.append("")
            
            for i, option in enumerate(question['options']):
                marker = "✓" if i == question['correct_index'] else " "
                option_text = option['text'] if isinstance(option, dict) else option
                output.append(f"{marker} {chr(65 + i)}. {option_text}")
            
            output.append("")
            output.append(f"Correct Answer: {question['correct_answer']}")
            output.append(f"Case ID: {question['case_id']}")
            output.append("")
            output.append("=" * 80)
            output.append("")
        
        return "\n".join(output)
    
    def _format_json(self, quiz_data: Dict[str, Any]) -> str:
        """Format quiz as JSON."""
        return json.dumps(quiz_data, indent=2, ensure_ascii=False)
    
    def _format_csv(self, quiz_data: Dict[str, Any]) -> str:
        """Format quiz as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            'Question_Number', 'Case_ID', 'Question_Text', 
            'Option_A', 'Option_B', 'Option_C', 'Option_D',
            'Correct_Answer', 'Correct_Index', 'Category', 'Age_Group', 'Complexity'
        ]
        
        # Adjust header for number of choices
        num_choices = quiz_data['quiz_metadata']['num_choices']
        option_headers = [f'Option_{chr(65 + i)}' for i in range(num_choices)]
        header = [
            'Question_Number', 'Case_ID', 'Question_Text'
        ] + option_headers + [
            'Correct_Answer', 'Correct_Index', 'Category', 'Age_Group', 'Complexity'
        ]
        
        writer.writerow(header)
        
        # Write questions
        for question in quiz_data['questions']:
            row = [
                question['question_number'],
                question['case_id'],
                question['question_text']
            ]
            
            # Add options (pad with empty strings if needed)
            options = question['options'] + [{'text': ''}] * (num_choices - len(question['options']))
            option_texts = [opt['text'] if isinstance(opt, dict) else opt for opt in options]
            row.extend(option_texts)
            
            # Add metadata
            row.extend([
                question['correct_answer'],
                question['correct_index'],
                question['case_metadata']['category'],
                question['case_metadata']['age_group'],
                question['case_metadata']['complexity']
            ])
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_adaptive_complexities(self) -> List[str]:
        """
        Get adaptive complexity recommendations based on user performance.
        
        Returns:
            List of recommended complexity levels
        """
        if not self.user_progress:
            return ["easy", "moderate"]
        
        recent_performance = self.user_progress.performance_metrics.recent_performance
        if not recent_performance:
            return ["easy"]
        
        # Use the existing adaptive difficulty calculation
        recommended = self.user_progress.calculate_adaptive_difficulty(recent_performance)
        
        # Map to actual complexity levels in the data
        mapped_recommended = self.difficulty_mapping.get(recommended, recommended)
        
        # Return a range of difficulties around the recommendation
        actual_difficulties = ["easy", "moderate", "high"]
        rec_index = actual_difficulties.index(mapped_recommended) if mapped_recommended in actual_difficulties else 0
        
        # Include current level and one level above/below
        complexities = [mapped_recommended]
        if rec_index > 0:
            complexities.append(actual_difficulties[rec_index - 1])
        if rec_index < len(actual_difficulties) - 1:
            complexities.append(actual_difficulties[rec_index + 1])
        
        # Filter out any None values and return
        return [c for c in complexities if c is not None]
    
    def _get_unlocked_difficulties(self) -> List[str]:
        """
        Get unlocked difficulty levels based on user progress.
        
        Returns:
            List of unlocked difficulty levels
        """
        if not self.user_progress:
            return ["beginner"]
        
        return list(self.user_progress.unlock_status.unlocked_difficulties)
    
    def _adaptive_case_selection(self, filtered_cases: List[Dict[str, Any]], num_questions: int) -> List[Dict[str, Any]]:
        """
        Select cases adaptively based on user performance and weaknesses.
        
        Args:
            filtered_cases: List of available cases
            num_questions: Number of questions needed
            
        Returns:
            List of selected cases
        """
        if not self.user_progress:
            return random.sample(filtered_cases, min(num_questions, len(filtered_cases)))
        
        # Analyze user weaknesses
        weak_categories = []
        for category, proficiency in self.user_progress.specialties.items():
            if proficiency.accuracy < 70:  # Below 70% accuracy
                weak_categories.append(category)
        
        # Prioritize weak areas
        selected_cases = []
        remaining_cases = filtered_cases.copy()
        
        # First, select cases from weak categories
        if weak_categories:
            weak_cases = [case for case in remaining_cases if case.get('category') in weak_categories]
            weak_to_select = min(len(weak_cases), num_questions // 2)  # Up to half from weak areas
            if weak_to_select > 0:
                selected_weak = random.sample(weak_cases, weak_to_select)
                selected_cases.extend(selected_weak)
                remaining_cases = [case for case in remaining_cases if case not in selected_weak]
        
        # Fill remaining slots with balanced selection
        remaining_needed = num_questions - len(selected_cases)
        if remaining_needed > 0 and remaining_cases:
            additional_cases = random.sample(remaining_cases, min(remaining_needed, len(remaining_cases)))
            selected_cases.extend(additional_cases)
        
        return selected_cases[:num_questions]
    
    def _streak_based_sequencing(self, filtered_cases: List[Dict[str, Any]], num_questions: int) -> List[Dict[str, Any]]:
        """
        Sequence cases based on current streak to maintain engagement.
        
        Args:
            filtered_cases: List of available cases
            num_questions: Number of questions needed
            
        Returns:
            List of selected cases in streak-optimized order
        """
        if not self.user_progress:
            return random.sample(filtered_cases, min(num_questions, len(filtered_cases)))
        
        current_streak = self.user_progress.streak_data.current_streak
        
        # For high streaks, gradually increase difficulty
        # For broken streaks, start with easier cases
        if current_streak >= 10:
            # High streak - challenge with harder cases
            difficulty_preference = ["high", "moderate", "easy"]
        elif current_streak >= 5:
            # Medium streak - balanced approach
            difficulty_preference = ["moderate", "high", "easy"]
        else:
            # Low or no streak - build confidence
            difficulty_preference = ["easy", "moderate"]
        
        selected_cases = []
        remaining_cases = filtered_cases.copy()
        
        for preferred_difficulty in difficulty_preference:
            if len(selected_cases) >= num_questions:
                break
            
            difficulty_cases = [case for case in remaining_cases if case.get('complexity') == preferred_difficulty]
            if difficulty_cases:
                to_select = min(len(difficulty_cases), num_questions - len(selected_cases))
                selected = random.sample(difficulty_cases, to_select)
                selected_cases.extend(selected)
                remaining_cases = [case for case in remaining_cases if case not in selected]
        
        # Fill with any remaining cases if needed
        if len(selected_cases) < num_questions and remaining_cases:
            additional = random.sample(remaining_cases, min(num_questions - len(selected_cases), len(remaining_cases)))
            selected_cases.extend(additional)
        
        return selected_cases[:num_questions]
    
    def _create_differential_question(self, case: Dict[str, Any], diagnosis_by_category: Dict[str, List[str]], 
                                    num_choices: int, question_number: int) -> Dict[str, Any]:
        """
        Create a differential diagnosis question with multiple plausible options.
        
        Args:
            case: Case dictionary
            diagnosis_by_category: Dictionary mapping categories to diagnosis lists
            num_choices: Number of multiple choice options
            question_number: Question number for labeling
            
        Returns:
            Dictionary containing differential diagnosis question data
        """
        correct_answer = case['diagnosis']
        case_category = case.get('category', 'Unknown')
        
        # Generate clinically similar distractors
        distractors = self._generate_smart_distractors(
            correct_answer, case_category, diagnosis_by_category, num_choices - 1
        )
        
        # Combine correct answer with distractors and shuffle
        all_options = [correct_answer] + distractors
        random.shuffle(all_options)

        # Convert options to objects
        options_objects = []
        for i, option in enumerate(all_options):
            options_objects.append({
                'id': i,
                'text': option
            })

        # Find the index of the correct answer
        correct_index = all_options.index(correct_answer)

        # Format differential diagnosis question text
        question_text = self._format_differential_question_text(case)

        # Generate explanation and reference
        explanation = self._generate_explanation(case, correct_answer)
        reference = self._generate_reference(case)

        return {
            'question_number': question_number,
            'case_id': case['case_id'],
            'question_text': question_text,
            'question_type': 'differential_diagnosis',
            'options': options_objects,
            'correct_answer': correct_answer,
            'correct_index': correct_index,
            'explanation': explanation,
            'reference': reference,
            'case_metadata': {
                'category': case.get('category'),
                'age_group': case.get('age_group'),
                'complexity': case.get('complexity')
            },
            'differential_info': {
                'key_symptoms': self._extract_key_symptoms(case),
                'differential_considerations': distractors + [correct_answer]
            }
        }

    def _create_multi_case_matching_question(self, cases: List[Dict[str, Any]], question_number: int) -> Dict[str, Any]:
        """
        Create a multi-case matching question with multiple cases and shuffled diagnoses.

        Args:
            cases: List of case dictionaries (should be 3)
            question_number: Question number for labeling

        Returns:
            Dictionary containing multi-case matching question data
        """
        if len(cases) != 3:
            raise ValueError("Multi-case matching requires exactly 3 cases")

        # Extract diagnoses from cases
        diagnoses = [case['diagnosis'] for case in cases]

        # Shuffle the diagnoses for the matching challenge
        shuffled_diagnoses = diagnoses.copy()
        random.shuffle(shuffled_diagnoses)

        # Create correct mapping
        correct_mapping = {case['case_id']: case['diagnosis'] for case in cases}

        # Create diagnosis options with IDs
        diagnosis_options = []
        for i, diagnosis in enumerate(shuffled_diagnoses):
            diagnosis_options.append({
                'id': i,
                'text': diagnosis
            })

        # Prepare case data for frontend (simplified)
        case_data = []
        for case in cases:
            case_data.append({
                'case_id': case['case_id'],
                'age': case.get('age_group', 'Unknown'),
                'gender': 'Unknown',  # Could be extracted from narrative if needed
                'chief_complaint': self._extract_chief_complaint(case),
                'history': self._extract_history(case),
                'examination': case.get('MSE', 'Not available'),
                'category': case.get('category'),
                'complexity': case.get('complexity')
            })

        question_text = "Match each case to the most appropriate diagnosis by dragging the diagnoses to the correct case columns."

        return {
            'question_number': question_number,
            'question_text': question_text,
            'question_type': 'multi_case_matching',
            'cases': case_data,
            'diagnosis_options': diagnosis_options,
            'correct_mapping': correct_mapping,
            'explanation': "Correct matching demonstrates understanding of distinguishing clinical features.",
            'reference': "Based on DSM-5 criteria and clinical presentation patterns."
        }

    def _generate_smart_distractors(self, correct_answer: str, case_category: str, 
                                  diagnosis_by_category: Dict[str, List[str]], 
                                  num_distractors: int) -> List[str]:
        """
        Generate smart distractors based on clinical similarity.
        
        Args:
            correct_answer: The correct diagnosis
            case_category: Category of the case
            diagnosis_by_category: Dictionary mapping categories to diagnosis lists
            num_distractors: Number of distractors needed
            
        Returns:
            List of clinically similar distractor diagnosis names
        """
        distractors = []
        
        # Get clinically similar diagnoses from the similarity map
        similar_diagnoses = []
        for category, diagnoses in self.clinical_similarity_map.items():
            if category == case_category or any(correct_answer.lower() in d.lower() for d in diagnoses):
                similar_diagnoses.extend(diagnoses)
        
        # Remove correct answer from similar diagnoses
        similar_diagnoses = [d for d in similar_diagnoses if d.lower() != correct_answer.lower()]
        
        # Shuffle similar diagnoses
        random.shuffle(similar_diagnoses)
        
        # Add clinically similar distractors first
        for distractor in similar_diagnoses:
            if len(distractors) >= num_distractors:
                break
            distractors.append(distractor)
        
        # If we need more distractors, use the original method
        if len(distractors) < num_distractors:
            additional_distractors = self._generate_distractors(
                correct_answer, case_category, diagnosis_by_category, 
                num_distractors - len(distractors)
            )
            distractors.extend(additional_distractors)
        
        return distractors[:num_distractors]
    
    def _format_differential_question_text(self, case: Dict[str, Any]) -> str:
        """
        Format the differential diagnosis question text.
        
        Args:
            case: Case dictionary
            
        Returns:
            Formatted differential diagnosis question text
        """
        question_text = f"""Case {case['case_id']} - Differential Diagnosis

Patient Information:
- Age Group: {case.get('age_group', 'Unknown')}
- Category: {case.get('category', 'Unknown')}

Clinical Presentation:
{case.get('narrative', '')}

Mental Status Examination:
{case.get('MSE', '')}

Considering the differential diagnosis, which of the following is the most likely primary diagnosis?"""
        
        return question_text
    
    def _extract_key_symptoms(self, case: Dict[str, Any]) -> List[str]:
        """
        Extract key symptoms from case narrative for differential diagnosis.
        
        Args:
            case: Case dictionary
            
        Returns:
            List of key symptoms
        """
        narrative = case.get('narrative', '').lower()
        mse = case.get('MSE', '').lower()
        combined_text = narrative + ' ' + mse
        
        # Simple keyword extraction for common psychiatric symptoms
        symptom_keywords = [
            'depressed', 'elevated', 'anxious', 'psychotic', 'hallucination',
            'delusion', 'mania', 'panic', 'obsessive', 'compulsive',
            'paranoid', 'disorganized', 'withdrawn', 'agitated', 'irritable'
        ]
        
        key_symptoms = []
        for keyword in symptom_keywords:
            if keyword in combined_text:
                key_symptoms.append(keyword)
        
        return key_symptoms[:5]  # Return top 5 symptoms

    def _extract_chief_complaint(self, case: Dict[str, Any]) -> str:
        """
        Extract chief complaint from case narrative.

        Args:
            case: Case dictionary

        Returns:
            Chief complaint string
        """
        narrative = case.get('narrative', '')
        # Simple extraction - look for first sentence or key phrases
        sentences = narrative.split('.')
        if sentences:
            return sentences[0].strip() + '.'
        return "Chief complaint not specified."

    def _extract_history(self, case: Dict[str, Any]) -> str:
        """
        Extract history from case narrative.

        Args:
            case: Case dictionary

        Returns:
            History string
        """
        narrative = case.get('narrative', '')
        sentences = narrative.split('.')
        if len(sentences) > 1:
            return '. '.join(sentences[1:3]).strip() + '.'  # Next 1-2 sentences
        return "History not detailed."

    def _add_bonus_xp_opportunities(self, question: Dict[str, Any], case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add bonus XP opportunities for complex cases or combinations.
        
        Args:
            question: Existing question dictionary
            case: Case dictionary
            
        Returns:
            Enhanced question dictionary with bonus XP opportunities
        """
        complexity = case.get('complexity', 'basic')
        category = case.get('category', 'unknown')
        
        bonus_opportunities = []
        
        # Complexity-based bonuses
        if complexity in ['advanced', 'expert']:
            bonus_opportunities.append({
                'type': 'complexity_bonus',
                'description': f'Bonus XP for {complexity} case',
                'xp_multiplier': self.difficulty_tiers.get(complexity, {}).get('xp_multiplier', 1.0)
            })
        
        # Category mastery bonuses
        if self.user_progress and category in self.user_progress.specialties:
            proficiency = self.user_progress.specialties[category]
            if proficiency.level >= 7:  # High proficiency
                bonus_opportunities.append({
                    'type': 'mastery_bonus',
                    'description': f'Mastery bonus for {category}',
                    'xp_multiplier': 1.2
                })
        
        # Streak bonuses
        if self.user_progress and self.user_progress.streak_data.current_streak >= 5:
            bonus_opportunities.append({
                'type': 'streak_bonus',
                'description': f'Streak bonus ({self.user_progress.streak_data.current_streak} in a row)',
                'xp_multiplier': self.user_progress.streak_data.streak_multiplier
            })
        
        question['bonus_opportunities'] = bonus_opportunities
        return question
    
    def _add_time_based_adjustments(self, question: Dict[str, Any], case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add time-based difficulty adjustments and bonuses.
        
        Args:
            question: Existing question dictionary
            case: Case dictionary
            
        Returns:
            Enhanced question dictionary with time-based adjustments
        """
        complexity = case.get('complexity', 'basic')
        tier_config = self.difficulty_tiers.get(complexity, {})
        
        time_adjustments = {
            'time_bonus_threshold': tier_config.get('time_bonus_threshold', 120),
            'accuracy_threshold': tier_config.get('accuracy_threshold', 60),
            'base_xp': 10 * tier_config.get('xp_multiplier', 1.0)
        }
        
        # Add time-based XP calculation
        question['time_adjustments'] = time_adjustments
        question['xp_calculation'] = {
            'base_xp': time_adjustments['base_xp'],
            'time_bonus_available': True,
            'accuracy_bonus_available': True
        }
        
        return question
    
    def calculate_xp_earned(self, question: Dict[str, Any], is_correct: bool, time_taken: float) -> Dict[str, Any]:
        """
        Calculate XP earned for a question with all bonuses and adjustments.
        
        Args:
            question: Question dictionary
            is_correct: Whether the answer was correct
            time_taken: Time taken to answer in seconds
            
        Returns:
            Dictionary with XP calculation details
        """
        if not is_correct:
            return {
                'base_xp': 0,
                'bonus_xp': 0,
                'total_xp': 0,
                'breakdown': {'incorrect_answer': 0}
            }
        
        base_xp = question.get('xp_calculation', {}).get('base_xp', 10)
        total_xp = base_xp
        breakdown = {'base_xp': base_xp}
        
        # Time bonus
        time_threshold = question.get('time_adjustments', {}).get('time_bonus_threshold', 120)
        if time_taken <= time_threshold:
            time_bonus = int(base_xp * 0.5)  # 50% bonus for fast answer
            total_xp += time_bonus
            breakdown['time_bonus'] = time_bonus
        
        # Apply bonus opportunities
        for bonus in question.get('bonus_opportunities', []):
            bonus_multiplier = bonus.get('xp_multiplier', 1.0)
            bonus_xp = int(base_xp * (bonus_multiplier - 1.0))
            if bonus_xp > 0:
                total_xp += bonus_xp
                breakdown[bonus['type']] = bonus_xp
        
        return {
            'base_xp': base_xp,
            'bonus_xp': total_xp - base_xp,
            'total_xp': total_xp,
            'breakdown': breakdown
        }
    
    def get_clinical_accuracy_score(self, question: Dict[str, Any], user_answer: str, 
                                  time_taken: float) -> Dict[str, Any]:
        """
        Calculate clinical accuracy score with detailed feedback.
        
        Args:
            question: Question dictionary
            user_answer: User's selected answer
            time_taken: Time taken to answer
            
        Returns:
            Dictionary with clinical accuracy scoring
        """
        correct_answer = question['correct_answer']
        is_correct = user_answer == correct_answer
        
        # Base accuracy
        accuracy_score = 100 if is_correct else 0
        
        # Time adjustment
        time_threshold = question.get('time_adjustments', {}).get('time_bonus_threshold', 120)
        time_efficiency = min(1.0, time_threshold / max(time_taken, 1))
        
        # Clinical similarity scoring for wrong answers
        similarity_score = 0
        if not is_correct and question.get('question_type') == 'differential_diagnosis':
            differential_info = question.get('differential_info', {})
            considerations = differential_info.get('differential_considerations', [])
            if user_answer in considerations:
                similarity_score = 50  # Partial credit for plausible differential
        elif question.get('question_type') == 'multi_case_matching':
            # For multi-case matching, calculate partial credit based on correct matches
            correct_mapping = question.get('correct_mapping', {})
            if isinstance(user_answer, dict):
                correct_matches = 0
                total_cases = len(correct_mapping)
                for case_id, correct_diagnosis in correct_mapping.items():
                    user_diagnosis = user_answer.get(case_id, {}).get('text') if isinstance(user_answer.get(case_id), dict) else user_answer.get(case_id)
                    if user_diagnosis == correct_diagnosis:
                        correct_matches += 1
                similarity_score = int((correct_matches / total_cases) * 100) if total_cases > 0 else 0
                is_correct = correct_matches == total_cases  # All must be correct for full credit
        
        final_score = accuracy_score
        if is_correct:
            final_score = min(100, accuracy_score + int(time_efficiency * 10))  # Up to 10 bonus points
        else:
            final_score = max(0, similarity_score)
        
        return {
            'accuracy_score': accuracy_score,
            'time_efficiency': time_efficiency,
            'similarity_score': similarity_score,
            'final_score': final_score,
            'is_correct': is_correct,
            'clinical_feedback': self._generate_clinical_feedback(question, user_answer, is_correct)
        }
    
    def _generate_clinical_feedback(self, question: Dict[str, Any], user_answer: str, is_correct: bool) -> str:
        """
        Generate clinical feedback based on the answer.
        
        Args:
            question: Question dictionary
            user_answer: User's answer
            is_correct: Whether the answer was correct
            
        Returns:
            Clinical feedback string
        """
        if is_correct:
            return "Excellent diagnosis! Your clinical reasoning is accurate."
        
        correct_answer = question['correct_answer']
        case_category = question['case_metadata']['category']
        
        # Check if the answer was clinically similar
        if question.get('question_type') == 'differential_diagnosis':
            differential_info = question.get('differential_info', {})
            considerations = differential_info.get('differential_considerations', [])
            if user_answer in considerations:
                return f"Good clinical thinking! {user_answer} is a valid differential diagnosis, but {correct_answer} is the primary diagnosis based on the key presenting features."
        
        # Provide category-specific feedback
        if case_category in self.clinical_similarity_map:
            similar_diagnoses = self.clinical_similarity_map[case_category]
            if any(user_answer.lower() in d.lower() for d in similar_diagnoses):
                return f"Close! {user_answer} is in the same category as the correct diagnosis. Consider the specific diagnostic criteria more carefully."
        
        return f"The correct diagnosis is {correct_answer}. Review the key distinguishing features for this condition."
    
    def generate_case_combination_quiz(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a quiz with case combinations for differential diagnosis scenarios.
        
        Args:
            config: Quiz configuration with combination parameters:
                - num_combinations: Number of case combinations (default: 5)
                - cases_per_combination: Number of cases per combination (default: 2-3)
                - combination_type: Type of combination ('similar', 'contrasting', 'progression')
        
        Returns:
            Dictionary containing combination quiz data
        """
        try:
            num_combinations = config.get('num_combinations', 5)
            combination_type = config.get('combination_type', 'similar')
            cases_per_combination = config.get('cases_per_combination', random.choice([2, 3]))
            
            # Get filtered cases
            filtered_cases = self.data_loader.get_filtered_cases(
                category=config.get('categories'),
                age_group=config.get('age_groups'),
                complexity=config.get('complexities'),
                diagnosis=config.get('diagnoses'),
                difficulty_tier=config.get('difficulty_tiers'),
                clinical_specifiers=config.get('clinical_specifiers'),
                course_specifiers=config.get('course_specifiers'),
                symptom_variants=config.get('symptom_variants')
            )
            
            if len(filtered_cases) < cases_per_combination:
                raise ValueError(f"Not enough cases for combinations. Need at least {cases_per_combination}")
            
            # Generate case combinations
            combinations = self._generate_case_combinations(
                filtered_cases, num_combinations, cases_per_combination, combination_type
            )
            
            # Load diagnoses for distractor generation
            all_diagnoses = self.data_loader.load_diagnoses()
            diagnosis_by_category = {}
            for diagnosis in all_diagnoses:
                category = diagnosis.get('category', 'Unknown')
                if category not in diagnosis_by_category:
                    diagnosis_by_category[category] = []
                diagnosis_by_category[category].append(diagnosis['name'])
            
            # Generate combination questions
            questions = []
            for i, combination in enumerate(combinations):
                question = self._create_combination_question(
                    combination, diagnosis_by_category, i + 1
                )
                questions.append(question)
            
            quiz_data = {
                'quiz_metadata': {
                    'total_questions': len(questions),
                    'quiz_type': 'case_combination',
                    'combination_type': combination_type,
                    'cases_per_combination': cases_per_combination,
                    'configuration': config,
                    'generated_at': self._get_timestamp()
                },
                'questions': questions
            }
            
            self.logger.info(f"Successfully generated combination quiz with {len(questions)} questions")
            return quiz_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate combination quiz: {e}")
            raise
    
    def _generate_case_combinations(self, cases: List[Dict[str, Any]], num_combinations: int, 
                                  cases_per_combination: int, combination_type: str) -> List[List[Dict[str, Any]]]:
        """
        Generate case combinations based on the specified type.
        
        Args:
            cases: List of available cases
            num_combinations: Number of combinations to generate
            cases_per_combination: Number of cases per combination
            combination_type: Type of combination ('similar', 'contrasting', 'progression')
        
        Returns:
            List of case combinations
        """
        combinations = []
        remaining_cases = cases.copy()
        
        for _ in range(num_combinations):
            if len(remaining_cases) < cases_per_combination:
                break
            
            if combination_type == 'similar':
                # Select cases from the same category
                category = random.choice([case.get('category') for case in remaining_cases])
                similar_cases = [case for case in remaining_cases if case.get('category') == category]
                if len(similar_cases) >= cases_per_combination:
                    combination = random.sample(similar_cases, cases_per_combination)
                else:
                    combination = random.sample(remaining_cases, cases_per_combination)
            
            elif combination_type == 'contrasting':
                # Select cases from different categories
                categories = list(set(case.get('category') for case in remaining_cases))
                combination = []
                for _ in range(cases_per_combination):
                    if categories:
                        category = random.choice(categories)
                        category_cases = [case for case in remaining_cases if case.get('category') == category]
                        if category_cases:
                            case = random.choice(category_cases)
                            combination.append(case)
                            remaining_cases.remove(case)
                            categories = list(set(case.get('category') for case in remaining_cases))
                
                if len(combination) < cases_per_combination:
                    # Fill with random cases if needed
                    needed = cases_per_combination - len(combination)
                    additional = random.sample(remaining_cases, min(needed, len(remaining_cases)))
                    combination.extend(additional)
            
            else:  # progression
                # Select cases with increasing complexity
                complexities = ['basic', 'intermediate', 'advanced', 'expert']
                combination = []
                for complexity in complexities[:cases_per_combination]:
                    complexity_cases = [case for case in remaining_cases if case.get('complexity') == complexity]
                    if complexity_cases:
                        case = random.choice(complexity_cases)
                        combination.append(case)
                        remaining_cases.remove(case)
                
                if len(combination) < cases_per_combination:
                    # Fill with random cases if needed
                    needed = cases_per_combination - len(combination)
                    additional = random.sample(remaining_cases, min(needed, len(remaining_cases)))
                    combination.extend(additional)
            
            combinations.append(combination)
            
            # Remove used cases from remaining
            for case in combination:
                if case in remaining_cases:
                    remaining_cases.remove(case)
        
        return combinations
    
    def _create_combination_question(self, combination: List[Dict[str, Any]], 
                                   diagnosis_by_category: Dict[str, List[str]], 
                                   question_number: int) -> Dict[str, Any]:
        """
        Create a question from a case combination.
        
        Args:
            combination: List of cases in the combination
            diagnosis_by_category: Dictionary mapping categories to diagnosis lists
            question_number: Question number for labeling
        
        Returns:
            Dictionary containing combination question data
        """
        # Use the first case as the primary case for the correct answer
        primary_case = combination[0]
        correct_answer = primary_case['diagnosis']
        
        # Generate distractors based on all cases in the combination
        all_categories = list(set(case.get('category') for case in combination))
        distractors = []
        
        for category in all_categories:
            if category:  # Ensure category is not None
                category_distractors = self._generate_distractors(
                    correct_answer, category, diagnosis_by_category, 2
                )
                distractors.extend(category_distractors)
        
        # Remove duplicates and limit to reasonable number
        distractors = list(set(distractors))[:3]
        
        # Combine correct answer with distractors and shuffle
        all_options = [correct_answer] + distractors
        random.shuffle(all_options)

        # Convert options to objects
        options_objects = []
        for i, option in enumerate(all_options):
            options_objects.append({
                'id': i,
                'text': option
            })

        # Find the index of the correct answer
        correct_index = all_options.index(correct_answer)

        # Format combination question text
        question_text = self._format_combination_question_text(combination)

        # Generate explanation and reference (use primary case)
        explanation = self._generate_explanation(combination[0], correct_answer)
        reference = self._generate_reference(combination[0])

        return {
            'question_number': question_number,
            'case_ids': [case['case_id'] for case in combination],
            'question_text': question_text,
            'question_type': 'case_combination',
            'options': options_objects,
            'correct_answer': correct_answer,
            'correct_index': correct_index,
            'explanation': explanation,
            'reference': reference,
            'combination_metadata': {
                'num_cases': len(combination),
                'categories': all_categories,
                'complexities': [case.get('complexity') for case in combination]
            }
        }
    
    def _format_combination_question_text(self, combination: List[Dict[str, Any]]) -> str:
        """
        Format the question text for a case combination.
        
        Args:
            combination: List of cases in the combination
        
        Returns:
            Formatted combination question text
        """
        question_text = "Case Combination Analysis\n\n"
        
        for i, case in enumerate(combination, 1):
            question_text += f"""Case {case['case_id']} (Patient {i}):

Patient Information:
- Age Group: {case.get('age_group', 'Unknown')}
- Category: {case.get('category', 'Unknown')}

Clinical Presentation:
{case.get('narrative', '')}

Mental Status Examination:
{case.get('MSE', '')}

"""
        
        question_text += """Based on the clinical presentations above, which diagnosis best fits Patient 1 (the primary case)?
Note: Consider the differential diagnoses suggested by the other patient presentations."""

        return question_text

    def _generate_explanation(self, case: Dict[str, Any], correct_answer: str) -> str:
        """
        Generate a clinical explanation for the correct diagnosis.

        Args:
            case: Case dictionary
            correct_answer: The correct diagnosis

        Returns:
            Explanation string
        """
        category = case.get('category', 'Unknown')

        explanations = {
            'Depressive Disorders': f"The diagnosis of {correct_answer} is supported by the patient's persistent depressed mood, anhedonia, and neurovegetative symptoms. The MSE reveals psychomotor changes and hopelessness, which are characteristic of this condition.",
            'Anxiety Disorders': f"The diagnosis of {correct_answer} is based on the patient's excessive worry, physical symptoms of anxiety, and avoidance behaviors. The MSE shows anxious affect and preoccupation with feared outcomes.",
            'Schizophrenia Spectrum and Other Psychotic Disorders': f"The diagnosis of {correct_answer} is indicated by the presence of psychotic symptoms including delusions and hallucinations, along with disorganized thinking. The MSE demonstrates thought disorder and impaired insight.",
            'Bipolar and Related Disorders': f"The diagnosis of {correct_answer} is supported by the history of manic or hypomanic episodes with elevated mood, increased energy, and impaired judgment. The MSE may show expansive affect during acute episodes."
        }

        return explanations.get(category, f"The diagnosis of {correct_answer} is supported by the clinical presentation and mental status examination findings.")

    def _generate_reference(self, case: Dict[str, Any]) -> str:
        """
        Generate a reference for the diagnosis.

        Args:
            case: Case dictionary

        Returns:
            Reference string
        """
        category = case.get('category', 'Unknown')

        references = {
            'Depressive Disorders': "DSM-5 Criteria: Five or more symptoms including depressed mood, anhedonia, weight changes, sleep disturbance, fatigue, guilt, concentration difficulties, psychomotor changes, or suicidal ideation.",
            'Anxiety Disorders': "DSM-5 Criteria: Excessive anxiety and worry occurring more days than not for at least 6 months, plus associated symptoms like restlessness, fatigue, difficulty concentrating, irritability, muscle tension, or sleep disturbance.",
            'Schizophrenia Spectrum and Other Psychotic Disorders': "DSM-5 Criteria: Two or more symptoms including delusions, hallucinations, disorganized speech, grossly disorganized behavior, or negative symptoms, with duration of 6 months and impairment in functioning.",
            'Bipolar and Related Disorders': "DSM-5 Criteria: Distinct period of abnormally elevated, expansive, or irritable mood and increased activity/energy lasting at least 1 week, with marked impairment or requiring hospitalization."
        }

        return references.get(category, "DSM-5 Diagnostic Criteria for psychiatric disorders.")
    
    def calculate_achievement_opportunities(self, quiz_data: Dict[str, Any], user_progress=None) -> Dict[str, Any]:
        """
        Calculate achievement opportunities for a given quiz.
        
        Args:
            quiz_data: Quiz data dictionary
            user_progress: UserProgress instance for personalized opportunities
        
        Returns:
            Dictionary with achievement opportunities
        """
        opportunities = {
            'potential_achievements': [],
            'xp_opportunities': {},
            'challenge_recommendations': []
        }
        
        questions = quiz_data.get('questions', [])
        quiz_metadata = quiz_data.get('quiz_metadata', {})
        
        # Analyze quiz characteristics
        total_questions = len(questions)
        categories = list(set(q.get('case_metadata', {}).get('category') for q in questions))
        complexities = list(set(q.get('case_metadata', {}).get('complexity') for q in questions))
        
        # XP opportunities
        base_xp_total = sum(q.get('xp_calculation', {}).get('base_xp', 10) for q in questions)
        opportunities['xp_opportunities'] = {
            'base_xp_total': base_xp_total,
            'potential_bonus_xp': int(base_xp_total * 0.5),  # Estimate potential bonuses
            'max_possible_xp': int(base_xp_total * 1.5)
        }
        
        # Potential achievements based on quiz type
        if quiz_metadata.get('quiz_type') == 'case_combination':
            opportunities['potential_achievements'].append({
                'id': 'combination_master',
                'name': 'Combination Master',
                'description': 'Complete a case combination quiz',
                'requirement': 'Complete the quiz with 80% accuracy'
            })
        
        if 'expert' in complexities:
            opportunities['potential_achievements'].append({
                'id': 'expert_challenger',
                'name': 'Expert Challenger',
                'description': 'Attempt expert-level cases',
                'requirement': 'Complete all expert cases correctly'
            })
        
        if len(categories) >= 3:
            opportunities['potential_achievements'].append({
                'id': 'versatile_diagnostician',
                'name': 'Versatile Diagnostician',
                'description': 'Work with multiple diagnostic categories',
                'requirement': f'Complete cases across {len(categories)} categories'
            })
        
        # Challenge recommendations based on user progress
        if user_progress:
            current_streak = user_progress.streak_data.current_streak
            if current_streak >= 5:
                opportunities['challenge_recommendations'].append({
                    'type': 'streak_maintenance',
                    'description': f'Maintain your {current_streak}-question streak!',
                    'bonus_multiplier': user_progress.streak_data.streak_multiplier
                })
            
            # Check for specialty opportunities
            for category in categories:
                proficiency = user_progress.specialties.get(category)
                if proficiency and proficiency.level >= 5:
                    opportunities['challenge_recommendations'].append({
                        'type': 'specialty_mastery',
                        'category': category,
                        'description': f'Excel in {category} cases',
                        'current_level': proficiency.level
                    })
        
        return opportunities
    
    def get_answer_key(self, quiz_data: Dict[str, Any]) -> str:
        """
        Generate an answer key for the quiz.
        
        Args:
            quiz_data: Quiz data dictionary from generate_quiz
        
        Returns:
            Formatted answer key string
        """
        try:
            output = []
            metadata = quiz_data['quiz_metadata']
            
            output.append("=" * 50)
            output.append("ANSWER KEY")
            output.append("=" * 50)
            output.append(f"Total Questions: {metadata['total_questions']}")
            output.append(f"Generated: {metadata['generated_at']}")
            output.append("")
            
            for question in quiz_data['questions']:
                output.append(f"Q{question['question_number']}: {question['correct_answer']}")
                output.append(f"   Case ID: {question['case_id']}")
                output.append(f"   Category: {question['case_metadata']['category']}")
                output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            self.logger.error(f"Failed to generate answer key: {e}")
            raise