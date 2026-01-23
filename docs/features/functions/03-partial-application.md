# Partial Application: Fix Function Arguments

Fix specific arguments of a function to create new functions with fewer parameters.

## Overview

```python
from mfn.functions import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
square(5)  # 25
```

## What is Partial Application?

**Partial application** fixes some arguments of a function, creating a new function with fewer parameters.

```python
# Original function
def power(base, exp):
    return base ** exp

# Partial application
square = partial(power, exp=2)

# square is function waiting for base
square(5)  # 25 = power(5, 2)
```

## partial() - Basic Usage

### Positional Arguments

```python
from mfn.functions import partial

def subtract(a, b):
    return a - b

# Fix first argument
sub_from_10 = partial(subtract, 10)
sub_from_10(3)  # 7 = subtract(10, 3)

# Fix second argument
sub_3 = partial(subtract, b=3)
sub_3(10)  # 7 = subtract(10, 3)
```

### Keyword Arguments

```python
from mfn.functions import partial

def greet(name, greeting, punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

# Fix keyword arguments
hello = partial(greet, greeting="Hello")
hello("Alice")  # "Hello, Alice!"

# Fix multiple
excited = partial(greet, greeting="Hello", punctuation="!!!")
excited("Bob")  # "Hello, Bob!!!"
```

### Mixed Arguments

```python
from mfn.functions import partial

def format_user(id, name, active=True, role="user"):
    return {"id": id, "name": name, "active": active, "role": role}

# Fix positional
user_1 = partial(format_user, 1)
user_1("Alice")  # {"id": 1, "name": "Alice", "active": True, "role": "user"}

# Fix keyword
admin = partial(format_user, role="admin")
admin(2, "Bob")  # {"id": 2, "name": "Bob", "active": True, "role": "admin"}

# Fix both
admin_3 = partial(format_user, 3, role="admin")
admin_3("Charlie")  # {"id": 3, "name": "Charlie", "active": True, "role": "admin"}
```

## Advanced Partial Application

### partial_right() - Fix Right Arguments

```python
from mfn.functions import partial_right

def divide(a, b):
    return a / b

# Fix right argument
div_by_2 = partial_right(divide, 2)
div_by_2(10)  # 5.0 = divide(10, 2)
```

### partial_at() - Fix Specific Position

```python
from mfn.functions import partial_at

def multiply(a, b, c):
    return a * b * c

# Fix middle argument
mul_b_5 = partial_at(multiply, 1, 5)  # Position 1 = b
mul_b_5(1, 2)  # 10 = multiply(1, 5, 2)

# Fix last argument
mul_c_10 = partial_at(multiply, -1, 10)  # Position -1 = c
mul_c_10(1, 2)  # 20 = multiply(1, 2, 10)
```

### partial_kwargs() - Keyword Dict

```python
from mfn.functions import partial_kwargs

def api_call(url, method="GET", headers=None, timeout=30):
    return requests.request(method, url, headers=headers, timeout=timeout)

# Fix multiple kwargs
safe_call = partial_kwargs(api_call, {"timeout": 60, "headers": {"User-Agent": "MyApp"}})
safe_call("https://api.example.com")  # Uses timeout=60, headers
```

## Practical Examples

### Configuration

```python
from mfn.functions import partial

def connect(host, port, database, user, password):
    return DBConnection(host, port, database, user, password)

# Partial configs
local = partial(connect, host="localhost", port=5432)
local("mydb", "user", "pass")  # DBConnection("localhost", 5432, "mydb", ...)

prod = partial(connect, host="prod.db", port=5432, user="admin")
prod("production", password)  # DBConnection(...)
```

### Validation

```python
from mfn.functions import partial

def validate_length(value, min_len, max_len):
    return min_len <= len(value) <= max_len

# Create validators
validate_name = partial(validate_length, min_len=2, max_len=50)
validate_username = partial(validate_length, min_len=3, max_len=20)

validate_name("Alice")  # True
validate_name("A")  # False
```

