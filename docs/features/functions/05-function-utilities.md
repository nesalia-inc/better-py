# Function Utilities: Helper Functions

Miscellaneous helper functions for working with functions - flip, tap, identity, memoize, and more.

## Overview

| Utility | Purpose | Example |
|---------|---------|---------|
| `identity` | Return input unchanged | `identity(5)` → `5` |
| `always` | Return constant value | `always(42)(x)` → `42` |
| `flip` | Reverse argument order | `flip(subtract)(5, 3)` → `3 - 5` |
| `tap` | Call function, return value | `tap(print)(value)` |
| `trace` | Debug function calls | `trace("f")(x)` |
| `noop` | Do nothing | `noop(x)` → `x` |

## identity()

```python
from mfn.functions import identity

identity(5)  # 5
identity("hello")  # "hello"

# Use case: Default function
def get_or_default(maybe, default_func=identity):
    return maybe.unwrap_or_else(default_func)
```

## always()

```python
from mfn.functions import always

return_42 = always(42)
return_42(1)  # 42
return_42("anything")  # 42

# Use case: Default callback
def fetch_with_callback(url, callback=always(None)):
    result = fetch(url)
    callback(result)
    return result
```

## flip()

```python
from mfn.functions import flip

def subtract(a, b):
    return a - b

# Normal: a - b
subtract(5, 3)  # 2

# Flipped: b - a
sub_backwards = flip(subtract)
sub_backwards(5, 3)  # -2 = 3 - 5

# Use case: Different argument order
def divide(a, b):
    return a / b

div_by_2 = flip(divide, 2)
div_by_2(8)  # 4 = 8 / 2
```

### flip_with()

```python
from mfn.functions import flip_with

def process(data, options, config):
    ...

# Flip first two arguments
alt_process = flip_with(process, 0, 1)  # Flip data, options
alt_process(options, data, config)
```

## tap()

```python
from mfn.functions import tap

def log(data):
    print(f"Processing: {data}")
    return data

# Tap: Call function but return original value
result = tap([1, 2, 3], log)
# Prints: Processing: [1, 2, 3]
# Returns: [1, 2, 3]

# In pipeline
from mfn.functions import pipe

result = pipe(
    data,
    tap(validate),     # Validate but pass through
    transform,
    tap(save),        # Save but pass through
    format
)
```

## trace()

```python
from mfn.functions import trace

# Trace function calls
traced_add = trace("add")(lambda a, b: a + b)

result = traced_add(5, 3)
# Logs: add(5, 3) = 8
# Returns: 8

# With custom formatter
traced_multiply = trace(
    "multiply",
    formatter=lambda a, b, r: f"{a} * {b} = {r}"
)

result = traced_multiply(3, 4)
# Logs: multiply(3, 4) = 12
```

## noop()

```python
from mfn.functions import noop

# No-op function
noop(5)  # 5
noop("anything")  # "anything"

# Use case: Optional callback
def process(data, callback=noop):
    result = compute(data)
    callback(result)  # No-op by default
    return result
```

## Type Coercion

```python
from mfn.functions import as_int, as_float, as_str

as_int("42")    # 42
as_int(3.14)    # 3

as_float("3.14")  # 3.14
as_float(42)     # 42.0

as_str(42)       # "42"
as_str(3.14)     # "3.14"

# Use case: Safe type conversion
def process(value):
    return pipe(
        value,
        as_str,
        lambda s: s.strip(),
        as_int
    )
```

## Comparison Functions

```python
from mfn.functions import eq, ne, gt, lt, ge, le

# Equality
eq(5)(5)   # True
eq(5)(3)   # False

# Comparison
gt(5)(3)   # True (5 > 3)
lt(5)(3)   # False (5 < 3)

# Use case: Filter
numbers = [1, 2, 3, 4, 5]
filtered = filter(gt(3), numbers)  # [4, 5]
```

## Logical Operators

