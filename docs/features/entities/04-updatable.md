# Updatable: Immutable Updates

**Updatable** is a protocol for objects that support **immutable updates** - returning new instances with modified values without changing the original.

## Overview

```python
@runtime_checkable
class Updatable(Protocol[T]):
    """Objects that support immutable updates"""

    def update(self, **kwargs) -> T:
        """Return new instance with updated fields"""
        ...

    def set_in(self, path: str, value: Any) -> T:
        """Immutable deep update using dot notation"""
        ...
```

## Core Concepts

### Immutable Updates

```python
# ❌ Mutable: Changes original
config = {"host": "localhost"}
config["port"] = 5432  # config is modified

# ✅ Immutable: Returns new instance
config = ImmutableDict({"host": "localhost"})
new_config = config.set("port", 5432)  # config unchanged
```

## Implementations

### ImmutableDict

```python
from dataclasses import replace
from copy import deepcopy

@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    """Immutable dictionary with update operations"""

    _data: dict[K, V]

    # === Shallow updates ===

    def set(self, key: K, value: V) -> 'ImmutableDict[K, V]':
        """Return new dict with key set"""
        return ImmutableDict({**self._data, key: value})

    def update(self, **kwargs) -> 'ImmutableDict[K, V]':
        """Return new dict with updates"""
        return ImmutableDict({**self._data, **kwargs})

    def remove(self, key: K) -> 'ImmutableDict[K, V]':
        """Return new dict without key"""
        new_data = {k: v for k, v in self._data.items() if k != key}
        return ImmutableDict(new_data)

    # === Deep updates ===

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

    def update_in(self, path: str, **kwargs) -> 'ImmutableDict[K, V]':
        """Immutable deep update at path"""
        keys = path.split(".")
        new_data = deepcopy(self._data)

        current = new_data
        for key in keys:
            if key not in current:
                current[key] = {}
            current = current[key]

        current.update(kwargs)
        return ImmutableDict(new_data)

    def remove_in(self, path: str) -> 'ImmutableDict[K, V]':
        """Immutable deep removal using dot notation"""
        keys = path.split(".")
        new_data = deepcopy(self._data)

        current = new_data
        for key in keys[:-1]:
            if key not in current:
                return ImmutableDict(new_data)  # Path doesn't exist
            current = current[key]

        if keys[-1] in current:
            del current[keys[-1]]

        return ImmutableDict(new_data)

    # === Merge operations ===

    def merge(self, other: 'ImmutableDict[K, V]') -> 'ImmutableDict[K, V]':
        """Shallow merge (other takes precedence)"""
        return ImmutableDict({**self._data, **other._data})

    def deep_merge(self, other: 'ImmutableDict[K, V]') -> 'ImmutableDict[K, V]':
        """Deep merge for nested dicts"""
        def deep_merge_dict(d1, d2):
            result = dict(d1)
            for key, value in d2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge_dict(result[key], value)
                else:
                    result[key] = value
            return result

        return ImmutableDict(deep_merge_dict(self._data, other._data))

    # === Query operations ===

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._data.get(key, default)

    def get_in(self, path: str, default: Any = None) -> Any:
        """Get value using dot notation"""
        keys = path.split(".")
        current = self._data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default

        return current

    def has(self, key: K) -> bool:
        return key in self._data

    def has_in(self, path: str) -> bool:
        """Check if path exists"""
        keys = path.split(".")
        current = self._data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False

        return True

    # === Conversion ===

    def to_dict(self) -> dict[K, V]:
        return self._data.copy()

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __contains__(self, key: K) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)
```

#### Usage Examples

```python
# Create
config = ImmutableDict({
    "host": "localhost",
    "port": 5432,
    "database": "mydb"
})

# Shallow updates
config2 = config.set("ssl", True)
config3 = config.update(port=3306, ssl=False)

# Original unchanged
config._data  # {"host": "localhost", "port": 5432, "database": "mydb"}

# Deep updates
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "credentials": {
            "username": "admin"
        }
    }
})

config2 = config.set_in("database.port", 5432)
config3 = config.set_in("database.credentials.password", "secret")

# Deep merge
config1 = ImmutableDict({"a": {"x": 1}, "b": 2})
config2 = ImmutableDict({"a": {"y": 2}, "c": 3})
merged = config1.deep_merge(config2)
# {"a": {"x": 1, "y": 2}, "b": 2, "c": 3}

# Get with path
value = config.get_in("database.credentials.username")  # "admin"
exists = config.has_in("database.credentials.password")  # False

# Remove
config2 = config.remove("database")
config3 = config.remove_in("database.credentials.username")
```

