# Logging/Tracing - Observability

Add observability to code with logging and tracing helpers.

## Overview

Logging/tracing enables:
- Automatic logging
- Correlation IDs
- Performance tracking
- Error tracking
- Request tracing

## Trace Decorator

```python
import logging
from typing import Callable, Any
from functools import wraps
from uuid import uuid4

logger = logging.getLogger(__name__)

def trace(
    level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = False,
    log_error: bool = True
) -> Callable:
    """Trace function execution"""

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args, **kwargs):

            # Generate correlation ID
            correlation_id = str(uuid4())

            # Log entry
            if log_args:
                logger.log(
                    level,
                    f"[{correlation_id}] Entering {func.__name__} "
                    f"with args={args}, kwargs={kwargs}"
                )
            else:
                logger.log(
                    level,
                    f"[{correlation_id}] Entering {func.__name__}"
                )

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Log result
                if log_result:
                    logger.log(
                        level,
                        f"[{correlation_id}] {func.__name__} returned {result!r}"
                    )
                else:
                    logger.log(
                        level,
                        f"[{correlation_id}] Exiting {func.__name__}"
                    )

                return result

            except Exception as e:
                # Log error
                if log_error:
                    logger.error(
                        f"[{correlation_id}] {func.__name__} raised {type(e).__name__}: {e}"
                    )
                raise

        return wrapper

    return decorator


# === Usage ===

@trace(level=logging.DEBUG, log_args=True, log_result=True)
def calculate(a: int, b: int) -> int:
    return a * b

@trace(log_error=True)
def risky_operation():
    raise ValueError("Something went wrong")

calculate(5, 3)
# Output:
# DEBUG:__main__:[abc-123] Entering calculate with args=(5, 3), kwargs={}
# DEBUG:__main__:[abc-123] calculate returned 15
```

## Performance Trace

```python
import time
from contextlib import contextmanager

@contextmanager
def performance_trace(operation: str, threshold: float = 0.0):
    """Trace operation performance"""

    start = time.time()
    logger.info(f"Starting: {operation}")

    try:
        yield

    finally:
        duration = time.time() - start
        logger.info(f"Completed: {operation} in {duration:.3f}s")

        if duration > threshold:
            logger.warning(
                f"Performance: {operation} took {duration:.3f}s "
                f"(threshold: {threshold}s)"
            )


# === Usage ===

def process_items(items: list):

    with performance_trace("process_items", threshold=1.0):
        for item in items:
            # Process item
            time.sleep(0.01)

# Output:
# INFO:__main__:Starting: process_items
# INFO:__main__:Completed: process_items in 0.150s
```

## Request Tracing

```python
from contextvars import ContextVar
from typing import Generator

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


@contextmanager
def request_context(request_id: str) -> Generator[None, None, None]:
    """Set request context"""

    token = request_id_var.set(request_id)

    try:
        logger.info(f"Request started: {request_id}")
        yield
    finally:
        logger.info(f"Request ended: {request_id}")
        request_id_var.reset(token)


def get_request_id() -> str:
    """Get current request ID"""

    return request_id_var.get()


def log_with_context(message: str, level: int = logging.INFO):
    """Log with request context"""

    request_id = get_request_id()
    logger.log(level, f"[{request_id}] {message}")


# === Usage ===

@trace()
def handle_request(data: dict):
    """Handle request with context"""

    log_with_context(f"Processing: {data}")

    # Do work
    result = process(data)

    log_with_context(f"Result: {result}")
    return result


# Use context
with request_context("req-abc-123"):
    handle_request({"user": "alice"})

# All logs include [req-abc-123]
```

## Structured Logging

```python
from typing import Any
import json

class StructuredLogger:
    """Structured JSON logger"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: dict = {}

    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Add context to logger"""

        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger

    def _log(self, level: int, message: str, **extra):
        """Log structured data"""

        log_data = {
            "message": message,
            **self.context,
            **extra
        }

        self.logger.log(level, json.dumps(log_data))

    def info(self, message: str, **extra):
        self._log(logging.INFO, message, **extra)

    def error(self, message: str, **extra):
        self._log(logging.ERROR, message, **extra)

    def warning(self, message: str, **extra):
        self._log(logging.WARNING, message, **extra)

    def debug(self, message: str, **extra):
        self._log(logging.DEBUG, message, **extra)


# === Usage ===

logger = StructuredLogger("app")

logger.with_context(user_id=123, service="payment").info(
    "Processing payment",
    amount=99.99,
    currency="USD"
)

# Output: {"message": "Processing payment", "user_id": 123, "service": "payment", "amount": 99.99, "currency": "USD"}
```

## Error Tracking

```python
from traceback import format_exception
from typing import Type

class ErrorTracker:
    """Track and log errors"""

    def __init__(self):
        self.errors: list[dict] = []

    def track(
        self,
        error: Exception,
        context: dict | None = None,
        level: int = logging.ERROR
    ):

        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": "".join(format_exception(type(error), error, error.__traceback__)),
            "context": context or {}
        }

        self.errors.append(error_info)

        logger.log(level, f"Error: {error_info['type']}: {error_info['message']}")
        logger.debug(f"Traceback:\n{error_info['traceback']}")

        if error_info['context']:
            logger.debug(f"Context: {error_info['context']}")

        return error_info

    def clear(self):
        """Clear error history"""
        self.errors.clear()


# === Usage ===

tracker = ErrorTracker()

try:
    risky_operation()
except Exception as e:
    tracker.track(e, context={"user_id": 123, "action": "delete"})
```

## Metrics

```python
from collections import defaultdict
from time import time

class Metrics:
    """Simple metrics tracker"""

    def __init__(self):
        self.counters: defaultdict[str, int] = defaultdict(int)
        self.gauges: dict[str, float] = {}
        self.timings: defaultdict[str, list] = defaultdict(list)

    def increment(self, name: str, value: int = 1):
        """Increment counter"""

        self.counters[name] += value

    def set_gauge(self, name: str, value: float):
        """Set gauge value"""

        self.gauges[name] = value

    def timing(self, name: str, duration: float):
        """Record timing"""

        self.timings[name].append(duration)

    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)

    def get_gauge(self, name: str) -> float | None:
        return self.gauges.get(name)

    def get_timing_stats(self, name: str) -> dict | None:

        if name not in self.timings:
            return None

        timings = self.timings[name]

        return {
            "count": len(timings),
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings)
        }


# === Usage ===

metrics = Metrics()

@trace()
def process_request():
    metrics.increment("requests.total")

    start = time.time()

    # Do work
    time.sleep(0.1)

    duration = time.time() - start
    metrics.timing("request.duration", duration)
    metrics.set_gauge("requests.active", 0)

process_request()

print(metrics.get_counter("requests.total"))  # 1
print(metrics.get_timing_stats("request.duration"))  # {"count": 1, "min": ..., "avg": ...}
```

## DX Benefits

✅ **Automatic**: Add tracing with decorators
✅ **Correlated**: Track related operations
✅ **Observable**: Metrics and logs
✅ **Debuggable**: Full context
✅ **Performance**: Track slow operations

## Best Practices

```python
# ✅ Good: Use correlation IDs
@trace()
def operation():
    # All logs include correlation ID

# ✅ Good: Structured logging
logger.info("Payment processed", amount=99.99, user_id=123)

# ✅ Good: Performance thresholds
with performance_trace("export", threshold=5.0):
    ...

# ✅ Good: Error context
tracker.track(e, context={"user_id": 123})

# ❌ Bad: Print statements
# Use logger instead
```
