# Protocols: Structural Typing for Functional Patterns

Inspired by Python's `collections.abc`, we use **Protocols** to define functional behaviors that any class can implement.

## What are Protocols?

**Protocols** are **structural types** - they define interfaces that classes implement **implicitly** by having the right methods.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Mappable(Protocol[T]):
    """Any object with a map() method is Mappable"""
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

# This class is Mappable! No inheritance needed.
class SmartList:
    def map(self, func):
        return SmartList([func(x) for x in self._data])

isinstance(SmartList(), Mappable)  # True
```

## Why Protocols?

### ❌ Traditional Inheritance
```python
# Rigid: Must inherit from Mappable
class MappableList(Mappable):
    def map(self, func): ...

# Can't use built-in types
list([1,2,3]).map(...)  # No!
```

### ✅ Protocols
```python
# Flexible: Any class with map() is Mappable
class SmartList:
    def map(self, func): ...

isinstance(SmartList(), Mappable)  # True!

# Even built-ins can be adapted
@dataclass
class MappableList:
    _data: list
    def map(self, func): ...
```

**Benefits**:
- No rigid inheritance hierarchy
- Works with existing classes
- Duck typing with type checking
- Runtime introspection with `@runtime_checkable`

## Protocol-Based Design

### Defining Protocols

```python
from typing import Protocol, TypeVar, Generic, Callable, runtime_checkable

T = TypeVar('T')
U = TypeVar('U')

@runtime_checkable
class Mappable(Protocol[T]):
    """Structure that can be mapped over"""

    def map(self, func: Callable[[T], U]) -> 'Mappable[U]':
        """Transform values"""
        ...

