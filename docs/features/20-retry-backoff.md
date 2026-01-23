# Retry with Backoff - Resilient Operations

Automatic retry with exponential backoff for handling transient failures.

## Overview

Retry mechanisms enable:
- Handle transient failures automatically
- Exponential backoff for resilience
- Jitter to avoid thundering herd
- Max attempts limits
- Custom retry conditions

## Basic Retry Decorator

```python
import time
from typing import Callable, TypeVar, Type, Tuple
from functools import wraps
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class RetryConfig:
    """Retry configuration"""

    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 5.0
    exponential_base: float = 2.0
    jitter: bool = True


def retry(
    max_attempts: int = 3,
    on: Tuple[Type[Exception], ...] = (Exception,),
    backoff: float = 0.1,
    max_delay: float = 5.0
) -> Callable:
    """Retry decorator with exponential backoff"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except on as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(backoff * (2 ** attempt), max_delay)

                        # Add jitter
                        import random
                        if RetryConfig().jitter:
                            delay = delay * (0.5 + random.random())

                        time.sleep(delay)

            raise last_exception  # type: ignore

        return wrapper

    return decorator


# === Usage ===

@retry(max_attempts=3, on=(ConnectionError,), backoff=0.5)
def fetch_api(url: str) -> dict:
    """Fetch from API with automatic retry"""

    import random
    if random.random() < 0.6:
        raise ConnectionError("Network error")

    return {"data": "success"}


result = fetch_api("https://api.example.com")
print(result)  # {"data": "success"}
```

## Retry with Callback

```python
def retry_with_callback(
    max_attempts: int = 3,
    on: Tuple[Type[Exception], ...] = (Exception,),
    backoff: float = 0.1,
    on_retry: Callable[[int, Exception], None] | None = None
) -> Callable:
    """Retry with custom callback"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except on as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        # Call callback
                        if on_retry:
                            on_retry(atpect + 1, e)

                        delay = min(backoff * (2 ** attempt), 5.0)
                        time.sleep(delay)

            raise last_exception  # type: ignore

        return wrapper

    return decorator


# === Usage ===

def log_retry(attempt: int, error: Exception):
    print(f"Attempt {attempt} failed: {error}, retrying...")

@retry_with_callback(
    max_attempts=3,
    on_retry=log_retry
)
def unstable_operation():
    import random
    if random.random() < 0.7:
        raise ValueError("Failed")
    return "Success"

result = unstable_operation()
# Logs retry attempts
```

## Conditional Retry

```python
def retry_if(
    condition: Callable[[Exception], bool],
    max_attempts: int = 3,
    backoff: float = 0.1
) -> Callable:
    """Retry only if condition is met"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:

        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    # Check if should retry
                    if not condition(e) or attempt >= max_attempts - 1:
                        raise

                    delay = min(backoff * (2 ** attempt), 5.0)
                    time.sleep(delay)

            raise last_exception  # type: ignore

        return wrapper

    return decorator


# === Usage ===

def is_transient(error: Exception) -> bool:
    """Check if error is transient"""
    return isinstance(error, (ConnectionError, TimeoutError))

@retry_if(is_transient, max_attempts=5)
def fetch_data():
    # Only retry on transient errors
    ...

# Permanent errors fail immediately
@retry_if(is_transient)
def validate_user(user_id: int):
    if user_id < 0:
        raise ValueError("Invalid user id")  # Won't retry
    return user_id
```

## Async Retry

```python
import asyncio
from typing import Awaitable, Callable

async def async_retry(
    func: Callable[..., Awaitable[T]],
    max_attempts: int = 3,
    on: Tuple[Type[Exception], ...] = (Exception,),
    backoff: float = 0.1
) -> T:
    """Async retry with backoff"""

    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func()

        except on as e:
            last_exception = e

            if attempt < max_attempts - 1:
                delay = min(backoff * (2 ** attempt), 5.0)
                await asyncio.sleep(delay)

    raise last_exception  # type: ignore


def async_retry_decorator(
    max_attempts: int = 3,
    on: Tuple[Type[Exception], ...] = (Exception,),
    backoff: float = 0.1
) -> Callable:
    """Async retry decorator"""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:

        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await async_retry(
                lambda: func(*args, **kwargs),
                max_attempts,
                on,
                backoff
            )

        return wrapper

    return decorator


# === Usage ===

@async_retry_decorator(max_attempts=3, on=(ConnectionError,))
async def fetch_async(url: str) -> dict:
    await asyncio.sleep(0.1)

    import random
    if random.random() < 0.6:
        raise ConnectionError("Network error")

    return {"url": url, "data": "success"}


async def main():
    result = await fetch_async("https://api.example.com")
    print(result)

asyncio.run(main())
```

## Retry Builder

