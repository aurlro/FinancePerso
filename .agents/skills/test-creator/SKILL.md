# Test Creator Skill

> Creates and maintains tests for FinancePerso

## Quick Commands

```bash
# Run tests
make test           # Essential tests (~5s)
make test-all       # All tests with coverage (~30s)

# Create new test
python scripts/create_test.py --module MODULE_NAME
```

## Test Structure

```
tests/
├── test_essential.py       # ✅ Critical tests (always run)
├── test_integration.py     # Integration tests
├── conftest.py            # Shared fixtures
├── db/                    # Database layer tests
├── ui/                    # UI component tests
├── ai/                    # AI module tests
└── e2e/                   # End-to-end tests
```

## Writing Tests

### Essential Test Template
```python
def test_feature_name():
    """Short description of what's tested."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| modules/db/ | 60% | 80% |
| modules/core/ | 40% | 70% |
| modules/ai/ | 30% | 60% |
| modules/ui/ | 20% | 50% |

## Testing Best Practices

1. **Test behavior, not implementation**
2. **One assert per test** (when possible)
3. **Use fixtures** for common setup
4. **Mock external services** (AI APIs)
5. **Test edge cases** (empty inputs, None, etc.)
