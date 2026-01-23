# Protocols - Structural Duck Typing

Type-safe structural subtyping using Python's Protocol for polymorphic behavior.

## Overview

Protocols enable:
- Structural subtyping (duck typing with types)
- Polymorphism without inheritance
- Type-safe ad-hoc interfaces
- Protocol composition
- Runtime and static checking

## Basic Protocol

```python
from typing import Protocol, runtime_checkable, Any

class Sized(Protocol):
    """Protocol for objects with size"""

    def __len__(self) -> int: ...


def get_size(obj: Sized) -> int:
    """Accepts any object with __len__"""
    return len(obj)


# Works with any sized object
print(get_size([1, 2, 3]))      # 3
print(get_size("hello"))        # 5
print(get_size({'a': 1}))       # 1

# Type checking
print(isinstance([1, 2, 3], Sized))  # True (if @runtime_checkable)
```

## Functor Protocol

```python
from typing import Protocol, TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

class Functor(Protocol[T]):
    """Protocol for functor types"""

    def map(self, f: Callable[[T], U]) -> 'Functor[U]':
        """Apply function to wrapped value"""
        ...


def double_if_functor(value: Functor[int]) -> Functor[int]:
    """Double any functor containing an int"""
    return value.map(lambda x: x * 2)


# Any type implementing map is a Functor
@dataclass
class Maybe(Generic[T]):
    value: T | None

    def map(self, f: Callable[[T], U]) -> 'Maybe[U]':
        if self.value is None:
            return Maybe(None)
        return Maybe(f(self.value))


maybe = Maybe(5)
result = double_if_functor(maybe)
print(result)  # Maybe(value=10)
```

## Monad Protocol

```python
from typing import Protocol, TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

class Monad(Protocol[T]):
    """Protocol for monadic types"""

    def bind(self, f: Callable[[T], 'Monad[U]']) -> 'Monad[U]':
        """Chain monadic operations"""
        ...


def parse_int(s: str) -> Maybe[int]:
    """Parse string to int, return Maybe"""
    try:
        return Maybe(int(s))
    except ValueError:
        return Maybe(None)


def divide_by_two(x: int) -> Maybe[int]:
    """Divide by two, return Maybe"""
    return Maybe(x // 2)


def process_string(s: str) -> Maybe[int]:
    """Chain monadic operations"""
    maybe_s = Maybe(s)
    return maybe_s.bind(parse_int).bind(divide_by_two)


print(process_string("42"))    # Maybe(21)
print(process_string("abc"))   # Maybe(None)
print(process_string("5"))     # Maybe(2)
```

## Composable Protocols

```python
from typing import Protocol

class Sized(Protocol):
    def __len__(self) -> int: ...

class Iterable(Protocol):
    def __iter__(self): ...

class Container(Sized, Iterable, Protocol):
    """Protocol combining multiple interfaces"""

    def __contains__(self, item) -> bool: ...


def describe(obj: Container) -> str:
    """Works with any container"""
    size = len(obj)
    has_item = 42 in obj
    items = list(obj)
    return f"Container with {size} items, contains 42: {has_item}"


print(describe([1, 2, 42, 5]))  # "Container with 4 items, contains 42: True"
print(describe("hello"))        # "Container with 5 items, contains 42: False"
```

## Protocol for Validation

```python
from typing import Protocol, TypeVar, Generic

T = TypeVar('T')

class Validator(Protocol[T]):
    """Protocol for validation functions"""

    def is_valid(self, value: T) -> bool:
        """Check if value is valid"""
        ...

    def error_message(self, value: T) -> str:
        """Return error message for invalid value"""
        ...


class EmailValidator:
    def is_valid(self, value: str) -> bool:
        return "@" in value and "." in value.split("@")[1]

    def error_message(self, value: str) -> str:
        return f"Invalid email: {value}"


class PositiveNumberValidator:
    def is_valid(self, value: int) -> bool:
        return value > 0

    def error_message(self, value: int) -> str:
        return f"Number must be positive, got {value}"


def validate(value: T, validator: Validator[T]) -> Result[T, str]:
    """Validate using any validator"""
    if validator.is_valid(value):
        return Result.ok(value)
    return Result.error(validator.error_message(value))


@dataclass
class Result:
    _value: any
    _error: str | None

    @classmethod
    def ok(cls, value):
        return cls(value, None)

    @classmethod
    def error(cls, error):
        return cls(None, error)


# === Usage ===

email_result = validate("user@example.com", EmailValidator())
print(email_result._value)  # "user@example.com"

number_result = validate(-5, PositiveNumberValidator())
print(number_result._error)  # "Number must be positive, got -5"
```

## Protocol for Equality

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Equatable(Protocol):
    """Protocol for equality comparison"""

    def __eq__(self, other: object) -> bool: ...


def find_in_list(items: list[Equatable], target: Equatable) -> int:
    """Find index of item in list"""
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1


# Works with any equatable type
numbers = [1, 2, 3, 4, 5]
print(find_in_list(numbers, 3))  # 2

