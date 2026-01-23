"""Mappable protocol for functor-like operations.

The Mappable protocol defines the ability to apply a function to values
in a context, similar to fmap in Haskell or map in other functional
languages.
"""

from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

from better_py.protocols.types import T, U

T_contra = TypeVar("T_contra", contravariant=True)


@runtime_checkable
class Mappable(Protocol[T]):
    """Protocol for types that support mapping operations.

    A Mappable is a container or context that can have a function applied
    to its contents, producing a new Mappable with the result.

    Type Parameters:
        T: The type of values in the Mappable

    Example:
        >>> class Box(Mappable):
        ...     def map(self, f):
        ...         return Box(f(self.value))
    """

    def map(self, f: "Callable[[T], U]") -> "Mappable[U]":
        """Apply a function to the contained value.

        Args:
            f: A function from T to U

        Returns:
            A new Mappable containing the result of applying f

        Example:
            >>> maybe_some = Maybe.some(5)
            >>> maybe_some.map(lambda x: x * 2)  # Maybe.some(10)
        """
        ...


@runtime_checkable
class Mappable1(Protocol[T]):
    """Alternative Mappable protocol with method-only definition.

    This is a simpler version that only requires the map method without
    enforcing return type constraints as strictly.
    """

    def map(self, f):  # type: ignore[no-untyped-def]
        """Apply a function to the contained value."""
        ...


__all__ = ["Mappable", "Mappable1"]
