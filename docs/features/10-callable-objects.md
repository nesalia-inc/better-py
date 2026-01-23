# Callable Objects - Higher-Order Functions

Objects that behave like functions using `__call__` for powerful functional programming patterns.

## Overview

Callable objects enable:
- Stateful function-like objects
- Method chaining
- Function composition
- Lazy evaluation
- Custom execution semantics

## Basic Callable Object

```python
from typing import Callable

class Adder:
    """Callable object that adds a constant"""

    def __init__(self, n: int):
        self.n = n

    def __call__(self, x: int) -> int:
        return x + self.n


# === Usage ===

add_five = Adder(5)
print(add_five(10))  # 15
print(add_five(20))  # 25

# Callable check
print(callable(add_five))  # True
print(isinstance(add_five, Callable))  # True
```

## Function Composition

```python
from typing import Callable, TypeVar, Any
from functools import reduce

T = TypeVar('T')

class Compose:
    """Compose multiple functions"""

    def __init__(self, *funcs: Callable[[Any], Any]):
        self.funcs = funcs

    def __call__(self, value: T) -> Any:
        """Execute composition: f(g(h(x)))"""
        result = value
        for func in reversed(self.funcs):
            result = func(result)
        return result

    def __or__(self, other: Callable) -> 'Compose':
        """Compose using | operator"""
        return Compose(*self.funcs, other)

    def __rshift__(self, other: Callable) -> 'Compose':
        """Compose using >> operator (left-to-right)"""
        return Compose(other, *self.funcs)


# === Usage ===

def add_one(x: int) -> int:
    return x + 1

def double(x: int) -> int:
    return x * 2

def to_str(x: int) -> str:
    return f"Result: {x}"

# Compose: add_one → double → to_str
pipeline = Compose(to_str, double, add_one)

print(pipeline(5))  # "Result: 12" (5+1=6, 6*2=12)

# Using operators
pipeline2 = Compose(add_one) | double | to_str
print(pipeline2(5))  # "Result: 12"
```

## Lazy Evaluation

```python
from typing import Callable, Iterator, Iterable

class LazyMap:
    """Lazy mapping callable"""

    def __init__(self, func: Callable, iterable: Iterable):
        self.func = func
        self.iterable = iterable

    def __call__(self) -> Iterator:
        """Return iterator over mapped values"""
        return (self.func(x) for x in self.iterable)

    def __iter__(self):
        """Make iterable"""
        return self()


# === Usage ===

numbers = range(1000000)  # Large range
lazy_squared = LazyMap(lambda x: x ** 2, numbers)

# No computation yet!
print(lazy_squared)  # LazyMap object

# Iterate to compute
count = 0
for value in lazy_squared:
    print(value)
    count += 1
    if count >= 5:
        break  # Only computes first 5 values!
```

## Memoized Callable

```python
from typing import Callable, TypeVar, Hashable
from functools import wraps

T = TypeVar('T')

class Memoized:
    """Memoization wrapper"""

    def __init__(self, func: Callable[..., T]):
        self.func = func
        self.cache: dict = {}

    def __call__(self, *args, **kwargs) -> T:
        # Create cache key
        key = (args, tuple(sorted(kwargs.items())))

        if key not in self.cache:
            self.cache[key] = self.func(*args, **kwargs)

        return self.cache[key]

    def clear(self):
        """Clear cache"""
        self.cache.clear()

    def cache_size(self) -> int:
        """Get cache size"""
        return len(self.cache)


# === Usage ===

@Memoized
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(100))  # Fast! (cached)
print(fibonacci.cache_size())  # Number of cached results
```

## Currying Callable

```python
from typing import Callable, Any
from functools import partial

class Curried:
    """Currying wrapper"""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._arity = func.__code__.co_argcount

    def __call__(self, *args, **kwargs) -> Any:
        # Combine all arguments
        all_args = self.args + args
        all_kwargs = {**self.kwargs, **kwargs}

        # Check if we have all arguments
        if len(all_args) + len(all_kwargs) >= self._arity:
            return self.func(*all_args, **all_kwargs)

        # Return new curried function
        return Curried(self.func, *all_args, **all_kwargs)


# === Usage ===

def add(a: int, b: int, c: int) -> int:
    return a + b + c

curried_add = Curried(add)

# Can apply all at once
print(curried_add(1, 2, 3))  # 6

# Or partially
add_one = curried_add(1)
add_one_two = add_one(2)
print(add_one_two(3))  # 6

# Or in one expression
print(Curried(add)(1)(2)(3))  # 6
```

## Validation Callable

```python
from typing import Callable, TypeVar, Any
from dataclasses import dataclass, field

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Validator:
    """Callable validator"""

    predicates: list[Callable[[T], bool]] = field(default_factory=list)
    error_message: str = "Validation failed"

    def __call__(self, value: T) -> bool:
        """Validate value against all predicates"""
        return all(pred(value) for pred in self.predicates)

    def add(self, predicate: Callable[[T], bool]) -> 'Validator':
        """Add validation predicate"""
        self.predicates.append(predicate)
        return self

    def with_message(self, message: str) -> 'Validator':
        """Set custom error message"""
        self.error_message = message
        return self


# === Usage ===

email_validator = (
    Validator()
    .add(lambda x: "@" in x)
    .add(lambda x: "." in x.split("@")[1])
    .with_message("Invalid email format")
)

print(email_validator("user@example.com"))  # True
print(email_validator("invalid"))  # False
print(email_validator.error_message)  # "Invalid email format"
```

