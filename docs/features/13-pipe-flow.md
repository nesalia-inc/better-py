# Pipe/Flow - Natural Composition

Intuitive function composition using pipe operators that read left-to-right.

## Overview

Pipe operators enable:
- Natural reading order (left-to-right)
- Clean function composition
- No nested parentheses
- Easy to debug intermediate steps
- Familiar shell-like syntax

## Basic Pipe Operator

```python
from typing import Callable, TypeVar, Any
from functools import reduce

T = TypeVar('T')

def pipe(value: T, *funcs: Callable) -> Any:
    """Pipe value through functions: value | func1 | func2 | func3"""

    result = value
    for func in funcs:
        result = func(result)
    return result


# === Usage ===

def add_one(x: int) -> int:
    return x + 1

def double(x: int) -> int:
    return x * 2

def to_str(x: int) -> str:
    return f"Result: {x}"

# Before (nested, hard to read)
result = to_str(double(add_one(5)))

# After (pipe, natural)
result = pipe(5, add_one, double, to_str)
print(result)  # "Result: 12"
```

## Pipe with | Operator

```python
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')

class Pipeable(Generic[T]):
    """Wrapper to enable pipe syntax"""

    def __init__(self, value: T):
        self._value = value

    def __or__(self, func: Callable[[T], U]) -> 'Pipeable[U]':
        """Pipe operator: value | func"""
        return Pipeable(func(self._value))

    def __ror__(self, func: Callable[[T], U]) -> 'Pipeable[U]':
        """Reverse pipe for: func | value"""
        return Pipeable(func(self._value))

    def unwrap(self) -> T:
        """Get final value"""
        return self._value


def pipe(value: T) -> Pipeable[T]:
    """Start a pipe chain"""
    return Pipeable(value)


# === Usage ===

result = (
    pipe(5)
    | add_one
    | double
    | to_str
).unwrap()

print(result)  # "Result: 12"

# Alternative syntax with | starting
result = (5 | Pipeable | add_one | double | to_str).unwrap()
```

## Flow Builder

```python
from typing import Callable, Any

class Flow:
    """Flow builder for complex transformations"""

    def __init__(self, steps: list[Callable] | None = None):
        self._steps = steps or []

    def step(self, func: Callable, name: str | None = None) -> 'Flow':
        """Add transformation step"""
        self._steps.append(func)
        return self

    def map(self, func: Callable) -> 'Flow':
        """Add map step"""
        return self.step(func)

    def filter(self, predicate: Callable) -> 'Flow':
        """Add filter step"""
        def filter_step(data):
            if isinstance(data, list):
                return [item for item in data if predicate(item)]
            return data if predicate(data) else None
        return self.step(filter_step)

    def tap(self, func: Callable) -> 'Flow':
        """Add side effect (logging, etc) without changing data"""
        def tap_step(data):
            func(data)
            return data
        return self.step(tap_step)

    def __call__(self, initial: Any) -> Any:
        """Execute the flow"""
        result = initial
        for step in self._steps:
            result = step(result)
        return result

    def __or__(self, other: Callable) -> 'Flow':
        """Chain flows: flow1 | flow2"""
        new_flow = Flow(self._steps.copy())
        return new_flow.step(other)


# === Usage ===

process_user = (
    Flow()
    .step(lambda data: data.strip())
    .step(lambda s: s.lower())
    .filter(lambda s: len(s) > 0)
    .tap(lambda x: print(f"Processing: {x}"))
)

result = process_user("  HELLO  ")
# Prints: "Processing: hello"
print(result)  # "hello"
```

## Async Pipe

```python
import asyncio
from typing import Callable, Awaitable, TypeVar

T = TypeVar('T')

async def async_pipe(value: T, *funcs: Callable) -> Any:
    """Pipe value through async functions"""

    result = value
    for func in funcs:
        result = func(result)
        if isinstance(result, Awaitable):
            result = await result
    return result


# === Usage ===

async def fetch_user(id: int):
    await asyncio.sleep(0.1)
    return {"id": id, "name": "Alice"}

async def validate(user: dict) -> dict:
    await asyncio.sleep(0.05)
    if "name" not in user:
        raise ValueError("No name")
    return user

def transform(user: dict) -> str:
    return f"User: {user['name']}"

async def main():
    result = await async_pipe(
        1,
        fetch_user,
        validate,
        transform
    )
    print(result)  # "User: Alice"

asyncio.run(main())
```

