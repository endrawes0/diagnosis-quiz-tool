# Scoring Module

A comprehensive scoring system for diagnosis quizzes with detailed analytics, multiple scoring modes, and export capabilities.

## Features

### 🎯 Multiple Scoring Modes
- **Strict Mode**: Exact match required for correct answers
- **Lenient Mode**: Allows for minor variations and partial word matches
- **Partial Credit Mode**: Awards partial points for category matches and similar diagnoses

### 📊 Comprehensive Analytics
- Performance statistics by category, complexity, and age group
- Time analysis and efficiency scoring
- Difficulty assessment and question analysis
- Detailed feedback per question

### 📤 Export Capabilities
- **JSON**: Structured data for programmatic use
- **CSV**: Tabular format for spreadsheet analysis
- **Text**: Human-readable reports
- **HTML**: Styled reports for web display

### ⏱️ Time Tracking
- Per-question timing
- Session duration tracking
- Time efficiency analysis
- Performance vs. time correlation

### 🎓 Personalized Feedback
- Strengths identification
- Areas for improvement
- Personalized recommendations
- Learning suggestions

## Quick Start

```python
from modules.scoring import Scoring, ScoringMode, ExportFormat

# Initialize scoring system
scoring = Scoring(scoring_mode=ScoringMode.STRICT)

# Start a quiz session
scoring.start_quiz_session(quiz_data)

# Record answers with timing
scoring.start_question_timer(1)
scoring.record_answer(1, "Major Depressive Disorder", 30.5)

# Calculate scores
stats = scoring.calculate_scores()

# Export results
json_report = scoring.export_results(ExportFormat.JSON)
text_report = scoring.export_results(ExportFormat.TEXT)
```

## Scoring Modes

### Strict Mode
- Requires exact string match (case-insensitive)
- Binary scoring: 1.0 for correct, 0.0 for incorrect
- Best for formal assessments

### Lenient Mode
- Allows for minor variations in wording
- Checks for word overlap (80% threshold)
- Good for practice sessions

### Partial Credit Mode
- Awards points for category matches
- Similarity-based scoring
- Configurable bonus system:
  - Category match: 0.25 points
  - Age group match: 0.15 points
  - Complexity match: 0.10 points
  - Similarity threshold: 0.7

## Performance Analytics

### Category Performance
```python
stats = scoring.calculate_scores()
for category, data in stats.category_performance.items():
    print(f"{category}: {data['accuracy']:.1f}% accuracy")
```

### Complexity Analysis
```python
for complexity, data in stats.complexity_performance.items():
    print(f"{complexity}: {data['average_score']:.2f} avg score")
```

### Time Analysis
```python
time_stats = stats.time_analysis
print(f"Average time: {time_stats['median_time']:.1f}s")
print(f"Time efficiency: {time_stats['time_efficiency_score']:.1f}")
```

## Export Formats

### JSON Export
Structured data with all metrics:
```json
{
  "session_info": {...},
  "summary": {...},
  "performance_analysis": {...},
  "detailed_feedback": [...]
}
```

### CSV Export
Tabular format for analysis:
```csv
SUMMARY
Metric,Value
Total Questions,10
Correct Answers,7
Percentage Score,70.0%
```

### Text Export
Human-readable report with sections:
- Summary statistics
- Performance by category
- Performance by complexity
- Detailed feedback

### HTML Export
Styled web report with:
- Color-coded results
- Responsive tables
- Professional formatting

## Advanced Features

### Partial Credit Configuration
```python
partial_config = {
    'category_match_bonus': 0.30,
    'age_group_match_bonus': 0.15,
    'complexity_match_bonus': 0.10,
    'similarity_threshold': 0.6
}

scoring = Scoring(
    scoring_mode=ScoringMode.PARTIAL,
    partial_credit_config=partial_config
)
```

### Performance Reports
```python
report = scoring.get_performance_report()
print("Strengths:", report['strengths'])
print("Recommendations:", report['recommendations'])
```

### Session Management
```python
# Get session summary
summary = scoring.get_session_summary()

# Reset session
scoring.reset_session()
```

## Data Structures

### QuestionResult
```python
@dataclass
class QuestionResult:
    question_number: int
    case_id: str
    user_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    score: float
    max_score: float
    time_spent: float
    category: str
    age_group: str
    complexity: str
    feedback: str
    partial_credit_reason: Optional[str]
```

### PerformanceStats
```python
@dataclass
class PerformanceStats:
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    total_score: float
    max_possible_score: float
    percentage_score: float
    average_time_per_question: float
    total_time_spent: float
    category_performance: Dict[str, Dict[str, Any]]
    complexity_performance: Dict[str, Dict[str, Any]]
    age_group_performance: Dict[str, Dict[str, Any]]
    difficulty_analysis: Dict[str, Any]
    time_analysis: Dict[str, Any]
```

## Error Handling

The module includes comprehensive error handling:
- Invalid quiz data validation
- Question number bounds checking
- Session state validation
- Export format validation
- Graceful fallbacks for missing data

## Logging

Detailed logging for debugging and monitoring:
- Session start/end events
- Answer recording
- Score calculations
- Export operations
- Error conditions

## Integration

The scoring module integrates seamlessly with:
- `QuizGenerator`: Uses generated quiz data
- `DataLoader`: Access to case and diagnosis data
- CLI interfaces: Command-line quiz applications
- Web applications: REST API endpoints

## Best Practices

1. **Always start a session** before recording answers
2. **Use timing** for accurate performance analysis
3. **Choose appropriate scoring mode** for your use case
4. **Export results** for long-term tracking
5. **Handle exceptions** gracefully in production code

## Examples

See the example usage file for comprehensive demonstrations of all features.