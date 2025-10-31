#!/usr/bin/env python3
"""Quick smoke test to verify core functionality works."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    print("=" * 60)
    print("SMOKE TEST: Core Functionality")
    print("=" * 60)

    # Test 1: Data Loader
    print("\n[1/5] Testing DataLoader...")
    from modules.data_loader import DataLoader
    loader = DataLoader('data')
    cases = loader.load_cases()
    diagnoses = loader.load_diagnoses()
    print(f"  ✓ Loaded {len(cases)} cases and {len(diagnoses)} diagnoses")

    # Test 2: Quiz Generator
    print("\n[2/5] Testing QuizGenerator...")
    from modules.quiz_generator import QuizGenerator
    generator = QuizGenerator(loader)
    quiz = generator.generate_quiz({'num_questions': 3, 'num_choices': 4})
    print(f"  ✓ Generated quiz with {len(quiz['questions'])} questions")

    # Test 3: Scoring
    print("\n[3/5] Testing Scoring...")
    from modules.scoring import Scoring, ScoringMode
    scoring = Scoring(scoring_mode=ScoringMode.STRICT)
    scoring.start_quiz_session(quiz)
    scoring.record_answer(1, quiz['questions'][0]['correct_answer'], 10.0)
    stats = scoring.calculate_scores()
    print(f"  ✓ Scoring works: {stats.correct_answers}/{stats.total_questions} correct")

    # Test 4: User Manager
    print("\n[4/5] Testing UserManager...")
    from modules.user_manager import UserManager
    user_mgr = UserManager('data')
    print(f"  ✓ UserManager initialized")

    # Test 5: Progression
    print("\n[5/5] Testing UserProgress...")
    from modules.progression import UserProgress
    progress = UserProgress("test_user", "Test User")
    progress.add_xp(100, "quiz_completion")
    print(f"  ✓ UserProgress works: Level {progress.level}, XP {progress.total_xp}")

    print("\n" + "=" * 60)
    print("✓ ALL CORE MODULES WORKING!")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"\n✗ SMOKE TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
