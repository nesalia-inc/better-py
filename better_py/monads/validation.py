"""Validation monad for accumulating errors.

The Validation monad represents either a success value or a collection
of errors, allowing error accumulation during validation.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import Result

E = TypeVar("E")  # Error type
T = TypeVar("T")  # Success type
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Validation(Mappable[T], Generic[E, T]):
    """Validation monad for accumulating errors.

    A Validation is either Valid(value) or Invalid([errors]), representing
    the success or failure of validation operations with error accumulation.

    Type Parameters:
        E: The error type
        T: The success value type

    Example:
        >>> valid = Validation.valid(42)
        >>> invalid = Validation.invalid(["Error 1", "Error 2"])
        >>> valid.is_valid()  # True
        >>> invalid.is_invalid()  # True
    """

    _value: T | None
    _errors: list[E] = field(default_factory=list)

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
        return Validation(value, [])

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
            return Validation(None, errors)
        return Validation(None, [errors])

    def is_valid(self) -> bool:
        """Check if this is Valid.

        Returns:
            True if Valid, False otherwise

        Example:
            >>> Validation.valid(42).is_valid()  # True
            >>> Validation.invalid(["error"]).is_valid()  # False
        """
        return len(self._errors) == 0

    def is_invalid(self) -> bool:
        """Check if this is Invalid.

        Returns:
            True if Invalid, False otherwise

        Example:
            >>> Validation.invalid(["error"]).is_invalid()  # True
            >>> Validation.valid(42).is_invalid()  # False
        """
        return len(self._errors) > 0

    def unwrap(self) -> T:
        """Get the success value, raising an error if Invalid.

        Returns:
            The success value

        Raises:
            ValueError: If this is Invalid

        Example:
            >>> Validation.valid(42).unwrap()  # 42
            >>> Validation.invalid(["error"]).unwrap()  # Raises ValueError
        """
        if self._errors:
            raise ValueError(f"Cannot unwrap Invalid: {self._errors}")
        # _value is not None when _errors is empty
        assert self._value is not None
        return self._value

    def unwrap_errors(self) -> list[E]:
        """Get the errors, raising an error if Valid.

        Returns:
            The list of errors

        Raises:
            ValueError: If this is Valid

        Example:
            >>> Validation.invalid(["error"]).unwrap_errors()  # ["error"]
            >>> Validation.valid(42).unwrap_errors()  # Raises ValueError
        """
        if not self._errors:
            raise ValueError("Cannot unwrap_errors Valid")
        return self._errors

    def map(self, f: Callable[[T], U]) -> Validation[E, U]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Valid(f(value)) if Valid, otherwise Invalid

        Example:
            >>> Validation.valid(5).map(lambda x: x * 2)  # Valid(10)
            >>> Validation.invalid(["error"]).map(lambda x: x * 2)  # Invalid(['error'])
        """
        if self._errors:
            return Validation(None, self._errors)
        # _value is not None when _errors is empty
        assert self._value is not None
        return Validation(f(self._value), [])

    def map_errors(self, f: Callable[[list[E]], list[E]]) -> Validation[E, T]:
        """Apply a function to the errors.

        Args:
            f: Function to apply to errors

        Returns:
            Valid(value) if Valid, otherwise Invalid(f(errors))

        Example:
            >>> Validation.invalid(["error"]).map_errors(lambda errs: [f"! {e}" for e in errs])
            Invalid(['! error'])
        """
        if not self._errors:
            # _value is not None when _errors is empty
            assert self._value is not None
            return Validation(self._value, [])
        return Validation(None, f(self._errors))

    def ap(self, other: Validation[E, Callable[[T], U]]) -> Validation[E, U]:
        """Apply a Validation containing a function to this Validation.

        Args:
            other: Validation containing a function

        Returns:
            Valid(f(value)) if both are Valid, otherwise Invalid with accumulated errors

        Example:
            >>> add = Validation.valid(lambda x: x + 1)
            >>> val = Validation.valid(5)
            >>> add.ap(val)  # Valid(6)
        """
        if self._errors and other._errors:
            # Accumulate errors from both sides
            return Validation(None, self._errors + other._errors)
        if self._errors:
            return Validation(None, self._errors)
        if other._errors:
            return Validation(None, other._errors)
        # Both _value fields are not None when _errors is empty
        assert self._value is not None
        assert other._value is not None
        return Validation(self._value(other._value), [])

    def flat_map(self, f: Callable[[T], Validation[E, U]]) -> Validation[E, U]:
        """Chain operations that return Validation.

        Args:
            f: Function that takes a value and returns a Validation

        Returns:
            The result of applying f if Valid, otherwise Invalid

        Example:
            >>> def validate_positive(x): return Validation.valid(x) if x > 0 else Validation.invalid(["Not positive"])
            >>> Validation.valid(5).flat_map(validate_positive)  # Valid(5)
            >>> Validation.valid(-1).flat_map(validate_positive)  # Invalid(['Not positive'])
        """
        if self._errors:
            return Validation(None, self._errors)
        # _value is not None when _errors is empty
        assert self._value is not None
        result = f(self._value)
        if result._errors:
            return Validation(None, result._errors)
        # result._value is not None when result._errors is empty
        assert result._value is not None
        return Validation(result._value, [])

    def fold(self, on_invalid: Callable[[list[E]], U], on_valid: Callable[[T], U]) -> U:
        """Fold both cases into a single value.

        Args:
            on_invalid: Function to apply if Invalid
            on_valid: Function to apply if Valid

        Returns:
            Result of applying the appropriate function

        Example:
            >>> result = Validation.valid(42).fold(
            ...     on_invalid=lambda errs: f"Errors: {errs}",
            ...     on_valid=lambda v: f"Value: {v}"
            ... )
            >>> "Value: 42"
        """
        if self._errors:
            return on_invalid(self._errors)
        # _value is not None when _errors is empty
        assert self._value is not None
        return on_valid(self._value)

    def to_result(self) -> Result[T, E]:
        """Convert Validation to Result.

        Returns:
            Ok(value) if Valid, Error(errors[0]) if Invalid

        Example:
            >>> Validation.valid(42).to_result()  # Ok(42)
            >>> Validation.invalid(["error"]).to_result()  # Error('error')
        """
        from better_py.monads import Result

        if self._errors:
            return Result.error(self._errors[0])
        # _value is not None when _errors is empty
        assert self._value is not None
        return Result.ok(self._value)

    @override
    def __repr__(self) -> str:
        if self._errors:
            return f"Invalid({self._errors!r})"
        return f"Valid({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Validation):
            return False
        return self._value == other._value and self._errors == other._errors


__all__ = ["Validation"]
