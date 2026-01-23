# Reducible: Collections That Can Be Reduced

**Reducible** is a protocol for collections that can be **reduced** to a single value through aggregation.

## Overview

```python
@runtime_checkable
class Reducible(Protocol[T]):
    """Any object that can be reduced"""

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce to single value"""
        ...

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U:
        """Fold with initial value (left-to-right)"""
        ...
```

## Core Concepts

### reduce vs fold_left

```python
# reduce: No initial value, requires non-empty collection
numbers = [1, 2, 3, 4]
result = reduce(lambda a, b: a + b, numbers)  # 10

# fold_left: Has initial value, works with empty collections
result = fold_left(0, lambda acc, x: acc + x, numbers)  # 10
result = fold_left(0, lambda acc, x: acc + x, [])  # 0
```

## Implementation

### ReducibleList

```python
@dataclass(frozen=True, slots=True)
class ReducibleList(Generic[T]):
    """List with reduce operations"""

    _data: list[T]

    # === Basic reduce ===

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce to single value (requires non-empty)"""
        if not self._data:
            raise ValueError("Cannot reduce empty list")

        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U:
        """Fold left-to-right with initial value"""
        result = initial
        for item in self._data:
            result = func(result, item)
        return result

    def fold_right(self, initial: U, func: Callable[[T, U], U]) -> U:
        """Fold right-to-left with initial value"""
        result = initial
        for item in reversed(self._data):
            result = func(item, result)
        return result

    # === Aggregation helpers ===

    def sum(self) -> T:
        """Sum all elements (requires numeric)"""
        return self.fold_left(type(self._data[0])(0), lambda acc, x: acc + x)

    def product(self) -> T:
        """Multiply all elements (requires numeric)"""
        return self.fold_left(type(self._data[0])(1), lambda acc, x: acc * x)

    def min(self) -> T:
        """Get minimum element"""
        return self.reduce(lambda a, b: a if a < b else b)

    def max(self) -> T:
        """Get maximum element"""
        return self.reduce(lambda a, b: a if a > b else b)

    def avg(self) -> float:
        """Get average (requires numeric)"""
        return self.sum() / len(self._data)

    # === Boolean aggregation ===

    def any(self) -> bool:
        """True if any element is truthy"""
        return self.fold_left(False, lambda acc, x: acc or bool(x))

    def all(self) -> bool:
        """True if all elements are truthy"""
        return self.fold_left(True, lambda acc, x: acc and bool(x))

    def none(self) -> bool:
        """True if no element is truthy"""
        return not self.any()

    # === Count operations ===

    def count(self) -> int:
        """Count elements"""
        return len(self._data)

    def count_if(self, predicate: Callable[[T], bool]) -> int:
        """Count elements matching predicate"""
        return self.fold_left(0, lambda acc, x: acc + (1 if predicate(x) else 0))

    # === Partition operations ===

    def partition_map(
        self,
        func: Callable[[T], 'Result[U, V]']
    ) -> tuple[list[U], list[V]]:
        """Partition into success and failure lists"""
        successes = []
        failures = []

        for item in self._data:
            result = func(item)
            if result.is_ok():
                successes.append(result.unwrap())
            else:
                failures.append(result.error)

        return successes, failures

    # === Group operations ===

    def group_by(
        self,
        key_func: Callable[[T], Any]
    ) -> 'ReducibleDict[Any, ReducibleList[T]]':
        """Group elements by key function"""
        groups = {}
        for item in self._data:
            key = key_func(item)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        return ReducibleDict({
            k: ReducibleList(v) for k, v in groups.items()
        })

    def group_by_fold(
        self,
        key_func: Callable[[T], Any],
        fold_func: Callable[[U, T], U],
        initial: U
    ) -> dict[Any, U]:
        """Group and fold in one pass"""
        groups = {}
        for item in self._data:
            key = key_func(item)
            if key not in groups:
                groups[key] = initial
            groups[key] = fold_func(groups[key], item)
        return groups

    # === String operations ===

    def join(self, separator: str = "") -> str:
        """Join elements as strings"""
        return separator.join(str(x) for x in self._data)

    # === First/Last ===

    def head(self) -> 'Maybe[T]':
        """Get first element"""
        if self._data:
            return Some(self._data[0])
        return None_

    def last(self) -> 'Maybe[T]':
        """Get last element"""
        if self._data:
            return Some(self._data[-1])
        return None_

    def head_and_tail(self) -> 'Maybe[tuple[T, ReducibleList[T]]]':
        """Get first element and rest"""
        if self._data:
            return Some((self._data[0], ReducibleList(self._data[1:])))
        return None_

    # === Conversion ===

    def to_list(self) -> list[T]:
        return self._data.copy()

    def to_set(self) -> set[T]:
        return set(self._data)
```

