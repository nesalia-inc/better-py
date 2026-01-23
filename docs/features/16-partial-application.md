# Partial Application - Easy Function Specialization

Create specialized functions by fixing some arguments, making code more reusable.

## Overview

Partial application enables:
- Fix function arguments
- Create reusable specialized functions
- Reduce boilerplate with lambdas
- Improve code readability
- Build higher-order functions

## Basic Partial Application

```python
from functools import partial

def greet(greeting: str, name: str) -> str:
    return f"{greeting}, {name}!"

# Fix first argument
say_hello = partial(greet, "Hello")
say_hi = partial(greet, "Hi")

print(say_hello("Alice"))  # "Hello, Alice!"
print(say_hi("Bob"))       # "Hi, Bob!"

# Fix second argument using keyword
greet_alice = partial(greet, name="Alice")
print(greet_alice("Hello"))  # "Hello, Alice!"
```

## Custom Partial Helper

```python
from typing import Callable, TypeVar, Any
from functools import wraps

P = TypeVar('P')
R = TypeVar('R')

def partial_right(func: Callable, *args, **kwargs) -> Callable:
    """Partial application from right to left"""

    @wraps(func)
    def wrapper(*remaining_args, **remaining_kwargs):
        all_args = remaining_args + args
        all_kwargs = {**kwargs, **remaining_kwargs}
        return func(*all_args, **all_kwargs)

    return wrapper


def partial_at(func: Callable, positions: dict[int, Any]) -> Callable:
    """Partial application at specific positions"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Build full arg list
        full_args = list(args)
        for pos, value in sorted(positions.items()):
            if pos >= len(full_args):
                full_args.append(value)
            else:
                full_args.insert(pos, value)

        return func(*full_args, **kwargs)

    return wrapper


# === Usage ===

def calculate(price: float, tax: float, discount: float) -> float:
    return price * (1 + tax) * (1 - discount)

# Fix tax and discount
with_tax_and_discount = partial_right(calculate, 0.10, 0.0)

print(with_tax_and_discount(100))  # 110.0

# Fix specific positions
with_fixed_tax = partial_at(calculate, {1: 0.20})
print(with_fixed_tax(100, 0.0))  # 120.0
```

## Curry Decorator

```python
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def curry(func: Callable) -> Callable:
    """Transform function into curried version"""

    @wraps(func)
    def curried(*args, **kwargs):
        # If all args provided, call function
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)

        # Otherwise return partial
        return partial(func, *args, **kwargs)

    return curried


# === Usage ===

@curry
def add(a: int, b: int, c: int) -> int:
    return a + b + c

# Can call with all args
print(add(1, 2, 3))  # 6

# Or partially apply
add_one = add(1)
add_one_two = add_one(2)
print(add_one_two(3))  # 6

# Or in one expression
print(add(1)(2)(3))  # 6
```

## Pipeable Partial

```python
from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')

class Partial:
    """Partial application with pipe support"""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        """Execute with additional args"""
        all_args = self.args + args
        all_kwargs = {**self.kwargs, **kwargs}
        return self.func(*all_args, **all_kwargs)

    def __or__(self, other: Callable) -> 'Partial':
        """Compose: partial1 | partial2"""
        return Partial(lambda x: other(self(x)))

    def __rshift__(self, other: Callable) -> 'Partial':
        """Map operation"""
        return Partial(lambda x: other(self.func(*self.args, x, **self.kwargs)))


def partial_pipe(func: Callable, *args, **kwargs) -> Partial:
    """Create pipeable partial function"""
    return Partial(func, *args, **kwargs)


# === Usage ===

def fetch_user(id: int, timeout: float, retries: int) -> dict:
    return {"id": id, "timeout": timeout, "retries": retries}

# Create partial with defaults
fetch_user_defaults = partial_pipe(fetch_user, timeout=5.0, retries=3)

# Call with remaining args
user = fetch_user_defaults(123)
print(user)  # {"id": 123, "timeout": 5.0, "retries": 3}
```

## Fluent Partial Builder

```python
class PartialBuilder:
    """Builder pattern for partial application"""

    def __init__(self, func: Callable):
        self.func = func
        self._args: list = []
        self._kwargs: dict = {}

    def set(self, **kwargs) -> 'PartialBuilder':
        """Set keyword arguments"""
        self._kwargs.update(kwargs)
        return self

    def append(self, *args) -> 'PartialBuilder':
        """Append positional arguments"""
        self._args.extend(args)
        return self

    def build(self) -> Callable:
        """Build partial function"""
        return partial(self.func, *self._args, **self._kwargs)


# === Usage ===

def send_email(to: str, subject: str, body: str, priority: str = "normal") -> str:
    return f"Email to {to}: {subject} ({priority})"

email_builder = PartialBuilder(send_email)
urgent_email = email_builder.set(priority="urgent").build()

print(urgent_email("admin@example.com", "Alert", "System down"))
# "Email to admin@example.com: Alert (urgent)"
```

