# MappableDict: Functional Dictionary Operations

A functional dictionary with immutable value/key transformations and type-safe operations.

## Overview

```python
@dataclass(frozen=True, slots=True)
class MappableDict(Generic[K, V]):
    """Immutable functional dict with map operations"""
    _data: dict[K, V]
```

## Creation

```python
from mfn.collections import MappableDict

# From dict
users = MappableDict({
    1: {"name": "Alice", "age": 30},
    2: {"name": "Bob", "age": 25},
})

# Empty
empty = MappableDict.empty()

# From pairs
pairs = MappableDict.from_pairs([(1, "a"), (2, "b")])
# MappableDict({1: "a", 2: "b"})
```

## Transformation Operations

### map_values

```python
users = MappableDict({
    1: {"name": "Alice", "age": 30},
    2: {"name": "Bob", "age": 25},
})

# Transform values
names = users.map_values(lambda u: u["name"])
# MappableDict({1: "Alice", 2: "Bob"})

# Transform to uppercase
upper = users.map_values(lambda u: u["name"].upper())
# MappableDict({1: "ALICE", 2: "BOB"})

# Extract field
ages = users.map_values(lambda u: u["age"])
# MappableDict({1: 30, 2: 25})
```

### map_keys

```python
users = MappableDict({
    "user_1": "Alice",
    "user_2": "Bob",
})

# Transform keys
simple_keys = users.map_keys(lambda k: k.replace("user_", ""))
# MappableDict({"1": "Alice", "2": "Bob"})

# To uppercase
upper_keys = users.map_keys(str.upper)
# MappableDict({"USER_1": "Alice", "USER_2": "Bob"})
```

### map_items

```python
data = MappableDict({"a": 1, "b": 2})

# Transform both keys and values
swapped = data.map_items(lambda kv: (kv[1], kv[0]))
# MappableDict({1: "a", 2: "b"})

# Add prefix to keys
prefixed = data.map_items(lambda kv: (f"key_{kv[0]}", kv[1]))
# MappableDict({"key_a": 1, "key_b": 2})
```

## Filter Operations

### filter_values

```python
users = MappableDict({
    1: {"name": "Alice", "age": 30},
    2: {"name": "Bob", "age": 25},
    3: {"name": "Charlie", "age": 35},
})

# Keep adults
adults = users.filter_values(lambda u: u["age"] >= 30)
# MappableDict({
#     1: {"name": "Alice", "age": 30},
#     3: {"name": "Charlie", "age": 35},
# })
```

### filter_keys

```python
data = MappableDict({
    "user_1": "Alice",
    "user_2": "Bob",
    "admin_1": "Admin",
})

# Keep only users
users = data.filter_keys(lambda k: k.startswith("user_"))
# MappableDict({"user_1": "Alice", "user_2": "Bob"})
```

### filter_items

```python
scores = MappableDict({
    "Alice": 85,
    "Bob": 92,
    "Charlie": 78,
})

# Keep high scores
high_scores = scores.filter_items(lambda kv: kv[1] >= 80)
# MappableDict({"Alice": 85, "Bob": 92})
```

## Reduction Operations

### reduce_values

```python
scores = MappableDict({
    "Alice": 85,
    "Bob": 92,
    "Charlie": 78,
})

# Sum values
total = scores.reduce_values(lambda a, b: a + b)  # 255

# Max value
max_score = scores.reduce_values(lambda a, b: a if a > b else b)  # 92
```

### fold_values

```python
data = MappableDict({"a": 1, "b": 2, "c": 3})

# Fold with initial
result = data.fold_values(
    10,
    lambda acc, v: acc + v
)  # 16 (10 + 1 + 2 + 3)

# Build string
concat = data.fold_values(
    "",
    lambda s, v: f"{s}{v}"
)  # "123"
```

## Access Operations

### get

```python
users = MappableDict({
    1: "Alice",
    2: "Bob",
})

# Get value
name = users.get(1)  # "Alice"

# With default
name = users.get(3, "Unknown")  # "Unknown"

# Nested get
config = MappableDict({
    "db": {"host": "localhost", "port": 5432}
})
host = config.get_in("db.host")  # "localhost"
```

### keys / values / items

```python
data = MappableDict({"a": 1, "b": 2, "c": 3})

# Keys as list
keys = data.keys()  # MappableList(["a", "b", "c"])

# Values as list
values = data.values()  # MappableList([1, 2, 3])

# Items as list
items = data.items()  # MappableList([("a", 1), ("b", 2), ("c", 3)])
```

## Query Operations

### contains_key

```python
users = MappableDict({1: "Alice", 2: "Bob"})

has_user_1 = users.contains_key(1)  # True
has_user_3 = users.contains_key(3)  # False
```

### has_in

```python
config = MappableDict({
    "db": {"host": "localhost", "port": 5432}
})

# Check nested path
has_host = config.has_in("db.host")  # True
has_password = config.has_in("db.password")  # False
```

## Update Operations

### set

```python
config = MappableDict({"host": "localhost", "port": 5432})

# Set new key
config2 = config.set("ssl", True)
# {"host": "localhost", "port": 5432, "ssl": True}

# Update existing
config3 = config2.set("port", 3306)
# {"host": "localhost", "port": 3306, "ssl": True}

# Original unchanged
config._data  # {"host": "localhost", "port": 5432}
```

### update

