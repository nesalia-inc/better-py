"""AsyncResult monad for async result values.

The AsyncResult monad extends Result with async operations, supporting
awaitable computations with Ok/Error states.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import Result

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class AsyncResult(Mappable[T], Generic[T, E]):
    """AsyncResult monad for async result values.

    An AsyncResult is an awaitable version of Result, representing
    either Ok(value) or Error(error), with async operations.

    Type Parameters:
        T: The success type
        E: The error type

    Example:
        >>> async_result = AsyncResult.ok(42)
        >>> result = await async_result.map(lambda x: x * 2)
    """

    _result: Result[T, E]

    @staticmethod
    def ok(value: T) -> AsyncResult[T, E]:
        """Create an AsyncResult containing a success value.

        Args:
            value: The success value

        Returns:
            An AsyncResult containing the value

        Example:
            >>> AsyncResult.ok(42)
            Ok(42)
        """
        from better_py.monads import Result
        return AsyncResult(Result.ok(value))

    @staticmethod
    def error(error: E) -> AsyncResult[T, E]:
        """Create an AsyncResult containing an error.

        Args:
            error: The error value

        Returns:
            An AsyncResult containing the error

        Example:
            >>> AsyncResult.error("failed")
            Error('failed')
        """
        from better_py.monads import Result
        return AsyncResult(Result.error(error))

    @staticmethod
    def from_value(value: T | None, error: E | None = None) -> AsyncResult[T, E]:
        """Create an AsyncResult from a value.

        Args:
            value: The value, or None
            error: The error if value is None

        Returns:
            Ok(value) if value is not None, otherwise Error(error)

        Example:
            >>> AsyncResult.from_value(42)  # Ok(42)
            >>> AsyncResult.from_value(None, "error")  # Error('error')
        """
        from better_py.monads import Result
        if value is None:
            return AsyncResult(Result.error(error))
        return AsyncResult(Result.ok(value))

    async def is_ok_async(self) -> bool:
        """Check if this is Ok (async version).

        Returns:
            True if Ok, False otherwise

        Example:
            >>> await AsyncResult.ok(42).is_ok_async()  # True
        """
        return self._result.is_ok()

    async def is_error_async(self) -> bool:
        """Check if this is Error (async version).

        Returns:
            True if Error, False otherwise

        Example:
            >>> await AsyncResult.error("fail").is_error_async()  # True
        """
        return self._result.is_error()

    async def unwrap(self) -> T:
        """Get the value, raising an error if Error (async).

        Returns:
            The value

        Raises:
            ValueError: If this is Error

        Example:
            >>> await AsyncResult.ok(42).unwrap()  # 42
        """
        return self._result.unwrap()

    async def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the value or compute a default (async version).

        Args:
            supplier: A function that produces the default value

        Returns:
            The value, or supplier() if Error

        Example:
            >>> await AsyncResult.error("fail").unwrap_or_else(lambda: 0)  # 0
        """
        return self._result.unwrap_or_else(supplier)

    async def unwrap_error(self) -> E:
        """Get the error value (async version).

        Returns:
            The error value

        Raises:
            ValueError: If this is Ok

        Example:
            >>> await AsyncResult.error("fail").unwrap_error()  # 'fail'
        """
        return self._result.unwrap_error()

    def map(self, f: Callable[[T], U]) -> AsyncResult[U, E]:
        """Apply a function to the success value.

        Args:
            f: Function to apply

        Returns:
            Ok(f(value)) if Ok, otherwise Error

        Example:
            >>> AsyncResult.ok(5).map(lambda x: x * 2)
        """
        return AsyncResult(self._result.map(f))

    async def map_async(self, f: Callable[[T], Awaitable[U]]) -> AsyncResult[U, E]:
        """Apply an async function to the success value.

        Args:
            f: Async function to apply

        Returns:
            Ok(await f(value)) if Ok, otherwise Error

        Example:
            >>> await AsyncResult.ok(5).map_async(lambda x: fetch(x))
        """
        from better_py.monads import Result
        if self._result.is_error():
            return AsyncResult(Result.error(self._result.unwrap_error()))
        result = await f(self._result.unwrap())
        return AsyncResult(Result.ok(result))

    def map_error(self, f: Callable[[E], E]) -> AsyncResult[T, E]:
        """Apply a function to the error value.

        Args:
            f: Function to apply to the error

        Returns:
            Ok if Ok, otherwise Error(f(error))

        Example:
            >>> AsyncResult.error("fail").map_error(lambda e: f"Error: {e}")
        """
        return AsyncResult(self._result.map_error(f))

    async def bind(self, f: Callable[[T], AsyncResult[U, E] | Awaitable[AsyncResult[U, E]]]) -> AsyncResult[U, E]:
        """Chain operations that return AsyncResult (async version).

        Args:
            f: Function that takes a value and returns an AsyncResult (or awaitable)

        Returns:
            The result of applying f if Ok, otherwise Error

        Example:
            >>> await async_result.bind(lambda x: AsyncResult.ok(x * 2))
        """
        from better_py.monads import Result
        if self._result.is_error():
            return AsyncResult(Result.error(self._result.unwrap_error()))
        # f may return AsyncResult or Awaitable[AsyncResult]
        result = f(self._result.unwrap())
        if isinstance(result, AsyncResult):
            return result
        return await result

    async def recover(self, f: Callable[[E], T]) -> AsyncResult[T, E]:
        """Recover from an error (async version).

        Args:
            f: Function to transform error into success value

        Returns:
            Ok(f(error)) if Error, otherwise Ok

        Example:
            >>> await AsyncResult.error("fail").recover(lambda _: 0)
        """
        from better_py.monads import Result
        if self._result.is_ok():
            return AsyncResult(self._result)
        return AsyncResult(Result.ok(f(self._result.unwrap_error())))

    def to_result(self) -> Result[T, E]:
        """Convert to Result.

        Returns:
            The underlying Result

        Example:
            >>> AsyncResult.ok(42).to_result()  # Ok(42)
        """
        return self._result

    @override
    def __repr__(self) -> str:
        return f"AsyncResult({self._result!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncResult):
            return False
        return self._result == other._result


__all__ = ["AsyncResult"]
