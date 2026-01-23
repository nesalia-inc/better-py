# Parallelizable: Parallel Processing Entities

**Parallelizable** is a protocol for collections that can be **processed in parallel** - executing operations concurrently for performance.

## Overview

```python
@runtime_checkable
class Parallelizable(Protocol[T]):
    """Collections that can be processed in parallel"""

    def par_map(self, func: Callable[[T], U]) -> 'Parallelizable[U]':
        """Map function over elements in parallel"""
        ...
```

## Core Concepts

### Sequential vs Parallel

```python
# Sequential: Process one at a time
items = [1, 2, 3, 4, 5]
results = [expensive_func(x) for x in items]  # 5 seconds (1s each)

# Parallel: Process all at once
results = items.par_map(expensive_func)  # 1 second (all at once)
```

## Implementations

### ParallelList

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import asyncio

@dataclass(frozen=True, slots=True)
class ParallelList(Generic[T]):
    """List with parallel operations"""

    _data: list[T]

    # === Thread-based parallelism ===

    def par_map(
        self,
        func: Callable[[T], U],
        max_workers: int | None = None
    ) -> 'ParallelList[U]':
        """Map function in parallel (thread pool)"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, self._data))
        return ParallelList(results)

    def par_map_async(
        self,
        func: Callable[[T], U],
        max_workers: int | None = None
    ) -> 'ParallelList[U]':
        """Map function in parallel, return futures"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(func, item) for item in self._data]
            results = [f.result() for f in as_completed(futures)]
        return ParallelList(results)

    # === Process-based parallelism ===

    def par_map_processes(
        self,
        func: Callable[[T], U],
        max_workers: int | None = None
    ) -> 'ParallelList[U]':
        """Map function in parallel (process pool)"""
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, self._data))
        return ParallelList(results)

    # === Parallel filtering ===

    def par_filter(
        self,
        predicate: Callable[[T], bool],
        max_workers: int | None = None
    ) -> 'ParallelList[T]':
        """Filter in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            keep_flags = list(executor.map(predicate, self._data))

        results = [item for item, keep in zip(self._data, keep_flags) if keep]
        return ParallelList(results)

    # === Parallel reduce ===

    def par_reduce(
        self,
        func: Callable[[T, T], T],
        max_workers: int | None = None
    ) -> T:
        """Reduce in parallel (map-reduce pattern)"""
        import math

        # Split into chunks
        chunk_size = max(1, len(self._data) // (max_workers or 4))
        chunks = [
            self._data[i:i + chunk_size]
            for i in range(0, len(self._data), chunk_size)
        ]

        # Reduce each chunk in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            chunk_results = list(executor.map(
                lambda chunk: reduce(func, chunk),
                chunks
            ))

        # Combine chunk results
        return reduce(func, chunk_results)

    # === Parallel flat_map ===

    def par_flat_map(
        self,
        func: Callable[[T], list[U]],
        max_workers: int | None = None
    ) -> 'ParallelList[U]':
        """Flat map in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results_lists = list(executor.map(func, self._data))

        # Flatten
        results = []
        for result_list in results_lists:
            results.extend(result_list)

        return ParallelList(results)

    # === Parallel for_each ===

    def par_for_each(
        self,
        func: Callable[[T], None],
        max_workers: int | None = None
    ) -> None:
        """Execute function for each element in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(func, self._data))

    # === Partition operations ===

    def par_partition(
        self,
        predicate: Callable[[T], bool],
        max_workers: int | None = None
    ) -> tuple['ParallelList[T]', 'ParallelList[T]']:
        """Partition in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            flags = list(executor.map(predicate, self._data))

        matching = [item for item, flag in zip(self._data, flags) if flag]
        non_matching = [item for item, flag in zip(self._data, flags) if not flag]

        return ParallelList(matching), ParallelList(non_matching)

    # === Parallel group_by ===

    def par_group_by(
        self,
        key_func: Callable[[T], Any],
        max_workers: int | None = None
    ) -> dict[Any, 'ParallelList[T]']:
        """Group by in parallel (compute keys in parallel)"""
        # Compute keys in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            keys = list(executor.map(key_func, self._data))

        # Group sequentially (fast)
        groups = {}
        for item, key in zip(self._data, keys):
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        return {k: ParallelList(v) for k, v in groups.items()}

    # === Conversion ===

    def to_list(self) -> list[T]:
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
```

#### Usage Examples

```python
# Create
items = ParallelList([1, 2, 3, 4, 5])