### Usage Examples

```python
# Create
numbers = ReducibleList([1, 2, 3, 4, 5])

# Basic reduce
sum_ = numbers.reduce(lambda a, b: a + b)  # 15
product = numbers.reduce(lambda a, b: a * b)  # 120

# Fold with initial
sum_with_initial = numbers.fold_left(10, lambda acc, x: acc + x)  # 25

# Aggregation helpers
sum_nums = numbers.sum()  # 15
min_val = numbers.min()  # 1
max_val = numbers.max()  # 5
avg = numbers.avg()  # 3.0

# Boolean
has_positive = numbers.any()  # True
all_positive = numbers.all(lambda x: x > 0)  # True

# Count
count = numbers.count()  # 5
count_even = numbers.count_if(lambda x: x % 2 == 0)  # 2

# Group
users = ReducibleList([
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob", "dept": "Sales"},
    {"name": "Charlie", "dept": "Eng"},
])
by_dept = users.group_by_fold(
    key_func=lambda u: u["dept"],
    fold_func=lambda acc, u: acc + 1,
    initial=0
)
# {"Eng": 2, "Sales": 1}

# String
words = ReducibleList(["Hello", "World", "!"])
joined = words.join(" ")  # "Hello World !"

# First/Last
first = numbers.head()  # Some(1)
last = numbers.last()  # Some(5)
head_tail = numbers.head_and_tail()  # Some((1, ReducibleList([2,3,4,5])))
```

### ReducibleDict

```python
@dataclass(frozen=True, slots=True)
class ReducibleDict(Generic[K, V]):
    """Dict with reduce operations"""

    _data: dict[K, V]

    def reduce_values(self, func: Callable[[V, V], V]) -> V:
        """Reduce values"""
        values = list(self._data.values())
        if not values:
            raise ValueError("Cannot reduce empty dict")
        result = values[0]
        for value in values[1:]:
            result = func(result, value)
        return result

    def reduce_keys(self, func: Callable[[K, K], K]) -> K:
        """Reduce keys"""
        keys = list(self._data.keys())
        if not keys:
            raise ValueError("Cannot reduce empty dict")
        result = keys[0]
        for key in keys[1:]:
            result = func(result, key)
        return result

    def fold_values(self, initial: U, func: Callable[[U, V], U]) -> U:
        """Fold values with initial"""
        result = initial
        for value in self._data.values():
            result = func(result, value)
        return result

    def fold_keys(self, initial: U, func: Callable[[U, K], U]) -> U:
        """Fold keys with initial"""
        result = initial
        for key in self._data.keys():
            result = func(result, key)
        return result

    def fold_items(self, initial: U, func: Callable[[U, tuple[K, V]], U]) -> U:
        """Fold items with initial"""
        result = initial
        for item in self._data.items():
            result = func(result, item)
        return result

    # === Aggregation ===

    def values_sum(self) -> V:
        """Sum of values (requires numeric)"""
        return self.fold_values(type(list(self._data.values())[0])(0), lambda acc, v: acc + v)

    def values_min(self) -> V:
        """Minimum value"""
        return self.reduce_values(lambda a, b: a if a < b else b)

    def values_max(self) -> V:
        """Maximum value"""
        return self.reduce_values(lambda a, b: a if a > b else b)

    def values_count(self) -> int:
        """Count values"""
        return len(self._data)

    def keys_count(self) -> int:
        """Count keys"""
        return len(self._data)
```

