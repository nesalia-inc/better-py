"""Maybe monad for handling optional values.

The Maybe monad represents optional values: either Some(value) or Nothing.
This is a type-safe alternative to using None.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, override

from better_py.protocols import Mappable

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Maybe(Mappable[T], Generic[T]):
    """Maybe monad for optional values.

    A Maybe is either Some(value) or Nothing, representing the presence
    or absence of a value in a type-safe way.

    Type Parameters:
        T: The type of the contained value

    Example:
        >>> some = Maybe.some(5)
        >>> nothing = Maybe.nothing()
        >>> some.is_some()  # True
        >>> nothing.is_nothing()  # True
    """

    _value: T | None

    @staticmethod
    def some(value: T) -> Maybe[T]:
        """Create a Maybe containing a value.

        Args:
            value: The value to wrap

        Returns:
            A Some variant containing the value

        Example:
            >>> Maybe.some(42)
            Some(42)
        """
        return Maybe(value)

    @staticmethod
    def nothing() -> Maybe[T]:
        """Create an empty Maybe (Nothing variant).

        Returns:
            A Nothing variant

        Example:
            >>> Maybe.nothing()
            Nothing
        """
        return Maybe(None)

    @staticmethod
    def from_value(value: T | None) -> Maybe[T]:
        """Create a Maybe from an optional value.

        Args:
            value: A value that might be None

        Returns:
            Some(value) if value is not None, otherwise Nothing

        Example:
            >>> Maybe.from_value(42)
            Some(42)
            >>> Maybe.from_value(None)
            Nothing
        """
        return Maybe(value)

    def is_some(self) -> bool:
        """Check if this is Some variant.

        Returns:
            True if containing a value, False otherwise

        Example:
            >>> Maybe.some(5).is_some()  # True
            >>> Maybe.nothing().is_some()  # False
        """
        return self._value is not None

    def is_nothing(self) -> bool:
        """Check if this is Nothing variant.

        Returns:
            True if empty, False otherwise

        Example:
            >>> Maybe.some(5).is_nothing()  # False
            >>> Maybe.nothing().is_nothing()  # True
        """
        return self._value is None

    def unwrap(self) -> T:
        """Get the contained value, raising an error if Nothing.

        Returns:
            The contained value

        Raises:
            ValueError: If this is Nothing

        Example:
            >>> Maybe.some(42).unwrap()  # 42
            >>> Maybe.nothing().unwrap()  # Raises ValueError
        """
        if self._value is None:
            raise ValueError("Cannot unwrap Nothing")
        return self._value

    def unwrap_or(self, default: T) -> T:
        """Get the contained value or a default.

        Args:
            default: The default value to return if Nothing

        Returns:
            The contained value, or default if Nothing

        Example:
            >>> Maybe.some(42).unwrap_or(0)  # 42
            >>> Maybe.nothing().unwrap_or(0)  # 0
        """
        return self._value if self._value is not None else default

    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the contained value or compute a default.

        Args:
            supplier: A function that produces the default value

        Returns:
            The contained value, or supplier() if Nothing

        Example:
            >>> Maybe.some(42).unwrap_or_else(lambda: 0)  # 42
            >>> Maybe.nothing().unwrap_or_else(lambda: 0)  # 0
        """
        return self._value if self._value is not None else supplier()

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value.

        Args:
            f: Function to apply

        Returns:
            Some(f(value)) if Some, otherwise Nothing

        Example:
            >>> Maybe.some(5).map(lambda x: x * 2)  # Some(10)
            >>> Maybe.nothing().map(lambda x: x * 2)  # Nothing
        """
        if self._value is None:
            return Maybe(None)
        return Maybe(f(self._value))

    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that return Maybe (monadic bind).

        Also known as flatMap or andThen.

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f if Some, otherwise Nothing

        Example:
            >>> def divide(x): return Maybe.some(10 / x) if x != 0 else Maybe.nothing()
            >>> Maybe.some(2).bind(divide)  # Some(5.0)
            >>> Maybe.some(0).bind(divide)  # Nothing
            >>> Maybe.nothing().bind(divide)  # Nothing
        """
        if self._value is None:
            return Maybe(None)
        return f(self._value)

    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind.

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f if Some, otherwise Nothing

        Example:
            >>> Maybe.some(5).flat_map(lambda x: Maybe.some(x * 2))  # Some(10)
        """
        return self.bind(f)

    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind (more readable chaining).

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f if Some, otherwise Nothing

        Example:
            >>> Maybe.some(5).and_then(lambda x: Maybe.some(x * 2))  # Some(10)
        """
        return self.bind(f)

    def or_else(self, default: Maybe[T]) -> Maybe[T]:
        """Return this Maybe, or default if this is Nothing.

        Args:
            default: The Maybe to return if this is Nothing

        Returns:
            This Maybe if Some, otherwise default

        Example:
            >>> Maybe.some(5).or_else(Maybe.some(10))  # Some(5)
            >>> Maybe.nothing().or_else(Maybe.some(10))  # Some(10)
        """
        return self if self._value is not None else default

    @override
    def __repr__(self) -> str:
        if self._value is None:
            return "Nothing"
        return f"Some({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Maybe):
            return False
        return self._value == other._value


__all__ = ["Maybe"]
