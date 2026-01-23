# AsyncResult - Async Error Handling

Handle async operations that can fail without exceptions.

## Overview

`AsyncResult` is like `Result` but for async operations:
- `Ok(value)` - Success with value
- `Error(exception)` - Failure with Exception object

## Basic Usage

```python
import asyncio
from mfn import AsyncResult, Ok, Error

async def fetch_user(id: int) -> AsyncResult[dict]:
    await asyncio.sleep(0.1)

    if id <= 0:
        return Error(ValidationError("Invalid ID"))

    return Ok({"id": id, "name": "Alice"})


# Use
async def main():
    result = await fetch_user(1)

    if result.is_ok():
        print(f"User: {result.unwrap()}")
    else:
        exc = result.exception
        print(f"Error: {type(exc).__name__}: {exc}")

asyncio.run(main())
```

## Transformation

```python
from mfn import AsyncResult

async def validate(data: dict) -> AsyncResult:
    await asyncio.sleep(0.05)

    if "email" not in data:
        return Error(ValidationError("No email"))

    return Ok(data)

async def sanitize(data: dict) -> AsyncResult:
    await asyncio.sleep(0.05)
    return Ok({**data, "email": data["email"].lower()})

# Chain async operations
async def process():
    result = await (
        AsyncResult.ok({"email": "USER@EXAMPLE.COM"})
        .then(validate)
        .then(sanitize)
    )

    return result
```

## Pipe Operators

```python
from mfn import AsyncResult

async def fetch_api(url: str) -> AsyncResult:
    await asyncio.sleep(0.1)
    return Ok({"data": "success"})

async def validate(response: dict) -> AsyncResult:
    if "data" in response:
        return Ok(response)
    return Error(ValidationError("Invalid response"))

async def process():
    result = await (
        AsyncResult.ok("https://api.example.com")
        | fetch_api
        | validate
    )

    return result
```

## Combining Async Results

```python
from mfn import AsyncResult

async def gather_all(*results: AsyncResult) -> AsyncResult:

    awaited = [await result for result in results]

    values = []
    errors = []

    for result in awaited:
        if result.is_ok():
            values.append(result.unwrap())
        else:
            errors.append(result.exception)

    if errors:
        return Error(errors)

    return Ok(values)


# Use case
async def main():
    user = await fetch_user(1)
    posts = await fetch_posts(1)
    metadata = await fetch_metadata(1)

    result = await gather_all(user, posts, metadata)

    if result.is_ok():
        user_data, posts_data, metadata_data = result.unwrap()
        print(f"Got {len(posts_data)} posts")
    else:
        excs = result.exception
        for exc in excs:
            print(f"Error: {type(exc).__name__}: {exc}")
```

## Conversion

```python
from mfn import AsyncResult, Result

# Result to AsyncResult
async def to_async(result: Result) -> AsyncResult:
    return result

# AsyncResult to Result
async def from_async(async_result: AsyncResult) -> Result:
    return await async_result

# Maybe to AsyncResult
async def maybe_to_async(maybe: Maybe, error: Exception) -> AsyncResult:
    if maybe.is_some():
        return Ok(maybe.unwrap())
    return Error(error)

# Try/catch to AsyncResult
async def safe_execute(coro):
    try:
        return Ok(await coro)
    except Exception as e:
        return Error(e)
```

## Rate Limiting

```python
from mfn import AsyncResult

async def fetch_with_limit(ids: list[int]) -> AsyncResult:

    async def fetch_one(id: int):
        await asyncio.sleep(0.1)
        if id > 0:
            return Ok({"id": id})
        return Error(ValidationError(f"Invalid {id}"))

    results = []

    for id in ids:
        result = await fetch_one(id)

        if result.is_ok():
            results.append(result.unwrap())
        else:
            # Continue on error
            continue

    return Ok(results)


# Use
async def main():
    result = await fetch_with_limit([1, 2, -1, 3, -2])
    # Ok([{"id": 1}, {"id": 2}, {"id": 3}])
```

## Parallel Execution

```python
from mfn import AsyncResult

async def fetch_parallel(*coros) -> AsyncResult:

    results = await asyncio.gather(
        *[safe_execute(coro) for coro in coros],
        return_exceptions=True
    )

    values = []
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
        elif result.is_error():
            errors.append(result.exception)
        else:
            values.append(result.unwrap())

    if errors:
        return Error(errors)

    return Ok(values)


# Use
async def main():
    result = await fetch_parallel(
        fetch_user(1),
        fetch_posts(1),
        fetch_metadata(1)
    )
```

## DX Benefits

✅ **Async-safe**: No exception handling in async code
✅ **Composable**: Chain async operations
✅ **Type-safe**: Full typing support
✅ **Parallel**: Combine multiple async results
✅ **Explicit**: Error handling is visible
✅ **Structured**: Exception objects with attributes

## Best Practices

```python
# ✅ Good: Chain async operations
result = await (
    AsyncResult.ok(data)
    | validate
    | save
)

# ✅ Good: Gather parallel results
results = await gather_all(fetch1(), fetch2(), fetch3())

# ✅ Good: Continue on errors
for result in results:
    if result.is_ok():
        process(result.unwrap())

# ✅ Good: Use custom exceptions
Error(ValidationError("message"))

# ❌ Bad: Mix sync/async
# Keep all operations async or all sync

# ❌ Bad: Try/catch in async
# Use AsyncResult instead
```
