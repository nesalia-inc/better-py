"""AsyncMaybe monad for async optional values.

The AsyncMaybe monad extends Maybe with async operations, supporting
awaitable computations.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar, override

from better_py.protocols import Mappable

if TYPE_CHECKING:
    from better_py.monads import Maybe

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class AsyncMaybe(Mappable[T], Generic[T]):
    """AsyncMaybe monad for async optional values.

    An AsyncMaybe is an awaitable version of Maybe, representing
    either Some(value) or Nothing, with async operations.

    Type Parameters:
        T: The contained type

    Example:
        >>> async_maybe = AsyncMaybe.some(42)
        >>> result = await async_maybe.map(lambda x: x * 2)
    """

    _maybe: Maybe[T]

    @staticmethod
    def some(value: T) -> AsyncMaybe[T]:
        """Create an AsyncMaybe containing a value.

        Args:
            value: The value to wrap

        Returns:
            An AsyncMaybe containing the value

        Example:
            >>> AsyncMaybe.some(42)
            Some(42)
        """
        from better_py.monads import Maybe
        return AsyncMaybe(Maybe.some(value))

    @staticmethod
    def nothing() -> AsyncMaybe[T]:
        """Create an AsyncMaybe with no value.

        Returns:
            An empty AsyncMaybe

        Example:
            >>> AsyncMaybe.nothing()
            Nothing
        """
        from better_py.monads import Maybe
        return AsyncMaybe(Maybe.nothing())

    @staticmethod
    def from_value(value: T | None) -> AsyncMaybe[T]:
        """Create an AsyncMaybe from a value.

        Args:
            value: The value, or None

        Returns:
            Some(value) if value is not None, otherwise Nothing

        Example:
            >>> AsyncMaybe.from_value(42)  # Some(42)
            >>> AsyncMaybe.from_value(None)  # Nothing
        """
        from better_py.monads import Maybe
        return AsyncMaybe(Maybe.from_value(value))

    async def is_some_async(self) -> bool:
        """Check if this is Some (async version).

        Returns:
            True if Some, False otherwise

        Example:
            >>> await AsyncMaybe.some(42).is_some_async()  # True
        """
        return self._maybe.is_some()

    async def is_nothing_async(self) -> bool:
        """Check if this is Nothing (async version).

        Returns:
            True if Nothing, False otherwise

        Example:
            >>> await AsyncMaybe.nothing().is_nothing_async()  # True
        """
        return self._maybe.is_nothing()

    async def unwrap(self) -> T:
        """Get the value, raising an error if Nothing (async).

        Returns:
            The value

        Raises:
            ValueError: If this is Nothing

        Example:
            >>> await AsyncMaybe.some(42).unwrap()  # 42
        """
        return self._maybe.unwrap()

    async def unwrap_or_else(self, default: T) -> T:
        """Get the value or a default (async version).

        Args:
            default: The default value

        Returns:
            The value, or default if Nothing

        Example:
            >>> await AsyncMaybe.nothing().unwrap_or_else(0)  # 0
        """
        return self._maybe.unwrap_or_else(default)

    def map(self, f: Callable[[T], U]) -> AsyncMaybe[U]:
        """Apply a function to the value.

        Args:
            f: Function to apply

        Returns:
            Some(f(value)) if Some, otherwise Nothing

        Example:
            >>> AsyncMaybe.some(5).map(lambda x: x * 2)
        """
        return AsyncMaybe(self._maybe.map(f))

    async def map_async(self, f: Callable[[T], Awaitable[U]]) -> AsyncMaybe[U]:
        """Apply an async function to the value.

        Args:
            f: Async function to apply

        Returns:
            Some(await f(value)) if Some, otherwise Nothing

        Example:
            >>> await AsyncMaybe.some(5).map_async(lambda x: fetch(x))
        """
        from better_py.monads import Maybe
        if self._maybe.is_nothing():
            return AsyncMaybe(Maybe.nothing())
        result = await f(self._maybe.unwrap())
        return AsyncMaybe(Maybe.some(result))

    async def bind(self, f: Callable[[T], AsyncMaybe[U]]) -> AsyncMaybe[U]:
        """Chain operations that return AsyncMaybe (async version).

        Args:
            f: Function that takes a value and returns an AsyncMaybe

        Returns:
            The result of applying f if Some, otherwise Nothing

        Example:
            >>> await async_maybe.bind(lambda x: AsyncMaybe.some(x * 2))
        """
        from better_py.monads import Maybe
        if self._maybe.is_nothing():
            return AsyncMaybe(Maybe.nothing())
        return await f(self._maybe.unwrap())

    def to_maybe(self) -> Maybe:
        """Convert to Maybe.

        Returns:
            The underlying Maybe

        Example:
            >>> AsyncMaybe.some(42).to_maybe()  # Some(42)
        """
        return self._maybe

    @override
    def __repr__(self) -> str:
        return f"AsyncMaybe({self._maybe!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AsyncMaybe):
            return False
        return self._maybe == other._maybe


__all__ = ["AsyncMaybe"]
