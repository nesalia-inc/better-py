# ImmutableList: Immutable Persistent List

An immutable persistent list with efficient prepend/append operations and structural sharing.

## Overview

```python
@dataclass(frozen=True, slots=True)
class ImmutableList(Generic[T]):
    """Immutable persistent list"""
    _data: list[T]
```

## Key Features

- ✅ **Immutable**: All operations return new instances
- ✅ **Efficient prepends**: O(1) prepend
- ✅ **Efficient appends**: O(1) amortized append
- ✅ **Structural sharing**: Memory efficient
- ✅ **Type-safe**: Generic types

## Creation

```python
from mfn.collections import ImmutableList

# From list
numbers = ImmutableList([1, 2, 3, 4, 5])

# Empty
empty = ImmutableList.empty()

# From iterable
numbers = ImmutableList.from_iterable(range(5))  # [0, 1, 2, 3, 4]

# Single element
single = ImmutableList.of(1)  # [1]
```

## Basic Operations

### append

```python
numbers = ImmutableList([1, 2, 3])

# Append element
numbers2 = numbers.append(4)
# ImmutableList([1, 2, 3, 4])

# Original unchanged
numbers._data  # [1, 2, 3]

# Chain appends
numbers3 = numbers.append(4).append(5)
# ImmutableList([1, 2, 3, 4, 5])
```

### prepend

```python
numbers = ImmutableList([2, 3, 4])

# Prepend element
numbers2 = numbers.prepend(1)
# ImmutableList([1, 2, 3, 4])

# Chain prepends
numbers3 = numbers.prepend(1).prepend(0)
# ImmutableList([0, 1, 2, 3, 4])
```

### insert

```python
numbers = ImmutableList([1, 2, 4, 5])

# Insert at index
numbers2 = numbers.insert(2, 3)
# ImmutableList([1, 2, 3, 4, 5])

# Insert at beginning
numbers3 = numbers.insert(0, 0)
# ImmutableList([0, 1, 2, 4, 5])
```

### extend

```python
numbers = ImmutableList([1, 2, 3])

# Extend with list
numbers2 = numbers.extend([4, 5])
# ImmutableList([1, 2, 3, 4, 5])

# Extend with another ImmutableList
numbers3 = numbers2.extend(ImmutableList([6, 7]))
# ImmutableList([1, 2, 3, 4, 5, 6, 7])
```

## Update Operations

### set

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Set at index
numbers2 = numbers.set(2, 99)
# ImmutableList([1, 2, 99, 4, 5])

# Original unchanged
numbers._data  # [1, 2, 3, 4, 5]
```

### update

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Update with function
doubled = numbers.update(2, lambda x: x * 2)
# ImmutableList([1, 2, 6, 4, 5])

# Update multiple
updated = numbers.update(0, lambda x: x + 10).update(4, lambda x: x - 10)
# ImmutableList([11, 2, 3, 4, -5])
```

### remove

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Remove by value
numbers2 = numbers.remove(3)
# ImmutableList([1, 2, 4, 5])

# Remove first occurrence
numbers3 = ImmutableList([1, 2, 2, 3]).remove(2)
# ImmutableList([1, 2, 3])
```

### remove_at

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Remove by index
numbers2 = numbers.remove_at(2)
# ImmutableList([1, 2, 4, 5])
```

### remove_if

```python
numbers = ImmutableList([1, 2, 3, 4, 5, 6])

# Remove matching elements
evens = numbers.remove_if(lambda x: x % 2 == 0)
# ImmutableList([1, 3, 5])

# Remove negatives
positives = ImmutableList([-1, 2, -3, 4]).remove_if(lambda x: x < 0)
# ImmutableList([2, 4])
```

## Query Operations

### get

```python
numbers = ImmutableList([10, 20, 30, 40, 50])

# Get by index
value = numbers.get(0)  # 10
value = numbers.get(4)  # 50

# Out of range
value = numbers.get(10)  # None

# With default
value = numbers.get(10, default=0)  # 0
```

### first / last

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# First element
first = numbers.first()  # Some(1)

# Last element
last = numbers.last()  # Some(5)

# Empty list
empty = ImmutableList()
first_empty = empty.first()  # None_
last_empty = empty.last()  # None_
```

### head / tail

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Head (first element)
head = numbers.head()  # Some(1)

# Tail (rest of list)
tail = numbers.tail()  # ImmutableList([2, 3, 4, 5])
```

### take / drop

```python
numbers = ImmutableList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Take first n
first_3 = numbers.take(3)  # [1, 2, 3]

# Drop first n
rest = numbers.drop(3)  # [4, 5, 6, 7, 8, 9, 10]

# Take last
last_3 = numbers.take_last(3)  # [8, 9, 10]

# Drop last
without_last = numbers.drop_last(3)  # [1, 2, 3, 4, 5, 6, 7]
```

