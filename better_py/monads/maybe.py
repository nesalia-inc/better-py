"""Maybe monad for handling optional values.

The Maybe monad represents optional values: either Some(value) or Nothing.
This is a type-safe alternative to using None.

New API (preferred):
    >>> some = Some(5)
    >>> nothing = Nothing()
    >>> some_none = Some(None)

Legacy API (still supported):
    >>> some = Maybe.some(5)
    >>> nothing = Maybe.nothing()
    >>> some_none = Maybe.some_none()
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable

T = TypeVar("T")
U = TypeVar("U")


class Maybe(Mappable[T], Generic[T]):
    """Base class for Maybe monad.

    This class provides factory methods for creating Maybe values.
    For new code, prefer using Some() and Nothing() directly.

    Type Parameters:
        T: The type of the contained value

    Example (new API - preferred):
        >>> some = Some(5)
        >>> nothing = Nothing()

    Example (legacy API - still supported):
        >>> some = Maybe.some(5)
        >>> nothing = Maybe.nothing()
    """

    @staticmethod
    def some(value: T) -> Maybe[T]:
        """Create a Maybe containing a value.

        Args:
            value: The value to wrap (can be None, use some_none() instead)

        Returns:
            A Some variant containing the value

        Example:
            >>> Maybe.some(42)
            Some(42)
        """
        return Some(value)

    @staticmethod
    def some_none() -> Maybe[T | None]:
        """Create a Maybe explicitly containing None.

        This distinguishes between "value is None" and "no value".

        Returns:
            A Some variant containing None

        Example:
            >>> maybe_none = Maybe.some_none()
            >>> maybe_none.is_some()  # True - it has a value (None)
            >>> maybe_none.unwrap() is None  # True - the value is None
            >>> maybe_none == Maybe.nothing()  # False - different from Nothing
        """
        return Some(None)

    @staticmethod
    def nothing() -> Maybe[T]:
        """Create an empty Maybe (Nothing variant).

        Returns:
            A Nothing variant

        Example:
            >>> Maybe.nothing()
            Nothing
        """
        return Nothing()

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

        Note:
            To explicitly wrap None as a value, use Maybe.some_none()
        """
        if value is None:
            return Nothing()
        return Some(value)

    # Abstract methods that subclasses must implement
    def is_some(self) -> bool:
        """Check if this is Some variant."""
        raise NotImplementedError()

    def is_nothing(self) -> bool:
        """Check if this is Nothing variant."""
        raise NotImplementedError()

    def unwrap(self) -> T:
        """Get the contained value, raising an error if Nothing."""
        raise NotImplementedError()

    def unwrap_or(self, default: T) -> T:
        """Get the contained value or a default."""
        raise NotImplementedError()

    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the contained value or compute a default."""
        raise NotImplementedError()

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value."""
        raise NotImplementedError()

    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that return Maybe (monadic bind)."""
        raise NotImplementedError()

    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind."""
        raise NotImplementedError()

    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind (more readable chaining)."""
        raise NotImplementedError()

    def ap(self, fn: Maybe[Callable[[T], U]]) -> Maybe[U]:
        """Apply a Maybe containing a function to this Maybe."""
        raise NotImplementedError()

    def or_else(self, default: Maybe[T]) -> Maybe[T]:
        """Return this Maybe, or default if this is Nothing."""
        raise NotImplementedError()

    @staticmethod
    def lift2(f: Callable[[T, U], object], ma: Maybe[T], mb: Maybe[U]) -> Maybe[object]:
        """Lift a binary function to operate on Maybe values."""
        curried = ma.map(lambda x: lambda y: f(x, y))
        return mb.ap(curried)

    @staticmethod
    def lift3(
        f: Callable[[T, U, object], object],
        ma: Maybe[T],
        mb: Maybe[U],
        mc: Maybe[object],
    ) -> Maybe[object]:
        """Lift a ternary function to operate on Maybe values."""
        curried = ma.map(lambda x: lambda y: lambda z: f(x, y, z))
        return mc.ap(mb.ap(curried))

    @staticmethod
    def zip(*monads: Maybe[T]) -> Maybe[tuple[T, ...]]:
        """Combine multiple Maybe values into a tuple."""
        result: list[T] = []
        for m in monads:
            if m.is_nothing():
                return Nothing()
            result.append(m.unwrap())
        return Some(tuple(result))


@dataclass(frozen=True, slots=True)
class Some(Maybe[T], Generic[T]):
    """Some variant of Maybe, containing a value.

    Type Parameters:
        T: The type of the contained value

    Example:
        >>> some = Some(42)
        >>> some.is_some()  # True
        >>> some.unwrap()  # 42
    """

    _value: T

    @override
    def is_some(self) -> bool:
        """Check if this is Some variant.

        Returns:
            True - this is Some

        Example:
            >>> Some(5).is_some()  # True
        """
        return True

    @override
    def is_nothing(self) -> bool:
        """Check if this is Nothing variant.

        Returns:
            False - this is Some

        Example:
            >>> Some(5).is_nothing()  # False
        """
        return False

    @override
    def unwrap(self) -> T:
        """Get the contained value.

        Returns:
            The contained value (which may be None for Some(None))

        Example:
            >>> Some(42).unwrap()  # 42
            >>> Some(None).unwrap()  # None
        """
        return self._value

    @override
    def unwrap_or(self, default: T) -> T:
        """Get the contained value or a default.

        Args:
            default: The default value (ignored for Some)

        Returns:
            The contained value

        Example:
            >>> Some(42).unwrap_or(0)  # 42
        """
        return self._value

    @override
    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the contained value or compute a default.

        Args:
            supplier: The default supplier (ignored for Some)

        Returns:
            The contained value

        Example:
            >>> Some(42).unwrap_or_else(lambda: 0)  # 42
        """
        return self._value

    @override
    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value.

        Args:
            f: Function to apply

        Returns:
            Some(f(value))

        Example:
            >>> Some(5).map(lambda x: x * 2)  # Some(10)
        """
        return Some(f(self._value))

    @override
    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that return Maybe (monadic bind).

        Also known as flatMap or andThen.

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f

        Example:
            >>> def divide(x): return Some(10 / x) if x != 0 else Nothing()
            >>> Some(2).bind(divide)  # Some(5.0)
        """
        return f(self._value)

    @override
    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind.

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f

        Example:
            >>> Some(5).flat_map(lambda x: Some(x * 2))  # Some(10)
        """
        return self.bind(f)

    @override
    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind (more readable chaining).

        Args:
            f: Function that takes a value and returns a Maybe

        Returns:
            The result of applying f

        Example:
            >>> Some(5).and_then(lambda x: Some(x * 2))  # Some(10)
        """
        return self.bind(f)

    @override
    def ap(self, fn: Maybe[Callable[[T], U]]) -> Maybe[U]:
        """Apply a Maybe containing a function to this Maybe.

        Args:
            fn: A Maybe containing a function

        Returns:
            Some(f(value)) if fn is Some, otherwise Nothing

        Example:
            >>> add = Some(lambda x: x + 1)
            >>> value = Some(5)
            >>> add.ap(value)  # Some(6)
        """
        if fn.is_nothing():
            return Nothing()
        return Some(fn.unwrap()(self._value))

    @override
    def or_else(self, default: Maybe[T]) -> Maybe[T]:
        """Return this Maybe (since it's Some).

        Args:
            default: The default Maybe (ignored)

        Returns:
            This Some

        Example:
            >>> Some(5).or_else(Some(10))  # Some(5)
        """
        return self

    @override
    def __repr__(self) -> str:
        return f"Some({self._value!r})"

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Some):
            return self._value == other._value
        return False


