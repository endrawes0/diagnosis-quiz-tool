#!/usr/bin/env python3
"""
Simple test runner for the diagnosis quiz tool when pytest is not available.
"""

import sys
import traceback
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def run_test_module(module_name, test_class_name):
    """Run tests for a specific module."""
    try:
        # Import the test module
        module = __import__(f"tests.{module_name}", fromlist=[module_name])
        test_class = getattr(module, test_class_name)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        print(f"\n{'='*60}")
        print(f"Running {module_name}.{test_class_name}")
        print(f"{'='*60}")
        
        passed = 0
        failed = 0
        
        # Create test instance
        test_instance = test_class()
        
        # Run each test method
        for method_name in test_methods:
            try:
                print(f"  Running {method_name}... ", end="")
                method = getattr(test_instance, method_name)
                
                # Check if method needs fixtures
                import inspect
                sig = inspect.signature(method)
                if len(sig.parameters) > 0:
                    print("SKIPPED (requires fixtures)")
                    continue
                
                method()
                print("PASSED")
                passed += 1
                
            except Exception as e:
                print(f"FAILED: {e}")
                failed += 1
                traceback.print_exc()
        
        print(f"\nResults: {passed} passed, {failed} failed")
        return failed == 0
        
    except Exception as e:
        print(f"Failed to load {module_name}: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Running diagnosis quiz tool tests...")
    
    test_modules = [
        ("test_data_loader", "TestDataLoader"),
        ("test_quiz_generator", "TestQuizGenerator"),
        ("test_scoring", "TestScoring"),
        ("test_integration", "TestIntegration")
    ]
    
    total_passed = 0
    total_failed = 0
    
    for module_name, test_class_name in test_modules:
        try:
            success = run_test_module(module_name, test_class_name)
            if success:
                total_passed += 1
            else:
                total_failed += 1
        except Exception as e:
            print(f"Error running {module_name}: {e}")
            total_failed += 1
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Modules passed: {total_passed}")
    print(f"Modules failed: {total_failed}")
    print(f"Total: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total_failed} module(s) had failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())