#### Usage Examples

```python
# Create
scores = ReducibleDict({
    "Alice": 85,
    "Bob": 92,
    "Charlie": 78,
})

# Reduce
max_score = scores.reduce_values(lambda a, b: a if a > b else b)  # 92

# Fold
total = scores.fold_values(0, lambda acc, score: acc + score)  # 255

# Aggregation
sum_scores = scores.values_sum()  # 255
min_score = scores.values_min()  # 78
max_score = scores.values_max()  # 92
count = scores.values_count()  # 3
```

## Advanced Patterns

### Custom Reduction

```python
# Build custom data structure
numbers = ReducibleList([1, 2, 3, 4, 5])

# Build tuple of (sum, count, min, max)
stats = numbers.fold_left(
    (0, 0, float('inf'), float('-inf')),
    lambda acc, x: (
        acc[0] + x,      # sum
        acc[1] + 1,      # count
        min(acc[2], x),  # min
        max(acc[3], x)   # max
    )
)
# (15, 5, 1, 5)

# Build dict
pairs = ReducibleList([("a", 1), ("b", 2), ("a", 3)])
result = pairs.fold_left(
    {},
    lambda acc, pair: {
        **acc,
        pair[0]: acc.get(pair[0], 0) + pair[1]
    }
)
# {"a": 4, "b": 2}
```

### Multi-fold

```python
numbers = ReducibleList([1, 2, 3, 4, 5])

# Single pass for multiple aggregations
sum_, count, min_, max_ = numbers.fold_left(
    (0, 0, float('inf'), float('-inf')),
    lambda acc, x: (
        acc[0] + x,
        acc[1] + 1,
        min(acc[2], x),
        max(acc[3], x)
    )
)
# More efficient than multiple passes
```

### Recursive Reduction

```python
# Reduce nested structure
@dataclass
class Tree(Generic[T]):
    value: T
    left: 'Tree[T] | None'
    right: 'Tree[T] | None'

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Reduce tree values"""
        left_val = self.left.reduce(func) if self.left else None
        right_val = self.right.reduce(func) if self.right else None

        result = self.value
        if left_val is not None:
            result = func(result, left_val)
        if right_val is not None:
            result = func(result, right_val)

        return result

# Usage
tree = Tree(3, Tree(1, None, None), Tree(2, None, None))
total = tree.reduce(lambda a, b: a + b)  # 6
```

## Protocol Compliance

```python
@runtime_checkable
class Reducible(Protocol[T]):
    def reduce(self, func): ...
    def fold_left(self, initial, func): ...

class CustomCollection:
    def __init__(self, items):
        self._items = items

    def reduce(self, func):
        result = self._items[0]
        for item in self._items[1:]:
            result = func(result, item)
        return result

    def fold_left(self, initial, func):
        result = initial
        for item in self._items:
            result = func(result, item)
        return result

# CustomCollection is Reducible!
isinstance(CustomCollection([1, 2, 3]), Reducible)  # True
```

## Best Practices

### ✅ Do: Use fold_left for safety

```python
# Safe: Works with empty collections
result = items.fold_left(0, lambda acc, x: acc + x)

# Unsafe: Requires non-empty
result = items.reduce(lambda a, b: a + b)  # Error if empty!
```

### ✅ Do: Use aggregation helpers

```python
# Clear
total = numbers.sum()

# Instead of
total = numbers.reduce(lambda a, b: a + b)
```

### ❌ Don't: Reduce when you can use built-in

```python
# Slower
sum_nums = numbers.reduce(lambda a, b: a + b)

# Faster
sum_nums = sum(numbers.to_list())
```

## Summary

**Reducible** protocol:
- ✅ Reduce collections to single values
- ✅ `reduce()` - No initial, requires non-empty
- ✅ `fold_left()` - With initial, works with empty
- ✅ Aggregation helpers (sum, min, max, avg)
- ✅ Group by and fold

**Implementations**:
- `ReducibleList[T]` - Reducible list
- `ReducibleDict[K, V]` - Reducible dict

---

**Next**: See [Combinable](./03-combinable.md) for combinable entities.
