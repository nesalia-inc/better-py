# LazySequence: Lazy Evaluation Sequences

A lazy sequence implementation for infinite streams, deferred computation, and memory-efficient iteration.

## Overview

```python
@dataclass(frozen=True, slots=True)
class LazySequence(Generic[T]):
    """Lazy sequence with deferred evaluation"""
    _iterator: Iterator[T]
    _cache: list[T] = field(default_factory=list)
    _exhausted: bool = False
```

## Key Features

- ✅ **Lazy**: Values computed only when accessed
- ✅ **Infinite**: Can represent infinite sequences
- ✅ **Memory efficient**: Only stores accessed values
- ✅ **Composable**: Chain operations without intermediate lists
- ✅ **Reusable**: Can iterate multiple times (with caching)

## Creation

```python
from mfn.collections import LazySequence

# From generator
seq = LazySequence.from_generator(lambda: (x * 2 for x in range(10)))

# From iterable (evaluated lazily)
seq = LazySequence.from_iterable(range(1000000))

# Range
seq = LazySequence.range(0, 100)  # 0, 1, 2, ..., 99

# Infinite range
seq = LazySequence.infinite_range(0)  # 0, 1, 2, ... (infinite)

# Constant
seq = LazySequence.constant(42)  # 42, 42, 42, ... (infinite)

# Cycle
seq = LazySequence.cycle([1, 2, 3])  # 1, 2, 3, 1, 2, 3, ... (infinite)

# Repeat
seq = LazySequence.repeat(5)  # 5, 5, 5, ... (infinite)
```

## Lazy Transformations

### map

```python
seq = LazySequence.infinite_range(1)

# Lazy map (no computation yet)
doubled = seq.map(lambda x: x * 2)

# Values computed on access
for i, val in enumerate(doubled):
    print(val)  # 2, 4, 6, 8, ...
    if i >= 4:
        break
```

### filter

```python
# Infinite range
seq = LazySequence.infinite_range(1)

# Lazy filter
evens = seq.filter(lambda x: x % 2 == 0)

# Compute on demand
for i, val in enumerate(evens):
    print(val)  # 2, 4, 6, 8, ...
    if i >= 4:
        break
```

### flat_map

```python
seq = LazySequence.range(1, 4)  # 1, 2, 3

# Lazy flat_map
pairs = seq.flat_map(lambda x: [x, x * 10])

list(pairs)  # [1, 10, 2, 20, 3, 30]
```

### take

```python
# Infinite sequence
seq = LazySequence.infinite_range(1)

# Take first n
first_10 = seq.take(10)  # LazySequence([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Still lazy!
type(first_10)  # LazySequence (not evaluated yet)

# Force evaluation
list(first_10)  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

### take_while

```python
seq = LazySequence.infinite_range(1)

# Take while condition holds
less_than_10 = seq.take_while(lambda x: x < 10)

list(less_than_10)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### drop / drop_while

```python
seq = LazySequence.range(1, 11)  # 1, 2, 3, ..., 10

# Drop first n
from_5 = seq.drop(4)  # 5, 6, 7, 8, 9, 10

# Drop while condition
from_5_on = seq.drop_while(lambda x: x < 5)  # 5, 6, 7, 8, 9, 10
```

### distinct

```python
seq = LazySequence.from_iterable([1, 2, 2, 3, 3, 3, 4])

# Lazy distinct
unique = seq.distinct()

list(unique)  # [1, 2, 3, 4]
```

## Reduction Operations

### reduce

```python
seq = LazySequence.range(1, 6)  # 1, 2, 3, 4, 5

# Reduce (requires finite)
sum_ = seq.reduce(lambda a, b: a + b)  # 15

# Error on infinite
infinite = LazySequence.infinite_range(1)
infinite.reduce(lambda a, b: a + b)  # Infinite loop!
```

### fold_left

```python
seq = LazySequence.range(1, 6)

# Fold with initial
from_10 = seq.fold_left(10, lambda acc, x: acc + x)  # 25
```

