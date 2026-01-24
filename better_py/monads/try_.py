"""Try monad for exception handling.

The Try monad represents either a successful value or an exception,
providing a type-safe way to handle operations that may throw exceptions.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import Maybe

T = TypeVar("T")  # Success type
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Try(Mappable[T], Generic[T]):
    """Try monad for exception handling.

    A Try is either Success(value) or Failure(exception), representing
    the success or failure of an operation that may throw exceptions.

    Type Parameters:
        T: The success value type

    Example:
        >>> result = Try(lambda: 1 / 0)  # Failure(ZeroDivisionError)
        >>> result = Try(lambda: 10 / 2)  # Success(5.0)
    """

    _value: T | None
    _exception: BaseException | None

    @staticmethod
    def of(f: Callable[[], T]) -> Try[T]:
        """Execute a function and catch any exceptions.

        Args:
            f: Function to execute

        Returns:
            Success(f()) if no exception, otherwise Failure(exception)

        Example:
            >>> Try.of(lambda: 42)  # Success(42)
            >>> Try.of(lambda: int("abc"))  # Failure(ValueError)
        """
        try:
            return Try(f(), None)
        except BaseException as e:
            return Try(None, e)

    @staticmethod
    def success(value: T) -> Try[T]:
        """Create a Success Try containing a value.

        Args:
            value: The success value

        Returns:
            A Success variant containing the value

        Example:
            >>> Try.success(42)
            Success(42)
        """
        return Try(value, None)

    @staticmethod
    def failure(exception: BaseException) -> Try[T]:
        """Create a Failure Try containing an exception.

        Args:
            exception: The exception

        Returns:
            A Failure variant containing the exception

        Example:
            >>> Try.failure(ValueError("Invalid"))
            Failure(ValueError('Invalid'))
        """
        return Try(None, exception)

    def is_success(self) -> bool:
        """Check if this is Success.

        Returns:
            True if Success, False otherwise

        Example:
            >>> Try.success(42).is_success()  # True
            >>> Try.failure(ValueError("x")).is_success()  # False
        """
        return self._exception is None

    def is_failure(self) -> bool:
        """Check if this is Failure.

        Returns:
            True if Failure, False otherwise

        Example:
            >>> Try.failure(ValueError("x")).is_failure()  # True
            >>> Try.success(42).is_failure()  # False
        """
        return self._exception is not None

    def get(self) -> T | None:
        """Get the success value, or None if Failure.

        Returns:
            The success value, or None if Failure

        Example:
            >>> Try.success(42).get()  # 42
            >>> Try.failure(ValueError("x")).get()  # None
        """
        return self._value

    def get_exception(self) -> BaseException | None:
        """Get the exception, or None if Success.

        Returns:
            The exception, or None if Success

        Example:
            >>> Try.failure(ValueError("x")).get_exception()  # ValueError
            >>> Try.success(42).get_exception()  # None
        """
        return self._exception

    def get_or_else(self, default: T) -> T:
        """Get the success value, or a default if Failure.

        Args:
            default: The default value

        Returns:
            The success value, or default if Failure

        Example:
            >>> Try.success(42).get_or_else(0)  # 42
            >>> Try.failure(ValueError("x")).get_or_else(0)  # 0
        """
        if self._exception is None:
            # _value is not None when _exception is None
            assert self._value is not None
            return self._value
        return default

    def recover(self, f: Callable[[BaseException], T]) -> Try[T]:
        """Recover from a failure using a function.

        Args:
            f: Function to handle the exception

        Returns:
            Success(f(exception)) if Failure, otherwise Success(value)

        Example:
            >>> Try.failure(ValueError("x")).recover(lambda e: 0)  # Success(0)
            >>> Try.success(42).recover(lambda e: 0)  # Success(42)
        """
        if self._exception is not None:
            try:
                return Try(f(self._exception), None)
            except BaseException:
                return Try(None, self._exception)
        # _value is not None when _exception is None
        assert self._value is not None
        return Try(self._value, None)

    def map(self, f: Callable[[T], U]) -> Try[U]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Success(f(value)) if Success, otherwise Failure

        Example:
            >>> Try.success(5).map(lambda x: x * 2)  # Success(10)
            >>> Try.failure(ValueError("x")).map(lambda x: x * 2)  # Failure
        """
        if self._exception is not None:
            return Try(None, self._exception)
        try:
            # _value is not None when _exception is None
            assert self._value is not None
            return Try(f(self._value), None)
        except BaseException as e:
            return Try(None, e)

    def flat_map(self, f: Callable[[T], Try[U]]) -> Try[U]:
        """Chain operations that return Try.

        Args:
            f: Function that takes a value and returns a Try

        Returns:
            The result of applying f if Success, otherwise Failure

        Example:
            >>> def divide(x): return Try(lambda: 10 / x)
            >>> Try.success(2).flat_map(divide)  # Success(5.0)
            >>> Try.success(0).flat_map(divide)  # Failure
        """
        if self._exception is not None:
            return Try(None, self._exception)
        try:
            # _value is not None when _exception is None
            assert self._value is not None
            result = f(self._value)
            return result
        except BaseException as e:
            return Try(None, e)

    def fold(self, on_failure: Callable[[BaseException], U], on_success: Callable[[T], U]) -> U:
        """Fold both cases into a single value.

        Args:
            on_failure: Function to apply if Failure
            on_success: Function to apply if Success

        Returns:
            Result of applying the appropriate function

        Example:
            >>> result = Try.success(42).fold(
            ...     on_failure=lambda e: f"Error: {e}",
            ...     on_success=lambda v: f"Value: {v}"
            ... )
            >>> "Value: 42"
        """
        if self._exception is not None:
            return on_failure(self._exception)
        # _value is not None when _exception is None
        assert self._value is not None
        return on_success(self._value)

    def to_option(self) -> Maybe[T]:
        """Convert Try to Maybe.

        Returns:
            Some(value) if Success, Nothing if Failure

        Example:
            >>> Try.success(42).to_option()  # Some(42)
            >>> Try.failure(ValueError("x")).to_option()  # Nothing
        """
        from better_py.monads import Maybe

        if self._exception is not None:
            return Maybe.nothing()
        # _value is not None when _exception is None
        assert self._value is not None
        return Maybe.some(self._value)

    @override
    def __repr__(self) -> str:
        if self._exception is not None:
            return f"Failure({self._exception!r})"
        return f"Success({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Try):
            return False
        return self._value == other._value and self._exception == other._exception


__all__ = ["Try"]
