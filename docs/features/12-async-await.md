# Async/Await - Async Functional

Composable asynchronous functional programming using Python's async/await.

## Overview

Async functional programming enables:
- Non-blocking monadic operations
- Composable async pipelines
- Concurrent processing
- Error handling in async contexts
- Resource management

## Basic Async Maybe

```python
from typing import Generic, TypeVar, Awaitable, Callable
import asyncio

T = TypeVar('T')

class AsyncMaybe(Generic[T]):
    """Async Maybe monad"""

    def __init__(self, value: T | None):
        self._value = value

    @classmethod
    def some(cls, value: T) -> 'AsyncMaybe[T]':
        return cls(value)

    @classmethod
    def none(cls) -> 'AsyncMaybe[T]':
        return cls(None)

    async def map(self, f: Callable[[T], Awaitable[T] | T]) -> 'AsyncMaybe[T]':
        """Async map operation"""
        if self._value is None:
            return AsyncMaybe.none()

        result = f(self._value)
        if isinstance(result, Awaitable):
            result = await result

        return AsyncMaybe.some(result)

    async def flat_map(self, f: Callable[[T], Awaitable['AsyncMaybe[T]'] | 'AsyncMaybe[T]') -> 'AsyncMaybe[T]':
        """Async bind operation"""
        if self._value is None:
            return AsyncMaybe.none()

        result = f(self._value)
        if isinstance(result, Awaitable):
            result = await result

        return result


# === Usage ===

async def fetch_user(user_id: int) -> str:
    """Simulate async fetch"""
    await asyncio.sleep(0.1)
    return "Alice" if user_id == 1 else None

async def greet(name: str) -> str:
    """Simulate async greeting"""
    await asyncio.sleep(0.05)
    return f"Hello, {name}!"


async def main():
    maybe_id = AsyncMaybe.some(1)

    result = await (
        maybe_id
        .flat_map(lambda id: AsyncMaybe.some(fetch_user(id)))
        .flat_map(lambda user_future: AsyncMaybe.some(await user_future))
        .map(greet)
        .map(lambda greeting_future: asyncio.create_task(greeting_future))
    )

    if result._value:
        final_greeting = await result._value
        print(final_greeting)  # "Hello, Alice!"

asyncio.run(main())
```

## Async Result Type

```python
from typing import Generic, TypeVar, Awaitable, Callable
import asyncio

T = TypeVar('T')
E = TypeVar('E')

class AsyncResult(Generic[T, E]):
    """Async Result type for error handling"""

    def __init__(self, value: T | None, error: E | None, is_ok: bool):
        self._value = value
        self._error = error
        self._is_ok = is_ok

    @classmethod
    def ok(cls, value: T) -> 'AsyncResult[T, E]':
        return cls(value, None, True)

    @classmethod
    def error(cls, error: E) -> 'AsyncResult[T, E]':
        return cls(None, error, False)

    def is_ok(self) -> bool:
        return self._is_ok

    def is_error(self) -> bool:
        return not self._is_ok

    async def map(self, f: Callable[[T], Awaitable[T] | T]) -> 'AsyncResult[T, E]':
        """Map over success value"""
        if not self._is_ok:
            return self

        result = f(self._value)  # type: ignore
        if isinstance(result, Awaitable):
            result = await result

        return AsyncResult.ok(result)

    async def map_error(self, f: Callable[[E], Awaitable[E] | E]) -> 'AsyncResult[T, E]':
        """Map over error value"""
        if self._is_ok:
            return self

        result = f(self._error)  # type: ignore
        if isinstance(result, Awaitable):
            result = await result

        return AsyncResult.error(result)

    async def flat_map(self, f: Callable[[T], Awaitable['AsyncResult[T, E]'] | 'AsyncResult[T, E]') -> 'AsyncResult[T, E]':
        """Chain Results"""
        if not self._is_ok:
            return self

        result = f(self._value)  # type: ignore
        if isinstance(result, Awaitable):
            result = await result

        return result


# === Usage ===

async def fetch_user(id: int) -> AsyncResult[str, str]:
    """Fetch user async"""
    await asyncio.sleep(0.1)

    if id == 1:
        return AsyncResult.ok("Alice")
    return AsyncResult.error("User not found")

async def validate_user(name: str) -> AsyncResult[str, str]:
    """Validate user async"""
    await asyncio.sleep(0.05)

    if len(name) >= 3:
        return AsyncResult.ok(name)
    return AsyncResult.error("Name too short")


async def main():
    result = await (
        fetch_user(1)
        .flat_map(lambda user: validate_user(user))
    )

    if result.is_ok():
        print(f"Success: {result._value}")
    else:
        print(f"Error: {result._error}")

asyncio.run(main())  # "Success: Alice"
```

