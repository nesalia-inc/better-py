"""Maybe monad for handling optional values.

The Maybe monad represents optional values: either Some(value) or Nothing.
This is a type-safe alternative to using None.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

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

    def ap(self, fn: Maybe[Callable[[T], U]]) -> Maybe[U]:
        """Apply a Maybe containing a function to this Maybe.

        Args:
            fn: A Maybe containing a function

        Returns:
            Some(f(value)) if both are Some, otherwise Nothing

        Example:
            >>> add = Maybe.some(lambda x: x + 1)
            >>> value = Maybe.some(5)
            >>> add.ap(value)  # Some(6)
            >>> Maybe.nothing().ap(value)  # Nothing
            >>> add.ap(Maybe.nothing())  # Nothing
        """
        if self._value is None or fn._value is None:
            return Maybe(None)
        assert fn._value is not None
        return Maybe(fn._value(self._value))

    @staticmethod
    def lift2(f: Callable[[T, U], object], ma: Maybe[T], mb: Maybe[U]) -> Maybe[object]:
        """Lift a binary function to operate on Maybe values.

        Args:
            f: A binary function
            ma: First Maybe value
            mb: Second Maybe value

        Returns:
            Some(f(a, b)) if both are Some, otherwise Nothing

        Example:
            >>> Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.some(2))  # Some(3)
            >>> Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.nothing())  # Nothing
        """
        curried = ma.map(lambda x: lambda y: f(x, y))
        return mb.ap(curried)

    @staticmethod
    def lift3(f: Callable[[T, U, object], object], ma: Maybe[T], mb: Maybe[U], mc: Maybe[object]) -> Maybe[object]:
        """Lift a ternary function to operate on Maybe values.

        Args:
            f: A ternary function
            ma: First Maybe value
            mb: Second Maybe value
            mc: Third Maybe value

        Returns:
            Some(f(a, b, c)) if all are Some, otherwise Nothing

        Example:
            >>> Maybe.lift3(lambda x, y, z: x + y + z, Maybe.some(1), Maybe.some(2), Maybe.some(3))  # Some(6)
        """
        curried = ma.map(lambda x: lambda y: lambda z: f(x, y, z))
        return mc.ap(mb.ap(curried))

    @staticmethod
    def zip(*monads: Maybe[T]) -> Maybe[tuple[T, ...]]:
        """Combine multiple Maybe values into a tuple.

        Args:
            *monads: Maybe values to combine

        Returns:
            Some(tuple of values) if all are Some, otherwise Nothing

        Example:
            >>> Maybe.zip(Maybe.some(1), Maybe.some(2), Maybe.some(3))  # Some((1, 2, 3))
            >>> Maybe.zip(Maybe.some(1), Maybe.nothing(), Maybe.some(3))  # Nothing
        """
        result: list[T] = []
        for m in monads:
            if m._value is None:
                return Maybe(None)
            assert m._value is not None
            result.append(m._value)
        return Maybe(tuple(result))

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