```python
class RetryBuilder:
    """Fluent retry configuration"""

    def __init__(self):
        self.max_attempts = 3
        self.exceptions = (Exception,)
        self.base_delay = 0.1
        self.max_delay = 5.0
        self.on_retry = None

    def attempts(self, n: int) -> 'RetryBuilder':
        """Set max attempts"""
        self.max_attempts = n
        return self

    def on_exceptions(self, *exceptions: Type[Exception]) -> 'RetryBuilder':
        """Set exceptions to retry"""
        self.exceptions = exceptions
        return self

    def with_delay(self, base: float, max_delay: float = 5.0) -> 'RetryBuilder':
        """Set delay parameters"""
        self.base_delay = base
        self.max_delay = max_delay
        return self

    def on_retry_callback(self, callback: Callable) -> 'RetryBuilder':
        """Set retry callback"""
        self.on_retry = callback
        return self

    def build(self) -> Callable:
        """Build retry decorator"""

        return retry(
            max_attempts=self.max_attempts,
            on=self.exceptions,
            backoff=self.base_delay,
            max_delay=self.max_delay
        )

    def __call__(self, func: Callable) -> Callable:
        """Apply as decorator"""
        return self.build()(func)


# === Usage ===

# Build retry configuration
http_retry = (
    RetryBuilder()
    .attempts(5)
    .on_exceptions(ConnectionError, TimeoutError)
    .with_delay(0.5, 10.0)
    .on_retry_callback(lambda attempt, err: print(f"Retry {attempt}"))
    .build()
)

@http_retry
def fetch_http():
    ...

# Or use directly
@RetryBuilder().attempts(3).on_exceptions(ConnectionError)
def fetch_data():
    ...
```

## Circuit Breaker Pattern

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker for failing services"""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_attempts: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts

        self.failures = 0
        self.state = CircuitState.CLOSED
        self.opened_at: datetime | None = None
        self.half_open_successes = 0

    def call(self, func: Callable[..., T], *args, **kwargs) -> Result[T, str]:

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.half_open_successes = 0
            else:
                return Error("Circuit breaker is open")

        # Attempt call
        try:
            result = func(*args, **kwargs)

            # Success
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_successes += 1
                if self.half_open_successes >= self.half_open_attempts:
                    self._reset()

            return Ok(result)

        except Exception as e:
            # Failure
            self._record_failure()
            return Error(str(e))

    def _should_attempt_reset(self) -> bool:
        if self.opened_at is None:
            return False
        elapsed = (datetime.now() - self.opened_at).total_seconds()
        return elapsed >= self.timeout

    def _record_failure(self):
        self.failures += 1

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = datetime.now()

    def _reset(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.opened_at = None
        self.half_open_successes = 0


# === Usage ===

breaker = CircuitBreaker(failure_threshold=3, timeout=30)

@breaker.call
def unstable_service():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Service unavailable")
    return {"data": "success"}

# After 3 failures, circuit opens
# Subsequent calls fail immediately
# After timeout, allows test calls
```

## Retry Statistics

```python
from collections import defaultdict
from typing import Dict

class RetryTracker:
    """Track retry statistics"""

    def __init__(self):
        self.attempts: Dict[str, int] = defaultdict(int)
        self.successes: Dict[str, int] = defaultdict(int)
        self.failures: Dict[str, int] = defaultdict(int)

    def record_attempt(self, name: str):
        self.attempts[name] += 1

    def record_success(self, name: str):
        self.successes[name] += 1

    def record_failure(self, name: str):
        self.failures[name] += 1

    def get_stats(self, name: str) -> dict:
        return {
            "attempts": self.attempts[name],
            "successes": self.successes[name],
            "failures": self.failures[name],
            "success_rate": (
                self.successes[name] / self.attempts[name]
                if self.attempts[name] > 0
                else 0
            )
        }


# === Usage ===

tracker = RetryTracker()

def tracked_retry(func: Callable) -> Callable:
    name = func.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            tracker.record_attempt(name)
            try:
                result = func(*args, **kwargs)
                tracker.record_success(name)
                return result
            except Exception:
                tracker.record_failure(name)
                if attempt < 2:
                    time.sleep(0.1)
        raise

    return wrapper

@tracked_retry
def api_call():
    ...

print(tracker.get_stats("api_call"))
```

## DX Benefits

✅ **Resilient**: Handle transient failures automatically
✅ **Configurable**: Customize retry behavior
✅ **Observable**: Track retry statistics
✅ **Flexible**: Works with sync/async
✅ **Safe**: Circuit breaker prevents cascading failures

## Best Practices

```python
# ✅ Good: Specific exceptions
@retry(on=(ConnectionError, TimeoutError))
def fetch_api(): ...

# ✅ Good: Exponential backoff
@retry(max_attempts=5, backoff=0.5)

# ✅ Good: Retry only transient errors
@retry_if(is_transient)

# ❌ Bad: Retry indefinitely
# Always set max_attempts

# ❌ Bad: Retry on all errors
# Some errors are permanent (e.g., authentication)
```
