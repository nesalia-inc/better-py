# Issue 009: Writer Assumes Monoid Uses + Operator

## Description

The `Writer` monad assumes the log type uses the `+` operator for monoid combination. This works for built-in types like `list`, `str`, and `int`, but fails for custom types that need different combination strategies.

## Current Implementation

```python
# The log type W must be a monoid (support + and have empty element)
W = TypeVar("W", bound=SupportsAdd)  # Assumes + operator

def flat_map(self, f: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
    result = f(self.value)
    combined_log = self.log + result.log  # Assumes + exists
    return Writer(combined_log, result.value)
```

## Problem

Users cannot use custom log types without:
1. Implementing `__add__` on their type
2. Being limited to the specific semantics of `+`

## Examples of Limitations

### Example 1: Multiplicative Monoid

```python
# Want to use multiplication as the monoid operation
# Product monoid: combine with *, identity is 1

class ProductLog:
    def __init__(self, value: int):
        self.value = value

# Writer won't work because it uses +
# Even if we define __add__, the semantics are wrong
```

### Example 2: Custom Logging Strategy

```python
# Want to merge log dictionaries with special rules
log1 = {"errors": ["e1"], "warnings": ["w1"]}
log2 = {"errors": ["e2"], "warnings": ["w2"]}

# Want: {"errors": ["e1", "e2"], "warnings": ["w1", "w2"]}
# But + would just overwrite or concatenate incorrectly
```

### Example 3: Monoid with Different Identity

```python
# Want to use set as log type (union operation)
# Identity should be empty set, combination should be set.union

Writer(set(), lambda: Writer(set(), value))  # Doesn't work
```

## Proposed Solutions

### Option 1: Monoid Protocol (Recommended)

Define a Monoid protocol and require it:

```python
@runtime_checkable
class Monoid(Protocol[T]):
    """Protocol for monoid types."""

    @staticmethod
    def empty() -> T:
        """The identity element for the monoid."""
        ...

    def combine(self, other: T) -> T:
        """Combine two monoid values."""
        ...

# Update Writer signature
class Writer(Generic[W, A], Monoid[W]):
    _log: W
    _value: A

    def flat_map(self, f: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
        result = f(self._value)
        combined_log = self._log.combine(result.log)  # Use combine
        return Writer(combined_log, result.value)

    @classmethod
    def tell(cls, log: W) -> Writer[W, None]:
        """Write a log value."""
        return Writer(log, None)
```

### Option 2: Pass Monoid Instance

Allow users to provide monoid operations:

```python
from typing import Protocol, TypeVar

class MonoidOps(Generic[T]):
    def empty(self) -> T: ...
    def combine(self, a: T, b: T) -> T: ...

class Writer(Generic[W, A]):
    _log: W
    _value: A
    _monoid: MonoidOps[W]  # Store monoid instance

    @classmethod
    def with_monoid(cls, monoid: MonoidOps[W]) -> type["Writer[W, A]"]:
        """Create a Writer subclass with custom monoid."""
        class CustomWriter(cls):
            _monoid = monoid
        return CustomWriter

    def flat_map(self, f: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
        result = f(self._value)
        combined_log = self._monoid.combine(self._log, result.log)
        return Writer(combined_log, result.value)
```

### Option 3: Support Built-in Monoids

Provide pre-configured Writer instances for common monoids:

```python
# Built-in monoid factories
def list_writer() -> type[Writer[list[T], A]]:
    """Writer with list concatenation monoid."""
    class ListWriter(Writer[list[T], A]):
        @staticmethod
        def _combine_logs(a: list[T], b: list[T]) -> list[T]:
            return a + b

    return ListWriter

def set_writer() -> type[Writer[set[T], A]]:
    """Writer with set union monoid."""
    class SetWriter(Writer[set[T], A]):
        @staticmethod
        def _combine_logs(a: set[T], b: set[T]) -> set[T]:
            return a | b

    return SetWriter

def dict_writer() -> type[Writer[dict[K, V], A]]:
    """Writer with dict merge monoid."""
    class DictWriter(Writer[dict[K, V], A]):
        @staticmethod
        def _combine_logs(a: dict[K, V], b: dict[K, V]) -> dict[K, V]:
            return {**a, **b}

    return DictWriter

# Usage
ListWriter = list_writer()
SetWriter = set_writer()
```

### Option 4: Keep Current, Document Limitation

Add clear documentation and provide examples:

```python
class Writer(Generic[W, A]):
    """Writer monad for accumulating logs.

    Type Parameters:
        W: The log type (must be a monoid with + operator and empty)
        A: The value type

    The log type W must support:
    - Addition operator (+) for combining logs
    - Empty value as identity (e.g., [], '', 0, set())

    Supported monoids:
    - list: concatenation
    - str: concatenation
    - int: addition
    - float: addition
    - set: union (uses | operator)

    For custom monoids, define __add__ on your type or use
    Writer.with_monoid() to provide custom combine operation.

    Example:
        >>> Writer.list(lambda: Writer([2], 3))
        Writer([1, 2], 3)
    """
```

## Recommendation

**Option 1** (Monoid Protocol) + **Option 3** (Built-in factories):

1. Define a `Monoid` protocol
2. Make `Writer` work with any `Monoid` type
3. Provide convenience factories for common monoids
4. Keep backward compatibility with types supporting `+`

## Implementation Example

```python
# Define Monoid protocol
@runtime_checkable
class Monoid(Protocol[T_co]):
    """Protocol for types with monoid structure."""

    @staticmethod
    def empty() -> T_co:
        """Return the identity element."""
        ...

    def combine(self, other: T_co) -> T_co:
        """Combine two values."""
        ...

# Built-in monoid instances
class ListMonoid(Generic[T], Monoid[list[T]]):
    @staticmethod
    def empty() -> list[T]:
        return []

    def combine(self, other: list[T]) -> list[T]:
        return self + other

# Usage with Writer
Writer[ListMonoid[int], int](logs, value)
```

## Related Issues

- Issue #008: Maybe cannot contain None
- Issue #001: Validation.ap() doesn't accumulate errors

## References

- Haskell's Monoid typeclass
- Scala's Monoid trait
- Cats kernel Monoid