@runtime_checkable
class Reducible(Protocol[T]):
    """Structure that can be reduced"""

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce to single value"""
        ...

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U:
        """Fold with initial value"""
        ...
```

### Implementing Protocols

```python
# Implementation 1: Custom class
class SmartList(Generic[T]):
    def __init__(self, items: list[T]):
        self._data = items

    def map(self, func: Callable[[T], U]) -> 'SmartList[U]':
        return SmartList([func(x) for x in self._data])

    def reduce(self, func: Callable[[T, T], T]) -> T:
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

# SmartList is both Mappable and Reducible!
isinstance(SmartList([1,2,3]), Mappable)  # True
isinstance(SmartList([1,2,3]), Reducible)  # True

# Implementation 2: Wrapper around built-in
@dataclass
class MappableDict(Generic[K, V]):
    _data: dict[K, V]

    def map_values(self, func: Callable[[V], U]) -> 'MappableDict[K, U]':
        return MappableDict({
            k: func(v) for k, v in self._data.items()
        })

    def map_keys(self, func: Callable[[K], U]) -> 'MappableDict[U, V]':
        return MappableDict({
            func(k): v for k, v in self._data.items()
        })
```

## Multiple Protocol Compliance

A single class can implement multiple protocols:

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

@runtime_checkable
class Reducible(Protocol[T]):
    def reduce(self, func): ...

@runtime_checkable
class Filterable(Protocol[T]):
    def filter(self, predicate): ...

class SmartList(Generic[T]):
    def __init__(self, items: list[T]):
        self._data = items

    def map(self, func):
        return SmartList([func(x) for x in self._data])

    def reduce(self, func):
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

    def filter(self, predicate):
        return SmartList([x for x in self._data if predicate(x)])

# Implements all 3 protocols!
isinstance(SmartList([1,2,3]), Mappable)   # True
isinstance(SmartList([1,2,3]), Reducible)  # True
isinstance(SmartList([1,2,3]), Filterable) # True
```

## Protocol Inheritance

Protocols can extend other protocols:

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

@runtime_checkable
class Filterable(Protocol[T]):
    def filter(self, predicate): ...

@runtime_checkable
class Transformable(Mappable[T], Filterable[T], Protocol):
    """Combines mapping and filtering"""
    pass

class SmartList(Generic[T]):
    def map(self, func): ...
    def filter(self, predicate): ...

# SmartList is Transformable (has both map and filter)
isinstance(SmartList([1,2,3]), Transformable)  # True
```

## Generic Protocols

Protocols support generics for type-safe transformations:

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

class SmartList(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'SmartList[U]':
        return SmartList([func(x) for x in self._data])

# Type inference works!
numbers: SmartList[int] = SmartList([1, 2, 3])
strings: SmartList[str] = numbers.map(str)

# mypy knows:
# - numbers is SmartList[int]
# - strings is SmartList[str]
```

## Protocol Attributes

Protocols can also specify attributes:

```python
@runtime_checkable
class Sized(Protocol):
    """Has a size"""
    @property
    def size(self) -> int: ...

@dataclass
class Cache:
    _items: dict

    @property
    def size(self) -> int:
        return len(self._items)

# Cache is Sized!
isinstance(Cache({}), Sized)  # True
```

## Callable Protocols

Protocols can define callable objects:

```python
@runtime_checkable
class Validator(Protocol[T]):
    """Object that can validate"""
    def __call__(self, value: T) -> Validation: ...

class EmailValidator:
    def __call__(self, value: str) -> Validation:
        if "@" in value:
            return Validation.success(value)
        return Validation.errors_(ValidationError("Invalid email"))

# EmailValidator is Validator[str]!
validator: Validator[str] = EmailValidator()
result = validator("test@example.com")
```

## Practical Examples

### Example 1: Collection Protocols

```python
@runtime_checkable
class Mappable(Protocol[T]): ...
@runtime_checkable
class Reducible(Protocol[T]): ...
@runtime_checkable
class Filterable(Protocol[T]): ...

class FunctionalList(Generic[T]):
    """List that implements all collection protocols"""

    def __init__(self, items: list[T]):
        self._data = items

    def map(self, func: Callable[[T], U]) -> 'FunctionalList[U]':
        return FunctionalList([func(x) for x in self._data])

    def filter(self, predicate: Callable[[T], bool]) -> 'FunctionalList[T]':
        return FunctionalList([x for x in self._data if predicate(x)])

    def reduce(self, func: Callable[[T, T], T]) -> T:
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U:
        result = initial
        for item in self._data:
            result = func(result, item)
        return result

# Usage
numbers = FunctionalList([1, 2, 3, 4, 5])

result = (
    numbers
    .filter(lambda x: x % 2 == 0)  # [2, 4]
    .map(lambda x: x * 2)          # [4, 8]
    .reduce(lambda a, b: a + b)    # 12
)
```

### Example 2: Result Protocols

```python
@runtime_checkable
class Unwrappable(Protocol[T]):
    """Can unwrap a value"""
    def unwrap(self) -> T: ...
    def unwrap_or(self, default: T) -> T: ...

@runtime_checkable
class MappableResult(Protocol[T, E]):
    """Result that can be mapped"""
    def map(self, func: Callable[[T], U]) -> 'MappableResult[U, E]': ...

class Result(Generic[T, E]):
    def is_ok(self) -> bool: ...
    def is_error(self) -> bool: ...
    def unwrap(self) -> T: ...
    def unwrap_or(self, default: T) -> T: ...
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]': ...

# Result is both Unwrappable and MappableResult
```

### Example 3: Validator Protocol

```python
@runtime_checkable
class Validator(Protocol[T]):
    """Validates values of type T"""
    def validate(self, value: T) -> Validation: ...

class StringValidator:
    def min_length(self, n: int) -> 'StringValidator':
        # Fluent builder
        def rule(value: str):
            if len(value) < n:
                return ValidationError(f"Must be at least {n} chars")
            return None
        self._rules.append(rule)
        return self

    def validate(self, value: str) -> Validation:
        for rule in self._rules:
            error = rule(value)
            if error:
                return Validation.errors_(error)
        return Validation.success(value)

# Any class with validate() is a Validator!
class CustomValidator:
    def validate(self, value: int) -> Validation:
        if value < 0:
            return Validation.errors_(ValidationError("Must be positive"))
        return Validation.success(value)

isinstance(CustomValidator(), Validator)  # True
```

## Best Practices

### ✅ Do: Use Protocols for Behaviors

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

# Any class can implement Mappable by having map()
class MyCollection:
    def map(self, func): ...
```

### ✅ Do: Use Generic Protocols

```python
class Mappable(Protocol[T]):
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

# Type-safe transformations
numbers: Mappable[int] = ...
strings: Mappable[str] = numbers.map(str)
```

### ✅ Do: Use @runtime_checkable for Introspection

```python
@runtime_checkable
class Mappable(Protocol[T]): ...

# Can check at runtime
if isinstance(obj, Mappable):
    obj.map(lambda x: x * 2)
```

### ❌ Don't: Over-narrow Protocols

```python
# Too specific: Only for MyList
class MyListMappable(Protocol):
    def map(self, func: Callable[[int], int]) -> 'MyList': ...

# Better: Generic for any type
class Mappable(Protocol[T]):
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...
```

### ❌ Don't: Require Protocol Inheritance

```python
# Unnecessary: Just implement the methods
class MyList(Mappable):  # No need to inherit!
    def map(self, func): ...

# Better: Just have the method
class MyList:
    def map(self, func): ...  # Automatically Mappable!
```

## Summary

**Protocols** provide:
- ✅ Structural typing - implement by having methods
- ✅ Generic type safety - track transformations
- ✅ Runtime introspection - check with `isinstance()`
- ✅ No rigid inheritance - work with any class
- ✅ Duck typing with type hints - best of both worlds

**Protocol-based design** means:
1. Define protocols for functional behaviors
2. Implement protocols by having the right methods
3. Use generic types for type safety
4. Check compliance at runtime if needed

**Inspired by `collections.abc`**, but for functional patterns.

---

**Next**: See [Functional Entities](../entities/00-overview.md) for protocol definitions.
