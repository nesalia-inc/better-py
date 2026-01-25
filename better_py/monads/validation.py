"""Validation monad for accumulating errors.

The Validation monad represents either a success value or a collection
of errors, allowing error accumulation during validation.

New API (preferred):
    >>> valid = Valid(42)
    >>> invalid = Invalid(["Error 1", "Error 2"])

Legacy API (still supported):
    >>> valid = Validation.valid(42)
    >>> invalid = Validation.invalid(["Error 1", "Error 2"])
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import Result

E = TypeVar("E")  # Error type
T = TypeVar("T")  # Success type
U = TypeVar("U")


class Validation(Mappable[T], Generic[E, T]):
    """Base class for Validation monad.

    This class provides factory methods for creating Validation values.
    For new code, prefer using Valid() and Invalid() directly.

    Type Parameters:
        E: The error type
        T: The success value type

    Example (new API - preferred):
        >>> valid = Valid(42)
        >>> invalid = Invalid(["error"])

    Example (legacy API - still supported):
        >>> valid = Validation.valid(42)
        >>> invalid = Validation.invalid(["error"])
    """

    @staticmethod
    def valid(value: T) -> Validation[E, T]:
        """Create a Valid Validation containing a success value.

        Args:
            value: The success value

        Returns:
            A Valid variant containing the value

        Example:
            >>> Validation.valid(42)
            Valid(42)
        """
        return Valid(value)

    @staticmethod
    def invalid(errors: list[E] | E) -> Validation[E, T]:
        """Create an Invalid Validation containing errors.

        Args:
            errors: List of errors or single error

        Returns:
            An Invalid variant containing the errors

        Example:
            >>> Validation.invalid(["Error 1", "Error 2"])
            Invalid(['Error 1', 'Error 2'])
        """
        if isinstance(errors, list):
            return Invalid(errors)
        return Invalid([errors])

    # Abstract methods that subclasses must implement
    def is_valid(self) -> bool:
        """Check if this is Valid variant."""
        raise NotImplementedError()

    def is_invalid(self) -> bool:
        """Check if this is Invalid variant."""
        raise NotImplementedError()

    def unwrap(self) -> T:
        """Get the success value, raising an error if Invalid."""
        raise NotImplementedError()

    def unwrap_errors(self) -> list[E]:
        """Get the errors, raising an error if Valid."""
        raise NotImplementedError()

    def map(self, f: Callable[[T], U]) -> Validation[E, U]:
        """Apply a function to the success value."""
        raise NotImplementedError()

    def map_errors(self, f: Callable[[list[E]], list[E]]) -> Validation[E, T]:
        """Apply a function to the errors."""
        raise NotImplementedError()

    def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
        """Apply a Validation containing a function to this Validation."""
        raise NotImplementedError()

    def flat_map(self, f: Callable[[T], Validation[E, U]]) -> Validation[E, U]:
        """Chain operations that return Validation."""
        raise NotImplementedError()

    def fold(self, on_invalid: Callable[[list[E]], U], on_valid: Callable[[T], U]) -> U:
        """Fold both cases into a single value."""
        raise NotImplementedError()

    def to_result(self) -> Result[T, E]:
        """Convert Validation to Result."""
        raise NotImplementedError()


@dataclass(frozen=True, slots=True)
class Valid(Validation[E, T], Generic[E, T]):
    """Valid variant of Validation, containing a success value.

    Type Parameters:
        E: The error type (for type compatibility)
        T: The success value type

    Example:
        >>> valid = Valid(42)
        >>> valid.is_valid()  # True
        >>> valid.unwrap()  # 42
    """

    _value: T

    @override
    def is_valid(self) -> bool:
        """Check if this is Valid variant.

        Returns:
            True - this is Valid

        Example:
            >>> Valid(42).is_valid()  # True
        """
        return True

    @override
    def is_invalid(self) -> bool:
        """Check if this is Invalid variant.

        Returns:
            False - this is Valid

        Example:
            >>> Valid(42).is_invalid()  # False
        """
        return False

    @override
    def unwrap(self) -> T:
        """Get the success value.

        Returns:
            The success value

        Example:
            >>> Valid(42).unwrap()  # 42
        """
        return self._value

    @override
    def unwrap_errors(self) -> list[E]:
        """Get the errors, raising an error.

        Raises:
            ValueError: Always, since Valid has no errors

        Example:
            >>> Valid(42).unwrap_errors()  # Raises ValueError
        """
        raise ValueError("Cannot unwrap_errors Valid")

    @override
    def map(self, f: Callable[[T], U]) -> Validation[E, U]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Valid(f(value))

        Example:
            >>> Valid(5).map(lambda x: x * 2)  # Valid(10)
        """
        return Valid(f(self._value))

    @override
    def map_errors(self, f: Callable[[list[E]], list[E]]) -> Validation[E, T]:
        """Apply a function to the errors (no-op for Valid).

        Args:
            f: Function to apply (ignored for Valid)

        Returns:
            This Valid

        Example:
            >>> Valid(42).map_errors(lambda errs: [f"! {e}" for e in errs])
            Valid(42)
        """
        return self

    @override
    def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
        """Apply a Validation containing a function to this Validation.

        Args:
            other: Validation containing a function

        Returns:
            Valid(f(value)) if other is Valid, otherwise Invalid

        Example:
            >>> add = Valid(lambda x: x + 1)
            >>> val = Valid(5)
            >>> add.ap(val)  # Valid(6)
        """
        if other.is_invalid():
            return Invalid(other.unwrap_errors())
        return Valid(other.unwrap()(self._value))

    @override
    def flat_map(self, f: Callable[[T], Validation[E, U]]) -> Validation[E, U]:
        """Chain operations that return Validation.

        Args:
            f: Function that takes a value and returns a Validation

        Returns:
            The result of applying f

        Example:
            >>> def validate_positive(x): return Valid(x) if x > 0 else Invalid(["Not positive"])
            >>> Valid(5).flat_map(validate_positive)  # Valid(5)
            >>> Valid(-1).flat_map(validate_positive)  # Invalid(['Not positive'])
        """
        return f(self._value)

    @override
    def fold(self, on_invalid: Callable[[list[E]], U], on_valid: Callable[[T], U]) -> U:
        """Fold both cases into a single value.

        Args:
            on_invalid: Function to apply if Invalid (ignored)
            on_valid: Function to apply if Valid

        Returns:
            Result of applying on_valid

        Example:
            >>> result = Valid(42).fold(
            ...     on_invalid=lambda errs: f"Errors: {errs}",
            ...     on_valid=lambda v: f"Value: {v}"
            ... )
            >>> "Value: 42"
        """
        return on_valid(self._value)

    @override
    def to_result(self) -> Result[T, E]:
        """Convert Validation to Result.

        Returns:
            Ok(value)

        Example:
            >>> Valid(42).to_result()  # Ok(42)
        """
        from better_py.monads import Result

        return Result.ok(self._value)

    @override
    def __repr__(self) -> str:
        return f"Valid({self._value!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Valid):
            return self._value == other._value
        return False


