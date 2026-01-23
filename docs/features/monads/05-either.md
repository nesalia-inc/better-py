# Either - Two Disjoint Types

Represent values that can be one of two types (commonly Left/Right).

## Overview

`Either` represents one of two possibilities:
- `Left(value)` - Typically used for errors
- `Right(value)` - Typically used for success

## Basic Usage

```python
from mfn import Either, Left, Right

# Create Either instances
left = Left("error")   # Left("error")
right = Right(42)      # Right(42)

# Check which side
if either.is_left():
    print("Has left value")

if either.is_right():
    print("Has right value")

# Get values
left_value = left.unwrap_left()    # "error"
right_value = right.unwrap_right()  # 42
```

## Transformation

```python
from mfn import Either

# Map right value
result = Right(5).map(lambda x: x * 2)
# Right(10)

# Map left value
result = Left("error").map_left(lambda s: s.upper())
# Left("ERROR")

# Map on right only (left skipped)
result = Left("error").map(lambda x: x * 2)
# Left("error") - unchanged

# Either: Map both sides
def either_to_string(either):
    return either.either(
        lambda left: f"Error: {left}",
        lambda right: f"Success: {right}"
    )

result = either_to_string(Left("fail"))
# "Error: fail"

result = either_to_string(Right(42))
# "Success: 42"
```

## Chaining

```python
from mfn import Either

def validate(data: dict) -> Either:
    if "email" not in data:
        return Left("No email")
    return Right(data)

def sanitize(data: dict) -> Either:
    return Right({**data, "email": data["email"].lower()})

# Chain continues on Right
result = (
    Right({"email": "USER@EXAMPLE.COM"})
    | validate   # Right({...})
    | sanitize   # Right({...})
)

# Chain stops on Left
result = (
    Right({"invalid": "data"})
    | validate   # Left("No email")
    | sanitize   # Skipped
)

# Left("No email")
```

## Pattern Matching

```python
from mfn import Either

either = Right(42)

match either:
    case Left(error):
        print(f"Error: {error}")
    case Right(value):
        print(f"Success: {value}")
```

## Merging Eithers

```python
from mfn import Either

def merge_eithers(*eithers: Either) -> Either:

    rights = []
    lefts = []

    for either in eithers:
        if either.is_right():
            rights.append(either.unwrap_right())
        else:
            lefts.append(either.unwrap_left())

    if lefts:
        return Left(lefts)

    return Right(rights)


# Use
result = merge_eithers(
    Right(1),
    Right(2),
    Left("error 1"),
    Right(3)
)
# Left(["error 1"])

result = merge_eithers(
    Right(1),
    Right(2),
    Right(3)
)
# Right([1, 2, 3])
```

## Conversion

```python
from mfn import Either, Result

# Result to Either
def result_to_either(result: Result) -> Either:

    if result.is_ok():
        return Right(result.unwrap())

    return Left(result.error())

# Either to Result
def either_to_result(either: Either) -> Result:

    if either.is_right():
        return Result.ok(either.unwrap_right())

    return Result.error(either.unwrap_left())
```

## Common Patterns

```python
from mfn import Either

# Validation with Left as errors
def validate_email(email: str) -> Either[str, str]:

    if "@" not in email:
        return Left("Invalid email format")

    if "." not in email.split("@")[1]:
        return Left("Invalid domain")

    return Right(email.lower())


# Validation that accumulates errors
class Validation:
    """Accumulate errors in Left"""

    @staticmethod
    def all_valid(*validators):
        """All validators must pass"""

        def validate(value):
            errors = []

            for validator in validators:
                result = validator(value)
                if result.is_left():
                    errors.append(result.unwrap_left())

            if errors:
                return Left(errors)
            return Right(value)

        return validate


# Use
validate_user = Validation.all_valid(
    lambda x: Left("No name") if not x else Right(x),
    lambda x: Left("No email") if "@" not in x else Right(x)
)

result = validate_user("Bob")
# Left(["No email"])
```

## DX Benefits

✅ **Explicit**: Type can be one of two things
✅ **Composable**: Chain operations
✅ **Pattern match**: Works with `match/case`
✅ **Bidirectional**: Map both sides
✅ **Flexible**: Use for any two-type scenario

## Best Practices

```python
# ✅ Good: Left for errors, Right for success
Right(success_value)
Left(error_message)

# ✅ Good: Chain Right operations
Right(data) | validate | transform

# ✅ Good: Use for validation
Either[str, User]  # Left=error, Right=user

# ❌ Bad: Overuse
# Use Result/Error for simple success/failure

# ❌ Bad: Confused left/right
# Keep consistent: Left=error, Right=success
```
