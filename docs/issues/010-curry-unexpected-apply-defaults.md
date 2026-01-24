# Issue 010: curry() Uses apply_defaults() Unexpectedly

**Severity:** Medium
**Status:** Open
**Location:** `better_py/curry.py:46`
**Priority:** P2 - Medium Priority

## Description

The `curry` function calls `apply_defaults()` unconditionally, which means default values are filled in even when not all arguments are provided. This leads to unexpected behavior where curried functions may return results instead of waiting for more arguments.

## Current Implementation

```python
def curry(func: Callable[..., T]) -> Callable[..., T]:
    """Convert a function into a curried function."""
    sig = signature(func)
    total_params = len(sig.parameters)

    def curried(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()  # <--- Problematic line
        # ...
```

## Problem

When a function has default parameters, `apply_defaults()` fills them in early, causing the curried function to execute prematurely instead of waiting for all non-default arguments.

## Example

```python
def func(a, b, c=10, d=20):
    return a + b + c + d

curried = curry(func)

# User expects: waits for a and b
# Actual: applies defaults for c and d, executes with just a and b
result = curried(1, 2)

# Expected: curry(lambda b: curry(lambda c: func(1, b, c)))
# Actual: func(1, 2, 10, 20) = 33
```

## Why This Is Wrong

Currying should only require arguments without defaults. Default parameters should remain as optional parameters that can be provided later or left to their defaults at final call time.

### Expected Behavior

```python
def func(a, b, c=10, d=20):
    return a + b + c + d

curried = curry(func)

# Should require a and b, but allow optional c and d
step1 = curried(1)        # Still curried, waiting for b
step2 = step1(2)         # Now have a and b, still curried (can provide c, d)
result1 = step2()        # Uses defaults: func(1, 2, 10, 20) = 33
result2 = step2(5)       # Provide c: func(1, 2, 5, 20) = 28
result3 = step2(5, 3)    # Provide c and d: func(1, 2, 5, 3) = 11
```

## Impact

1. **Unexpected Early Execution:** Functions execute when all non-default arguments are provided
2. **Cannot Override Defaults Selectively:** Cannot provide some defaults while leaving others
3. **Violates Curry Semantics:** Currying should wait for all required arguments

## Proposed Fix

Remove `apply_defaults()` or make it conditional:

### Option 1: Remove apply_defaults (Recommended)

```python
def curry(func: Callable[..., T]) -> Callable[..., T]:
    """Convert a function into a curried function."""
    sig = signature(func)

    def curried(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        # Removed: bound.apply_defaults()

        if len(bound.arguments) >= total_params:
            return func(*bound.args, **bound.kwargs)

        @wraps(func)
        def waiting(*more_args, **more_kwargs):
            new_args = args + more_args
            new_kwargs = {**kwargs, **more_kwargs}
            return curried(*new_args, **new_kwargs)

        return waiting

    return curried
```

### Option 2: Track Required Parameters

```python
def curry(func: Callable[..., T]) -> Callable[..., T]:
    """Convert a function into a curried function."""
    sig = signature(func)

    # Count only required parameters (no defaults)
    required_params = sum(
        1 for p in sig.parameters.values()
        if p.default is p.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    )

    def curried(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()

        # Only execute when all required params are provided
        provided = len(bound.arguments)
        if provided >= required_params:
            # Allow extra calls with more args to override defaults
            return func(*bound.args, **bound.kwargs)

        @wraps(func)
        def waiting(*more_args, **more_kwargs):
            new_args = args + more_args
            new_kwargs = {**kwargs, **more_kwargs}
            return curried(*new_args, **new_kwargs)

        return waiting

    return curried
```

### Option 3: Add Parameter to Control Behavior

```python
def curry(func: Callable[..., T], respect_defaults: bool = True) -> Callable[..., T]:
    """Convert a function into a curried function.

    Args:
        func: Function to curry
        respect_defaults: If True (default), don't fill defaults early.
                        If False, apply defaults when possible (current behavior).
    """
    sig = signature(func)

    def curried(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)

        if not respect_defaults:
            bound.apply_defaults()

        if len(bound.arguments) >= total_params:
            return func(*bound.args, **bound.kwargs)

        @wraps(func)
        def waiting(*more_args, **more_kwargs):
            new_args = args + more_args
            new_kwargs = {**kwargs, **more_kwargs}
            return curried(*new_args, **new_kwargs)

        return waiting

    return curried
```

## Recommendation

**Option 1** (Remove `apply_defaults()`) is the cleanest solution:

1. Curried functions wait for all required arguments
2. Default parameters can still be provided explicitly
3. Defaults are applied at final call time, not intermediate calls

## Test Cases Needed

```python
def test_curry_with_defaults():
    """curry should not apply defaults early."""

    def func(a, b, c=10, d=20):
        return a + b + c + d

    curried = curry(func)

    # Should wait for both a and b
    partial = curried(1)
    assert callable(partial), "Should still be curried"

    # Should wait for b
    result = partial(2)
    assert result == 33  # 1 + 2 + 10 + 20

    # Should allow overriding c
    result2 = partial(2, 5)
    assert result2 == 28  # 1 + 2 + 5 + 20

    # Should allow overriding c and d
    result3 = partial(2, 5, 3)
    assert result3 == 11  # 1 + 2 + 5 + 3
```

## Related Issues

- Issue #008: Maybe cannot contain None
- Issue #004: Performance issues in collections

## References

- Currying semantics in functional languages
- Python's inspect.signature documentation
- functools.partial behavior with defaults
