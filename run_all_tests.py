#!/usr/bin/env python3
"""
Test runner for all test suites in the slackbot-poc project.
"""

import unittest
import sys
import os

# Import test modules
import test_csv_processor
import test_server_integration
import test_file_upload


def run_all_tests():
    """Run all test suites and return results."""
    print("Slack CSV Bot - Complete Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    suite.addTests(loader.loadTestsFromModule(test_csv_processor))
    suite.addTests(loader.loadTestsFromModule(test_server_integration))
    suite.addTests(loader.loadTestsFromModule(test_file_upload))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOVERALL RESULT: {'✓ PASS' if success else '✗ FAIL'}")
    
    return success


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)