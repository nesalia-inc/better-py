# Immutability: Patterns in Python

Immutability is a core principle of functional programming. In Python, we achieve immutability through **frozen dataclasses**, **tuples**, and **copy-on-write** patterns.

## Why Immutability?

### Benefits

- ✅ **Predictable**: Objects don't change under you
- ✅ **Thread-safe**: No race conditions
- ✅ **Easier to reason**: No hidden state changes
- ✅ **Better testing**: No side effects to track
- ✅ **Time-travel debugging**: Can keep history of changes

### Example

```python
# ❌ Mutable: Hard to track changes
config = {"host": "localhost"}
config["port"] = 5432
# Where did config["port"] come from?

# ✅ Immutable: Clear transformation
config1 = ImmutableDict({"host": "localhost"})
config2 = config1.set("port", 5432)
# config2 is explicitly derived from config1
```

## Immutable Patterns in Python

### 1. Frozen Dataclasses

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class User:
    """Immutable user entity"""
    id: int
    name: str
    email: str

# Can't modify
user = User(1, "Alice", "alice@example.com")
user.name = "Bob"  # ❌ FrozenInstanceError!

# Create new instance instead
updated_user = User(user.id, "Bob", user.email)  # ✅
```

**With default values and methods**:

```python
@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
    email: str
    active: bool = True

    def with_name(self, name: str) -> 'User':
        """Return new User with different name"""
        return User(self.id, name, self.email, self.active)

    def activate(self) -> 'User':
        """Return new activated User"""
        return User(self.id, self.name, self.email, True)

    def deactivate(self) -> 'User':
        """Return new deactivated User"""
        return User(self.id, self.name, self.email, False)

# Usage
user = User(1, "Alice", "alice@example.com")
active_user = user.activate()
renamed_user = user.with_name("Bob")

# Original unchanged
user.active  # True (default)
user.name  # "Alice"
```

### 2. NamedTuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    """Immutable 2D point"""
    x: float
    y: float

    def move(self, dx: float, dy: float) -> 'Point':
        """Return new Point moved by dx, dy"""
        return Point(self.x + dx, self.y + dy)

    def scale(self, factor: float) -> 'Point':
        """Return new Point scaled by factor"""
        return Point(self.x * factor, self.y * factor)

# Usage
p1 = Point(1.0, 2.0)
p2 = p1.move(1.0, 1.0)  # Point(2.0, 3.0)
p3 = p2.scale(2.0)     # Point(4.0, 6.0)

# p1 unchanged
print(p1)  # Point(x=1.0, y=2.0)
```

### 3. Immutable Collections

#### ImmutableDict

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    """Immutable dictionary"""

    _data: dict[K, V]

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._data.get(key, default)

    def update(self, **kwargs) -> 'ImmutableDict[K, V]':
        """Return NEW dict with updates"""
        return ImmutableDict({**self._data, **kwargs})

    def set(self, key: K, value: V) -> 'ImmutableDict[K, V]':
        """Return NEW dict with key set"""
        return ImmutableDict({**self._data, key: value})

    def remove(self, key: K) -> 'ImmutableDict[K, V]':
        """Return NEW dict without key"""
        new_data = {k: v for k, v in self._data.items() if k != key}
        return ImmutableDict(new_data)

    def merge(self, other: 'ImmutableDict[K, V]') -> 'ImmutableDict[K, V]':
        """Return NEW dict merged with other"""
        return ImmutableDict({**self._data, **other._data})

# Usage
config = ImmutableDict({"host": "localhost", "port": 5432})
config2 = config.set("ssl", True)
config3 = config2.update(port=3306)

# Each is independent
config._data    # {"host": "localhost", "port": 5432}
config2._data   # {"host": "localhost", "port": 5432, "ssl": True}
config3._data   # {"host": "localhost", "port": 3306, "ssl": True}
```

#### ImmutableList

```python
@dataclass(frozen=True, slots=True)
class ImmutableList(Generic[T]):
    """Immutable list"""

    _data: list[T]

    def append(self, item: T) -> 'ImmutableList[T]':
        """Return NEW list with item appended"""
        return ImmutableList(self._data + [item])

    def prepend(self, item: T) -> 'ImmutableList[T]':
        """Return NEW list with item prepended"""
        return ImmutableList([item] + self._data)

    def extend(self, items: list[T]) -> 'ImmutableList[T]':
        """Return NEW list with items extended"""
        return ImmutableList(self._data + list(items))

    def remove(self, item: T) -> 'ImmutableList[T]':
        """Return NEW list without item"""
        return ImmutableList([x for x in self._data if x != item])

    def filter(self, predicate: Callable[[T], bool]) -> 'ImmutableList[T]':
        """Return NEW list with filtered items"""
        return ImmutableList([x for x in self._data if predicate(x)])

    def map(self, func: Callable[[T], U]) -> 'ImmutableList[U]':
        """Return NEW list with mapped items"""
        return ImmutableList([func(x) for x in self._data])

# Usage
numbers = ImmutableList([1, 2, 3])
nums2 = numbers.append(4)
nums3 = nums2.map(lambda x: x * 2)