### slice

```python
numbers = ImmutableList([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

# Slice
middle = numbers.slice(2, 7)  # [2, 3, 4, 5, 6]

# Slice from start
first_5 = numbers.slice(0, 5)  # [0, 1, 2, 3, 4]

# Slice to end
from_5 = numbers.slice(5)  # [5, 6, 7, 8, 9]
```

## Transformation Operations

### map

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Transform
doubled = numbers.map(lambda x: x * 2)
# ImmutableList([2, 4, 6, 8, 10])

# Type change
strings = numbers.map(str)
# ImmutableList(["1", "2", "3", "4", "5"])
```

### filter

```python
numbers = ImmutableList([1, 2, 3, 4, 5, 6])

# Keep evens
evens = numbers.filter(lambda x: x % 2 == 0)
# ImmutableList([2, 4, 6])

# Keep positives
positives = ImmutableList([-1, 2, -3, 4]).filter(lambda x: x > 0)
# ImmutableList([2, 4])
```

### flat_map

```python
numbers = ImmutableList([[1, 2], [3, 4], [5]])

# Flatten
flattened = numbers.flat_map(lambda lst: lst)
# ImmutableList([1, 2, 3, 4, 5])

# Expand
pairs = ImmutableList([1, 2, 3]).flat_map(lambda x: [x, x * 2])
# ImmutableList([1, 2, 2, 4, 3, 6])
```

## Reduction Operations

### reduce

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Sum
sum_ = numbers.reduce(lambda a, b: a + b)  # 15

# Product
product = numbers.reduce(lambda a, b: a * b)  # 120

# Min/Max
min_ = numbers.reduce(lambda a, b: a if a < b else b)  # 1
max_ = numbers.reduce(lambda a, b: a if a > b else b)  # 5
```

### fold_left

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# With initial
from_10 = numbers.fold_left(10, lambda acc, x: acc + x)  # 25

# Build string
concat = numbers.fold_left("", lambda s, x: f"{s}{x}")  # "12345"

# Build dict
numbered = numbers.fold_left(
    {},
    lambda d, x: {**d, str(x): x}
)  # {"1": 1, "2": 2, ...}
```

## Searching

### find

```python
users = ImmutableList([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
])

# Find first matching
found = users.find(lambda u: u["age"] >= 30)
# Some({"name": "Alice", "age": 30})

# Not found
not_found = users.find(lambda u: u["age"] > 100)
# None_
```

### find_index

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Find index
idx = numbers.find_index(lambda x: x == 3)  # Some(2)

# Not found
not_found = numbers.find_index(lambda x: x == 10)  # None_
```

### contains

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

has_3 = numbers.contains(3)  # True
has_10 = numbers.contains(10)  # False
```

### exists / for_all

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Any match?
has_even = numbers.exists(lambda x: x % 2 == 0)  # True
has_negative = numbers.exists(lambda x: x < 0)  # False

# All match?
all_positive = numbers.for_all(lambda x: x > 0)  # True
all_even = numbers.for_all(lambda x: x % 2 == 0)  # False
```

## Ordering

### sort

```python
numbers = ImmutableList([3, 1, 4, 1, 5, 9, 2, 6])

# Ascending
sorted_nums = numbers.sort()
# ImmutableList([1, 1, 2, 3, 4, 5, 6, 9])

# Descending
sorted_desc = numbers.sort(reverse=True)
# ImmutableList([9, 6, 5, 4, 3, 2, 1, 1])

# By key
users = ImmutableList([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
])
by_age = users.sort(key=lambda u: u["age"])
# [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
```

### reverse

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

reversed_nums = numbers.reverse()
# ImmutableList([5, 4, 3, 2, 1])
```

### shuffle

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Random order
shuffled = numbers.shuffle()
# ImmutableList([3, 1, 5, 2, 4])  # Order varies
```

## Set Operations

### distinct

```python
numbers = ImmutableList([1, 2, 2, 3, 3, 3, 4])

unique = numbers.distinct()
# ImmutableList([1, 2, 3, 4])
```

### union / intersect / difference

```python
list1 = ImmutableList([1, 2, 3, 4])
list2 = ImmutableList([3, 4, 5, 6])

# Union
combined = list1.union(list2)  # [1, 2, 3, 4, 5, 6]

# Intersection
common = list1.intersect(list2)  # [3, 4]

# Difference
diff = list1.difference(list2)  # [1, 2]
```

## Conversion

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# To Python list
python_list = numbers.to_list()  # [1, 2, 3, 4, 5]

# To tuple
python_tuple = numbers.to_tuple()  # (1, 2, 3, 4, 5)

