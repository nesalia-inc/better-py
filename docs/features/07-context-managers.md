# Context Managers - Resource Management

Functional approach to resource management using Python's context managers.

## Overview

Context managers enable:
- Automatic resource cleanup
- Transaction-like semantics
- State management
- Composable resource handling
- Exception-safe operations

## Basic Context Manager

```python
from contextlib import contextmanager
from typing import Generator, TypeVar

T = TypeVar('T')

@contextmanager
def maybe_context(maybe: Maybe[T]) -> Generator[Maybe[T], None, None]:
    """Context manager for Maybe monad"""
    print(f"Entering context with: {maybe}")
    try:
        yield maybe
    finally:
        print("Exiting context")


# Usage
maybe_value = Maybe(42)

with maybe_context(maybe_value) as m:
    print(f"Inside: {m}")
# Output:
# Entering context with: Maybe(42)
# Inside: Maybe(42)
# Exiting context
```

## Transaction Context Manager

```python
from contextlib import contextmanager
from typing import Generator, Callable

@contextmanager
def transaction(session):
    """Database transaction with automatic commit/rollback"""

    try:
        yield session  # Provide session to block
        session.commit()
        print("Transaction committed")

    except Exception as e:
        session.rollback()
        print(f"Transaction rolled back: {e}")
        raise


# === Usage ===

class Session:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def execute(self, sql):
        if "error" in sql.lower():
            raise ValueError("SQL error")
        return f"Executed: {sql}"


# Success case
session = Session()
with transaction(session):
    session.execute("SELECT * FROM users")

print(f"Committed: {session.committed}")  # True

# Failure case
session = Session()
try:
    with transaction(session):
        session.execute("ERROR SQL")
except ValueError:
    pass

print(f"Rolled back: {session.rolled_back}")  # True
```

## Maybe Context Manager

```python
from contextlib import contextmanager
from typing import Generator, TypeVar

T = TypeVar('T')

@dataclass
class Maybe(Generic[T]):
    value: T | None

    @contextmanager
    def unpack(self) -> Generator[T, None, None]:
        """Unpack Maybe in context, raises if None"""
        if self.value is None:
            raise ValueError("Cannot unpack None Maybe")
        try:
            yield self.value
        finally:
            pass


# === Usage ===

maybe_user = Maybe("Alice")

with maybe_user.unpack() as username:
    print(f"Hello, {username}!")  # "Hello, Alice!"

maybe_empty = Maybe(None)

# This raises ValueError
try:
    with maybe_empty.unpack() as username:
        print(username)
except ValueError as e:
    print(f"Error: {e}")  # "Error: Cannot unpack None Maybe"
```

## Resource Management with Maybe

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(resource_id: str) -> Generator[Maybe[Resource], None, None]:
    """Acquire resource, return Maybe for safe handling"""

    resource = None
    try:
        # Try to acquire resource
        resource = acquire(resource_id)

        if resource is None:
            yield Maybe(None)
        else:
            yield Maybe(resource)

    finally:
        # Always cleanup if acquired
        if resource is not None:
            release(resource)


def acquire(resource_id: str) -> 'Resource | None':
    """Simulate resource acquisition"""
    if resource_id == "invalid":
        return None
    return Resource(resource_id)

def release(resource: 'Resource'):
    """Simulate resource release"""
    print(f"Released: {resource.id}")


class Resource:
    def __init__(self, id: str):
        self.id = id

    def use(self):
        return f"Using {self.id}"


# === Usage ===

# Valid resource
with managed_resource("res1") as maybe_res:
    result = maybe_res.map(lambda r: r.use())
    print(result)  # Maybe("Using res1")
# Output: "Released: res1"

# Invalid resource
with managed_resource("invalid") as maybe_res:
    print(maybe_res)  # Maybe(None)
    # No resource to release
```

## Composable Context Managers

```python
from contextlib import ExitStack, contextmanager

@contextmanager
def log_context(name: str):
    """Logging context"""
    print(f"[{name}] Entering")
    try:
        yield
    finally:
        print(f"[{name}] Exiting")


@contextmanager
def timer_context():
    """Timing context"""
    import time
    start = time.time()
    try:
        yield
    finally:
        print(f"Elapsed: {time.time() - start:.3f}s")


def compose_contexts(*contexts):
    """Compose multiple context managers"""

    def outer(wrapped_func):
        def wrapper(*args, **kwargs):
            with ExitStack() as stack:
                # Enter all contexts
                for ctx in contexts:
                    stack.enter_context(ctx)

                # Run wrapped function
                return wrapped_func(*args, **kwargs)

        return wrapper

    return outer


