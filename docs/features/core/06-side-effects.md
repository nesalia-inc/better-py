# Side Effects: Explicit and Structured

Functional programming avoids hidden side effects. In Python, we use **context managers** and **explicit effect types** to structure side effects.

## What are Side Effects?

A **side effect** is anything that interacts with the outside world:
- Reading/writing files
- Network requests
- Database operations
- Printing to console
- Reading/writing environment variables
- System time
- Randomness

### The Problem with Implicit Effects

```python
# ❌ Implicit: Side effects hidden in function
def process_user(user_id: int) -> User:
    user = db.query(user_id)  # Side effect!
    print(f"Processing {user.name}")  # Side effect!
    send_email(user.email)  # Side effect!
    return user

# Can't test without database
# Can't know what effects happen
# Can't control effects
```

### Explicit Side Effects

```python
# ✅ Explicit: Effects are clear
def process_user(user_id: int) -> Result[User, Exception]:
    return fetch_user(user_id)

def log_user(user: User) -> Unit:
    print(f"Processing {user.name}")
    return unit()

def notify_user(user: User) -> Result[None, Exception]:
    return send_email(user.email)

# Effects are composable and testable
result = (
    fetch_user(user_id)
    .and_then(lambda user: log_user(user).and_then(lambda _: notify_user(user)))
)
```

## Context Managers for Effects

### Basic Context Manager

```python
from contextlib import contextmanager

@contextmanager
def database_connection(url: str):
    """Context manager for database connection"""
    conn = connect(url)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Usage
with database_connection(url) as db:
    user = db.query(user_id)
# Automatically cleaned up
```

### Context Manager with Result

```python
@contextmanager
def with_resource(
    acquire: Callable[[], T],
    release: Callable[[T], None]
) -> Iterator[T]:
    """Generic resource management"""
    resource = None
    try:
        resource = acquire()
        yield resource
    finally:
        if resource is not None:
            release(resource)

# Usage
with with_resource(
    lambda: connect(url),
    lambda conn: conn.close()
) as db:
    result = db.query(user_id)
```

### Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_database_connection(url: str):
    """Async context manager for database"""
    conn = await async_connect(url)
    try:
        yield conn
        await conn.commit()
    finally:
        await conn.close()

# Usage
async with async_database_connection(url) as db:
    user = await db.query(user_id)
```

## Effect Types

### 1. IO Monad (Explicit Effects)

```python
@dataclass(frozen=True, slots=True)
class IO(Generic[T]):
    """Represent a computation with side effects"""

    _run: Callable[[], T]

    def map(self, func: Callable[[T], U]) -> 'IO[U]':
        """Transform the result"""
        def run():
            result = self._run()
            return func(result)
        return IO(run)

    def and_then(self, func: Callable[[T], 'IO[U]']) -> 'IO[U]':
        """Chain IO operations"""
        def run():
            result = self._run()
            next_io = func(result)
            return next_io._run()
        return IO(run)

    def unsafe_run(self) -> T:
        """Execute the IO computation"""
        return self._run()

# IO operations
def read_file(path: str) -> IO[str]:
    def run():
        with open(path) as f:
            return f.read()
    return IO(run)

def write_file(path: str, content: str) -> IO[None]:
    def run():
        with open(path, 'w') as f:
            f.write(content)
    return IO(run)

def print_io(message: str) -> IO[None]:
    def run():
        print(message)
    return IO(run)

# Compose IO operations
def process_file(input_path: str, output_path: str) -> IO[None]:
    return (
        read_file(input_path)
        .map(lambda content: content.upper())
        .and_then(lambda upper: write_file(output_path, upper))
    )

# Execute at the edge of the world
process_file("input.txt", "output.txt").unsafe_run()
```

### 2. Resource Monad

```python
@dataclass(frozen=True, slots=True)
class Resource(Generic[T]):
    """Managed resource with automatic cleanup"""

    acquire: Callable[[], T]
    release: Callable[[T], None]

    def use(self, func: Callable[[T], U]) -> U:
        """Use resource, then cleanup"""
        resource = self.acquire()
        try:
            return func(resource)
        finally:
            self.release(resource)

# Predefined resources
def file_resource(path: str, mode: str = 'r') -> Resource:
    return Resource(
        acquire=lambda: open(path, mode),
        release=lambda f: f.close()
    )

def database_resource(url: str) -> Resource:
    return Resource(
        acquire=lambda: connect(url),
        release=lambda conn: conn.close()
    )

# Usage
file_resource("data.txt").use(lambda f: f.read())

