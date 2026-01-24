# Issue 012: Missing Test Coverage for Edge Cases and Error Conditions

**Severity:** Medium
**Status:** Open
**Location:** Various test files
**Priority:** P2 - Medium Priority

## Description

The test suite has several gaps in coverage, particularly for edge cases, error conditions, and verifying correct behavior in failure scenarios.

## Missing Test Coverage

### 1. Validation.ap Error Accumulation

**Location:** `tests/monads/test_validation.py:175-180`

**Current Test:**
```python
def test_ap_both_invalid(self):
    """ap should return Invalid when both are Invalid."""
    invalid_fn = Validation.invalid(["error1"])
    invalid_value = Validation.invalid(["error2"])
    result = invalid_fn.ap(invalid_value)
    assert result.is_invalid()
    # Missing: verify error accumulation!
```

**Missing Test:**
```python
def test_ap_accumulates_errors(self):
    """ap should accumulate errors from both Invalid validations."""
    invalid_fn = Validation.invalid(["error1", "error2"])
    invalid_value = Validation.invalid(["error3"])
    result = invalid_fn.ap(invalid_value)

    assert result.is_invalid()
    assert result.unwrap_errors() == ["error1", "error2", "error3"]
```

### 2. State Monad Double Execution

**Location:** No test exists

**Missing Test:**
```python
def test_map_executes_once(self):
    """map should execute state transformation exactly once."""
    count = [0]

    def counting_state(s):
        count[0] += 1
        return (s, s)

    state = State(counting_state)
    mapped = state.map(lambda x: x)
    result = mapped.run(0)

    assert count[0] == 1, f"Expected 1 execution, got {count[0]}"
```

### 3. IO/Task Equality Side Effects

**Location:** No test exists

**Missing Test:**
```python
def test_io_equality_no_side_effects(self):
    """IO equality should not execute the computation."""
    count = [0]
    io1 = IO(lambda: count.append(1) or count[0])
    io2 = IO(lambda: count.append(1) or count[0])

    result = io1 == io2

    # Side effects should not occur during equality check
    assert count[0] == 0, "Equality check executed side effects"
```

### 4. Writer Non-Monoid Log Types

**Location:** No test exists

**Missing Test:**
```python
def test_writer_fails_with_non_monoid():
    """Writer should fail gracefully with non-monoid log types."""
    class BadLog:
        def __init__(self, value: int):
            self.value = value

        # No __add__ defined

    with pytest.raises(AttributeError):
        Writer(BadLog(1), lambda: (BadLog(2), "value"))
```

### 5. PersistentMap.map_keys Collisions

**Location:** No test exists

**Missing Test:**
```python
def test_map_keys_collision_behavior(self):
    """map_keys should handle key collisions predictably."""
    m = PersistentMap.of({1: 'a', 2: 'b', 3: 'c'})

    # Keys 1 and 2 both map to 0
    result = m.map_keys(lambda k: k // 2)

    # Current: Last value wins (2 -> 'b' overwrites 1 -> 'a')
    # But this isn't tested or documented!
    assert result.to_dict() == {0: 'c', 1: 'b'}
    # Note: 'a' was silently lost
```

### 6. Maybe.from_value with None

**Location:** Limited test coverage

**Missing Tests:**
```python
def test_from_value_with_none():
    """from_value should treat None as Nothing."""
    maybe = Maybe.from_value(None)
    assert maybe.is_nothing()

def test_cannot_distinguish_none_from_nothing():
    """Cannot distinguish Some(None) from Nothing (known limitation)."""
    # This is a known issue (Issue #008)
    maybe1 = Maybe.from_value(None)
    maybe2 = Maybe.nothing()
    assert maybe1 == maybe2  # Cannot distinguish
```

### 7. Property-Based Test Gaps

**Missing Properties:**

```python
# State monad associativity property
def test_state_flat_map_associativity_property():
    """flat_map should satisfy associativity law."""
    # This would catch the double-execution bug!

# Validation applicative laws
def test_validation_applicative_laws():
    """Validation should satisfy applicative laws."""
    # This would catch the ap bug!

# Writer monad laws
def test_writer_monoid_laws():
    """Writer log combination should satisfy monoid laws."""
```

### 8. Performance Regression Tests

**Location:** No performance tests exist

**Missing Tests:**
```python
def test_persistentlist_append_performance():
    """append should have reasonable performance."""
    import time

    lst = PersistentList.of(*range(1000))
    start = time.time()

    for i in range(100):
        lst = lst.append(i)

    elapsed = time.time() - start
    assert elapsed < 0.1, f"append too slow: {elapsed}s"

def test_persistentlist_drop_performance():
    """drop should not create intermediate lists."""
    # Test that drop doesn't allocate excessive memory
```

### 9. Error Message Format

**Location:** Various unwrap() methods

**Missing Tests:**
```python
def test_unwrap_error_message_format():
    """unwrap() errors should have consistent message format."""
    result = Result.error("test error")

    with pytest.raises(ValueError) as exc_info:
        result.unwrap()

    assert "test error" in str(exc_info.value)
```

### 10. Edge Cases Not Tested

**Missing Tests:**

```python
# Empty collections
def test_persistentlist_empty_operations():
    """Operations on empty list should work correctly."""
    lst = PersistentList.empty()
    assert lst.reverse() == lst
    assert lst.drop(10) == lst
    assert lst.take(0) == lst

# Large collections
def test_persistentlist_large_operations():
    """Operations should work with large lists."""
    lst = PersistentList.of(*range(10000))
    assert lst.length() == 10000

# Special values
def test_maybe_with_special_values():
    """Maybe should handle False, 0, '' correctly."""
    assert Maybe.some(0).is_some()
    assert Maybe.some(False).is_some()
    assert Maybe.some('').is_some()
```

## Recommended Actions

1. **Add missing test cases** for all identified gaps
2. **Run mutation testing** with `mutmut` or `pymut` to find untested code paths
3. **Add property-based tests** for all monad laws
4. **Add performance benchmarks** with pytest-benchmark
5. **Add integration tests** for common usage patterns
6. **Increase coverage target** to 90%+ (currently unknown)

## Tools to Use

1. **pytest-cov**: Coverage reporting
   ```bash
   pytest --cov=better_py --cov-report=html
   ```

2. **pytest-benchmark**: Performance regression tests
   ```python
   def test_append_performance(benchmark):
       lst = PersistentList.of(*range(100))
       result = benchmark(lambda: lst.append(0))
   ```

3. **hypothesis**: Property-based testing
   ```python
   @given(st.lists(st.integers()))
   def test_persistentlist_roundtrip(items):
       lst = PersistentList.of(*items)
       assert lst.to_list() == items
   ```

4. **mutmut**: Mutation testing
   ```bash
   mutmut run better_py
   ```

## Related Issues

- Issue #001: Validation.ap() doesn't accumulate errors
- Issue #002: State monad double execution
- Issue #003: IO/Task equality side effects

## References

- pytest documentation
- Hypothesis property testing
- Mutation testing best practices
