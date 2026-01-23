# Cacheable: Objects That Can Be Cached

**Cacheable** is a protocol for objects that can be **cached** - providing cache keys and serialization for efficient storage and retrieval.

## Overview

```python
@runtime_checkable
class Cacheable(Protocol[T]):
    """Objects that can be cached"""

    @property
    def cache_key(self) -> str:
        """Unique key for caching"""
        ...

    def to_cache_repr(self) -> bytes | str:
        """Serialize for cache storage"""
        ...

    @classmethod
    def from_cache_repr(cls, data: bytes | str) -> T:
        """Deserialize from cache"""
        ...
```

## Core Concepts

### Cache Key

```python
# Cache key uniquely identifies cached object
@dataclass
class User(Cacheable):
    id: int
    name: str

    @property
    def cache_key(self) -> str:
        return f"user:{self.id}"
```

### Cache Representation

```python
# Convert to/from cache-friendly format
user = User(1, "Alice")
cache_repr = user.to_cache_repr()  # JSON, pickle, etc.
restored = User.from_cache_repr(cache_repr)  # User(1, "Alice")
```

## Implementations

### Cacheable Entity

```python
from dataclasses import dataclass, asdict
import json
import pickle
import hashlib
import time

@dataclass(frozen=True, slots=True)
class CacheableEntity(Generic[T]):
    """Base class for cacheable entities"""

    @property
    def cache_key(self) -> str:
        """Generate cache key from all fields"""
        # Use hash of values for unique key
        values = str(asdict(self).values())
        hash_val = hashlib.md5(values.encode()).hexdigest()
        return f"{self.__class__.__name__}:{hash_val}"

    def to_cache_repr(self) -> bytes:
        """Serialize to bytes (using pickle by default)"""
        return pickle.dumps(self)

    @classmethod
    def from_cache_repr(cls, data: bytes) -> T:
        """Deserialize from bytes"""
        return pickle.loads(data)

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> T:
        """Deserialize from JSON"""
        return cls(**json.loads(data))
```

### Cacheable User

```python
@dataclass(frozen=True, slots=True)
class User:
    """Cacheable user"""

    id: int
    name: str
    email: str
    created_at: str

    @property
    def cache_key(self) -> str:
        """User cache key"""
        return f"user:{self.id}"

    def to_cache_repr(self) -> bytes:
        """Serialize to bytes"""
        return pickle.dumps(asdict(self))

    @classmethod
    def from_cache_repr(cls, data: bytes) -> 'User':
        """Deserialize from bytes"""
        return cls(**pickle.loads(data))

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at
        })

    @classmethod
    def from_json(cls, data: str) -> 'User':
        """Deserialize from JSON"""
        return cls(**json.loads(data))
```

#### Usage Examples

```python
# Create
user = User(1, "Alice", "alice@example.com", "2024-01-15")

# Get cache key
key = user.cache_key  # "user:1"

# Serialize
cache_repr = user.to_cache_repr()  # bytes

# Deserialize
restored = User.from_cache_repr(cache_repr)
# User(1, "Alice", "alice@example.com", "2024-01-15")

# JSON
json_str = user.to_json()
restored = User.from_json(json_str)
```

### CacheableDict

```python
@dataclass(frozen=True, slots=True)
class CacheableDict(Generic[K, V]):
    """Cacheable dictionary"""

    _data: dict[K, V]
    _ttl: int = 300  # Time to live in seconds

    @property
    def cache_key(self) -> str:
        """Generate key from dict contents"""
        # Sort keys for consistent hash
        items = sorted(self._data.items())
        hash_val = hashlib.md5(str(items).encode()).hexdigest()
        return f"dict:{hash_val}"

    def to_cache_repr(self) -> bytes:
        """Include TTL in cache"""
        cache_data = {
            "data": self._data,
            "ttl": self._ttl,
            "created_at": time.time()
        }
        return pickle.dumps(cache_data)

    @classmethod
    def from_cache_repr(cls, data: bytes) -> 'CacheableDict[K, V]':
        """Deserialize with TTL check"""
        cache_data = pickle.loads(data)

        # Check TTL
        created_at = cache_data.get("created_at", 0)
        ttl = cache_data.get("ttl", 0)

        if time.time() - created_at > ttl:
            raise ValueError("Cache entry expired")

        return cls(
            cache_data["data"],
            ttl=cache_data.get("ttl", 300)
        )

    def is_expired(self) -> bool:
        """Check if cache entry expired"""
        # Requires storing created_at separately
        return False

    def to_dict(self) -> dict[K, V]:
        return self._data.copy()
```