database_resource(url).use(lambda db: db.query("SELECT * FROM users"))
```

### 3. Transaction Monad

```python
@dataclass(frozen=True, slots=True)
class Transaction(Generic[T]):
    """Database transaction with auto commit/rollback"""

    db: Any
    operation: Callable[[], Result[T, Exception]]

    def execute(self) -> Result[T, Exception]:
        """Execute with auto commit/rollback"""
        try:
            self.db.begin()
            result = self.operation()
            if result.is_ok():
                self.db.commit()
                return result
            else:
                self.db.rollback()
                return result
        except Exception as e:
            self.db.rollback()
            return Error(e)

def in_transaction(db: Any, operation: Callable[[], Result[T, Exception]]) -> Result[T, Exception]:
    """Run operation in transaction"""
    return Transaction(db, operation).execute()

# Usage
def create_user(db, user_data: dict) -> Result[User, Exception]:
    def operation():
        user = db.insert("users", user_data)
        profile = db.insert("profiles", {"user_id": user.id})
        return Ok(user)

    return in_transaction(db, operation)

# Automatically commits on success, rolls back on error
result = create_user(database, {"name": "Alice"})
```

## Effect Protocols

### Resourceful Protocol

```python
@runtime_checkable
class Resourceful(Protocol[T]):
    """Object that manages a resource"""

    def __enter__(self) -> T: ...
    def __exit__(self, *exc) -> bool | None: ...

class DatabaseConnection:
    """Database connection implementing Resourceful"""

    def __init__(self, url: str):
        self.url = url
        self._conn = None

    def __enter__(self) -> 'DatabaseConnection':
        self._conn = connect(self.url)
        return self

    def __exit__(self, *exc):
        if self._conn:
            self._conn.close()
        return False

    def query(self, sql: str) -> Result[list[dict], Exception]:
        try:
            return Ok(self._conn.query(sql))
        except Exception as e:
            return Error(e)

# Usage
with DatabaseConnection(url) as db:
    result = db.query("SELECT * FROM users")
    if result.is_ok():
        users = result.unwrap()
```

### Async Resourceful Protocol

```python
@runtime_checkable
class AsyncResourceful(Protocol[T]):
    """Async resource management"""

    async def __aenter__(self) -> T: ...
    async def __aexit__(self, *exc) -> bool | None: ...

class AsyncDatabaseConnection:
    """Async database connection"""

    def __init__(self, url: str):
        self.url = url
        self._conn = None

    async def __aenter__(self) -> 'AsyncDatabaseConnection':
        self._conn = await async_connect(self.url)
        return self

    async def __aexit__(self, *exc):
        if self._conn:
            await self._conn.close()
        return False

    async def query(self, sql: str) -> Result[list[dict], Exception]:
        try:
            return Ok(await self._conn.query(sql))
        except Exception as e:
            return Error(e)

# Usage
async with AsyncDatabaseConnection(url) as db:
    result = await db.query("SELECT * FROM users")
```

## Practical Effect Patterns

### 1. Retry with Backoff

```python
@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Retry strategy"""
    max_attempts: int = 3
    base_delay: float = 0.1
    max_delay: float = 10.0

    def get_delay(self, attempt: int) -> float:
        """Exponential backoff"""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)

def with_retry[T](
    operation: Callable[[], Result[T, Exception]],
    policy: RetryPolicy
) -> Result[T, Exception]:
    """Run operation with retry"""
    last_error = None

    for attempt in range(policy.max_attempts):
        result = operation()

        if result.is_ok():
            return result

        last_error = result.error

        if attempt < policy.max_attempts - 1:
            import time
            time.sleep(policy.get_delay(attempt))

    return Error(last_error)

# Usage
def fetch_with_retry(url: str) -> Result[Response, Exception]:
    return with_retry(
        lambda: http_get(url),
        RetryPolicy(max_attempts=5, base_delay=0.5)
    )
```

### 2. Timeout

```python
def with_timeout[T](
    operation: Callable[[], T],
    timeout: float
) -> Result[T, TimeoutError]:
    """Run operation with timeout"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout}s")

    # Set alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(int(timeout))

    try:
        result = operation()
        signal.alarm(0)  # Cancel alarm
        return Ok(result)
    except TimeoutError as e:
        return Error(e)
    finally:
        signal.signal(signal.SIGALRM, old_handler)