@dataclass(frozen=True, slots=True)
class Nothing(Maybe[T], Generic[T]):
    """Nothing variant of Maybe, representing absence of a value.

    Type Parameters:
        T: The type that would be contained if this were Some

    Example:
        >>> nothing = Nothing()
        >>> nothing.is_nothing()  # True
        >>> nothing.unwrap_or(0)  # 0
    """

    @override
    def is_some(self) -> bool:
        """Check if this is Some variant.

        Returns:
            False - this is Nothing

        Example:
            >>> Nothing().is_some()  # False
        """
        return False

    @override
    def is_nothing(self) -> bool:
        """Check if this is Nothing variant.

        Returns:
            True - this is Nothing

        Example:
            >>> Nothing().is_nothing()  # True
        """
        return True

    @override
    def unwrap(self) -> T:
        """Get the contained value, raising an error.

        Raises:
            ValueError: Always, since Nothing has no value

        Example:
            >>> Nothing().unwrap()  # Raises ValueError
        """
        raise ValueError("Cannot unwrap Nothing")

    @override
    def unwrap_or(self, default: T) -> T:
        """Get the contained value or a default.

        Args:
            default: The default value to return

        Returns:
            The default value

        Example:
            >>> Nothing().unwrap_or(0)  # 0
        """
        return default

    @override
    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the contained value or compute a default.

        Args:
            supplier: A function that produces the default value

        Returns:
            supplier()

        Example:
            >>> Nothing().unwrap_or_else(lambda: 0)  # 0
        """
        return supplier()

    @override
    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value.

        Args:
            f: Function to apply (ignored for Nothing)

        Returns:
            Nothing

        Example:
            >>> Nothing().map(lambda x: x * 2)  # Nothing
        """
        return Nothing()

    @override
    def bind(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Chain operations that return Maybe.

        Args:
            f: Function (ignored for Nothing)

        Returns:
            Nothing

        Example:
            >>> def divide(x): return Some(10 / x) if x != 0 else Nothing()
            >>> Nothing().bind(divide)  # Nothing
        """
        return Nothing()

    @override
    def flat_map(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind.

        Args:
            f: Function (ignored for Nothing)

        Returns:
            Nothing
        """
        return Nothing()

    @override
    def and_then(self, f: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Alias for bind.

        Args:
            f: Function (ignored for Nothing)

        Returns:
            Nothing
        """
        return Nothing()

    @override
    def ap(self, fn: Maybe[Callable[[T], U]]) -> Maybe[U]:
        """Apply a Maybe containing a function to this Maybe.

        Args:
            fn: A Maybe containing a function

        Returns:
            Nothing

        Example:
            >>> add = Some(lambda x: x + 1)
            >>> Nothing().ap(add)  # Nothing
        """
        return Nothing()

    @override
    def or_else(self, default: Maybe[T]) -> Maybe[T]:
        """Return the default Maybe.

        Args:
            default: The Maybe to return

        Returns:
            default

        Example:
            >>> Nothing().or_else(Some(10))  # Some(10)
        """
        return default

    @override
    def __repr__(self) -> str:
        return "Nothing"

    @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Nothing)


__all__ = ["Maybe", "Some", "Nothing"]
