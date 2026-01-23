# State - State Management Monad

Manage state transitions with explicit state threading.

## Overview

`State` represents a stateful computation:
- `State(func)` - Function that takes state and returns (value, new_state)

## Basic Usage

```python
from mfn import State

# Create State
def increment(state: int):
    new_state = state + 1
    return (new_state, new_state)

state = State(increment)

# Run with initial state
value, new_state = state.run(0)
# value: 1
# new_state: 1
```

## Transformation

```python
from mfn import State

# Map: Transform produced value
state = State(lambda s: (s * 2, s + 1))

result = state.map(lambda x: x + 10)
# State(lambda s: (s * 2 + 10, s + 1))

# Then: Chain stateful computations
def double(s: int):
    return (s * 2, s * 2)

def add_five(s: int):
    return (s + 5, s + 5)

state = State(double).then(State(add_five))

value, final_state = state.run(10)
# value: 25 (10 * 2 = 20, 20 + 5 = 25)
# final_state: 25
```

## Get and Put

```python
from mfn import State

# Get current state
get_state = State(lambda s: (s, s))

# Put new state
def put_state(new_state):
    return State(lambda s: (None, new_state))

# Modify state
def modify_state(func):
    return State(lambda s: (None, func(s)))


# Use
state = get_state.then(lambda s: put_state(s * 2))

value, final_state = state.run(5)
# value: None
# final_state: 10

# Or with modify
state = modify_state(lambda s: s * 2)

value, final_state = state.run(5)
# value: None
# final_state: 10
```

## Composing State Operations

```python
from mfn import State

def increment(state: int):
    value = state + 1
    return (value, value)

def double(state: int):
    value = state * 2
    return (value, value)


def process():
    """Chain multiple state operations"""

    def inner(state: int):
        # Increment
        value1, state1 = increment(state)

        # Double
        value2, state2 = double(state1)

        # Return final
        return (value2, state2)

    return State(inner)


# Or with helpers
from mfn import State

def process_chain():
    """Chain using State API"""

    return (
        State(increment)
        .then(State(double))
        .then(State(increment))
    )


# Use
state = process_chain()
value, final_state = state.run(0)

# value: 1 -> 2 -> 3
# final_state: 3
```

## Complex State

```python
from mfn import State
from dataclasses import dataclass

@dataclass
class Counter:
    value: int
    operations: int


def increment_counter(state: Counter):
    return (
        Counter(state.value + 1, state.operations + 1),
        Counter(state.value + 1, state.operations + 1)
    )


def reset_counter(state: Counter):
    return (
        Counter(0, state.operations + 1),
        Counter(0, state.operations + 1)
    )


# Chain
def process_counter():
    return (
        State(increment_counter)
        .then(State(increment_counter))
        .then(State(reset_counter))
        .then(State(increment_counter))
    )


counter = Counter(0, 0)
result, final_counter = process_counter().run(counter)

# final_counter: Counter(value=1, operations=4)
```

## State Helpers

```python
from mfn import State

class StateHelper:
    """Common state operations"""

    @staticmethod
    def get():
        """Get current state"""

        return State(lambda s: (s, s))

    @staticmethod
    def puts(value):
        """Put value (return value, set state to value)"""

        return State(lambda s: (value, value))

    @staticmethod
    def modify(func):
        """Modify state with function"""

        return State(lambda s: (func(s), func(s)))

    @staticmethod
    def gets(func):
        """Get computed value from state"""

        return State(lambda s: (func(s), s))


# Use
from mfn import StateHelper

def operations():
    return (
        StateHelper.gets(lambda s: s * 2)  # Get s * 2
        .then(StateHelper.modify(lambda x: x + 1))  # Increment state
        .then(StateHelper.get())  # Get final state
    )


value, final_state = operations().run(5)

# value progression: 10 -> None -> 6
# final_state: 6
```

## Multiple State Values

```python
from mfn import State
from typing import tuple

def multi_state(state: tuple[int, str]):

    count, name = state

    # Increment count
    new_count = count + 1

    # Capitalize name
    new_name = name.upper()

    return ((new_count, new_name), (new_count, new_name))


# Use
state = State(multi_state)
value, final_state = state.run((5, "alice"))

# value: (6, "ALICE")
# final_state: (6, "ALICE")
```

## State Transactions

```python
from mfn import State

class Transaction:
    """State transaction with rollback"""

    def __init__(self):
        self.initial_state = None

    def begin(self):
        """Start transaction"""

        def inner(state):
            self.initial_state = state
            return (None, state)

        return State(inner)

    def commit(self):
        """Commit transaction"""

        return State(lambda s: (s, s))

    def rollback(self):
        """Rollback to initial state"""

        def inner(state):
            return (None, self.initial_state)

        return State(inner)


# Use
def safe_operation():

    return (
        Transaction().begin()
        .then(State(increment_counter))
        .then(lambda _: State(lambda s: (
            s if s.value < 10 else Transaction().rollback().run(s)[1]
        , s
        )))
    )
```

## DX Benefits

✅ **Explicit**: State is visible
✅ **Predictable**: State transitions are clear
✅ **Testable**: Pure state functions
✅ **Composable**: Chain state operations
✅ **Immutable**: State is never mutated

## Best Practices

```python
# ✅ Good: Return (value, new_state)
def operation(state):
    new_state = transform(state)
    return (new_state, new_state)

# ✅ Good: Chain state operations
State(op1).then(State(op2)).then(State(op3))

# ✅ Good: Use helpers
StateHelper.get()
StateHelper.modify(lambda s: s + 1)

# ❌ Bad: Mutating state
# Always return new state

# ❌ Bad: Hidden state
# Make state explicit in function signature
```
