# Lenses - Immutable Deep Updates

Update nested data structures immutably with path-based accessors and shared memory.

## Overview

Lenses enable:
- Deep updates without copying entire structures
- Path-based access to nested properties
- Immutable updates with structural sharing
- Composable accessors
- Type-safe navigation

## Basic Lens

```python
from dataclasses import dataclass, replace
from typing import Callable, TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')

@dataclass(frozen=True)
class Lens(Generic[T, U]):
    """Immutable lens for accessing and updating nested values"""

    get: Callable[[T], U]
    set: Callable[[T, U], T]

    def __rshift__(self, other: 'Lens[U, V]') -> 'Lens[T, V]':
        """Compose lenses: lens1 >> lens2"""
        def get(obj):
            return other.get(self.get(obj))

        def set(obj, value):
            inner = self.get(obj)
            updated = other.set(inner, value)
            return self.set(obj, updated)

        return Lens(get, set)


# === Usage ===

@dataclass(frozen=True)
class Address:
    city: str
    country: str

@dataclass(frozen=True)
class User:
    name: str
    address: Address

# Create lenses
address_lens = Lens(
    get=lambda user: user.address,
    set=lambda user, addr: replace(user, address=addr)
)

city_lens = Lens(
    get=lambda addr: addr.city,
    set=lambda addr, city: replace(addr, city=city)
)

# Compose to create deep lens
user_city_lens = address_lens >> city_lens

# Get deep value
user = User("Alice", Address("Paris", "France"))
print(user_city_lens.get(user))  # "Paris"

# Update immutably
updated = user_city_lens.set(user, "London")
print(user.address.city)        # "Paris" - unchanged
print(updated.address.city)     # "London" - updated
```

## Path-Based Lens Builder

```python
from typing import Any

def lens_path(path: str) -> Lens:
    """Create lens from dot-notation path"""

    def get(obj: Any) -> Any:
        value = obj
        for part in path.split('.'):
            value = getattr(value, part)
        return value

    def set(obj: Any, new_value: Any) -> Any:
        parts = path.split('.')

        # Navigate to parent
        current = obj
        for part in parts[:-1]:
            current = getattr(current, part)

        # Replace leaf
        leaf_attr = parts[-1]
        return replace(current, **{leaf_attr: new_value})

    return Lens(get, set)


# === Usage ===

user = User("Alice", Address("Paris", "France"))

city = lens_path("address.city")
print(city.get(user))  # "Paris"

updated = city.set(user, "London")
print(updated.address.city)  # "London"
```

## List Index Lenses

```python
def lens_index(index: int) -> Lens:
    """Lens for list index"""

    def get(obj: list) -> Any:
        return obj[index]

    def set(obj: list, value: Any) -> list:
        new_list = obj.copy()
        new_list[index] = value
        return new_list

    return Lens


# === Usage ===

numbers = [1, 2, 3, 4, 5]

first = lens_index(0)
third = lens_index(2)

print(first.get(numbers))  # 1
print(third.get(numbers))  # 3

updated = third.set(numbers, 30)
print(numbers)  # [1, 2, 3, 4, 5] - unchanged
print(updated)  # [1, 2, 30, 4, 5] - updated
```

## Dictionary Key Lenses

```python
def lens_key(key: str) -> Lens:
    """Lens for dictionary key"""

    def get(obj: dict) -> Any:
        return obj.get(key)

    def set(obj: dict, value: Any) -> dict:
        new_dict = obj.copy()
        new_dict[key] = value
        return new_dict

    return Lens


# === Usage ===

data = {"name": "Alice", "age": 30, "city": "Paris"}

name = lens_key("name")
age = lens_key("age")

print(name.get(data))  # "Alice"
print(age.get(data))   # 30

updated = name.set(data, "Bob")
print(data)    # {"name": "Alice", ...} - unchanged
print(updated) # {"name": "Bob", ...} - updated
```

## Over Operation (Modify)

```python
def over(lens: Lens, func: Callable) -> Callable:
    """Apply function to lens focus"""

    def modifier(obj):
        current = lens.get(obj)
        new_value = func(current)
        return lens.set(obj, new_value)

    return modifier


# === Usage ===

user = User("Alice", Address("Paris", "France"))

# Modify city to uppercase
uppercase_city = over(user_city_lens, str.upper)
updated = uppercase_city(user)
print(updated.address.city)  # "PARIS"

# Modify name
name_lens = lens_path("name")
capitalize = over(name_lens, str.capitalize)
updated2 = capitalize(user)
print(updated2.name)  # "Alice" (if was "alice")
```

## Multiple Updates