strings = ["a", "b", "c"]
print(find_in_list(strings, "b"))  # 1
```

## Protocol for Ordering

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Ordered(Protocol):
    """Protocol for ordered types"""

    def __lt__(self: T, other: T) -> bool: ...
    def __le__(self: T, other: T) -> bool: ...


def clamp(value: T, min_val: T, max_val: T) -> T:
    """Clamp value between min and max"""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


print(clamp(5, 0, 10))    # 5
print(clamp(-5, 0, 10))   # 0
print(clamp(15, 0, 10))   # 10

# Works with any ordered type
print(clamp("m", "a", "z"))  # "m"
```

## Protocol for Hashing

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Hashable(Protocol):
    """Protocol for hashable types"""

    def __hash__(self) -> int: ...


def create_lookup(items: list[T]) -> dict[int, T]:
    """Create hash-based lookup"""
    return {hash(item): item for item in items}


@dataclass(frozen=True)
class Item:
    id: int
    name: str


items = [Item(1, "a"), Item(2, "b"), Item(3, "c")]
lookup = create_lookup(items)
print(lookup)  # {hash values mapped to Items}
```

## Runtime Protocol Checking

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Renderable(Protocol):
    """Protocol that can be checked at runtime"""

    def render(self) -> str:
        """Render to string"""
        ...


def render_all(items: list[Renderable]) -> list[str]:
    """Render all items"""

    # Filter to only Renderable items at runtime
    valid_items = [item for item in items if isinstance(item, Renderable)]

    return [item.render() for item in valid_items]


class User:
    def __init__(self, name: str):
        self.name = name

    def render(self) -> str:
        return f"User: {self.name}"


class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def render(self) -> str:
        return f"{self.name}: ${self.price}"


# === Usage ===

items = [
    User("Alice"),
    Product("Widget", 9.99),
    "not renderable"  # Will be filtered out
]

print(render_all(items))
# ["User: Alice", "Widget: $9.99"]
```

## Callable Protocol

```python
from typing import Protocol, Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class Transformer(Protocol[T, R]):
    """Protocol for transformation functions"""

    def __call__(self, value: T) -> R:
        """Transform value"""
        ...


def apply_pipeline(value: T, *transforms: Transformer[T, T]) -> T:
    """Apply sequence of transformations"""
    result = value
    for transform in transforms:
        result = transform(result)
    return result


# Various callable objects
add_one = lambda x: x + 1
double = lambda x: x * 2
to_str = lambda x: f"Result: {x}"

result = apply_pipeline(5, add_one, double)
print(result)  # 12
```

## Protocol for State Machines

```python
from typing import Protocol, TypeVar

S = TypeVar('S')
E = TypeVar('E')

class StateMachine(Protocol[S, E]):
    """Protocol for state machines"""

    def current_state(self) -> S:
        """Get current state"""
        ...

    def transition(self, event: E) -> S:
        """Handle event, return new state"""
        ...


def run_machine(machine: StateMachine, events: list) -> None:
    """Run state machine through events"""
    for event in events:
        state = machine.transition(event)
        print(f"Event: {event}, New state: {state}")


class TrafficLight:
    STATES = ['red', 'yellow', 'green']

    def __init__(self):
        self._state_idx = 0

    def current_state(self) -> str:
        return self.STATES[self._state_idx]

    def transition(self, event: str) -> str:
        if event == 'next':
            self._state_idx = (self._state_idx + 1) % len(self.STATES)
        return self.current_state()


# === Usage ===

light = TrafficLight()
run_machine(light, ['next', 'next', 'next'])
# Output:
# Event: next, New state: yellow
# Event: next, New state: green
# Event: next, New state: red
```

## Protocol Composition

```python
from typing import Protocol

class Sized(Protocol):
    def __len__(self) -> int: ...

class Container(Protocol):
    def __contains__(self, item) -> bool: ...

class Iterable(Protocol):
    def __iter__(self): ...

class Collection(Sized, Container, Iterable, Protocol):
    """Full collection protocol combining all"""

    def count(self, item) -> int:
        """Count occurrences"""
        return sum(1 for x in self if x == item)


def count_items(coll: Collection, item) -> int:
    """Count items in any collection"""
    return coll.count(item)


print(count_items([1, 2, 1, 3, 1], 1))  # 3
print(count_items("hello world", "l"))  # 3
```

## DX Benefits

✅ **Flexible**: No inheritance required
✅ **Type-safe**: Static checking with mypy
✅ **Composable**: Combine multiple protocols
✅ **Runtime**: Optional runtime checking
✅ **Documented**: Self-documenting interfaces

## Best Practices

```python
# ✅ Good: Protocol for behavior
class Renderable(Protocol):
    def render(self) -> str: ...

# ✅ Good: Multiple protocol composition
class SizedIterable(Sized, Iterable, Protocol): ...

# ✅ Good: Generic protocols
class Functor(Protocol[T]): ...

# ✅ Good: Runtime checkable when needed
@runtime_checkable
class MyProtocol(Protocol): ...

# ❌ Bad: Protocol with concrete implementations
class BadProtocol(Protocol):
    def render(self):
        return "concrete"  # Should just be interface
```
