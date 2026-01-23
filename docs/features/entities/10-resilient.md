# Resilient: Fault-Tolerant Operations

**Resilient** is a protocol/mixin for operations that can **withstand failures** - implementing retry, timeout, circuit breaking, and fallback strategies.

## Overview

```python
@dataclass
class Resilient(Generic[T]):
    """Mixin for resilient operations"""

    operation: Callable[[], T]
    retry_policy: 'RetryPolicy' = field(default_factory=RetryPolicy)
    timeout_policy: 'TimeoutPolicy' = field(default_factory=TimeoutPolicy)
    circuit_breaker: 'CircuitBreaker' = field(default_factory=CircuitBreaker)

    def execute(self) -> Result[T, Exception]:
        """Execute with all resilience strategies"""
        ...
```

## Core Concepts

### Resilience Patterns

- **Retry**: Retry failed operations
- **Timeout**: Fail fast if operation takes too long
- **Circuit Breaker**: Stop trying if service is down
- **Fallback**: Use alternative on failure
- **Bulkhead**: Limit concurrent operations

## Implementations

### RetryPolicy

```python
from dataclasses import dataclass, field
import time

@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Retry strategy"""

    max_attempts: int = 3
    base_delay: float = 0.1  # Seconds
    max_delay: float = 10.0
    backoff: Callable[[int], float] = lambda n: min(0.1 * (2 ** n), 10.0)
    retry_on: tuple[Exception, ...] = (Exception,)
    retry_if: Callable[[Exception], bool] | None = None

    def with_max_attempts(self, n: int) -> 'RetryPolicy':
        """Return new policy with different max attempts"""
        return Replace(self, max_attempts=n)

    def with_backoff(self, backoff: Callable[[int], float]) -> 'RetryPolicy':
        """Return new policy with different backoff"""
        return Replace(self, backoff=backoff)

    def with_retry_on(self, *exceptions: Exception) -> 'RetryPolicy':
        """Return new policy retrying on specific exceptions"""
        return Replace(self, retry_on=exceptions)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Check if should retry"""
        if attempt >= self.max_attempts:
            return False

        if not isinstance(error, self.retry_on):
            return False

        if self.retry_if and not self.retry_if(error):
            return False

        return True

    def get_delay(self, attempt: int) -> float:
        """Get delay for attempt"""
        return self.backoff(attempt)
```

#### Usage Examples

```python
# Default retry
policy = RetryPolicy()
# max_attempts=3, exponential backoff

# Custom retry
policy = (
    RetryPolicy()
    .with_max_attempts(5)
    .with_backoff(lambda n: n * 0.5)  # Linear backoff
    .with_retry_on(ConnectionError, TimeoutError)
)

# Usage
for attempt in range(policy.max_attempts):
    try:
        result = operation()
        break
    except Exception as e:
        if not policy.should_retry(attempt, e):
            raise
        time.sleep(policy.get_delay(attempt))
```

### TimeoutPolicy

```python
@dataclass(frozen=True, slots=True)
class TimeoutPolicy:
    """Timeout strategy"""

    timeout: float = 30.0  # Seconds
    on_timeout: Callable[[], Exception] = lambda: TimeoutError("Operation timed out")

    def with_timeout(self, seconds: float) -> 'TimeoutPolicy':
        """Return new policy with different timeout"""
        return Replace(self, timeout=seconds)

    def with_on_timeout(self, exception: Exception) -> 'TimeoutPolicy':
        """Return new policy with different timeout exception"""
        return Replace(self, on_timeout=lambda: exception)
```

### CircuitBreaker

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

@dataclass
class CircuitBreaker:
    """Circuit breaker pattern"""

    failure_threshold: int = 5
    success_threshold: int = 2  # For half-open state
    timeout: timedelta = timedelta(seconds=60)

    def __post_init__(self):
        self._failures = 0
        self._successes = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED

    def call[T](
        self,
        operation: Callable[[], Result[T, Exception]]
    ) -> Result[T, Exception]:
        """Execute operation through circuit breaker"""

        # Check state
        if self._state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self._state = CircuitState.HALF_OPEN
            else:
                return Error(CircuitBreakerError("Circuit is OPEN"))

        # Execute operation
        result = operation()

        # Handle result
        if result.is_error():
            self._on_failure()
        else:
            self._on_success()

        return result

    def _should_attempt_recovery(self) -> bool:
        if self._last_failure_time is None:
            return True
        return datetime.now() - self._last_failure_time >= self.timeout

    def _on_failure(self):
        self._failures += 1
        self._successes = 0
        self._last_failure_time = datetime.now()

        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def _on_success(self):
        self._failures = 0
        self._successes += 1

        if self._state == CircuitState.HALF_OPEN:
            if self._successes >= self.success_threshold:
                self._state = CircuitState.CLOSED

    @property
    def state(self) -> CircuitState:
        return self._state
