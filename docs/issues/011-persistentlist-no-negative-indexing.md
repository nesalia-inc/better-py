# Issue 011: PersistentList.get() Does Not Support Negative Indexing

**Severity:** Low
**Status:** Open
**Location:** `better_py/collections/persistent_list.py:187-209`
**Priority:** P3 - Low Priority

## Description

The `get` method in `PersistentList` rejects negative indices, breaking Python's standard indexing convention where negative indices count from the end of the sequence.

## Current Implementation

```python
def get(self, index: int) -> T | None:
    """Get element at index.

    Returns:
        The element at index, or None if out of bounds
    """
    if index < 0 or index >= self._length:  # Negative indices rejected
        return None
    # ...
```

## Python Convention

In Python, negative indices are standard:
```python
lst = [1, 2, 3, 4, 5]
lst[-1]  # 5 (last element)
lst[-2]  # 4 (second to last)
```

## Example

```python
lst = PersistentList.of(1, 2, 3, 4, 5)

# Current behavior:
lst.get(-1)  # None (rejected)

# Expected behavior (like Python lists):
lst.get(-1)  # Should return: 5
lst.get(-2)  # Should return: 4
```

## Impact

1. **Non-Pythonic:** Breaks user expectations from Python's standard indexing
2. **Inconsistent API:** Other operations may support negative indexing
3. **Minor Usability Issue:** Users must manually calculate positive indices

## Proposed Fix

```python
def get(self, index: int) -> T | None:
    """Get element at index.

    Supports negative indexing (counting from end of list).

    Args:
        index: The index to get. Negative values count from the end.

    Returns:
        The element at index, or None if out of bounds

    Example:
        >>> lst = PersistentList.of(1, 2, 3, 4, 5)
        >>> lst.get(0)   # 1
        >>> lst.get(-1)  # 5
        >>> lst.get(10)  # None
    """
    # Convert negative index to positive
    if index < 0:
        index = self._length + index

    if index < 0 or index >= self._length:
        return None

    current = self._node
    for _ in range(index):
        if current is None:
            return None
        current = current.tail

    return current.head if current else None
```

## Alternative: Follow Python's Error Convention

Instead of returning `None`, raise `IndexError` like Python lists:

```python
def __getitem__(self, index: int) -> T:
    """Get element at index (Python convention).

    Raises:
        IndexError: if index is out of bounds

    Example:
        >>> lst = PersistentList.of(1, 2, 3)
        >>> lst[0]   # 1
        >>> lst[-1]  # 3
        >>> lst[10]  # Raises IndexError
    """
    if index < 0:
        index = self._length + index

    if index < 0 or index >= self._length:
        raise IndexError("PersistentList index out of range")

    current = self._node
    for _ in range(index):
        if current is None:
            raise IndexError("PersistentList index out of range")
        current = current.tail

    if current is None:
        raise IndexError("PersistentList index out of range")

    return current.head
```

## Recommendation

1. **Add negative indexing support** to `get()` method
2. **Consider adding `__getitem__`** for bracket notation support
3. **Follow Python conventions** - raise `IndexError` in `__getitem__`, return `None` in `get()`

## Related Issues

- Issue #004: PersistentList performance issues
- Issue #005: PersistentList.drop() inefficiency

## References

- Python sequence types documentation
- PEP 8 programming recommendations
