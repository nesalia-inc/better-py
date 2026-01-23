# AsyncMaybe - Async Optional Values

Handle async operations that might not return values.

## Overview

`AsyncMaybe` is `Maybe` for async operations:
- `AsyncSome(value)` - Async computation with value
- `AsyncNone` - Async computation without value
- `await maybe.or_else(default)` - Get value or default

## Basic Usage

```python
from mfn import AsyncMaybe, AsyncSome, AsyncNone

async def fetch_user(id: int) -> AsyncMaybe[dict]:
    await asyncio.sleep(0.1)

    if id <= 0:
        return AsyncNone

    return AsyncSome({"id": id, "name": "Alice"})


# Use
async def main():
    result = await fetch_user(1)

    if await result.is_some():
        user = await result.unwrap()
        print(f"User: {user}")
    else:
        print("User not found")

asyncio.run(main())
```

## Transformation

```python
class AsyncMaybe(Generic[T]):

    async def map(self, func: Callable[[T], Awaitable[U]]) -> 'AsyncMaybe[U]':

        if self._value is None:
            return AsyncNone

        result = await func(self._value)
        return AsyncSome(result)

    async def flat_map(self, func: Callable[[T], 'AsyncMaybe[U]']) -> 'AsyncMaybe[U]':

        if self._value is None:
            return AsyncNone

        return await func(self._value)

    async def filter(self, predicate: Callable[[T], bool]) -> 'AsyncMaybe[T]':

        if self._value is None:
            return AsyncNone

        if predicate(self._value):
            return AsyncSome(self._value)

        return AsyncNone
```

## Pipe Operators

```python
async def get_user(id: int) -> AsyncMaybe[dict]:
    # Fetch user from cache
    cached = await cache.get(f"user:{id}")
    if cached:
        return AsyncSome(cached)

    # Fetch from DB
    user = await db.find(id)
    if user:
        await cache.set(f"user:{id}", user)
        return AsyncSome(user)

    return AsyncNone


async def validate_user(user: dict) -> AsyncMaybe[dict]:

    if not user.get("active", True):
        return AsyncNone

    return AsyncSome(user)


async def process():
    maybe_user = (
        AsyncSome(1)
        | get_user
        | validate_user
    )

    if await maybe_user.is_some():
        user = await maybe_user.unwrap()
        print(f"Valid user: {user}")


asyncio.run(process())
```

## Get Value or Default

```python
class AsyncMaybe(Generic[T]):

    async def unwrap_or(self, default: T) -> T:

        if self._value is None:
            return default

        return self._value

    async def unwrap_or_else(self, func: Callable[[], T]) -> T:

        if self._value is not None:
            return self._value

        return func()

    async def or_else(self, default_factory: Callable[[], T]) -> 'AsyncMaybe[T]':

        if self._value is not None:
            return AsyncSome(self._value)

        # Async default factory
        result = await default_factory()
        return AsyncSome(result)
```

## AsyncMaybe Helpers

```python
class AsyncMaybeOps:
    """AsyncMaybe utilities"""

    @staticmethod
    async def from_maybe(maybe: Maybe[T]) -> AsyncMaybe[T]:
        """Convert Maybe to AsyncMaybe"""

        if maybe.is_some():
            return AsyncSome(maybe.unwrap())
        return AsyncNone

    @staticmethod
    async def from_result(result: Result[T, E]) -> AsyncMaybe[T]:

        if result.is_ok():
            return AsyncSome(result.unwrap())
        return AsyncNone

    @staticmethod
    async def from_exception(callable: Callable) -> AsyncMaybe[T]:

        try:
            result = await callable()
            return AsyncSome(result)
        except:
            return AsyncNone

    @staticmethod
    async def collect(maybes: list[AsyncMaybe]) -> AsyncMaybe[list]:

        values = []

        for maybe in maybes:
            if await maybe.is_some():
                values.append(await maybe.unwrap())

        if values:
            return AsyncSome(values)

        return AsyncNone

    @staticmethod
    async def first(maybes: list[AsyncMaybe]) -> AsyncMaybe:

        for maybe in maybes:
            if await maybe.is_some():
                return maybe

        return AsyncNone
```

## AsyncMaybe with Database

```python
class UserRepository:

    async def find_cached(self, id: int) -> AsyncMaybe[User]:

        # Try cache
        cached = await self.cache.get(f"user:{id}")

        if cached:
            return AsyncSome(cached)

        # Try database
        user = await self.db.query(
            "SELECT * FROM users WHERE id = $1",
            id
        ).first()

        if user:
            await self.cache.set(f"user:{id}", user)
            return AsyncSome(user)

        return AsyncNone

    async def find_or_create(self, id: int, defaults: dict) -> AsyncMaybe[User]:

        user = await self.find_cached(id)

        if await user.is_some():
            return user

        # Create new user
        new_user = await self.db.create(user_id=id, **defaults)
        return AsyncSome(new_user)


# === Usage ===
async def get_user_profile(id: int) -> AsyncMaybe[dict]:

    user_maybe = await repo.find_or_create(id, {"name": "Guest"})

    if await user_maybe.is_some():
        user = await user_maybe.unwrap()

        profile = await fetch_profile(user.id)
        return AsyncSome({**user.dict(), **profile})

    return AsyncNone
```

## AsyncMaybe Chaining

```python
async def process_order(order_id: int) -> Result[Order, Exception]:

    maybe_order = (
        AsyncSome(order_id)
        | fetch_order
        | validate_order
        | fetch_items
    )

    if await maybe_order.is_none():
        return Error(NotFoundError("Order", order_id))

    order = await maybe_order.unwrap()
    return Ok(order)
```

## Conversion Between AsyncMaybe and Others

```python
# AsyncMaybe to Result
async def to_result(async_maybe: AsyncMaybe, error: Exception) -> Result:

    if await async_maybe.is_some():
        return Ok(await async_maybe.unwrap())

    return Error(error)


# AsyncMaybe to Maybe
async def to_maybe(async_maybe: AsyncMaybe) -> Maybe:

    if await async_maybe.is_some():
        return Some(await async_maybe.unwrap())

    return None_


# Result to AsyncMaybe
async def from_result(result: Result) -> AsyncMaybe:

    if result.is_ok():
        return AsyncSome(result.unwrap())

    return AsyncNone
```

## AsyncMaybe in Pipelines

```python
async def fetch_user_data(user_id: int) -> AsyncMaybe[dict]:

    return (
        AsyncSome(user_id)
        | (lambda id: fetch_user(id))
        | (lambda user: fetch_profile(user.get('id')))
        | (lambda profile: AsyncSome(profile))
    )
```

## DX Benefits

✅ **Async-native**: Designed for coroutines
✅ **Lazy**: Deferred execution
✅ **Composable**: Chain with pipe operators
✅ **Safe**: No None checks needed
✅ **Convertible**: Works with Maybe, Result

## Best Practices

```python
# ✅ Good: Chain async operations
AsyncSome(id) | fetch_user | validate_user

# ✅ Good: Provide defaults
await maybe.unwrap_or(default_user)

# ✅ Good: Use with Result
await to_result(async_maybe, ValidationError("Not found"))

# ✅ Good: Cache lookups
return AsyncSome(cached_value)

# ❌ Bad: Mixing sync/async
# Keep operations consistently async

# ❌ Bad: Returning None
# Use AsyncNone() explicitly
```
