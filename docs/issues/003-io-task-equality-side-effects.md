# Issue 003: IO.__eq__() and Task.__eq__() Execute Side Effects

**Severity:** Critical
**Status:** Open
**Location:**
- `better_py/monads/io.py:185-189`
- `better_py/monads/task.py:230-234`

**Priority:** P0 - Must Fix

## Description

The `__eq__` method in both `IO` and `Task` monads executes the wrapped computation when comparing instances. This is a serious violation of the principle that equality checks should be side-effect-free.

### Affected Classes

1. `IO` - `better_py/monads/io.py`
2. `Task` - `better_py/monads/task.py`

## Current Implementation

### IO.__eq__()

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, IO):
        return False
    return self._value() == other._value()  # Executes both IOs!
```

### Task.__eq__()

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Task):
        return False
    return self.run() == other.run()  # Runs both tasks!
```

## Impact

1. **Side Effects in Equality Check:** Comparing two IO/Task values executes them, which is completely unexpected
2. **Collection Corruption:** If IO/Task instances are stored in sets, dictionaries, or lists, equality checks during insertion/lookup will execute side effects
3. **Performance Issues:** Equality checks become expensive operations
4. **Semantic Violation:** Equality should be a pure, side-effect-free operation

## Example

```python
count = [0]

io1 = IO(lambda: (count.append(1), count[0])[-1])
io2 = IO(lambda: (count.append(1), count[0])[-1])

result = io1 == io2

# count is now 2!
# Both IOs were executed just to check equality
```

### Real-World Scenario

```python
# Storing IOs in a set
io_set = set()

database_write = IO(lambda: write_to_database())
io_set.add(database_write)  # Database write executed!

# Checking if IO is in set
if database_write in io_set:  # Database write executed again!
    pass
```

## Proposed Fix

### Option 1: Structural Equality (Recommended)

Compare IO/Task instances by their identity, not their execution result:

```python
# For IO
def __eq__(self, other: object) -> bool:
    if not isinstance(other, IO):
        return False
    return self is other  # Identity-based equality

def __hash__(self) -> int:
    return id(self)
```

```python
# For Task
def __eq__(self, other: object) -> bool:
    if not isinstance(other, Task):
        return False
    return self is other  # Identity-based equality

def __hash__(self) -> int:
    return id(self)
```

### Option 2: Remove Equality

Make IO and Task intentionally non-comparable:

```python
def __eq__(self, other: object) -> bool:
    return NotImplemented  # Never equal, even to itself
```

### Option 3: Lazy Equality with Caching

Cache the result and compare cached values:

```python
# For IO
@dataclass
class IO(Generic[T]):
    _value: Callable[[], T]
    _cached: T | None = field(init=False, default=None)
    _executed: bool = field(init=False, default=False)

    def _get_value(self) -> T:
        if not self._executed:
            object.__setattr__(self, "_cached", self._value())
            object.__setattr__(self, "_executed", True)
        return self._cached

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IO):
            return False
        return self._get_value() == other._get_value()
```

## Recommendation

**Use Option 1 (Identity-based equality)** as it:
1. Is the standard approach for IO monads in other languages (Haskell, Scala)
2. Avoids all side effects
3. Is simple and efficient
4. Makes the semantics clear: IO values are not comparable by their results

## Related Issues

- Issue #001: Validation.ap() doesn't accumulate errors
- Issue #002: State monad double execution bug

## Breaking Changes

This is a **breaking change** for users who rely on structural equality of IO/Task instances. However, the current behavior is incorrect and should be fixed.

## References

- Haskell's IO type: no Eq instance by default
- Scala's IO: uses reference equality
- ZIO: uses reference equality