## Pipeline Callable

```python
from typing import Callable, Any

class Pipeline:
    """Callable pipeline for data transformation"""

    def __init__(self, *steps: Callable[[Any], Any]):
        self.steps = steps

    def __call__(self, data: Any) -> Any:
        """Execute all pipeline steps"""
        result = data
        for step in self.steps:
            result = step(result)
        return result

    def add(self, step: Callable) -> 'Pipeline':
        """Add step to pipeline"""
        return Pipeline(*self.steps, step)

    def __or__(self, step: Callable) -> 'Pipeline':
        """Add step using | operator"""
        return self.add(step)


# === Usage ===

def validate(data: dict) -> dict:
    if 'email' not in data:
        raise ValueError("Missing email")
    return data

def sanitize(data: dict) -> dict:
    data['email'] = data['email'].lower().strip()
    return data

def transform(data: dict) -> str:
    return f"Processed: {data['email']}"

# Build pipeline
process = Pipeline()
process = process | validate | sanitize | transform

# Or inline
result = Pipeline(validate, sanitize, transform)({'email': '  JOHN@EXAMPLE.COM  '})
print(result)  # "Processed: john@example.com"
```

## Thunk/Lazy Evaluation

```python
from typing import Callable, TypeVar

T = TypeVar('T')

class Thunk:
    """Lazy evaluation wrapper (thunk)"""

    def __init__(self, func: Callable[[], T]):
        self.func = func
        self._computed: T | None = None
        self._evaluated = False

    def __call__(self) -> T:
        """Evaluate on first call, cache result"""
        if not self._evaluated:
            self._computed = self.func()
            self._evaluated = True
        return self._computed  # type: ignore

    def is_evaluated(self) -> bool:
        """Check if thunk has been evaluated"""
        return self._evaluated

    def force(self) -> T:
        """Force evaluation"""
        return self()


# === Usage ===

import time

def expensive_computation():
    print("Computing...")
    time.sleep(0.1)
    return 42

thunk = Thunk(expensive_computation)

# Not evaluated yet
print(thunk.is_evaluated())  # False

# First call - computes
result = thunk()
# Output: "Computing..."
print(result)  # 42

# Subsequent calls - cached
print(thunk())  # 42 (no computation!)
print(thunk.is_evaluated())  # True
```

## Predicate Builder

```python
from typing import Callable, Any

class Predicate:
    """Composable predicate builder"""

    def __init__(self, func: Callable[[Any], bool]):
        self.func = func

    def __call__(self, value: Any) -> bool:
        return self.func(value)

    def __and__(self, other: 'Predicate') -> 'Predicate':
        """Combine with AND: p1 & p2"""
        return Predicate(lambda x: self(x) and other(x))

    def __or__(self, other: 'Predicate') -> 'Predicate':
        """Combine with OR: p1 | p2"""
        return Predicate(lambda x: self(x) or other(x))

    def __invert__(self) -> 'Predicate':
        """Negate: ~p"""
        return Predicate(lambda x: not self(x))

    @staticmethod
    def gt(n: int) -> 'Predicate':
        return Predicate(lambda x: x > n)

    @staticmethod
    def lt(n: int) -> 'Predicate':
        return Predicate(lambda x: x < n)

    @staticmethod
    def eq(value: Any) -> 'Predicate':
        return Predicate(lambda x: x == value)


# === Usage ===

is_positive = Predicate.gt(0)
is_even = Predicate(lambda x: x % 2 == 0)
is_small = Predicate.lt(100)

# Combine predicates
is_valid = is_positive & is_even & is_small

print(is_valid(4))    # True
print(is_valid(6))    # False (6 < 100 is True, but need all True)
print(is_valid(-2))   # False (not positive)

# Negation
not_small = ~is_small
print(not_small(150))  # True
```

## Retry Callable

```python
import time
from typing import Callable, TypeVar, Type

T = TypeVar('T')

class Retry:
    """Callable with automatic retry"""

    def __init__(
        self,
        func: Callable[..., T],
        max_attempts: int = 3,
        delay: float = 0.1,
        exceptions: tuple[Type[Exception], ...] = (Exception,)
    ):
        self.func = func
        self.max_attempts = max_attempts
        self.delay = delay
        self.exceptions = exceptions

    def __call__(self, *args, **kwargs) -> T:
        """Execute with retry logic"""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return self.func(*args, **kwargs)
            except self.exceptions as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    time.sleep(self.delay * (2 ** attempt))

        raise last_exception  # type: ignore


# === Usage ===

import random

def flaky_operation():
    if random.random() < 0.7:
        raise ConnectionError("Failed")
    return "Success"

retry_flaky = Retry(flaky_operation, max_attempts=5, delay=0.1)
print(retry_flaky())  # "Success" (after retries)
```

## DX Benefits

✅ **Stateful**: Carry state between calls
✅ **Composable**: Chain and combine callables
✅ **Flexible**: Custom execution semantics
✅ **Pythonic**: Natural function syntax
✅ **Type-safe**: Works with static type checkers

## Best Practices

```python
# ✅ Good: Stateful callable
class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1
        return self.count

# ✅ Good: Preserving function metadata
from functools import wraps

class Wrapper:
    def __init__(self, func):
        self.func = func
        wraps(func)(self)  # Copy metadata

# ✅ Good: Type annotations
class Processor:
    def __call__(self, data: str) -> str: ...

# ❌ Bad: Overly complex callables
# Keep __call__ simple and focused
```
