# MappableList: Functional List Operations

A functional list implementation with immutable transformations (`map`, `filter`, `reduce`) and type-safe operations.

## Overview

```python
@dataclass(frozen=True, slots=True)
class MappableList(Generic[T]):
    """Immutable functional list with map/filter/reduce"""
    _data: list[T]
```

## Creation

```python
from mfn.collections import MappableList

# From list
numbers = MappableList([1, 2, 3, 4, 5])

# From iterable
numbers = MappableList.range(1, 6)  # [1, 2, 3, 4, 5]

# Empty
empty = MappableList.empty()

# From generator
squared = MappableList.from_generator(x*x for x in range(5))
```

## Transformation Operations

### map

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Double each element
doubled = numbers.map(lambda x: x * 2)
# MappableList([2, 4, 6, 8, 10])

# Type transformation
strings: MappableList[str] = numbers.map(str)
# MappableList(["1", "2", "3", "4", "5"])
```

### filter

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Even numbers
evens = numbers.filter(lambda x: x % 2 == 0)
# MappableList([2, 4])

# Positive numbers
positives = numbers.filter(lambda x: x > 0)
# MappableList([1, 2, 3, 4, 5])
```

### flat_map

```python
# Transform and flatten
numbers = MappableList([[1, 2], [3, 4], [5]])
flattened = numbers.flat_map(lambda lst: lst)
# MappableList([1, 2, 3, 4, 5])

# Create pairs
numbers = MappableList([1, 2, 3])
pairs = numbers.flat_map(lambda x: [x, x * 2])
# MappableList([1, 2, 2, 4, 3, 6])
```

## Reduction Operations

### reduce

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Sum
sum_ = numbers.reduce(lambda a, b: a + b)  # 15

# Product
product = numbers.reduce(lambda a, b: a * b)  # 120

# Max
max_ = numbers.reduce(lambda a, b: a if a > b else b)  # 5
```

### fold_left

```python
numbers = MappableList([1, 2, 3, 4, 5])

# With initial value
sum_from_10 = numbers.fold_left(10, lambda acc, x: acc + x)  # 25

# Build different type
concat = numbers.fold_left("", lambda s, x: f"{s}{x}")  # "12345"
```

## Query Operations

### find

```python
users = MappableList([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
])

# Find first matching
found = users.find(lambda u: u["age"] >= 30)
# Some({"name": "Alice", "age": 30})

not_found = users.find(lambda u: u["age"] > 100)
# None_
```

### exists / for_all

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Any match?
has_even = numbers.exists(lambda x: x % 2 == 0)  # True
has_negative = numbers.exists(lambda x: x < 0)  # False

# All match?
all_positive = numbers.for_all(lambda x: x > 0)  # True
all_even = numbers.for_all(lambda x: x % 2 == 0)  # False
```

### contains

```python
numbers = MappableList([1, 2, 3, 4, 5])

has_3 = numbers.contains(3)  # True
has_10 = numbers.contains(10)  # False
```

## Access Operations

### first / last

```python
numbers = MappableList([1, 2, 3, 4, 5])

first = numbers.first()  # Some(1)
last = numbers.last()  # Some(5)

empty = MappableList([])
first_empty = empty.first()  # None_
```

### get

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Get by index
value = numbers.get(0)  # 1
value = numbers.get(10)  # None (out of range)

# With default
value = numbers.get(10, default=0)  # 0
```

## Grouping Operations

### group_by

```python
users = MappableList([
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob", "dept": "Sales"},
    {"name": "Charlie", "dept": "Engineering"},
])

by_dept = users.group_by(lambda u: u["dept"])
# {
#     "Engineering": MappableList([{"name": "Alice", ...}, {"name": "Charlie", ...}]),
#     "Sales": MappableList([{"name": "Bob", ...}])
# }
```

### partition

```python
numbers = MappableList([1, 2, 3, 4, 5, 6])

# Split by predicate
evens, odds = numbers.partition(lambda x: x % 2 == 0)
# evens: MappableList([2, 4, 6])
# odds: MappableList([1, 3, 5])
```

### distinct

```python
numbers = MappableList([1, 2, 2, 3, 3, 3, 4])

unique = numbers.distinct()
# MappableList([1, 2, 3, 4])
```

## Ordering Operations

### sort

```python
numbers = MappableList([3, 1, 4, 1, 5, 9, 2, 6])

# Ascending
sorted_nums = numbers.sort()
# MappableList([1, 1, 2, 3, 4, 5, 6, 9])

# Descending
sorted_desc = numbers.sort(reverse=True)
# MappableList([9, 6, 5, 4, 3, 2, 1, 1])

# By key
users = MappableList([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
])
by_age = users.sort(key=lambda u: u["age"])
# [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
```

### reverse

```python
numbers = MappableList([1, 2, 3, 4, 5])

