# Composition: Combining Functions

Combine functions to create new functions through composition, enabling reusable transformation pipelines.

## Overview

```python
from mfn.functions import compose, pipe

# Compose: Right to left
pipeline = compose(str, abs, neg)
pipeline(-5)  # "5"

# Pipe: Left to right
result = pipe(-5, neg, abs, str)  # "5"
```

## What is Composition?

**Function composition** combines functions so the output of one becomes the input of the next.

```python
# Compose: g(f(x))
def compose(f, g):
    return lambda x: g(f(x))

# Pipe: f → g → h
def pipe(value, *funcs):
    result = value
    for func in funcs:
        result = func(result)
    return result
```

## compose() - Right to Left

### Basic Usage

```python
from mfn.functions import compose

def increment(x):
    return x + 1

def double(x):
    return x * 2

# Compose functions
pipeline = compose(increment, double)
pipeline(5)  # 11 = increment(double(5))
# First: double(5) = 10
# Then: increment(10) = 11

# Multiple functions
pipeline = compose(str, abs, neg)
pipeline(-5)  # "5"
# neg(-5) = 5
# abs(5) = 5
# str(5) = "5"
```

### compose_many()

```python
from mfn.functions import compose_many

def f(x): return x * 2
def g(x): return x + 10
def h(x): return x - 5

# Compose multiple
pipeline = compose_many(h, g, f)
pipeline(5)  # 15 = h(g(f(5)))
# f(5) = 10
# g(10) = 20
# h(20) = 15
```

### compose_three() / compose_four()

```python
from mfn.functions import compose_three, compose_four

def add_1(x): return x + 1
def mul_2(x): return x * 2
def sub_3(x): return x - 3
def div_4(x): return x / 4

# Three functions
c3 = compose_three(sub_3, mul_2, add_1)
c3(10)  # 19 = sub_3(mul_2(add_1(10)))

# Four functions
c4 = compose_four(div_4, sub_3, mul_2, add_1)
c4(20)  # 10.25 = div_4(sub_3(mul_2(add_1(20))))
```

## pipe() - Left to Right

### Basic Usage

```python
from mfn.functions import pipe

def increment(x):
    return x + 1

def double(x):
    return x * 2

# Pipe data through functions
result = pipe(5, double, increment)
result  # 11 = increment(double(5))
# First: double(5) = 10
# Then: increment(10) = 11

# Multiple steps
result = pipe(
    -5,
    neg,      # 5
    abs,      # 5
    str,      # "5"
    upper     # "5" (uppercase)
)
```

### pipe_with()

```python
from mfn.functions import pipe_with

# With context
result = pipe_with(
    5,
    lambda x: x * 2,
    lambda x: x + 10,
    lambda x: x - 3
)
# 17 = ((5 * 2) + 10) - 3
```

## Advanced Composition

### compose_dict() - For dicts

```python
from mfn.functions import compose_dict

def extract_user(data):
    return data.get("user", {})

def get_name(user):
    return user.get("name", "")

# Compose dict operations
get_username = compose_dict(get_name, extract_user)
get_username({"user": {"name": "Alice"}})  # "Alice"
```

### async_compose() - Async functions

```python
from mfn.functions import async_compose

async def fetch_user(id):
    return await db.get_user(id)

async def get_profile(user):
    return await api.get_profile(user["id"])

async def get_emails(profile):
    return profile.get("emails", [])

# Compose async
pipeline = async_compose(get_emails, get_profile, fetch_user)
emails = await pipeline(123)  # ["alice@example.com"]
```

### flow() - Compose with methods

```python
from mfn.functions import flow

# Compose with method calls
pipeline = flow(
    "  hello  world  ",
    str.strip,      # "hello  world"
    str.upper,      # "HELLO  WORLD"
    lambda s: s.replace("  ", " "),  # "HELLO WORLD"
)
```

## Composition Laws

### Identity

```python
from mfn.functions import compose, identity

# Compose with identity does nothing
f = lambda x: x * 2

compose(f, identity)(5)  # 10
compose(identity, f)(5)  # 10
```

### Associativity

