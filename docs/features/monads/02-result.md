# Result - Explicit Error Handling

Handle operations that can fail with explicit error values, no exceptions.

## Overview

`Result` represents success or failure:
- `Ok(value)` - Success with value
- `Error(exception)` - Failure with Exception object

## Basic Usage

```python
from mfn import Result, Ok, Error

# Create Result instances
success = Result.ok(42)        # Ok(42)
failure = Result.error(ValueError("fail"))  # Error(ValueError("fail"))

# Or use constructors
ok = Ok(42)
err = Error(ValueError("Something failed"))

# Check result
if result.is_ok():
    print("Success")

if result.is_error():
    print("Failed")

# Access the exception
if result.is_error():
    exception = result.exception
    print(f"Error type: {type(exception).__name__}")
    print(f"Error message: {exception}")
```

## Transformation

```python
from mfn import Result, Ok

# Map: Transform success value
result = Ok(5).map(lambda x: x * 2)
# Ok(10)

# Map on Error skips function
result = Error(ValueError("fail")).map(lambda x: x * 2)
# Error(ValueError("fail"))

# Map error: Transform exception
result = Error(ValueError("fail")).map_error(lambda e: TypeError(str(e)))
# Error(TypeError("fail"))

# Then: Chain with Result-returning function
def validate(id: int) -> Result[dict]:
    if id <= 0:
        return Error(ValidationError("Invalid ID"))
    return Ok({"id": id})

result = Ok(1).then(validate)
# Ok({"id": 1})

result = Ok(-1).then(validate)
# Error(ValidationError("Invalid ID"))
```

## Pipe Operators

```python
from mfn import Result

def validate(data: dict) -> Result:
    if "email" not in data:
        return Error(ValidationError("No email"))
    return Ok(data)

def sanitize(data: dict) -> Result:
    return Ok({**data, "email": data["email"].lower()})

def save(data: dict) -> Result:
    return Ok(123)

# Chain with pipe
result = (
    Result.ok({"email": "USER@EXAMPLE.COM"})
    | validate
    | sanitize
    | save
)

# Ok(123)

# Error in chain
result = (
    Result.ok({"invalid": "data"})
    | validate     # Error(ValidationError("No email"))
    | sanitize     # Skipped
    | save         # Skipped
)

# Error(ValidationError("No email"))
```

## Error Handling

```python
from mfn import Result

result = Error(ValueError("Database error"))

# Get value or default
value = result.unwrap_or(0)      # 0
value = Ok(42).unwrap_or(0)      # 42

# Get value or raise exception
value = Ok(42).unwrap()          # 42
value = Error(ValueError("fail")).unwrap()   # Raises ValueError with original exception

# Map error to default value
value = Error(ValueError("fail")).unwrap_or_else(lambda _: 0)
# 0
value = Ok(42).unwrap_or_else(lambda _: 0)
# 42

# Get both possibilities
match result:
    case Ok(value):
        print(f"Success: {value}")
    case Error(err):
        print(f"Error: {type(err).__name__}: {err}")

# Access exception properties
result = Error(DatabaseError("Connection failed", code=500))

if result.is_error():
    exc = result.exception
    print(f"Error: {exc}")
    print(f"Code: {exc.code}")  # Access custom exception attributes
```

## Custom Exceptions

```python
from mfn import Result, Error

# Define custom exceptions
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class NotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} {id} not found")

class PermissionError(Exception):
    def __init__(self, user: str, required: str):
        self.user = user
        self.required = required
        super().__init__(f"User {user} requires {required} permission")


# Use custom exceptions
def validate_user(data: dict) -> Result:
    if "email" not in data:
        return Error(ValidationError("email", "Email is required"))
    return Ok(data)

def fetch_user(id: int) -> Result:
    user = db.find(id)
    if not user:
        return Error(NotFoundError("User", id))
    return Ok(user)

def check_permission(user: dict, action: str) -> Result:
    if action not in user.get("permissions", []):
        return Error(PermissionError(user["name"], action))
    return Ok(user)


# Chain with custom exceptions
result = (
    Result.ok({"email": "test@example.com"})
    | validate_user
    | (lambda d: fetch_user(d["id"]))
    | (lambda u: check_permission(u, "delete"))
)

match result:
    case Ok(user):
        print(f"User can delete: {user['name']}")
    case Error(ValidationError):
        print("Validation failed")
    case Error(NotFoundError):
        print("User not found")
    case Error(PermissionError as exc):
        print(f"Permission denied: {exc.message}")
```

## Combining Results

```python
from mfn import Result

# Collect list of Results
def collect_all(results: list[Result]) -> Result[list, list]:
    values = []
    errors = []

    for result in results:
        match result:
            case Ok(v):
                values.append(v)
            case Error(e):
                errors.append(e)

    if errors:
        return Error(errors)

    return Ok(values)


# Use case
results = [
    Ok(1),
    Ok(2),
    Error(ValueError("Failed 3")),
    Ok(4)
]

combined = collect_all(results)
# Error([ValueError("Failed 3")])

# First success only
def first_ok(results: list[Result]) -> Result:

    for result in results:
        if result.is_ok():
            return result

    return Error(ValueError("All failed"))
```

## Conversion

```python
from mfn import Result, Maybe

# Maybe to Result
maybe_value = Some(42)
result = Result.from_maybe(maybe_value, error=ValueError("No value"))
# Ok(42)

maybe_none = None_
result = Result.from_maybe(maybe_none, error=ValueError("No value"))
# Error(ValueError("No value"))

# Try/catch to Result
result = Result.from_callable(lambda: 10 / 2)
# Ok(5.0)

result = Result.from_callable(lambda: 10 / 0)
# Error(ZeroDivisionError())

# Exception to Result
try:
    result = Ok(risky_operation())
except Exception as e:
    result = Error(e)
```

## Exception Type Matching

```python
from mfn import Result

def recover_by_error_type(result: Result) -> Result:

    match result:
        case Ok(value):
            return Ok(value)
        case Error(ValidationError as exc):
            # Handle validation errors
            return Ok({"error": exc.message, "field": exc.field})
        case Error(NotFoundError):
            # Handle not found errors
            return Ok({"error": "Resource not found"})
        case Error(PermissionError):
            # Handle permission errors
            return Ok({"error": "Permission denied"})
        case Error(exc):
            # Unknown error
            return Error(exc)


# Use
result = fetch_user(999)
handled = recover_by_error_type(result)
# Ok({"error": "Resource not found"})
```

## DX Benefits

✅ **Explicit**: Errors are visible in type
✅ **No exceptions**: Control flow is clear
✅ **Composable**: Chain operations
✅ **Typed errors**: Error type is known
✅ **Structured**: Custom exception attributes
✅ **Pattern matching**: Works with `match/case`

## Best Practices

```python
# ✅ Good: Use custom exceptions
class UserNotFoundError(Exception):
    pass

Error(UserNotFoundError(user_id))

# ✅ Good: Structured error data
class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message

# ✅ Good: Chain operations
Result.ok(data) | validate | transform | save

# ✅ Good: Match on error type
match result:
    case Error(ValidationError as exc):
        return handle_validation(exc)
    case Error(DatabaseError as exc):
        return handle_db_error(exc)

# ❌ Bad: Use generic Exception
# Use specific exception types

# ❌ Bad: String errors
Error("error")  # Bad
Error(ValueError("error"))  # Good
```
