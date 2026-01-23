# Collections: Functional Data Structures

Functional collection implementations that provide immutable, type-safe, and composable data structures.

## Overview

Unlike the [Entities](../entities/) folder which defines protocols (Mappable, Reducible, etc.), this folder contains **concrete, ready-to-use implementations**.

## Collection Types

### [MappableList](./01-mappable-list.md)
Functional list with `map()`, `filter()`, `reduce()` operations.

```python
numbers = MappableList([1, 2, 3, 4, 5])
result = numbers.filter(lambda x: x % 2 == 0).map(lambda x: x * 2)
# MappableList([4, 8])
```

### [MappableDict](./02-mappable-dict.md)
Functional dictionary with value/key transformations.

```python
users = MappableDict({1: "Alice", 2: "Bob"})
names = users.map_values(lambda u: u.upper())
# MappableDict({1: "ALICE", 2: "BOB"})
```

### [ImmutableDict](./03-immutable-dict.md)
Immutable dictionary with deep updates.

```python
config = ImmutableDict({"db": {"host": "localhost"}})
config2 = config.set_in("db.port", 5432)
# Original unchanged, config2 has new port
```

### [ImmutableList](./04-immutable-list.md)
Immutable list with O(1) updates at ends.

```python
items = ImmutableList([1, 2, 3])
items2 = items.append(4)
# items is still [1, 2, 3]
```

### [LazySequence](./05-lazy-sequence.md)
Lazy evaluation sequences (infinite iterators).

```python
seq = LazySequence.range().map(lambda x: x * 2)
first_10 = seq.take(10)  # Only computes 10 values
```

### [BiDirectionalMap](./06-bidirectional-map.md)
Dictionary with reverse lookup.

```python
bimap = BiDirectionalMap()
bimap.set("id", 1)
bimap.get_by_key("id")  # 1
bimap.get_by_value(1)   # "id"
```

## Comparison Table

| Collection | Mutable | Thread-Safe | Lazy | Use Case |
|------------|---------|-------------|------|----------|
| `MappableList` | ❌ | ✅ | ❌ | Functional transformations |
| `MappableDict` | ❌ | ✅ | ❌ | Functional dict operations |
| `ImmutableDict` | ❌ | ✅ | ❌ | Configuration, state |
| `ImmutableList` | ❌ | ✅ | ❌ | Append-only logs |
| `LazySequence` | ❌ | ✅ | ✅ | Streams, infinite data |
| `BiDirectionalMap` | ❌ | ✅ | ❌ | Reverse lookups |

## When to Use What

### Use MappableList when:
- You need `map()`, `filter()`, `reduce()`
- Data transformation pipelines
- Type-safe collection operations

### Use ImmutableDict when:
- You need immutable state
- Deep nested updates
- Thread-safe configuration

### Use LazySequence when:
- Working with large/infinite data
- Lazy evaluation needed
- Stream processing

### Use BiDirectionalMap when:
- Need reverse lookups
- One-to-one mappings
- ID ↔ Object mappings

## Design Principles

All functional collections share these principles:

### ✅ Immutable

```python
# Operations return new instances
list2 = list1.append(item)
# list1 unchanged
```

### ✅ Type-Safe

```python
# Generic types track transformations
numbers: MappableList[int] = MappableList([1, 2, 3])
doubled: MappableList[int] = numbers.map(lambda x: x * 2)
```

### ✅ Composable

```python
# Chain operations naturally
result = (
    collection
    .filter(predicate)
    .map(transform)
    .reduce(combiner)
)
```

### ✅ Protocol-Compliant

```python
# Implement Mappable, Reducible, etc.
isinstance(MappableList([1]), Mappable)  # True
```

## Import Examples

```python
# Import specific collections
from mfn.collections import (
    MappableList,
    MappableDict,
    ImmutableDict,
    ImmutableList,
    LazySequence,
    BiDirectionalMap
)

# Import all collections
from mfn.collections import *

# Import from submodules
from mfn.collections.lists import MappableList
from mfn.collections.dicts import ImmutableDict
from mfn.collections.lazy import LazySequence
```

## Performance Considerations

| Operation | MappableList | ImmutableList | LazySequence |
|-----------|--------------|---------------|--------------|
| Append | O(n) | O(1) | O(1) |
| Prepend | O(n) | O(1) | O(1) |
| Map | O(n) | O(n) | O(1) (lazy) |
| Filter | O(n) | O(n) | O(1) (lazy) |
| Access | O(1) | O(n) | O(1) |
| Update index | O(n) | O(n) | O(1) (lazy) |

## Related Documentation

- [Entities: Mappable](../entities/01-mappable.md) - Protocol definition
- [Entities: Reducible](../entities/02-reducible.md) - Reduce protocol
- [Entities: Updatable](../entities/04-updatable.md) - Update protocol
- [Core: Immutability](../core/03-immutability.md) - Immutability patterns
- [Core: Composition](../core/05-composition.md) - Composition patterns

## Summary

Functional collections provide:
- ✅ **Immutable** data structures
- ✅ **Type-safe** operations
- ✅ **Composable** transformations
- ✅ **Protocol-compliant** implementations
- ✅ **Ready to use** out of the box

**Key insight**: Use these collections instead of built-in `list`/`dict` when you need immutability, composability, and functional transformations.

---

**Next**: See [MappableList](./01-mappable-list.md) for implementation details.
