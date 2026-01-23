# Decorators - Metaprogramming

Elegant composition of cross-cutting concerns using Python decorators.

## Overview

Decorators enable:
- Function transformation
- Cross-cutting concerns (logging, caching, validation)
- Fluent, declarative APIs
- Behavior injection
- Method chaining

## Basic Decorator Pattern

```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

P = ParamSpec('P')
R = TypeVar('R')

def decorator(func: Callable[P, R]) -> Callable[P, R]:
    """Basic decorator structure"""

    @wraps(func)  # Preserves original function metadata
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Before
        result = func(*args, **kwargs)
        # After
        return result

    return wrapper
```

## Curry Decorator

```python
from functools import wraps, partial
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def curried(func: Callable) -> Callable:
    """Transforms a function into a curried version"""

    @wraps(func)
    def curried_wrapper(*args, **kwargs):
        # If all args provided, call the function
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)

        # Otherwise, return a partial waiting for remaining args
        return partial(curried_wrapper, *args, **kwargs)

    return curried_wrapper


# === Usage ===

@curried
def add(a: int, b: int, c: int) -> int:
    return a + b + c

# Can call with all arguments
print(add(1, 2, 3))  # 6

# Or partially apply
add_one = add(1)
add_one_two = add_one(2)
print(add_one_two(3))  # 6

# Or in one expression
print(add(1)(2)(3))  # 6
```

## Memoize Decorator

```python
from functools import wraps, lru_cache
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

def memoize(func: Callable[P, R]) -> Callable[P, R]:
    """Cache function results"""

    cache: dict = {}

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Create cache key from args and kwargs
        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    # Add cache management methods
    wrapper.cache_clear = cache.clear  # type: ignore
    wrapper.cache_info = lambda: f"{len(cache)} entries cached"  # type: ignore

    return wrapper


# === Usage ===

@memoize
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(100))  # Fast! (cached)
print(fibonacci.cache_info())  # "101 entries cached"
```

## Type Validation Decorator

```python
from typing import Any, Callable, TypeVar, get_type_hints
from inspect import signature

T = TypeVar('T')

def validate_types(func: Callable[..., T]) -> Callable[..., T]:
    """Runtime type checking based on type hints"""

    hints = get_type_hints(func)
    sig = signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # Bind arguments to parameter names
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Validate each argument
        for name, value in bound.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"{func.__name__}() argument '{name}' "
                        f"must be {expected_type}, got {type(value)}"
                    )

        result = func(*args, **kwargs)

        # Validate return type
        if 'return' in hints:
            if not isinstance(result, hints['return']):
                raise TypeError(
                    f"{func.__name__}() must return {hints['return']}, "
                    f"got {type(result)}"
                )

        return result

    return wrapper


# === Usage ===

@validate_types
def process_user(user_id: int, name: str) -> str:
    return f"User {user_id}: {name}"

print(process_user(1, "Alice"))  # ✅ Works
print(process_user("1", "Alice"))  # ❌ TypeError: user_id must be <class 'int'>
```

## Retry Decorator

```python
from typing import Callable, TypeVar, Type
from time import sleep
from functools import wraps

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    delay: float = 0.1,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """Retry a function on failure"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep(delay * (2 ** attempt))  # Exponential backoff

            raise last_exception  # type: ignore

        return wrapper

    return decorator


# === Usage ===

@retry(max_attempts=3, delay=0.5, exceptions=(ConnectionError,))
def fetch_data(url: str) -> dict:
    # Simulate flaky connection
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return {"data": "success"}

print(fetch_data("https://api.example.com"))  # Retries on failure
```

## Monadic Transform Decorator

