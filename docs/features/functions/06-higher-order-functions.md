# Higher-Order Functions: Functions Operating on Functions

Functions that take functions as input or return functions as output - the essence of functional programming.

## Overview

| Function | Purpose | Example |
|----------|---------|---------|
| `converge` | Call multiple functions | `converge([sum, len])` |
| `branch` | Route based on condition | `branch(pred, f, g)` |
| `trampoline` | Eliminate recursion | `trampoline(fact)` |
| `y-combinator` | Call self recursively | `y(recurse)` |
| `lift` | Lift function to monad | `lift(Result)(f)` |
| `compose_async` | Compose async | `compose_async(f, g)` |

## converge() - Multiple Results

### Basic Usage

```python
from mfn.functions import converge

def stats(data):
    total = sum(data)
    count = len(data)
    avg = total / count
    return {"total": total, "count": count, "avg": avg}

# Converge: Call multiple functions, gather results
stats_func = converge([sum, len, lambda d: sum(d) / len(d)])

stats_func([1, 2, 3, 4, 5])
# [15, 5, 3.0]
```

### Converge with Transform

```python
from mfn.functions import converge

def transform_results(results):
    keys = ["sum", "count", "avg"]
    return dict(zip(keys, results))

stats = converge(
    [sum, len, lambda d: sum(d) / len(d)],
    transform=transform_results
)

stats([1, 2, 3, 4, 5])
# {"sum": 15, "count": 5, "avg": 3.0}
```

## branch() - Conditional Routing

```python
from mfn.functions import branch

# Branch based on condition
process = branch(
    lambda x: x > 0,
    lambda x: x * 2,    # If true
    lambda x: x * 3     # If false
)

process(5)   # 10 = 5 * 2
process(-5)  # -15 = -5 * 3
```

### Multi-way Branch

```python
from mfn.functions import branch_multi

# Route to different functions
router = branch_multi(
    lambda x: x["type"],
    {
        "user": process_user,
        "admin": process_admin,
        "guest": process_guest
    }
)

router({"type": "user", "data": ...})
```

## trampoline() - Recursion Elimination

```python
from mfn.functions import trampoline

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Trampolined version
def factorial_t(n):
    def fact(n, acc=1):
        if n <= 1:
            return acc
        return lambda: fact(n - 1, acc * n)
    return trampoline(fact(n))

factorial_t(10000)  # No stack overflow!
```

## Y Combinator

```python
from mfn.functions import y_combinator

# Y combinator for recursion
fact = y_combinator(lambda recur: lambda n: 1 if n <= 1 else n * recur(n - 1))

fact(5)  # 120
```

## lift() - Lift to Monad

```python
from mfn.functions import lift

def safe_divide(a, b):
    return a / b  # May raise ZeroDivisionError

# Lift to Result
safe_divide_result = lift(Result)(safe_divide)
safe_divide_result(10, 2)  # Ok(5)
safe_divide_result(10, 0)  # Error(ZeroDivisionError)

# Lift to Maybe
safe_divide_maybe = lift(Maybe)(safe_divide)
```

## unlift() - Remove Monad

```python
from mfn.functions import unlift

# Remove Result wrapper
def divide(a, b):
    return Ok(a / b)

# Unlift: May raise exception
divide_unsafe = unlift(divide)
divide_unsafe(10, 2)  # 5.0
divide_unsafe(10, 0)  # ZeroDivisionError
```

## async_lift() - Async Monad

```python
from mfn.functions import async_lift

async def fetch_user(id):
    return await db.get_user(id)

# Lift to AsyncResult
fetch_user_async_result = async_lift(AsyncResult)(fetch_user)
```

## Function Builders

### builder()

```python
from mfn.functions import func_builder

def create_api(base_url):
    @func_builder
    def api(endpoint):
        return requests.get(f"{base_url}/{endpoint}")
    return api

api = create_api("https://api.example.com")
api("/users")  # GET https://api.example.com/users
```

### chain()

```python
from mfn.functions import chain

# Chain multiple functions
def f(x):
    return x + 1

def g(x):
    return x * 2

def h(x):
    return x - 5

chained = chain(f, g, h)
chained(5)  # 7 = ((((5 + 1) * 2) - 5)
```

### around()

```python
from mfn.functions import around

# Wrap function with before/after
@around(logging, validate)
def process(data):
    return transform(data)

# Equivalent to:
# def process_with_logging(data):
#     logged = logging(data)
#     validated = validate(logged)
#     result = process(validated)
#     return log_return(result)
```

