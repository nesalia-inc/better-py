# Descriptors - Declarative Attributes

Reusable attribute logic using Python's descriptor protocol for validation and transformation.

## Overview

Descriptors provide a powerful mechanism for attribute management. They enable:
- Declarative validation
- Computed/cached properties
- Reusable attribute behavior
- Type coercion
- Side effects on access

## Descriptor Basics

A descriptor implements any of:
- `__get__(self, instance, owner)` - Called on attribute access
- `__set__(self, instance, value)` - Called on attribute assignment
- `__delete__(self, instance)` - Called on attribute deletion
- `__set_name__(self, owner, name)` - Called on class creation

## Functional Validation Descriptor

```python
from typing import Any, Callable, Generic, TypeVar

T = TypeVar('T')

class Validated(Generic[T]):
    """Reusable validation descriptor"""

    def __init__(self, type_hint: type[T] | None = None):
        self.type_hint = type_hint
        self.validators: list[Callable[[T], bool]] = []
        self.transformers: list[Callable[[T], T]] = []
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: Any, owner: type) -> T:
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance: Any, value: T) -> None:
        # Apply transformers
        for transformer in self.transformers:
            value = transformer(value)

        # Validate type
        if self.type_hint and not isinstance(value, self.type_hint):
            raise TypeError(f"{self.name[1:]} must be {self.type_hint}")

        # Run validators
        for validator in self.validators:
            if not validator(value):
                raise ValueError(f"Invalid {self.name[1:]}: {value}")

        setattr(instance, self.name, value)

    # === Fluent API ===

    def validate(self, predicate: Callable[[T], bool]) -> 'Validated[T]':
        self.validators.append(predicate)
        return self

    def transform(self, func: Callable[[T], T]) -> 'Validated[T]':
        self.transformers.append(func)
        return self


# === Usage Example ===

@dataclass
class User:
    email: str = (
        Validated(str)
        .validate(lambda x: "@" in x)
        .validate(lambda x: "." in x.split("@")[1])
        .transform(str.lower)
    )

    age: int = (
        Validated(int)
        .validate(lambda x: x >= 0)
        .validate(lambda x: x < 150)
    )

    username: str = (
        Validated(str)
        .validate(lambda x: len(x) >= 3)
        .validate(lambda x: x.isalnum())
    )


user = User(
    email="JOHN@EXAMPLE.COM",
    age=30,
    username="john123"
)

print(user.email)  # "john@example.com" (lowercased)

# These would raise errors:
# User(email="invalid", age=30, username="john")  # ValueError: Invalid email
# User(email="john@example.com", age=-5, username="john")  # ValueError: Invalid age
```

## Maybe/Option Descriptor

```python
from typing import TypeVar, Generic, Optional, Callable

T = TypeVar('T')

class MaybeAttribute(Generic[T]):
    """Descriptor that wraps values in Maybe monad"""

    def __init__(self, default: T | None = None):
        self.default = default
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: Any, owner: type) -> Maybe[T]:
        if instance is None:
            return self
        value = getattr(instance, self.name, self.default)
        return Maybe(value)

    def __set__(self, instance: Any, value: T | None) -> None:
        setattr(instance, self.name, value)


# === Usage ===

class Database:
    connection: MaybeAttribute[Connection] = MaybeAttribute()

db = Database()
print(db.connection)  # Maybe(None)

db.connection = Connection()
print(db.connection)  # Maybe(Connection(...))

# Safe chaining
result = (
    db.connection
    | (lambda conn: conn.execute("SELECT 1"))
    | (lambda cursor: cursor.fetchone())
)
```

## Cached Function Descriptor

```python
from functools import wraps
from typing import Any, Callable

class memoized:
    """Memoization descriptor for methods"""

    def __init__(self, func: Callable):
        self.func = func
        self.cache_name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.cache_name = f"_cache_{name}"

    def __get__(self, instance: Any, owner: type) -> Callable:
        if instance is None:
            return self.func

        # Create cache if needed
        if not hasattr(instance, self.cache_name):
            setattr(instance, self.cache_name, {})

        @wraps(self.func)
        def wrapper(*args, **kwargs):
            cache = getattr(instance, self.cache_name)
            key = (args, tuple(sorted(kwargs.items())))

            if key not in cache:
                cache[key] = self.func(instance, *args, **kwargs)

            return cache[key]

        return wrapper


# === Usage ===

class Fibonacci:
    @memoized
    def fib(self, n: int) -> int:
        if n < 2:
            return n
        return self.fib(n - 1) + self.fib(n - 2)


fib = Fibonacci()
print(fib.fib(100))  # Fast! (cached results)
```

## Computed Property Descriptor

