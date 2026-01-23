# Task - Lazy Coroutine Wrapper

Wrap coroutines for lazy execution and composition.

## Overview

`Task` represents a lazy coroutine:
- `Task(coro)` - Lazy coroutine wrapper
- `task.run()` - Execute the coroutine
- `task.map()` - Transform result

## Basic Usage

```python
from mfn import Task

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "data": "success"}


# Create task
task = Task(lambda: fetch_data("https://api.example.com"))

# Task doesn't execute yet
# ...

# Execute when needed
async def main():
    result = await task.run()
    print(result)

asyncio.run(main())
```

## Task Creation Helpers

```python
class TaskHelper:
    """Utilities for Task creation"""

    @staticmethod
    def from_value(value: T) -> Task[T]:
        """Task that immediately returns value"""

        async def inner():
            return value

        return Task(inner)

    @staticmethod
    def from_exception(error: Exception) -> Task:
        """Task that raises exception"""

        async def inner():
            raise error

        return Task(inner)

    @staticmethod
    def delay(duration: float) -> Task:
        """Task that delays"""

        async def inner():
            await asyncio.sleep(duration)

        return Task(inner)

    @staticmethod
    def from_func(func: Callable[[], T]) -> Task[T]:
        """Convert sync function to Task"""

        async def inner():
            return func()

        return Task(inner)
```

## Transformation

```python
class Task(Generic[T]):

    def map(self, func: Callable[[T], U]) -> 'Task[U]':

        async def inner():
            result = await self._coro()
            return func(result)

        return Task(inner)

    def then(self, func: Callable[[T], 'Task[U]']) -> 'Task[U]':

        async def inner():
            result = await self._coro()
            next_task = func(result)
            return await next_task._coro()

        return Task(inner)

    def and_then(self, func: Callable[[T], Any]) -> 'Task':
        """Run task, then ignore result"""

        async def inner():
            result = await self._coro()
            await func(result)
            return result

        return Task(inner)


# === Usage ===
def process(data: dict) -> Task[dict]:
    return Task(lambda: transform_api(data))


async def save(data: dict):
    await db.insert(data)


task = (
    Task(lambda: fetch_data("api"))
    | (lambda d: process(d))
    | (lambda d: Task(lambda: save(d)))
)

result = await task.run()
```

## Error Handling

```python
class Task(Generic[T]):

    def catch(self, exception_type: Type[Exception], handler: Callable) -> 'Task':

        async def inner():
            try:
                return await self._coro()
            except exception_type as e:
                return handler(e)

        return Task(inner)

    def catch_all(self, handler: Callable) -> 'Task':

        async def inner():
            try:
                return await self._coro()
            except Exception as e:
                return handler(e)

        return Task(inner)

    def to_result(self) -> Task[Result[T, Exception]]:

        async def inner():
            try:
                result = await self._coro()
                return Ok(result)
            except Exception as e:
                return Error(e)

        return Task(inner)


# === Usage ===
def risky_operation():
    raise ValueError("Failed")


task = Task(risky_operation).catch_all(lambda e: Ok(f"Handled: {e}"))

result = await task.to_result().run()
# Ok("Handled: Failed")
```

## Task Composition

```python
def sequence(*tasks: Task) -> Task[list]:

    def inner():
        results = []
        for task in tasks:
            result = await task.run()
            results.append(result)
        return results

    return Task(inner)


def parallel(*tasks: Task) -> Task:
    """Run tasks in parallel"""

    async def inner():
        return await asyncio.gather(
            *(task._coro() for task in tasks)
        )

    return Task(inner)


# === Usage ===
async def main():
    # Sequential
    seq = sequence(
        Task(lambda: fetch_user(1)),
        Task(lambda: fetch_posts(1)),
        Task(lambda: fetch_metadata(1))
    )
    user, posts, metadata = await seq.run()

    # Parallel
    par = parallel(
        Task(lambda: fetch_user(1)),
        Task(lambda: fetch_user(2)),
        Task(lambda: fetch_user(3))
    )
    users = await par.run()


asyncio.run(main())
```

## Task Memoization

```python
class MemoizedTask(Generic[T]):

    def __init__(self, task: Task):
        self._task = task
        self._cache: dict = {}

    def run(self) -> Task[T]:

        async def inner():
            # Check cache
            cache_key = id(self._task._coro)
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Execute and cache
            result = await self._task.run()
            self._cache[cache_key] = result

            return result

        return Task(inner)


# === Usage ===
task = Task(lambda: expensive_computation())

# Create memoized wrapper
memoized = MemoizedTask(task)

result1 = await memoized.run()  # Computes
result2 = await memoized.run()  # Cached
```

## Task Retry

```python
def retry_task(task: Task, max_attempts: int = 3, delay: float = 0.1) -> Task:

    async def inner():
        last_error = None

        for attempt in range(max_attempts):
            try:
                return await task.run()
            except Exception as e:
                last_error = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(delay * (2 ** attempt))

        raise last_error

    return Task(inner)


# === Usage ===
task = Task(lambda: fetch_with_retry())
retried = retry_task(task, max_attempts=5)

result = await retried.run()
```

## Task with Timeout

```python
def with_timeout(task: Task, timeout: float) -> Task:

    async def inner():
        try:
            return await asyncio.wait_for(task.run(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Task timed out after {timeout}s")

    return Task(inner)


# === Usage ===
task = Task(lambda: long_running_operation())

timed_task = with_timeout(task, timeout=5.0)

try:
    result = await timed_task.run()
except TimeoutError as e:
    print(f"Task timed out: {e}")
```

## Task Utilities

```python
class TaskOps:
    """Task operations"""

    @staticmethod
    def sleep(duration: float) -> Task[Unit]:

        async def inner():
            await asyncio.sleep(duration)
            return unit()

        return Task(inner)

    @staticmethod
    def from_maybe(maybe: Maybe[T], error: Exception) -> Task[T]:

        async def inner():
            if maybe.is_some():
                return maybe.unwrap()

            raise error

        return Task(inner)

    @staticmethod
    def from_result(result: Result[T, E]) -> Task[T]:

        async def inner():
            if result.is_ok():
                return result.unwrap()

            raise result.error

        return Task(inner)

    @staticmethod
    def from_validation(validation: Validation) -> Task:

        async def inner():
            if validation.is_success():
                return validation.get()

            raise ValidationError(*validation.errors)

        return Task(inner)
```

## DX Benefits

✅ **Lazy**: Coroutines don't execute until run()
✅ **Reusable**: Define once, run multiple times
✅ **Composable**: Chain tasks naturally
✅ **Error-safe**: Built-in error handling
✅ **Memoizable**: Cache expensive computations

## Best Practices

```python
# ✅ Good: Lazy computation
task = Task(lambda: expensive_operation())

# ✅ Good: Compose tasks
Task(process) | (lambda t: t.and_then(save))

# ✅ Good: Convert to Result
task.to_result()

# ✅ Good: Retry and timeout
retry_task(task, max_attempts=3)
with_timeout(task, timeout=5.0)

# ❌ Bad: Running too early
# Keep tasks lazy until needed

# ❌ Bad: Blocking in task
# Use async/await consistently
```
