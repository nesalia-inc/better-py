# Issue 008: Maybe Cannot Distinguish None from Nothing

## Description

The `Maybe` monad treats `None` as "no value", making it impossible to distinguish between:
1. A value that is actually `None`
2. No value at all (Nothing)

This is a common pattern in Python where `None` is a valid value.

## Current Implementation

```python
@staticmethod
def from_value(value: T | None) -> Maybe[T]:
    """Create a Maybe from a value, treating None as Nothing."""
    return Maybe(value)  # If value is None, returns Nothing
```

## Problem

In Python, `None` is often used as a valid value, not just "absence". The current API makes this impossible to express.

## Examples

### Example 1: Optional Return Value

```python
def find_user_optional(user_id: int) -> User | None:
    """Return None if user not found."""
    return db.query(user_id)

# Problem: Cannot wrap this in Maybe while preserving None
maybe_user = Maybe.from_value(find_user_optional(123))
# If user exists but is None (valid), we get Nothing
# If user doesn't exist, we also get Nothing
# Cannot distinguish these cases!
```

### Example 2: Configuration with Explicit None

```python
config = {
    "timeout": None,  # Explicitly set to None (no timeout)
    "retries": None,  # Explicitly set to None (use default)
}

# Want to know if key exists vs key exists with None value
timeout = Maybe.from_value(config.get("timeout"))
retries = Maybe.from_value(config.get("retries"))

# Both return Nothing if:
# 1. Key doesn't exist
# 2. Key exists with value None
# Cannot distinguish!
```

### Example 3: Database Nullable Field

```python
# Database allows NULL for phone_number
user = db.get_user(123)
phone_number = user.phone_number  # Could be None (valid) or missing

# Want to distinguish:
# - User exists, phone_number is NULL (valid None)
# - User doesn't exist
# - User exists, phone_number column doesn't exist
```

## Proposed Solutions

### Option 1: Separate Types (Recommended)

Use a different monad for optional values that can be None:

```python
@dataclass(frozen=True)
class Optional(Generic[T]):
    """For values that can be T or None (both valid)."""

    _value: T | None

    def is_present(self) -> bool:
        return True  # Always present (even if None)

    def get(self) -> T | None:
        return self._value

    def map(self, f: Callable[[T], U]) -> Optional[U]:
        if self._value is None:
            return Optional(None)
        return Optional(f(self._value))

# Usage
phone_number = Optional(user.phone_number)  # None is valid
name = Maybe.from_value(user.name)  # None means missing
```

### Option 2: Explicit Wrapper Type

Use a wrapper to distinguish None from Nothing:

```python
@dataclass(frozen=True)
class ExplicitNone:
    """Explicit None value."""

# API
def from_value(value: T | None | ExplicitNone) -> Maybe[T]:
    """Create a Maybe, with ExplicitNone treated as Some(None)."""
    if isinstance(value, ExplicitNone):
        return Maybe(None)  # Some(None)
    if value is None:
        return Maybe()  # Nothing
    return Maybe(value)  # Some(value)

# Usage
maybe_user = Maybe.from_value(ExplicitNone())  # Some(None)
maybe_missing = Maybe.from_value(None)  # Nothing
```

### Option 3: Add Factory Method

Add a method to explicitly create `Some(None)`:

```python
@staticmethod
def some_none() -> Maybe[T | None]:
    """Create a Maybe containing None explicitly.

    This distinguishes between "value is None" and "no value".
    """
    return Maybe(None)  # Creates Some(None), not Nothing

@staticmethod
def from_value(value: T | None) -> Maybe[T]:
    """Create a Maybe from a value, treating None as Nothing."""
    if value is None:
        return Maybe()  # Nothing
    return Maybe(value)  # Some(value)

# Usage
explicit_none = Maybe.some_none()  # Some(None)
nothing = Maybe.from_value(None)  # Nothing
```

### Option 4: Change is_some() Semantics

Distinguish internally between Some(None) and Nothing:

```python
@dataclass(frozen=True)
class Maybe(Generic[T]):
    _value: T | None
    _is_defined: bool = True  # False for Nothing

    def is_some(self) -> bool:
        return self._is_defined

    @staticmethod
    def nothing() -> Maybe[T]:
        return Maybe(None, False)

    @staticmethod
    def some(value: T | None) -> Maybe[T]:
        return Maybe(value, True)
```

## Recommendation

**Option 3** (Add `some_none()` factory) is the simplest and most Pythonic:

```python
# Clear API
Maybe.some(value)     # Some(value)
Maybe.some_none()     # Some(None) - explicit None
Maybe.nothing()       # Nothing
Maybe.from_value(x)   # Some(x) or Nothing if x is None
```

## Migration Path

```python
# Before (ambiguous)
maybe_value = Maybe.from_value(get_optional_value())

# After (explicit)
maybe_value = Maybe.from_value(get_optional_value())
if maybe_value.is_nothing():
    # Value was None or missing
    pass

# Or use explicit
maybe_value = Maybe.some(get_optional_value() or ExplicitNone())
```

## Related Issues

- Issue #007: Missing applicative operations
- Issue #009: Writer assumes monoid with +

## References

- Scala's Option vs Try vs Either distinction
- Haskell's Maybe vs Optional
- Rust's Option<T>
