# Result Combinators - Error Handling Chains

Chain operations and handle errors gracefully with Result types.

## Overview

Result combinators enable:
- Chain operations that can fail
- Handle errors at the end
- No nested try/catch
- Clear error flow
- Composable error handlers

## Basic Result Type

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable, Any

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    """Success value"""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_error(self) -> bool:
        return False

    def unwrap(self):
        return self.value

    def unwrap_or(self, default):
        return self.value

    def map(self, func: Callable[[T], Any]) -> 'Ok':
        return Ok(func(self.value))

    def then(self, func: Callable[[T], 'Result']) -> 'Result':
        return func(self.value)

    def map_error(self, func):
        return self


@dataclass
class Error(Generic[E]):
    """Error value"""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_error(self) -> bool:
        return True

    def unwrap(self):
        raise ValueError(f"Cannot unwrap error: {self.error}")

    def unwrap_or(self, default):
        return default

    def map(self, func):
        return self

    def then(self, func):
        return self

    def map_error(self, func: Callable[[E], Any]) -> 'Error':
        return Error(func(self.error))


Result = Ok[T] | Error[E]


# === Usage ===

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Error("Division by zero")
    return Ok(a / b)

result = divide(10, 2)
print(result.is_ok())  # True
print(result.unwrap())  # 5.0

result = divide(10, 0)
print(result.is_error())  # True
print(result.unwrap_or(0))  # 0
```

## Chaining with Then

```python
def validate_email(email: str) -> Result[str, str]:
    if "@" not in email:
        return Error("Invalid email format")
    return Ok(email.lower())

def check_unique(email: str) -> Result[bool, str]:
    if email in database:
        return Error("Email already exists")
    return Ok(True)

def hash_password(password: str) -> Result[str, str]:
    if len(password) < 8:
        return Error("Password too short")
    return Ok(hashlib.sha256(password.encode()).hexdigest())

def create_user(data: dict) -> Result[User, str]:
    return (
        Result.from_value(data.get("email"))
        .then(validate_email)
        .then(lambda _: check_unique(data["email"]))
        .then(lambda _: hash_password(data["password"]))
        .then(lambda hashed: Ok(User(
            email=data["email"],
            password=hashed
        )))
    )


# === Usage ===

data = {
    "email": "user@example.com",
    "password": "securepassword123"
}

result = create_user(data)

if result.is_ok():
    user = result.unwrap()
    print(f"Created user: {user.email}")
else:
    error = result.error
    print(f"Failed: {error}")
```

## Pipeline Combinators

```python
class ResultPipeline:
    """Build result processing pipelines"""

    def __init__(self):
        self._steps: list[Callable] = []

    def step(self, func: Callable) -> 'ResultPipeline':
        """Add processing step"""
        self._steps.append(func)
        return self

    def validate(self, predicate: Callable, error: str) -> 'ResultPipeline':
        """Add validation step"""

        def validator(value):
            if predicate(value):
                return Ok(value)
            return Error(error)

        return self.step(validator)

    def __call__(self, initial: Any) -> Result:
        """Execute pipeline"""

        result = Result.from_value(initial)

        for step in self._steps:
            if result.is_error():
                return result
            result = step(result.unwrap())

        return result


# === Usage ===

process_user = (
    ResultPipeline()
    .step(lambda d: d.get("name"))
    .validate(lambda x: x is not None, "Name required")
    .step(lambda x: x.strip())
    .validate(lambda x: len(x) >= 2, "Name too short")
    .step(lambda x: x.capitalize())
)

result = process_user({"name": "  alice  "})
print(result.unwrap())  # "Alice"

result = process_user({"name": "A"})
print(result.error)  # "Name too short"
```

## Async Result Combinators

```python
import asyncio
from typing import Awaitable, Callable

class AsyncResult:
    """Async result operations"""

    @staticmethod
    async def then(result: Result, func: Callable[[T], Awaitable[Result]]) -> Result:
        """Chain async operations"""

        if result.is_error():
            return result

        return await func(result.unwrap())

    @staticmethod
    async def map(result: Result, func: Callable[[T], Awaitable[T]]) -> Result:
        """Map async function"""

        if result.is_error():
            return result

        value = await func(result.unwrap())
        return Ok(value)


# === Usage ===

async def fetch_user(id: int) -> Result[dict, str]:
    await asyncio.sleep(0.1)
    if id == 1:
        return Ok({"id": 1, "name": "Alice"})
    return Error("User not found")

async def validate_user(user: dict) -> Result[dict, str]:
    await asyncio.sleep(0.05)
    if "name" not in user:
        return Error("No name")
    return Ok(user)

