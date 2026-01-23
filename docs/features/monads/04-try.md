# Try - Exception Handling

Convert exceptions into values for safe error handling.

## Overview

`Try` captures exceptions as values:
- `Success(value)` - Operation succeeded
- `Failure(exception)` - Operation raised exception

## Basic Usage

```python
from mfn import Try, Success, Failure

# Create Try from callable
result = Try(lambda: 10 / 2)
# Success(5.0)

result = Try(lambda: 10 / 0)
# Failure(ZeroDivisionError)

# Use constructors
success = Success(42)
failure = Failure(ValueError("Invalid"))
```

## Transformation

```python
from mfn import Try

# Map: Transform success value
result = Success(5).map(lambda x: x * 2)
# Success(10)

# Map on Failure skips function
result = Failure(ValueError("fail")).map(lambda x: x * 2)
# Failure(ValueError("fail"))

# Map error: Transform exception
result = Failure(ValueError("fail")).map_error(lambda e: TypeError(str(e)))
# Failure(TypeError("fail"))

# Then: Chain with Try-returning function
def risky_divide(x: int) -> Try:
    return Try(lambda: 100 / x)

result = Success(5).then(risky_divide)
# Success(20.0)

result = Success(0).then(risky_divide)
# Failure(ZeroDivisionError)
```

## Pipe Operators

```python
from mfn import Try

def parse_int(s: str) -> Try:
    return Try(lambda: int(s))

def divide_by(x: int) -> Try:
    return Try(lambda: 100 / x)

# Chain with pipe
result = (
    Success("10")
    | parse_int       # Success(10)
    | divide_by       # Success(10.0)
)

# Error in chain
result = (
    Success("invalid")
    | parse_int       # Failure(ValueError)
    | divide_by       # Skipped
)
```

## Error Handling

```python
from mfn import Try

result = Failure(ValueError("error"))

# Get value or default
value = result.unwrap_or(0)      # 0
value = Success(42).unwrap_or(0)  # 42

# Get value or raise (original exception)
value = Success(42).unwrap()      # 42
value = Failure(ValueError("fail")).unwrap()  # Raises ValueError

# Recover from error
result = Failure(ValueError("fail")).recover(lambda _: 0)
# Success(0)

# Recover based on exception type
result = (
    Failure(ValueError("fail"))
    .recover_if(ValueError, lambda _: 1)
    .recover_if(KeyError, lambda _: 2)
)
# Success(1)

result = (
    Failure(KeyError("missing"))
    .recover_if(ValueError, lambda _: 1)
    .recover_if(KeyError, lambda _: 2)
)
# Success(2)
```

## Resource Management

```python
from mfn import Try
from contextlib import contextmanager

@contextmanager
def resource():
    """Managed resource"""
    r = open("file.txt", "r")
    try:
        yield r
    finally:
        r.close()

def read_file():
    """Read file with Try"""

    def inner():
        with resource() as f:
            return f.read()

    return Try(inner)

result = read_file()
# Success(content) or Failure(IOError)
```

## Raising Exceptions

```python
from mfn import Try

# Convert Try to exception
success = Success(42)
value = success.raise_if_failed()  # Returns 42

failure = Failure(ValueError("error"))
failure.raise_if_failed()  # Raises ValueError

# Or with custom exception
result = Failure("error").raise_error_if_failed(RuntimeError)
# Raises RuntimeError("error")
```

## Conversion

```python
from mfn import Try, Result

# Try to Result
def to_result(try_result: Try) -> Result:

    if try_result.is_success():
        return Result.ok(try_result.unwrap())

    return Result.error(str(try_result.exception()))

# Result to Try
def to_try(result: Result) -> Try:

    if result.is_ok():
        return Success(result.unwrap())

    return Failure(Exception(result.error()))
```

## DX Benefits

✅ **No try/catch**: Exception handling as values
✅ **Composable**: Chain operations safely
✅ **Explicit**: Exception handling visible
✅ **Recoverable**: Can recover from specific errors
✅ **Type-safe**: Works with static type checkers

## Best Practices

```python
# ✅ Good: Wrap risky operations
result = Try(lambda: risky_operation())

# ✅ Good: Recover from specific errors
result.recover_if(ValueError, lambda _: default)

# ✅ Good: Chain operations
Try(lambda: parse(s)) | (lambda x: Try(lambda: transform(x)))

# ❌ Bad: Try/catch inside Try
# Just use Try directly

# ❌ Bad: Ignore exceptions
# Always handle Failure case
```
