#!/usr/bin/env python3
"""
Main Test Runner for TutorDraw
Executes all test suites in proper order
"""

import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Discover and add all tests
    start_dir = os.path.dirname(__file__)
    suite.addTests(loader.discover(start_dir, pattern='test_*.py'))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)