### Data Processing

```python
from mfn.functions import partial

def encode(data, encoding="utf-8", errors="strict"):
    return data.encode(encoding, errors)

# Specific encoders
encode_utf8 = partial(encode, encoding="utf-8")
encode_latin1 = partial(encode, encoding="latin-1")

encode_utf8("hello")  # b"hello"
```

### API Calls

```python
from mfn.functions import partial

def fetch_api(url, version="v1", format="json"):
    return requests.get(f"{url}/{version}", params={"format": format})

# Versioned clients
api_v1 = partial(fetch_api, version="v1")
api_v2 = partial(fetch_api, version="v2")

api_v1("https://api.example.com")  # GET .../v1?format=json
```

## partial vs curry

```python
from mfn.functions import curry, partial

def multiply(a, b, c):
    return a * b * c

# Curry: Partialize left-to-right
curried = curry(multiply)
step1 = curried(2)  # Waiting for b, c
step2 = step1(3)   # Waiting for c
step3 = step2(4)   # 24

# Partial: Fix specific arguments
mul_2_3 = partial(multiply, b=2, c=3)
mul_2_3(5)  # 30

# Difference:
# - curry: All args partialized in order
# - partial: Any args can be fixed
```

## partialmethod() - Methods

```python
from mfn.functions import partialmethod

class API:
    def _call(self, endpoint, method="GET"):
        return requests.request(method, endpoint)

    # Partial method
    get = partialmethod(_call, method="GET")
    post = partialmethod(_call, method="POST")

api = API("https://api.example.com")
api.get("/users")   # GET https://api.example.com/users
api.post("/users")  # POST https://api.example.com/users
```

## Type Safety

```python
from typing import Callable, TypeVar
from functools import partial

T = TypeVar('T')
U = TypeVar('U')

def partial_func(func: Callable[[T, U], int], value: T) -> Callable[[U], int]:
    """Partial with type hints"""
    return partial(func, value)

# Type inference works
def add(a: int, b: int) -> int:
    return a + b

add_5: Callable[[int], int] = partial_func(add, 5)
```

## Implementation

### Basic partial

```python
from functools import partial

# Already in Python standard library
from functools import partial

def greet(name, greeting):
    return f"{greeting}, {name}!"

hello = partial(greet, greeting="Hello")
hello("World")  # "Hello, World!"
```

### Custom partial

```python
def my_partial(func, *args, **kwargs):
    """Custom partial implementation"""
    def wrapper(*more_args, **more_kwargs):
        all_args = args + more_args
        all_kwargs = {**kwargs, **more_kwargs}
        return func(*all_args, **all_kwargs)
    return wrapper
```

## Best Practices

### ✅ Do: Use for reusable configurations

```python
# Good: Reusable DB connection
local_db = partial(connect, host="localhost", port=5432)
```

### ✅ Do: Fix constants

```python
# Good: Fix conversion factor
km_to_miles = partial(convert, factor=0.621371)
```

### ✅ Do: Create specialized functions

```python
# Good: Specific validators
is_adult = partial(validate_age, min=18)
```

### ❌ Don't: Partial when curry is better

```python
# If partializing left-to-right, use curry
# Bad:
add_1 = partial(add, 1)
add_1(2)(3)  # Error!

# Good:
curried = curry(add)
add_1 = curried(1)
add_1(2)(3)  # Works
```

## Performance

Partial application has minimal overhead:

```python
# Direct call
power(5, 2)  # ~0.1µs

# Partial
square = partial(power, exp=2)
square(5)  # ~0.15µs (50% overhead, still fast)
```

## See Also

- [Currying](./01-currying.md) - Incremental arguments
- [Composition](./02-composition.md) - Combine functions
- [Function Utilities](./05-function-utilities.md) - flip, tap, identity

---

**Next**: [Pipe & Flow](./04-pipe-and-flow.md)
