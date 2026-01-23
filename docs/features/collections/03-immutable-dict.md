# ImmutableDict: Immutable Dictionary with Deep Updates

An immutable dictionary with deep update capabilities using dot notation for nested structures.

## Overview

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(Generic[K, V]):
    """Immutable dictionary with deep update operations"""
    _data: dict[K, V]
```

## Key Features

- ✅ **Immutable**: All operations return new instances
- ✅ **Deep updates**: Update nested values with dot notation
- ✅ **Deep merge**: Recursively merge nested dicts
- ✅ **Type-safe**: Generic types
- ✅ **Frozen**: `@dataclass(frozen=True)` prevents mutation

## Creation

```python
from mfn.collections import ImmutableDict

# From dict
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Empty
empty = ImmutableDict.empty()

# With defaults
config = ImmutableDict.with_defaults({
    "host": "localhost",
    "port": 5432
})
```

## Shallow Updates

### set

```python
config = ImmutableDict({
    "host": "localhost",
    "port": 5432
})

# Set new key
config2 = config.set("ssl", True)
# {"host": "localhost", "port": 5432, "ssl": True}

# Update existing key
config3 = config2.set("port", 3306)
# {"host": "localhost", "port": 3306, "ssl": True}

# Original unchanged
config._data  # {"host": "localhost", "port": 5432}
```

### update

```python
config = ImmutableDict({"host": "localhost"})

# Update multiple
config2 = config.update(
    port=5432,
    ssl=True,
    timeout=30
)
# {"host": "localhost", "port": 5432, "ssl": True, "timeout": 30}
```

### remove

```python
data = ImmutableDict({
    "a": 1,
    "b": 2,
    "c": 3
})

# Remove key
data2 = data.remove("b")
# {"a": 1, "c": 3}

# Original unchanged
data._data  # {"a": 1, "b": 2, "c": 3}
```

## Deep Updates

### set_in

```python
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "credentials": {
            "username": "admin"
        }
    }
})

# Deep set with dot notation
config2 = config.set_in("database.port", 5432)
# {
#     "database": {
#         "host": "localhost",
#         "credentials": {"username": "admin"},
#         "port": 5432  # ← Added
#     }
# }

config3 = config.set_in("database.credentials.password", "secret")
# {
#     "database": {
#         "host": "localhost",
#         "credentials": {
#             "username": "admin",
#             "password": "secret"  # ← Added
#         }
#     }
# }
```

### update_in

```python
config = ImmutableDict({
    "database": {
        "host": "localhost"
    }
})

# Update nested dict
config2 = config.update_in("database", port=5432, ssl=True)
# {
#     "database": {
#         "host": "localhost",
#         "port": 5432,
#         "ssl": True
#     }
# }
```

### remove_in

```python
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    }
})

# Remove nested key
config2 = config.remove_in("database.credentials.password")
# {
#     "database": {
#         "host": "localhost",
#         "port": 5432,
#         "credentials": {"username": "admin"}
#     }
# }
```

## Merge Operations

### merge

```python
defaults = ImmutableDict({
    "host": "localhost",
    "port": 5432
})

overrides = ImmutableDict({
    "port": 3306,
    "ssl": True
})

# Shallow merge (overrides win)
merged = defaults.merge(overrides)
# {"host": "localhost", "port": 3306, "ssl": True}
```

### deep_merge

```python
config1 = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "cache": {"enabled": True}
})

config2 = ImmutableDict({
    "database": {
        "port": 3306,
        "ssl": True
    }
})

# Deep merge
merged = config1.deep_merge(config2)
# {
#     "database": {
#         "host": "localhost",  # ← Kept
#         "port": 3306,        # ← Overridden
#         "ssl": True          # ← Added
#     },
#     "cache": {"enabled": True}
# }
```

## Query Operations

### get

```python
config = ImmutableDict({
    "host": "localhost",
    "port": 5432
})

# Get value
host = config.get("host")  # "localhost"

# With default
timeout = config.get("timeout", 30)  # 30
```

### get_in

```python
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "credentials": {
            "username": "admin"
        }
    }
})

# Deep get
host = config.get_in("database.host")  # "localhost"
username = config.get_in("database.credentials.username")  # "admin"

# With default
password = config.get_in("database.credentials.password", "default")  # "default"

# Missing path returns default
missing = config.get_in("database.unknown.key", None)  # None
```

### has / has_in

```python
config = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Has key
config.has("database")  # True
config.has("ssl")  # False

# Has path
config.has_in("database.host")  # True
config.has_in("database.password")  # False
```

## Conversion

```python
data = ImmutableDict({"a": 1, "b": 2})

# To Python dict
python_dict = data.to_dict()  # {"a": 1, "b": 2}

# To JSON
import json
json_str = json.dumps(data._data)

# From JSON
json_data = '{"a": 1, "b": 2}'
restored = ImmutableDict.from_json(json_data)
```

## Information

```python
data = ImmutableDict({"a": 1, "b": 2, "c": 3})

# Size
len(data)  # 3
data.size()  # 3

# Check if empty
data.is_empty()  # False

# Boolean
bool(data)  # True
bool(ImmutableDict({}))  # False
```

## Use Cases

### Configuration Management

```python
# Default config
defaults = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "pool_size": 10
    },
    "cache": {
        "enabled": True,
        "ttl": 300
    }
})