```python
class Computed:
    """Descriptor for computed properties with dependencies"""

    def __init__(self, *dependencies: str):
        self.dependencies = dependencies
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.computed_name = f"_computed_{name}"

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self

        # Check if already computed
        if hasattr(instance, self.computed_name):
            return getattr(instance, self.computed_name)

        # Compute value
        dep_values = {dep: getattr(instance, dep) for dep in self.dependencies}
        value = self.compute(instance, **dep_values)

        # Cache it
        setattr(instance, self.computed_name, value)
        return value

    def compute(self, instance, **deps):
        raise NotImplementedError


# === Usage ===

class Person:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    @Computed('first_name', 'last_name')
    def full_name(self, first_name, last_name):
        return f"{first_name} {last_name}"


person = Person("Alice", "Smith")
print(person.full_name)  # "Alice Smith" (computed and cached)
```

## Lens Descriptor

```python
class Lens:
    """Descriptor for immutable nested access/updates"""

    def __init__(self, path: str):
        self.path = path.split(".")
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self

        # Get nested value
        value = instance
        for key in self.path:
            value = getattr(value, key)

        return value

    def __set__(self, instance: Any, new_value: Any) -> None:
        # Immutable update - create new instance
        # This would work well with dataclasses/frozen dataclasses
        raise AttributeError("Cannot directly assign to lens. Use .set() method")


# === Usage ===

@dataclass(frozen=True)
class Address:
    city: str
    country: str

@dataclass(frozen=True)
class Person:
    name: str
    address: Address

    city = Lens("address.city")

    def with_city(self, new_city: str) -> 'Person':
        new_address = Address(new_city, self.address.country)
        return Person(self.name, new_address)


person = Person("Alice", Address("Paris", "France"))
print(person.city)  # "Paris"

person2 = person.with_city("London")
print(person.city)   # "Paris" (unchanged)
print(person2.city)  # "London"
```

## Type-Coercing Descriptor

```python
class Coerced:
    """Automatically coerce values to specified type"""

    def __init__(self, type_: type, factory: Callable | None = None):
        self.type = type_
        self.factory = factory or type_
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: Any, owner: type) -> Any:
        if instance is None:
            return self
        return getattr(instance, self.name)

    def __set__(self, instance: Any, value: Any) -> None:
        if not isinstance(value, self.type):
            try:
                value = self.factory(value)
            except (ValueError, TypeError) as e:
                raise TypeError(
                    f"Cannot coerce {type(value).__name__} to {self.type.__name__}"
                ) from e
        setattr(instance, self.name, value)


# === Usage ===

class Config:
    timeout: float = Coerced(float)  # "5.0" -> 5.0
    retries: int = Coerced(int)      # "3" -> 3
    enabled: bool = Coerced(bool)    # "true" -> True (with custom factory)


config = Config(timeout="5.0", retries="3")
print(config.timeout)  # 5.0 (float, not str)
print(config.retries)  # 3 (int, not str)
```

## Signal/Event Descriptor

```python
from typing import Callable, TypeVar, Any

T = TypeVar('T')

class Signal:
    """Event emitter descriptor"""

    def __init__(self):
        self.listeners: list[Callable] = []
        self.name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type) -> 'SignalEmitter':
        if instance is None:
            return self
        return SignalEmitter(instance, self)

    def emit(self, instance: Any, *args, **kwargs) -> None:
        for listener in self.listeners:
            listener(instance, *args, **kwargs)

    def subscribe(self, listener: Callable) -> Callable:
        """Subscribe to signal, returns unsubscribe function"""
        self.listeners.append(listener)

        def unsubscribe():
            self.listeners.remove(listener)

        return unsubscribe


class SignalEmitter:
    def __init__(self, instance: Any, signal: Signal):
        self.instance = instance
        self.signal = signal

    def __call__(self, *args, **kwargs):
        """Emit the signal"""
        self.signal.emit(self.instance, *args, **kwargs)

    def __iadd__(self, listener: Callable):
        """Subscribe using += operator"""
        self.signal.listeners.append(listener)
        return self

    def __isub__(self, listener: Callable):
        """Unsubscribe using -= operator"""
        self.signal.listeners.remove(listener)
        return self


# === Usage ===

class Button:
    clicked = Signal()
    hovered = Signal()

    def __init__(self, label: str):
        self.label = label

    def click(self):
        self.clicked(self.label)


button = Button("OK")

# Subscribe to signal
def on_clicked(instance, label):
    print(f"Button {label} clicked!")

button.clicked += on_clicked

button.click()  # Prints: "Button OK clicked!"
```

## DX Benefits

✅ **Declarative**: Behavior defined at class level
✅ **Reusable**: Same descriptor across many classes
✅ **Composable**: Chain multiple descriptors
✅ **Encapsulated**: Logic hidden from class users
✅ **Type-safe**: Works with static type checkers

## Best Practices

```python
# ✅ Good: Descriptors for cross-cutting concerns
class User:
    email: str = Validated(str).validate(is_email)
    age: int = Validated(int).validate(is_positive)

# ✅ Good: Use __set_name__ for attribute naming
def __set_name__(self, owner, name):
    self.private_name = f"_{name}"

# ❌ Bad: Descriptors for simple attributes
class User:
    name: str = SimpleDescriptor()  # Just use a normal attribute!
```