# Parallel map
doubled = items.par_map(lambda x: x * 2)
# ParallelList([2, 4, 6, 8, 10])

# Parallel filter
evens = items.par_filter(lambda x: x % 2 == 0)
# ParallelList([2, 4])

# Parallel reduce (map-reduce)
sum_ = items.par_reduce(lambda a, b: a + b)  # 15

# Parallel flat_map
result = items.par_flat_map(lambda x: [x, x * 2])
# ParallelList([1, 2, 2, 4, 3, 6, 4, 8, 5, 10])

# Parallel for_each
items.par_for_each(print)  # Prints all (order may vary)
```

### AsyncList

```python
@dataclass(frozen=True, slots=True)
class AsyncList(Generic[T]):
    """List with async parallel operations"""

    _data: list[T]

    async def par_map(
        self,
        func: Callable[[T], Awaitable[U]]
    ) -> 'AsyncList[U]':
        """Map async function in parallel"""
        results = await asyncio.gather(
            *[func(item) for item in self._data]
        )
        return AsyncList(results)

    async def par_filter(
        self,
        func: Callable[[T], Awaitable[bool]]
    ) -> 'AsyncList[T]':
        """Filter with async predicate in parallel"""
        flags = await asyncio.gather(
            *[func(item) for item in self._data]
        )

        results = [
            item for item, flag in zip(self._data, flags)
            if flag
        ]
        return AsyncList(results)

    async def par_for_each(
        self,
        func: Callable[[T], Awaitable[None]]
    ) -> None:
        """Execute async function for each element in parallel"""
        await asyncio.gather(
            *[func(item) for item in self._data]
        )

    async def sequence(
        self,
        async_funcs: list[Callable[[], Awaitable[T]]
    ) -> 'AsyncList[T]':
        """Run async functions in parallel"""
        results = await asyncio.gather(
            *[func() for func in async_funcs]
        )
        return AsyncList(results)

    # === Parallel map with concurrency limit ===

    async def par_map_concurrent(
        self,
        func: Callable[[T], Awaitable[U]],
        concurrency: int = 10
    ) -> 'AsyncList[U]':
        """Map with concurrency limit"""
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_func(item):
            async with semaphore:
                return await func(item)

        results = await asyncio.gather(
            *[bounded_func(item) for item in self._data]
        )
        return AsyncList(results)

    def to_list(self) -> list[T]:
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
```

#### Usage Examples

```python
# Async operations
async def fetch_user(id: int) -> User:
    await asyncio.sleep(0.1)  # Simulate network
    return User(id, f"User{id}")

ids = AsyncList([1, 2, 3, 4, 5])

# Parallel fetch
users = await ids.par_map(fetch_user)
# AsyncList([User(1), User(2), User(3), User(4), User(5)])

# Parallel filter
adults = await ids.par_filter(lambda id: fetch_user(id).then(lambda u: u.age >= 18))

# Concurrency-limited map
users = await ids.par_map_concurrent(fetch_user, concurrency=2)
```

### ParallelDict

```python
@dataclass(frozen=True, slots=True)
class ParallelDict(Generic[K, V]):
    """Dict with parallel operations"""

    _data: dict[K, V]

    def par_map_values(
        self,
        func: Callable[[V], U],
        max_workers: int | None = None
    ) -> 'ParallelDict[K, U]':
        """Map values in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            items = list(self._data.items())
            mapped_values = list(executor.map(
                lambda item: (item[0], func(item[1])),
                items
            ))

        return ParallelDict(dict(mapped_values))

    def par_map_keys(
        self,
        func: Callable[[K], U],
        max_workers: int | None = None
    ) -> 'ParallelDict[U, V]':
        """Map keys in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            items = list(self._data.items())
            mapped_items = list(executor.map(
                lambda item: (func(item[0]), item[1]),
                items
            ))

        return ParallelDict(dict(mapped_items))

    def par_filter_values(
        self,
        predicate: Callable[[V], bool],
        max_workers: int | None = None
    ) -> 'ParallelDict[K, V]':
        """Filter by values in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            items = list(self._data.items())
            flags = list(executor.map(
                lambda item: predicate(item[1]),
                items
            ))

        return ParallelDict({
            k: v for (k, v), flag in zip(items, flags) if flag
        })

    def to_dict(self) -> dict[K, V]:
        return self._data.copy()
```

## Advanced Patterns

### Batch Processing

```python
@dataclass(frozen=True, slots=True)
class ParallelList(Generic[T]):
    _data: list[T]

    def par_map_batches(
        self,
        func: Callable[[list[T]], list[U]],
        batch_size: int = 100,
        max_workers: int | None = None
    ) -> 'ParallelList[U]':
        """Map in batches"""
        # Split into batches
        batches = [
            self._data[i:i + batch_size]
            for i in range(0, len(self._data), batch_size)
        ]

        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            batch_results = list(executor.map(func, batches))

        # Flatten results
        results = []
        for batch_result in batch_results:
            results.extend(batch_result)

        return ParallelList(results)
```

### Parallel Retry

```python
@dataclass
class ParallelRetry:
    """Retry failed operations in parallel"""

    max_attempts: int = 3

    def par_map_with_retry(
        self,
        items: list[T],
        func: Callable[[T], U],
        max_workers: int | None = None
    ) -> list[Result[U, Exception]]:
        """Map with retry for failures"""

        def func_with_retry(item):
            last_error = None
            for attempt in range(self.max_attempts):
                try:
                    return Ok(func(item))
                except Exception as e:
                    last_error = e
                    if attempt < self.max_attempts - 1:
                        time.sleep(0.1 * (2 ** attempt))
            return Error(last_error)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func_with_retry, items))

        return results
```

### Parallel Processing with Progress

```python
@dataclass
class ParallelProgress:
    """Parallel processing with progress tracking"""

    def par_map_with_progress(
        self,
        items: list[T],
        func: Callable[[T], U],
        progress_callback: Callable[[int, int], None] | None = None,
        max_workers: int | None = None
    ) -> list[U]:
        """Map with progress callback"""

        results = [None] * len(items)
        completed = 0

        def with_index(item):
            return item

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(func, item): i
                for i, item in enumerate(items)
            }

            for future in as_completed(futures):
                index = futures[future]
                results[index] = future.result()
                completed += 1

                if progress_callback:
                    progress_callback(completed, len(items))

        return results
```

## Protocol Compliance

```python
@runtime_checkable
class Parallelizable(Protocol[T]):
    def par_map(self, func): ...

class CustomParallelizable:
    def __init__(self, items):
        self._items = items

    def par_map(self, func, max_workers=None):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, self._items))
        return CustomParallelizable(results)

# CustomParallelizable is Parallelizable!
isinstance(CustomParallelizable([]), Parallelizable)  # True
```

## Best Practices

### ✅ Do: Use thread pool for I/O-bound

```python
# Good: I/O-bound operations
await AsyncList(urls).par_map(fetch_url)  # Threads work well
```

### ✅ Do: Use process pool for CPU-bound

```python
# Good: CPU-bound operations
ParallelList(data).par_map_processes(expensive_computation)
```

### ❌ Don't: Over-parallelize

```python
# Bad: Too many workers
items.par_map(func, max_workers=1000)  # Overhead too high

# Good: Let executor decide
items.par_map(func)  # Default is optimal
```

## Summary

**Parallelizable** protocol:
- ✅ Thread-based parallelism (`par_map`)
- ✅ Process-based parallelism (`par_map_processes`)
- ✅ Async parallelism (`par_map` in AsyncList)
- ✅ Concurrency limiting
- ✅ Progress tracking
- ✅ Batch processing

**Key benefit**: **Automatic parallelization** with **minimal code changes**.

---

**Next**: See [Resilient](./10-resilient.md) for resilient entities.