```python
config = MappableDict({"host": "localhost"})

# Update multiple
config2 = config.update(port=5432, ssl=True)
# {"host": "localhost", "port": 5432, "ssl": True}
```

### remove

```python
data = MappableDict({"a": 1, "b": 2, "c": 3})

# Remove key
data2 = data.remove("b")
# {"a": 1, "c": 3}

# Original unchanged
data._data  # {"a": 1, "b": 2, "c": 3}
```

## Merge Operations

### merge

```python
defaults = MappableDict({"host": "localhost", "port": 5432})
overrides = MappableDict({"port": 3306, "ssl": True})

# Merge (overrides take precedence)
merged = defaults.merge(overrides)
# {"host": "localhost", "port": 3306, "ssl": True}
```

### deep_merge

```python
config1 = MappableDict({
    "db": {"host": "localhost", "port": 5432}
})

config2 = MappableDict({
    "db": {"port": 3306, "ssl": True}
})

# Deep merge
merged = config1.deep_merge(config2)
# {
#     "db": {
#         "host": "localhost",
#         "port": 3306,
#         "ssl": True
#     }
# }
```

## Conversion Operations

```python
data = MappableDict({"a": 1, "b": 2, "c": 3})

# To Python dict
python_dict = data.to_dict()  # {"a": 1, "b": 2, "c": 3}

# To list of tuples
pairs = data.to_list()  # [("a", 1), ("b", 2), ("c", 3)]

# To MappableList
keys = MappableList(data.keys())  # ["a", "b", "c"]
values = MappableList(data.values())  # [1, 2, 3]
```

## Information Operations

```python
data = MappableDict({"a": 1, "b": 2})

# Size
len(data)  # 2
data.size()  # 2

# Check
bool(data)  # True
bool(MappableDict({}))  # False
```

## Advanced Operations

### transform_values (with index)

```python
data = MappableDict({"a": 1, "b": 2, "c": 3})

# Transform with key available
result = data.map_items(lambda kv: (kv[0], kv[1] * 2))
# MappableDict({"a": 2, "b": 4, "c": 6})
```

### pick / omit

```python
data = MappableDict({
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com",
    "password": "secret"
})

# Pick specific keys
public = data.pick("name", "age", "email")
# {"name": "Alice", "age": 30, "email": "alice@example.com"}

# Omit specific keys
safe = data.omit("password")
# {"name": "Alice", "age": 30, "email": "alice@example.com"}
```

### compact

```python
data = MappableDict({
    "a": 1,
    "b": None,
    "c": 3,
    "d": None,
})

# Remove None values
compacted = data.compact()
# {"a": 1, "c": 3}
```

## Examples

### Configuration Management

```python
# Default config
defaults = MappableDict({
    "database": {
        "host": "localhost",
        "port": 5432,
        "ssl": False
    },
    "cache": {
        "enabled": True,
        "ttl": 300
    }
})

# Environment-specific overrides
prod_overrides = MappableDict({
    "database": {
        "host": "prod-db.example.com",
        "ssl": True
    }
})

# Merge
config = defaults.deep_merge(prod_overrides)

# Update specific value
config2 = config.set_in("database.pool_size", 20)
```

### Data Processing

```python
users = MappableDict({
    1: {"name": "Alice", "scores": [85, 92, 78]},
    2: {"name": "Bob", "scores": [76, 88, 82]},
    3: {"name": "Charlie", "scores": [90, 85, 95]},
})

# Calculate averages
averages = users.map_values(
    lambda u: sum(u["scores"]) / len(u["scores"])
)
# {1: 85.0, 2: 82.0, 3: 90.0}

# Filter high performers
high_performers = users.filter_values(
    lambda u: sum(u["scores"]) / len(u["scores"]) >= 85
)
# {1: {...}, 3: {...}}
```

### Group and Aggregate

```python
sales = MappableDict({
    "Q1": 1000,
    "Q2": 1500,
    "Q3": 1200,
    "Q4": 1800,
})

# Total
total = sales.reduce_values(lambda a, b: a + b)  # 5500

# Average
average = sales.fold_values(
    0,
    lambda acc, v: acc + v
) / len(sales)  # 1375.0
```

## Performance

| Operation | Time Complexity |
|-----------|----------------|
| `get()` | O(1) |
| `set()` | O(n) - creates new dict |
| `map_values()` | O(n) |
| `filter_values()` | O(n) |
| `merge()` | O(n+m) |
| `deep_merge()` | O(n+m) |
| `reduce_values()` | O(n) |

## Best Practices

### ✅ Do: Use for transformations

```python
result = (
    users
    .map_values(lambda u: u["name"])
    .filter_values(lambda n: len(n) > 3)
)
```

### ✅ Do: Chain with MappableList

```python
keys = MappableList(users.keys())
values = MappableList(users.values())
```

### ❌ Don't: Use for large updates

```python
# Bad: Many updates
config = config.set("a", 1)
config = config.set("b", 2)
config = config.set("c", 3)

# Good: Batch updates
config = config.update(a=1, b=2, c=3)
```

## See Also

- [Entities: Mappable](../entities/01-mappable.md) - Protocol definition
- [MappableList](./01-mappable-list.md) - List version
- [ImmutableDict](./03-immutable-dict.md) - Immutable dict with deep updates
- [BiDirectionalMap](./06-bidirectional-map.md) - Two-way lookup

---

**Next**: [ImmutableDict](./03-immutable-dict.md)
