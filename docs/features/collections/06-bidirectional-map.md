# BiDirectionalMap: Two-Way Dictionary Lookup

A bidirectional map allowing efficient lookup by both key and value with automatic consistency.

## Overview

```python
@dataclass(frozen=True, slots=True)
class BiDirectionalMap(Generic[K, V]):
    """Dictionary with reverse lookup"""
    _forward: dict[K, V]
    _reverse: dict[V, K]
```

## Key Features

- ✅ **Bidirectional**: Lookup by key or value
- ✅ **Consistent**: Forward and reverse always synced
- ✅ **Type-safe**: Generic types for both directions
- ✅ **Immutable**: All operations return new instances
- ✅ **One-to-one**: Each key maps to exactly one value

## Creation

```python
from mfn.collections import BiDirectionalMap

# Empty
bimap = BiDirectionalMap()

# From dict
bimap = BiDirectionalMap.from_dict({
    "alice": 1,
    "bob": 2,
    "charlie": 3
})

# From pairs
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2),
    ("charlie", 3)
])
```

## Basic Operations

### set

```python
bimap = BiDirectionalMap()

# Set key-value pair
bimap = bimap.set("alice", 1)
# {"alice": 1} <-> {1: "alice"}

# Add more
bimap = bimap.set("bob", 2).set("charlie", 3)
# {"alice": 1, "bob": 2, "charlie": 3} <-> {1: "alice", 2: "bob", 3: "charlie"}

# Update existing
bimap = bimap.set("alice", 10)
# {"alice": 10, "bob": 2, "charlie": 3} <-> {10: "alice", 2: "bob", 3: "charlie"}
```

### get_by_key / get_by_value

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Lookup by key
id_alice = bimap.get_by_key("alice")  # 1
id_bob = bimap.get_by_key("bob")  # 2

# Lookup by value
name_1 = bimap.get_by_value(1)  # "alice"
name_2 = bimap.get_by_value(2)  # "bob"

# With default
missing = bimap.get_by_key("unknown", None)  # None
missing = bimap.get_by_value(99, None)  # None
```

### has_key / has_value

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Has key?
has_alice = bimap.has_key("alice")  # True
has_charlie = bimap.has_key("charlie")  # False

# Has value?
has_1 = bimap.has_value(1)  # True
has_3 = bimap.has_value(3)  # False
```

## Update Operations

### update

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Update multiple
bimap = bimap.update(charlie=3, david=4)
# {"alice": 1, "bob": 2, "charlie": 3, "david": 4}
# <->
# {1: "alice", 2: "bob", 3: "charlie", 4: "david"}
```

### remove_by_key / remove_by_value

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2),
    ("charlie", 3)
])

# Remove by key
bimap = bimap.remove_by_key("bob")
# {"alice": 1, "charlie": 3} <-> {1: "alice", 3: "charlie"}

# Remove by value
bimap = bimap.remove_by_value(1)
# {"charlie": 3} <-> {3: "charlie"}
```

## Query Operations

### keys / values

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2),
    ("charlie", 3)
])

# All keys
keys = bimap.keys()  # ["alice", "bob", "charlie"]

# All values
values = bimap.values()  # [1, 2, 3]
```

### items / inverse_items

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Forward items
items = list(bimap.items())  # [("alice", 1), ("bob", 2)]

# Inverse items
inverse = list(bimap.inverse_items())  # [(1, "alice"), (2, "bob")]
```

### size / is_empty

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Size
bimap.size()  # 2
len(bimap)  # 2

# Empty?
bimap.is_empty()  # False
BiDirectionalMap().is_empty()  # True
```

## Conversion

### to_dict / to_inverse_dict

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Forward dict
forward = bimap.to_dict()  # {"alice": 1, "bob": 2}

# Inverse dict
inverse = bimap.to_inverse_dict()  # {1: "alice", 2: "bob"}
```

## Constraints

### One-to-One Mapping

```python
bimap = BiDirectionalMap()

# Each key must have unique value
bimap = bimap.set("alice", 1)

# This will remove old key with value 1
bimap = bimap.set("bob", 1)
# {"bob": 1} (alice was removed because 1 already mapped)

# Explicit error on conflict
bimap = bimap.set_with_conflict_check("alice", 1)
# Error: ValueError("Value 1 already mapped to key 'bob'")
```

### Conflicts

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Try to add conflicting pair
try:
    bimap = bimap.set("charlie", 1)  # Value 1 already used
except ValueError as e:
    print(f"Conflict: {e}")

