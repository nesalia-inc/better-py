"""Validable protocol for validation operations.

The Validable protocol defines the ability to validate values and collect
errors, supporting both successful validation and error accumulation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable

from better_py.protocols.types import E, T


@runtime_checkable
class Validable(Protocol[T, E]):
    """Protocol for validation operations.

    A Validable type can validate values and collect errors, supporting
    both successful validation and error accumulation.

    Type Parameters:
        T: The value type
        E: The error type

    Example:
        >>> result = validate_email("user@example.com")  # Valid("user@example.com")
        >>> result = validate_email("invalid")  # Invalid(["Invalid email"])
    """

    def is_valid(self) -> bool:
        """Check if this is a valid value.

        Returns:
            True if valid, False otherwise

        Example:
            >>> result.is_valid()
        """
        ...

    def is_invalid(self) -> bool:
        """Check if this is invalid.

        Returns:
            True if invalid, False otherwise

        Example:
            >>> result.is_invalid()
        """
        ...

    def validate(self, *validators: Callable[[T], bool]) -> Validable[T, E]:
        """Apply validators to the value.

        Args:
            *validators: Functions that validate the value

        Returns:
            A Validable with validation results

        Example:
            >>> result.validate(is_positive, is_even)
        """
        ...

    def map(self, f: Callable[[T], T]) -> Validable[T, E]:
        """Apply a function to the valid value.

        Args:
            f: Function to apply

        Returns:
            A new Validable with the function applied

        Example:
            >>> result.map(lambda x: x * 2)
        """
        ...

    def map_errors(self, f: Callable[[list[E]], list[E]]) -> Validable[T, E]:
        """Apply a function to the errors.

        Args:
            f: Function to apply to errors

        Returns:
            A new Validable with transformed errors

        Example:
            >>> result.map_errors(lambda errs: [f"Error: {e}" for e in errs])
        """
        ...

    def get_errors(self) -> list[E]:
        """Get the list of errors.

        Returns:
            List of errors, empty if valid

        Example:
            >>> result.get_errors()
        """
        ...


__all__ = ["Validable"]