## Partial Application with Pipe

```python
from functools import partial

# Create reusable partial functions
add = lambda x, y: x + y
multiply = lambda x, y: x * y

add_five = partial(add, 5)
multiply_by_two = partial(multiply, 2)

result = pipe(
    10,
    add_five,        # 15
    multiply_by_two  # 30
)

print(result)  # 30
```

## Error Handling in Pipe

```python
from typing import Callable, Any

class PipeError(Exception):
    pass

def safe_pipe(value: Any, *funcs: Callable) -> Any:
    """Pipe with error handling"""

    try:
        result = value
        for func in funcs:
            result = func(result)
        return result
    except Exception as e:
        raise PipeError(f"Pipe failed at step: {func.__name__}") from e


# === Usage ===

def might_fail(x):
    if x < 0:
        raise ValueError("Negative")
    return x * 2

try:
    result = safe_pipe(5, might_fail, add_one)
    print(result)  # 11

    result = safe_pipe(-5, might_fail, add_one)
except PipeError as e:
    print(f"Error: {e}")
```

## Pipe with Maybe

```python
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

class Maybe:
    """Maybe monad with pipe support"""

    def __init__(self, value: T | None):
        self._value = value

    def __or__(self, func: Callable[[T], 'Maybe']) -> 'Maybe':
        """Pipe through maybe-aware functions"""
        if self._value is None:
            return Maybe(None)
        return func(self._value)

    def unwrap(self, default=None):
        """Get value or default"""
        return self._value if self._value is not None else default


def map_maybe(func: Callable) -> Callable:
    """Create a maybe-aware function"""
    def wrapper(value):
        return Maybe(func(value))
    return wrapper


# === Usage ===

add_one_maybe = map_maybe(lambda x: x + 1)
double_maybe = map_maybe(lambda x: x * 2)

result = (
    Maybe(5)
    | add_one_maybe
    | double_maybe
)

print(result.unwrap())  # 12

# With None
empty = Maybe(None) | add_one_maybe | double_maybe
print(empty.unwrap())  # None
```

## Composable Flows

```python
# Reusable flow components
validate_email = lambda data: {**data, "email_valid": "@" in data.get("email", "")}
normalize_name = lambda data: {**data, "name": data.get("name", "").strip().title()}
add_timestamp = lambda data: {**data, "created_at": datetime.now()}

# Combine into flows
sanitize_user = Flow().step(normalize_name).step(validate_email)
complete_user = sanitize_user.step(add_timestamp)

# Use
raw_data = {"name": "  alice  ", "email": "alice@example.com"}
clean = complete_user(raw_data)
print(clean)
# {"name": "Alice", "email": "alice@example.com", "email_valid": True, "created_at": ...}
```

## Debugging with Tap

```python
def debug_tap(label: str = ""):
    """Create a tap function for debugging"""
    def tap_func(value):
        print(f"[{label}] {repr(value)}")
        return value
    return tap_func

result = pipe(
    [1, 2, 3, 4, 5],
    debug_tap("Original"),
    lambda x: [i * 2 for i in x],
    debug_tap("Doubled"),
    lambda x: [i for i in x if i > 4],
    debug_tap("Filtered"),
)

# Output:
# [Original] [1, 2, 3, 4, 5]
# [Doubled] [2, 4, 6, 8, 10]
# [Filtered] [6, 8, 10]
```

## DX Benefits

✅ **Readable**: Left-to-right like natural language
✅ **Composable**: Build complex flows from simple steps
✅ **Debuggable**: Easy to insert taps between steps
✅ **Flexible**: Works with sync/async, any callable
✅ **Familiar**: Shell-like syntax developers know

## Best Practices

```python
# ✅ Good: Named reusable steps
sanitize = Flow().step(clean).step(validate)
transform = Flow().step(parse).step(enrich)
pipeline = sanitize | transform

# ✅ Good: Simple functions
add_one = lambda x: x + 1

# ✅ Good: Descriptive tap for debugging
.tap(lambda x: print(f"Processing {x}"))

# ❌ Bad: Too much in one pipe
# Break into named flows instead

# ❌ Bad: Complex lambdas
# Define as named functions
```