### CacheableList

```python
@dataclass(frozen=True, slots=True)
class CacheableList(Generic[T]):
    """Cacheable list"""

    _items: list[T]
    _ttl: int = 300

    @property
    def cache_key(self) -> str:
        """Generate key from list contents"""
        hash_val = hashlib.md5(str(self._items).encode()).hexdigest()
        return f"list:{hash_val}"

    def to_cache_repr(self) -> bytes:
        """Serialize list"""
        cache_data = {
            "items": self._items,
            "ttl": self._ttl,
            "created_at": time.time()
        }
        return pickle.dumps(cache_data)

    @classmethod
    def from_cache_repr(cls, data: bytes) -> 'CacheableList[T]':
        """Deserialize list"""
        cache_data = pickle.loads(data)
        return cls(
            cache_data["items"],
            ttl=cache_data.get("ttl", 300)
        )

    def to_list(self) -> list[T]:
        return self._items.copy()
```

## Cache Operations

### CacheBackend Protocol

```python
@runtime_checkable
class CacheBackend(Protocol):
    """Cache storage backend"""

    def get(self, key: str) -> bytes | None:
        """Get from cache"""
        ...

    def set(self, key: str, value: bytes, ttl: int | None = None) -> None:
        """Set in cache"""
        ...

    def delete(self, key: str) -> None:
        """Delete from cache"""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        ...
```

### In-Memory Cache

```python
@dataclass
class InMemoryCache:
    """Simple in-memory cache"""

    _data: dict[str, tuple[bytes, float, int | None]] = field(default_factory=dict)

    def get(self, key: str) -> bytes | None:
        """Get from cache"""
        if key not in self._data:
            return None

        value, created_at, ttl = self._data[key]

        # Check TTL
        if ttl and time.time() - created_at > ttl:
            del self._data[key]
            return None

        return value

    def set(self, key: str, value: bytes, ttl: int | None = None) -> None:
        """Set in cache"""
        self._data[key] = (value, time.time(), ttl)

    def delete(self, key: str) -> None:
        """Delete from cache"""
        self._data.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.get(key) is not None

    def clear(self) -> None:
        """Clear all cache"""
        self._data.clear()
```

### Cache Decorator

```python
def cached(ttl: int = 300, key_func: Callable | None = None):
    """Cache function results"""
    cache = InMemoryCache()

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return pickle.loads(cached_value)

            # Call function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(key, pickle.dumps(result), ttl)

            return result

        return wrapper
    return decorator

# Usage
@cached(ttl=60)
def expensive_computation(x: int) -> int:
    print(f"Computing {x}...")
    return x ** 2

# First call: Computes
result1 = expensive_computation(5)  # "Computing 5..." → 25

# Second call: Cached
result2 = expensive_computation(5)  # 25 (no print)
```

### Cached Async Function

```python
def cached_async(ttl: int = 300, key_func: Callable | None = None):
    """Cache async function results"""
    cache = InMemoryCache()

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            # Try cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return pickle.loads(cached_value)

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            cache.set(key, pickle.dumps(result), ttl)

            return result

        return wrapper
    return decorator

# Usage
@cached_async(ttl=60)
async def fetch_user(id: int) -> User:
    print(f"Fetching user {id}...")
    return await db.query_user(id)

# First call: Fetches
user1 = await fetch_user(1)  # "Fetching user 1..." → User(1, ...)

# Second call: Cached
user2 = await fetch_user(1)  # User(1, ...) (no print)
```

### CacheAside Pattern

```python
class CacheAside:
    """Cache-aside pattern: check cache, load if miss"""

    def __init__(self, backend: CacheBackend):
        self.backend = backend

    def get(self, key: str, load_func: Callable[[], T]) -> T:
        """Get from cache or load"""
        # Try cache
        cached = self.backend.get(key)
        if cached is not None:
            return pickle.loads(cached)

        # Cache miss - load
        value = load_func()

        # Store in cache
        self.backend.set(key, pickle.dumps(value))

        return value

    def get_or_load(
        self,
        key: str,
        load_func: Callable[[], T],
        ttl: int | None = None
    ) -> T:
        """Get from cache or load with TTL"""
        return self.get(key, load_func)
```