```python
def update_all(obj: T, *updates: Callable[[T], T]) -> T:
    """Apply multiple lens updates"""

    result = obj
    for update in updates:
        result = update(result)
    return result


# === Usage ===

user = User("alice", Address("paris", "france"))

updated = update_all(
    user,
    over(lens_path("name"), str.capitalize),
    over(lens_path("address.city"), str.capitalize),
    over(lens_path("address.country"), str.capitalize),
)

print(updated)
# User(name="Alice", address=Address(city="Paris", country="France"))
```

## Optional Path Lenses

```python
def lens_path_safe(path: str) -> Lens:
    """Lens that returns Maybe for safe navigation"""

    def get(obj: Any) -> Maybe:
        try:
            value = obj
            for part in path.split('.'):
                value = getattr(value, part)
            return Maybe.some(value)
        except (AttributeError, TypeError):
            return Maybe.none()

    def set(obj: Any, new_value: Any) -> Any:
        return lens_path(path).set(obj, new_value)

    return Lens(get, set)


# === Usage ===

maybe_city = lens_path_safe("address.city").get(user)
if maybe_city:
    print(f"City: {maybe_city.unwrap()}")
else:
    print("No city")
```

## Lens Combinators

```python
class LensCombinator:
    """Helper for lens operations"""

    @staticmethod
    def compose(*lenses: Lens) -> Lens:
        """Compose multiple lenses"""
        result = lenses[0]
        for lens in lenses[1:]:
            result = result >> lens
        return result

    @staticmethod
    def attr(name: str) -> Lens:
        """Create attribute lens"""
        return Lens(
            get=lambda obj: getattr(obj, name),
            set=lambda obj, value: replace(obj, **{name: value})
        )

    @staticmethod
    def index(i: int) -> Lens:
        """Create index lens"""
        return lens_index(i)

    @staticmethod
    def key(k: str) -> Lens:
        """Create key lens"""
        return lens_key(k)


# === Usage ===

# Compose using helper
city_lens = LensCombinator.compose(
    LensCombinator.attr("address"),
    LensCombinator.attr("city")
)

print(city_lens.get(user))  # "Paris"
```

## Update Helper Function

```python
def update_in(obj: T, path: str, value: Any) -> T:
    """Simple path-based update"""

    return lens_path(path).set(obj, value)


def modify_in(obj: T, path: str, func: Callable) -> T:
    """Simple path-based modification"""

    lens = lens_path(path)
    current = lens.get(obj)
    return lens.set(obj, func(current))


# === Usage ===

user = User("Alice", Address("Paris", "France"))

# Simple update
updated = update_in(user, "address.city", "London")

# Simple modification
updated2 = modify_in(user, "name", str.upper)
print(updated2.name)  # "ALICE"
```

## Traversals (Multi-Focus)

```python
class Traversal(Generic[T, U]):
    """Lens-like structure for multiple values"""

    def __init__(self, get_all: Callable[[T], list[U]], set_all: Callable[[T, list[U]], T]):
        self.get_all = get_all
        self.set_all = set_all

    def to_list(self, obj: T) -> list[U]:
        return self.get_all(obj)

    def update(self, obj: T, func: Callable) -> T:
        values = self.get_all(obj)
        updated = [func(v) for v in values]
        return self.set_all(obj, updated)


def traversal_all() -> Traversal:
    """Traversal that modifies all list items"""

    def get_all(obj: list) -> list:
        return obj

    def set_all(obj: list, values: list) -> list:
        return values

    return Traversal(get_all, set_all)


def traversal_filter(predicate: Callable) -> Traversal:
    """Traversal that only modifies matching items"""

    def get_all(obj: list) -> list:
        return [item for item in obj if predicate(item)]

    def set_all(obj: list, values: list) -> list:
        result = []
        value_iter = iter(values)
        for item in obj:
            if predicate(item):
                result.append(next(value_iter))
            else:
                result.append(item)
        return result

    return Traversal(get_all, set_all)


# === Usage ===

numbers = [1, 2, 3, 4, 5]

# Double all evens
evens = traversal_filter(lambda x: x % 2 == 0)
updated = evens.update(numbers, lambda x: x * 2)
print(updated)  # [1, 4, 3, 8, 5]
```

## DX Benefits

✅ **Immutable**: No mutation, always new objects
✅ **Efficient**: Structural sharing, not full copies
✅ **Composable**: Combine lenses for deep access
✅ **Type-safe**: Works with static type checkers
✅ **Simple**: Path-based notation

## Best Practices

```python
# ✅ Good: Path lenses for simple cases
city = lens_path("address.city")

# ✅ Good: Reusable lens definitions
user_city = lens_path("address.city")

# ✅ Good: Named modifications
uppercase_city = over(user_city, str.upper)

# ❌ Bad: Creating new lenses repeatedly
# Reuse lens definitions instead
```
