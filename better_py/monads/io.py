"""IO monad for side-effecting computations.

The IO monad encapsulates side effects, allowing impure operations
to be represented as pure values.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, override

from better_py.protocols import Mappable

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class IO(Mappable[T], Generic[T]):
    """IO monad for side-effecting computations.

    An IO represents a computation that can produce side effects.
    The computation is only executed when unsafe_run is called.

    Type Parameters:
        T: The result type

    Example:
        >>> io = IO(lambda: print("Hello"))
        >>> io.unsafe_run()  # Prints "Hello"
    """

    _value: Callable[[], T]

    def unsafe_run(self) -> T:
        """Execute the IO computation.

        Returns:
            The result of the computation

        Example:
            >>> IO(lambda: 42).unsafe_run()  # 42
        """
        return self._value()

    def map(self, f: Callable[[T], U]) -> IO[U]:
        """Apply a function to the result.

        Args:
            f: Function to apply

        Returns:
            A new IO that applies f to the result

        Example:
            >>> IO(lambda: 5).map(lambda x: x * 2).unsafe_run()  # 10
        """
        return IO(lambda: f(self._value()))

    def flat_map(self, f: Callable[[T], IO[U]]) -> IO[U]:
        """Chain IO computations.

        Args:
            f: Function that takes a value and returns an IO

        Returns:
            A new IO that chains the computations

        Example:
            >>> IO(lambda: 5).flat_map(lambda x: IO(lambda: x * 2)).unsafe_run()  # 10
        """
        return IO(lambda: f(self._value()).unsafe_run())

    def and_then(self, other: IO[U]) -> IO[U]:
        """Sequence two IO computations, discarding the first result.

        Args:
            other: The next IO computation

        Returns:
            A new IO that runs both, returning the second result

        Example:
            >>> IO(lambda: print("First")).and_then(IO(lambda: print("Second")))
        """
        return IO(lambda: (self._value(), other.unsafe_run())[1])

    def filter(self, predicate: Callable[[T], bool]) -> IO[T | None]:
        """Filter the result.

        Args:
            predicate: Function to test the value

        Returns:
            IO containing the value if predicate passes, None otherwise

        Example:
            >>> IO(lambda: 5).filter(lambda x: x > 3).unsafe_run()  # 5
            >>> IO(lambda: 2).filter(lambda x: x > 3).unsafe_run()  # None
        """
        return IO(lambda: self._value() if predicate(self._value()) else None)

    def recover(self, f: Callable[[Exception], T]) -> IO[T]:
        """Recover from exceptions.

        Args:
            f: Function to handle exceptions

        Returns:
            An IO that catches exceptions and applies f

        Example:
            >>> IO(lambda: 1 / 0).recover(lambda _: 0).unsafe_run()  # 0
        """
        def handler():
            try:
                return self._value()
            except Exception as e:
                return f(e)

        return IO(handler)

    def retry(self, times: int) -> IO[T]:
        """Retry the computation on failure.

        Args:
            times: Number of times to retry

        Returns:
            An IO that retries the computation

        Example:
            >>> attempts = 0
            >>> io = IO(lambda: 1 if (global attempts) >= 1 else exec("attempts += 1") or 1/0)
        """
        def handler():
            last_error = None
            for _ in range(times + 1):
                try:
                    return self._value()
                except Exception as e:
                    last_error = e
            raise last_error  # type: ignore

        return IO(handler)

    @staticmethod
    def pure(value: T) -> IO[T]:
        """Lift a pure value into IO.

        Args:
            value: The value to lift

        Returns:
            An IO that produces the value

        Example:
            >>> IO.pure(42).unsafe_run()  # 42
        """
        return IO(lambda: value)

    @staticmethod
    def delay(value: T | Callable[[], T]) -> IO[T]:
        """Create a delayed computation.

        Args:
            value: Either a value or a function producing a value

        Returns:
            An IO that delays evaluation

        Example:
            >>> IO.delay(lambda: expensive_computation()).unsafe_run()
        """
        if callable(value):
            return IO(value)
        return IO(lambda: value)

    @override
    def __repr__(self) -> str:
        return "IO(...)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IO):
            return False
        # IO instances are compared by their results
        return self._value() == other._value()


__all__ = ["IO"]