### first / last

```python
seq = LazySequence.range(1, 100)

# First element
first = seq.first()  # Some(1)

# Last (requires finite!)
last = seq.last()  # Some(99)

# Infinite sequence
infinite = LazySequence.infinite_range(1)
infinite.last()  # Infinite loop!
```

### head / tail

```python
seq = LazySequence.range(1, 10)

# Head (first element)
head = seq.head()  # Some(1)

# Tail (rest)
tail = seq.tail()  # LazySequence([2, 3, 4, 5, 6, 7, 8, 9])
```

## Query Operations

### find

```python
seq = LazySequence.infinite_range(1)

# Find first match (lazy!)
found = seq.find(lambda x: x > 100)  # Some(101)

# Not found
not_found = seq.find(lambda x: x < 0)  # None_
```

### exists / for_all

```python
seq = LazySequence.range(1, 100)

# Any match?
has_even = seq.exists(lambda x: x % 2 == 0)  # True

# All match?
all_positive = seq.for_all(lambda x: x > 0)  # True

# Infinite: be careful!
infinite = LazySequence.infinite_range(1)
infinite.for_all(lambda x: x > 0)  # True (OK)
infinite.exists(lambda x: x < 0)  # False (OK)
```

### contains

```python
seq = LazySequence.range(1, 100)

has_50 = seq.contains(50)  # True
has_100 = seq.contains(100)  # False
```

## Combining Sequences

### zip

```python
nums = LazySequence.range(1, 4)  # 1, 2, 3
letters = LazySequence.from_iterable(['a', 'b', 'c'])

# Zip (stops at shortest)
zipped = nums.zip(letters)

list(zipped)  # [(1, 'a'), (2, 'b'), (3, 'c')]
```

### zip_with_index

```python
seq = LazySequence.range(10, 15)

# With indices
indexed = seq.zip_with_index()

list(indexed)  # [(0, 10), (1, 11), (2, 12), (3, 13), (4, 14)]
```

### merge / interleave

```python
seq1 = LazySequence.range(1, 4)  # 1, 2, 3
seq2 = LazySequence.range(4, 7)  # 4, 5, 6

# Merge (concatenate)
merged = seq1.merge(seq2)  # 1, 2, 3, 4, 5, 6

# Interleave
interleaved = seq1.interleave(seq2)  # 1, 4, 2, 5, 3, 6
```

### enumerate

```python
seq = LazySequence.range(10, 15)

# Enumerate
indexed = seq.enumerate()

list(indexed)  # [(0, 10), (1, 11), (2, 12), (3, 13), (4, 14)]
```

## Special Sequences

### fibonacci

```python
# Fibonacci sequence (infinite)
fib = LazySequence.fibonacci()

list(fib.take(10))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### primes

```python
# Prime numbers (infinite)
primes = LazySequence.primes()

list(primes.take(10))  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### random

```python
import random

# Random sequence (infinite)
seq = LazySequence.random(lambda: random.randint(1, 100))

list(seq.take(5))  # [42, 17, 83, 5, 91]  # Random values
```

### iterate

```python
# Iterate with function
seq = LazySequence.iterate(1, lambda x: x * 2)

list(seq.take(10))  # [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
```

## Conversion

### force / to_list

```python
seq = LazySequence.range(1, 1000)

# Force evaluation (caches all values)
seq.force()

# Now cached, fast access
list(seq)  # Fast (from cache)

# Convert to list
python_list = seq.to_list()  # [1, 2, 3, ..., 999] (caches all)
```

### cache

```python
seq = LazySequence.infinite_range(1)

# Cache first 10 values
cached = seq.cache(10)

# Now cached
for val in cached.take(10):
    print(val)  # Fast (from cache)
```

### skip / limit

```python
seq = LazySequence.range(1, 100)

# Alias for take
first_10 = seq.limit(10)  # [1, 2, 3, ..., 10]

# Alias for drop
from_90 = seq.skip(10)  # [11, 12, 13, ...]
```

