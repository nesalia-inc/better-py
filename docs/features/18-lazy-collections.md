# Lazy Collections - Efficient Evaluation

Process large datasets efficiently with lazy evaluation and computation on demand.

## Overview

Lazy collections enable:
- Process large datasets without memory issues
- Computation only when needed
- Infinite sequences
- Chainable operations
- Memory efficiency

## Basic Lazy Sequence

```python
from typing import Callable, Iterator, TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')

class LazySequence(Generic[T]):
    """Lazy sequence with deferred computation"""

    def __init__(self, iterator_factory: Callable[[], Iterator[T]]):
        self._iterator_factory = iterator_factory

    def __iter__(self) -> Iterator[T]:
        return self._iterator_factory()

    def map(self, func: Callable[[T], U]) -> 'LazySequence[U]':
        """Map over elements lazily"""

        def mapped_factory():
            return (func(item) for item in self._iterator_factory())

        return LazySequence(mapped_factory)

    def filter(self, predicate: Callable[[T], bool]) -> 'LazySequence[T]':
        """Filter elements lazily"""

        def filtered_factory():
            return (item for item in self._iterator_factory() if predicate(item))

        return LazySequence(filtered_factory)

    def take(self, n: int) -> list[T]:
        """Take first n elements"""
        result = []
        for item in self._iterator_factory():
            result.append(item)
            if len(result) >= n:
                break
        return result

    def skip(self, n: int) -> 'LazySequence[T]':
        """Skip first n elements"""

        def skipped_factory():
            iterator = self._iterator_factory()
            for _ in range(n):
                try:
                    next(iterator)
                except StopIteration:
                    break
            return iterator

        return LazySequence(skipped_factory)

    def to_list(self) -> list[T]:
        """Materialize entire sequence"""
        return list(self._iterator_factory())


# === Usage ===

def count_from(n: int):
    """Infinite counter"""
    while True:
        yield n
        n += 1

# Create infinite lazy sequence
numbers = LazySequence(count_from(0))

# Only compute first 5
first_five = numbers.take(5)
print(first_five)  # [0, 1, 2, 3, 4]

# Chain operations (still lazy!)
evens = numbers.skip(1).filter(lambda x: x % 2 == 0).map(lambda x: x * 2)

# Only compute what we use
print(evens.take(5))  # [4, 8, 12, 16, 20]
```

## Lazy Range

```python
class LazyRange:
    """Memory-efficient range with additional operations"""

    def __init__(self, start: int, stop: int | None = None, step: int = 1):
        if stop is None:
            self.start = 0
            self.stop = start
        else:
            self.start = start
            self.stop = stop
        self.step = step

    def __iter__(self):
        current = self.start
        while current < self.stop:
            yield current
            current += self.step

    def map(self, func):
        """Map lazily"""
        return LazySequence(lambda: (func(x) for x in self))

    def filter(self, predicate):
        """Filter lazily"""
        return LazySequence(lambda: (x for x in self if predicate(x)))

    def __repr__(self):
        return f"LazyRange({self.start}, {self.stop}, {self.step})"


# === Usage ===

# Huge range, no memory used
huge = LazyRange(0, 1_000_000_000)

# Only compute what's needed
result = (
    huge
    .filter(lambda x: x > 500_000_000)
    .map(lambda x: x * 2)
    .take(3)
)

print(result)  # [1000000002, 1000000004, 1000000006]
```

## Lazy File Processing

```python
class LazyFile:
    """Process large files line by line"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def lines(self) -> 'LazySequence[str]':
        """Lazy file lines"""

        def line_generator():
            with open(self.filepath, 'r') as f:
                for line in f:
                    yield line.rstrip('\n')

        return LazySequence(line_generator)

    def parse(self, parser: Callable[[str], T]) -> 'LazySequence[T]':
        """Parse each line lazily"""

        def parse_generator():
            with open(self.filepath, 'r') as f:
                for line in f:
                    yield parser(line.rstrip('\n'))

        return LazySequence(parse_generator)

    def chunks(self, size: int) -> 'LazySequence[list[str]]':
        """Read file in chunks"""

        def chunk_generator():
            with open(self.filepath, 'r') as f:
                chunk = []
                for line in f:
                    chunk.append(line.rstrip('\n'))
                    if len(chunk) >= size:
                        yield chunk
                        chunk = []
                if chunk:
                    yield chunk

        return LazySequence(chunk_generator)


# === Usage ===

# Process huge file without loading into memory
large_file = LazyFile("huge_log.txt")

# Only load first 100 lines
first_100 = large_file.lines().take(100)

# Filter and parse (still lazy!)
errors = (
    large_file.lines()
    .filter(lambda line: "ERROR" in line)
    .take(10)
)
```

## Cached Lazy Sequence

