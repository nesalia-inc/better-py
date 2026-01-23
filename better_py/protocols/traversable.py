"""Traversable protocol for data structures that can be traversed.

The Traversable protocol defines the ability to transform a data structure
with effects, combining Functor and Foldable operations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

from better_py.protocols.types import T

Applicative = TypeVar("Applicative")


@runtime_checkable
class Traversable(Protocol[T]):
    """Protocol for traversable data structures.

    A Traversable type can be traversed with an effectful function,
    transforming its contents while preserving structure.

    Type Parameters:
        T: The element type

    Example:
        >>> from better_py.monads import Maybe
        >>> traverse(lambda x: Maybe.some(x * 2), [1, 2, 3])  # Maybe.some([2, 4, 6])
    """

    def traverse(self, f: Callable[[T], Applicative]) -> Applicative:
        """Transform contents with an effectful function.

        Args:
            f: A function that returns an applicative effect

        Returns:
            An applicative containing the transformed structure

        Example:
            >>> result.traverse(lambda x: Maybe.some(x * 2))
        """
        ...

    def sequence(self) -> Applicative:
        """Extract effects from a traversable of applicatives.

        Returns:
            An applicative containing the traversable structure

        Example:
            >>> result.sequence()  # Maybe.some([1, 2, 3])
        """
        ...


__all__ = ["Traversable"]