numbers._data   # [1, 2, 3]
nums2._data     # [1, 2, 3, 4]
nums3._data     # [2, 4, 6, 8]
```

### 4. Copy-on-Write Pattern

When immutability is too expensive, use copy-on-write:

```python
@dataclass
class CopyOnWriteList(Generic[T]):
    """List that copies only when modified"""

    _data: list[T]
    _version: int = field(default=0, compare=False)
    _copies: dict = field(default_factory=dict, compare=False)

    def __post_init__(self):
        self._copies[id(self._data)] = self._data.copy()

    def append(self, item: T) -> 'CopyOnWriteList[T]':
        # Copy only if this instance has unique data
        if id(self._data) in self._copies and len(self._copies) == 1:
            # Safe to modify in place
            self._data.append(item)
            return self
        else:
            # Copy first
            new_data = self._data.copy()
            new_list = CopyOnWriteList(new_data)
            new_list._data.append(item)
            return new_list

# Usage
original = CopyOnWriteList([1, 2, 3])
ref1 = original  # Same data
ref2 = original  # Same data

# First modification copies
modified = ref1.append(4)
# original._data is [1, 2, 3]
# modified._data is [1, 2, 3, 4]
```

### 5. ImmutableBuilder Pattern

For building immutable objects incrementally:

```python
@dataclass
class UserBuilder:
    """Builder for immutable User"""
    id: int | None = None
    name: str | None = None
    email: str | None = None
    active: bool = True

    def with_id(self, id: int) -> 'UserBuilder':
        return UserBuilder(id, self.name, self.email, self.active)

    def with_name(self, name: str) -> 'UserBuilder':
        return UserBuilder(self.id, name, self.email, self.active)

    def with_email(self, email: str) -> 'UserBuilder':
        return UserBuilder(self.id, self.name, email, self.active)

    def build(self) -> User:
        if None in (self.id, self.name, self.email):
            raise ValueError("Missing required fields")
        return User(self.id, self.name, self.email, self.active)

# Usage
user = (
    UserBuilder()
    .with_id(1)
    .with_name("Alice")
    .with_email("alice@example.com")
    .build()
)
```

### 6. @replace Decorator Pattern

For creating modified copies:

```python
from dataclasses import replace

@dataclass(frozen=True, slots=True)
class Config:
    host: str = "localhost"
    port: int = 5432
    ssl: bool = False
    timeout: int = 30

# Create modified copies
config = Config()

config_with_ssl = replace(config, ssl=True)
config_custom = replace(config, host="remote", port=3306)

# Each is independent
config.port           # 5432
config_with_ssl.port  # 5432 (ssl=True)
config_custom.port    # 3306 (host="remote")
```

### 7. Immutable Nested Updates

Deep updates without mutation:

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    _data: dict[K, V]

    def set_in(self, path: str, value: Any) -> 'ImmutableDict[K, V]':
        """Immutable deep update using dot notation"""
        keys = path.split(".")
        new_data = deepcopy(self._data)

        current = new_data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
        return ImmutableDict(new_data)

# Usage
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "credentials": {
            "username": "admin"
        }
    }
})

config2 = config.set_in("database.port", 5432)
config3 = config2.set_in("database.credentials.password", "secret")

# Original unchanged
config._data  # {"database": {"host": "localhost", "credentials": {"username": "admin"}}}
config3._data  # {"database": {"host": "localhost", "credentials": {"username": "admin", "password": "secret"}, "port": 5432}
```

## Performance Considerations

### When to Use Immutability

✅ **Use immutability when**:
- Small to medium objects
- Shared state across threads
- Complex state machines
- Audit trails needed
- Predictable behavior is critical

❌ **Avoid immutability when**:
- Very large data structures (>100MB)
- Performance-critical inner loops
- Memory is constrained
- Frequent modifications of large objects

### Optimization: Structural Sharing

```python
@dataclass(frozen=True, slots=True)
class PersistentList(Generic[T]):
    """Persistent list with structural sharing"""

    _head: T | None
    _tail: 'PersistentList[T] | None'
    _length: int

    def prepend(self, item: T) -> 'PersistentList[T]':
        """O(1) - shares tail"""
        return PersistentList(item, self, self._length + 1)

    def append(self, item: T) -> 'PersistentList[T]':
        """O(n) - must copy entire list"""
        if self._tail is None:
            return PersistentList(self._head, PersistentList(item, None, 1), 2)
        return PersistentList(self._head, self._tail.append(item), self._length + 1)

# prepend is O(1) - shares structure
lst = PersistentList(3, None, 1)
lst2 = lst.prepend(2)  # Shares original
lst3 = lst2.prepend(1)  # Shares lst2

# append is O(n) - copies
lst4 = lst.append(4)  # Copies entire list
```

## Best Practices

### ✅ Do: Use frozen dataclasses

```python
@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
```

### ✅ Do: Return new instances

```python
def with_name(self, name: str) -> 'User':
    return User(self.id, name, self.email)
```

### ✅ Do: Use @replace for copies

```python
new_user = replace(user, name="Bob")
```

### ❌ Don't: Mix mutable and immutable

```python
@dataclass(frozen=True)
class Bad:
    items: list  # ❌ List is mutable!

# Better
@dataclass(frozen=True)
class Good:
    items: tuple  # ✅ Tuple is immutable
```

### ❌ Don't: Return self from mutations

```python
def set_name(self, name: str) -> 'User':  # ❌ Returns self
    self.name = name  # ❌ Mutates!
    return self
```

## Summary

**Immutability in Python**:
- `@dataclass(frozen=True, slots=True)` - Main pattern
- `NamedTuple` - Lightweight immutable records
- Immutable collections - Dict, List with copy-on-write
- `replace()` - Create modified copies
- Builder pattern - Construct immutable objects
- Structural sharing - Optimize performance

**Key principle**: Methods **never mutate**, they **return new instances**.

---

**Next**: See [Generic Types](./04-generic-types.md) for type-safe entities.
