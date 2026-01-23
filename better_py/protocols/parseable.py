"""Parseable protocol for parsing operations.

The Parseable protocol defines the ability to parse strings into values,
supporting both successful parsing and error handling.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar, runtime_checkable

from better_py.protocols.types import T

E = TypeVar("E")


@runtime_checkable
class Parseable(Protocol[T, E]):
    """Protocol for parsing operations.

    A Parseable type can parse strings into values, with error handling
    for invalid inputs.

    Type Parameters:
        T: The parsed value type
        E: The error type

    Example:
        >>> result = parseInt.parse("42")  # Some(42)
        >>> result = parseInt.parse("abc")  # Nothing
    """

    def parse(self, s: str) -> T | E:
        """Parse a string into a value or error.

        Args:
            s: The string to parse

        Returns:
            The parsed value, or an error if parsing fails

        Example:
            >>> result.parse("123")
        """
        ...

    @staticmethod
    def from_value(value: T) -> T:
        """Create a parsed value directly.

        Args:
            value: The value to wrap

        Returns:
            The value as-is

        Example:
            >>> Parseable.from_value(42)
        """
        ...

    def is_valid(self) -> bool:
        """Check if this is a valid parsed value.

        Returns:
            True if valid, False otherwise

        Example:
            >>> result.is_valid()
        """
        ...

    def map(self, f: Callable[[T], T]) -> Parseable[T, E]:
        """Apply a function to the parsed value.

        Args:
            f: Function to apply

        Returns:
            A new Parseable with the function applied

        Example:
            >>> result.map(lambda x: x * 2)
        """
        ...


__all__ = ["Parseable"]
