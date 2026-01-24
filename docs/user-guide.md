# better-py User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Functional Programming Concepts](#functional-programming-concepts)
4. [Monads](#monads)
   - [Error Handling](#error-handling)
   - [State & Computations](#state--computations)
   - [Async & Effects](#async--effects)
5. [Persistent Collections](#persistent-collections)
6. [Functional Utilities](#functional-utilities)
7. [Common Patterns](#common-patterns)
8. [Best Practices](#best-practices)

---

## Introduction

**better-py** is a modern, pragmatic functional programming library for Python that provides:

- **13 monads** for different computational contexts
- **3 persistent collections** with structural sharing
- **Functional utilities** (compose, curry, pipe)
- **Type-safe protocols** for functional patterns

### Why Functional Programming?

Functional programming helps you write code that is:
- **More predictable** - No hidden state mutations
- **Easier to test** - Pure functions are simple to unit test
- **More composable** - Small functions combine into complex behaviors
- **Safer** - Immutable data prevents entire classes of bugs

---

## Installation

```bash
pip install better-py-fp
```

---

## Functional Programming Concepts

### Pure Functions

A pure function:
- Always returns the same output for the same input
- Has no side effects (no mutations, I/O, etc.)

```python
# ❌ Impure
counter = 0
def increment():
    global counter
    counter += 1
    return counter

# ✅ Pure
def increment(count: int) -> int:
    return count + 1
```

### Immutability

Immutable data cannot be changed after creation:

```python
# ✅ With better-py
from better_py import PersistentList

lst1 = PersistentList.of(1, 2, 3)
lst2 = lst1.append(4)

assert lst1.to_list() == [1, 2, 3]  # Unchanged
assert lst2.to_list() == [1, 2, 3, 4]  # New list
```

---

## Monads

Monads are design patterns that structure computations. Think of them as **containers** with special rules for transformation.

### Error Handling

#### Maybe - For Optional Values

Use `Maybe` when a value might not exist:

```python
from better_py import Maybe

# Creating Maybe values
some_value = Maybe.some(42)
no_value = Maybe.nothing()

# From potentially None values
maybe_value = Maybe.from_value(get_user())  # None → Nothing, other → Some

# Transformations
Maybe.some(5).map(lambda x: x * 2)  # Maybe(10)
Maybe.nothing().map(lambda x: x * 2)  # Nothing

# Chaining operations
Maybe.some(10) \
    .map(lambda x: x / 2) \
    .bind(lambda x: Maybe.some(x) if x > 3 else Maybe.nothing())  # Maybe(5)

# Pattern matching
result = Maybe.some(42).fold(
    on_nothing=lambda: "No value",
    on_some=lambda x: f"Got {x}"
)  # "Got 42"
```

**When to use:**
- Optional configuration values
- Safe dictionary access
- Chaining operations that might not return values

**⚠️ Breaking Change:** `Maybe.some(None)` returns `Some(None)`, not `Nothing`. Use `Maybe.from_value(None)` for `Nothing` or `Maybe.some_none()` for explicit `Some(None)`.

#### Result - For Error Handling

Use `Result` when operations can fail with specific errors:

```python
from better_py import Result

# Creating Results
success = Result.ok(42)
error = Result.error("Something went wrong")

# Transformations on success
Result.ok(10).map(lambda x: x * 2)  # Result.ok(20)
Result.error("bad").map(lambda x: x * 2)  # Still error("bad")

# Error handling
Result.ok(10).map_error(lambda e: f"Error: {e}")  # Result.ok(10)
Result.error("fail").map_error(lambda e: f"Error: {e}")  # Result.error("Error: fail")

# Chaining
def divide(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Result.error("Division by zero")
    return Result.ok(a // b)

Result.ok(100).bind(lambda x: divide(x, 5))  # Result.ok(20)
Result.ok(100).bind(lambda x: divide(x, 0))  # Result.error("Division by zero")

# Pattern matching
result.fold(
    on_error=lambda err: f"Failed: {err}",
    on_ok=lambda val: f"Success: {val}"
)
```

**When to use:**
- API calls that can fail
- Database operations
- File parsing
- Any operation with explicit error types

#### Validation - Accumulating Errors

Use `Validation` when validating multiple fields and collecting all errors:

```python
from better_py import Validation

# Creating Validations
valid = Validation.valid(42)
invalid = Validation.invalid(["Error 1", "Error 2"])

# Single field validation
def validate_positive(value: int) -> Validation[str, int]:
    if value > 0:
        return Validation.valid(value)
    return Validation.invalid([f"{value} is not positive"])

def validate_range(value: int) -> Validation[str, int]:
    if 0 <= value <= 100:
        return Validation.valid(value)
    return Validation.invalid([f"{value} is out of range"])

# Accumulate errors
class UserData:
    name: str
    age: int
    email: str

def validate_name(name: str) -> Validation[str, str]:
    if len(name) >= 2:
        return Validation.valid(name)
    return Validation.invalid(["Name too short"])

def validate_age(age: int) -> Validation[str, int]:
    if 0 < age < 150:
        return Validation.valid(age)
    return Validation.invalid(["Invalid age"])

# Combine validations
data = UserData(name="A", age=200, email="test@example.com")

name_valid = validate_name(data.name)
age_valid = validate_age(data.age)

# Using applicative style for parallel validation
name_valid.ap(age_valid)  # Accumulates both errors

# Sequential validation
name_valid.flat_map(lambda _: age_valid)
```

**When to use:**
- Form validation
- Multi-field validation
- Any scenario where you need **all** errors, not just the first

#### Try - Exception Handling

Use `Try` when working with code that might throw exceptions:

```python
from better_py import Try

# Execute code that might raise exceptions
result = Try(lambda: int("42"))  # Success(42)
result = Try(lambda: int("invalid"))  # Failure(ValueError)

# Recovery
Try(lambda: 1 / 0).recover(lambda e: 0)  # Success(0)

# Pattern matching
result.fold(
    on_failure=lambda exc: f"Exception: {exc}",
    on_success=lambda val: f"Value: {val}"
)
```

**When to use:**
- Wrapping existing Python APIs
- Legacy code integration
- Operations that might raise exceptions

---

### State & Computations

#### State - Stateful Computations

`State` manages state transitions in a pure functional way:

```python
from better_py import State

# Get current state
current = State.get()

# Modify state
incremented = State.modify(lambda x: x + 1)

# Put new state
reset = State.put(0)

# Extract value (leaving state unchanged)
value = State.eval(lambda s: s * 2)  # Returns s*2, state unchanged

# Extract new state (discarding value)
new_state = State.execute(lambda s: s + 1)  # Returns new state

# Chain state operations
def add_and_multiply(x: int) -> State[int, int]:
    return State.modify(lambda s: s + x).flat_map(
        lambda _: State.get()
    )

# Run with initial state
result = add_and_multiply(5).run(10)
# Returns (15, 15) - value 15, new state 15
```

**When to use:**
- State machines
- Counters
- Game logic
- Any scenario requiring state in functional code

#### Reader - Dependency Injection

`Reader` represents computations that depend on an environment:

```python
from better_py import Reader

# Access environment
config = Reader.ask()

# Modify environment locally
local_config = Reader.local(lambda env: env * 2)

def compute(x: int) -> Reader[int, int]:
    return Reader.ask().map(lambda env: x + env)

# Run with environment
compute(5).run(10)  # Returns 15
```

**When to use:**
- Configuration access
- Dependency injection
- Environment-based computations

#### Writer - Logging & Accumulation

`Writer` accumulates values (logs, metrics) alongside computations:

```python
from better_py import Writer, list_writer, str_writer

# Create with list log
writer = list_writer(["Operation 1"], 42)

# Transform value
result = writer.map(lambda x: x * 2)
# log: ["Operation 1"], value: 84

# Chain operations
def add_log(x):
    return Writer.list_writer([f"Processed {x}"], x + 1)

Writer.list_writer(["init"], 5) \
    .flat_map(add_log) \
    .flat_map(add_log)

# Extract both log and value
log, value = writer.tell()

# Convenience functions
list_writer([1, 2], "value")    # List accumulation
str_writer("msg1", "value")     # String accumulation
sum_writer(5, "value")          # Numeric accumulation
```

**When to use:**
- Logging
- Audit trails
- Metrics collection
- Debugging functional pipelines

---

### Async & Effects

#### IO - Side Effects

`IO` represents computations with side effects in a pure interface:

```python
from better_py import IO

# Wrap side effects
read_file = IO(lambda: open("file.txt").read())
write_file = IO(lambda: open("file.txt", "w").write(data))

# Transform result (lazy - doesn't execute)
read_file.map(lambda content: content.upper())

# Chain operations
read_file.flat_map(lambda content:
    IO(lambda: open("output.txt", "w").write(content))
)

# Execute
result = read_file.unsafe_run()  # Actually executes

# Error recovery
IO(lambda: 1 / 0).recover(lambda e: 0).unsafe_run()  # 0

# Retry
IO(lambda: unstable_api()).retry(3).unsafe_run()
```

**When to use:**
- File I/O
- Network requests
- Database operations
- Any side effects you want to delay/control

#### Task - Lazy Memoized Computations

`Task` provides lazy evaluation with automatic caching:

```python
from better_py import Task

# Lazy computation
task = Task(lambda: expensive_computation())

# Not executed yet
assert task.peek() is None

# Execute and cache
result = task.run()  # Executes once
result2 = task.run()  # Returns cached value

# Memoization
task.memoize(max_size=100)

# Combine tasks
task1 = Task(lambda: 42)
task2 = Task(lambda: "hello")
combined = task1.zip(task2)  # Task((42, "hello"))
```

**When to use:**
- Expensive computations
- Caching
- Lazy evaluation
- Background tasks

---

## Persistent Collections

### PersistentList

Immutable linked list with O(1) prepend:

```python
from better_py import PersistentList

# Creation
lst = PersistentList.of(1, 2, 3)
empty = PersistentList.empty()

# Operations
lst.prepend(0)        # O(1) - Add to front
lst.append(4)         # O(n) - Add to end
lst.head()            # First element
lst.tail()            # All except first
lst.get(0)            # Get by index
lst.get(-1)           # Negative indexing
lst[0]                # Bracket notation
lst.take(2)           # First 2 elements
lst.drop(2)           # All except first 2
lst.reverse()         # Reversed copy

# Functional operations
lst.map(lambda x: x * 2)
lst.filter(lambda x: x > 2)
lst.reduce(lambda acc, x: acc + x, 0)

# Conversion
lst.to_list()         # To Python list
```

### PersistentMap

Immutable dictionary with efficient updates:

```python
from better_py import PersistentMap

# Creation
m = PersistentMap.of({"a": 1, "b": 2})
empty = PersistentMap.empty()

# Operations
m.set("c", 3)                    # New map with "c": 3
m.delete("a")                    # New map without "a"
m.get("a")                       # Get value
m.get_or_else("x", "default")    # Get with default
m.contains_key("a")              # Check existence
m.size()                         # Number of entries
m.keys()                         # Get keys
m.values()                       # Get values
m.items()                        # Get key-value pairs

# Transformations
m.map_values(lambda v: v * 2)    # Transform values
m.map_keys(lambda k: k.upper())  # ⚠️ Can lose data on collisions
m.map_keys_collect(              # Safe alternative with collision handling
    lambda k: k.upper(),
    lambda k, v1, v2: f"{k}: [{v1}, {v2}]"
)

# Combine maps
m1.merge(m2)                     # Combine two maps
m.to_dict()                      # To Python dict
```

### PersistentSet

Immutable set with algebraic operations:

```python
from better_py import PersistentSet

# Creation
s = PersistentSet.of(1, 2, 3)
empty = PersistentSet.empty()

# Operations
s.add(4)                         # New set with 4
s.remove(1)                      # New set without 1
s.contains(2)                    # Check membership
s.size()                         # Number of elements

# Set operations
s1.union(s2)                     # Elements in either
s1.intersection(s2)              # Elements in both
s1.difference(s2)                 # Elements in s1 not in s2

# Conversion
s.to_set()                       # To Python set
s.to_list()                      # To Python list
```

---

## Functional Utilities

### Function Composition

```python
from better_py import compose, compose_left

# Right-to-left (mathematical)
multiply_add = compose(lambda x: x + 1, lambda x: x * 2)
multiply_add(5)  # (5 * 2) + 1 = 11

# Left-to-right (readable)
add_multiply = compose_left(lambda x: x * 2, lambda x: x + 1)
add_multiply(5)  # (5 + 1) * 2 = 12
```

### Currying

```python
from better_py import curry, partial_right, flip, _

# Curry function
@curry
def add(a: int, b: int, c: int = 10) -> int:
    return a + b + c

add_5 = add(2, 3)
add_5(1)    # 6 (uses default for c)

# Partial application from right
subtract_from_10 = partial_right(subtract, 10)
subtract_from_10(5)  # 5 - 10 = -5

# Flip arguments
flipped_subtract = flip(subtract)
flipped_subtract(10, 5)  # 5 - 10 = -5

# Placeholder with currying
@curry
def func(a, b, c):
    return (a, b, c)

# Fill second argument now, leave first and third for later
# (placeholder support depends on implementation)
```

### Pipe Operations

```python
from better_py import pipe, pipeable, flow

# Pipe value through functions
result = pipe(
    [1, 2, 3, 4, 5],
    lambda x: filter(lambda v: v > 2, x),
    lambda x: map(lambda v: v * 2, x),
    list
)  # [6, 8, 10]

# Mark functions as pipeable
@pipeable
def double(items):
    return [x * 2 for x in items]

@pipeable
def filter_gt(items, threshold):
    return [x for x in items if x > threshold]

result = [1, 2, 3, 4, 5] >> double >> filter_gt(3)

# Create reusable flows
process_data = flow(
    lambda x: filter(lambda v: v > 0, x),
    lambda x: map(lambda v: v * 2, x),
    sum
)

process_data([1, -2, 3, -4, 5])  # 18
```

---

## Common Patterns

### 1. Safe Data Access

```python
from better_py import Maybe

user_id = 123

# ❌ Nested None checks
if user_id is not None:
    user = get_user(user_id)
    if user is not None:
        address = user.get_address()
        if address is not None:
            return address.city

# ✅ With Maybe
Maybe.from_value(get_user(user_id)) \
    .map(lambda u: u.get_address()) \
    .map(lambda a: a.city) \
    .unwrap_or_else(lambda: "Unknown")
```

### 2. Chaining Failable Operations

```python
from better_py import Result

def validate_user(id: int) -> Result[User, str]:
    # Returns Result.ok(user) or Result.error(...)
    pass

def get_orders(user: User) -> Result[List[Order], str]:
    # Returns Result.ok(orders) or Result.error(...)
    pass

def calculate_total(orders: List[Order]) -> Result[int, str]:
    # Returns Result.ok(total) or Result.error(...)
    pass

# ✅ Clean chaining
total = validate_user(user_id) \
    .bind(get_orders) \
    .bind(calculate_total)

total.fold(
    on_error=lambda err: print(f"Error: {err}"),
    on_ok=lambda tot: print(f"Total: ${tot}")
)
```

### 3. Data Processing Pipeline

```python
from better_py import PersistentList, pipe
from better_py.collections import PersistentList

data = PersistentList.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

# Process through pipeline
result = data \
    .filter(lambda x: x > 5) \
    .map(lambda x: x * 2) \
    .take(3) \
    .to_list()  # [12, 14, 16]

# With pipe
result = pipe(
    [1, 2, 3, 4, 5],
    lambda x: PersistentList.from_iterable(x),
    lambda lst: lst.filter(lambda v: v > 2),
    lambda lst: lst.map(lambda v: v * 2),
    lambda lst: lst.to_list()
)
```

### 4. Form Validation with Error Accumulation

```python
from better_py import Validation

def validate_email(email: str) -> Validation[str, str]:
    if "@" in email and "." in email:
        return Validation.valid(email)
    return Validation.invalid(["Invalid email"])

def validate_age(age: int) -> Validation[str, int]:
    if 0 < age < 150:
        return Validation.valid(age)
    return Validation.invalid(["Invalid age"])

def validate_name(name: str) -> Validation[str, str]:
    if len(name) >= 2:
        return Validation.valid(name)
    return Validation.invalid(["Name too short"])

def validate_form(name: str, age: int, email: str) -> Validation[str, tuple]:
    name_v = validate_name(name)
    age_v = validate_age(age)
    email_v = validate_email(email)

    # Combine all validations
    return name_v.ap(age_v).ap(
        lambda n_a: email_v.map(lambda e: (n_a[0], a, e))
    )

result = validate_form("A", 200, "invalid")
# Invalid(["Invalid age", "Invalid email"])
```

### 5. State Machine with State Monad

```python
from better_py import State

class TrafficLight:
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"

def transition(state: str) -> State[str, str]:
    current = State.get()

    if state == TrafficLight.RED:
        return State.put(TrafficLight.GREEN)
    elif state == TrafficLight.GREEN:
        return State.put(TrafficLight.YELLOW)
    else:  # YELLOW
        return State.put(TrafficLight.RED)

# Run state machine
initial = TrafficLight.RED
final_state = transition(initial).run(initial)  # GREEN
```

---

## Best Practices

### 1. Choose the Right Monad

| Scenario | Use Monad |
|----------|-----------|
| Value might not exist | `Maybe` |
| Operation can fail with specific error | `Result` |
| Need all validation errors | `Validation` |
| Working with exceptions | `Try` |
| File/Network I/O | `IO` |
| Configuration/Environment | `Reader` |
| Logging/Metrics | `Writer` |
| Stateful computation | `State` |

### 2. Keep Functions Pure

```python
# ❌ Impure - hard to test
def process_user(user_id: int):
    user = db.query(user_id)  # Side effect
    send_email(user.email)    # Side effect
    return user

# ✅ Pure - easy to test and compose
def process_user(user: User) -> User:
    return User(
        name=user.name.upper(),
        email=user.email.lower(),
        age=user.age + 1
    )
```

### 3. Use Type Hints

```python
from better_py import Maybe, Result

def find_user(user_id: int) -> Maybe[User]:
    """Find user by ID, returns Nothing if not found."""
    pass

def divide(a: int, b: int) -> Result[float, str]:
    """Divide a by b, returns error if b is zero."""
    pass
```

### 4. Pattern Matching with fold

Always use `fold()` for exhaustive pattern matching:

```python
# Maybe
maybe.fold(
    on_nothing=lambda: print("No value"),
    on_some=lambda x: print(f"Value: {x}")
)

# Result
result.fold(
    on_error=lambda err: print(f"Error: {err}"),
    on_ok=lambda val: print(f"Success: {val}")
)

# Either
either.fold(
    on_left=lambda err: print(f"Error: {err}"),
    on_right=lambda val: print(f"Success: {val}")
)
```

### 5. Avoid Over-Nesting

```python
# ❌ Too much nesting
Maybe.from_value(get_user(id)) \
    .map(lambda u: Maybe.from_value(get_profile(u))) \
    .map(lambda p: Maybe.from_value(get_posts(p))) \
    .map(lambda posts: posts[0] if posts else None) \
    .map(lambda post: post.title)

# ✅ Use bind/flat_map to unwrap
Maybe.from_value(get_user(id)) \
    .bind(lambda u: get_profile(u)) \
    .bind(lambda p: get_posts(p)) \
    .map(lambda posts: posts[0] if posts else None) \
    .map(lambda post: post.title)
```

---

## Type Safety

better-py is fully type-hinted and works with mypy strict mode:

```bash
mypy better_py --strict
```

All protocols are `@runtime_checkable` for runtime type checking when needed.

---

## Next Steps

- Explore the [API Documentation](https://github.com/nesalia-inc/better-py) for complete API reference
- Check out the [test files](https://github.com/nesalia-inc/better-py/tree/main/tests) for more examples
- Read about [functional programming patterns](https://github.com/nesalia-inc/better-py) for deeper understanding
