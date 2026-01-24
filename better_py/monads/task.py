"""Task monad for lazy computations.

The Task monad represents lazy computations that can be executed
later, supporting memoization and composition.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import IO

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Task(Mappable[T], Generic[T]):
    """Task monad for lazy computations.

    A Task represents a lazy computation that can be executed later.
    Once executed, the result is memoized for subsequent accesses.

    Type Parameters:
        T: The result type

    Example:
        >>> task = Task(lambda: 42)
        >>> task.run()  # 42
    """

    _compute: Callable[[], T]
    _cache: dict[int, T] = field(default_factory=dict, hash=False)

    def run(self) -> T:
        """Execute the task and cache the result.

        Returns:
            The result of the computation

        Example:
            >>> Task(lambda: 42).run()  # 42
        """
        cache_key = id(self._compute)
        if cache_key not in self._cache:
            self._cache[cache_key] = self._compute()
        return self._cache[cache_key]

    def peek(self) -> T | None:
        """Get the cached result without executing if not cached.

        Returns:
            The cached result, or None if not yet executed

        Example:
            >>> task = Task(lambda: 42)
            >>> task.peek()  # None
            >>> task.run()
            >>> task.peek()  # 42
        """
        cache_key = id(self._compute)
        return self._cache.get(cache_key)

    def is_cached(self) -> bool:
        """Check if the result is cached.

        Returns:
            True if cached, False otherwise

        Example:
            >>> task = Task(lambda: 42)
            >>> task.is_cached()  # False
            >>> task.run()
            >>> task.is_cached()  # True
        """
        cache_key = id(self._compute)
        return cache_key in self._cache

    def map(self, f: Callable[[T], U]) -> Task[U]:
        """Apply a function to the result.

        Args:
            f: Function to apply

        Returns:
            A new Task that applies f to the result

        Example:
            >>> Task(lambda: 5).map(lambda x: x * 2).run()  # 10
        """
        return Task(lambda: f(self.run()))

    def flat_map(self, f: Callable[[T], Task[U]]) -> Task[U]:
        """Chain task computations.

        Args:
            f: Function that takes a value and returns a Task

        Returns:
            A new Task that chains the computations

        Example:
            >>> Task(lambda: 5).flat_map(lambda x: Task(lambda: x * 2)).run()  # 10
        """
        return Task(lambda: f(self.run()).run())

    def and_then(self, other: Task[U]) -> Task[U]:
        """Sequence two task computations, discarding the first result.

        Args:
            other: The next task computation

        Returns:
            A new Task that runs both, returning the second result

        Example:
            >>> Task(lambda: 5).and_then(Task(lambda: 10)).run()  # 10
        """
        return Task(lambda: (self.run(), other.run())[1])

    def filter(self, predicate: Callable[[T], bool]) -> Task[T | None]:
        """Filter the result.

        Args:
            predicate: Function to test the value

        Returns:
            Task containing the value if predicate passes, None otherwise

        Example:
            >>> Task(lambda: 5).filter(lambda x: x > 3).run()  # 5
            >>> Task(lambda: 2).filter(lambda x: x > 3).run()  # None
        """
        return Task(lambda: self.run() if predicate(self.run()) else None)

    def zip(self, other: Task[U]) -> Task[tuple[T, U]]:
        """Combine two tasks into a tuple.

        Args:
            other: The other task

        Returns:
            A Task containing both results as a tuple

        Example:
            >>> Task(lambda: 5).zip(Task(lambda: "hello")).run()  # (5, "hello")
        """
        return Task(lambda: (self.run(), other.run()))

    def memoize(self, max_size: int | None = None) -> Task[T]:
        """Create a memoized version of this task.

        Args:
            max_size: Maximum cache size, None for unlimited

        Returns:
            A new Task with memoization

        Example:
            >>> expensive_task = Task(lambda: expensive_computation()).memoize()
        """
        cache: dict[int, T] = {}

        @lru_cache(maxsize=max_size if max_size is not None else 128)
        def cached_compute() -> T:
            return self._compute()

        return Task(cached_compute, cache)

    @staticmethod
    def pure(value: T) -> Task[T]:
        """Lift a pure value into Task.

        Args:
            value: The value to lift

        Returns:
            A Task that produces the value

        Example:
            >>> Task.pure(42).run()  # 42
        """
        return Task(lambda: value)

    @staticmethod
    def delay(value: T | Callable[[], T]) -> Task[T]:
        """Create a delayed computation.

        Args:
            value: Either a value or a function producing a value

        Returns:
            A Task that delays evaluation

        Example:
            >>> Task.delay(lambda: expensive_computation()).run()
        """
        if callable(value):
            return Task(value)
        return Task(lambda: value)

    @staticmethod
    def from_io(io_value: "IO[T]") -> "Task[T]":
        """Create a Task from an IO computation.

        Args:
            io_value: An IO value to convert

        Returns:
            A Task that runs the IO computation

        Example:
            >>> from better_py.monads import IO
            >>> Task.from_io(IO(lambda: 42)).run()  # 42
        """
        return Task(io_value.unsafe_run)

    @override
    def __repr__(self) -> str:
        cached = self.is_cached()
        return f"Task(cached={cached})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return False
        # If both are cached, compare cached results (no execution)
        # Otherwise compare by function identity to avoid executing side effects
        if self.is_cached() and other.is_cached():
            return self.peek() == other.peek()
        return self._compute is other._compute


__all__ = ["Task"]
