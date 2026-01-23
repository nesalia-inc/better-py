"""Result monad for error handling.

The Result monad represents either a successful value (Ok) or an error (Error).
This is a type-safe alternative to exceptions for error handling.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Result(Mappable[T], Generic[T, E]):
    """Result monad for error handling.

    A Result is either Ok(value) or Error(error), representing the success
    or failure of an operation in a type-safe way.

    Type Parameters:
        T: The success value type
        E: The error type

    Example:
        >>> ok = Result.ok(42)
        >>> error = Result.error("Something went wrong")
        >>> ok.is_ok()  # True
        >>> error.is_error()  # True
    """

    _value: T | None
    _error: E | None

    @staticmethod
    def ok(value: T) -> Result[T, E]:
        """Create a successful Result containing a value.

        Args:
            value: The success value

        Returns:
            An Ok variant containing the value

        Example:
            >>> Result.ok(42)
            Ok(42)
        """
        return Result(value, None)

    @staticmethod
    def error(error: E) -> Result[T, E]:
        """Create a failed Result containing an error.

        Args:
            error: The error value

        Returns:
            An Error variant containing the error

        Example:
            >>> Result.error("Division by zero")
            Error('Division by zero')
        """
        return Result(None, error)

    @staticmethod
    def from_value(value: T, error_value: E | None = None) -> Result[T, E]:
        """Create a Result from a value and optional error.

        Args:
            value: The value
            error_value: Optional error value

        Returns:
            Ok(value) if error_value is None, otherwise Error(error_value)

        Example:
            >>> Result.from_value(42)
            Ok(42)
            >>> Result.from_value(42, "Error")
            Error('Error')
        """
        if error_value is not None:
            return Result(None, error_value)
        return Result(value, None)

    def is_ok(self) -> bool:
        """Check if this is Ok variant.

        Returns:
            True if successful, False otherwise

        Example:
            >>> Result.ok(42).is_ok()  # True
            >>> Result.error("failed").is_ok()  # False
        """
        return self._error is None

    def is_error(self) -> bool:
        """Check if this is Error variant.

        Returns:
            True if failed, False otherwise

        Example:
            >>> Result.ok(42).is_error()  # False
            >>> Result.error("failed").is_error()  # True
        """
        return self._error is not None

    def unwrap(self) -> T:
        """Get the success value, raising an error if Error.

        Returns:
            The success value

        Raises:
            ValueError: If this is Error

        Example:
            >>> Result.ok(42).unwrap()  # 42
            >>> Result.error("failed").unwrap()  # Raises ValueError
        """
        if self._error is not None:
            raise ValueError(f"Cannot unwrap Error: {self._error}")
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default.

        Args:
            default: The default value to return if Error

        Returns:
            The success value, or default if Error

        Example:
            >>> Result.ok(42).unwrap_or(0)  # 42
            >>> Result.error("failed").unwrap_or(0)  # 0
        """
        return self._value if self._error is None else default

    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the success value or compute a default.

        Args:
            supplier: A function that produces the default value

        Returns:
            The success value, or supplier() if Error

        Example:
            >>> Result.ok(42).unwrap_or_else(lambda: 0)  # 42
            >>> Result.error("failed").unwrap_or_else(lambda: 0)  # 0
        """
        return self._value if self._error is None else supplier()

    def unwrap_error(self) -> E:
        """Get the error value, raising an error if Ok.

        Returns:
            The error value

        Raises:
            ValueError: If this is Ok

        Example:
            >>> Result.error("failed").unwrap_error()  # "failed"
            >>> Result.ok(42).unwrap_error()  # Raises ValueError
        """
        if self._error is None:
            raise ValueError("Cannot unwrap_error Ok")
        return self._error

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Ok(f(value)) if Ok, otherwise Error

        Example:
            >>> Result.ok(5).map(lambda x: x * 2)  # Ok(10)
            >>> Result.error("failed").map(lambda x: x * 2)  # Error('failed')
        """
        if self._error is not None:
            return Result(None, self._error)
        return Result(f(self._value), None)

    def bind(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations that return Result (monadic bind).

        Also known as flatMap or andThen.

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f if Ok, otherwise Error

        Example:
            >>> def divide(x): return Result.ok(10 / x) if x != 0 else Result.error("Div by zero")
            >>> Result.ok(2).bind(divide)  # Ok(5.0)
            >>> Result.ok(0).bind(divide)  # Error('Div by zero')
            >>> Result.error("failed").bind(divide)  # Error('failed')
        """
        if self._error is not None:
            return Result(None, self._error)
        return f(self._value)

    def flat_map(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind.

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f if Ok, otherwise Error

        Example:
            >>> Result.ok(5).flat_map(lambda x: Result.ok(x * 2))  # Ok(10)
        """
        return self.bind(f)

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind (more readable chaining).

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f if Ok, otherwise Error

        Example:
            >>> Result.ok(5).and_then(lambda x: Result.ok(x * 2))  # Ok(10)
        """
        return self.bind(f)

    def map_error(self, f: Callable[[E], E]) -> Result[T, E]:
        """Apply a function to the error value.

        Args:
            f: Function to apply to the error

        Returns:
            Ok(value) if Ok, otherwise Error(f(error))

        Example:
            >>> Result.ok(42).map_error(str.upper)  # Ok(42)
            >>> Result.error("failed").map_error(str.upper)  # Error('FAILED')
        """
        if self._error is None:
            return Result(self._value, None)
        return Result(None, f(self._error))

    def or_else(self, default: Result[T, E]) -> Result[T, E]:
        """Return this Result, or default if this is Error.

        Args:
            default: The Result to return if this is Error

        Returns:
            This Result if Ok, otherwise default

        Example:
            >>> Result.ok(5).or_else(Result.ok(10))  # Ok(5)
            >>> Result.error("failed").or_else(Result.ok(10))  # Ok(10)
        """
        return self if self._error is None else default

    @override
    def __repr__(self) -> str:
        if self._error is None:
            return f"Ok({self._value!r})"
        return f"Error({self._error!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Result):
            return False
        return self._value == other._value and self._error == other._error


__all__ = ["Result"]
