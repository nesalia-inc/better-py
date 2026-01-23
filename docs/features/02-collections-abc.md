# Collections ABC - Native Protocols

Abstract Base Classes ensure your functional types behave like native Python collections.

## Overview

Instead of inheriting from concrete classes, use `collections.abc` to implement protocols. This makes your types compatible with:
- Built-in functions: `len()`, `reversed()`, `iter()`
- Type checking: `isinstance()`, `issubclass()`
- Static typing: Mypy, pyright
- Standard library: `list()`, `tuple()`, `in` operator

## Core ABCs for Functional Programming

### Sequence - Ordered Collections

```python
from collections.abc import Sequence
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')

class PersistentList(Sequence[T]):
    """Immutable persistent linked list"""

    __slots__ = ('_head', '_tail', '_length')

    def __init__(self, head: T | None = None, tail: 'PersistentList[T]' | None = None):
        self._head = head
        self._tail = tail or EmptyList()
        self._length = 1 + len(self._tail) if head is not None else 0

    # === Sequence protocol ===

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, index: int) -> T:
        if index < 0:
            index += self._length
        if index < 0 or index >= self._length:
            raise IndexError(index)
        return self._nth(index)

    def __contains__(self, item: object) -> bool:
        """'item' in list"""
        current: PersistentList[T] = self
        while current._head is not None:
            if current._head == item:
                return True
            current = current._tail
        return False

    def __iter__(self) -> Iterator[T]:
        current: PersistentList[T] = self
        while current._head is not None:
            yield current._head
            current = current._tail

    # === Additional methods ===

    def prepend(self, item: T) -> 'PersistentList[T]':
        return PersistentList(item, self)

    def append(self, item: T) -> 'PersistentList[T]':
        return PersistentList(self._head, self._tail.append(item)) if self._head else PersistentList(item)

    def map(self, f) -> 'PersistentList':
        ...

    def filter(self, predicate) -> 'PersistentList':
        ...


class EmptyList(PersistentList[T]):
    def __init__(self):
        super().__init__(None, None)

    def __len__(self) -> int:
        return 0

    def __getitem__(self, index: int) -> T:
        raise IndexError("Cannot index empty list")


# === Usage ===

lst = PersistentList(1).prepend(2).prepend(3)
print(len(lst))           # 3
print(lst[0])             # 3
print(2 in lst)           # True
for x in lst:             # 3, 2, 1
    print(x)

# Standard conversions
print(list(lst))          # [3, 2, 1]
print(tuple(lst))         # (3, 2, 1)
```

### Mapping - Dictionary-like Types

```python
from collections.abc import Mapping
from typing import TypeVar, Generic, Iterator

K = TypeVar('K')
V = TypeVar('V')

class PersistentMap(Mapping[K, V]):
    """Immutable persistent hash map"""

    __slots__ = ('_data',)

    def __init__(self, data: dict[K, V] | None = None):
        self._data = data or {}

    # === Mapping protocol ===

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    # === Additional methods ===

    def assoc(self, key: K, value: V) -> 'PersistentMap[K, V]':
        new_data = dict(self._data)
        new_data[key] = value
        return PersistentMap(new_data)

    def dissoc(self, key: K) -> 'PersistentMap[K, V]':
        new_data = dict(self._data)
        new_data.pop(key, None)
        return PersistentMap(new_data)

    def update_with(self, key: K, func: Callable[[V | None], V]) -> 'PersistentMap[K, V]':
        new_data = dict(self._data)
        new_data[key] = func(new_data.get(key))
        return PersistentMap(new_data)


# === Usage ===

m = PersistentMap({'a': 1, 'b': 2})
print(len(m))              # 2
print(m['a'])              # 1
print('c' in m)            # False

# Immutable updates
m2 = m.assoc('c', 3).assoc('a', 10)
print(m)                   # {'a': 1, 'b': 2}  (unchanged)
print(m2)                  # {'a': 10, 'b': 2, 'c': 3}

# Dict conversions
print(dict(m2))            # {'a': 10, 'b': 2, 'c': 3}
```

### Callable - Function-like Objects

