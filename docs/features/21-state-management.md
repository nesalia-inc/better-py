# State Management - Immutable State Updates

Manage application state with immutable updates and explicit transitions.

## Overview

State management enables:
- Predictable state transitions
- Time travel debugging
- Undo/redo functionality
- Clear state history
- Thread-safe updates

## Immutable Store

```python
from dataclasses import dataclass, replace
from typing import Callable, TypeVar, Generic
from typing import Any

T = TypeVar('T')

class Store(Generic[T]):
    """Immutable state store"""

    def __init__(self, initial_state: T):
        self._state = initial_state
        self._listeners: list[Callable[[T], None]] = []

    def get_state(self) -> T:
        """Get current state"""
        return self._state

    def update(self, updater: Callable[[T], T]) -> T:
        """Update state immutably"""

        new_state = updater(self._state)
        self._state = new_state

        # Notify listeners
        for listener in self._listeners:
            listener(new_state)

        return new_state

    def subscribe(self, listener: Callable[[T], None]) -> Callable:
        """Subscribe to state changes"""

        self._listeners.append(listener)

        # Return unsubscribe function
        def unsubscribe():
            self._listeners.remove(listener)

        return unsubscribe

    def replace(self, new_state: T) -> T:
        """Replace entire state"""
        return self.update(lambda _: new_state)


# === Usage ===

@dataclass(frozen=True)
class AppState:
    counter: int
    user: str | None
    loading: bool

# Create store
store = Store(AppState(counter=0, user=None, loading=False))

# Update state
def increment(state: AppState) -> AppState:
    return replace(state, counter=state.counter + 1)

store.update(increment)
print(store.get_state())  # AppState(counter=1, user=None, loading=False)
```

## Action-Based State

```python
from typing import Protocol

class Action(Protocol):
    """Action protocol"""

    def apply(self, state: T) -> T:
        """Apply action to state"""
        ...


class ActionStore(Generic[T]):
    """Store with actions"""

    def __init__(self, initial_state: T):
        self._state = initial_state
        self._history: list[T] = [initial_state]
        self._listeners: list[Callable[[T], None]] = []

    def dispatch(self, action: Action) -> T:
        """Dispatch action"""

        new_state = action.apply(self._state)
        self._state = new_state
        self._history.append(new_state)

        for listener in self._listeners:
            listener(new_state)

        return new_state

    def get_state(self) -> T:
        return self._state

    def get_history(self) -> list[T]:
        """Get state history"""
        return self._history.copy()

    def undo(self) -> T | None:
        """Undo last action"""

        if len(self._history) > 1:
            self._history.pop()
            self._state = self._history[-1]
            return self._state

        return None


# === Usage ===

@dataclass(frozen=True)
class IncrementAction:
    amount: int

    def apply(self, state: AppState) -> AppState:
        return replace(state, counter=state.counter + self.amount)

@dataclass(frozen=True)
class SetUserAction:
    user: str

    def apply(self, state: AppState) -> AppState:
        return replace(state, user=self.user)

store = ActionStore(AppState(counter=0, user=None, loading=False))

store.dispatch(IncrementAction(5))
store.dispatch(IncrementAction(3))
print(store.get_state())  # AppState(counter=8, ...)

store.dispatch(SetUserAction("Alice"))
print(store.get_state())  # AppState(counter=8, user="Alice", ...)

# Undo
store.undo()
print(store.get_state())  # AppState(counter=8, user=None, ...)
```

## Reducer Pattern

```python
from typing import Callable, TypeVar

A = TypeVar('A')  # Action type

Reducer = Callable[[T, A], T]

class ReducerStore(Generic[T, A]):
    """Store with reducer pattern"""

    def __init__(self, initial_state: T, reducer: Reducer):
        self._state = initial_state
        self._reducer = reducer
        self._history: list[T] = [initial_state]

    def dispatch(self, action: A) -> T:
        """Dispatch action through reducer"""

        new_state = self._reducer(self._state, action)
        self._state = new_state
        self._history.append(new_state)

        return new_state

    def get_state(self) -> T:
        return self._state


# === Usage ===

from enum import Enum

class CounterAction(Enum):
    INCREMENT = "increment"
    DECREMENT = "decrement"
    RESET = "reset"


def counter_reducer(state: int, action: CounterAction) -> int:
    """Counter reducer"""

    match action:
        case CounterAction.INCREMENT:
            return state + 1
        case CounterAction.DECREMENT:
            return state - 1
        case CounterAction.RESET:
            return 0

store = ReducerStore(0, counter_reducer)

store.dispatch(CounterAction.INCREMENT)
store.dispatch(CounterAction.INCREMENT)
print(store.get_state())  # 2

store.dispatch(CounterAction.RESET)
print(store.get_state())  # 0
```

## Selectors

