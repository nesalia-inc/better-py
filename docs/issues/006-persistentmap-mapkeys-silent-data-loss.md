# Issue 006: PersistentMap.map_keys() Silently Loses Data on Key Collisions

## Description

The `map_keys` method in `PersistentMap` transforms keys using a function, but when the transformation produces duplicate keys, values are silently lost. There is no way to specify a collision resolution strategy.

### Current Implementation

```python
def map_keys(self, f: Callable[[K], U]) -> PersistentMap[U, V]:
    """Apply a function to all keys (values unchanged)."""
    new_data = {f(k): v for k, v in self._data.items()}
    return PersistentMap(new_data)
```

## Problem

When `f(k1) == f(k2)` for different keys `k1` and `k2`, the dictionary comprehension will overwrite the first value with the second, with no warning or error.

## Example

```python
m = PersistentMap.of({1: 'a', 2: 'b', 3: 'c'})
result = m.map_keys(lambda k: k // 2)

# Input:  {1: 'a', 2: 'b', 3: 'c'}
# f(1) = 0, f(2) = 1, f(3) = 1

# Result: {0: 'a', 1: 'c'}
# 'b' was silently lost! (key 2 mapped to 1, but key 3 also mapped to 1)
```

## Impact

1. **Data Loss:** Values can be lost without any indication
2. **Silent Failure:** No error or warning when collisions occur
3. **Unexpected Behavior:** Users expect map operations to preserve all data

## Proposed Solutions

### Option 1: Document the Behavior (Minimum)

Add clear documentation that data may be lost:

```python
def map_keys(self, f: Callable[[K], U]) -> PersistentMap[U, V]:
    """Apply a function to all keys (values unchanged).

    Warning: If the function produces duplicate keys, only the last
    value will be kept. Consider using map_keys_with() for custom
    collision resolution.
    """
    new_data = {f(k): v for k, v in self._data.items()}
    return PersistentMap(new_data)
```

### Option 2: Add Collision Resolution Parameter (Recommended)

Add a parameter to specify how to handle collisions:

```python
from typing import Callable, Literal

CollisionStrategy = Literal["first", "last", "error", "combine"]

def map_keys(
    self,
    f: Callable[[K], U],
    on_collision: CollisionStrategy = "last"
) -> PersistentMap[U, V]:
    """Apply a function to all keys with collision resolution.

    Args:
        f: Function to apply to keys
        on_collision: How to handle key collisions
            - "first": Keep first value encountered
            - "last": Keep last value encountered (default)
            - "error": Raise ValueError on collision
            - "combine": Keep all values as a list
    """
    if on_collision == "error":
        new_keys = [f(k) for k in self._data.keys()]
        if len(new_keys) != len(set(new_keys)):
            raise ValueError("Key collision detected in map_keys")

    if on_collision == "combine":
        new_data: dict[U, V | list[V]] = {}
        for k, v in self._data.items():
            new_key = f(k)
            if new_key in new_data:
                existing = new_data[new_key]
                if isinstance(existing, list):
                    existing.append(v)
                else:
                    new_data[new_key] = [existing, v]
            else:
                new_data[new_key] = v
        return PersistentMap(new_data)  # Type: ignore

    # Default: last wins (current behavior)
    new_data = {f(k): v for k, v in self._data.items()}
    return PersistentMap(new_data)
```

### Option 3: Return Validation

Return a Validation that accumulates errors:

```python
def map_keys_safe(
    self,
    f: Callable[[K], U]
) -> Validation[list[str], PersistentMap[U, V]]:
    """Apply a function to all keys, returning Validation for error handling."""
    errors = []
    seen_keys = set()
    new_data = {}

    for k, v in self._data.items():
        new_key = f(k)
        if new_key in seen_keys:
            errors.append(f"Key collision: {k} -> {new_key}")
        else:
            seen_keys.add(new_key)
            new_data[new_key] = v

    if errors:
        return Validation.invalid(errors)
    return Validation.valid(PersistentMap(new_data))
```

### Option 4: Add Alternative Method

Keep `map_keys` as-is (documented) and add a safer alternative:

```python
def map_keys(self, f: Callable[[K], U]) -> PersistentMap[U, V]:
    """Apply a function to all keys.

    Warning: May lose data on key collisions. Use map_keys_collect()
    to collect all values when collisions occur.
    """
    return PersistentMap({f(k): v for k, v in self._data.items()})

def map_keys_collect(
    self,
    f: Callable[[K], U]
) -> PersistentMap[U, list[V]]:
    """Apply a function to all keys, collecting values on collision."""
    new_data: dict[U, list[V]] = {}
    for k, v in self._data.items():
        new_key = f(k)
        if new_key not in new_data:
            new_data[new_key] = []
        new_data[new_key].append(v)
    return PersistentMap(new_data)
```

## Recommendation

1. **Short term:** Add clear warning documentation
2. **Medium term:** Add `map_keys_with()` with collision resolution parameter
3. **Add tests** that verify collision behavior

## Example Usage with Fix

```python
m = PersistentMap.of({1: 'a', 2: 'b', 3: 'c'})

# Option 1: Explicit collision handling
result = m.map_keys(lambda k: k // 2, on_collision="error")
# Raises: ValueError: Key collision detected

# Option 2: Collect all values
result = m.map_keys_collect(lambda k: k // 2)
# Result: {0: ['a'], 1: ['b', 'c']}
```

## Related Issues

- Issue #007: Missing applicative operations
- Issue #004: Performance issues in PersistentList

## References

- Python dict behavior with duplicate keys
- Clojure's update-with function
- Scala's Map.groupBy
