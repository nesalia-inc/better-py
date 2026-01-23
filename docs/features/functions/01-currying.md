# Currying: Incremental Function Application

Transform functions to take arguments one at a time, enabling incremental application and partial application.

## Overview

```python
from mfn.functions import curry

def add(a, b, c):
    return a + b + c

curried = curry(add)
curried(1)(2)(3)  # 6
```

## What is Currying?

**Currying** transforms a function that takes multiple arguments into a sequence of functions that each take a single argument.

```python
# Normal function
def add(a, b, c):
    return a + b + c

add(1, 2, 3)  # 6

# Curried
curried = curry(add)
curried(1)(2)(3)  # 6
```

## Basic Usage

### curry()

```python
from mfn.functions import curry

def multiply(a, b, c):
    return a * b * c

# Curry the function
curried = curry(multiply)

# Apply arguments one at a time
step1 = curried(2)      # Returns function
step2 = step1(3)        # Returns function
step3 = step2(4)        # Returns 16

# Or all at once
result = curried(2)(3)(4)  # 16

# Or original call still works
result = multiply(2, 3, 4)  # 24
```

### Partial Application

```python
def greet(greeting, name):
    return f"{greeting}, {name}!"

# Curry
curried = curry(greet)

# Partial application
hello = curried("Hello")
hi = curried("Hi")

hello("Alice")  # "Hello, Alice!"
hi("Bob")      # "Hi, Bob!"
```

### @curry Decorator

```python
from mfn.functions import curry

@curry
def add(a, b, c):
    return a + b + c

add_1 = add(1)
add_1_2 = add_1(2)
add_1_2(3)  # 6
```

## Advanced Currying

### curry_n() - Specific Arity

```python
from mfn.functions import curry_n

def add(*args):
    return sum(args)

# Curry to exactly 3 arguments
curried_3 = curry_n(3, add)

curried_3(1)(2)(3)  # 6

# Extra arguments ignored or error?
curried_3(1)(2)(3)(4)  # Error or 6
```

### curry_right() - Right to Left

```python
from mfn.functions import curry_right

def subtract(a, b, c):
    return a - b - c

# Normal curry
curried = curry(subtract)
curried(10)(2)(3)  # 10 - 2 - 3 = 5

# Right curry (apply from right)
curried_r = curry_right(subtract)
# First call sets last argument
```

### auto_curry() - Automatic

```python
from mfn.functions import auto_curry

@auto_curry
def add(a, b, c):
    return a + b + c

# Can call with any number of args
add(1, 2, 3)     # 6
add(1)(2, 3)      # 6
add(1)(2)(3)      # 6
add(1, 2)(3)      # 6
```

## Currying vs Partial Application

```python
from mfn.functions import curry, partial

def power(base, exp):
    return base ** exp

# Currying
curried_power = curry(power)
power_of_2 = curried_power(2)
power_of_2(3)  # 8

# Partial application
power_of_2 = partial(power, base=2)
power_of_2(3)  # 8

# Difference:
# - curry: All args partialized left-to-right
# - partial: Specific args fixed by name/position
```

## Practical Examples

### Configuration Builders

```python
@curry
def config(host, port, database):
    return {"host": host, "port": port, "database": database}

# Build configs incrementally
local_config = config("localhost")
dev_config = local_config(5432)
dev_db = dev_config("mydb")

# Or all at once
prod = config("prod.example.com", 3306, "production")
```

### Validation

```python
@curry
def validate(min_val, max_val, value):
    return min_val <= value <= max_val

# Create validators
age_range = validate(18, 100)
port_range = validate(1, 65535)

is_adult = age_range(25)   # True
valid_port = port_range(8080)  # True
```

### Data Processing

```python
@curry
def process(separator, transform, data):
    return separator.join(transform(x) for x in data)

# Create processors
csv = process(",")
uppercase = csv(str.upper)

uppercase(["a", "b", "c"])  # "A,B,C"
```

### API Calls

```python
@curry
def api_call(base_url, endpoint, params):
    return requests.get(f"{base_url}/{endpoint}", params=params)

# Build API client
api = api_call("https://api.example.com")
users = api("users")
page_1 = users({"page": 1})
```

## Method Currying

```python
class Calculator:
    def add(self, a, b):
        return a + b

# Curry instance method
calc = Calculator()
curried_add = curry(calc.add)

add_5 = curried_add(5)
add_5(3)  # 8
```

## Implementation

### Basic Curry

```python
from functools import wraps

def curry(func):
    """Curry function (auto-detect arity)"""
    @wraps(func)
    def curried(*args):
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return lambda *more: curried(*(args + more))
    return curried
```

### Fixed Arity

```python
def curry_n(n, func):
    """Curry to n arguments"""
    def curried(*args):
        if len(args) >= n:
            return func(*args[:n])
        return lambda *more: curried(*(args + more))
    return curried
```

### With Keyword Args

```python
def curry_kwargs(func):
    """Curry with keyword arguments support"""
    @wraps(func)
    def curried(*args, **kwargs):
        # Check if all args satisfied
        # ...
        return func(*args, **kwargs)
    return curried
```

## Type Safety

```python
from typing import TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

def curry(func: Callable[[T, U, V], V]) -> Callable[[T], Callable[[U], V]]:
    """Curried function with type hints"""
    @wraps(func)
    def curried(a: T):
        def step1(b: U):
            return func(a, b)
        return step1
    return curried

# Type inference works
@curry
def add(a: int, b: int) -> int:
    return a + b

add_1: Callable[[int], int] = add(1)
```

## Best Practices

### ✅ Do: Curry multi-argument functions

```python
# Good: Multiple logical arguments
@curry
def connect(host, port, database, user, password):
    return DBConnection(host, port, database, user, password)

local = connect("localhost")
local_db = local(5432)
```

### ✅ Do: Use for creating templates

```python
# Good: Reusable templates
process_csv = process(",")
process_json = process("|")
```

### ❌ Don't: Curry single-arg functions

```python
# Unnecessary
@curry
def square(x):  # Only 1 arg
    return x * x

# Just use the function directly
def square(x):
    return x * x
```

### ❌ Don't: Over-curry

```python
# Hard to read
result = curry(lambda a: curry(lambda b: curry(lambda c: a + b + c)))

# Better: Use decorator
@curry
def add(a, b, c):
    return a + b + c
```

## Performance

Currying has minimal overhead:

```python
# Direct call
add(1, 2, 3)  # ~0.1µs

# Curried call
curried = curry(add)
curried(1)(2)(3)  # ~0.5µs (5x slower, still fast)

# For most applications, overhead is negligible
```

## See Also

- [Partial Application](./03-partial-application.md) - Fix specific arguments
- [Composition](./02-composition.md) - Combine functions
- [Higher-Order Functions](./06-higher-order-functions.md) - Functions for functions
- [Core: Composition](../core/05-composition.md) - Composition philosophy

---

**Next**: [Composition](./02-composition.md)
