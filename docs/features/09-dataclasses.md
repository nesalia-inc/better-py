# Dataclasses - Immutable Structures

Concise, optimized data structures using Python's dataclasses for functional programming.

## Overview

Dataclasses enable:
- Immutable structures in one line
- Automatic `__init__`, `__repr__`, `__eq__`
- Type validation
- Memory optimization with slots
- Easy pattern matching

## Basic Immutable Dataclass

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class Maybe(Generic[T]):
    """Immutable Maybe monad"""

    value: T | None

    def map(self, f):
        if self.value is None:
            return Maybe(None)
        return Maybe(f(self.value))

    def bind(self, f):
        if self.value is None:
            return Maybe(None)
        return f(self.value)


# === Usage ===

maybe1 = Maybe(5)
maybe2 = maybe1.map(lambda x: x * 2)

print(maybe1)  # Maybe(value=5) - unchanged!
print(maybe2)  # Maybe(value=10)

# Immutable - this raises an error
# maybe1.value = 10  # FrozenInstanceError
```

## Default Factories

```python
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True, slots=True)
class Config:
    name: str
    tags: List[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# Each instance gets its own list/dict
config1 = Config("app1")
config2 = Config("app2")

config1.tags.append("important")
config2.tags.append("test")

print(config1.tags)  # ['important']
print(config2.tags)  # ['test'] - independent!
```

## Custom `__post_init__` for Validation

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Email:
    """Validated email value object"""

    address: str

    def __post_init__(self):
        """Validate email after initialization"""
        if not self._is_valid():
            raise ValueError(f"Invalid email: {self.address}")

    def _is_valid(self) -> bool:
        return "@" in self.address and "." in self.address.split("@")[1]


# === Usage ===

valid = Email("user@example.com")  # ✅ Works
print(valid.address)  # "user@example.com"

try:
    invalid = Email("not-an-email")  # ❌ Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

## Functional Updates with `replace`

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
    email: str
    active: bool = True


# Create user
user = User(1, "Alice", "alice@example.com")

# Immutable update - creates new instance
updated = replace(user, name="Alice Smith")

print(user)     # User(id=1, name='Alice', email='alice@example.com', active=True)
print(updated)  # User(id=1, name='Alice Smith', email='alice@example.com', active=True)
```

## Nested Immutable Structures

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True, slots=True)
class Address:
    street: str
    city: str
    country: str


@dataclass(frozen=True, slots=True)
class Person:
    name: str
    address: Address


# Create nested structure
person = Person(
    "Alice",
    Address("123 Main St", "Paris", "France")
)

# Deep update (manual for nested)
new_address = replace(person.address, city="London")
updated_person = replace(person, address=new_address)

print(person.address.city)        # "Paris" - unchanged
print(updated_person.address.city) # "London" - updated
```

## Lenses for Nested Updates

```python
from dataclasses import dataclass, replace
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

@dataclass(frozen=True)
class Lens(Generic[T, U]):
    """Immutable lens for nested access/updates"""

    get: Callable[[T], U]
    set: Callable[[T, U], T]


def lens(path: str) -> Lens:
    """Create lens from dot-notation path"""

    parts = path.split('.')

    def get(obj):
        value = obj
        for part in parts:
            value = getattr(value, part)
        return value

    def set(obj, new_value):
        # Build new object by replacing at path
        current = obj
        updates = {}

        # Navigate to parent
        for part in parts[:-1]:
            current = getattr(current, part)

        # Set leaf
        leaf_attr = parts[-1]
        return replace(current, **{leaf_attr: new_value})

    return Lens(get, set)


# === Usage ===

@dataclass(frozen=True)
class Address:
    city: str

@dataclass(frozen=True)
class Person:
    name: str
    address: Address


person = Person("Alice", Address("Paris"))

# Create lens
city_lens = lens("address.city")

# Get value
print(city_lens.get(person))  # "Paris"

# Update value
updated = city_lens.set(person, "London")
print(updated.address.city)  # "London"
print(person.address.city)   # "Paris" - unchanged
```

## Union Types with Pattern Matching

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True, slots=True)
class Ok:
    value: any
    __match_args__ = ("value",)

@dataclass(frozen=True, slots=True)
class Error:
    error: str
    __match_args__ = ("error",)

Result = Union[Ok, Error]


def handle_result(result: Result) -> str:
    """Pattern match on Result"""
    match result:
        case Ok(value):
            return f"Success: {value}"
        case Error(err):
            return f"Error: {err}"


print(handle_result(Ok(42)))       # "Success: 42"
print(handle_result(Error("fail"))) # "Error: fail"
```