# Usage
result = with_timeout(
    lambda: slow_operation(),
    timeout=5.0
)
```

### 3. Circuit Breaker

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
    recovery_timeout: timedelta = timedelta(seconds=60)

    def __post_init__(self):
        self._failures = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED

    def call[T](self, operation: Callable[[], Result[T, Exception]]) -> Result[T, Exception]:
        """Call operation through circuit breaker"""

        # Check if should attempt recovery
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
        return datetime.now() - self._last_failure_time >= self.recovery_timeout

    def _on_failure(self):
        self._failures += 1
        self._last_failure_time = datetime.now()

        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def _on_success(self):
        self._failures = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED

# Usage
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=timedelta(seconds=60))

def call_service() -> Result[Response, Exception]:
    return breaker.call(lambda: http_get(api_url))
```

### 4. Rate Limiting

```python
@dataclass
class RateLimiter:
    """Token bucket rate limiter"""

    rate: float  # Tokens per second
    capacity: int  # Max tokens

    def __post_init__(self):
        self._tokens = self.capacity
        self._last_update = time.time()

    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        now = time.time()
        elapsed = now - self._last_update

        # Refill tokens
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_update = now

        # Check if enough tokens
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    def acquire_or_wait[T](
        self,
        operation: Callable[[], T],
        tokens: int = 1
    ) -> Result[T, Exception]:
        """Acquire tokens or wait, then run operation"""
        while not self.acquire(tokens):
            time.sleep(0.1)

        try:
            return Ok(operation())
        except Exception as e:
            return Error(e)

# Usage
limiter = RateLimiter(rate=10.0, capacity=100)

def api_call() -> Result[Response, Exception]:
    return limiter.acquire_or_wait(lambda: http_get(api_url))
```

## Testing with Effects

### Mocking Effects

```python
# Abstract effect
class Database(Protocol):
    def query(self, sql: str) -> Result[list, Exception]: ...

# Production implementation
class RealDatabase:
    def query(self, sql: str) -> Result[list, Exception]:
        try:
            return Ok(self._conn.query(sql))
        except Exception as e:
            return Error(e)

# Test implementation
class MockDatabase:
    def __init__(self):
        self._queries = []
        self._results = {}

    def query(self, sql: str) -> Result[list, Exception]:
        self._queries.append(sql)
        return Ok(self._results.get(sql, []))

    def set_result(self, sql: str, result: list):
        self._results[sql] = result

    def get_queries(self) -> list[str]:
        return self._queries

# Test without real database
def test_process_user():
    mock_db = MockDatabase()
    mock_db.set_result("SELECT * FROM users WHERE id = 1", [{"id": 1, "name": "Alice"}])

    result = process_user(mock_db, 1)

    assert result.is_ok()
    assert result.unwrap()["name"] == "Alice"
    assert mock_db.get_queries() == ["SELECT * FROM users WHERE id = 1"]
```

## Best Practices

### ✅ Do: Make effects explicit

```python
def fetch_user(id: int) -> Result[User, Exception]:
    """Clear: May fail with Exception"""
```

### ✅ Do: Use context managers for resources

```python
with database_connection(url) as db:
    result = db.query(sql)
```

### ✅ Do: Compose effects

```python
result = (
    fetch_user(id)
    .and_then(send_email)
    .and_then(log_action)
)
```

### ❌ Don't: Hide effects

```python
# ❌ Effect hidden
def get_user(id: int) -> User:
    return db.query(id)  # What if db fails?

# ✅ Effect explicit
def get_user(id: int) -> Result[User, Exception]:
    try:
        return Ok(db.query(id))
    except Exception as e:
        return Error(e)
```

### ❌ Don't: Mix pure and impure

```python
# ❌ Mixed concerns
def process(user: User) -> User:
    send_email(user.email)  # Side effect in pure function
    user.processed = True
    return user

# ✅ Separate concerns
def process(user: User) -> User:
    return replace(user, processed=True)

def notify_user(user: User) -> Result[None, Exception]:
    return send_email(user.email)
```

## Summary

**Side effects** in functional Python:
- ✅ Explicit with `Result[T, Exception]`
- ✅ Structured with context managers
- ✅ Composable with `and_then`
- ✅ Controllable with retry, timeout, circuit breaker
- ✅ Testable with Protocol-based mocks

**Patterns**:
- IO monad for explicit effects
- Resource monad for cleanup
- Transaction for atomicity
- Retry for resilience
- Circuit breaker for fault tolerance

**Principle**: Keep functions **pure** at the core, push effects to the **edges**.

---

**Next**: See [Functional Entities](../entities/00-overview.md) for entity definitions.