## Async Pipeline Operators

```python
from typing import Callable, Any, Awaitable, Iterable
import asyncio

class AsyncPipeline:
    """Async pipeline builder"""

    def __init__(self, steps: list[Callable] | None = None):
        self.steps = steps or []

    def pipe(self, step: Callable) -> 'AsyncPipeline':
        """Add step to pipeline"""
        return AsyncPipeline(self.steps + [step])

    def __or__(self, step: Callable) -> 'AsyncPipeline':
        """Add step using | operator"""
        return self.pipe(step)

    async def __call__(self, initial: Any) -> Any:
        """Execute pipeline"""
        result = initial
        for step in self.steps:
            result = step(result)
            if isinstance(result, Awaitable):
                result = await result
        return result


# === Usage ===

async def fetch_data(id: int):
    await asyncio.sleep(0.1)
    return {"id": id, "value": f"data-{id}"}

async def validate(data: dict):
    await asyncio.sleep(0.05)
    if "value" not in data:
        raise ValueError("No value")
    return data

def transform(data: dict):
    return f"Processed: {data['value']}"

# Build pipeline
pipeline = AsyncPipeline()
pipeline = (
    pipeline
    | fetch_data
    | validate
    | transform
)

async def main():
    result = await pipeline(1)
    print(result)  # "Processed: data-1"

asyncio.run(main())
```

## Async Validation Chain

```python
from typing import Callable, Awaitable, TypeVar
import asyncio

T = TypeVar('T')

class AsyncValidator:
    """Async validation chain"""

    def __init__(self, value: T):
        self._value = value
        self._errors: list[str] = []

    async def check(self, predicate: Callable[[T], Awaitable[bool] | bool], error: str) -> 'AsyncValidator':
        """Add validation check"""
        result = predicate(self._value)
        if isinstance(result, Awaitable):
            result = await result

        if not result:
            self._errors.append(error)

        return self

    async def is_valid(self) -> bool:
        """Check if all validations passed"""
        return len(self._errors) == 0

    def errors(self) -> list[str]:
        """Get validation errors"""
        return self._errors


# === Usage ===

async def check_email_unique(email: str) -> bool:
    """Async email uniqueness check"""
    await asyncio.sleep(0.1)
    return email not in ["taken@example.com"]

async def validate_user_data(data: dict) -> bool:
    """Validate user data"""
    validator = AsyncValidator(data)

    await (
        validator
        .check(lambda d: "email" in d, "Email is required")
        .check(lambda d: "@" in d.get("email", ""), "Invalid email format")
        .check(lambda d: len(d.get("name", "")) >= 2, "Name too short")
        .check(lambda d: asyncio.create_task(check_email_unique(d.get("email", ""))), "Email already taken")
    )

    if await validator.is_valid():
        print("Valid!")
        return True
    else:
        print(f"Errors: {validator.errors()}")
        return False

asyncio.run(validate_user_data({"email": "new@example.com", "name": "Alice"}))
```

## Async Retry

```python
import asyncio
from typing import Callable, TypeVar, Type, Awaitable

T = TypeVar('T')

class AsyncRetry:
    """Async retry with exponential backoff"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 5.0,
        exceptions: tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions

    async def __call__(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute with retry logic"""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)

            except self.exceptions as e:
                last_exception = e

                if attempt < self.max_attempts - 1:
                    # Exponential backoff with jitter
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    await asyncio.sleep(delay)

        raise last_exception  # type: ignore

    def __or__(self, func: Callable[..., Awaitable[T]]) -> Callable:
        """Use with pipe operator"""
        async def wrapped(*args, **kwargs):
            return await self(func, *args, **kwargs)
        return wrapped


# === Usage ===

async def flaky_api_call():
    """Simulate flaky API"""
    import random
    await asyncio.sleep(0.1)

    if random.random() < 0.7:
        raise ConnectionError("API error")

    return {"data": "success"}

retry = AsyncRetry(max_attempts=5, base_delay=0.2)

# Direct usage
result = await retry(flaky_api_call)
print(result)

# Pipe usage
retry_fn = retry | flaky_api_call
result = await retry_fn()
print(result)
```

## Async Context Manager

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator, TypeVar, Generic

T = TypeVar('T')

@asynccontextmanager
async def async_transaction(session):
    """Async transaction context manager"""

    try:
        print("Starting transaction")
        yield session
        await session.commit()
        print("Transaction committed")

    except Exception as e:
        await session.rollback()
        print(f"Transaction rolled back: {e}")
        raise