```python
class CachedLazySequence(Generic[T]):
    """Lazy sequence that caches computed values"""

    def __init__(self, iterator_factory: Callable[[], Iterator[T]]):
        self._iterator_factory = iterator_factory
        self._cache: list[T] = []
        self._exhausted = False

    def __iter__(self) -> Iterator[T]:
        # Yield cached values first
        for item in self._cache:
            yield item

        # Then continue if not exhausted
        if not self._exhausted:
            for item in self._iterator_factory():
                self._cache.append(item)
                yield item
            self._exhausted = True

    def __getitem__(self, index: int) -> T:
        """Get item by index, computing as needed"""
        while index >= len(self._cache) and not self._exhausted:
            try:
                item = next(iter(self))
            except StopIteration:
                break

        if index < len(self._cache):
            return self._cache[index]

        raise IndexError("Index out of range")


# === Usage ===

def slow_generator():
    """Simulate slow computation"""
    for i in range(10):
        time.sleep(0.01)
        yield i

cached = CachedLazySequence(slow_generator)

# First access - computes
print(cached[0])  # 0 (takes 0.01s)

# Second access - from cache
print(cached[0])  # 0 (instant)

# Access out of order - computes up to that point
print(cached[5])  # 5 (computes 1-5)
```

## Infinite Sequences

```python
class Infinite:
    """Common infinite sequences"""

    @staticmethod
    def count(start: int = 0, step: int = 1) -> 'LazySequence[int]':
        """Count forever"""

        def counter():
            n = start
            while True:
                yield n
                n += step

        return LazySequence(counter)

    @staticmethod
    def cycle(sequence: list[T]) -> 'LazySequence[T]':
        """Cycle through sequence forever"""

        def cycler():
            while True:
                for item in sequence:
                    yield item

        return LazySequence(cycler)

    @staticmethod
    def repeat(value: T) -> 'LazySequence[T]':
        """Repeat value forever"""

        def repeater():
            while True:
                yield value

        return LazySequence(repeater)


# === Usage ===

# Count forever
count = Infinite.count(0, 5)
print(count.take(5))  # [0, 5, 10, 15, 20]

# Cycle through values
colors = Infinite.cycle(['red', 'green', 'blue'])
print(colors.take(5))  # ['red', 'green', 'blue', 'red', 'green']

# Repeat value
trues = Infinite.repeat(True)
print(trues.take(3))  # [True, True, True]
```

## Lazy String Processing

```python
class LazyString:
    """Process large strings lazily"""

    def __init__(self, text: str):
        self.text = text

    def lines(self) -> 'LazySequence[str]':
        """Split into lines lazily"""
        return LazySequence(lambda: iter(self.text.splitlines()))

    def chars(self) -> 'LazySequence[str]':
        """Iterate characters lazily"""
        return LazySequence(lambda: iter(self.text))

    def words(self) -> 'LazySequence[str]':
        """Split into words lazily"""
        return LazySequence(lambda: iter(self.text.split()))

    def findall(self, pattern: str) -> 'LazySequence[str]':
        """Find all matches lazily"""
        import re
        return LazySequence(lambda: iter(re.findall(pattern, self.text)))


# === Usage ===

text = LazyString("huge document text...")

# Process lines lazily
long_lines = (
    text.lines()
    .filter(lambda line: len(line) > 80)
    .take(10)
)

# Find all emails lazily
emails = text.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
```

## Lazy Group By

```python
from typing import Dict, List
from collections import defaultdict

def lazy_group_by(
    sequence: LazySequence[T],
    key_func: Callable[[T], U]
) -> Dict[U, List[T]]:
    """Group lazy sequence by key function"""

    groups = defaultdict(list)

    for item in sequence:
        key = key_func(item)
        groups[key].append(item)

    return dict(groups)


# === Usage ===

words = LazySequence(lambda: iter(["apple", "banana", "apricot", "cherry", "blueberry"]))

# Group by first letter
grouped = lazy_group_by(words, lambda w: w[0])
print(grouped)
# {
#     'a': ['apple', 'apricot'],
#     'b': ['banana', 'blueberry'],
#     'c': ['cherry']
# }
```

## Lazy Batch Processing

```python
def lazy_batch(sequence: LazySequence[T], batch_size: int) -> 'LazySequence[list[T]]':
    """Batch lazy sequence into chunks"""

    def batch_generator():
        batch = []
        for item in sequence:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    return LazySequence(batch_generator)


# === Usage ===

numbers = LazySequence(lambda: iter(range(100)))

# Process in batches of 10
for batch in lazy_batch(numbers, 10):
    print(f"Processing batch: {batch}")
    # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # [10, 11, 12, ...]
```

## DX Benefits

✅ **Memory efficient**: Only compute what's needed
✅ **Fast**: No upfront computation cost
✅ **Infinite**: Handle infinite sequences
✅ **Composable**: Chain operations together
✅ **Transparent**: Works like normal sequences

## Best Practices

```python
# ✅ Good: Use for large datasets
data = LazySequence(huge_file_lines).map(parse).filter(valid)

# ✅ Good: Materialize when needed
results = lazy_data.to_list()

# ✅ Good: Take what you need
first_10 = infinite_sequence.take(10)

# ❌ Bad: Materialize too early
# Don't call to_list() if you only need first 10 items
# ❌ Bad: Lazy when not needed
# For small lists, just use list comprehension
```
