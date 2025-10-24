#!/usr/bin/env python3
"""Test script for API endpoints without authentication."""

import sys
import time
import subprocess
import requests
from pathlib import Path

# Ensure we're using the venv python
VENV_PYTHON = Path(__file__).parent / "venv" / "bin" / "python"

def test_api_endpoints():
    """Test key API endpoints."""
    print("=" * 60)
    print("API ENDPOINT TESTS (No Auth Mode)")
    print("=" * 60)

    base_url = "http://localhost:5000/api"

    tests = [
        ("Health Check", f"{base_url}/health", "GET"),
        ("Config Check", f"{base_url}/config", "GET"),
        ("Browse Cases", f"{base_url}/cases?limit=5", "GET"),
        ("Get Categories", f"{base_url}/cases/categories", "GET"),
        ("Generate Quiz", f"{base_url}/quiz/generate", "POST", {
            "num_questions": 3,
            "num_choices": 4
        }),
    ]

    passed = 0
    failed = 0

    for test_name, url, method, *data in tests:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data[0] if data else {}, timeout=5)

            if response.status_code in [200, 201]:
                print(f"✓ {test_name}: {response.status_code}")
                passed += 1
            else:
                print(f"✗ {test_name}: {response.status_code} - {response.text[:100]}")
                failed += 1
        except requests.exceptions.ConnectionError:
            print(f"✗ {test_name}: Connection refused (is server running?)")
            failed += 1
        except Exception as e:
            print(f"✗ {test_name}: {str(e)}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)
