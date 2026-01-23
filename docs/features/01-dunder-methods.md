# Dunder Methods - Expressive Syntax

Leverage Python's special methods to create a fluid, operator-based API.

## Overview

Dunder (double underscore) methods enable custom types to behave like built-in Python objects. For functional programming, this means monadic operations can use natural operators instead of method chaining.

## Key Operators

### `__or__` - Bind/flatMap Operator

```python
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    def __init__(self, value: T | None):
        self._value = value

    def __or__(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Bind operation: maybe | func"""
        if self._value is None:
            return Maybe(None)
        return func(self._value)

# Usage
result = Maybe(5) | (lambda x: Maybe(x * 2)) | (lambda x: Maybe(x + 10))
# Result: Maybe(20)
```

### `__rshift__` - Map Operator

```python
class Maybe(Generic[T]):
    # ... previous code ...

    def __rshift__(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """Map operation: maybe >> func"""
        if self._value is None:
            return Maybe(None)
        return Maybe(func(self._value))

# Usage
result = Maybe([1, 2, 3]) >> len  # Maybe(3)
```

### `__and__` - Sequential Composition

```python
class Maybe(Generic[T]):
    # ... previous code ...

    def __and__(self, other: 'Maybe[U]') -> 'Maybe[U]':
        """Monadic AND: short-circuit on None"""
        if self._value is None:
            return Maybe(None)
        return other

# Usage
user = get_user(id) & validate_user & fetch_profile
```

### `__bool__` - Truthiness Check

```python
class Maybe(Generic[T]):
    # ... previous code ...

    def __bool__(self) -> bool:
        """Natural truthiness: if maybe:"""
        return self._value is not None

# Usage
if Maybe(42):
    print("Has value!")
```

### `__iter__` - Unpacking Support

```python
class Maybe(Generic[T]):
    # ... previous code ...

    def __iter__(self):
        """Enable unpacking: for x in maybe:"""
        if self._value is not None:
            yield self._value
        else:
            return
            raise StopIteration

# Usage
for value in Maybe(10):
    print(value)  # prints: 10

# Unpacking
x, = Maybe(5)  # x = 5
```

## Comparison: Before vs After

### Before (Method chaining)
```python
result = (
    Maybe(user_id)
    .bind(fetch_user)
    .bind(validate)
    .bind(transform)
    .get_or_default(default_user)
)
```

### After (Operator-based)
```python
result = Maybe(user_id) | fetch_user | validate | transform or default_user
```

## Additional Dunder Methods

### `__repr__` - Developer-Friendly Display
```python
def __repr__(self) -> str:
    if self._value is None:
        return "Maybe(None)"
    return f"Maybe({self._value!r})"
```

### `__eq__` - Structural Equality
```python
def __eq__(self, other) -> bool:
    if not isinstance(other, Maybe):
        return False
    return self._value == other._value
```

### `__match_args__` - Pattern Matching (Python 3.10+)
```python
__match_args__ = ("_value",)

# Usage:
match maybe_value:
    case Maybe(None):
        print("Empty")
    case Maybe(value):
        print(f"Has: {value}")
```

## Full Example: Integrated Maybe Type

```python
from typing import Generic, TypeVar, Callable, Iterator

T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    """A Maybe monad with operator-based API"""

    __slots__ = ('_value',)  # Memory optimization

    __match_args__ = ('_value',)  # Pattern matching support

    def __init__(self, value: T | None):
        self._value = value

    # === Monadic operations ===

    def __or__(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Bind: self | func"""
        if self._value is None:
            return Maybe(None)
        return func(self._value)

    def __rshift__(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """Map: self >> func"""
        if self._value is None:
            return Maybe(None)
        return Maybe(func(self._value))

    def __and__(self, other: 'Maybe[U]') -> 'Maybe[U]':
        """And: self & other (short-circuit)"""
        if self._value is None:
            return Maybe(None)
        return other

    # === Python protocol support ===

    def __bool__(self) -> bool:
        """Truthiness: if maybe:"""
        return self._value is not None

    def __iter__(self) -> Iterator[T]:
        """Unpacking: for x in maybe:"""
        if self._value is not None:
            yield self._value

    # === Object protocol ===

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Maybe):
            return NotImplemented
        return self._value == other._value

    def __repr__(self) -> str:
        return f"Maybe({self._value!r})"

    # === Factory methods ===

    @classmethod
    def some(cls, value: T) -> 'Maybe[T]':
        return cls(value)

    @classmethod
    def none(cls) -> 'Maybe[T]':
        return cls(None)

    @classmethod
    def from_nullable(cls, value: T | None) -> 'Maybe[T]':
        return cls(value)


# === Usage Examples ===

def get_user(id: int) -> Maybe[str]:
    return Maybe.some("alice") if id > 0 else Maybe.none()

def validate(name: str) -> Maybe[str]:
    return Maybe(name) if len(name) > 2 else Maybe.none()

def greet(name: str) -> str:
    return f"Hello, {name}!"

# Pipeline with operators
result = (
    Maybe.from_nullable(5)
    | get_user
    | validate
    >> greet
)

print(result)  # Maybe("Hello, alice!")

# Direct usage with None
empty = Maybe.from_nullable(None) | get_user | validate >> greet
print(empty)  # Maybe(None)

# Conditional execution
if Maybe(42):
    print("Has value!")  # Executed

# Unpacking
value, = Maybe(100)
print(value)  # 100
```

## DX Benefits

✅ **Readable**: Operators read left-to-right like natural language
✅ **Discoverable**: Autocomplete shows all operators naturally
✅ **Concise**: Less verbose than method chaining
✅ **Pythonic**: Uses familiar operator semantics
✅ **Type-safe**: Works with static type checkers

## Trade-offs

⚠️ **Overload**: Don't use operators for non-standard semantics
⚠️ **Documentation**: Operator usage needs clear docs
⚠️ **Precedence**: Remember operator precedence rules