```python
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')
R = TypeVar('R')

def monadic_transform(monad_class: type) -> Callable:
    """Transform regular function to return monadic value"""

    def decorator(func: Callable[..., R]) -> Callable[..., 'Maybe[R]']:
        @wraps(func)
        def wrapper(*args, **kwargs) -> 'Maybe[R]':
            try:
                result = func(*args, **kwargs)
                return monad_class(result)
            except Exception as e:
                return monad_class(None)

        return wrapper

    return decorator


# === Usage ===

class Maybe:
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return f"Maybe({self._value!r})"


@monadic_transform(Maybe)
def divide(a: int, b: int) -> float:
    return a / b


print(divide(10, 2))  # Maybe(5.0)
print(divide(10, 0))  # Maybe(None) (caught ZeroDivisionError)
```

## Pipeline Decorator

```python
from typing import Callable, Iterable

def pipeline(*steps: Callable) -> Callable:
    """Chain functions into a pipeline"""

    def decorator(input_data: Any) -> Any:
        result = input_data
        for step in steps:
            result = step(result)
        return result

    return decorator


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

# Create pipeline
process_user = pipeline(validate, sanitize, transform)

result = process_user({'email': '  JOHN@EXAMPLE.COM  '})
print(result)  # "Processed: john@example.com"
```

## Logging Decorator

```python
import logging
from typing import Callable, Any
from functools import wraps

def log(level: int = logging.INFO, logger: logging.Logger | None = None) -> Callable:
    """Log function calls"""

    def decorator(func: Callable) -> Callable:
        log = logger or logging.getLogger(func.__module__)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            log.log(level, f"Calling {func.__name__}(*{args}, **{kwargs})")
            try:
                result = func(*args, **kwargs)
                log.log(level, f"{func.__name__} returned {result!r}")
                return result
            except Exception as e:
                log.log(level, f"{func.__name__} raised {e}")
                raise

        return wrapper

    return decorator


# === Usage ===

@log(level=logging.DEBUG)
def expensive_computation(n: int) -> int:
    return sum(range(n))


# Logs:
# DEBUG:__main__:Calling expensive_computation(*(1000,), **{})
# DEBUG:__main__:expensive_computation returned 499500
```

## Compose Decorator

```python
from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

def compose(*funcs: Callable) -> Callable:
    """Compose functions right-to-left: compose(f, g, h)(x) = f(g(h(x)))"""

    def composed(value: T) -> R:
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result

    return composed


# === Usage ===

def add_one(x: int) -> int:
    return x + 1

def double(x: int) -> int:
    return x * 2

def to_str(x: int) -> str:
    return str(x)

# Compose: add_one → double → to_str
pipeline = compose(to_str, double, add_one)

print(pipeline(5))  # "12" (add_one: 6, double: 12, to_str: "12")
```

## Stackable Decorators

```python
@curried
@memoize
@validate_types
def process(user_id: int, multiplier: int) -> int:
    """Stack multiple decorators"""
    return user_id * multiplier


# Execution order (bottom to top):
# 1. validate_types checks types
# 2. memoize caches result
# 3. curried enables partial application
print(process(5)(2))  # 10
```

## Class-Based Decorators

```python
class CountCalls:
    """Decorator that counts function calls"""

    def __init__(self, func: Callable):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} called {self.count} times")
        return self.func(*args, **kwargs)


# === Usage ===

@CountCalls
def calculate():
    return 42

print(calculate())  # "calculate called 1 times", then 42
print(calculate())  # "calculate called 2 times", then 42
print(calculate.count)  # 2
```

## DX Benefits

✅ **Separation of concerns**: Business logic separated from cross-cutting concerns
✅ **Declarative**: Read like configuration
✅ **Reusable**: Apply same decorator to many functions
✅ **Composable**: Stack multiple decorators
✅ **Readable**: Intent at a glance

## Best Practices

```python
# ✅ Good: Always use functools.wraps
@wraps(func)
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)

# ✅ Good: Type-preserving decorators
P = ParamSpec('P')
R = TypeVar('R')
def decorator(func: Callable[P, R]) -> Callable[P, R]: ...

# ✅ Good: Descriptive names
@retry(max_attempts=3, delay=0.1)
def fetch_data(): ...

# ❌ Bad: Losing function metadata
def bad_decorator(func):
    def wrapper(*args, **kwargs):  # Missing @wraps
        return func(*args, **kwargs)
    return wrapper
```
