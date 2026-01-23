"""Reader monad for dependency injection.

The Reader monad represents a computation that reads from a shared environment,
useful for dependency injection and configuration.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from better_py.protocols import Mappable

E = TypeVar("E")  # Environment type
A = TypeVar("A")  # Result type
B = TypeVar("B")


class Reader(Mappable[A], Generic[E, A]):
    """Reader monad for dependency injection.

    A Reader is a function from an environment to a value, representing
    a computation that depends on a shared environment.

    Type Parameters:
        E: The environment type
        A: The result type

    Example:
        >>> ask = Reader(lambda env: env)
        >>> local = Reader(lambda env: env["key"])
    """

    def __init__(self, run: Callable[[E], A]):
        """Create a Reader from a function.

        Args:
            run: Function from environment to value

        Example:
            >>> Reader(lambda env: env["key"])
        """
        self._run = run

    def run(self, env: E) -> A:
        """Run the Reader with an environment.

        Args:
            env: The environment

        Returns:
            The result value

        Example:
            >>> reader.run(config)
        """
        return self._run(env)

    def map(self, f: Callable[[A], B]) -> Reader[E, B]:
        """Apply a function to the result.

        Args:
            f: Function to apply

        Returns:
            A Reader that applies f to the result

        Example:
            >>> reader.map(lambda x: x * 2)
        """
        return Reader(lambda env: f(self._run(env)))

    def flat_map(self, f: Callable[[A], Reader[E, B]]) -> Reader[E, B]:
        """Chain operations that return Reader.

        Args:
            f: Function that takes a value and returns a Reader

        Returns:
            A Reader that chains the computations

        Example:
            >>> reader.flat_map(lambda x: Reader(lambda env: x + env["offset"]))
        """
        return Reader(lambda env: f(self._run(env)).run(env))

    @staticmethod
    def ask() -> Reader[E, E]:
        """Get the environment.

        Returns:
            A Reader that returns the environment

        Example:
            >>> Reader.ask().run(env)  # Returns env
        """
        return Reader(lambda env: env)

    def local(self, f: Callable[[E], E]) -> Reader[E, A]:
        """Modify the environment for this computation.

        Args:
            f: Function to modify the environment

        Returns:
            A Reader that runs with modified environment

        Example:
            >>> reader.local(lambda env: {**env, "key": "value"})
        """
        return Reader(lambda env: self._run(f(env)))

    def __repr__(self) -> str:
        return f"Reader({self._run!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Reader):
            return False
        return self._run == other._run


__all__ = ["Reader"]