# === Usage ===

@compose_contexts(
    log_context("operation"),
    timer_context()
)
def process_data(n: int):
    """Function with composed contexts"""
    return sum(range(n))


process_data(1000000)
# Output:
# [operation] Entering
# Elapsed: 0.045s
# [operation] Exiting
```

## Result-based Context Manager

```python
from contextlib import contextmanager
from typing import Generator, Callable

@dataclass
class Result:
    value: any
    error: Exception | None

    def is_ok(self) -> bool:
        return self.error is None

    @contextmanager
    def unwrap(self):
        """Unpack result, raise on error"""
        if self.error:
            raise self.error
        try:
            yield self.value
        finally:
            pass


@contextmanager
def safe_operation(operation: Callable) -> Generator[Result, None, None]:
    """Execute operation safely, capture errors"""
    try:
        result = operation()
        yield Result(result, None)
    except Exception as e:
        yield Result(None, e)


# === Usage ===

def risky_division(a: int, b: int) -> float:
    return a / b

# Success case
with safe_operation(lambda: risky_division(10, 2)) as result:
    if result.is_ok():
        print(f"Result: {result.value}")  # "Result: 5.0"

# Error case
with safe_operation(lambda: risky_division(10, 0)) as result:
    if result.error:
        print(f"Error caught: {result.error}")  # "Error caught: division by zero"
```

## Functional State Management

```python
from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Generator

@dataclass(frozen=True)
class State:
    counter: int
    active: bool


@contextmanager
def state_transition(initial: State) -> Generator[State, None, None]:
    """Manage state transitions with automatic rollback"""

    current = initial
    states = [initial]  # History for rollback

    def update(new_state: State):
        nonlocal current
        states.append(new_state)
        current = new_state
        return current

    try:
        yield update

    except Exception:
        # Rollback to initial state
        current = initial
        print(f"Rolled back to: {current}")
        raise

    finally:
        print(f"State history: {states}")


# === Usage ===

initial = State(counter=0, active=False)

with state_transition(initial) as transition:
    print(f"Initial: {transition(State(counter=0, active=False))}")

    state1 = transition(State(counter=1, active=True))
    print(f"State 1: {state1}")

    state2 = transition(State(counter=2, active=True))
    print(f"State 2: {state2}")

# Output:
# Initial: State(counter=0, active=False)
# State 1: State(counter=1, active=True)
# State 2: State(counter=2, active=True)
# State history: [State(counter=0, active=False), State(counter=1, active=True), State(counter=2, active=True)]
```

## Async Context Managers

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def async_maybe_context(maybe: 'Maybe'):
    """Async context manager for Maybe"""
    print("Entering async context")
    try:
        yield maybe
    finally:
        print("Exiting async context")


@dataclass
class Maybe:
    value: any

    async def async_map(self, func):
        """Async map operation"""
        if self.value is None:
            return Maybe(None)
        result = await func(self.value)
        return Maybe(result)


# === Usage ===

import asyncio

async def fetch_user(user_id: int):
    """Simulate async fetch"""
    await asyncio.sleep(0.1)
    return "Alice" if user_id == 1 else None

async def main():
    maybe_id = Maybe(1)

    async with async_maybe_context(maybe_id) as m:
        user = await m.async_map(fetch_user)
        print(f"User: {user.value}")  # "User: Alice"

asyncio.run(main())
```

## DX Benefits

✅ **Automatic cleanup**: Resources guaranteed to be released
✅ **Exception-safe**: Cleanup even on errors
✅ **Composable**: Combine multiple contexts
✅ **Readable**: Intent is explicit
✅ **Type-safe**: Works with static type checkers

## Best Practices

```python
# ✅ Good: Simple cleanup
@contextmanager
def resource():
    r = acquire()
    try:
        yield r
    finally:
        release(r)

# ✅ Good: Handling errors
@contextmanager
def transaction():
    try:
        yield
    except Exception:
        rollback()
        raise
    else:
        commit()

# ✅ Good: Composable with ExitStack
with ExitStack() as stack:
    f1 = stack.enter_context(open('file1.txt'))
    f2 = stack.enter_context(open('file2.txt'))

# ❌ Bad: Not releasing on error
@contextmanager
def bad_resource():
    r = acquire()
    yield r  # What if exception?
    release(r)  # Never called on error!
```