## Method Partial Application

```python
class PartialMethods:
    """Helper for partial method binding"""

    @staticmethod
    def bind(obj: Any, method_name: str, *args, **kwargs) -> Callable:
        """Bind method with partial args"""

        method = getattr(obj, method_name)

        @wraps(method)
        def bound(*more_args, **more_kwargs):
            return method(*args, *more_args, **{**kwargs, **more_kwargs})

        return bound


# === Usage ===

class User:
    def __init__(self, name: str):
        self.name = name

    def greet(self, greeting: str, punctuation: str = "!") -> str:
        return f"{greeting}, {self.name}{punctuation}"


user = User("Alice")

# Bind with partial args
hello_user = PartialMethods.bind(user, "greet", "Hello")
print(hello_user())              # "Hello, Alice!"
print(hello_user("Hi", "!!!"))   # "Hi, Alice!!!"
```

## Async Partial Application

```python
import asyncio
from typing import Awaitable, Callable

def async_partial(func: Callable[..., Awaitable], *args, **kwargs) -> Callable:
    """Partial application for async functions"""

    @wraps(func)
    async def wrapper(*more_args, **more_kwargs):
        all_args = args + more_args
        all_kwargs = {**kwargs, **more_kwargs}
        return await func(*all_args, **all_kwargs)

    return wrapper


# === Usage ===

async def fetch_data(url: str, timeout: float, headers: dict) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "timeout": timeout}

# Create partial
fetch_with_timeout = async_partial(fetch_data, timeout=5.0, headers={})

async def main():
    result = await fetch_with_timeout("https://api.example.com")
    print(result)

asyncio.run(main())
```

## Predicate Builders

```python
def predicate_from(func: Callable[[T], R], value: R) -> Callable[[T], bool]:
    """Create predicate from function and expected value"""

    def predicate(item: T) -> bool:
        return func(item) == value

    return predicate


# === Usage ===

users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 30}
]

# Create predicates
is_30 = predicate_from(lambda u: u["age"], 30)
is_alice = predicate_from(lambda u: u["name"], "Alice")

# Use with filter
thirty_year_olds = list(filter(is_30, users))
print([u["name"] for u in thirty_year_olds])  # ["Alice", "Charlie"]
```

## Composable Partial Operations

```python
class ComposablePartial:
    """Partial application with composition support"""

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        all_args = self.args + args
        all_kwargs = {**self.kwargs, **kwargs}
        return self.func(*all_args, **all_kwargs)

    def then(self, next_func: Callable) -> 'ComposablePartial':
        """Chain with another function"""

        def chained(*args, **kwargs):
            result = self(*args, **kwargs)
            return next_func(result)

        return ComposablePartial(chained)

    def map(self, mapper: Callable) -> 'ComposablePartial':
        """Map the result"""

        def mapped(*args, **kwargs):
            result = self(*args, **kwargs)
            return mapper(result)

        return ComposablePartial(mapped)


# === Usage ===

def fetch_user(id: int) -> dict:
    return {"id": id, "name": "Alice", "email": "alice@example.com"}

def get_email(user: dict) -> str:
    return user["email"]

def to_upper(s: str) -> str:
    return s.upper()

# Chain operations
get_upper_email = (
    ComposablePartial(fetch_user)
    .then(get_email)
    .map(to_upper)
)

print(get_upper_email(1))  # "ALICE@EXAMPLE.COM"
```

## DX Benefits

✅ **Reusable**: Create specialized functions from general ones
✅ **Concise**: Replace lambdas with partial application
✅ **Readable**: Named partial functions are self-documenting
✅ **Composable**: Chain partial functions together
✅ **Flexible**: Works with sync/async, methods, etc.

## Best Practices

```python
# ✅ Good: Named partial for clarity
say_hello = partial(greet, "Hello")

# ✅ Good: Use keyword args for clarity
fetch = partial(requests.get, timeout=30)

# ✅ Good: Curry for building step by step
add_one = curry(add)(1)

# ❌ Bad: Partial with unclear args
# What does this fix?
p = partial(func, "value", None, True)

# ❌ Bad: Overusing partial when lambda is clearer
# Prefer: lambda x: x + 1
# Over: partial(add, 1)
```