```python
from collections.abc import Callable
from typing import TypeVar, Generic

T = TypeVar('T')
R = TypeVar('R')

class Compose(Generic[T, R], Callable):
    """Composable functions"""

    __slots__ = ('_funcs',)

    def __init__(self, *funcs: Callable):
        self._funcs = funcs

    def __call__(self, value: T) -> R:
        """Execute composition"""
        result = value
        for func in self._funcs:
            result = func(result)
        return result

    def __or__(self, other: Callable) -> 'Compose':
        """Compose: f | g = g ∘ f"""
        return Compose(*self._funcs, other)


# === Usage ===

add_one = lambda x: x + 1
double = lambda x: x * 2

pipeline = Compose(add_one, double)
print(pipeline(5))  # (5 + 1) * 2 = 12

# Callable protocol
print(callable(pipeline))  # True
from typing import Callable as TCallable
print(isinstance(pipeline, TCallable))  # True
```

### Iterable - Lazy Sequences

```python
from collections.abc import Iterable, Iterator
from typing import TypeVar, Generic

T = TypeVar('T')

class LazySequence(Iterable[T]):
    """Lazy infinite sequences"""

    __slots__ = ('_iterator_factory',)

    def __init__(self, factory: Callable[[], Iterator[T]]):
        self._iterator_factory = factory

    def __iter__(self) -> Iterator[T]:
        return self._iterator_factory()

    def map(self, f) -> 'LazySequence':
        def new_factory():
            return (f(x) for x in self._iterator_factory())
        return LazySequence(new_factory)

    def filter(self, predicate) -> 'LazySequence':
        def new_factory():
            return (x for x in self._iterator_factory() if predicate(x))
        return LazySequence(new_factory)

    def take(self, n: int) -> list:
        return list(self._take_generator(n))

    def _take_generator(self, n: int) -> Iterator[T]:
        it = self._iterator_factory()
        for _ in range(n):
            try:
                yield next(it)
            except StopIteration:
                break


# === Usage ===

def count_from(n: int):
    while True:
        yield n
        n += 1

numbers = LazySequence(count_from)
evens = numbers.filter(lambda x: x % 2 == 0).map(lambda x: x * 2)

print(evens.take(5))  # [0, 4, 8, 12, 16]
```

## Type Checking Integration

```python
from collections.abc import Sequence
from typing import TYPE_CHECKING

def process_list(lst: Sequence[int]) -> int:
    """Works with any Sequence, including custom ones"""
    return sum(lst)

# Our custom type is compatible
my_list = PersistentList(1).prepend(2).prepend(3)
print(process_list(my_list))  # 6

# Type checking understands the protocol
if TYPE_CHECKING:
    # Mypy knows PersistentList is a Sequence
    reveal_type(my_list)  # Revealed type: PersistentList[int]
```

## Full Protocol Checklist

| ABC | Required Methods | Common Methods | Use Case |
|-----|------------------|----------------|----------|
| `Sequence` | `__len__`, `__getitem__` | `__contains__`, `__iter__`, `__reversed__` | Ordered lists |
| `Mapping` | `__getitem__`, `__len__`, `__iter__` | `__contains__`, `get`, `keys`, `values`, `items` | Dicts |
| `Set` | `__len__`, `__iter__`, `__contains__` | `add`, `remove`, `union`, `intersection` | Unique values |
| `Callable` | `__call__` | - | Function objects |
| `Iterable` | `__iter__` | - | Lazy sequences |
| `Iterator` | `__iter__`, `__next__` | - | Custom iterators |

## DX Benefits

✅ **Standard compliance**: Works with all Python tools
✅ **Type safety**: Static checkers understand protocols
✅ **Interoperability**: Seamless integration with built-ins
✅ **Performance**: Protocol checks are fast
✅ **Documentation**: Self-documenting through ABC names

## Best Practices

```python
# ✅ Good: Protocol compliance
class MyList(Sequence):
    def __len__(self): ...
    def __getitem__(self, i): ...

# ❌ Bad: Direct inheritance from list
class MyList(list):  # Too heavyweight
    ...
```

Use ABCs as interfaces, not implementations. They document intent and enable duck typing while maintaining type safety.
