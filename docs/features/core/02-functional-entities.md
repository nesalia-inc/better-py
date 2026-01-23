# Functional Entities: Objects as Functional Concepts

In traditional functional programming, you have **functions** that manipulate data. In our approach, **functional concepts are living entities** (objects) with behavior.

## What is a Functional Entity?

A **functional entity** is an object that **represents** a functional concept:
- It has **immutable state** (frozen dataclass)
- It has **methods** that represent operations
- Methods **return new instances** (immutability)
- It implements **Protocols** for composability

```python
@dataclass(frozen=True, slots=True)
class Maybe(Generic[T]):
    """Entity that represents an optional value"""
    value: T | None

    def is_some(self) -> bool:
        return self.value is not None

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        if self.value is None:
            return None_
        return Some(func(self.value))

    def unwrap_or(self, default: T) -> T:
        return self.value if self.value is not None else default
```

## Entities vs Functions

### ❌ Traditional FP: Functions

```python
# Maybe as functions
def some(value):
    return {"type": "some", "value": value}

def none_():
    return {"type": "none"}

def map(maybe, func):
    if maybe["type"] == "none":
        return none_()
    return some(func(maybe["value"]))

# Usage
result = map(some(42), lambda x: x * 2)
```

**Problems**:
- Not object-oriented
- Hard to discover operations
- No type safety for operations
- Feels alien in Python

### ✅ Our Approach: Entities

```python
# Maybe as entity
result = Some(42).map(lambda x: x * 2)

# Or with pipe
result = Some(42) | (lambda x: x * 2)
```

**Benefits**:
- Object-oriented (methods)
- IDE autocomplete discovers operations
- Type-safe (generic types)
- Natural Python syntax

## Examples of Functional Entities

### 1. Maybe Entity

```python
@dataclass(frozen=True, slots=True)
class Maybe(Generic[T]):
    """Entity representing optional value"""

    value: T | None

    # Query operations
    def is_some(self) -> bool:
        return self.value is not None

    def is_none(self) -> bool:
        return self.value is None

    # Transform operations
    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        if self.value is None:
            return None_
        return Some(func(self.value))

    def filter(self, predicate: Callable[[T], bool]) -> 'Maybe[T]':
        if self.value is None or not predicate(self.value):
            return None_
        return Some(self.value)

    # Unwrap operations
    def unwrap(self) -> T:
        if self.value is None:
            raise ValueError("Cannot unwrap None")
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value if self.value is not None else default

    def unwrap_or_else(self, func: Callable[[], T]) -> T:
        return self.value if self.value is not None else func()

    # Composition
    def flat_map(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.value is None:
            return None_
        return func(self.value)

    # Pipe operator
    def __or__(self, func) -> 'Maybe':
        return func(self.value) if self.is_some() else None_

# Usage
user = fetch_user(42)
if user.is_some():
    name = user.unwrap().name

# Or chain
result = (
    fetch_user(42)
    .map(lambda u: u.name)
    .filter(lambda n: len(n) > 0)
)
```

### 2. Result Entity

```python
@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    """Entity representing success or failure"""

    value: T | None
    error: E | None

    # Query operations
    def is_ok(self) -> bool:
        return self.error is None

    def is_error(self) -> bool:
        return self.error is not None

    # Transform operations
    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        if self.is_error():
            return Error(self.error)
        return Ok(func(self.value))

    def map_error(self, func: Callable[[E], F]) -> 'Result[T, F]':
        if self.is_ok():
            return Ok(self.value)
        return Error(func(self.error))

    # Unwrap operations
    def unwrap(self) -> T:
        if self.is_error():
            raise ValueError(f"Cannot unwrap error: {self.error}")
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value if self.is_ok() else default

    # Composition
    def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        if self.is_error():
            return Error(self.error)
        return func(self.value)

    def or_else(self, func: Callable[[E], 'Result[T, F]']) -> 'Result[T, F]':
        if self.is_ok():
            return Ok(self.value)
        return func(self.error)

# Usage
result = fetch_user(42)
if result.is_ok():
    user = result.unwrap()
else:
    handle_error(result.error)
```

### 3. Validator Entity

```python
class StringValidator(BaseValidator[str]):
    """Entity that validates strings"""

    def __init__(self):
        super().__init__()

    def min_length(self, n: int) -> 'StringValidator':
        """Returns NEW validator with added rule"""
        def rule(value: str):
            if len(value) < n:
                return ValidationError(f"Must be at least {n} chars")
            return None
        self._rules.append(rule)
        return self

    def max_length(self, n: int) -> 'StringValidator':
        """Returns NEW validator with added rule"""
        def rule(value: str):
            if len(value) > n:
                return ValidationError(f"Must be at most {n} chars")
            return None
        self._rules.append(rule)
        return self

    def email(self) -> 'StringValidator':
        """Returns NEW validator with email rule"""
        def rule(value: str):
            if "@" not in value:
                return ValidationError("Invalid email")
            return None
        self._rules.append(rule)
        return self

    def validate(self, value: str) -> Validation:
        """Validate value"""
        for rule in self._rules:
            error = rule(value)
            if error:
                return Validation.errors_(error)
        return Validation.success(value)

# Usage
email_validator = (
    StringValidator()
    .min_length(5)
    .max_length(100)
    .email()
)

result = email_validator.validate(user_input)
if result.is_success():
    value = result.get()
```