async def main():
    result = await AsyncResult.then(
        Ok(1),
        lambda id: fetch_user(id)
    )

    if result.is_ok():
        print(f"User: {result.unwrap()}")

asyncio.run(main())
```

## Combinator Library

```python
class R:
    """Combinator library for Results"""

    @staticmethod
    def map(func: Callable[[T], U]) -> Callable[[Result], Result]:
        """Create map function"""

        def mapper(result: Result) -> Result:
            return result.map(func)

        return mapper

    @staticmethod
    def then(func: Callable[[T], Result]) -> Callable[[Result], Result]:
        """Create then function"""

        def chainer(result: Result) -> Result:
            return result.then(func)

        return chainer

    @staticmethod
    def validate(predicate: Callable[[T], bool], error: E) -> Callable[[Result], Result]:
        """Create validator"""

        def validator(result: Result) -> Result:
            if result.is_error():
                return result
            if predicate(result.unwrap()):
                return result
            return Error(error)

        return validator

    @staticmethod
    def fallback(default: T) -> Callable[[Result], T]:
        """Unwrap with default"""

        def unfaller(result: Result) -> T:
            return result.unwrap_or(default)

        return unfaller


# === Usage ===

pipeline = [
    R.map(lambda x: x * 2),
    R.validate(lambda x: x > 0, "Must be positive"),
    R.map(lambda x: x + 10),
]

value = Ok(5)
for step in pipeline:
    value = step(value)

print(value.unwrap())  # 20
```

## Collect Results

```python
from typing import list

def collect_all(results: list[Result]) -> Result[list[T], E]:
    """Collect list of Results into Result of list"""

    values = []
    errors = []

    for result in results:
        if result.is_ok():
            values.append(result.unwrap())
        else:
            errors.append(result.error)

    if errors:
        return Error(errors)

    return Ok(values)


def collect_first_ok(results: list[Result]) -> Result:
    """Return first Ok, or combined Errors"""

    for result in results:
        if result.is_ok():
            return result

    errors = [r.error for r in results if r.is_error()]
    return Error(errors)


# === Usage ===

results = [
    Ok(1),
    Ok(2),
    Error("Failed"),
    Ok(3)
]

all_ok = collect_all(results)
print(all_ok)  # Error(["Failed"])

first = collect_first_ok(results)
print(first)  # Ok(1)
```

## Retry Combinator

```python
def retry_result(
    func: Callable[[], Result],
    max_attempts: int = 3,
    backoff: float = 0.1
) -> Result:
    """Retry operation until success or max attempts"""

    last_error = None

    for attempt in range(max_attempts):
        result = func()

        if result.is_ok():
            return result

        last_error = result.error

        if attempt < max_attempts - 1:
            time.sleep(backoff * (2 ** attempt))

    return Error(last_error)


# === Usage ===

def flaky_operation() -> Result[int, str]:
    import random
    if random.random() < 0.7:
        return Error("Temporary failure")
    return Ok(42)

result = retry_result(flaky_operation, max_attempts=5)
print(result.is_ok())  # Likely True
```

## Conversion Helpers

```python
class Result:
    """Result type helpers"""

    @staticmethod
    def from_value(value: T) -> Result:
        """Create Ok from value"""
        return Ok(value)

    @staticmethod
    def from_error(error: E) -> Result:
        """Create Error from error"""
        return Error(error)

    @staticmethod
    def from_callable(func: Callable[[], T]) -> Result:
        """Execute callable and catch exceptions"""

        try:
            return Ok(func())
        except Exception as e:
            return Error(str(e))

    @staticmethod
    def from_optional(value: T | None, error: E = "No value") -> Result:
        """Convert optional to Result"""

        if value is None:
            return Error(error)
        return Ok(value)


# === Usage ===

result = Result.from_callable(lambda: 10 / 2)
print(result)  # Ok(5.0)

result = Result.from_callable(lambda: 10 / 0)
print(result)  # Error("division by zero")

result = Result.from_optional(None)
print(result)  # Error("No value")
```

## DX Benefits

✅ **Composable**: Chain operations easily
✅ **Safe**: Cannot forget error handling
✅ **Clear**: Error flow is explicit
✅ **Testable**: Easy to test error paths
✅ **Flexible**: Works with sync/async

## Best Practices

```python
# ✅ Good: Chain operations
result = (Ok(data)
    .then(validate)
    .then(transform)
    .then(save))

# ✅ Good: Handle errors at the end
if result.is_ok():
    use(result.unwrap())
else:
    log_error(result.error)

# ✅ Good: Provide context
Error(f"Failed to create user: {err}")

# ❌ Bad: Unwrap without checking
# result.unwrap()  # Could crash!

# ❌ Bad: Ignoring errors
# Don't just check is_ok() and ignore error branch
```
