# Cache/Memoization - Performance Helpers

Cache function results for performance optimization.

## Overview

Caching enables:
- Skip expensive recalculations
- Automatic cache management
- TTL-based expiration
- Size limits
- Cache invalidation

## Basic Memoization

```python
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar('T')

def memoize(func: Callable) -> Callable:
    """Cache function results"""

    cache: dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:

        # Create cache key
        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    # Add cache management
    wrapper.cache = cache  # type: ignore
    wrapper.cache_clear = cache.clear  # type: ignore
    wrapper.cache_info = lambda: f"{len(cache)} entries"  # type: ignore

    return wrapper


# === Usage ===

@memoize
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(100))  # Fast! (cached)
print(fibonacci.cache_info())  # "101 entries"
fibonacci.cache_clear()
```

## TTL Cache

```python
import time
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """Cache entry with expiration"""

    value: Any
    expires_at: float


def ttl_cache(ttl: float = 60.0) -> Callable:
    """Cache with TTL (time-to-live)"""

    def decorator(func: Callable) -> Callable:

        cache: dict = {}

        @wraps(func)
        def wrapper(*args, **kwargs):

            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()

            # Check cache
            if key in cache:
                entry = cache[key]
                if entry.expires_at > now:
                    return entry.value
                else:
                    # Expired, remove
                    del cache[key]

            # Compute and cache
            value = func(*args, **kwargs)
            cache[key] = CacheEntry(value, now + ttl)

            return value

        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_info = lambda: f"{len(cache)} entries"  # type: ignore

        return wrapper

    return decorator


# === Usage ===

@ttl_cache(ttl=10)  # Cache for 10 seconds
def expensive_computation(n: int) -> int:
    """Expensive operation"""
    time.sleep(0.1)
    return n * n

print(expensive_computation(5))  # Computes (takes 0.1s)
print(expensive_computation(5))  # Cached (instant)

# After 10 seconds, cache expires
print(expensive_computation(5))  # Recomputes
```

## LRU Cache

```python
from collections import OrderedDict
from typing import Callable, Any

def lru_cache(max_size: int = 128) -> Callable:
    """Least Recently Used cache"""

    def decorator(func: Callable) -> Callable:

        cache: OrderedDict = OrderedDict()

        @wraps(func)
        def wrapper(*args, **kwargs):

            key = (args, tuple(sorted(kwargs.items())))

            # Cache hit
            if key in cache:
                # Move to end (most recently used)
                cache.move_to_end(key)
                return cache[key]

            # Cache miss
            result = func(*args, **kwargs)

            # Add to cache
            cache[key] = result

            # Evict if over capacity
            if len(cache) > max_size:
                cache.popitem(last=False)  # Remove oldest

            return result

        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_info = lambda: f"{len(cache)}/{max_size} entries"  # type: ignore

        return wrapper

    return decorator


# === Usage ===

@lru_cache(max_size=3)
def compute(x: int) -> int:
    return x * x

compute(1)  # Cache: [1]
compute(2)  # Cache: [1, 2]
compute(3)  # Cache: [1, 2, 3]
compute(4)  # Cache: [2, 3, 4] (1 evicted)
```

## Size-Based Cache

```python
import sys

def sized_cache(max_bytes: int = 1024 * 1024) -> Callable:
    """Cache with size limit in bytes"""

    def decorator(func: Callable) -> Callable:

        cache: dict = {}
        sizes: dict = {}

        @wraps(func)
        def wrapper(*args, **kwargs):

            key = (args, tuple(sorted(kwargs.items())))

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)

            # Calculate size
            size = sys.getsizeof(result)

            # Add to cache
            cache[key] = result
            sizes[key] = size

            # Evict if over capacity
            current_size = sum(sizes.values())
            while current_size > max_bytes and cache:
                oldest_key = next(iter(cache))
                current_size -= sizes.pop(oldest_key)
                del cache[oldest_key]

            return result

        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_info = lambda: f"{len(cache)} entries, {sum(sizes.values())} bytes"  # type: ignore

        return wrapper

    return decorator


# === Usage ===

@sized_cache(max_bytes=1024)  # 1KB cache
def load_data(key: str) -> bytes:
    """Load data (could be large)"""
    return open(f"{key}.dat", "rb").read()
```

## Async Cache

