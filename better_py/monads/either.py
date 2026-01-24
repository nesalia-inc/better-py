"""Either monad for error handling with two variants.

The Either monad represents either a Left value (typically an error) or
a Right value (typically a success), providing a type-safe alternative
to exceptions for error handling.
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


@dataclass(frozen=True, slots=True)
class Either(Mappable[R], Generic[L, R]):
    """Either monad for error handling with two variants.

    An Either is either Left(value) or Right(value), representing the
    failure or success of an operation in a type-safe way.

    Type Parameters:
        L: The Left type (typically error)
        R: The Right type (typically success)

    Example:
        >>> right = Either.right(42)
        >>> left = Either.left("Error occurred")
        >>> right.is_right()  # True
        >>> left.is_left()  # True
    """

    _left: L | None
    _right: R | None

    @staticmethod
    def left(value: L) -> Either[L, R]:
        """Create a Left Either containing an error/value.

        Args:
            value: The Left value

        Returns:
            A Left variant containing the value

        Example:
            >>> Either.left("Error occurred")
            Left('Error occurred')
        """
        return Either(value, None)

    @staticmethod
    def right(value: R) -> Either[L, R]:
        """Create a Right Either containing a success value.

        Args:
            value: The success value

        Returns:
            A Right variant containing the value

        Example:
            >>> Either.right(42)
            Right(42)
        """
        return Either(None, value)

    def is_left(self) -> bool:
        """Check if this is Left variant.

        Returns:
            True if Left, False otherwise

        Example:
            >>> Either.left("error").is_left()  # True
            >>> Either.right(42).is_left()  # False
        """
        return self._left is not None

    def is_right(self) -> bool:
        """Check if this is Right variant.

        Returns:
            True if Right, False otherwise

        Example:
            >>> Either.right(42).is_right()  # True
            >>> Either.left("error").is_right()  # False
        """
        return self._right is not None

    def unwrap_left(self) -> L:
        """Get the Left value, raising an error if Right.

        Returns:
            The Left value

        Raises:
            ValueError: If this is Right

        Example:
            >>> Either.left("error").unwrap_left()  # "error"
            >>> Either.right(42).unwrap_left()  # Raises ValueError
        """
        if self._left is None:
            raise ValueError("Cannot unwrap_left Right")
        return self._left

    def unwrap_right(self) -> R:
        """Get the Right value, raising an error if Left.

        Returns:
            The Right value

        Raises:
            ValueError: If this is Left

        Example:
            >>> Either.right(42).unwrap_right()  # 42
            >>> Either.left("error").unwrap_right()  # Raises ValueError
        """
        if self._right is None:
            raise ValueError(f"Cannot unwrap_right Left: {self._left}")
        return self._right

    def swap(self) -> Either[R, L]:
        """Swap Left and Right.

        Returns:
            Left becomes Right, Right becomes Left

        Example:
            >>> Either.left(1).swap()  # Right(1)
            >>> Either.right(2).swap()  # Left(2)
        """
        if self._left is not None:
            return Either.right(self._left)
        # _right is not None when _left is None
        assert self._right is not None
        return Either.left(self._right)

    def map(self, f: Callable[[R], U]) -> Either[L, U]:
        """Apply a function to the Right value.

        Args:
            f: Function to apply

        Returns:
            Right(f(value)) if Right, otherwise Left

        Example:
            >>> Either.right(5).map(lambda x: x * 2)  # Right(10)
            >>> Either.left("error").map(lambda x: x * 2)  # Left('error')
        """
        if self._right is None:
            return Either(self._left, None)
        # _right is not None here
        assert self._right is not None
        return Either(None, f(self._right))

    def map_left(self, f: Callable[[L], L]) -> Either[L, R]:
        """Apply a function to the Left value.

        Args:
            f: Function to apply to Left

        Returns:
            Left(f(value)) if Left, otherwise Right

        Example:
            >>> Either.left("error").map_left(str.upper)  # Left('ERROR')
            >>> Either.right(42).map_left(str.upper)  # Right(42)
        """
        if self._left is None:
            return Either(None, self._right)
        # _left is not None here
        assert self._left is not None
        return Either(f(self._left), None)

    def flat_map(self, f: Callable[[R], Either[L, U]]) -> Either[L, U]:
        """Chain operations that return Either.

        Args:
            f: Function that takes a value and returns an Either

        Returns:
            The result of applying f if Right, otherwise Left

        Example:
            >>> def divide(x): return Either.right(10 / x) if x != 0 else Either.left("Div by zero")
            >>> Either.right(2).flat_map(divide)  # Right(5.0)
            >>> Either.right(0).flat_map(divide)  # Left('Div by zero')
        """
        if self._right is None:
            return Either(self._left, None)
        # _right is not None here
        assert self._right is not None
        return f(self._right)

    def ap(self, fn: Either[L, Callable[[R], U]]) -> Either[L, U]:
        """Apply an Either containing a function to this Either.

        Args:
            fn: An Either containing a function

        Returns:
            Right(f(value)) if both are Right, otherwise Left

        Example:
            >>> add = Either.right(lambda x: x + 1)
            >>> value = Either.right(5)
            >>> add.ap(value)  # Right(6)
            >>> Either.left("bad").ap(value)  # Left('bad')
            >>> add.ap(Either.left("bad"))  # Left('bad')
        """
        if self._left is not None or fn._left is not None:
            if self._left is not None:
                return Either(self._left, None)
            return Either(fn._left, None)
        assert self._right is not None
        assert fn._right is not None
        return Either(None, fn._right(self._right))

    @staticmethod
    def lift2(f: Callable[[R, U], object], ma: Either[L, R], mb: Either[L, U]) -> Either[L, object]:
        """Lift a binary function to operate on Either values.

        Args:
            f: A binary function
            ma: First Either value
            mb: Second Either value

        Returns:
            Right(f(a, b)) if both are Right, otherwise Left

        Example:
            >>> Either.lift2(lambda x, y: x + y, Either.right(1), Either.right(2))  # Right(3)
            >>> Either.lift2(lambda x, y: x + y, Either.right(1), Either.left("bad"))  # Left('bad')
        """
        curried = ma.map(lambda x: lambda y: f(x, y))
        return mb.ap(curried)

    @staticmethod
    def lift3(f: Callable[[R, U, object], object], ma: Either[L, R], mb: Either[L, U], mc: Either[L, object]) -> Either[L, object]:
        """Lift a ternary function to operate on Either values.

        Args:
            f: A ternary function
            ma: First Either value
            mb: Second Either value
            mc: Third Either value

        Returns:
            Right(f(a, b, c)) if all are Right, otherwise Left

        Example:
            >>> Either.lift3(lambda x, y, z: x + y + z, Either.right(1), Either.right(2), Either.right(3))  # Right(6)
        """
        curried = ma.map(lambda x: lambda y: lambda z: f(x, y, z))
        return mc.ap(mb.ap(curried))

    @staticmethod
    def zip(*eithers: Either[L, R]) -> Either[L, tuple[R, ...]]:
        """Combine multiple Either values into a tuple.

        Args:
            *eithers: Either values to combine

        Returns:
            Right(tuple of values) if all are Right, otherwise Left

        Example:
            >>> Either.zip(Either.right(1), Either.right(2), Either.right(3))  # Right((1, 2, 3))
            >>> Either.zip(Either.right(1), Either.left("bad"), Either.right(3))  # Left('bad')
        """
        vals: list[R] = []
        for e in eithers:
            if e._left is not None:
                return Either(e._left, None)
            assert e._right is not None
            vals.append(e._right)
        return Either(None, tuple(vals))

    def fold(self, on_left: Callable[[L], U], on_right: Callable[[R], U]) -> U:
        """Fold both cases into a single value.

        Args:
            on_left: Function to apply if Left
            on_right: Function to apply if Right

        Returns:
            Result of applying the appropriate function

        Example:
            >>> result = Either.right(42).fold(lambda e: f"Error: {e}", lambda v: f"Value: {v}")
            >>> "Value: 42"
        """
        if self._left is not None:
            return on_left(self._left)
        # _right is not None when _left is None
        assert self._right is not None
        return on_right(self._right)

    @override
    def __repr__(self) -> str:
        if self._left is not None:
            return f"Left({self._left!r})"
        return f"Right({self._right!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Either):
            return False
        return self._left == other._left and self._right == other._right


__all__ = ["Either"]
