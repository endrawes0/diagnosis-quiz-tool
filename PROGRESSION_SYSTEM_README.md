# Enhanced Scoring and Progression System

This document describes the enhanced scoring module with gamified progression and unlock mechanics for the diagnosis quiz tool.

## Overview

The enhanced system combines comprehensive scoring with gamification elements to create an engaging learning experience. It tracks user progress, awards achievements, provides adaptive difficulty recommendations, and maintains detailed performance analytics.

## Components

### 1. Progression System (`src/modules/progression.py`)

The `UserProgress` class is the core of the progression system, tracking:

#### Core Features
- **XP and Levels**: Exponential XP scaling with level progression
- **Achievements**: 24+ achievements across 11 categories
- **Streak Tracking**: Consecutive correct diagnoses with multipliers
- **Specialty Proficiency**: Category-specific skill levels (1-10)
- **Performance Analytics**: Detailed metrics and trend analysis
- **Unlock System**: Progressive content unlocking based on performance

#### Key Classes

```python
class UserProgress:
    """Main progression tracking class"""
    
class Achievement:
    """Achievement definition"""
    
class SpecialtyProficiency:
    """Category-specific skill tracking"""
    
class StreakData:
    """Streak tracking with multipliers"""
```

### 2. Enhanced Scoring (`src/modules/scoring.py`)

The enhanced `Scoring` class integrates with the progression system:

#### New Features
- **XP Calculation**: Based on accuracy, speed, and difficulty
- **Clinical Accuracy Scoring**: Partial credit for specifiers
- **Progression Integration**: Automatic updates to user progress
- **Achievement Awards**: Session-based achievement checking
- **Performance Reports**: Detailed analytics with recommendations

#### XP Calculation Formula

```
Base XP = Score × 10
Accuracy Bonus = 
  - 50% for perfect accuracy (100%)
  - 25% for excellent accuracy (90-99%)
  - 10% for good accuracy (80-89%)

Time Bonus = 
  - 20% for <30 seconds per question
  - 10% for <60 seconds per question

Difficulty Bonus = 
  - 15% for advanced cases with 80%+ accuracy
  - 25% for expert cases with 70%+ accuracy

Total XP = (Base XP + Accuracy Bonus + Time Bonus + Difficulty Bonus) × Streak Multiplier
```

## Achievement System

### Achievement Categories

1. **Progression**: Level-based achievements
2. **Skill**: Accuracy and competence achievements
3. **Specialty**: Category mastery achievements
4. **Speed**: Quick diagnosis achievements
5. **Streak**: Consecutive correct diagnoses
6. **Advanced**: Complex scenario achievements
7. **Exploration**: Variety-based achievements
8. **Consistency**: Regular practice achievements
9. **Time-based**: Time-specific achievements
10. **Endurance**: Long session achievements
11. **Resilience**: Recovery-based achievements

### Badge Types

- **Bronze**: Basic achievements (10-75 XP)
- **Silver**: Intermediate achievements (75-150 XP)
- **Gold**: Advanced achievements (150-250 XP)

## Difficulty Tiers

### Progressive Unlock System

1. **Beginner** (Level 1+)
   - Classic textbook presentations
   - Low differential complexity
   - No time pressure

2. **Intermediate** (Level 5+)
   - Atypical features and comorbidities
   - Moderate differential complexity
   - Time limits introduced

3. **Advanced** (Level 15+)
   - Complex cases with multiple comorbidities
   - High differential complexity
   - Challenging time limits

4. **Expert** (Level 30+)
   - Highly atypical presentations
   - Very high differential complexity
   - Strict time limits

## Adaptive Difficulty Algorithm

The system recommends appropriate difficulty based on:

- Recent performance accuracy
- Average completion time
- Current unlocked difficulties
- User preferences

### Recommendation Logic

```python
if recent_accuracy >= 90 and avg_time < 120:
    recommend highest unlocked difficulty
elif recent_accuracy >= 75:
    recommend intermediate or advanced
elif recent_accuracy >= 60:
    recommend intermediate
else:
    recommend beginner
```

## Specialty Proficiency System

### Categories Tracked

- Mood Disorders
- Psychotic Disorders
- Anxiety Disorders
- Personality Disorders
- Substance Use Disorders
- Neurodevelopmental Disorders
- Trauma & Stressor-Related
- Eating Disorders
- Obsessive-Compulsive
- Somatic Symptom
- Sleep-Wake Disorders
- Sexual Dysfunctions
- Gender Dysphoria
- Disruptive Impulse Control
- Neurocognitive Disorders

### Proficiency Calculation