reversed_nums = numbers.reverse()
# MappableList([5, 4, 3, 2, 1])
```

## Set Operations

```python
list1 = MappableList([1, 2, 3, 4])
list2 = MappableList([3, 4, 5, 6])

# Union
combined = list1.union(list2)  # [1, 2, 3, 4, 5, 6]

# Intersection
common = list1.intersect(list2)  # [3, 4]

# Difference
diff = list1.difference(list2)  # [1, 2]
```

## Conversion Operations

```python
numbers = MappableList([1, 2, 3, 4, 5])

# To built-in types
python_list = numbers.to_list()  # [1, 2, 3, 4, 5]
python_tuple = numbers.to_tuple()  # (1, 2, 3, 4, 5)
python_set = numbers.to_set()  # {1, 2, 3, 4, 5}
python_dict = numbers.to_dict(lambda x: str(x): x)  # {"1": 1, "2": 2, ...}

# String
joined = numbers.join(", ")  # "1, 2, 3, 4, 5"
```

## Chaining Operations

```python
result = (
    MappableList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    .filter(lambda x: x % 2 == 0)     # [2, 4, 6, 8, 10]
    .map(lambda x: x * 2)             # [4, 8, 12, 16, 20]
    .filter(lambda x: x > 10)         # [12, 16, 20]
    .sort()                           # [12, 16, 20]
    .reduce(lambda a, b: a + b)       # 48
)
```

## Information Operations

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Size
len(numbers)  # 5
numbers.size()  # 5
numbers.is_empty()  # False

# Check
bool(numbers)  # True
bool(MappableList([]))  # False
```

## Iteration

```python
numbers = MappableList([1, 2, 3, 4, 5])

# Iterate
for num in numbers:
    print(num)

# For each (side effects)
numbers.for_each(print)

# List comprehension compatible
result = [x * 2 for x in numbers]  # [2, 4, 6, 8, 10]
```

## Class Methods

```python
# Empty list
empty = MappableList.empty()

# Range
nums = MappableList.range(1, 6)  # [1, 2, 3, 4, 5]

# Generate
nums = MappableList.generate(5, lambda i: i * 2)  # [0, 2, 4, 6, 8]

# From iterable
nums = MappableList.from_iterable(range(5))  # [0, 1, 2, 3, 4]

# From generator
nums = MappableList.from_generator(x*x for x in range(5))  # [0, 1, 4, 9, 16]
```

## Performance

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| `map()` | O(n) | O(n) |
| `filter()` | O(n) | O(n) |
| `reduce()` | O(n) | O(1) |
| `get(i)` | O(1) | O(1) |
| `sort()` | O(n log n) | O(n) |
| `group_by()` | O(n) | O(n) |
| `distinct()` | O(n) | O(n) |

## Best Practices

### ✅ Do: Chain operations

```python
result = (
    items
    .filter(is_valid)
    .map(transform)
    .distinct()
    .sort()
)
```

### ✅ Do: Use method chaining

```python
# Clear and readable
numbers.filter(lambda x: x > 0).map(lambda x: x * 2)
```

### ❌ Don't: Mix paradigms

```python
# Confusing
result = MappableList(numbers).map(lambda x: x * 2)._data

# Better: Stay consistent
result = MappableList(numbers).map(lambda x: x * 2)
```

## Examples

### Data Processing Pipeline

```python
data = MappableList([
    {"name": "Alice", "age": 30, "salary": 50000},
    {"name": "Bob", "age": 25, "salary": 45000},
    {"name": "Charlie", "age": 35, "salary": 60000},
])

# Find high earners under 40
result = (
    data
    .filter(lambda p: p["age"] < 40)
    .filter(lambda p: p["salary"] > 50000)
    .map(lambda p: p["name"])
)
# MappableList(["Charlie"])
```

### Word Count

```python
text = "hello world hello python world"

words = MappableList(text.split())

# Count words
word_counts = (
    words
    .group_by(lambda w: w)
    .map(lambda item: (item[0], len(item[1])))
)
# {"hello": 2, "world": 2, "python": 1}
```

### Prime Numbers

```python
# Sieve of Eratosthenes
def primes_upto(n: int) -> MappableList[int]:
    numbers = MappableList.range(2, n + 1)

    for i in range(2, int(n**0.5) + 1):
        numbers = numbers.filter(lambda x: x == i or x % i != 0)

    return numbers

primes = primes_upto(30)
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

## See Also

- [Entities: Mappable](../entities/01-mappable.md) - Protocol definition
- [MappableDict](./02-mappable-dict.md) - Dictionary version
- [ImmutableList](./04-immutable-list.md) - Persistent list
- [LazySequence](./05-lazy-sequence.md) - Lazy evaluation

---

**Next**: [MappableDict](./02-mappable-dict.md)