class AsyncSession:
    async def commit(self):
        await asyncio.sleep(0.1)

    async def rollback(self):
        await asyncio.sleep(0.1)

    async def execute(self, sql):
        await asyncio.sleep(0.1)
        return f"Executed: {sql}"


# === Usage ===

async def main():
    session = AsyncSession()

    async with async_transaction(session):
        result = await session.execute("SELECT * FROM users")
        print(result)

asyncio.run(main())
```

## Async Generator Pipeline

```python
from typing import AsyncGenerator, Callable, Awaitable, TypeVar

T = TypeVar('T')
U = TypeVar('U')

class AsyncStream:
    """Async stream processing"""

    def __init__(self, source: AsyncGenerator[T, None]):
        self._source = source

    @staticmethod
    def from_iterable(items: list[T]) -> 'AsyncStream[T]':
        """Create stream from iterable"""

        async def generator():
            for item in items:
                yield item

        return AsyncStream(generator())

    async def map(self, f: Callable[[T], Awaitable[U] | U]) -> 'AsyncStream[U]':
        """Map over stream"""

        async def mapped_generator():
            async for item in self._source:
                result = f(item)
                if isinstance(result, Awaitable):
                    result = await result
                yield result

        return AsyncStream(mapped_generator())

    async def filter(self, predicate: Callable[[T], Awaitable[bool] | bool]) -> 'AsyncStream[T]':
        """Filter stream"""

        async def filtered_generator():
            async for item in self._source:
                result = predicate(item)
                if isinstance(result, Awaitable):
                    result = await result
                if result:
                    yield item

        return AsyncStream(filtered_generator())

    async def take(self, n: int) -> list[T]:
        """Take first n items"""
        results = []
        async for item in self._source:
            results.append(item)
            if len(results) >= n:
                break
        return results

    async def to_list(self) -> list[T]:
        """Collect all items"""
        return [item async for item in self._source]


# === Usage ===

async def process_number(n: int):
    await asyncio.sleep(0.01)
    return n * 2

async def main():
    stream = AsyncStream.from_iterable(range(10))

    result = await (
        stream
        .map(lambda x: x + 1)
        .map(process_number)
        .filter(lambda x: x > 10)
        .take(3)
    )

    print(result)  # [12, 14, 16]

asyncio.run(main())
```

## Concurrent Processing

```python
import asyncio
from typing import Callable, TypeVar, Awaitable, Iterable

T = TypeVar('T')
R = TypeVar('R')

async def map_concurrent(
    items: Iterable[T],
    func: Callable[[T], Awaitable[R]],
    concurrency: int = 10
) -> list[R]:
    """Map over items concurrently"""

    async def worker(queue: asyncio.Queue, results: list):
        """Worker coroutine"""
        while True:
            item, index = await queue.get()
            try:
                result = await func(item)
                results[index] = result
            finally:
                queue.task_done()

    # Create queue
    queue: asyncio.Queue = asyncio.Queue()
    for index, item in enumerate(items):
        await queue.put((item, index))

    # Initialize results
    results = [None] * len(list(items))

    # Create workers
    tasks = [
        asyncio.create_task(worker(queue, results))
        for _ in range(concurrency)
    ]

    # Wait for all items to be processed
    await queue.join()

    # Cancel workers
    for task in tasks:
        task.cancel()

    return results  # type: ignore


# === Usage ===

async def fetch_item(id: int):
    await asyncio.sleep(0.1)  # Simulate I/O
    return f"item-{id}"

async def main():
    items = range(20)
    results = await map_concurrent(items, fetch_item, concurrency=5)
    print(results[:5])  # ['item-0', 'item-1', 'item-2', 'item-3', 'item-4']

asyncio.run(main())
```

## DX Benefits

✅ **Non-blocking**: Composable async operations
✅ **Efficient**: Concurrent I/O operations
✅ **Type-safe**: Full typing support for async
✅ **Readable**: Linear code flow
✅ **Pythonic**: Native async/await syntax

## Best Practices

```python
# ✅ Good: Explicit async operations
async def fetch_user(id: int) -> AsyncResult[User]:
    ...

# ✅ Good: Composable async pipelines
result = await fetch_user(1) | validate | transform

# ✅ Good: Proper error handling
try:
    result = await risky_operation()
except SpecificError:
    handle_error()

# ✅ Good: Using asyncio.gather for independence
results = await asyncio.gather(op1(), op2(), op3())

# ❌ Bad: Mixing sync and async incorrectly
def bad():
    result = await async_func()  # SyntaxError!

# ❌ Bad: Blocking in async
async def blocking():
    time.sleep(1)  # Blocks! Use asyncio.sleep instead
```
