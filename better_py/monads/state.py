"""State monad for stateful computations.

The State monad represents a stateful computation as a function from
state to a (value, new state) pair, useful for managing state.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from better_py.protocols import Mappable

S = TypeVar("S")  # State type
A = TypeVar("A")  # Result type
B = TypeVar("B")


class State(Mappable[A], Generic[S, A]):
    """State monad for stateful computations.

    A State is a function from state to a (value, new state) pair,
    representing a stateful computation.

    Type Parameters:
        S: The state type
        A: The result type

    Example:
        >>> get = State(lambda s: (s, s))
        >>> put = State(lambda s: (None, new_state))
    """

    def __init__(self, run: Callable[[S], tuple[A, S]]):
        """Create a State from a function.

        Args:
            run: Function from state to (value, new state)

        Example:
            >>> State(lambda s: (s * 2, s))
        """
        self._run = run

    def run(self, initial: S) -> tuple[A, S]:
        """Run the State with an initial state.

        Args:
            initial: The initial state

        Returns:
            Tuple of (result value, new state)

        Example:
            >>> state.run(0)
        """
        return self._run(initial)

    def eval(self, initial: S) -> A:
        """Run the State and get only the result value.

        Args:
            initial: The initial state

        Returns:
            The result value

        Example:
            >>> state.eval(0)
        """
        value, _ = self._run(initial)
        return value

    def execute(self, initial: S) -> S:
        """Run the State and get only the final state.

        Args:
            initial: The initial state

        Returns:
            The final state

        Example:
            >>> state.execute(0)
        """
        _, state = self._run(initial)
        return state

    def map(self, f: Callable[[A], B]) -> State[S, B]:
        """Apply a function to the result value.

        Args:
            f: Function to apply

        Returns:
            A State that applies f to the result value

        Example:
            >>> state.map(lambda x: x * 2)
        """
        def mapped(s: S) -> tuple[B, S]:
            value, new_state = self._run(s)
            return f(value), new_state

        return State(mapped)

    def flat_map(self, f: Callable[[A], State[S, B]]) -> State[S, B]:
        """Chain operations that return State.

        Args:
            f: Function that takes a value and returns a State

        Returns:
            A State that chains the computations

        Example:
            >>> state.flat_map(lambda x: State(lambda s: (x + s, s)))
        """
        def chained(s: S) -> tuple[B, S]:
            value, new_state = self._run(s)
            return f(value)._run(new_state)

        return State(chained)

    @staticmethod
    def get() -> State[S, S]:
        """Get the current state.

        Returns:
            A State that returns the state as the value

        Example:
            >>> State.get().run(42)  # (42, 42)
        """
        return State(lambda s: (s, s))

    @staticmethod
    def put(state: S) -> State[S, None]:
        """Replace the state with a new value.

        Args:
            state: The new state

        Returns:
            A State that sets the state

        Example:
            >>> State.put(100).run(0)  # (None, 100)
        """
        return State(lambda _s: (None, state))

    @staticmethod
    def modify(f: Callable[[S], S]) -> State[S, None]:
        """Modify the state with a function.

        Args:
            f: Function to modify the state

        Returns:
            A State that modifies the state

        Example:
            >>> State.modify(lambda x: x + 1).run(0)  # (None, 1)
        """
        return State(lambda s: (None, f(s)))

    def __repr__(self) -> str:
        return f"State({self._run!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return False
        return self._run == other._run


__all__ = ["State"]