```

#### Usage Examples

```python
breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=timedelta(seconds=60)
)

def call_service() -> Result[Response, Exception]:
    return breaker.call(lambda: http_get(api_url))

# First 5 failures: Circuit opens
# After 60s: Half-open (test with 2 requests)
# If success: Closes
# If failure: Opens again
```

### Resilient Operation

```python
@dataclass
class ResilientOperation(Generic[T]):
    """Operation with resilience"""

    operation: Callable[[], Result[T, Exception]]

    # Policies
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = field(default_factory=TimeoutPolicy)
    circuit_breaker: CircuitBreaker | None = None

    # Fallback
    fallback: Callable[[], Result[T, Exception]] | None = None

    def execute(self) -> Result[T, Exception]:
        """Execute with all resilience strategies"""

        # Circuit breaker
        if self.circuit_breaker:
            def wrapped():
                return self._execute_with_retry()
            return self.circuit_breaker.call(wrapped)
        else:
            return self._execute_with_retry()

    def _execute_with_retry(self) -> Result[T, Exception]:
        """Execute with retry"""
        last_error = None

        for attempt in range(self.retry_policy.max_attempts):
            # Execute with timeout
            result = self._execute_with_timeout()

            if result.is_ok():
                return result

            last_error = result.error

            # Check if should retry
            if not self.retry_policy.should_retry(attempt, last_error):
                break

            # Wait before retry
            delay = self.retry_policy.get_delay(attempt)
            time.sleep(delay)

        # All retries failed - try fallback
        if self.fallback:
            return self.fallback()

        return Error(last_error)

    def _execute_with_timeout(self) -> Result[T, Exception]:
        """Execute with timeout"""
        import signal

        def timeout_handler(signum, frame):
            raise self.timeout_policy.on_timeout()

        # Set alarm
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.timeout_policy.timeout))

        try:
            result = self.operation()
            signal.alarm(0)  # Cancel alarm
            return result
        except Exception as e:
            signal.alarm(0)
            return Error(e)
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    def with_retry(self, policy: RetryPolicy) -> 'ResilientOperation[T]':
        """Return new operation with retry policy"""
        return Replace(self, retry_policy=policy)

    def with_timeout(self, policy: TimeoutPolicy) -> 'ResilientOperation[T]':
        """Return new operation with timeout policy"""
        return Replace(self, timeout_policy=policy)

    def with_circuit_breaker(self, breaker: CircuitBreaker) -> 'ResilientOperation[T]':
        """Return new operation with circuit breaker"""
        return Replace(self, circuit_breaker=breaker)

    def with_fallback(self, fallback: Callable[[], Result[T, Exception]]) -> 'ResilientOperation[T]':
        """Return new operation with fallback"""
        return Replace(self, fallback=fallback)
```

#### Usage Examples

```python
# Basic resilient operation
operation = ResilientOperation(
    operation=lambda: fetch_user(1)
)

result = operation.execute()

# With custom policies
operation = (
    ResilientOperation(lambda: fetch_user(1))
    .with_retry(RetryPolicy(max_attempts=5))
    .with_timeout(TimeoutPolicy(timeout=10.0))
    .with_circuit_breaker(CircuitBreaker(failure_threshold=3))
    .with_fallback(lambda: Ok(cached_user))
)

result = operation.execute()
```

### Bulkhead Pattern

```python
@dataclass
class Bulkhead:
    """Limit concurrent operations"""

    max_concurrent: int = 10

    def __post_init__(self):
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._active = 0

    async def call[T](
        self,
        operation: Callable[[], Awaitable[T]]
    ) -> Result[T, Exception]:
        """Execute with concurrency limit"""
        async with self._semaphore:
            self._active += 1
            try:
                result = await operation()
                return Ok(result)
            except Exception as e:
                return Error(e)
            finally:
                self._active -= 1

    @property
    def active_count(self) -> int:
        return self._active