# To set
python_set = numbers.to_set()  # {1, 2, 3, 4, 5}

# To dict
indexed = numbers.to_dict(lambda x: str(x): x)
# {"1": 1, "2": 2, ...}

# Join
joined = numbers.join(", ")  # "1, 2, 3, 4, 5"
```

## Information

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Size
len(numbers)  # 5
numbers.size()  # 5

# Empty?
numbers.is_empty()  # False

# Boolean
bool(numbers)  # True
bool(ImmutableList())  # False
```

## Special Operations

### zip

```python
numbers = ImmutableList([1, 2, 3])
letters = ImmutableList(['a', 'b', 'c'])

# Zip
zipped = numbers.zip(letters)
# ImmutableList([(1, 'a'), (2, 'b'), (3, 'c')])
```

### zip_with_index

```python
numbers = ImmutableList([10, 20, 30, 40])

# With indices
indexed = numbers.zip_with_index()
# ImmutableList([(0, 10), (1, 20), (2, 30), (3, 40)])
```

### partition

```python
numbers = ImmutableList([1, 2, 3, 4, 5, 6])

# Split by predicate
evens, odds = numbers.partition(lambda x: x % 2 == 0)
# evens: ImmutableList([2, 4, 6])
# odds: ImmutableList([1, 3, 5])
```

### group_by

```python
users = ImmutableList([
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob", "dept": "Sales"},
    {"name": "Charlie", "dept": "Eng"},
])

by_dept = users.group_by(lambda u: u["dept"])
# {
#     "Eng": ImmutableList([{"name": "Alice", ...}, {"name": "Charlie", ...}]),
#     "Sales": ImmutableList([{"name": "Bob", ...}])
# }
```

## Chunking

### chunk

```python
numbers = ImmutableList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Chunk by size
chunks = numbers.chunk(3)
# ImmutableList([
#     ImmutableList([1, 2, 3]),
#     ImmutableList([4, 5, 6]),
#     ImmutableList([7, 8, 9]),
#     ImmutableList([10])
# ])
```

### sliding

```python
numbers = ImmutableList([1, 2, 3, 4, 5])

# Sliding window
windows = numbers.sliding(2)
# ImmutableList([
#     ImmutableList([1, 2]),
#     ImmutableList([2, 3]),
#     ImmutableList([3, 4]),
#     ImmutableList([4, 5])
# ])
```

## Use Cases

### Log / Event Stream

```python
# Immutable append-only log
log = ImmutableList()

log = log.append({"event": "start", "time": "2024-01-01T00:00:00"})
log = log.append({"event": "process", "time": "2024-01-01T00:00:01"})
log = log.append({"event": "complete", "time": "2024-01-01T00:00:02"})

# All events preserved
# Original references still valid
```

### Undo History

```python
# Immutable undo stack
history = ImmutableList()

# Push state
history = history.append(state1)
history = history.append(state2)
history = history.append(state3)

# Undo (pop last)
current = history.last()
history = history.drop_last(1)  # Removes last

# Redo (from backup)
backup = history  # Save before undo
# ... undo ...
history = backup  # Restore
```

### Pipeline Stages

```python
# Build pipeline
pipeline = ImmutableList()

pipeline = pipeline.append(validate)
pipeline = pipeline.append(transform)
pipeline = pipeline.append(save)

# Execute
def run_pipeline(data, pipeline):
    for stage in pipeline:
        data = stage(data)
    return data
```

## Performance

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| `append()` | O(1)* | Amortized |
| `prepend()` | O(1)* | Amortized |
| `insert(i)` | O(n) | Copies list |
| `set(i)` | O(n) | Copies list |
| `get(i)` | O(1) | Direct access |
| `map()` | O(n) | Creates new list |

*With structural sharing implementation

## Best Practices

### ✅ Do: Use for append-only data

```python
# Good: Log, event stream
log = ImmutableList().append(event1).append(event2)
```

### ✅ Do: Chain operations

```python
# Good: Readable
result = numbers.filter(p).map(f).distinct()
```

### ❌ Don't: Use for random access

```python
# Bad: Slow for large lists
for i in range(10000):
    value = immutable_list.get(i)

# Better: Use built-in list or array
values = immutable_list.to_list()
for i in range(len(values)):
    value = values[i]
```

## See Also

- [Core: Immutability](../core/03-immutability.md) - Immutability patterns
- [MappableList](./01-mappable-list.md) - Functional list with map/filter
- [ImmutableDict](./03-immutable-dict.md) - Immutable dict
- [LazySequence](./05-lazy-sequence.md) - Lazy evaluation

---

**Next**: [LazySequence](./05-lazy-sequence.md)