```python
import asyncio
from typing import Callable, Coroutine

def async_memoize(func: Callable[..., Coroutine]) -> Callable:

    cache: dict = {}

    @wraps(func)
    async def wrapper(*args, **kwargs):

        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache:
            cache[key] = await func(*args, **kwargs)

        return cache[key]

    wrapper.cache_clear = cache.clear  # type: ignore

    return wrapper


# === Usage ===

@async_memoize
async def fetch_user(id: int) -> dict:
    await asyncio.sleep(0.1)
    return {"id": id, "name": f"User{id}"}

async def main():
    user1 = await fetch_user(1)  # Fetches
    user2 = await fetch_user(1)  # Cached

asyncio.run(main())
```

## Cache Invalidation

```python
from typing import Callable, set

def invalidatable_cache(func: Callable) -> Callable:

    cache: dict = {}
    dependencies: dict[Any, set] = {}  # value -> keys that depend on it

    @wraps(func)
    def wrapper(*args, **kwargs):

        key = (args, tuple(sorted(kwargs.items())))

        if key in cache:
            return cache[key]

        result = func(*args, **kwargs)
        cache[key] = result

        # Track dependencies
        for arg in args:
            if arg not in dependencies:
                dependencies[arg] = set()
            dependencies[arg].add(key)

        return result

    def invalidate(*args):
        """Invalidate cache entries depending on args"""

        for arg in args:
            if arg in dependencies:
                for key in dependencies[arg]:
                    if key in cache:
                        del cache[key]
                del dependencies[arg]

    wrapper.cache_clear = cache.clear  # type: ignore
    wrapper.invalidate = invalidate  # type: ignore

    return wrapper


# === Usage ===

@invalidatable_cache
def get_user_posts(user_id: int) -> list:
    return fetch_posts(user_id)

posts1 = get_user_posts(1)

# Invalidate when user's posts change
get_user_posts.invalidate(1)

posts2 = get_user_posts(1)  # Recomputed
```

## Cache Decorator with Options

```python
class Cached:
    """Flexible caching decorator"""

    def __init__(
        self,
        ttl: float | None = None,
        max_size: int | None = None,
        key_func: Callable | None = None
    ):
        self.ttl = ttl
        self.max_size = max_size
        self.key_func = key_func or (lambda *args, **kw: (args, tuple(sorted(kw.items()))))

    def __call__(self, func: Callable) -> Callable:

        cache: dict = {}

        def get_key(*args, **kwargs):
            return self.key_func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):

            key = get_key(*args, **kwargs)

            # Check cache
            if key in cache:
                entry = cache[key]

                # Check expiration
                if self.ttl:
                    if isinstance(entry, tuple):
                        value, timestamp = entry
                        if time.time() - timestamp > self.ttl:
                            del cache[key]
                        else:
                            return value
                    else:
                        return entry
                else:
                    return entry

            # Compute
            result = func(*args, **kwargs)

            # Cache
            if self.ttl:
                cache[key] = (result, time.time())
            else:
                cache[key] = result

            # Evict if over capacity
            if self.max_size and len(cache) > self.max_size:
                cache.popitem(last=False)

            return result

        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_info = lambda: f"{len(cache)} entries"  # type: ignore

        return wrapper


# === Usage ===

@Cached(ttl=60, max_size=100)
def api_call(endpoint: str) -> dict:
    return requests.get(endpoint).json()

@Cached(key_func=lambda self, id: ("user", id))
class UserService:
    def get_user(self, id: int) -> dict:
        return db.find_user(id)
```

## DX Benefits

✅ **Fast**: Skip expensive recomputations
✅ **Flexible**: TTL, size limits, LRU
✅ **Automatic**: Transparent caching
✅ **Controllable**: Manual invalidation
✅ **Observable**: Cache statistics

## Best Practices

```python
# ✅ Good: Cache pure functions
@memoize
def expensive_calculation(x):
    ...

# ✅ Good: Use TTL for stale data
@ttl_cache(ttl=300)  # 5 minutes
def fetch_data():
    ...

# ✅ Good: Limit cache size
@lru_cache(max_size=1000)
def process(item):
    ...

# ❌ Bad: Cache impure functions
# Don't cache functions with side effects

# ❌ Bad: Cache everything
# Some computations are faster than cache lookup
```