@dataclass(frozen=True, slots=True)
class Invalid(Validation[E, T], Generic[E, T]):
    """Invalid variant of Validation, containing a list of errors.

    Type Parameters:
        E: The error type
        T: The success value type (for type compatibility)

    Example:
        >>> invalid = Invalid(["Error 1", "Error 2"])
        >>> invalid.is_invalid()  # True
        >>> invalid.unwrap_errors()  # ["Error 1", "Error 2"]
    """

    _errors: list[E]

    @override
    def is_valid(self) -> bool:
        """Check if this is Valid variant.

        Returns:
            False - this is Invalid

        Example:
            >>> Invalid(["error"]).is_valid()  # False
        """
        return False

    @override
    def is_invalid(self) -> bool:
        """Check if this is Invalid variant.

        Returns:
            True - this is Invalid

        Example:
            >>> Invalid(["error"]).is_invalid()  # True
        """
        return True

    @override
    def unwrap(self) -> T:
        """Get the success value, raising an error.

        Raises:
            ValueError: Always, since Invalid has no success value

        Example:
            >>> Invalid(["error"]).unwrap()  # Raises ValueError
        """
        raise ValueError(f"Cannot unwrap Invalid: {self._errors}")

    @override
    def unwrap_errors(self) -> list[E]:
        """Get the errors.

        Returns:
            The list of errors

        Example:
            >>> Invalid(["error"]).unwrap_errors()  # ["error"]
        """
        return self._errors

    @override
    def map(self, f: Callable[[T], U]) -> Validation[E, U]:
        """Apply a function to the success value (no-op for Invalid).

        Args:
            f: Function to apply (ignored for Invalid)

        Returns:
            This Invalid

        Example:
            >>> Invalid(["error"]).map(lambda x: x * 2)  # Invalid(['error'])
        """
        return self

    @override
    def map_errors(self, f: Callable[[list[E]], list[E]]) -> Validation[E, T]:
        """Apply a function to the errors.

        Args:
            f: Function to apply

        Returns:
            Invalid(f(errors))

        Example:
            >>> Invalid(["error"]).map_errors(lambda errs: [f"! {e}" for e in errs])
            Invalid(['! error'])
        """
        return Invalid(f(self._errors))

    @override
    def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
        """Apply a Validation containing a function to this Validation.

        Args:
            other: Validation containing a function

        Returns:
            Invalid with accumulated errors

        Example:
            >>> add = Valid(lambda x: x + 1)
            >>> val = Invalid(["bad"])
            >>> add.ap(val)  # Invalid(['bad'])
        """
        if other.is_invalid():
            # Accumulate errors from both sides
            return Invalid(self._errors + other.unwrap_errors())
        return self

    @override
    def flat_map(self, f: Callable[[T], Validation[E, U]]) -> Validation[E, U]:
        """Chain operations that return Validation (short-circuits for Invalid).

        Args:
            f: Function (ignored for Invalid)

        Returns:
            This Invalid

        Example:
            >>> def validate_positive(x): return Valid(x) if x > 0 else Invalid(["Not positive"])
            >>> Invalid(["bad"]).flat_map(validate_positive)  # Invalid(['bad'])
        """
        return self

    @override
    def fold(self, on_invalid: Callable[[list[E]], U], on_valid: Callable[[T], U]) -> U:
        """Fold both cases into a single value.

        Args:
            on_invalid: Function to apply if Invalid
            on_valid: Function to apply if Valid (ignored)

        Returns:
            Result of applying on_invalid

        Example:
            >>> result = Invalid(["error"]).fold(
            ...     on_invalid=lambda errs: f"Errors: {errs}",
            ...     on_valid=lambda v: f"Value: {v}"
            ... )
            >>> "Errors: ['error']"
        """
        return on_invalid(self._errors)

    @override
    def to_result(self) -> Result[T, E]:
        """Convert Validation to Result.

        Returns:
            Error(errors[0])

        Example:
            >>> Invalid(["error"]).to_result()  # Error('error')
        """
        from better_py.monads import Result

        return Result.error(self._errors[0])

    @override
    def __repr__(self) -> str:
        return f"Invalid({self._errors!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Invalid):
            return self._errors == other._errors
        return False


__all__ = ["Validation", "Valid", "Invalid"]
