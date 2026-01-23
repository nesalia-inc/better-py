# Async Helpers - Simplified Concurrency

Simplify async operations with helper functions for common concurrency patterns.

## Overview

Async helpers enable:
- Parallel execution
- Rate limiting
- Batching
- Timeouts
- Error aggregation

## Gather with Results

```python
import asyncio
from typing import Coroutine, TypeVar, Any

T = TypeVar('T')

async def gather_results(*coros: Coroutine[Any, Any, T]) -> list[T]:
    """Gather coroutines and return results"""

    return await asyncio.gather(*coros)


async def gather_results_dict(**coros: Coroutine) -> dict:
    """Gather named coroutines and return dict of results"""

    tasks = {name: asyncio.create_task(coro) for name, coro in coros.items()}
    results = {}

    for name, task in tasks.items():
        results[name] = await task

    return results


# === Usage ===

async def fetch_user(id: int) -> dict:
    await asyncio.sleep(0.1)
    return {"id": id, "name": f"User{id}"}

async def fetch_posts(user_id: int) -> list:
    await asyncio.sleep(0.15)
    return [{"id": 1, "user_id": user_id, "title": "Post 1"}]

async def fetch_metadata(user_id: int) -> dict:
    await asyncio.sleep(0.05)
    return {"created_at": "2024-01-01", "updated_at": "2024-01-15"}


# Parallel gather
user, posts, metadata = await gather_results(
    fetch_user(1),
    fetch_posts(1),
    fetch_metadata(1)
)

print(user)      # {"id": 1, "name": "User1"}
print(posts)     # [{"id": 1, ...}]
print(metadata)  # {"created_at": ...}

# Named gather
results = await gather_results_dict(
    user=fetch_user(1),
    posts=fetch_posts(1),
    metadata=fetch_metadata(1)
)

print(results["user"])
```

## Gather with Error Handling

```python
from dataclasses import dataclass
from typing import Exception

@dataclass
class TaskResult:
    """Result of a single task"""

    name: str
    success: bool
    value: Any | None
    error: Exception | None


async def gather_safe(*tasks: tuple[str, Coroutine]) -> list[TaskResult]:
    """Gather tasks, continue on errors"""

    async def run_task(name: str, coro: Coroutine):

        try:
            value = await coro
            return TaskResult(name, True, value, None)
        except Exception as e:
            return TaskResult(name, False, None, e)

    results = await asyncio.gather(
        *(run_task(name, coro) for name, coro in tasks)
    )

    return results


# === Usage ===

results = await gather_safe(
    ("user", fetch_user(1)),
    ("posts", fetch_posts(1)),
    ("invalid", fetch_user(999))  # Might fail
)

for result in results:
    if result.success:
        print(f"{result.name}: {result.value}")
    else:
        print(f"{result.name} failed: {result.error}")
```

## Rate Limiting

```python
import asyncio
from typing import AsyncIterator, TypeVar

T = TypeVar('T')

class RateLimiter:
    """Rate limit async operations"""

    def __init__(self, rate: float, per: float = 1.0):
        """
        rate: number of operations
        per: time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = asyncio.get_event_loop().time()

    async def acquire(self):
        """Wait until rate limit allows operation"""

        current = asyncio.get_event_loop().time()
        time_passed = current - self.last_check
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate

        if self.allowance < 1.0:
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0

        self.last_check = asyncio.get_event_loop().time()


async def rate_limit(
    coros: list[Coroutine],
    rate: float
) -> AsyncIterator[T]:
    """Rate limit execution of coroutines"""

    limiter = RateLimiter(rate)

    for coro in coros:
        await limiter.acquire()
        yield await coro


# === Usage ===

async def fetch_api(id: int) -> dict:
    await asyncio.sleep(0.1)
    return {"id": id, "data": f"item{id}"}

# Fetch 100 items at 10 per second
ids = list(range(100))
coros = [fetch_api(id) for id in ids]

results = []
async for result in rate_limit(coros, rate=10):
    results.append(result)

print(f"Fetched {len(results)} items")
```

## Batching

```python
async def batch_execute(
    coros: list[Coroutine],
    batch_size: int
) -> list[list[T]]:
    """Execute coroutines in batches"""

    results = []

    for i in range(0, len(coros), batch_size):
        batch = coros[i:i + batch_size]
        batch_results = await asyncio.gather(*batch)
        results.append(batch_results)

    return results


async def batch_concurrent(
    items: list[T],
    func: Callable[[T], Coroutine],
    batch_size: int,
    delay_between_batches: float = 0.0
) -> list[Any]:

    all_results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_coros = [func(item) for item in batch]
        batch_results = await asyncio.gather(*batch_coros)
        all_results.extend(batch_results)

        if delay_between_batches > 0 and i + batch_size < len(items):
            await asyncio.sleep(delay_between_batches)

    return all_results


# === Usage ===

async def process_item(item: int) -> int:
    await asyncio.sleep(0.1)
    return item * 2

items = list(range(100))

# Process in batches of 10
results = await batch_concurrent(items, process_item, batch_size=10)

print(f"Processed {len(results)} items")
```

