# Enhanced QuizGenerator - Adaptive Selection and Combination Logic

## Overview

The QuizGenerator has been significantly enhanced to support adaptive selection and combination logic, integrating seamlessly with the UserProgress system and the enhanced data model. This upgrade transforms the quiz generation from a static process to a dynamic, personalized learning experience.

## Key Features Implemented

### 1. Adaptive Difficulty Selection
- **Integration with UserProgress**: Uses user performance data to recommend appropriate difficulty levels
- **Dynamic Complexity Adjustment**: Automatically adjusts complexity based on recent performance metrics
- **Difficulty Tier Filtering**: Respects unlock requirements and user level restrictions
- **Backward Compatibility**: Maintains support for existing difficulty naming systems

### 2. Case Combinations for Differential Diagnosis
- **Similar Cases**: Groups cases from the same diagnostic category
- **Contrasting Cases**: Combines cases from different categories for broader differential practice
- **Progression Cases**: Sequences cases by increasing complexity
- **Multi-Patient Scenarios**: Creates complex clinical situations with multiple patient presentations

### 3. Smart Distractor Selection
- **Clinical Similarity Mapping**: Uses psychiatric diagnostic relationships to generate plausible distractors
- **Category-Based Selection**: Prioritizes distractors from the same diagnostic category
- **Symptom-Based Matching**: Considers key symptoms when selecting differential diagnoses
- **Fallback Mechanisms**: Ensures robust distractor generation even with limited data

### 4. Difficulty Tier Filtering with Unlock Requirements
- **Level-Based Access**: Restricts content based on user level and achievements
- **Progressive Unlocking**: Gradually opens higher difficulty tiers as users advance
- **Achievement-Based Unlocks**: Special content unlocked through specific achievements
- **Customizable Tiers**: Flexible difficulty configuration system

### 5. Clinical Specifiers in Answer Options
- **Age-Specific Specifiers**: Adds appropriate clinical specifiers based on patient age groups
- **Category-Specific Features**: Includes relevant diagnostic specifiers for different categories
- **Realistic Options**: Makes answer choices more clinically authentic
- **Randomized Application**: Applies specifiers probabilistically for variety

### 6. Bonus XP Opportunities
- **Complexity Bonuses**: Higher XP for advanced and expert cases
- **Mastery Bonuses**: Extra rewards for high proficiency in specialty areas
- **Streak Bonuses**: Multipliers for maintaining correct answer streaks
- **Time Bonuses**: Rewards for quick, accurate diagnoses

### 7. Streak-Based Question Sequencing
- **Confidence Building**: Starts with easier cases after streak breaks
- **Progressive Challenge**: Increases difficulty as streaks grow longer
- **Engagement Optimization**: Maintains user motivation through appropriate challenge levels
- **Performance-Based Adaptation**: Adjusts sequencing based on current streak status

### 8. Time-Based Difficulty Adjustments
- **Time Thresholds**: Different time expectations for different complexity levels
- **Efficiency Bonuses**: Rewards for quick, accurate responses
- **Adaptive Timing**: Adjusts time expectations based on case complexity
- **Performance Metrics**: Tracks time efficiency alongside accuracy

## New Methods Added

### Core Adaptive Methods
- `_get_adaptive_complexities()`: Recommends difficulty levels based on performance
- `_get_unlocked_difficulties()`: Returns available difficulty tiers for user
- `_adaptive_case_selection()`: Selects cases based on user weaknesses and strengths
- `_streak_based_sequencing()`: Orders questions to maintain engagement

### Enhanced Question Generation
- `_create_differential_question()`: Creates differential diagnosis questions
- `_generate_smart_distractors()`: Uses clinical similarity for distractor selection
- `_add_clinical_specifiers()`: Adds realistic clinical specifiers to options
- `_add_bonus_xp_opportunities()`: Calculates potential XP bonuses
- `_add_time_based_adjustments()`: Implements time-based scoring

### Case Combination Support
- `generate_case_combination_quiz()`: Creates multi-case quizzes
- `_generate_case_combinations()`: Groups cases by specified criteria
- `_create_combination_question()`: Builds questions from case combinations
- `_format_combination_question_text()`: Formats multi-patient scenarios

