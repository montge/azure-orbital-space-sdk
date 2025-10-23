# ShipDetector-ONNX Test Suite

Comprehensive test infrastructure for the shipdetector-onnx payload application.

## Overview

This test suite provides unit and integration tests for the ship detection application, achieving 25%+ code coverage with focus on critical path functionality.

### Test Coverage

- **app_config.py**: 80%+ coverage (configuration loading, validation, type conversions)
- **object_detection.py**: 70%+ coverage (model initialization, inference, preprocessing)
- **ship_detection.py**: 100% coverage (dataclass functionality)
- **Overall**: ~25% total codebase coverage

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest fixtures
├── README.md                # This file
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_app_config.py          # 18 test cases
│   ├── test_object_detection.py    # 16 test cases
│   └── test_ship_detection.py      # 10 test cases
└── integration/             # Integration tests
    ├── __init__.py
    └── test_image_pipeline.py      # 5 test cases
```

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd /home/e/Development/azure-orbital-space/azure-orbital-space-sdk/samples/payloadapps/python/shipdetector-onnx
poetry install
```

### Run All Tests

```bash
# Run all tests with coverage report
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run with detailed output including print statements
poetry run pytest -vv -s
```

### Run Specific Test Categories

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run specific test file
poetry run pytest tests/unit/test_app_config.py

# Run specific test class
poetry run pytest tests/unit/test_app_config.py::TestAppConfigValidLoading

# Run specific test case
poetry run pytest tests/unit/test_app_config.py::TestAppConfigValidLoading::test_load_valid_config
```

### Generate Coverage Reports

```bash
# Generate terminal coverage report
poetry run pytest --cov=src/app --cov-report=term-missing

# Generate HTML coverage report
poetry run pytest --cov=src/app --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage report (for CI/CD)
poetry run pytest --cov=src/app --cov-report=xml

# Run tests with coverage and fail if below threshold
poetry run pytest --cov=src/app --cov-fail-under=25
```

## Test Organization

### Unit Tests

Unit tests focus on individual components in isolation with extensive mocking:

#### test_app_config.py (18 tests)
- **TestAppConfigValidLoading**: Valid configuration scenarios
  - Loading from JSON file
  - Detection labels parsing
  - Directory creation

- **TestAppConfigTypeConversions**: Type conversion logic
  - String to float conversion
  - String to int conversion
  - Unmapped field handling

- **TestAppConfigFileValidation**: File validation
  - Missing config file handling
  - Missing model file detection
  - Missing labels file detection

- **TestAppConfigErrorHandling**: Error scenarios
  - Invalid JSON parsing
  - Empty configuration files
  - Invalid type conversions

- **TestAppConfigEdgeCases**: Boundary conditions
  - Zero values
  - Negative values
  - Very large values
  - Empty and whitespace-padded labels

#### test_object_detection.py (16 tests)
- **TestObjectDetectionInitialization**: Model loading
  - ONNX session creation
  - Input/output property extraction
  - Metadata parsing (BGR, pixel range)
  - Multiple input validation

- **TestObjectDetectionPrediction**: Inference functionality
  - Image resizing to model input shape
  - NCHW format conversion
  - Pixel normalization
  - BGR channel ordering
  - Output dictionary structure

- **TestObjectDetectionErrorHandling**: Error cases
  - Multiple input rejection
  - Invalid image shape handling

#### test_ship_detection.py (10 tests)
- **TestShipDetectionInitialization**: Dataclass creation
  - Valid parameter initialization
  - Zero coordinates
  - Float probability handling
  - Property access
  - Large coordinate values

- **TestShipDetectionEdgeCases**: Edge cases
  - Negative coordinates
  - Zero width/height
  - Very small probabilities
  - Probabilities > 1.0
  - Multiple instances

### Integration Tests

Integration tests verify end-to-end workflows with controlled mocking:

#### test_image_pipeline.py (5 tests)
- **TestImageProcessingPipeline**: Complete pipeline flow
  - Small image processing (no chipping)
  - Confidence threshold filtering
  - Error propagation through pipeline

- **TestImageChipping**: Large image handling
  - Automatic image chipping for large inputs
  - Multiple chip processing

- **TestParsePredictions**: Prediction formatting
  - ONNX output to structured format conversion

## Fixtures

### Shared Fixtures (conftest.py)

The following fixtures are available in all tests:

- `temp_dir`: Temporary directory for test files
- `mock_app_config_data`: Sample configuration dictionary
- `mock_app_config_file`: Complete configuration file
- `mock_labels_file`: Sample labels file
- `mock_model_file`: Mock ONNX model file
- `mock_onnx_session`: Mock ONNX inference session
- `mock_onnx_model`: Mock ONNX model object
- `sample_image`: 640x480 test image
- `sample_small_image`: 416x416 test image
- `sample_geotiff_path`: Mock GeoTIFF file path
- `mock_predictions`: Sample prediction results
- `mock_detection_labels`: Sample label list
- `mock_complete_config_setup`: Complete setup with all files

## Adding New Tests

### 1. Create Test File

```python
"""
Unit tests for new_module.py module.

Brief description of what is being tested.
"""
from pathlib import Path
import pytest

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app.new_module import NewClass


