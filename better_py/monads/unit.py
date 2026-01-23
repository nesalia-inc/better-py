"""Unit monad for the unit type.

The Unit monad represents the unit type (void/void), representing
computations with no meaningful return value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, override

from better_py.protocols import Mappable

A = TypeVar("A")


@dataclass(frozen=True, slots=True)
class Unit(Mappable[A], Generic[A]):
    """Unit monad for the unit type.

    A Unit represents a computation that produces a value but can
    also be used as the unit type () equivalent.

    Type Parameters:
        A: The value type

    Example:
        >>> unit = Unit()
        >>> result = Unit.of(42)
    """

    value: A | None = None

    def map(self, f):
        """Apply a function to the value.

        Args:
            f: Function to apply

        Returns:
            A Unit with the function applied

        Example:
            >>> Unit.of(5).map(lambda x: x * 2)
        """
        if self.value is None:
            return Unit(None)
        return Unit(f(self.value))

    @staticmethod
    def of(value: A) -> Unit[A]:
        """Create a Unit from a value.

        Args:
            value: The value

        Returns:
            A Unit containing the value

        Example:
            >>> Unit.of(42)
        """
        return Unit(value)

    @staticmethod
    def unit() -> Unit[None]:
        """Create an empty Unit.

        Returns:
            An empty Unit

        Example:
            >>> Unit.unit()
        """
        return Unit(None)

    @override
    def __repr__(self) -> str:
        if self.value is None:
            return "Unit()"
        return f"Unit({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return False
        return self.value == other.value


__all__ = ["Unit"]