### ImmutableList

```python
@dataclass(frozen=True, slots=True)
class ImmutableList(Generic[T]):
    """Immutable list with update operations"""

    _data: list[T]

    # === Update operations ===

    def set(self, index: int, value: T) -> 'ImmutableList[T]':
        """Return new list with element set"""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Index {index} out of range")

        new_data = self._data.copy()
        new_data[index] = value
        return ImmutableList(new_data)

    def update(self, index: int, func: Callable[[T], T]) -> 'ImmutableList[T]':
        """Return new list with element transformed"""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Index {index} out of range")

        new_data = self._data.copy()
        new_data[index] = func(new_data[index])
        return ImmutableList(new_data)

    def insert(self, index: int, value: T) -> 'ImmutableList[T]':
        """Return new list with value inserted"""
        new_data = self._data.copy()
        new_data.insert(index, value)
        return ImmutableList(new_data)

    def append(self, value: T) -> 'ImmutableList[T]':
        """Return new list with value appended"""
        return ImmutableList(self._data + [value])

    def prepend(self, value: T) -> 'ImmutableList[T]':
        """Return new list with value prepended"""
        return ImmutableList([value] + self._data)

    def extend(self, values: list[T]) -> 'ImmutableList[T]':
        """Return new list with values appended"""
        return ImmutableList(self._data + list(values))

    def remove(self, value: T) -> 'ImmutableList[T]':
        """Return new list without value"""
        return ImmutableList([x for x in self._data if x != value])

    def remove_at(self, index: int) -> 'ImmutableList[T]':
        """Return new list without element at index"""
        if index < 0 or index >= len(self._data):
            raise IndexError(f"Index {index} out of range")

        return ImmutableList(self._data[:index] + self._data[index+1:])

    def remove_if(self, predicate: Callable[[T], bool]) -> 'ImmutableList[T]':
        """Return new list without matching elements"""
        return ImmutableList([x for x in self._data if not predicate(x)])

    # === Query ===

    def get(self, index: int, default: T | None = None) -> T | None:
        if 0 <= index < len(self._data):
            return self._data[index]
        return default

    def to_list(self) -> list[T]:
        return self._data.copy()

    def __getitem__(self, index: int) -> T:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
```

#### Usage Examples

```python
# Create
numbers = ImmutableList([1, 2, 3, 4, 5])

# Update
nums2 = numbers.set(2, 10)  # [1, 2, 10, 4, 5]
nums3 = numbers.update(2, lambda x: x * 2)  # [1, 2, 6, 4, 5]

# Insert
nums2 = numbers.insert(2, 99)  # [1, 2, 99, 3, 4, 5]
nums3 = numbers.append(6)  # [1, 2, 3, 4, 5, 6]
nums4 = numbers.prepend(0)  # [0, 1, 2, 3, 4, 5]

# Remove
nums2 = numbers.remove(3)  # [1, 2, 4, 5]
nums3 = numbers.remove_at(2)  # [1, 2, 4, 5]
nums4 = numbers.remove_if(lambda x: x % 2 == 0)  # [1, 3, 5]
```

### ImmutableDataclass (Mixin)

```python
@dataclass(frozen=True, slots=True)
class ImmutableDataclass:
    """Mixin for immutable dataclasses with update methods"""

    def with_(self, **kwargs) -> 'ImmutableDataclass':
        """Return new instance with updated fields"""
        return replace(self, **kwargs)

    def with_fields(self, updates: dict[str, Any]) -> 'ImmutableDataclass':
        """Return new instance with fields from dict"""
        return replace(self, **updates)

# Usage
@dataclass(frozen=True, slots=True)
class User(ImmutableDataclass):
    id: int
    name: str
    email: str
    active: bool = True

user = User(1, "Alice", "alice@example.com")
updated = user.with_(name="Bob", active=False)
# User(1, "Bob", "alice@example.com", active=False)

# Original unchanged
user.name  # "Alice"
```

