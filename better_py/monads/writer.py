"""Writer monad for logging and accumulation.

The Writer monad represents a computation that produces a value along
with a log or accumulator, useful for logging and tracking.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

W = TypeVar("W")  # Log/accumulator type (must be a monoid)
A = TypeVar("A")  # Value type
B = TypeVar("B")


@dataclass(frozen=True, slots=True)
class Writer(Mappable[A], Generic[W, A]):
    """Writer monad for logging and accumulation.

    A Writer is a pair of a value and a log, representing a computation
    that produces a value while accumulating a log.

    Type Parameters:
        W: The log type (must be a monoid, e.g., list, str)
        A: The value type

    Example:
        >>> writer = Writer(["log1", "log2"], 42)
        >>> writer.tell()  # (["log1", "log2"], 42)
    """

    log: W
    value: A

    def tell(self) -> tuple[W, A]:
        """Extract the log and value.

        Returns:
            Tuple of (log, value)

        Example:
            >>> writer.tell()  # (log, value)
        """
        return self.log, self.value

    def map(self, f: Callable[[A], B]) -> Writer[W, B]:
        """Apply a function to the value.

        Args:
            f: Function to apply

        Returns:
            A Writer with the function applied to the value

        Example:
            >>> writer.map(lambda x: x * 2)
        """
        return Writer(self.log, f(self.value))

    def flat_map(self, f: Callable[[A], Writer[W, B]]) -> Writer[W, B]:
        """Chain operations that return Writer.

        Args:
            f: Function that takes a value and returns a Writer

        Returns:
            A Writer that chains the computations and accumulates logs

        Example:
            >>> writer.flat_map(lambda x: Writer(["new_log"], x + 1))
        """
        result = f(self.value)
        # Combine logs (assuming W is a monoid with +)
        combined_log = self.log + result.log  # type: ignore
        return Writer(combined_log, result.value)

    def listen(self) -> Writer[W, tuple[W, A]]:
        """Extract the log and value as a pair.

        Returns:
            A Writer containing (log, value) as the value

        Example:
            >>> writer.listen().tell()  # ((log, value), log)
        """
        return Writer(self.log, (self.log, self.value))

    def pass_(self) -> "Writer[W, W]":
        """Pass the log through unchanged.

        Returns:
            A Writer with the log as both log and value

        Example:
            >>> writer.pass_().tell()  # (log, log)
        """
        return Writer(self.log, self.log)

    @staticmethod
    def tell_log(log: W) -> Writer[W, None]:
        """Create a Writer that only logs.

        Args:
            log: The log to write

        Returns:
            A Writer with no value

        Example:
            >>> Writer.tell_log(["log entry"])
        """
        return Writer(log, None)

    @override
    def __repr__(self) -> str:
        return f"Writer({self.log!r}, {self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Writer):
            return False
        return self.log == other.log and self.value == other.value  # type: ignore[no-any-return]


__all__ = ["Writer"]
