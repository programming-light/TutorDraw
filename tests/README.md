# TutorDraw Test Suite

Industry-grade testing organization for the TutorDraw application.

## Directory Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions  
├── e2e/           # End-to-end tests simulating user workflows
├── run_tests.py   # Main test runner script
└── README.md      # This file
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual functions and classes in isolation
- Fast execution, no external dependencies
- Focus on business logic and core functionality

### Integration Tests (`tests/integration/`)
- Test interactions between multiple components
- May involve file I/O, network calls, or external services
- Verify component collaboration works correctly

### End-to-End Tests (`tests/e2e/`)
- Full application workflow simulations
- Test complete user journeys from start to finish
- Closest to real user experience

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python -m unittest discover tests/unit

# Integration tests only  
python -m unittest discover tests/integration

# E2E tests only
python -m unittest discover tests/e2e
```

### Run Individual Test Files
```bash
python -m unittest tests/unit/test_themes.py
python -m unittest tests/integration/test_window.py
```

## Test File Naming Convention

- Unit tests: `test_*.py` in `tests/unit/`
- Integration tests: `test_*.py` in `tests/integration/`
- E2E tests: `test_*.py` in `tests/e2e/`

## Best Practices

1. **Isolation**: Unit tests should not depend on external systems
2. **Speed**: Unit tests should run quickly (< 100ms each)
3. **Clarity**: Test names should clearly describe what is being tested
4. **Coverage**: Aim for comprehensive test coverage of core functionality
5. **Reliability**: Tests should produce consistent results

## Continuous Integration

This test suite is designed to integrate with CI/CD pipelines for automated testing on every commit.