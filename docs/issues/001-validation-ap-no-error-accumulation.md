# Issue 001: Validation.ap() Does Not Accumulate Errors

**Severity:** Critical
**Status:** Open
**Location:** `better_py/monads/validation.py:177-198`
**Priority:** P0 - Must Fix

## Description

The `ap` method in the `Validation` monad is supposed to accumulate errors from both Validations when both are Invalid. This is the core feature that distinguishes `Validation` from `Result` - the ability to collect multiple validation errors and report them all at once.

However, the current implementation only returns errors from the first Invalid validation encountered:

```python
def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
    if self._errors:
        return Validation(None, self._errors)  # Only returns self._errors
    if other._errors:
        return Validation(None, other._errors)  # Only returns other._errors
    # ...
```

## Impact

This breaks the core promise of the Validation monad. Users cannot rely on error accumulation when using applicative patterns, which is the primary use case for Validation over Result.

## Example

```python
# Expected behavior: accumulate errors
invalid_fn = Validation.invalid(["error1"])
invalid_value = Validation.invalid(["error2"])
result = invalid_fn.ap(invalid_value)

# Current result: Invalid(['error1'])
# Expected result: Invalid(['error1', 'error2'])
```

## Test Case

The existing test at `tests/monads/test_validation.py:175-180` does not verify error accumulation:

```python
def test_ap_both_invalid(self):
    """ap should return Invalid when both are Invalid."""
    invalid_fn = Validation.invalid(["error1"])
    invalid_value = Validation.invalid(["error2"])
    result = invalid_fn.ap(invalid_value)
    assert result.is_invalid()
    # Missing: assert result.unwrap_errors() == ["error1", "error2"]
```

## Proposed Fix

```python
def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
    """Apply a Validation containing a function to this Validation.

    Returns:
        Valid(f(value)) if both are Valid,
        Invalid with accumulated errors otherwise
    """
    if self._errors and other._errors:
        # Accumulate errors from both sides
        return Validation(None, self._errors + other._errors)
    if self._errors:
        return Validation(None, self._errors)
    if other._errors:
        return Validation(None, other._errors)
    # Both are valid
    assert self._value is not None
    assert other._value is not None
    return Validation(other._value(self._value), [])
```

## Related Issues

- Issue #002: State monad double execution bug
- Issue #003: IO/Task equality side effects

## References

- Functional Programming: Validation should accumulate errors
- Haskell's Validation/Data.Validation type
- Cats Scala Validated