#### Usage Examples

```python
cache = InMemoryCache()
cache_aside = CacheAside(cache)

def load_user(id: int) -> User:
    """Load user from database"""
    print(f"Loading user {id} from DB...")
    return db.query_user(id)

# First call: Loads from DB
user1 = cache_aside.get_or_load(f"user:1", lambda: load_user(1))
# "Loading user 1 from DB..."

# Second call: Loads from cache
user2 = cache_aside.get_or_load(f"user:1", lambda: load_user(1))
# (no print - cached)
```

## Advanced Patterns

### Multi-Level Cache

```python
@dataclass
class MultiLevelCache:
    """Multi-level cache (L1: memory, L2: disk)"""

    l1: InMemoryCache = field(default_factory=InMemoryCache)
    l2: DiskCache = field(default_factory=DiskCache)

    def get(self, key: str) -> bytes | None:
        """Check L1, then L2"""
        # L1 cache
        value = self.l1.get(key)
        if value is not None:
            return value

        # L2 cache
        value = self.l2.get(key)
        if value is not None:
            # Promote to L1
            self.l1.set(key, value)
            return value

        return None

    def set(self, key: str, value: bytes, ttl: int | None = None) -> None:
        """Set in both L1 and L2"""
        self.l1.set(key, value, ttl)
        self.l2.set(key, value, ttl)
```

### Cache Invalidation

```python
@dataclass
class InvalidatingCache:
    """Cache with invalidation support"""

    _backend: CacheBackend
    _tags: dict[str, set[str]] = field(default_factory=dict)

    def set(self, key: str, value: bytes, tags: list[str] = [], ttl: int | None = None):
        """Set with tags for invalidation"""
        self._backend.set(key, value, ttl)

        # Track tags
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(key)

    def invalidate_tag(self, tag: str):
        """Invalidate all entries with tag"""
        if tag in self._tags:
            for key in self._tags[tag]:
                self._backend.delete(key)
            del self._tags[tag]

    def invalidate_all(self):
        """Invalidate all cache"""
        self._backend.clear()
        self._tags.clear()
```

## Protocol Compliance

```python
@runtime_checkable
class Cacheable(Protocol[T]):
    @property
    def cache_key(self) -> str: ...
    def to_cache_repr(self) -> bytes: ...
    @classmethod
    def from_cache_repr(cls, data: bytes) -> T: ...

class CustomCacheable:
    def __init__(self, id, value):
        self.id = id
        self.value = value

    @property
    def cache_key(self) -> str:
        return f"custom:{self.id}"

    def to_cache_repr(self) -> bytes:
        return pickle.dumps({"id": self.id, "value": self.value})

    @classmethod
    def from_cache_repr(cls, data: bytes):
        restored = pickle.loads(data)
        return cls(restored["id"], restored["value"])

# CustomCacheable is Cacheable!
isinstance(CustomCacheable(0, 0), Cacheable)  # True
```

## Best Practices

### ✅ Do: Use meaningful cache keys

```python
# Good: Hierarchical keys
@property
def cache_key(self) -> str:
    return f"user:{self.id}:profile"

# Bad: Random hashes only
@property
def cache_key(self) -> str:
    return hashlib.md5(str(self).encode()).hexdigest()
```

### ✅ Do: Set appropriate TTL

```python
# Good: Short TTL for frequently-changing data
@cached(ttl=60)  # 1 minute
def get_stock_price(symbol: str) -> float: ...

# Good: Long TTL for rarely-changing data
@cached(ttl=3600)  # 1 hour
def get_country_code(name: str) -> str: ...
```

### ❌ Don't: Cache too much

```python
# Bad: Caching everything
@cached(ttl=3600)
def process_unique_request(request_id: str) -> Response:
    ...  # Never cache unique requests!
```

## Summary

**Cacheable** protocol:
- ✅ Unique cache keys via `cache_key`
- ✅ Serialization via `to_cache_repr()` / `from_cache_repr()`
- ✅ TTL support
- ✅ Multi-level caching
- ✅ Tag-based invalidation
- ✅ Decorators for functions

**Key benefit**: **Transparent caching** with **automatic invalidation**.

---

**Next**: See [Parallelizable](./09-parallelizable.md) for parallelizable entities.