```python
from typing import Callable

Selector = Callable[[T], Any]

class SelectorStore(Generic[T]):
    """Store with computed selectors"""

    def __init__(self, initial_state: T):
        self._state = initial_state
        self._selectors: dict[str, Callable[[T], Any]] = {}

    def get_state(self) -> T:
        return self._state

    def update(self, updater: Callable[[T], T]) -> T:
        self._state = updater(self._state)
        return self._state

    def select(self, selector: Callable[[T], R]) -> R:
        """Select computed value from state"""
        return selector(self._state)

    def memoize(self, name: str, selector: Callable[[T], R]) -> Callable[[], R]:
        """Memoize selector"""

        self._selectors[name] = selector

        def get_memoized() -> R:
            return selector(self._state)

        return get_memoized


# === Usage ===

@dataclass(frozen=True)
class UserState:
    users: list[dict]

store = SelectorStore(UserState(users=[
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Charlie", "active": True}
]))

# Define selectors
active_users = lambda state: [u for u in state.users if u["active"]]
user_count = lambda state: len(state.users)

# Use selectors
print(store.select(active_users))
# [{"id": 1, ...}, {"id": 3, ...}]

print(store.select(user_count))  # 3
```

## Computed State

```python
from typing import Any

class ComputedStore(SelectorStore[T]):
    """Store with computed values"""

    def __init__(self, initial_state: T):
        super().__init__(initial_state)
        self._computed: dict[str, Any] = {}
        self._dirty = True

    def update(self, updater: Callable[[T], T]) -> T:
        result = super().update(updater)
        self._dirty = True
        return result

    def get_computed(self, name: str, compute: Callable[[T], Any]) -> Any:

        # Recompute if dirty
        if self._dirty or name not in self._computed:
            self._computed[name] = compute(self._state)
            self._dirty = False

        return self._computed[name]


# === Usage ===

@dataclass(frozen=True)
class CartState:
    items: list[dict]

store = ComputedStore(CartState(items=[
    {"name": "Item 1", "price": 10, "quantity": 2},
    {"name": "Item 2", "price": 20, "quantity": 1}
]))

# Computed total
total = store.get_computed(
    "total",
    lambda state: sum(item["price"] * item["quantity"] for item in state.items)
)

print(total)  # 40

# Update state
store.update(lambda state: replace(state, items=[
    *state.items,
    {"name": "Item 3", "price": 15, "quantity": 1}
]))

# Recomputed automatically
total = store.get_computed("total", lambda state: ...)
print(total)  # 55
```

## Time Travel

```python
class TimeTravelStore(Store[T]):
    """Store with time travel capabilities"""

    def __init__(self, initial_state: T, max_history: int = 100):
        super().__init__(initial_state)
        self._history: list[T] = [initial_state]
        self._future: list[T] = []
        self._max_history = max_history

    def update(self, updater: Callable[[T], T]) -> T:
        result = super().update(updater)

        # Add to history
        self._history.append(result)

        # Limit history size
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Clear future on new action
        self._future.clear()

        return result

    def undo(self) -> T | None:
        """Undo to previous state"""

        if len(self._history) > 1:
            current = self._history.pop()
            self._future.append(current)
            self._state = self._history[-1]

            # Notify listeners
            for listener in self._listeners:
                listener(self._state)

            return self._state

        return None

    def redo(self) -> T | None:
        """Redo to next state"""

        if self._future:
            state = self._future.pop()
            self._history.append(state)
            self._state = state

            # Notify listeners
            for listener in self._listeners:
                listener(self._state)

            return self._state

        return None

    def jump_to(self, index: int) -> T:
        """Jump to specific history index"""

        if 0 <= index < len(self._history):
            self._state = self._history[index]
            self._future = self._history[index + 1:]

            for listener in self._listeners:
                listener(self._state)

            return self._state

        raise IndexError("Invalid history index")


# === Usage ===

store = TimeTravelStore(AppState(counter=0, user=None, loading=False))

store.update(lambda s: replace(s, counter=1))
store.update(lambda s: replace(s, counter=2))
store.update(lambda s: replace(s, counter=3))

print(store.get_state().counter)  # 3

store.undo()
print(store.get_state().counter)  # 2

store.undo()
print(store.get_state().counter)  # 1

store.redo()
print(store.get_state().counter)  # 2
```

## DX Benefits

✅ **Predictable**: State changes are explicit
✅ **Debuggable**: Full history of changes
✅ **Undo/Redo**: Built-in time travel
✅ **Testable**: Pure reducer functions
✅ **Observable**: Subscribe to changes

## Best Practices

```python
# ✅ Good: Immutable updates
def update_user(state, user):
    return replace(state, user=user)

# ✅ Good: Actions for complex updates
class UpdateUserAction:
    def apply(self, state):
        return replace(state, user=self.user)

# ✅ Good: Selectors for computed values
active_users = lambda state: [u for u in state.users if u.active]

# ❌ Bad: Mutating state
state.user = new_user  # Wrong!

# ❌ Bad: Unclear transitions
# Use named actions/reducers instead
```