```

### Retry Decorator

```python
def resilient_retry(
    max_attempts: int = 3,
    backoff: Callable[[int], float] = lambda n: 0.1 * (2 ** n),
    retry_on: tuple[Exception, ...] = (Exception,)
):
    """Decorator for resilient retry"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            policy = RetryPolicy(
                max_attempts=max_attempts,
                backoff=backoff,
                retry_on=retry_on
            )

            last_error = None
            for attempt in range(policy.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if not policy.should_retry(attempt, e):
                        break
                    time.sleep(policy.get_delay(attempt))

            raise last_error
        return wrapper
    return decorator

# Usage
@resilient_retry(max_attempts=5, retry_on=(ConnectionError, TimeoutError))
def fetch_api(url: str) -> dict:
    return http_get(url)
```

### Async Resilient Operation

```python
@dataclass
class AsyncResilientOperation(Generic[T]):
    """Async operation with resilience"""

    operation: Callable[[], Awaitable[Result[T, Exception]]]

    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = field(default_factory=TimeoutPolicy)

    async def execute(self) -> Result[T, Exception]:
        """Execute with resilience"""
        last_error = None

        for attempt in range(self.retry_policy.max_attempts):
            # Execute with timeout
            result = await self._execute_with_timeout()

            if result.is_ok():
                return result

            last_error = result.error

            if not self.retry_policy.should_retry(attempt, last_error):
                break

            # Wait before retry
            delay = self.retry_policy.get_delay(attempt)
            await asyncio.sleep(delay)

        return Error(last_error)

    async def _execute_with_timeout(self) -> Result[T, Exception]:
        """Execute with timeout"""
        try:
            result = await asyncio.wait_for(
                self.operation(),
                timeout=self.timeout_policy.timeout
            )
            return result
        except asyncio.TimeoutError:
            return Error(self.timeout_policy.on_timeout())
        except Exception as e:
            return Error(e)
```

## Advanced Patterns

### Fallback Chain

```python
@dataclass
class FallbackChain(Generic[T]):
    """Try multiple operations in sequence"""

    operations: list[Callable[[], Result[T, Exception]]]

    def execute(self) -> Result[T, Exception]:
        """Try each operation until success"""
        last_error = None

        for operation in self.operations:
            result = operation()
            if result.is_ok():
                return result
            last_error = result.error

        return Error(last_error)

    @classmethod
    def create(cls, *operations: Callable[[], Result[T, Exception]]) -> 'FallbackChain[T]':
        """Create fallback chain"""
        return cls(list(operations))

# Usage
chain = FallbackChain.create(
    lambda: fetch_from_cache(),
    lambda: fetch_from_db(),
    lambda: fetch_from_api()
)

result = chain.execute()
```

### Hedging

```python
@dataclass
class HedgingOperation(Generic[T]):
    """Execute same operation on multiple backends, use first result"""

    operations: list[Callable[[], Result[T, Exception]]]
    delay: float = 0.1  # Delay between starting each operation

    def execute(self) -> Result[T, Exception]:
        """Execute all operations, return first success"""
        import threading
        import queue

        results = queue.Queue()

        def worker(operation):
            result = operation()
            results.put(result)

        # Start operations with delay
        threads = []
        for i, operation in enumerate(self.operations):
            if i > 0:
                time.sleep(self.delay)
            thread = threading.Thread(target=worker, args=(operation,))
            thread.start()
            threads.append(thread)

        # Wait for first success
        for _ in range(len(self.operations)):
            result = results.get()
            if result.is_ok():
                return result

        # All failed
        return result
```

## Best Practices

### ✅ Do: Combine resilience patterns

```python
# Good: Layer multiple strategies
operation = (
    ResilientOperation(fetch_data)
    .with_retry(RetryPolicy(max_attempts=3))
    .with_timeout(TimeoutPolicy(timeout=5.0))
    .with_circuit_breaker(CircuitBreaker())
)
```

### ✅ Do: Use appropriate backoff

```python
# Good: Exponential backoff for retries
RetryPolicy(backoff=lambda n: min(0.1 * (2 ** n), 10))

# Good: Jitter to avoid thundering herd
import random
RetryPolicy(backoff=lambda n: 0.1 * (2 ** n) + random.random() * 0.1)
```

### ❌ Don't: Retry indefinitely

```python
# Bad: No limit on retries
for attempt in count():  # Infinite!
    try:
        return operation()
    except:
        pass

# Good: Limited retries
for attempt in range(3):
    try:
        return operation()
    except:
        if attempt == 2:
            raise
```

## Summary

**Resilient** patterns:
- ✅ **Retry**: Retry failed operations
- ✅ **Timeout**: Fail fast on long operations
- ✅ **Circuit Breaker**: Stop failing fast
- ✅ **Fallback**: Use alternatives
- ✅ **Bulkhead**: Limit concurrency
- ✅ **Hedging**: Race multiple backends

**Key benefit**: **Automatic fault tolerance** with **configurable policies**.

---

**Next**: See [Configurable](./11-configurable.md) for configurable entities.
