"""Reducible protocol for fold/reduce operations.

The Reducible protocol defines the ability to reduce a structure to a
single value by combining its elements, similar to fold in Haskell or
reduce in Python.
"""

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from better_py.protocols.types import T, U


@runtime_checkable
class Reducible(Protocol[T]):
    """Protocol for types that support reduction operations.

    A Reducible is a container that can be collapsed to a single value
    by combining its elements with a binary function.

    Type Parameters:
        T: The type of elements in the Reducible

    Example:
        >>> numbers = [1, 2, 3, 4, 5]
        >>> numbers.reduce(lambda acc, x: acc + x, 0)  # 15
    """

    def reduce(self, f: "Callable[[U, T], U]", initial: U) -> U:
        """Reduce the structure to a single value.

        Args:
            f: A binary function that combines an accumulator (U)
               with an element (T) to produce a new accumulator (U)
            initial: The initial accumulator value

        Returns:
            The final accumulator value after combining all elements

        Example:
            >>> [1, 2, 3].reduce(lambda acc, x: acc + x, 0)  # 6
            >>> ['a', 'b', 'c'].reduce(lambda acc, x: acc + x, '')  # 'abc'
        """
        ...

    def fold_left(self, f: "Callable[[U, T], U]", initial: U) -> U:
        """Left-associative fold (alias for reduce).

        Args:
            f: A binary function
            initial: The initial value

        Returns:
            The folded value

        Example:
            >>> [1, 2, 3].fold_left(lambda acc, x: acc - x, 0)  # -6
            # Equivalent to: ((0 - 1) - 2) - 3 = -6
        """
        ...


@runtime_checkable
class Reducible1(Protocol[T]):
    """Simplified Reducible protocol with basic reduce only."""

    def reduce(self, f, initial):  # type: ignore[no-untyped-def]
        """Reduce to a single value."""
        ...


__all__ = ["Reducible", "Reducible1"]