## Generic Immutable Containers

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Iterable

T = TypeVar('T')

@dataclass(frozen=True, slots=True)
class ImmutableList(Generic[T]):
    """Immutable persistent list"""

    _items: tuple[T, ...] = ()

    @classmethod
    def from_iterable(cls, items: Iterable[T]) -> 'ImmutableList[T]':
        return cls(tuple(items))

    def prepend(self, item: T) -> 'ImmutableList[T]':
        return ImmutableList((item,) + self._items)

    def append(self, item: T) -> 'ImmutableList[T]':
        return ImmutableList(self._items + (item,))

    def map(self, f) -> 'ImmutableList':
        return ImmutableList(tuple(f(x) for x in self._items))

    def filter(self, predicate) -> 'ImmutableList':
        return ImmutableList(tuple(x for x in self._items if predicate(x)))

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]


# === Usage ===

lst = ImmutableList.from_iterable([1, 2, 3])
lst2 = lst.prepend(0).append(4)

print(lst)   # ImmutableList(_items=(1, 2, 3))
print(lst2)  # ImmutableList(_items=(0, 1, 2, 3, 4))

lst3 = lst2.map(lambda x: x * 2)
print(lst3)  # ImmutableList(_items=(0, 2, 4, 6, 8))
```

## Value Objects (Equality by Value)

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Money:
    """Value object - equality based on values"""

    amount: int
    currency: str

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)


# === Usage ===

money1 = Money(100, "USD")
money2 = Money(100, "USD")
money3 = Money(200, "USD")

print(money1 == money2)  # True - same values
print(money1 == money3)  # False - different amount

total = money1 + money2
print(total)  # Money(amount=200, currency='USD')
```

## Enumeration as Dataclass

```python
from dataclasses import dataclass
from typing import Literal

Status = Literal['pending', 'running', 'completed', 'failed']

@dataclass(frozen=True, slots=True)
class JobStatus:
    """Type-safe status enumeration"""

    value: Status

    @classmethod
    def pending(cls) -> 'JobStatus':
        return cls('pending')

    @classmethod
    def running(cls) -> 'JobStatus':
        return cls('running')

    @classmethod
    def completed(cls) -> 'JobStatus':
        return cls('completed')

    @classmethod
    def failed(cls) -> 'JobStatus':
        return cls('failed')


# === Usage ===

status1 = JobStatus.pending()
status2 = JobStatus.pending()

print(status1 == status2)  # True
print(status1.value)       # "pending"
```

## Recursive Data Structures

```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True, slots=True)
class Leaf:
    """Binary tree leaf"""

    value: int
    __match_args__ = ("value",)

@dataclass(frozen=True, slots=True)
class Node:
    """Binary tree internal node"""

    left: Union['Node', Leaf]
    right: Union['Node', Leaf]
    __match_args__ = ("left", "right")

Tree = Union[Node, Leaf]


def sum_tree(tree: Tree) -> int:
    """Sum all values in tree"""
    match tree:
        case Leaf(value):
            return value
        case Node(left, right):
            return sum_tree(left) + sum_tree(right)


# === Usage ===

# Tree structure:
#     +
#    / \
#   3   *
#      / \
#     4   5

tree = Node(
    Leaf(3),
    Node(Leaf(4), Leaf(5))
)

print(sum_tree(tree))  # 12
```

## DX Benefits

✅ **Concise**: One line for full class definition
✅ **Immutable**: `frozen=True` prevents mutations
✅ **Efficient**: `slots=True` reduces memory by ~60%
✅ **Type-safe**: Full typing support
✅ **Pattern matching**: Works with `match/case`

## Best Practices

```python
# ✅ Good: Immutable with slots
@dataclass(frozen=True, slots=True)
class MyData: ...

# ✅ Good: Value objects
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

# ✅ Good: Default factories for mutables
@dataclass
class Config:
    items: list = field(default_factory=list)

# ✅ Good: Validation in __post_init__
def __post_init__(self):
    if not self.is_valid():
        raise ValueError(...)

# ❌ Bad: Mutable frozen dataclass
@dataclass(frozen=True)
class Bad:
    items: list = []  # Shared! Use field(default_factory=list)
```
