# Immutable Collections - Safe Data Structures

Immutable collections with structural sharing for efficient updates.

## Overview

Immutable collections enable:
- Safe data sharing
- Predictable code
- Efficient updates
- Structural sharing
- Thread safety

## Immutable List

```python
from typing import Iterator, TypeVar, Generic, Callable

T = TypeVar('T')

class ImmutableList:
    """Immutable persistent list"""

    __slots__ = ('_head', '_tail', '_length')

    def __init__(self, head: T | None = None, tail: 'ImmutableList | None' = None):
        self._head = head
        self._tail = tail or _EmptyList()
        self._length = 1 + len(self._tail) if head is not None else 0

    @classmethod
    def empty(cls) -> 'ImmutableList':
        return _EmptyList()

    @classmethod
    def of(cls, *items: T) -> 'ImmutableList':
        """Create list from items"""

        result = cls.empty()
        for item in reversed(items):
            result = cls(item, result)
        return result

    def prepend(self, item: T) -> 'ImmutableList':
        """Add item to front - O(1)"""
        return ImmutableList(item, self)

    def append(self, item: T) -> 'ImmutableList':
        """Add item to end - O(n)"""
        return ImmutableList.of(*list(self) + [item])

    def update(self, index: int, value: T) -> 'ImmutableList':
        """Update item at index"""

        if index == 0:
            return ImmutableList(value, self._tail)

        return ImmutableList(self._head, self._tail.update(index - 1, value))

    def remove(self, index: int) -> 'ImmutableList':
        """Remove item at index"""

        if index == 0:
            return self._tail

        return ImmutableList(self._head, self._tail.remove(index - 1))

    def map(self, func: Callable[[T], U]) -> 'ImmutableList':
        """Map over all items"""

        if self._head is None:
            return self

        return ImmutableList(
            func(self._head),
            self._tail.map(func) if self._tail else _EmptyList()
        )

    def filter(self, predicate: Callable[[T], bool]) -> 'ImmutableList':
        """Filter items"""

        if self._head is None:
            return self

        rest = self._tail.filter(predicate) if self._tail else _EmptyList()

        if predicate(self._head):
            return ImmutableList(self._head, rest)
        return rest

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> Iterator[T]:
        current = self
        while current._head is not None:
            yield current._head
            current = current._tail

    def __getitem__(self, index: int) -> T:
        if index < 0:
            index += self._length

        if index < 0 or index >= self._length:
            raise IndexError(index)

        if index == 0:
            return self._head

        return self._tail[index - 1]

    def __repr__(self) -> str:
        return f"ImmutableList({list(self)})"


class _EmptyList(ImmutableList):
    """Empty list singleton"""

    __slots__ = ()

    def __init__(self):
        super().__init__(None, None)

    def __len__(self) -> int:
        return 0

    def __iter__(self):
        return
        yield

    def __repr__(self):
        return "ImmutableList()"


# === Usage ===

lst = ImmutableList.of(1, 2, 3)
print(lst)  # ImmutableList([1, 2, 3])

# Prepend - O(1)
lst2 = lst.prepend(0)
print(lst)   # ImmutableList([1, 2, 3]) - unchanged
print(lst2)  # ImmutableList([0, 1, 2, 3])

# Append - O(n)
lst3 = lst.append(4)
print(lst3)  # ImmutableList([1, 2, 3, 4])

# Update
lst4 = lst.update(1, 20)
print(lst4)  # ImmutableList([1, 20, 3])

# Map
lst5 = lst.map(lambda x: x * 2)
print(lst5)  # ImmutableList([2, 4, 6])

# Filter
lst6 = lst.filter(lambda x: x > 1)
print(lst6)  # ImmutableList([2, 3])
```

## Immutable Dictionary

