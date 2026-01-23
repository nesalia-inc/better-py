# Mappable: Transformable Collections

**Mappable** is a protocol for collections that can be **transformed** by applying a function to each element.

## Overview

```python
@runtime_checkable
class Mappable(Protocol[T]):
    """Any object that can be mapped over"""

    def map(self, func: Callable[[T], U]) -> 'Mappable[U]':
        """Transform each element"""
        ...

    def filter(self, predicate: Callable[[T], bool]) -> 'Mappable[T]':
        """Keep elements matching predicate"""
        ...
```

## Implementations

### MappableList

```python
@dataclass(frozen=True, slots=True)
class MappableList(Generic[T]):
    """List with functional operations"""

    _data: list[T]

    # === Transform operations ===

    def map(self, func: Callable[[T], U]) -> 'MappableList[U]':
        """Transform each element"""
        return MappableList([func(x) for x in self._data])

    def filter(self, predicate: Callable[[T], bool]) -> 'MappableList[T]':
        """Keep elements matching predicate"""
        return MappableList([x for x in self._data if predicate(x)])

    def flat_map(self, func: Callable[[T], 'MappableList[U]']) -> 'MappableList[U]':
        """Transform and flatten"""
        result = []
        for item in self._data:
            result.extend(func(item)._data)
        return MappableList(result)

    # === Access operations ===

    def get(self, index: int, default: T | None = None) -> T | None:
        """Get element at index"""
        if 0 <= index < len(self._data):
            return self._data[index]
        return default

    def first(self) -> 'Maybe[T]':
        """Get first element"""
        if self._data:
            return Some(self._data[0])
        return None_

    def last(self) -> 'Maybe[T]':
        """Get last element"""
        if self._data:
            return Some(self._data[-1])
        return None_

    # === Query operations ===

    def find(self, predicate: Callable[[T], bool]) -> 'Maybe[T]':
        """Find first element matching predicate"""
        for item in self._data:
            if predicate(item):
                return Some(item)
        return None_

    def find_index(self, predicate: Callable[[T], bool]) -> 'Maybe[int]':
        """Find index of first element matching predicate"""
        for i, item in enumerate(self._data):
            if predicate(item):
                return Some(i)
        return None_

    def contains(self, item: T) -> bool:
        """Check if item is in list"""
        return item in self._data

    def exists(self, predicate: Callable[[T], bool]) -> bool:
        """Check if any element matches predicate"""
        return any(predicate(x) for x in self._data)

    def for_all(self, predicate: Callable[[T], bool]) -> bool:
        """Check if all elements match predicate"""
        return all(predicate(x) for x in self._data)

    # === Partition operations ===

    def partition(self, predicate: Callable[[T], bool]) -> tuple['MappableList[T]', 'MappableList[T]']:
        """Split into matching and non-matching"""
        matching = [x for x in self._data if predicate(x)]
        non_matching = [x for x in self._data if not predicate(x)]
        return MappableList(matching), MappableList(non_matching)

    def split_when(self, predicate: Callable[[T], bool]) -> list['MappableList[T]']:
        """Split list at first match"""
        for i, item in enumerate(self._data):
            if predicate(item):
                return [
                    MappableList(self._data[:i]),
                    MappableList(self._data[i:])
                ]
        return [MappableList(self._data)]

    # === Grouping operations ===

    def group_by(self, key_func: Callable[[T], Any]) -> dict[Any, 'MappableList[T]']:
        """Group elements by key function"""
        groups = {}
        for item in self._data:
            key = key_func(item)
            if key not in groups:
                groups[key] = MappableList([])
            groups[key] = groups[key].append(item)
        return groups

    def group_by_size(self, size: int) -> list['MappableList[T]']:
        """Split into chunks of size"""
        chunks = []
        for i in range(0, len(self._data), size):
            chunks.append(MappableList(self._data[i:i+size]))
        return chunks

    # === Order operations ===

    def sort(self, key: Callable[[T], Any] | None = None, reverse: bool = False) -> 'MappableList[T]':
        """Return sorted copy"""
        return MappableList(sorted(self._data, key=key, reverse=reverse))

    def sort_by(self, key: Callable[[T], Any]) -> 'MappableList[T]':
        """Sort by key function"""
        return self.sort(key=key)

    def reverse(self) -> 'MappableList[T]':
        """Return reversed copy"""
        return MappableList(list(reversed(self._data)))

    def shuffle(self) -> 'MappableList[T]':
        """Return shuffled copy"""
        import random
        data = self._data.copy()
        random.shuffle(data)
        return MappableList(data)

    # === Set operations ===

    def distinct(self) -> 'MappableList[T]':
        """Remove duplicates"""
        seen = set()
        return MappableList([x for x in self._data if not (x in seen or seen.add(x))])

    def union(self, other: 'MappableList[T]') -> 'MappableList[T]':
        """Combine with other, remove duplicates"""
        return MappableList(list(dict.fromkeys(self._data + other._data)))

    def intersect(self, other: 'MappableList[T]') -> 'MappableList[T]':
        """Keep elements also in other"""
        set_other = set(other._data)
        return MappableList([x for x in self._data if x in set_other])

    def difference(self, other: 'MappableList[T]') -> 'MappableList[T]':
        """Remove elements also in other"""
        set_other = set(other._data)
        return MappableList([x for x in self._data if x not in set_other])

    # === Conversion operations ===

    def to_list(self) -> list[T]:
        """Convert to Python list"""
        return self._data.copy()

    def to_tuple(self) -> tuple[T, ...]:
        """Convert to tuple"""
        return tuple(self._data)

    def to_set(self) -> set[T]:
        """Convert to set"""
        return set(self._data)

    def to_dict(self, key_func: Callable[[T], Any]) -> dict[Any, T]:
        """Convert to dict"""
        return {key_func(x): x for x in self._data}

    # === String operations ===

    def join(self, separator: str = "") -> -> str:
        """Join elements as strings"""
        return separator.join(str(x) for x in self._data)

    # === Zip operations ===

    def zip(self, *others: 'MappableList') -> 'MappableList[tuple]':
        """Zip with other lists"""
        return MappableList(list(zip(self._data, *(o._data for o in others))))

    def zip_with_index(self) -> 'MappableList[tuple[int, T]]':
        """Pair elements with indices"""
        return MappableList(list(enumerate(self._data)))

    # === Information ===

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    # === Iteration ===

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)

    def for_each(self, func: Callable[[T], None]) -> None:
        """Execute func for each element"""
        for item in self._data:
            func(item)
```

