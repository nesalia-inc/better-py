"""Result monad for error handling.

The Result monad represents either a successful value (Ok) or an error (Error).
This is a type-safe alternative to exceptions for error handling.

New API (preferred):
    >>> ok = Ok(42)
    >>> error = Error("Something went wrong")

Legacy API (still supported):
    >>> ok = Result.ok(42)
    >>> error = Result.error("Something went wrong")
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


class Result(Mappable[T], Generic[T, E]):
    """Base class for Result monad.

    This class provides factory methods for creating Result values.
    For new code, prefer using Ok() and Error() directly.

    Type Parameters:
        T: The success value type
        E: The error type

    Example (new API - preferred):
        >>> ok = Ok(42)
        >>> error = Error("failed")

    Example (legacy API - still supported):
        >>> ok = Result.ok(42)
        >>> error = Result.error("failed")
    """

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
        return Ok(value)

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
        return Error(error)

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
            return Error(error_value)
        return Ok(value)

    # Abstract methods that subclasses must implement
    def is_ok(self) -> bool:
        """Check if this is Ok variant."""
        raise NotImplementedError()

    def is_error(self) -> bool:
        """Check if this is Error variant."""
        raise NotImplementedError()

    def unwrap(self) -> T:
        """Get the success value, raising an error if Error."""
        raise NotImplementedError()

    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default."""
        raise NotImplementedError()

    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the success value or compute a default."""
        raise NotImplementedError()

    def unwrap_error(self) -> E:
        """Get the error value, raising an error if Ok."""
        raise NotImplementedError()

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the success value."""
        raise NotImplementedError()

    def bind(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations that return Result (monadic bind)."""
        raise NotImplementedError()

    def flat_map(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind."""
        raise NotImplementedError()

    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind (more readable chaining)."""
        raise NotImplementedError()

    def ap(self, fn: Result[Callable[[T], U], E]) -> Result[U, E]:
        """Apply a Result containing a function to this Result."""
        raise NotImplementedError()

    def map_error(self, f: Callable[[E], E]) -> Result[T, E]:
        """Apply a function to the error value."""
        raise NotImplementedError()

    def or_else(self, default: Result[T, E]) -> Result[T, E]:
        """Return this Result, or default if this is Error."""
        raise NotImplementedError()

    @staticmethod
    def lift2(f: Callable[[T, U], object], ma: Result[T, E], mb: Result[U, E]) -> Result[object, E]:
        """Lift a binary function to operate on Result values."""
        curried = ma.map(lambda x: lambda y: f(x, y))
        return mb.ap(curried)

    @staticmethod
    def lift3(
        f: Callable[[T, U, object], object],
        ma: Result[T, E],
        mb: Result[U, E],
        mc: Result[object, E],
    ) -> Result[object, E]:
        """Lift a ternary function to operate on Result values."""
        curried = ma.map(lambda x: lambda y: lambda z: f(x, y, z))
        return mc.ap(mb.ap(curried))

    @staticmethod
    def zip(*results: Result[T, E]) -> Result[tuple[T, ...], E]:
        """Combine multiple Result values into a tuple."""
        vals: list[T] = []
        for r in results:
            if r.is_error():
                return Error(r.unwrap_error())
            vals.append(r.unwrap())
        return Ok(tuple(vals))


@dataclass(frozen=True, slots=True)
class Ok(Result[T, E], Generic[T, E]):
    """Ok variant of Result, containing a success value.

    Type Parameters:
        T: The success value type
        E: The error type (for type compatibility)

    Example:
        >>> ok = Ok(42)
        >>> ok.is_ok()  # True
        >>> ok.unwrap()  # 42
    """

    _value: T

    @override
    def is_ok(self) -> bool:
        """Check if this is Ok variant.

        Returns:
            True - this is Ok

        Example:
            >>> Ok(42).is_ok()  # True
        """
        return True

    @override
    def is_error(self) -> bool:
        """Check if this is Error variant.

        Returns:
            False - this is Ok

        Example:
            >>> Ok(42).is_error()  # False
        """
        return False

    @override
    def unwrap(self) -> T:
        """Get the success value.

        Returns:
            The success value

        Example:
            >>> Ok(42).unwrap()  # 42
        """
        return self._value

    @override
    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default.

        Args:
            default: The default value (ignored for Ok)

        Returns:
            The success value

        Example:
            >>> Ok(42).unwrap_or(0)  # 42
        """
        return self._value

    @override
    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the success value or compute a default.

        Args:
            supplier: The default supplier (ignored for Ok)

        Returns:
            The success value

        Example:
            >>> Ok(42).unwrap_or_else(lambda: 0)  # 42
        """
        return self._value

    @override
    def unwrap_error(self) -> E:
        """Get the error value, raising an error.

        Raises:
            ValueError: Always, since Ok has no error

        Example:
            >>> Ok(42).unwrap_error()  # Raises ValueError
        """
        raise ValueError("Cannot unwrap_error Ok")

    @override
    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Ok(f(value))

        Example:
            >>> Ok(5).map(lambda x: x * 2)  # Ok(10)
        """
        return Ok(f(self._value))

    @override
    def bind(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations that return Result (monadic bind).

        Also known as flatMap or andThen.

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f

        Example:
            >>> def divide(x): return Ok(10 / x) if x != 0 else Error("Div by zero")
            >>> Ok(2).bind(divide)  # Ok(5.0)
        """
        return f(self._value)

    @override
    def flat_map(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind.

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f

        Example:
            >>> Ok(5).flat_map(lambda x: Ok(x * 2))  # Ok(10)
        """
        return self.bind(f)

    @override
    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind (more readable chaining).

        Args:
            f: Function that takes a value and returns a Result

        Returns:
            The result of applying f

        Example:
            >>> Ok(5).and_then(lambda x: Ok(x * 2))  # Ok(10)
        """
        return self.bind(f)

    @override
    def ap(self, fn: Result[Callable[[T], U], E]) -> Result[U, E]:
        """Apply a Result containing a function to this Result.

        Args:
            fn: A Result containing a function

        Returns:
            Ok(f(value)) if fn is Ok, otherwise Error

        Example:
            >>> add = Ok(lambda x: x + 1)
            >>> value = Ok(5)
            >>> add.ap(value)  # Ok(6)
        """
        if fn.is_error():
            return Error(fn.unwrap_error())
        return Ok(fn.unwrap()(self._value))

    @override
    def map_error(self, f: Callable[[E], E]) -> Result[T, E]:
        """Apply a function to the error value (no-op for Ok).

        Args:
            f: Function to apply (ignored for Ok)

        Returns:
            This Ok

        Example:
            >>> Ok(42).map_error(str.upper)  # Ok(42)
        """
        return self

    @override
    def or_else(self, default: Result[T, E]) -> Result[T, E]:
        """Return this Result (since it's Ok).

        Args:
            default: The default Result (ignored)

        Returns:
            This Ok

        Example:
            >>> Ok(5).or_else(Ok(10))  # Ok(5)
        """
        return self

    @override
    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Ok):
            return self._value == other._value
        return False


@dataclass(frozen=True, slots=True)
class Error(Result[T, E], Generic[T, E]):
    """Error variant of Result, containing an error value.

    Type Parameters:
        T: The success value type (for type compatibility)
        E: The error type

    Example:
        >>> error = Error("Division by zero")
        >>> error.is_error()  # True
        >>> error.unwrap_error()  # "Division by zero"
    """

    _error: E

    @override
    def is_ok(self) -> bool:
        """Check if this is Ok variant.

        Returns:
            False - this is Error

        Example:
            >>> Error("failed").is_ok()  # False
        """
        return False

    @override
    def is_error(self) -> bool:
        """Check if this is Error variant.

        Returns:
            True - this is Error

        Example:
            >>> Error("failed").is_error()  # True
        """
        return True

    @override
    def unwrap(self) -> T:
        """Get the success value, raising an error.

        Raises:
            ValueError: Always, since Error has no success value

        Example:
            >>> Error("failed").unwrap()  # Raises ValueError
        """
        raise ValueError(f"Cannot unwrap Error: {self._error}")

    @override
    def unwrap_or(self, default: T) -> T:
        """Get the success value or a default.

        Args:
            default: The default value to return

        Returns:
            The default value

        Example:
            >>> Error("failed").unwrap_or(0)  # 0
        """
        return default

    @override
    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the success value or compute a default.

        Args:
            supplier: A function that produces the default value

        Returns:
            supplier()

        Example:
            >>> Error("failed").unwrap_or_else(lambda: 0)  # 0
        """
        return supplier()

    @override
    def unwrap_error(self) -> E:
        """Get the error value.

        Returns:
            The error value

        Example:
            >>> Error("failed").unwrap_error()  # "failed"
        """
        return self._error

    @override
    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the success value (no-op for Error).

        Args:
            f: Function to apply (ignored for Error)

        Returns:
            This Error

        Example:
            >>> Error("failed").map(lambda x: x * 2)  # Error('failed')
        """
        return self

    @override
    def bind(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Chain operations that return Result (short-circuits for Error).

        Args:
            f: Function (ignored for Error)

        Returns:
            This Error

        Example:
            >>> def divide(x): return Ok(10 / x) if x != 0 else Error("Div by zero")
            >>> Error("failed").bind(divide)  # Error('failed')
        """
        return self

    @override
    def flat_map(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind.

        Args:
            f: Function (ignored for Error)

        Returns:
            This Error
        """
        return self

    @override
    def and_then(self, f: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """Alias for bind.

        Args:
            f: Function (ignored for Error)

        Returns:
            This Error
        """
        return self

    @override
    def ap(self, fn: Result[Callable[[T], U], E]) -> Result[U, E]:
        """Apply a Result containing a function to this Result.

        Args:
            fn: A Result containing a function

        Returns:
            This Error

        Example:
            >>> add = Ok(lambda x: x + 1)
            >>> Error("bad").ap(add)  # Error('bad')
        """
        return self

    @override
    def map_error(self, f: Callable[[E], E]) -> Result[T, E]:
        """Apply a function to the error value.

        Args:
            f: Function to apply

        Returns:
            Error(f(error))

        Example:
            >>> Error("failed").map_error(str.upper)  # Error('FAILED')
        """
        return Error(f(self._error))

    @override
    def or_else(self, default: Result[T, E]) -> Result[T, E]:
        """Return the default Result.

        Args:
            default: The Result to return

        Returns:
            default

        Example:
            >>> Error("failed").or_else(Ok(10))  # Ok(10)
        """
        return default

    @override
    def __repr__(self) -> str:
        return f"Error({self._error!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Error):
            return self._error == other._error
        return False


__all__ = ["Result", "Ok", "Error"]