```python
from typing import Mapping, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')

class ImmutableDict(Mapping[K, V]):
    """Immutable dictionary with structural sharing"""

    __slots__ = ('_data', '_hash')

    def __init__(self, data: dict[K, V] | None = None):
        self._data = data or {}

    @classmethod
    def empty(cls) -> 'ImmutableDict':
        return cls()

    @classmethod
    def of(cls, **kwargs: V) -> 'ImmutableDict':
        return cls(kwargs)

    def assoc(self, key: K, value: V) -> 'ImmutableDict':
        """Add or update key - O(1)"""

        new_data = dict(self._data)
        new_data[key] = value
        return ImmutableDict(new_data)

    def dissoc(self, key: K) -> 'ImmutableDict':
        """Remove key - O(1)"""

        if key not in self._data:
            return self

        new_data = dict(self._data)
        del new_data[key]
        return ImmutableDict(new_data)

    def update(self, *others: 'ImmutableDict') -> 'ImmutableDict':
        """Merge with other dicts"""

        new_data = dict(self._data)

        for other in others:
            new_data.update(other._data)

        return ImmutableDict(new_data)

    def map(self, func: Callable[[V], V]) -> 'ImmutableDict':
        """Map over values"""

        new_data = {k: func(v) for k, v in self._data.items()}
        return ImmutableDict(new_data)

    def map_keys(self, func: Callable[[K], K]) -> 'ImmutableDict':
        """Map over keys"""

        new_data = {func(k): v for k, v in self._data.items()}
        return ImmutableDict(new_data)

    # Mapping protocol
    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return f"ImmutableDict({self._data})"


# === Usage ===

d = ImmutableDict.of(a=1, b=2, c=3)
print(d)  # ImmutableDict({'a': 1, 'b': 2, 'c': 3})

# Assoc
d2 = d.assoc('d', 4)
print(d)   # ImmutableDict({'a': 1, 'b': 2, 'c': 3}) - unchanged
print(d2)  # ImmutableDict({'a': 1, 'b': 2, 'c': 3, 'd': 4})

# Dissoc
d3 = d.dissoc('b')
print(d3)  # ImmutableDict({'a': 1, 'c': 3})

# Update
d4 = d.update(ImmutableDict.of(d=4, e=5))
print(d4)  # ImmutableDict({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})

# Map values
d5 = d.map(lambda v: v * 2)
print(d5)  # ImmutableDict({'a': 2, 'b': 4, 'c': 6})
```

## Immutable Set

```python
from typing import AbstractSet, TypeVar, Generic

T = TypeVar('T')

class ImmutableSet(AbstractSet[T]):
    """Immutable set"""

    __slots__ = ('_data',)

    def __init__(self, items: set[T] | None = None):
        self._data = items or set()

    @classmethod
    def empty(cls) -> 'ImmutableSet':
        return cls()

    @classmethod
    def of(cls, *items: T) -> 'ImmutableSet':
        return cls(set(items))

    def add(self, item: T) -> 'ImmutableSet':
        """Add item"""

        new_data = set(self._data)
        new_data.add(item)
        return ImmutableSet(new_data)

    def remove(self, item: T) -> 'ImmutableSet':
        """Remove item"""

        if item not in self._data:
            return self

        new_data = set(self._data)
        new_data.remove(item)
        return ImmutableSet(new_data)

    def union(self, other: 'ImmutableSet') -> 'ImmutableSet':
        """Union with another set"""

        return ImmutableSet(self._data | other._data)

    def intersection(self, other: 'ImmutableSet') -> 'ImmutableSet':
        """Intersection with another set"""

        return ImmutableSet(self._data & other._data)

    def difference(self, other: 'ImmutableSet') -> 'ImmutableSet':
        """Difference with another set"""

        return ImmutableSet(self._data - other._data)

    # AbstractSet protocol
    def __contains__(self, item: T) -> bool:
        return item in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return f"ImmutableSet({self._data})"


# === Usage ===

s = ImmutableSet.of(1, 2, 3)
print(s)  # ImmutableSet({1, 2, 3})

# Add
s2 = s.add(4)
print(s2)  # ImmutableSet({1, 2, 3, 4})

# Remove
s3 = s.remove(2)
print(s3)  # ImmutableSet({1, 3})

# Union
s4 = s.union(ImmutableSet.of(3, 4, 5))
print(s4)  # ImmutableSet({1, 2, 3, 4, 5})

# Intersection
s5 = s.intersection(ImmutableSet.of(2, 3, 4))
print(s5)  # ImmutableSet({2, 3})
```