## Timeout

```python
import asyncio

async def with_timeout(
    coro: Coroutine,
    timeout: float
) -> Any:
    """Execute coroutine with timeout"""

    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout}s")


async def with_timeout_default(
    coro: Coroutine,
    timeout: float,
    default: Any
) -> Any:

    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default


# === Usage ===

async def slow_operation():
    await asyncio.sleep(2.0)
    return "Done"

# Raises TimeoutError
try:
    result = await with_timeout(slow_operation(), timeout=1.0)
except TimeoutError as e:
    print(e)

# Returns default
result = await with_timeout_default(slow_operation(), timeout=1.0, default="Timed out")
print(result)  # "Timed out"
```

## Retry Async

```python
async def async_retry(
    coro_func: Callable[[], Coroutine],
    max_attempts: int = 3,
    base_delay: float = 0.1
) -> Any:

    last_error = None

    for attempt in range(max_attempts):
        try:
            return await coro_func()

        except Exception as e:
            last_error = e

            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

    raise last_error


# === Usage ===

async def flaky_api():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Failed")
    return {"status": "ok"}

result = await async_retry(flaky_api, max_attempts=5)
print(result)
```

## Async Iterator Helpers

```python
async def async_take(iterator: AsyncIterator, n: int) -> list:
    """Take first n items from async iterator"""

    results = []
    async for item in iterator:
        results.append(item)
        if len(results) >= n:
            break
    return results


async def async_filter(
    iterator: AsyncIterator,
    predicate: Callable
) -> AsyncIterator:

    async for item in iterator:
        if predicate(item):
            yield item


async def async_map(
    iterator: AsyncIterator,
    func: Callable
) -> AsyncIterator:

    async for item in iterator:
        yield await func(item)


async def async_collect(iterator: AsyncIterator) -> list:
    """Collect all items from async iterator"""

    results = []
    async for item in iterator:
        results.append(item)
    return results


# === Usage ===

async def number_generator():
    for i in range(10):
        await asyncio.sleep(0.01)
        yield i

# Take first 5
first_five = await async_take(number_generator(), 5)

# Filter evens
evens = async_collect(
    async_filter(number_generator(), lambda x: x % 2 == 0)
)

# Map and double
doubled = async_collect(
    async_map(number_generator(), lambda x: x * 2)
)
```

## Parallel Map

```python
async def async_map_parallel(
    items: list[T],
    func: Callable[[T], Coroutine],
    max_concurrency: int = 10
) -> list:

    semaphore = asyncio.Semaphore(max_concurrency)

    async def bounded_func(item):
        async with semaphore:
            return await func(item)

    tasks = [bounded_func(item) for item in items]
    return await asyncio.gather(*tasks)


# === Usage ===

async def fetch_item(id: int):
    await asyncio.sleep(0.1)
    return {"id": id, "value": f"item{id}"}

ids = list(range(100))

# Fetch all items, max 10 concurrent
results = await async_map_parallel(ids, fetch_item, max_concurrency=10)

print(f"Fetched {len(results)} items")
```

## Debounce/Throttle

```python
from asyncio import Queue, Event
from typing import Callable, Any

class AsyncDebouncer:
    """Debounce async operations"""

    def __init__(self, delay: float):
        self.delay = delay
        self._queue: Queue = Queue()
        self._task: asyncio.Task | None = None
        self._latest: Any = None

    async def _worker(self):
        """Process delayed events"""

        while True:
            item = await self._queue.get()

            # Wait for delay
            await asyncio.sleep(self.delay)

            # Get latest value
            result = self._latest
            self._latest = None

            if result is not None:
                yield result

            self._queue.task_done()

    async def call(self, value: Any):
        """Debounced call"""

        self._latest = value
        await self._queue.put(value)


class AsyncThrottler:
    """Throttle async operations"""

    def __init__(self, rate: float):
        self.rate = rate
        self._min_interval = 1.0 / rate
        self._last_call = 0

    async def call(self, func: Callable, *args, **kwargs):

        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_call

        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)

        self._last_call = asyncio.get_event_loop().time()
        return await func(*args, **kwargs)


# === Usage ===

throttler = AsyncThrottler(rate=5)  # 5 calls per second

async def api_call(id: int):
    return await throttler.call(fetch_api, id)

# These will be throttled
results = await asyncio.gather(
    api_call(1),
    api_call(2),
    api_call(3),
    api_call(4),
    api_call(5)
)
```

## DX Benefits

✅ **Simple**: High-level helpers for common patterns
✅ **Safe**: Built-in error handling
✅ **Efficient**: Parallel execution
✅ **Controllable**: Rate limiting, batching
✅ **Flexible**: Works with any async code

## Best Practices

```python
# ✅ Good: Use gather for independent operations
results = await gather(fetch1(), fetch2(), fetch3())

# ✅ Good: Rate limit external APIs
async for result in rate_limit(requests, rate=10):
    ...

# ✅ Good: Batch expensive operations
results = await batch_concurrent(items, process, batch_size=100)

# ❌ Bad: No error handling
# Use gather_safe instead of gather when errors expected
```