class TestNewClass:
    """Tests for NewClass."""

    @pytest.mark.unit
    def test_something(self):
        """Test description following AAA pattern."""
        # Arrange
        test_data = "example"

        # Act
        result = NewClass(test_data)

        # Assert
        assert result is not None
```

### 2. Follow AAA Pattern

All tests should follow the Arrange-Act-Assert pattern:

- **Arrange**: Set up test data and mocks
- **Act**: Execute the code under test
- **Assert**: Verify expected outcomes

### 3. Use Descriptive Names

- Test function names: `test_<what>_<condition>_<expected_result>`
- Example: `test_config_loading_with_missing_file_raises_error`

### 4. Add Markers

```python
@pytest.mark.unit           # For unit tests
@pytest.mark.integration    # For integration tests
@pytest.mark.slow          # For slow-running tests
```

### 5. Document Complex Tests

Add detailed docstrings for complex test cases explaining:
- What is being tested
- Why it's important
- Any special setup required

## Mocking Strategy

### General Principles

1. **Mock External Dependencies**: Always mock file I/O, network calls, and external libraries
2. **Mock at Boundaries**: Mock at the integration points, not internal implementation
3. **Use unittest.mock**: Prefer `unittest.mock.patch` and `Mock` objects
4. **Fixture-Based Mocks**: Create reusable mocks in conftest.py

### Common Mocking Patterns

#### Mock File System

```python
@patch('builtins.open', mock_open(read_data='{"key": "value"}'))
def test_file_reading():
    # Test code that reads files
    pass
```

#### Mock ONNX Runtime

```python
@patch('app.object_detection.onnxruntime.InferenceSession')
def test_model_inference(mock_session_class, mock_onnx_session):
    mock_session_class.return_value = mock_onnx_session
    # Test code
```

#### Mock Configuration

```python
def test_with_config(mock_complete_config_setup):
    config_path, inbox, outbox = mock_complete_config_setup
    # Test code
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: |
    cd samples/payloadapps/python/shipdetector-onnx
    poetry install

- name: Run tests with coverage
  run: |
    cd samples/payloadapps/python/shipdetector-onnx
    poetry run pytest --cov=src/app --cov-report=xml --cov-fail-under=25

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./samples/payloadapps/python/shipdetector-onnx/coverage.xml
```

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Tests add `src` to `sys.path`. Ensure you're running from the correct directory:

```bash
cd /home/e/Development/azure-orbital-space/azure-orbital-space-sdk/samples/payloadapps/python/shipdetector-onnx
poetry run pytest
```

#### Fixture Not Found

**Problem**: `fixture 'mock_onnx_session' not found`

**Solution**: Ensure conftest.py is in the tests directory and contains the fixture.

#### Coverage Not Collected

**Problem**: Coverage shows 0%

**Solution**: Verify the source path in pytest.ini and .coveragerc:

```ini
[run]
source = src/app
```

#### Tests Hang or Timeout

**Problem**: Tests never complete

**Solution**: Check for infinite loops or missing mocks for blocking calls (e.g., `time.sleep`):

```python
@patch('time.sleep')  # Mock out sleeps
def test_something(mock_sleep):
    # Test code
```

## Best Practices

1. **Keep Tests Fast**: Use mocks to avoid slow operations (file I/O, network, ML inference)
2. **Test One Thing**: Each test should verify a single behavior
3. **Make Tests Independent**: Tests should not depend on execution order
4. **Use Meaningful Assertions**: Prefer specific assertions over generic ones
5. **Clean Up Resources**: Use fixtures and context managers for cleanup
6. **Avoid Test Logic**: Tests should be simple and straightforward
7. **Mock External Dependencies**: Never hit real file systems, networks, or APIs
8. **Test Edge Cases**: Include boundary values, empty inputs, and error conditions

## Coverage Goals

### Phase 1 (Current): Foundation - 25% Coverage
- ✅ app_config.py: 80%+
- ✅ object_detection.py: 70%+
- ✅ ship_detection.py: 100%
- ⏳ image_processor.py: 15%
- ⏳ main.py: 0%

### Phase 2 (Future): Expansion - 50% Coverage
- image_processor.py: 60%+
- main.py: 40%+
- Additional edge cases
- Performance tests

### Phase 3 (Future): Comprehensive - 75%+ Coverage
- Complete image_processor.py coverage
- End-to-end integration tests with real images
- Load and stress testing
- Security testing

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure new code has 70%+ coverage
3. Add integration tests for new workflows
4. Update this README if adding new test patterns
5. Run full test suite before committing

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Azure Orbital Space SDK Documentation](../../../../../../docs/)