## Immutable Stack

```python
class ImmutableStack(Generic[T]):
    """Immutable stack (LIFO)"""

    __slots__ = ('_items',)

    def __init__(self, items: tuple[T, ...] = ()):
        self._items = items

    @classmethod
    def empty(cls) -> 'ImmutableStack':
        return cls()

    def push(self, item: T) -> 'ImmutableStack':
        """Push item onto stack"""

        return ImmutableStack((item, *self._items))

    def pop(self) -> tuple[T, 'ImmutableStack']:
        """Pop item from stack"""

        if not self._items:
            raise IndexError("Cannot pop from empty stack")

        return self._items[0], ImmutableStack(self._items[1:])

    def peek(self) -> T:
        """Peek at top item"""

        if not self._items:
            raise IndexError("Stack is empty")

        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return f"ImmutableStack({list(self._items)})"


# === Usage ===

stack = ImmutableStack.empty()
stack = stack.push(1).push(2).push(3)
print(stack)  # ImmutableStack([3, 2, 1])

print(stack.peek())  # 3

top, rest = stack.pop()
print(top)   # 3
print(rest)  # ImmutableStack([2, 1])
```

## Immutable Queue

```python
class ImmutableQueue(Generic[T]):
    """Immutable queue (FIFO)"""

    __slots__ = ('_front', '_back')

    def __init__(self, front: tuple = (), back: tuple = ()):
        self._front = front
        self._back = back

    @classmethod
    def empty(cls) -> 'ImmutableQueue':
        return cls()

    def enqueue(self, item: T) -> 'ImmutableQueue':
        """Add to back"""

        # If front is empty, move back to front
        if not self._front:
            return ImmutableQueue((item,), ())

        return ImmutableQueue(self._front, (item, *self._back))

    def dequeue(self) -> tuple[T, 'ImmutableQueue']:
        """Remove from front"""

        if not self._front and not self._back:
            raise IndexError("Cannot dequeue from empty queue")

        # If front is empty, reverse back
        if not self._front:
            return ImmutableQueue(self._back[::-1], ()).dequeue()

        item = self._front[0]

        # Move back to front if needed
        if len(self._front) == 1:
            return item, ImmutableQueue(self._back[::-1], ())

        return item, ImmutableQueue(self._front[1:], self._back)

    def peek(self) -> T:

        if not self._front and not self._back:
            raise IndexError("Queue is empty")

        if not self._front:
            return self._back[-1]

        return self._front[0]

    def is_empty(self) -> bool:
        return len(self._front) == 0 and len(self._back) == 0

    def __len__(self) -> int:
        return len(self._front) + len(self._back)

    def __repr__(self) -> str:
        items = list(self._front) + list(self._back[::-1])
        return f"ImmutableQueue({items})"


# === Usage ===

q = ImmutableQueue.empty()
q = q.enqueue(1).enqueue(2).enqueue(3)
print(q)  # ImmutableQueue([1, 2, 3])

print(q.peek())  # 1

item, rest = q.dequeue()
print(item)  # 1
print(rest)  # ImmutableQueue([2, 3])
```

## DX Benefits

✅ **Safe**: No accidental mutations
✅ **Predictable**: Data doesn't change
✅ **Efficient**: Structural sharing
✅ **Thread-safe**: Share between threads
✅ **Pythonic**: Implements standard protocols

## Best Practices

```python
# ✅ Good: Use for shared data
shared_config = ImmutableDict.of(api_key="...", timeout=30)

# ✅ Good: Return new instances
def add_item(lst: ImmutableList, item):
    return lst.append(item)

# ✅ Good: Chain operations
result = lst.map(f).filter(p).map(g)

# ❌ Bad: Mutating after creation
# Don't try to modify in place
```