```python
from mfn.functions import complement, both, either

# Complement (not)
is_even = lambda x: x % 2 == 0
is_odd = complement(is_even)

is_odd(2)  # False
is_odd(3)  # True

# Both (and)
both(is_positive, is_even)(4)  # True
both(is_positive, is_even)(3)  # False

# Either (or)
either(is_even, is_multiple_of_3)(6)  # True
```

## Predicate Builders

```python
from mfn.functions import prop_eq, prop_gt, prop_lt

# Property equality
has_name = prop_eq("name")
has_name({"name": "Alice"})  # True
has_name({"name": "Bob"})   # False

# Property comparison
is_adult = prop_gt("age", 18)
is_adult({"age": 25})     # True
is_adult({"age": 15})     # False

# Use case: Filter objects
users = [{"age": 20}, {"age": 15}]
adults = filter(is_adult, users)  # [{"age": 20}]
```

## Memoization

```python
from mfn.functions import memoize, memoize_async

# Memoize (cache)
@memoize
def expensive_fib(n):
    if n <= 1:
        return n
    return expensive_fib(n-1) + expensive_fib(n-2)

expensive_fib(100)  # Fast (cached)
expensive_fib(100)  # From cache

# Async memoize
@memoize_async
async def fetch_user(id):
    return await db.query_user(id)

await fetch_user(1)  # Fetch
await fetch_user(1)  # From cache
```

## Argument Utilities

```python
from mfn.functions import reverse_args, spread_args

# Reverse arguments
def subtract(a, b):
    return a - b

sub_backwards = reverse_args(subtract)
sub_backwards(5, 3)  # -2 = 3 - 5

# Spread dict into args
def func(a, b, c):
    return a + b + c

spread = spread_args(func)
spread({"a": 1, "b": 2, "c": 3})  # 6
```

## Function Guards

```python
from mfn.functions import guard, guard_type

# Guard with condition
@guard(lambda x: x > 0)
def sqrt(x):
    return x ** 0.5

sqrt(9)   # 3.0
sqrt(-1)  # ValueError

# Guard with type
@guard_type(int)
def process_number(x):
    return x * 2

process_number(5)   # 10
process_number("5")  # TypeError
```

## Function Adapters

```python
from mfn.functions import adapt, retry, timeout

# Adapt output
@adapt(list)
def get_items():
    return yield_items()

get_items()  # Returns list

# Retry wrapper
@retry(max_attempts=3, backoff=exponential)
def fetch_api(url):
    return requests.get(url)

# Timeout wrapper
@timeout(seconds=5)
def long_operation():
    time.sleep(10)
```

## Implementation

### identity

```python
def identity(x):
    """Return input unchanged"""
    return x
```

### always

```python
def always(value):
    """Return function that always returns value"""
    def inner(*args, **kwargs):
        return value
    return inner
```

### flip

```python
def flip(func):
    """Reverse first two arguments"""
    def flipped(a, b):
        return func(b, a)
    return flipped
```

### tap

```python
def tap(func):
    """Call func with value, return value"""
    def inner(value):
        func(value)
        return value
    return inner
```

## Best Practices

### ✅ Do: Use tap for side effects

```python
# Good: Logging in pipeline
pipe(data, tap(log), transform)
```

### ✅ Do: Use flip for compatibility

```python
# Good: Adapt argument order
div_by = flip(divide, 2)
```

### ✅ Do: Use identity as default

```python
# Good: Default transformation
transform(data, func=identity)
```

### ❌ Don't: Over-engineer

```python
# Bad: Complex when simple works
always_return_identity(always(identity(x)))

# Good: Just use x
```

## See Also

- [Composition](./02-composition.md) - Function composition
- [Currying](./01-currying.md) - Incremental arguments
- [Higher-Order Functions](./06-higher-order-functions.md) - Functions for functions

---

**Next**: [Higher-Order Functions](./06-higher-order-functions.md)