# Environment-specific
prod = defaults
    .set_in("database.host", "prod-db.example.com")
    .set_in("database.pool_size", 50)
    .set_in("cache.ttl", 600)

# Original unchanged
defaults.get_in("database.host")  # "localhost"
```

### State Management

```python
# Initial state
state = ImmutableDict({
    "user": None,
    "loading": False,
    "error": None
})

# Loading
state = state.update(loading=True)

# Success
state = state.update(
    loading=False,
    user={"id": 1, "name": "Alice"}
)

# Error
state = state.update(
    loading=False,
    error={"message": "Failed to load"}
)
```

### Immutable Updates Pattern

```python
# Function that updates config
def set_database_url(config: ImmutableDict, url: str) -> ImmutableDict:
    return config.set_in("database.url", url)

# Chain updates
config = (
    ImmutableDict.empty()
    .pipe(set_database_url, "postgresql://localhost/db")
    .set_in("database.pool_size", 20)
    .set_in("cache.enabled", True)
)
```

## Advanced Patterns

### Patch Updates

```python
@dataclass
class Patch:
    """JSON Patch operation"""
    op: str  # "add", "remove", "replace", "move", "copy", "test"
    path: str
    value: Any = None

@dataclass
class ImmutableDict(Generic[K, V]):
    _data: dict[K, V]

    def apply_patch(self, patch: Patch) -> 'ImmutableDict[K, V]':
        """Apply JSON Patch (RFC 6902)"""
        if patch.op == "add":
            return self.set_in(patch.path, patch.value)
        elif patch.op == "remove":
            return self.remove_in(patch.path)
        elif patch.op == "replace":
            return self.set_in(patch.path, patch.value)
        # ... other operations
```

### Lenses

```python
def lens(path: str) -> Callable[[ImmutableDict, Any], ImmutableDict]:
    """Create lens for deep access"""
    def getter(obj: ImmutableDict) -> Any:
        return obj.get_in(path)

    def setter(obj: ImmutableDict, value: Any) -> ImmutableDict:
        return obj.set_in(path, value)

    return (getter, setter)

# Usage
host_lens = lens("database.host")
getter, setter = host_lens

host = getter(config)  # "localhost"
config2 = setter(config, "remotehost")
```

### Transactional Updates

```python
@dataclass
class DictTransaction(Generic[T]):
    original: ImmutableDict
    pending: dict = field(default_factory=dict)

    def set(self, key: str, value: T) -> 'DictTransaction':
        self.pending[key] = value
        return self

    def commit(self) -> ImmutableDict:
        """Apply all updates atomically"""
        return self.original.update(**self.pending)

# Usage
transaction = DictTransaction(config)
config2 = (
    transaction
    .set("a", 1)
    .set("b", 2)
    .set("c", 3)
    .commit()
)
```

## Performance Considerations

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `get()` | O(1) | Hash lookup |
| `set()` | O(n) | Copies entire dict |
| `set_in()` | O(n) | Deep copy |
| `merge()` | O(n+m) | Both dicts |
| `deep_merge()` | O(n+m) | Recursive copy |

**Note**: For large dictionaries with frequent updates, consider using mutable structures with copy-on-write or alternative persistent data structures.

## Best Practices

### ✅ Do: Use for configuration/state

```python
# Good: Immutable config
config = ImmutableDict({"host": "localhost"})
config2 = config.set("port", 5432)
```

### ✅ Do: Chain updates

```python
# Good: Atomic update
config2 = config.set("a", 1).set("b", 2).set("c", 3)
```

### ❌ Don't: Mutate after creation

```python
# Bad: Trying to mutate
config._data["key"] = "value"  # ❌ FrozenInstanceError!

# Good: Create new instance
config2 = config.set("key", "value")
```

### ❌ Don't: Use for frequently changing data

```python
# Bad: Many updates per second
for i in range(10000):
    config = config.set("counter", i)  # Creates 10000 copies!

# Better: Use mutable dict for counters
counter = {"value": 0}
counter["value"] += 1
```

## Examples

### Multi-Layer Configuration

```python
# Base config
base = ImmutableDict({
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Development overrides
dev = base.deep_merge(ImmutableDict({
    "database": {
        "host": "dev-db.example.com",
        "log_level": "debug"
    }
}))

# Production overrides
prod = base.deep_merge(ImmutableDict({
    "database": {
        "host": "prod-db.example.com",
        "ssl": True,
        "pool_size": 50
    }
}))

# All three independent
base.get_in("database.host")  # "localhost"
dev.get_in("database.host")   # "dev-db.example.com"
```

### Form State

```python
# Initial form state
form = ImmutableDict({
    "name": "",
    "email": "",
    "age": 0,
    "errors": {}
})

# Update field
form = form.set("name", "Alice")

# Add error
form = form.set_in("errors.name", "Required")

# Clear errors
form = form.set("errors", {})

# Submit
if not form.get_in("errors"):
    data = form.remove("errors")
```

## See Also

- [Core: Immutability](../core/03-immutability.md) - Immutability patterns
- [Entities: Updatable](../entities/04-updatable.md) - Update protocol
- [MappableDict](./02-mappable-dict.md) - Functional dict with map/filter
- [ImmutableList](./04-immutable-list.md) - Immutable list

---

**Next**: [ImmutableList](./04-immutable-list.md)
