# Issue 004: PersistentList.append() Has O(n) Performance Inefficient Implementation

## Description

The `append` method in `PersistentList` converts the entire linked list to a Python list, appends the item, then converts back to a `PersistentList`. This is highly inefficient, especially when called in a loop.

### Current Implementation

```python
def append(self, item: T) -> PersistentList[T]:
    """Add an item to the end of the list."""
    if self._node is None:
        return PersistentList(Node(item, None), 1)

    # Build new list in reverse then reverse back
    items = list(self)  # O(n) - converts entire list to Python list
    items.append(item)
    return PersistentList.from_iterable(items)  # O(n) - converts back
```

## Impact

1. **Performance:** Each `append` is O(n), making n appends O(n²)
2. **Memory Allocation:** Creates intermediate Python list for each append
3. **Defeats Purpose:** Persistent data structures should have efficient structural sharing

## Benchmark

```python
# Appending 100 items to a 1000-item list
lst = PersistentList.of(*range(1000))
for i in range(100):
    lst = lst.append(i)

# Takes ~0.09 seconds
# Should be near-instant with proper implementation
```

## Example of Problem

```python
# Naive usage pattern - O(n²)!
lst = PersistentList.empty()
for i in range(1000):
    lst = lst.append(i)  # Each append gets progressively slower
```

## Why This Happens

`PersistentList` is implemented as a singly-linked list with only `prepend` being O(1). True `append` in a linked list requires:
1. Traversing to the last node (O(n))
2. Creating a new path from head to tail (O(n))

The current implementation takes a shortcut by converting to a Python list.

## Proposed Solutions

### Option 1: Document and Recommend prepend()

Don't fix the implementation, but make it clear in documentation:

```python
def append(self, item: T) -> PersistentList[T]:
    """Add an item to the end of the list.

    Warning: This operation is O(n). Consider building lists
    using prepend() and then reverse() for better performance.

    Example:
        >>> # Bad: O(n²)
        >>> lst = PersistentList.empty()
        >>> for i in range(1000):
        ...     lst = lst.append(i)

        >>> # Good: O(n)
        >>> lst = PersistentList.empty()
        >>> for i in range(1000):
        ...     lst = lst.prepend(i)
        >>> lst = lst.reverse()
    """
```

### Option 2: Use Functional Queue (Chris Okasaki's)

Implement a persistent queue using two lists:
- Front list: items ready to be popped
- Rear list: items being built (in reverse)

This gives amortized O(1) for both prepend and append.

```python
@dataclass
class PersistentQueue(Generic[T]):
    _front: PersistentList[T]  # Normal order
    _rear: PersistentList[T]   # Reversed order

    def append(self, item: T) -> "PersistentQueue[T]":
        return PersistentQueue(self._front, self._rear.prepend(item))

    def to_list(self) -> PersistentList[T]:
        # When front is empty, reverse rear and make it front
        if self._front.is_empty():
            return self._rear.reverse()
        return self._front
```

### Option 3: Add Alternative Builder Methods

Add `append_all()` that builds efficiently:

```python
@staticmethod
def from_iterable(items: Iterable[T]) -> PersistentList[T]:
    """Create a list from an iterable - O(n)."""
    result = PersistentList()
    lst = list(items)
    for item in reversed(lst):
        result = result.prepend(item)
    return result

@staticmethod
def of_with_append(*items: T) -> PersistentList[T]:
    """Create a list using append instead of prepend - O(n²), use with caution."""
    result = PersistentList()
    for item in items:
        result = result.append(item)
    return result
```

## Recommendation

1. **Short term:** Add clear documentation warning about performance
2. **Long term:** Consider implementing `PersistentQueue` for O(1) append
3. **Add benchmark tests** to track performance

## Related Issues

- Issue #005: PersistentList.drop() is also inefficient
- Issue #006: PersistentList creates unnecessary intermediate lists

## References

- Chris Okasaki's "Purely Functional Data Structures"
- Functional queues: https://www.cs.cornell.edu/courses/cs3110/2019sp/lectures/20/pt.html
