# Issue 002: State.map() and flat_map() Execute State Transformation Twice

## Description

The `map` and `flat_map` methods in the `State` monad call `self._run(s)` twice instead of once and storing the result. This causes the state transformation to be executed twice, which is a performance issue and can lead to incorrect behavior when the state computation has side effects.

### Affected Methods

1. `State.map()` at line 89-101
2. `State.flat_map()` at line 103-115

## Current Implementation

```python
def map(self, f: Callable[[A], B]) -> State[S, B]:
    return State(lambda s: (f(self._run(s)[0]), self._run(s)[1]))
    #                                 ^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^
    #                                 Called twice!      Called twice again!
```

```python
def flat_map(self, f: Callable[[A], State[S, B]]) -> State[S, B]:
    return State(lambda s: f(self._run(s)[0])._run(self._run(s)[1]))
    #                         ^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^
    #                         Called twice!      Called twice again!
```

## Impact

1. **Performance:** Every map/flat_map operation executes the state transformation twice, effectively doubling the computation time
2. **Side Effects:** If the state transformation has side effects (logging, counting, I/O), they will be executed twice
3. **Semantic Violation:** Violates the expected monad laws where each computation should run exactly once

## Example

```python
count = [0]

def counting_state(s):
    count[0] += 1
    return (s * 2, s + 1)

state = State(counting_state)
mapped = state.map(lambda x: x + 10)
result = mapped.run(5)

# count is 2 instead of 1!
# The state transformation was executed twice
```

## Proposed Fix

### For map():

```python
def map(self, f: Callable[[A], B]) -> State[S, B]:
    """Apply a function to the state value."""
    def new_run(s: S) -> tuple[B, S]:
        value, new_state = self._run(s)  # Call once and store
        return (f(value), new_state)
    return State(new_run)
```

### For flat_map():

```python
def flat_map(self, f: Callable[[A], State[S, B]]) -> State[S, B]:
    """Chain state computations."""
    def new_run(s: S) -> tuple[B, S]:
        value, new_state = self._run(s)  # Call once and store
        return f(value)._run(new_state)
    return State(new_run)
```

## Testing

The existing property-based tests should catch this, but they don't. Need to add:

```python
def test_map_executes_once(self):
    """map should execute the state transformation exactly once."""
    count = [0]

    def counting_state(s):
        count[0] += 1
        return (s, s)

    state = State(counting_state)
    mapped = state.map(lambda x: x)
    result = mapped.run(0)

    assert count[0] == 1, f"Expected 1 execution, got {count[0]}"
```

## Related Issues

- Issue #001: Validation.ap() doesn't accumulate errors
- Issue #003: IO/Task equality executes side effects

## References

- State monad laws
- Performance optimization patterns