### 4. ImmutableDict Entity

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    """Entity representing immutable dictionary"""

    _data: dict[K, V]

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._data.get(key, default)

    def update(self, **kwargs) -> 'ImmutableDict[K, V]':
        """Returns NEW instance with updates"""
        return ImmutableDict({**self._data, **kwargs})

    def set_in(self, path: str, value: Any) -> 'ImmutableDict[K, V]':
        """Immutable deep update"""
        keys = path.split(".")
        new_data = self._data.copy()
        current = new_data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
        return ImmutableDict(new_data)

    def merge(self, other: 'ImmutableDict[K, V]') -> 'ImmutableDict[K, V]':
        """Returns NEW instance merged with another"""
        return ImmutableDict(deep_merge(self._data, other._data))

# Usage
config = ImmutableDict({"database": {"host": "localhost"}})
new_config = config.set_in("database.port", 5432)

# Original unchanged
config._data  # {"database": {"host": "localhost"}}
new_config._data  # {"database": {"host": "localhost", "port": 5432}}
```

### 5. RetryPolicy Entity

```python
@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Entity representing retry strategy"""

    max_attempts: int = 3
    backoff: Callable[[int], float] = lambda n: 2 ** n
    retry_on: tuple[Exception, ...] = (Exception,)

    def with_max_attempts(self, n: int) -> 'RetryPolicy':
        """Returns NEW policy with different max attempts"""
        return Replace(self, max_attempts=n)

    def with_backoff(self, backoff: Callable[[int], float]) -> 'RetryPolicy':
        """Returns NEW policy with different backoff"""
        return Replace(self, backoff=backoff)

    def with_retry_on(self, *exceptions: Exception) -> 'RetryPolicy':
        """Returns NEW policy with different exceptions"""
        return Replace(self, retry_on=exceptions)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Check if should retry"""
        return attempt < self.max_attempts and isinstance(error, self.retry_on)

    def get_delay(self, attempt: int) -> float:
        """Get delay for attempt"""
        return self.backoff(attempt)

# Usage
default_policy = RetryPolicy()

db_policy = (
    default_policy
    .with_max_attempts(5)
    .with_backoff(lambda n: n * 0.1)  # Linear backoff
    .with_retry_on(ConnectionError, TimeoutError)
)
```

## Characteristics of Functional Entities

### 1. Immutable State

```python
@dataclass(frozen=True, slots=True)
class Maybe:
    value: T | None

    # Can't modify state
    # def set_value(self, value):  # ERROR! frozen dataclass
    #     self.value = value
```

### 2. Methods Return New Instances

```python
def update(self, **kwargs) -> 'ImmutableDict':
    # Returns NEW instance
    return ImmutableDict({**self._data, **kwargs})
```

### 3. Implements Protocols

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

class Maybe(Generic[T]):
    def map(self, func): ...
    # Maybe is now Mappable!
```

### 4. Fluent Interface

```python
# Method chaining for readability
validator = (
    StringValidator()
    .min_length(5)
    .max_length(100)
    .email()
)
```

### 5. Generic Types

```python
class Maybe(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'Maybe[U]': ...

# Type inference
maybe_int: Maybe[int] = Some(42)
maybe_str: Maybe[str] = maybe_int.map(str)
```

## Entity Composition

Entities can compose with other entities:

```python
# Maybe composes with functions
result = (
    Some(user_id)
    | fetch_user
    | validate_user
    | get_profile
)

# Result composes with Result
user_result = fetch_user(42)
profile_result = user_result.and_then(lambda u: get_profile(u.id))

# Validator composes with Validator
email_validator = StringValidator().min_length(5).email()
user_validator = DictValidator().field("email", email_validator)
```

## Benefits of Functional Entities

### For Python Developers
- ✅ **Discoverable**: IDE autocomplete shows methods
- ✅ **Familiar**: Objects and methods are Pythonic
- ✅ **Readable**: Method chaining reads naturally
- ✅ **Intuitive**: Similar to built-in types (list.append, dict.update)

### For Functional Programming
- ✅ **Immutable**: Frozen dataclasses
- ✅ **Composable**: Protocols enable composition
- ✅ **Type-safe**: Generic types track transformations
- ✅ **Pure**: Side effects are explicit

### For Software Architecture
- ✅ **Testable**: Easy to mock and test
- ✅ **Maintainable**: Clear behavior in one place
- ✅ **Documentable**: Self-documenting with methods
- ✅ **Extensible**: Add methods without breaking code

## Anti-Patterns

### ❌ Don't: Mutable Entities

```python
@dataclass  # NOT frozen!
class BadMaybe:
    value: T | None

    def set_value(self, value):
        self.value = value  # Mutates!
```

### ✅ Do: Immutable Entities

```python
@dataclass(frozen=True)
class GoodMaybe:
    value: T | None

    def with_value(self, value) -> 'GoodMaybe':
        return GoodMaybe(value)  # New instance
```

### ❌ Don't: Entities without Protocols

```python
class BadList:
    def map(self, func): ...  # Alone

# Can't use generically
def process(data: ???):  # What type?
    return data.map(str)
```

### ✅ Do: Entities with Protocol Compliance

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

class GoodList:
    def map(self, func): ...  # Implements Mappable

# Can use generically
def process(data: Mappable[T]):
    return data.map(str)
```

## Summary

**Functional Entities** are:
- Objects representing functional concepts
- Immutable (frozen dataclasses)
- Methods return new instances
- Implement Protocols for composability
- Generic types for type safety
- Fluent interfaces for readability

**Think**: "Maybe is an object that might have a value"
**Not**: "Maybe is a monadic type from category theory"

---

**Next**: See [Immutability](./03-immutability.md) for immutability patterns.
