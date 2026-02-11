"""Either monad for error handling with two variants.

The Either monad represents either a Left value (typically an error) or
a Right value (typically a success).

Usage:
    >>> left = Left("Error occurred")
    >>> right = Right(42)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

L = TypeVar("L")  # Left type (typically error)
R = TypeVar("R")  # Right type (typically success)
U = TypeVar("U")


class Either(Mappable[R], Generic[L, R]):
    """Base class for Either monad.

    Type Parameters:
        L: The Left type (typically error)
        R: The Right type (typically success)

    Usage:
        >>> left = Left("Error occurred")
        >>> right = Right(42)
    """

    @staticmethod
    def left(value: L) -> Either[L, R]:
        """Create a Left Either containing an error/value.

        >>> Either.left("Error occurred")
        Left('Error occurred')
        """
        return Left(value)

    @staticmethod
    def right(value: R) -> Either[L, R]:
        """Create a Right Either containing a success value.

        >>> Either.right(42)
        Right(42)
        """
        return Right(value)

    # Abstract methods that subclasses must implement
    def is_left(self) -> bool:
        """Check if this is Left variant."""
        raise NotImplementedError()

    def is_right(self) -> bool:
        """Check if this is Right variant."""
        raise NotImplementedError()

    def unwrap_left(self) -> L:
        """Get the Left value, raising an error if Right."""
        raise NotImplementedError()

    def unwrap_right(self) -> R:
        """Get the Right value, raising an error if Left."""
        raise NotImplementedError()

    def swap(self) -> Either[R, L]:
        """Swap Left and Right."""
        raise NotImplementedError()

    def map(self, f: Callable[[R], U]) -> Either[L, U]:
        """Apply a function to the Right value."""
        raise NotImplementedError()

    def map_left(self, f: Callable[[L], L]) -> Either[L, R]:
        """Apply a function to the Left value."""
        raise NotImplementedError()

    def flat_map(self, f: Callable[[R], Either[L, U]]) -> Either[L, U]:
        """Chain operations that return Either."""
        raise NotImplementedError()

    def ap(self, fn: Either[L, Callable[[R], U]]) -> Either[L, U]:
        """Apply an Either containing a function to this Either."""
        raise NotImplementedError()

    @staticmethod
    def lift2(f: Callable[[R, U], object], ma: Either[L, R], mb: Either[L, U]) -> Either[L, object]:
        """Lift a binary function to operate on Either values."""
        curried = ma.map(lambda x: lambda y: f(x, y))
        return mb.ap(curried)

    @staticmethod
    def lift3(f: Callable[[R, U, object], object], ma: Either[L, R], mb: Either[L, U], mc: Either[L, object]) -> Either[L, object]:
        """Lift a ternary function to operate on Either values."""
        curried = ma.map(lambda x: lambda y: lambda z: f(x, y, z))
        return mc.ap(mb.ap(curried))

    @staticmethod
    def zip(*eithers: Either[L, R]) -> Either[L, tuple[R, ...]]:
        """Combine multiple Either values into a tuple."""
        vals: list[R] = []
        for e in eithers:
            if e.is_left():
                return Left(e.unwrap_left())
            vals.append(e.unwrap_right())
        return Right(tuple(vals))

    def fold(self, on_left: Callable[[L], U], on_right: Callable[[R], U]) -> U:
        """Fold both cases into a single value."""
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class Left(Either[L, R], Generic[L, R]):
    """Left variant of Either, typically containing an error value.

    >>> left = Left("Error occurred")
    >>> left.is_left()
    True
    >>> left.unwrap_left()
    'Error occurred'
    """

    _value: L

    @override
    def is_left(self) -> bool:
        """Check if this is Left variant.

        >>> Left("error").is_left()
        True
        """
        return True

    @override
    def is_right(self) -> bool:
        """Check if this is Right variant.

        >>> Left("error").is_right()
        False
        """
        return False

    @override
    def unwrap_left(self) -> L:
        """Get the Left value.

        >>> Left("error").unwrap_left()
        'error'
        """
        return self._value

    @override
    def unwrap_right(self) -> R:
        """Get the Right value, raising an error."""
        raise ValueError(f"Cannot unwrap_right Left: {self._value}")

    @override
    def swap(self) -> Either[R, L]:
        """Swap Left and Right.

        >>> Left(1).swap()
        Right(1)
        """
        return Right(self._value)

    @override
    def map(self, f: Callable[[R], U]) -> Either[L, U]:
        """Apply a function to the Right value (no-op for Left).

        >>> Left("error").map(lambda x: x * 2)
        Left('error')
        """
        return self

    @override
    def map_left(self, f: Callable[[L], L]) -> Either[L, R]:
        """Apply a function to the Left value.

        >>> Left("error").map_left(str.upper)
        Left('ERROR')
        """
        return Left(f(self._value))

    @override
    def flat_map(self, f: Callable[[R], Either[L, U]]) -> Either[L, U]:
        """Chain operations that return Either (short-circuits for Left)."""
        return self

    @override
    def ap(self, fn: Either[L, Callable[[R], U]]) -> Either[L, U]:
        """Apply an Either containing a function to this Either."""
        return self

    @override
    def fold(self, on_left: Callable[[L], U], on_right: Callable[[R], U]) -> U:
        """Fold both cases into a single value.

        >>> Left("error").fold(lambda e: f"Error: {e}", lambda v: f"Value: {v}")
        'Error: error'
        """
        return on_left(self._value)

    @override
    def __repr__(self) -> str:
        return f"Left({self._value!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Left):
            return self._value == other._value
        return False


@dataclass(frozen=True, slots=True)
class Right(Either[L, R], Generic[L, R]):
    """Right variant of Either, typically containing a success value.

    >>> right = Right(42)
    >>> right.is_right()
    True
    >>> right.unwrap_right()
    42
    """

    _value: R

    @override
    def is_left(self) -> bool:
        """Check if this is Left variant.

        >>> Right(42).is_left()
        False
        """
        return False

    @override
    def is_right(self) -> bool:
        """Check if this is Right variant.

        >>> Right(42).is_right()
        True
        """
        return True

    @override
    def unwrap_left(self) -> L:
        """Get the Left value, raising an error."""
        raise ValueError("Cannot unwrap_left Right")

    @override
    def unwrap_right(self) -> R:
        """Get the Right value.

        >>> Right(42).unwrap_right()
        42
        """
        return self._value

    @override
    def swap(self) -> Either[R, L]:
        """Swap Left and Right.

        >>> Right(2).swap()
        Left(2)
        """
        return Left(self._value)

    @override
    def map(self, f: Callable[[R], U]) -> Either[L, U]:
        """Apply a function to the Right value.

        >>> Right(5).map(lambda x: x * 2)
        Right(10)
        """
        return Right(f(self._value))

    @override
    def map_left(self, f: Callable[[L], L]) -> Either[L, R]:
        """Apply a function to the Left value (no-op for Right).

        >>> Right(42).map_left(str.upper)
        Right(42)
        """
        return self

    @override
    def flat_map(self, f: Callable[[R], Either[L, U]]) -> Either[L, U]:
        """Chain operations that return Either.

        >>> def divide(x): return Right(10 / x) if x != 0 else Left("Div by zero")
        >>> Right(2).flat_map(divide)
        Right(5.0)
        >>> Right(0).flat_map(divide)
        Left('Div by zero')
        """
        return f(self._value)

    @override
    def ap(self, fn: Either[L, Callable[[R], U]]) -> Either[L, U]:
        """Apply this Either's value to the function contained in fn.

        >>> add = Right(lambda x: x + 1)
        >>> value = Right(5)
        >>> value.ap(add)
        Right(6)
        >>> Left("bad").ap(add)
        Left('bad')
        >>> value.ap(Left("bad"))
        Left('bad')

        Note:
            The receiver (self) contains the value, fn contains the function.
        """
        if fn.is_left():
            return Left(fn.unwrap_left())
        return Right(fn.unwrap_right()(self._value))

    @override
    def fold(self, on_left: Callable[[L], U], on_right: Callable[[R], U]) -> U:
        """Fold both cases into a single value.

        >>> Right(42).fold(lambda e: f"Error: {e}", lambda v: f"Value: {v}")
        'Value: 42'
        """
        return on_right(self._value)

    @override
    def __repr__(self) -> str:
        return f"Right({self._value!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Right):
            return self._value == other._value
        return False


__all__ = ["Either", "Left", "Right"]
