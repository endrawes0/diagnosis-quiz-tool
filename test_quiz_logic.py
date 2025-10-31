#!/usr/bin/env python3
"""
Test the quiz generation logic directly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.quiz_generator import QuizGenerator
from modules.data_loader import DataLoader

def test_multicase_question_count():
    """Test that multi-case quiz generation creates the correct number of questions."""

    # Initialize components
    data_loader = DataLoader('data')
    quiz_generator = QuizGenerator(data_loader)

    # Test configuration for 5 multi-case questions
    config = {
        "num_questions": 5,
        "multi_case_matching": True,
        "categories": [],  # No category filter
        "age_groups": [],  # No age filter
        "complexities": []  # No complexity filter
    }

    try:
        quiz_data = quiz_generator.generate_quiz(config)
        questions = quiz_data['questions']

        print(f"Requested 5 multi-case questions")
        print(f"Generated {len(questions)} questions")

        # Each question should be multi-case matching
        for i, question in enumerate(questions):
            assert question['question_type'] == 'multi_case_matching', f"Question {i+1} is not multi-case"
            assert len(question['cases']) == 3, f"Question {i+1} should have 3 cases, got {len(question['cases'])}"

        print("✓ Multi-case quiz generation test passed")
        return True

    except Exception as e:
        print(f"✗ Multi-case quiz generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_regular_question_count():
    """Test that regular quiz generation creates the correct number of questions."""

    # Initialize components
    data_loader = DataLoader('data')
    quiz_generator = QuizGenerator(data_loader)

    config = {
        "num_questions": 5,
        "multi_case_matching": False,
        "categories": [],  # No category filter
        "age_groups": [],  # No age filter
        "complexities": []  # No complexity filter
    }

    try:
        quiz_data = quiz_generator.generate_quiz(config)
        questions = quiz_data['questions']

        print(f"Requested 5 regular questions")
        print(f"Generated {len(questions)} questions")

        # Each question should be regular
        for i, question in enumerate(questions):
            assert question['question_type'] != 'multi_case_matching', f"Question {i+1} should not be multi-case"

        print("✓ Regular quiz generation test passed")
        return True

    except Exception as e:
        print(f"✗ Regular quiz generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing quiz generation logic...")

    success1 = test_multicase_question_count()
    success2 = test_regular_question_count()

    if success1 and success2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")