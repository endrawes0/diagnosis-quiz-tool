#!/usr/bin/env python3
"""
Test script to verify multi-case matching fixes.
"""

import requests
import json

def test_multicase_quiz_generation():
    """Test that multi-case quiz generation creates the correct number of questions."""

    # Test configuration for 5 multi-case questions
    config = {
        "num_questions": 5,
        "multi_case_matching": True,
        "categories": ["Depressive Disorders", "Anxiety Disorders"],
        "age_groups": ["adult"],
        "complexities": ["basic", "intermediate"]
    }

    try:
        response = requests.post('http://localhost:5000/api/quiz/generate', json=config)
        response.raise_for_status()

        quiz_data = response.json()
        questions = quiz_data['quiz_data']['questions']

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
        return False

def test_regular_quiz_generation():
    """Test that regular quiz generation still works."""

    config = {
        "num_questions": 5,
        "multi_case_matching": False,
        "categories": ["Depressive Disorders"],
        "age_groups": ["adult"],
        "complexities": ["basic"]
    }

    try:
        response = requests.post('http://localhost:5000/api/quiz/generate', json=config)
        response.raise_for_status()

        quiz_data = response.json()
        questions = quiz_data['quiz_data']['questions']

        print(f"Requested 5 regular questions")
        print(f"Generated {len(questions)} questions")

        # Each question should be regular
        for i, question in enumerate(questions):
            assert question['question_type'] != 'multi_case_matching', f"Question {i+1} should not be multi-case"

        print("✓ Regular quiz generation test passed")
        return True

    except Exception as e:
        print(f"✗ Regular quiz generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing multi-case fixes...")

    success1 = test_multicase_quiz_generation()
    success2 = test_regular_quiz_generation()

    if success1 and success2:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")