### Usage Examples

```python
# Create
numbers = MappableList([1, 2, 3, 4, 5])

# Transform
doubled = numbers.map(lambda x: x * 2)  # [2, 4, 6, 8, 10]
evens = numbers.filter(lambda x: x % 2 == 0)  # [2, 4]

# Access
first = numbers.first()  # Some(1)
last = numbers.last()  # Some(5)

# Query
found = numbers.find(lambda x: x > 3)  # Some(4)
has_even = numbers.exists(lambda x: x % 2 == 0)  # True
all_positive = numbers.for_all(lambda x: x > 0)  # True

# Partition
evens, odds = numbers.partition(lambda x: x % 2 == 0)
# evens: [2, 4], odds: [1, 3, 5]

# Group
users = MappableList([
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob", "dept": "Sales"},
    {"name": "Charlie", "dept": "Engineering"},
])
by_dept = users.group_by(lambda u: u["dept"])
# {"Engineering": [...], "Sales": [...]}

# Sort
sorted_nums = numbers.sort(reverse=True)  # [5, 4, 3, 2, 1]

# Distinct
with_dupes = MappableList([1, 2, 2, 3, 3, 3])
unique = with_dupes.distinct()  # [1, 2, 3]

# Chaining
result = (
    MappableList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    .filter(lambda x: x % 2 == 0)  # [2, 4, 6, 8, 10]
    .map(lambda x: x * 2)          # [4, 8, 12, 16, 20]
    .filter(lambda x: x > 10)      # [12, 16, 20]
    .sort()                        # [12, 16, 20]
)
```

### MappableDict

```python
@dataclass(frozen=True, slots=True)
class MappableDict(Generic[K, V]):
    """Dict with functional operations"""

    _data: dict[K, V]

    def map_values(self, func: Callable[[V], U]) -> 'MappableDict[K, U]':
        """Transform values"""
        return MappableDict({k: func(v) for k, v in self._data.items()})

    def map_keys(self, func: Callable[[K], U]) -> 'MappableDict[U, V]':
        """Transform keys"""
        return MappableDict({func(k): v for k, v in self._data.items()})

    def map_items(self, func: Callable[[K, V], tuple[U, W]]) -> 'MappableDict[U, W]':
        """Transform keys and values"""
        return MappableDict(dict(func(k, v) for k, v in self._data.items()))

    def filter_values(self, predicate: Callable[[V], bool]) -> 'MappableDict[K, V]':
        """Keep items where value matches"""
        return MappableDict({k: v for k, v in self._data.items() if predicate(v)})

    def filter_keys(self, predicate: Callable[[K], bool]) -> 'MappableDict[K, V]':
        """Keep items where key matches"""
        return MappableDict({k: v for k, v in self._data.items() if predicate(k)})

    def filter_items(self, predicate: Callable[[K, V], bool]) -> 'MappableDict[K, V]':
        """Keep items matching predicate"""
        return MappableDict({k: v for k, v in self._data.items() if predicate(k, v)})

    def keys(self) -> 'MappableList[K]':
        """Get keys as MappableList"""
        return MappableList(list(self._data.keys()))

    def values(self) -> 'MappableList[V]':
        """Get values as MappableList"""
        return MappableList(list(self._data.values()))

    def items(self) -> 'MappableList[tuple[K, V]]':
        """Get items as MappableList"""
        return MappableList(list(self._data.items()))

    def get(self, key: K, default: V | None = None) -> V | None:
        """Get value or default"""
        return self._data.get(key, default)

    def contains_key(self, key: K) -> bool:
        """Check if key exists"""
        return key in self._data

    def merge(self, other: 'MappableDict[K, V]') -> 'MappableDict[K, V]':
        """Merge with other (other takes precedence)"""
        return MappableDict({**self._data, **other._data})

    def to_dict(self) -> dict[K, V]:
        """Convert to Python dict"""
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)
```

