# Maybe - Optional Values

Handle values that might not exist without `None` checks.

## Overview

`Maybe` represents a value that may or may not be present:
- `Some(value)` - A value exists
- `None` - No value

## Basic Usage

```python
from mfn import Maybe, Some, None_

# Create Maybe instances
maybe_value = Maybe(42)        # Some(42)
empty = Maybe(None)            # None

# Or use constructors
some = Some(42)
none = None_

# Check if value exists
if some:
    print("Has value")  # Prints

if none:
    print("Has value")  # Doesn't print
```

## Transformation

```python
from mfn import Maybe

# Map: Transform value if present
result = Maybe(5).map(lambda x: x * 2)
# Some(10)

# Map on None returns None
result = Maybe(None).map(lambda x: x * 2)
# None

# Chain: Transform with Maybe-returning function
def get_user(id: int) -> Maybe[dict]:
    if id > 0:
        return Some({"id": id, "name": "Alice"})
    return None_

result = Maybe(1).then(get_user)
# Some({"id": 1, "name": "Alice"})
```

## Pipe Operators

```python
from mfn import Maybe

def validate(data: dict) -> Maybe[dict]:
    if "email" not in data:
        return None_
    return Some(data)

def sanitize(data: dict) -> Maybe[dict]:
    return Some({
        **data,
        "email": data["email"].lower()
    })

def save(data: dict) -> Maybe[int]:
    return Some(123)  # Saved with ID

# Chain with pipe
result = (
    Maybe({"email": "USER@EXAMPLE.COM"})
    | validate
    | sanitize
    | save
)

# Some(123)

# Error in chain
result = (
    Maybe({"invalid": "data"})
    | validate  # Returns None
    | sanitize  # Skipped
    | save      # Skipped
)

# None
```

## Unwrapping

```python
from mfn import Maybe

maybe = Maybe(42)

# Get value or default
value = maybe.unwrap_or(0)      # 42
value = None_.unwrap_or(0)     # 0

# Get value or raise
value = maybe.unwrap()         # 42
value = none_.unwrap()         # Raises ValueError

# Execute callback
maybe.if_some(lambda x: print(f"Value: {x}"))  # Prints
none_.if_some(lambda x: print(...))           # Doesn't print
```

## Pattern Matching

```python
from mfn import Maybe

maybe = Maybe(42)

match maybe:
    case Some(value):
        print(f"Has value: {value}")
    case None_:
        print("No value")
```

## Optional Attributes

```python
from mfn import Maybe

class User:
    def __init__(self, email: str | None):
        self.email = email

# Access optional attribute
user = User("alice@example.com")
email = Maybe(user.email).map(str.lower).unwrap_or("no-email")
# "alice@example.com"

user = User(None)
email = Maybe(user.email).map(str.lower).unwrap_or("no-email")
# "no-email"
```

## Collection Operations

```python
from mfn import Maybe

# Filter list to only present values
items = [1, None, 2, None, 3]
present = [Maybe(item).unwrap_or(0) for item in items]
# [1, 0, 2, 0, 3]

# Or use helper
from mfn import filter_some
items = [Some(1), None_, Some(2), None_, Some(3)]
result = filter_some(items)
# [1, 2, 3]
```

## DX Benefits

✅ **No `None` checks**: Chain operations safely
✅ **Explicit**: Optional is clear from type
✅ **Composable**: Pipe operations together
✅ **Pattern matching**: Works with `match/case`
✅ **Type-safe**: Full mypy support

## Best Practices

```python
# ✅ Good: Chain operations
Maybe(data) | validate | transform | save

# ✅ Good: Provide defaults
Maybe(value).unwrap_or(default_value)

# ✅ Good: Use for optional attributes
Maybe(user.email).map(str.lower)

# ❌ Bad: Explicit None checking
# Use Maybe instead
if value is not None:
    result = transform(value)
else:
    result = None

# ❌ Bad: Unwrap without checking
# Always use unwrap_or or check first
```