## Advanced Operations

### group_by

```python
seq = LazySequence.range(1, 11)

# Group by parity
groups = seq.group_by(lambda x: x % 2)  # Lazy!

# Force evaluation
by_parity = {k: list(v) for k, v in groups.items()}
# {1: [1, 3, 5, 7, 9], 0: [2, 4, 6, 8, 10]}
```

### chunk

```python
seq = LazySequence.range(1, 11)

# Chunk by size
chunks = seq.chunk(3)

list(list(c) for c in chunks)  # [[1,2,3], [4,5,6], [7,8,9], [10]]
```

### sliding_window

```python
seq = LazySequence.range(1, 6)

# Sliding window
windows = seq.sliding_window(3)

list(list(w) for w in windows)  # [[1,2,3], [2,3,4], [3,4,5]]
```

## Use Cases

### Stream Processing

```python
# Process large file without loading all into memory
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()

lines = LazySequence.from_generator(lambda: read_lines("huge.txt"))

# Lazy processing
non_empty = (
    lines
    .filter(lambda line: line)  # Skip empty
    .map(lambda line: line.upper())  # Transform
    .take(1000)  # Only first 1000
)

# Process one at a time (memory efficient)
for line in non_empty:
    process(line)
```

### Infinite Sequence

```python
# Generate all even numbers (infinite)
evens = LazySequence.infinite_range(1).filter(lambda x: x % 2 == 0)

# Take first 10
list(evens.take(10))  # [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
```

### Pagination

```python
# Paginated API (lazy!)
def fetch_page(page):
    return api_call(f"/users?page={page}")

all_users = LazySequence.paginated(fetch_page)

# Lazy: only fetches pages as needed
first_20 = all_users.take(20)

for user in first_20:
    print(user)  # Fetches page 1 (20 users)
```

## Caching Behavior

```python
seq = LazySequence.range(1, 1000)

# First iteration: computes all
for val in seq.take(10):
    print(val)  # Computes 1, 2, 3, ..., 10

# Second iteration: from cache
for val in seq.take(10):
    print(val)  # From cache (fast)
```

## Performance

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| `map()` | O(1) | O(1) | Lazy |
| `filter()` | O(1) | O(1) | Lazy |
| `take(n)` | O(1) | O(1) | Lazy |
| `reduce()` | O(n) | O(n) | Forces evaluation |
| `to_list()` | O(n) | O(n) | Forces evaluation |
| Iteration | O(1) per | O(k) | k = values accessed |

## Best Practices

### ✅ Do: Use for large/infinite data

```python
# Good: Process large files
lines = LazySequence.from_generator(read_lines)
```

### ✅ Do: Chain operations

```python
# Good: Still lazy
result = seq.filter(p).map(f).take(10)
```

### ❌ Don't: Use when you need all values

```python
# Bad: Forces evaluation anyway
result = list(seq.map(f).filter(f))

# Better: Use MappableList
result = MappableList(items).map(f).filter(g)
```

## Examples

### Sieve of Eratosthenes

```python
def sieve():
    """Generate primes (infinite)"""
    composites = set()
    n = 2
    while True:
        if n not in composites:
            yield n
            # Mark multiples
            for i in range(n * n, n * n + 100, n):
                composites.add(i)
        n += 1

primes = LazySequence.from_generator(sieve)
list(primes.take(10))  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### Collatz Sequence

```python
def collatz(n):
    """Generate Collatz sequence"""
    while n > 1:
        yield n
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    yield n

seq = LazySequence.from_generator(lambda: collatz(27))
list(seq)  # [27, 82, 41, 124, 62, 31, 94, 47, ...]
```

## See Also

- [MappableList](./01-mappable-list.md) - Eager functional list
- [ImmutableList](./04-immutable-list.md) - Immutable list
- [Core: Lazy Collections](../13-lazy-collections.md) - Lazy evaluation patterns

---

**Next**: [BiDirectionalMap](./06-bidirectional-map.md)