```python
from mfn.functions import compose

# (f ∘ g) ∘ h == f ∘ (g ∘ h)
f = lambda x: x * 2
g = lambda x: x + 10
h = lambda x: x - 5

left = compose(compose(h, g), f)
right = compose(h, compose(g, f))

left(5)  # 15
right(5)  # 15
```

## Practical Examples

### Data Processing Pipeline

```python
from mfn.functions import pipe, compose

# Compose transformations
process = compose(
    lambda s: s.split(","),
    lambda parts: [int(p.strip()) for p in parts],
    lambda nums: sum(nums) / len(nums)
)

result = process("1, 2, 3, 4, 5")  # 3.0

# Same with pipe
result = pipe(
    "1, 2, 3, 4, 5",
    lambda s: s.split(","),
    lambda parts: [int(p.strip()) for p in parts],
    lambda nums: sum(nums) / len(nums)
)
```

### Validation Chain

```python
from mfn.functions import compose

def is_present(value):
    return value is not None and value != ""

def is_email(value):
    return "@" in value

def is_valid_domain(value):
    return "." in value.split("@")[1]

# Compose validations
is_valid_email = compose(
    lambda checks: all(checks),
    lambda v: [is_present(v), is_email(v), is_valid_domain(v)]
)

is_valid_email("user@example.com")  # True
is_valid_email("invalid")  # False
```

### String Processing

```python
from mfn.functions import compose

# Build text processor
process = compose(
    lambda s: s.strip(),
    str.upper,
    lambda s: s.replace(" ", "_")
)

process("  hello world  ")  # "HELLO_WORLD"
```

### Number Processing

```python
from mfn.functions import compose

# Build calculator
calculate = compose(
    lambda x: x / 100,  # Percentage
    lambda x: x + 10,   # Add 10
    lambda x: x * 2      # Double
)

calculate(50)  # 2.0 = ((50 * 2) + 10) / 100
```

## pipe Operators

### Custom pipe operator

```python
from mfn.functions import pipe

# Using | operator (if defined)
result = (
    5
    | (lambda x: x * 2)
    | (lambda x: x + 10)
    | (lambda x: x - 3)
)
# 17

# Equivalent to pipe()
result = pipe(
    5,
    lambda x: x * 2,
    lambda x: x + 10,
    lambda x: x - 3
)
```

## Type Safety

```python
from typing import Callable, TypeVar

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """Compose with type hints"""
    return lambda x: g(f(x))

# Type inference works
def increment(x: int) -> int: return x + 1
def double(x: int) -> int: return x * 2

pipeline: Callable[[int], int] = compose(increment, double)
```

## Comparison: compose vs pipe

```python
from mfn.functions import compose, pipe

# compose: Right to left, functions only
pipeline = compose(str, abs, neg)
result = pipeline(-5)

# pipe: Left to right, value then functions
result = pipe(-5, neg, abs, str)

# When to use which:
# - compose: Creating reusable pipelines
# - pipe: Processing data (left-to-right reads better)
```

## Performance

Composition has minimal overhead:

```python
# Direct call
result = f(g(h(x)))  # ~0.3µs

# Composed
pipeline = compose(f, g, h)
result = pipeline(x)  # ~0.35µs (slight overhead)
```

## Best Practices

### ✅ Do: Compose pure functions

```python
# Good: Pure transformations
pipeline = compose(str, abs, lambda x: x + 1)
```

### ✅ Do: Use pipe for data flow

```python
# Good: Left-to-right reads naturally
result = pipe(data, validate, transform, save)
```

### ✅ Do: Name composed functions

```python
# Good: Self-documenting
get_username = compose_dict(get_name, extract_user)
```

### ❌ Don't: Compose too many functions

```python
# Hard to read
pipeline = compose(a, b, c, d, e, f, g, h, i, j)

# Better: Break into named parts
step1 = compose(d, c, b, a)
step2 = compose(h, g, f, e)
pipeline = compose(step2, step1)
```

## See Also

- [Currying](./01-currying.md) - Incremental arguments
- [Partial Application](./03-partial-application.md) - Fix arguments
- [Pipe & Flow](./04-pipe-and-flow.md) - Pipeline patterns
- [Core: Composition](../core/05-composition.md) - Composition philosophy

---

**Next**: [Partial Application](./03-partial-application.md)
