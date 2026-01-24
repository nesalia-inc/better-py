# Issue 005: PersistentList.drop() Creates Unnecessary Intermediate Lists

## Description

The `drop` method in `PersistentList` traverses the linked list to find the starting point, then builds a Python list, then converts it back to a `PersistentList` by reversing and prepending. This is inefficient for a linked list.

### Current Implementation

```python
def drop(self, n: int) -> PersistentList[T]:
    """Drop the first n elements."""
    if n <= 0:
        return self

    current = self._node
    for _ in range(n):
        if current is None:
            return PersistentList()
        current = current.tail

    # Build new list from current node
    result: PersistentList[T] = PersistentList()
    items = []  # Creates intermediate Python list
    while current is not None:
        items.append(current.head)  # O(n) to build list
        current = current.tail

    for item in reversed(items):  # O(n) to reverse
        result = result.prepend(item)

    return result
```

## Impact

1. **Performance:** O(n) time and O(n) extra space for what should be O(1) for linked lists
2. **Memory Allocation:** Creates intermediate Python list
3. **Unnecessary Complexity:** For linked lists, drop should just return the remaining nodes

## Why This Is Inefficient

For a linked list, dropping the first n elements is trivial:
```python
# Just return the node at position n
def drop(self, n: int) -> PersistentList[T]:
    current = self._node
    for _ in range(n):
        if current is None:
            return PersistentList()
        current = current.tail
    return PersistentList(current, self._length - n)
```

However, we need to recalculate the length, which requires traversing to count the remaining nodes.

## Proposed Fix

```python
def drop(self, n: int) -> PersistentList[T]:
    """Drop the first n elements.

    Returns:
        A new list without the first n elements

    Complexity: O(n) time, O(1) extra space
    """
    if n <= 0:
        return self

    if n >= self._length:
        return PersistentList()

    # Traverse to the nth node
    current = self._node
    for _ in range(n):
        if current is None:
            return PersistentList()
        current = current.tail

    # Recalculate length by counting remaining nodes
    remaining_length = 0
    temp = current
    while temp is not None:
        remaining_length += 1
        temp = temp.tail

    return PersistentList(current, remaining_length)
```

## Even Better: Store Length in Nodes

If each node stored its cumulative length, we could make this O(1):

```python
@dataclass(frozen=True, slots=True)
class Node(Generic[T]):
    head: T
    tail: Node[T] | None
    length: int  # Cumulative length from this node
```

Then drop becomes:
```python
def drop(self, n: int) -> PersistentList[T]:
    if n <= 0:
        return self
    if n >= self._length:
        return PersistentList()

    current = self._node
    for _ in range(n):
        current = current.tail

    return PersistentList(current, current.length if current else 0)
```

## Benchmark

```python
# Dropping 5 elements from a 1000-element list
lst = PersistentList.of(*range(1000))

# Current implementation: Creates list of 995 elements, then reverses
# Fixed implementation: Just returns the node at position 5
```

## Recommendation

1. **Short term:** Implement the O(n) traversal without intermediate list
2. **Long term:** Consider storing length in nodes for O(1) drop
3. **Document complexity** in docstrings

## Related Issues

- Issue #004: PersistentList.append() is inefficient
- Issue #006: PersistentList creates unnecessary intermediate lists

## References

- Linked list operations
- Persistent data structures with path copying