### Scoring and Feedback
- `calculate_xp_earned()`: Comprehensive XP calculation with bonuses
- `get_clinical_accuracy_score()`: Detailed clinical accuracy assessment
- `_generate_clinical_feedback()`: Provides educational feedback
- `calculate_achievement_opportunities()`: Identifies potential achievements

## Configuration Options

The enhanced QuizGenerator supports numerous new configuration options:

```python
config = {
    # Existing options
    'num_questions': 10,
    'num_choices': 4,
    'categories': ['mood_disorders', 'anxiety_disorders'],
    
    # New adaptive features
    'adaptive_mode': True,                    # Enable adaptive difficulty
    'differential_mode': True,                 # Use differential diagnosis questions
    'streak_sequencing': True,                # Enable streak-based ordering
    'time_adjustment': True,                  # Add time-based bonuses
    'bonus_xp_opportunities': True,           # Enable bonus XP calculations
    
    # Case combination options
    'combination_type': 'similar',            # 'similar', 'contrasting', 'progression'
    'cases_per_combination': 2,               # Number of cases per combination
    'num_combinations': 5                     # Number of combinations to generate
}
```

## Integration with UserProgress

The enhanced QuizGenerator seamlessly integrates with the UserProgress system:

- **Performance Analysis**: Uses recent performance metrics for adaptation
- **Specialty Proficiency**: Considers user strengths and weaknesses
- **Streak Data**: Incorporates current streak information
- **Unlock Status**: Respects content unlock requirements
- **Achievement Progress**: Identifies achievement opportunities

## Clinical Accuracy Scoring

The new scoring system provides detailed feedback:

- **Base Accuracy**: Simple correct/incorrect scoring
- **Time Efficiency**: Rewards for quick, accurate responses
- **Similarity Scoring**: Partial credit for plausible differential diagnoses
- **Clinical Feedback**: Educational feedback based on answer choices
- **Comprehensive Breakdown**: Detailed scoring components

## Backward Compatibility

All existing functionality is preserved:

- Original `generate_quiz()` method works unchanged
- Existing configuration options remain supported
- Original question formatting maintained
- Legacy distractor generation preserved as fallback

## Example Usage

```python
# Initialize with UserProgress for adaptive features
data_loader = DataLoader()
user_progress = UserProgress('user123', 'Dr. Smith')
quiz_generator = QuizGenerator(data_loader, user_progress)

# Generate adaptive quiz
config = {
    'num_questions': 5,
    'adaptive_mode': True,
    'differential_mode': True,
    'bonus_xp_opportunities': True
}
quiz_data = quiz_generator.generate_quiz(config)

# Generate case combination quiz
combo_config = {
    'num_combinations': 3,
    'combination_type': 'contrasting'
}
combo_quiz = quiz_generator.generate_case_combination_quiz(combo_config)

# Calculate XP for a question
xp_result = quiz_generator.calculate_xp_earned(question, True, 85.5)

# Get clinical accuracy feedback
accuracy = quiz_generator.get_clinical_accuracy_score(question, user_answer, time_taken)

# Identify achievement opportunities
opportunities = quiz_generator.calculate_achievement_opportunities(quiz_data, user_progress)
```

## Benefits

1. **Personalized Learning**: Adapts to individual user performance and needs
2. **Clinical Realism**: More authentic diagnostic scenarios with specifiers and combinations
3. **Engagement**: Streak-based sequencing and bonus opportunities maintain motivation
4. **Educational Value**: Detailed feedback and differential diagnosis practice
5. **Progressive Difficulty**: Smooth difficulty progression based on user development
6. **Comprehensive Assessment**: Multi-dimensional scoring beyond simple accuracy

## Future Enhancements

The architecture supports future additions:

- Machine learning-based adaptation algorithms
- More sophisticated clinical similarity metrics
- Multi-modal case presentations (images, audio, video)
- Collaborative diagnosis scenarios
- Specialty-specific quiz modes
- Adaptive testing methodologies

This enhanced QuizGenerator represents a significant advancement in clinical education technology, providing a sophisticated, adaptive learning environment that grows with the user's expertise.