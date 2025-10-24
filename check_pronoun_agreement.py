#!/usr/bin/env python3
"""
Script to check and fix pronoun/sex/gender agreement in case narratives.
"""

import json
import re
from typing import Dict, List, Tuple

def extract_gender_from_narrative(narrative: str) -> str | None:
    """Extract gender from the narrative description."""
    # Look for patterns like "X-year-old male/female/boy/girl/man/woman"
    patterns = [
        r'(\d+)-year-old\s+(male|female|boy|girl|man|woman)',
        r'(\d+)\s+year\s+old\s+(male|female|boy|girl|man|woman)',
        r'(male|female|boy|girl|man|woman)\s+aged\s+(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, narrative, re.IGNORECASE)
        if match:
            gender_term = match.group(2) if len(match.groups()) > 1 else match.group(1)
            gender_term = gender_term.lower()
            # Normalize gender terms
            if gender_term in ['male', 'boy', 'man']:
                return 'male'
            elif gender_term in ['female', 'girl', 'woman']:
                return 'female'

    return None

def get_correct_pronouns(gender: str) -> Dict[str, str]:
    """Get the correct pronouns for a given gender."""
    if gender == 'male':
        return {
            'subject': 'he',
            'object': 'him',
            'possessive': 'his',
            'reflexive': 'himself'
        }
    elif gender == 'female':
        return {
            'subject': 'she',
            'object': 'her',
            'possessive': 'her',
            'reflexive': 'herself'
        }
    else:
        return {}

def find_pronoun_errors(narrative: str, gender: str) -> List[Tuple[str, str, int]]:
    """Find pronoun errors in the narrative."""
    if not gender:
        return []

    correct_pronouns = get_correct_pronouns(gender)
    errors = []

    # Define incorrect pronouns for each gender
    if gender == 'male':
        incorrect_patterns = [
            (r'\bshe\b', 'he'),
            (r'\bher\b(?!\s+sexual)', 'his'),  # Avoid matching "her sexual" which is correct
            (r'\bherself\b', 'himself'),
        ]
    elif gender == 'female':
        incorrect_patterns = [
            (r'\bhe\b', 'she'),
            (r'\bhis\b', 'her'),
            (r'\bhimself\b', 'herself'),
        ]
    else:
        return []

    for pattern, correct in incorrect_patterns:
        matches = re.finditer(pattern, narrative, re.IGNORECASE)
        for match in matches:
            # Skip if this is part of a compound word or specific context
            start = max(0, match.start() - 20)
            end = min(len(narrative), match.end() + 20)
            context = narrative[start:end].lower()

            # Skip certain contexts where pronouns might be used differently
            skip_contexts = [
                'wife', 'husband', 'partner', 'spouse', 'girlfriend', 'boyfriend',
                'mother', 'father', 'parent', 'daughter', 'son', 'child',
                'family', 'friend', 'colleague', 'doctor', 'therapist',
                'teacher', 'professor', 'boss', 'coworker'
            ]

            if any(skip_word in context for skip_word in skip_contexts):
                continue

            errors.append((match.group(), correct, match.start()))

    return errors

def fix_pronoun_errors(narrative: str, errors: List[Tuple[str, str, int]]) -> str:
    """Fix pronoun errors in the narrative."""
    # Sort errors by position (reverse order to avoid offset issues)
    errors.sort(key=lambda x: x[2], reverse=True)

    fixed_narrative = narrative
    for incorrect, correct, pos in errors:
        # Replace the incorrect pronoun with correct one
        fixed_narrative = fixed_narrative[:pos] + correct + fixed_narrative[pos + len(incorrect):]

    return fixed_narrative

def main():
    """Main function to check and fix pronoun agreement."""

    # Load cases
    with open('data/cases.json', 'r') as f:
        cases = json.load(f)

    total_cases = len(cases)
    cases_with_errors = 0
    total_errors = 0
    fixed_cases = 0

    print(f"Checking pronoun agreement in {total_cases} cases...")

    for case in cases:
        narrative = case.get('narrative', '')
        case_id = case.get('case_id', 'Unknown')

        # Extract gender from narrative
        gender = extract_gender_from_narrative(narrative)

        if not gender:
            print(f"Warning: Could not determine gender for case {case_id}")
            continue

        # Find pronoun errors
        errors = find_pronoun_errors(narrative, gender)

        if errors:
            cases_with_errors += 1
            total_errors += len(errors)

            print(f"\nCase {case_id} ({gender}): {len(errors)} errors")
            for incorrect, correct, pos in errors:
                start = max(0, pos - 30)
                end = min(len(narrative), pos + 30)
                context = narrative[start:end]
                print(f"  '{incorrect}' -> '{correct}' at position {pos}: ...{context}...")

            # Fix the errors
            original_narrative = narrative
            fixed_narrative = fix_pronoun_errors(narrative, errors)

            if fixed_narrative != original_narrative:
                case['narrative'] = fixed_narrative
                fixed_cases += 1
                print(f"  ✓ Fixed narrative for case {case_id}")

    # Save the updated cases
    if fixed_cases > 0:
        with open('data/cases.json', 'w') as f:
            json.dump(cases, f, indent=2)
        print(f"\n✓ Saved {fixed_cases} fixed cases to data/cases.json")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Total cases checked: {total_cases}")
    print(f"Cases with pronoun errors: {cases_with_errors}")
    print(f"Total pronoun errors found: {total_errors}")
    print(f"Cases fixed: {fixed_cases}")

    if cases_with_errors > 0:
        error_rate = (cases_with_errors / total_cases) * 100
        print(f"{error_rate:.1f}% of cases had pronoun errors")
    else:
        print("🎉 No pronoun agreement errors found!")

if __name__ == "__main__":
    main()