#### Usage Examples

```python
# Create
users = MappableDict({
    1: {"name": "Alice", "age": 30},
    2: {"name": "Bob", "age": 25},
    3: {"name": "Charlie", "age": 35},
})

# Transform
names = users.map_values(lambda u: u["name"])
# {1: "Alice", 2: "Bob", 3: "Charlie"}

upper_names = users.map_values(lambda u: u["name"].upper())
# {1: "ALICE", 2: "BOB", 3: "CHARLIE"}

# Filter
adults = users.filter_values(lambda u: u["age"] >= 30)
# {1: {...}, 3: {...}}

# Get
user = users.get(1)  # {"name": "Alice", "age": 30}
missing = users.get(99)  # None

# Merge
updates = MappableDict({2: {"name": "Robert", "age": 26}})
merged = users.merge(updates)
# {1: {...}, 2: {"name": "Robert", "age": 26}, 3: {...}}
```

### MappableSet

```python
@dataclass(frozen=True, slots=True)
class MappableSet(Generic[T]):
    """Set with functional operations"""

    _data: set[T]

    def map(self, func: Callable[[T], U]) -> 'MappableSet[U]':
        """Transform each element"""
        return MappableSet({func(x) for x in self._data})

    def filter(self, predicate: Callable[[T], bool]) -> 'MappableSet[T]':
        """Keep elements matching predicate"""
        return MappableSet({x for x in self._data if predicate(x)})

    def union(self, other: 'MappableSet[T]') -> 'MappableSet[T]':
        """Combine sets"""
        return MappableSet(self._data | other._data)

    def intersect(self, other: 'MappableSet[T]') -> 'MappableSet[T]':
        """Keep elements also in other"""
        return MappableSet(self._data & other._data)

    def difference(self, other: 'MappableSet[T]') -> 'MappableSet[T]':
        """Remove elements also in other"""
        return MappableSet(self._data - other._data)

    def add(self, item: T) -> 'MappableSet[T]':
        """Return new set with item"""
        return MappableSet(self._data | {item})

    def remove(self, item: T) -> 'MappableSet[T]':
        """Return new set without item"""
        return MappableSet(self._data - {item})

    def contains(self, item: T) -> bool:
        """Check if item is in set"""
        return item in self._data

    def to_list(self) -> 'MappableList[T]':
        """Convert to MappableList"""
        return MappableList(list(self._data))

    def to_set(self) -> set[T]:
        """Convert to Python set"""
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
```

## Protocol Compliance

Any class with `map()` method is automatically `Mappable`:

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

class CustomCollection:
    def __init__(self, items):
        self._items = items

    def map(self, func):
        return CustomCollection([func(x) for x in self._items])

# CustomCollection is Mappable!
isinstance(CustomCollection([1, 2, 3]), Mappable)  # True
```

## Best Practices

### ✅ Do: Chain operations

```python
result = (
    MappableList(data)
    .filter(is_valid)
    .map(transform)
    .distinct()
)
```

### ✅ Do: Use comprehensions for simple maps

```python
# For simple transformations, list comprehension is fine
squared = [x**2 for x in numbers]
```

### ❌ Don't: Mix paradigms

```python
# Confusing
result = MappableList(numbers).map(lambda x: x * 2)._data

# Better: Stay consistent
result = MappableList(numbers).map(lambda x: x * 2)
# or
result = [x * 2 for x in numbers]
```

## Summary

**Mappable** protocol:
- ✅ Transform collections with `map()`
- ✅ Filter with `filter()`
- ✅ Chain operations naturally
- ✅ Type-safe transformations
- ✅ Works for lists, dicts, sets

**Implementations**:
- `MappableList[T]` - Functional list
- `MappableDict[K, V]` - Functional dict
- `MappableSet[T]` - Functional set

---

**Next**: See [Reducible](./02-reducible.md) for reducible collections.