## Advanced Patterns

### Patch Updates

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    _data: dict[K, V]

    def patch(self, patch: 'Patch') -> 'ImmutableDict[K, V]':
        """Apply JSON patch (RFC 6902)"""
        result = dict(self._data)

        for op in patch.operations:
            if op.op == "add":
                self._apply_add(result, op)
            elif op.op == "remove":
                self._apply_remove(result, op)
            elif op.op == "replace":
                self._apply_replace(result, op)
            elif op.op == "move":
                self._apply_move(result, op)
            elif op.op == "copy":
                self._apply_copy(result, op)
            elif op.op == "test":
                if not self._apply_test(result, op):
                    raise ValueError(f"Patch test failed: {op.path}")

        return ImmutableDict(result)

    def _apply_add(self, data: dict, op: PatchOp):
        path = op.path.lstrip("/").split("/")
        current = data
        for key in path[:-1]:
            current = current[key]

        current[path[-1]] = op.value

    # ... other apply methods
```

### Lens-Based Updates

```python
def lens(path: str) -> Callable[[ImmutableDict, Any], ImmutableDict]:
    """Create lens update function"""
    def update(obj: ImmutableDict, value: Any) -> ImmutableDict:
        return obj.set_in(path, value)
    return update

# Usage
config = ImmutableDict({"database": {"host": "localhost"}})
host_lens = lens("database.host")
updated = host_lens(config, "remotehost")
```

### Transactional Updates

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    _data: dict[K, V]
    _pending: dict = field(default_factory=dict)

    def transaction(self) -> 'ImmutableTransaction':
        """Start transaction"""
        return ImmutableTransaction(self)

@dataclass
class ImmutableTransaction(Generic[K, V]):
    _original: ImmutableDict[K, V]
    _updates: dict[K, V] = field(default_factory=dict)

    def set(self, key: K, value: V) -> 'ImmutableTransaction':
        self._updates[key] = value
        return self

    def remove(self, key: K) -> 'ImmutableTransaction':
        self._updates[key] = None  # Marker for removal
        return self

    def commit(self) -> ImmutableDict[K, V]:
        """Apply all updates atomically"""
        new_data = dict(self._original._data)

        for key, value in self._updates.items():
            if value is None:
                new_data.pop(key, None)
            else:
                new_data[key] = value

        return ImmutableDict(new_data)

# Usage
config = ImmutableDict({"a": 1, "b": 2})

config2 = (
    config
    .transaction()
    .set("c", 3)
    .set("d", 4)
    .remove("a")
    .commit()
)
# {"b": 2, "c": 3, "d": 4}
```

## Protocol Compliance

```python
@runtime_checkable
class Updatable(Protocol[T]):
    def update(self, **kwargs) -> T: ...
    def set_in(self, path: str, value: Any) -> T: ...

class CustomUpdatable:
    def __init__(self, data):
        self._data = data

    def update(self, **kwargs):
        return CustomUpdatable({**self._data, **kwargs})

    def set_in(self, path: str, value: Any):
        keys = path.split(".")
        new_data = deepcopy(self._data)
        current = new_data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return CustomUpdatable(new_data)

# CustomUpdatable is Updatable!
isinstance(CustomUpdatable({}), Updatable)  # True
```

## Best Practices

### ✅ Do: Always return new instances

```python
# Good: Returns new instance
def set(self, key, value):
    return ImmutableDict({**self._data, key: value})
```

### ✅ Do: Use dataclasses.replace for frozen classes

```python
# Good
updated = replace(self, field=new_value)
```

### ❌ Don't: Mutate internal state

```python
# Bad: Mutates!
def set(self, key, value):
    self._data[key] = value
    return self
```

## Summary

**Updatable** protocol:
- ✅ Immutable updates with `update()` / `set()`
- ✅ Deep updates with `set_in()` / `update_in()`
- ✅ Deep merge with `deep_merge()`
- ✅ Transactional updates
- ✅ Lens-based updates

**Implementations**:
- `ImmutableDict[K, V]` - Immutable dictionary
- `ImmutableList[T]` - Immutable list
- `ImmutableDataclass` - Mixin for dataclasses

**Key principle**: **Never mutate**, always return **new instances**.

---

**Next**: See [Traversable](./05-traversable.md) for traversable collections.
