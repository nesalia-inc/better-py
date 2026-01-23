"""Combinable protocol for semigroup/monoid-like operations.

The Combinable protocol defines the ability to combine two values of the
same type, similar to semigroups (combine) and monads (combine with identity).
"""

from typing import Protocol, runtime_checkable

from better_py.protocols.types import T


@runtime_checkable
class Combinable(Protocol[T]):
    """Protocol for types that can be combined.

    A Combinable type supports a binary combine operation that merges
    two values into a new value of the same type (Semigroup).

    Type Parameters:
        T: The type being combined

    Example:
        >>> class Money(Combinable):
        ...     def combine(self, other):
        ...         return Money(self.amount + other.amount)
    """

    def combine(self, other: T) -> T:
        """Combine this value with another of the same type.

        Args:
            other: Another value of the same type to combine with

        Returns:
            A new value representing the combination

        Example:
            >>> money1 = Money(100)
            >>> money2 = Money(50)
            >>> combined = money1.combine(money2)  # Money(150)
        """
        ...


@runtime_checkable
class Monoid(Protocol[T]):
    """Protocol for types with combine operation and identity element.

    A Monoid is a Combinable type that also has an identity element
    (empty/zero value) that can be combined without changing a value.

    Type Parameters:
        T: The type being combined

    Example:
        >>> class Sum(Monoid):
        ...     @staticmethod
        ...     def identity():
        ...         return Sum(0)
        ...
        ...     def combine(self, other):
        ...         return Sum(self.value + other.value)
    """

    def combine(self, other: T) -> T:
        """Combine this value with another.

        Args:
            other: Another value to combine with

        Returns:
            A new combined value
        """
        ...

    @staticmethod
    def identity() -> T:  # type: ignore[empty-body]
        """Return the identity element for this type.

        The identity element satisfies:
        identity().combine(x) == x
        x.combine(identity()) == x

        Returns:
            The identity value for this type

        Example:
            >>> Sum(5).combine(Sum.identity())  # Sum(5)
            >>> Sum.identity().combine(Sum(5))  # Sum(5)
        """
        ...


__all__ = ["Combinable", "Monoid"]