```python
Level = min(10, int(accuracy / 10) + 1)
Accuracy = (correct_cases / total_cases) × 100
```

## Streak System

### Multiplier Tiers

- 1-2 correct: 1.0x multiplier
- 3-4 correct: 1.1x multiplier
- 5-9 correct: 1.25x multiplier
- 10-14 correct: 1.5x multiplier
- 15-19 correct: 1.75x multiplier
- 20+ correct: 2.0x multiplier

### Streak Persistence

Streaks persist across days but reset if more than 24 hours pass between correct diagnoses.

## Clinical Accuracy Scoring

### Specifier Support

The system supports partial credit for diagnosis specifiers:

```python
# Example: Major Depressive Disorder with anxious distress, moderate, recurrent
specifiers = {
    'with anxious distress': 0.15,
    'moderate': 0.10,
    'recurrent': 0.05
}

# Scoring:
# - 70% for correct main diagnosis
# - 30% for correct specifiers (weighted by importance)
```

## Performance Analytics

### Metrics Tracked

- Overall accuracy and trends
- Category-specific performance
- Difficulty-specific performance
- Time efficiency analysis
- Improvement trends
- Strength and weakness identification

### Report Generation

The system generates comprehensive reports including:

- Session summaries
- Progression status
- Achievement progress
- Performance recommendations
- Unlock status

## Usage Examples

### Basic Integration

```python
from modules.scoring import Scoring
from modules.progression import UserProgress

# Create progression system
user_progress = UserProgress("user123", "DrSmith")

# Create scoring with progression
scoring = Scoring(scoring_mode=ScoringMode.PARTIAL, user_progress=user_progress)

# Start quiz session
scoring.start_quiz_session(quiz_data)

# Record answers
scoring.record_answer(1, "MDD", 45.0)

# Calculate scores and update progression
stats = scoring.calculate_scores()

# Get progression report
report = scoring.get_session_progression_report()
```

### Clinical Accuracy Scoring

```python
# With specifiers
specifiers = {
    'with anxious distress': 0.15,
    'moderate': 0.10,
    'recurrent': 0.05
}

score, feedback = scoring.calculate_clinical_accuracy_score(
    "Major Depressive Disorder with anxious distress, moderate",
    "Major Depressive Disorder",
    specifiers
)
```

### Performance Analysis

```python
# Get comprehensive report
report = user_progress.generate_performance_report()

# Get XP breakdown
xp_breakdown = user_progress.get_xp_breakdown()

# Get unlock recommendations
recommendations = user_progress.get_unlock_recommendations()
```

## Data Persistence

### Serialization Support

Both `UserProgress` and `Scoring` classes support serialization:

```python
# Save user progress
data = user_progress.to_dict()
with open('user_progress.json', 'w') as f:
    json.dump(data, f)

# Load user progress
user_progress = UserProgress("user123", "DrSmith")
with open('user_progress.json', 'r') as f:
    data = json.load(f)
user_progress.from_dict(data)
```

## Configuration

### Achievement Configuration

Achievements are defined in `data/achievements.json` with:

- Achievement definitions
- Requirements and rewards
- Badge types and categories
- Icon assignments

### Difficulty Configuration

Difficulty tiers are defined in `data/difficulty_tiers.json` with:

- Tier characteristics
- Level requirements
- XP ranges
- Unlock conditions

## Testing

### Test Coverage

Comprehensive tests are provided:

- `test_progression_integration.py`: Integration tests
- `test_progression_features.py`: Feature-specific tests

### Running Tests

```bash
python3 test_progression_integration.py
python3 test_progression_features.py
```

## Backward Compatibility

The enhanced scoring system maintains full backward compatibility:

- Existing scoring modes (STRICT, LENIENT, PARTIAL) work unchanged
- All existing methods and properties preserved
- Progression system is optional (can be disabled)
- No breaking changes to existing API

## Future Enhancements

### Planned Features

1. **Leaderboards**: Global and category-specific rankings
2. **Social Features**: Achievement sharing and comparison
3. **Learning Paths**: Guided progression through specialties
4. **Adaptive Learning**: AI-powered difficulty adjustment
5. **Detailed Analytics**: Advanced performance insights
6. **Custom Achievements**: User-defined achievement goals

### Extensibility

The system is designed for easy extension:

- New achievement types can be added
- Custom difficulty algorithms supported
- Additional specialty categories easily integrated
- Flexible XP calculation formulas

## Conclusion

The enhanced scoring and progression system provides a comprehensive gamification framework that enhances the learning experience while maintaining educational rigor. The system balances engagement with clinical accuracy, encouraging both speed and precision in diagnostic skills development.