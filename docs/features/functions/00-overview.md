# Functions: Functional Programming Utilities

Utilities for working with functions - currying, partial application, composition, and higher-order functions.

## Overview

Unlike the [Core](../core/) folder which explains composition philosophy, this folder contains **concrete, ready-to-use function utilities**.

## Function Utilities

### [Currying](./01-currying.md)
Transform functions to take arguments one at a time.

```python
def add(a, b, c):
    return a + b + c

curried = curry(add)
curried(1)(2)(3)  # 6
```

### [Composition](./02-composition.md)
Combine functions to create new functions.

```python
# Compose functions
pipeline = compose(str, abs, neg)
pipeline(-5)  # "5"

# Pipe (reverse compose)
result = pipe(-5, neg, abs, str)  # "5"
```

### [Partial Application](./03-partial-application.md)
Fix some arguments of a function.

```python
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
square(5)  # 25
```

### [Pipe & Flow](./04-pipe-and-flow.md)
Flow data through function pipelines.

```python
result = pipe(
    data,
    validate,
    transform,
    save
)
```

### [Function Utilities](./05-function-utilities.md)
Miscellaneous function helpers.

```python
flip     # Reverse argument order
tap      # Call function, return value
identity  # Return input unchanged
always    # Return constant value
```

### [Higher-Order Functions](./06-higher-order-functions.md)
Functions that operate on functions.

```python
converge  # Call multiple functions, gather results
branch    # Route to different functions based on condition
trampoline  # Eliminate recursion stack overflow
```

## Comparison

| Utility | Use Case | Example |
|---------|----------|---------|
| `curry()` | Incremental arguments | `curried(1)(2)(3)` |
| `compose()` | Function composition | `compose(f, g, h)` |
| `partial()` | Fix arguments | `partial(f, 1)` |
| `pipe()` | Data pipeline | `pipe(x, f, g, h)` |
| `flip()` | Reverse arguments | `flip(subtract)` |
| `tap()` | Side effects in pipeline | `tap(print)` |
| `converge()` | Multiple results | `converge([sum, len])` |

## When to Use What

### Use curry() when:
- You want incremental argument application
- Creating reusable function templates
- Auto-partialing from left to right

### Use compose() when:
- Combining transformations
- Building function pipelines
- Right-to-left data flow

### Use pipe() when:
- Left-to-right data flow
- Multi-step transformations
- More readable than compose()

### Use partial() when:
- Fixing specific arguments
- Creating specialized versions
- Wrapping methods into functions

## Design Principles

All function utilities share these principles:

### ✅ Type-Safe

```python
# Generic types track transformations
def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    ...
```

### ✅ Lazy

```python
# curried functions return new functions
curried = curry(add)
add_1 = curried(1)  # Returns function
add_1(2)  # 3
```

### ✅ Composable

```python
# Combine utilities
pipeline = pipe(
    items,
    partial(map, str),
    partial(filter, lambda x: len(x) > 0),
    list
)
```

### ✅ Pure

```python
# No side effects (except tap, trace, etc.)
result = compose(f, g)(x)  # Pure
```

## Import Examples

```python
# Import specific utilities
from mfn.functions import (
    curry,
    compose,
    partial,
    pipe,
    flip,
    tap,
    identity
)

# Import all
from mfn.functions import *

# Import from submodules
from mfn.functions.curry import curry
from mfn.functions.compose import compose, pipe
```

## Performance Considerations

| Operation | Overhead | Notes |
|-----------|----------|-------|
| `curry()` | Low (wrapper) | Minimal overhead |
| `compose()` | Low | Creates closure |
| `partial()` | Low | Binds arguments |
| `pipe()` | Low | Sequential calls |
| `flip()` | Low | Argument swap |

## Related Documentation

- [Core: Composition](../core/05-composition.md) - Composition philosophy
- [Entities: Mappable](../entities/01-mappable.md) - Mappable protocol
- [Functions: Currying](./01-currying.md) - Currying details
- [Functions: Composition](./02-composition.md) - Composition patterns

## Summary

Function utilities provide:
- ✅ **Currying** - Incremental argument application
- ✅ **Composition** - Combine functions
- ✅ **Partial Application** - Fix arguments
- ✅ **Pipelines** - Data flow with `pipe()`
- ✅ **Higher-Order** - Functions for functions

**Key insight**: Write **functions that create functions** for maximum reusability and composability.

---

**Next**: See [Currying](./01-currying.md) for implementation details.
