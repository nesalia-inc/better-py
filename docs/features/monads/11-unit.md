# Unit - Void Return Type

Represent void computations (functions returning nothing) as a value.

## Overview

`Unit` represents a computation that returns nothing (void):
- `unit()` - Singleton value for void functions

## Basic Usage

```python
from mfn import unit

def log_message(message: str) -> Unit:
    """Log message and return Unit"""
    print(message)
    return unit()


def save_to_database(data: dict) -> Unit:
    """Save data, return Unit"""
    db.insert(data)
    return unit()


# Functions return Unit instead of None
result = log_message("Processing...")
# Unit

result = save_to_database({"key": "value"})
# Unit
```

## Unit Type

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Unit:
    """Represents void computation result"""

    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return "Unit()"


# Singleton instance
unit = Unit()

def unit() -> Unit:
    """Return the singleton Unit instance"""
    return unit
```

## Unit in Pattern Matching

```python
def handle_result(result: Result) -> Unit:

    match result:
        case Ok(value):
            print(f"Success: {value}")
            return unit()

        case Error(exc):
            print(f"Error: {exc}")
            return unit()


# All branches return Unit
result = handle_result(fetch_data())
```

## Unit in Composition

```python
from mfn import Task, Result

def process_data(data: dict) -> Task:

    async def inner():
        # Validate
        result = validate(data)

        if result.is_error():
            log(f"Validation failed: {result.error}")
            return unit()

        # Transform
        transformed = transform(result.unwrap())
        return save(transformed)


# Task[Unit] - task that returns Unit
def send_email(user_id: int) -> Task[Unit]:

    async def inner():
        user = await fetch_user(user_id)
        email_service.send(user.email)
        return unit()

    return Task(inner)
```

## Unit with Maybe

```python
class Maybe(Generic[T]):

    @staticmethod
    def unit() -> 'Maybe[Unit]':
        """Maybe containing Unit"""
        return Some(unit())


def find_and_log(id: int) -> Maybe[Unit]:

    user = db.find(id)

    if user:
        log(f"Found user {id}")
        return Maybe.unit()

    return None_


# Usage
result = find_and_log(123)
if result.is_some():
    print("User found and logged")
```

## Unit with Result

```python
class Result(Generic[T, E]):

    @staticmethod
    def unit() -> 'Result[Unit, E]':
        """Success with Unit value"""
        return Ok(unit())


def delete_user(user_id: int) -> Result[Unit, Exception]:

    if user_id < 0:
        return Error(ValidationError("Invalid user ID"))

    db.delete(user_id)
    log(f"Deleted user {user_id}")

    return Result.unit()


# Usage
result = delete_user(42)
if result.is_ok():
    print("User deleted successfully")  # Side effects happened
```

## Unit in Async Operations

```python
async def process_async() -> Unit:

    await asyncio.sleep(0.1)
    print("Async operation complete")

    return unit()


async def workflow():

    await log_message("Starting")
    result = await fetch_data()

    if result:
        await save_data(result)
        return await log_message("Complete")

    return unit()
```

## Unit vs None

```python
# ❌ Returning None
def bad_function():
    do_something()
    return None  # What does this mean?

# ✅ Returning Unit
def good_function() -> Unit:
    do_something()
    return unit()  # Explicit void return
```

## Unit Operations

```python
class UnitOps:
    """Unit operations and utilities"""

    @staticmethod
    def sequence(*units: Unit) -> Unit:
        """Run multiple Unit-returning functions"""
        for u in units:
            pass  # All ran
        return unit()

    @staticmethod
    def while_(predicate: Callable[[], bool], action: Callable) -> Unit:

        while predicate():
            action()

        return unit()

    @staticmethod
    def for_(iterable: Iterable, action: Callable) -> Unit:
        """Run action for each item"""

        for item in iterable:
            action(item)

        return unit()


# === Usage ===
UnitOps.while_(
    lambda: has_more_data(),
    lambda: process_next()
)

UnitOps.for_(users, lambda u: send_email(u.id))
```

## Task Returning Unit

```python
class Task(Generic[T]):

    def returning_unit(self) -> Task[Unit]:

        async def inner():
            await self._coro()
            return unit()

        return Task(inner)


# === Usage ===
task = Task(fetch_data).returning_unit()

await task.run()  # Runs fetch_data, returns Unit
```

## DX Benefits

✅ **Explicit**: Void return is explicit, not implicit None
✅ **Composable**: Chain void functions naturally
✅ **Type-safe**: Unit is distinct from None
✅ **Pattern matching**: Works with `match/case`
✅ **Consistent**: Always return unit() from void functions

## Best Practices

```python
# ✅ Good: Return unit() from void functions
def log_message(msg: str) -> Unit:
    print(msg)
    return unit()

# ✅ Good: Use in Result/Task
Result.unit()  # Success with no value
Task.unit()   # Task returning Unit

# ✅ Good: Chain Unit-returning functions
validate() | save() | log()  # All return Unit

# ❌ Bad: Returning None
def bad():
    return None  # Ambiguous

# ❌ Bad: Checking for None
# Don't check if result is None, check if it's Unit()
```