## Function Composition Helpers

### apply_to() - Apply to property

```python
from mfn.functions import apply_to

# Apply function to object property
get_name = apply_to("name")
get_name({"name": "Alice"})  # "Alice"

# With transformation
get_upper_name = apply_to("name", transform=str.upper)
get_upper_name({"name": "Alice"})  # "ALICE"
```

### pluck() - Extract field

```python
from mfn.functions import pluck

# Extract field from objects
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
]

names = pluck("name")(users)  # ["Alice", "Bob"]
```

### pick() - Select fields

```python
from mfn.functions import pick

# Pick specific keys
pick_name_age = pick(["name", "age"])

user = {"name": "Alice", "age": 30, "email": "alice@example.com"}
pick_name_age(user)  # {"name": "Alice", "age": 30}
```

## Function Adapters

### adapt_input() / adapt_output()

```python
from mfn.functions import adapt_input, adapt_output

# Adapt input
@adapt_input(int)
def process_number(x):
    return x * 2

process_number("5")  # 10

# Adapt output
@adapt_output(str)
def calculate(x):
    return x + 1

calculate(5)  # "6"
```

### with_default() / with_fallback()

```python
from mfn.functions import with_default

# Default on exception
@with_default(return_value=0)
def divide(a, b):
    return a / b

divide(10, 2)  # 5
divide(10, 0)  # 0 (caught, returned default)
```

## Implementation

### converge

```python
def converge(funcs, transform=None):
    """Call multiple functions, gather results"""
    def inner(value):
        results = [f(value) for f in funcs]
        if transform:
            return transform(results)
        return results
    return inner
```

### branch

```python
def branch(pred, if_true, if_false):
    """Route based on condition"""
    def inner(value):
        if pred(value):
            return if_true(value)
        else:
            return if_false(value)
    return inner
```

### trampoline

```python
def trampoline(func):
    """Eliminate tail recursion"""
    result = func()
    while callable(result):
        result = result()
    return result
```

### Y Combinator

```python
def y_combinator(func):
    """Y combinator for recursion"""
    def recursive(f):
        return func(lambda x: f(f)(x))
    return recursive(recursive)
```

## Use Cases

### Validation

```python
from mfn.functions import converge

# Run multiple validators
validate = converge([
    validate_presence,
    validate_format,
    validate_unique
])

errors = validate(data)
# [True, True, False] → Has errors
```

### Data Transformation

```python
from mfn.functions import converge

# Multiple aggregations
analyze = converge([
    sum,
    len,
    lambda d: max(d) if d else 0,
    lambda d: min(d) if d else 0
])

analyze([1, 2, 3, 4, 5])
# [15, 5, 5, 1]
```

### Route by Type

```python
from mfn.functions import branch_multi

router = branch_multi(
    lambda x: type(x).__name__,
    {
        "str": process_string,
        "int": process_int,
        "list": process_list,
        "dict": process_dict
    }
)

router("hello")  # process_string("hello")
router(42)     # process_int(42)
```

## Best Practices

### ✅ Do: Use converge for aggregations

```python
# Good: Multiple calculations
stats = converge([sum, len, min, max])
```

### ✅ Do: Use branch for routing

```python
# Good: Clear conditional logic
process = branch(is_admin, admin_process, user_process)
```

### ✅ Do: Use trampoline for recursion

```python
# Good: Prevent stack overflow
factorial_t = trampoline(fact_recursive)
```

### ❌ Don't: Over-complex

```python
# Bad: Hard to understand
complex = converge([f1, f2, f3, f4, f5], transform=complex_transform)

# Better: Break down
step1 = converge([f1, f2, f3])
step2 = transform_1(step1)
```

## Performance

Higher-order functions have overhead:

```python
# Direct call
result = func(value)  # ~0.1µs

# Through higher-order
wrapped = lift(Result)(func)
result = wrapped(value)  # ~0.5µs (5x overhead)

# For most applications, overhead is acceptable
```

## See Also

- [Composition](./02-composition.md) - Combining functions
- [Currying](./01-currying.md) - Incremental arguments
- [Function Utilities](./05-function-utilities.md) - flip, tap, identity

---

**End of Functions**

Next steps:
- See [Core Concepts](../core/) for foundational patterns
- See [Monads](../monads/) for error handling
- See [Collections](../collections/) for functional data structures