# Safe add (only if no conflict)
bimap = bimap.set_if_absent("charlie", 3)  # OK
bimap = bimap.set_if_absent("david", 2)  # Skipped (value 2 exists)
```

## Advanced Operations

### force_set

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Force set (removes conflicts automatically)
bimap = bimap.force_set("charlie", 2)  # Removes "bob" (value 2)
# {"alice": 1, "charlie": 3}... wait, let me recalculate

# Actually: {"alice": 1, "charlie": 2}
# Since we're setting charlie->2, and bob->2, bob gets removed
# Result: {"alice": 1, "charlie": 2}
```

### swap

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Swap key and value
bimap = bimap.swap()
# {1: "alice", 2: "bob"} <-> {"alice": 1, "bob": 2}
# Becomes:
# {"alice": 1, "bob": 2} (same, but now keys and values swapped in type)
```

### rename_key / rename_value

```python
bimap = BiDirectionalMap.from_pairs([
    ("alice", 1),
    ("bob", 2)
])

# Rename key
bimap = bimap.rename_key("alice", "Alice")
# {"Alice": 1, "bob": 2} <-> {1: "Alice", 2: "bob"}

# Rename value (updates all keys with that value)
bimap = bimap.rename_value(1, 100)
# {"Alice": 100, "bob": 2} <-> {100: "Alice", 2: "bob"}
```

## Use Cases

### ID ↔ Object Mapping

```python
# Map users by ID and back
users = BiDirectionalMap()
users = users.set("user_1", User(1, "Alice"))
users = users.set("user_2", User(2, "Bob"))

# Find user by ID
user = users.get_by_key("user_1")  # User(1, "Alice")

# Find ID by user object
user_id = users.get_by_value(User(1, "Alice"))  # "user_1"
```

### Slug ↔ ID Mapping

```python
# SEO-friendly URLs
posts = BiDirectionalMap()
posts = posts.set("hello-world", 123)
posts = posts.set("second-post", 456)

# Get ID from slug
post_id = posts.get_by_key("hello-world")  # 123

# Get slug from ID
slug = posts.get_by_value(123)  # "hello-world"
```

### Enum Mapping

```python
# Map enum values to strings
status_map = BiDirectionalMap()
status_map = status_map.set("pending", Status.PENDING)
status_map = status_map.set("active", Status.ACTIVE)

# String to enum
status = status_map.get_by_key("active")  # Status.ACTIVE

# Enum to string
str_status = status_map.get_by_value(Status.PENDING)  # "pending"
```

### Configuration

```python
# Service names to ports
services = BiDirectionalMap()
services = services.set("database", 5432)
services = services.set("redis", 6379)
services = services.set("api", 8080)

# Find port by service
port = services.get_by_key("database")  # 5432

# Find service by port
service = services.get_by_value(5432)  # "database"
```

## Performance

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `set()` | O(1) | Hash table ops |
| `get_by_key()` | O(1) | Hash lookup |
| `get_by_value()` | O(1) | Hash lookup |
| `remove_by_key()` | O(1) | Hash delete |
| `remove_by_value()` | O(1) | Hash delete |
| `has_key()` | O(1) | Hash lookup |
| `has_value()` | O(1) | Hash lookup |

## Best Practices

### ✅ Do: Use for one-to-one mappings

```python
# Good: Each ID maps to one object
bimap = BiDirectionalMap()
bimap = bimap.set("user_1", user_obj)
```

### ✅ Do: Validate uniqueness

```python
# Good: Check for conflicts
if bimap.has_value(value):
    raise ValueError(f"Value {value} already in use")
bimap = bimap.set(key, value)
```

### ❌ Don't: Use for one-to-many

```python
# Bad: Multiple users with same ID
bimap = bimap.set("user_1", user_a)
bimap = bimap.set("user_1", user_b)  # user_a replaced!

# Better: Use regular dict with lists
users = {"user_1": [user_a, user_b]}
```

## Examples

### User Session Management

```python
sessions = BiDirectionalMap()

# Create session
sessions = sessions.set("session_abc", User(id=1, name="Alice"))

# Look up by session token
user = sessions.get_by_key("session_abc")  # User(id=1, name="Alice")

# Look up session by user
session_id = sessions.get_by_value(User(id=1, name="Alice"))  # "session_abc"

# Logout
sessions = sessions.remove_by_key("session_abc")
```

### Two-Way Cache

```python
cache = BiDirectionalMap()

# Cache computed value
cache = cache.set("user:123", expensive_computation(123))

# Get by key
result = cache.get_by_key("user:123")

# Get by value (reverse lookup - what key gives this result?)
key = cache.get_by_value(result)  # "user:123"
```

## See Also

- [MappableDict](./02-mappable-dict.md) - Functional dictionary
- [ImmutableDict](./03-immutable-dict.md) - Immutable dict
- [Entities: Combinable](../entities/03-combinable.md) - Combinable protocol

---

**End of Collections**

See [Functions](../functions/) for function utilities.
