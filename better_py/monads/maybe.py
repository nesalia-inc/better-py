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

    Note: Maybe can now contain None as a valid value. Use Maybe.some_none()
    to explicitly create a Maybe containing None, distinguishing it from
    Nothing (no value).

    Type Parameters:
        T: The type of the contained value

    Example:
        >>> some = Maybe.some(5)
        >>> nothing = Maybe.nothing()
        >>> some_none = Maybe.some_none()
        >>> some.is_some()  # True
        >>> nothing.is_nothing()  # True
        >>> some_none.is_some()  # True - contains None as a value
    """

    _value: T | None
    _is_defined: bool = True  # False for Nothing, True for Some (even if value is None)

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
        return Maybe(value, True)

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
        return Maybe(None, True)

    @staticmethod
    def nothing() -> Maybe[T]:
        """Create an empty Maybe (Nothing variant).

        Returns:
            A Nothing variant

        Example:
            >>> Maybe.nothing()
            Nothing
        """
        return Maybe(None, False)

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
            return Maybe(None, False)
        return Maybe(value, True)

    def is_some(self) -> bool:
        """Check if this is Some variant.

        Returns:
            True if containing a value (even if that value is None), False otherwise

        Example:
            >>> Maybe.some(5).is_some()  # True
            >>> Maybe.nothing().is_some()  # False
            >>> Maybe.some_none().is_some()  # True - contains None as value
        """
        return self._is_defined

    def is_nothing(self) -> bool:
        """Check if this is Nothing variant.

        Returns:
            True if empty, False otherwise

        Example:
            >>> Maybe.some(5).is_nothing()  # False
            >>> Maybe.nothing().is_nothing()  # True
            >>> Maybe.some_none().is_nothing()  # False - it's Some(None)
        """
        return not self._is_defined

    def unwrap(self) -> T:
        """Get the contained value, raising an error if Nothing.

        Returns:
            The contained value (which may be None for some_none())

        Raises:
            ValueError: If this is Nothing

        Example:
            >>> Maybe.some(42).unwrap()  # 42
            >>> Maybe.some_none().unwrap()  # None (valid value)
            >>> Maybe.nothing().unwrap()  # Raises ValueError
        """
        if not self._is_defined:
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
            >>> Maybe.some_none().unwrap_or(0)  # None (contained value)
            >>> Maybe.nothing().unwrap_or(0)  # 0
        """
        return self._value if self._is_defined else default

    def unwrap_or_else(self, supplier: Callable[[], T]) -> T:
        """Get the contained value or compute a default.

        Args:
            supplier: A function that produces the default value

        Returns:
            The contained value, or supplier() if Nothing

        Example:
            >>> Maybe.some(42).unwrap_or_else(lambda: 0)  # 42
            >>> Maybe.some_none().unwrap_or_else(lambda: 0)  # None (contained value)
            >>> Maybe.nothing().unwrap_or_else(lambda: 0)  # 0
        """
        return self._value if self._is_defined else supplier()

    def map(self, f: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value.

        Args:
            f: Function to apply

        Returns:
            Some(f(value)) if Some, otherwise Nothing

        Example:
            >>> Maybe.some(5).map(lambda x: x * 2)  # Some(10)
            >>> Maybe.some_none().map(lambda x: x or "default")  # Some("default")
            >>> Maybe.nothing().map(lambda x: x * 2)  # Nothing
        """
        if not self._is_defined:
            return Maybe(None, False)
        return Maybe(f(self._value), True)

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
        if not self._is_defined:
            return Maybe(None, False)
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
        if not self._is_defined or not fn._is_defined:
            return Maybe(None, False)
        assert fn._value is not None
        return Maybe(fn._value(self._value), True)

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
            if not m._is_defined:
                return Maybe(None, False)
            result.append(m._value)
        return Maybe(tuple(result), True)

    def or_else(self, default: Maybe[T]) -> Maybe[T]:
        """Return this Maybe, or default if this is Nothing.

        Args:
            default: The Maybe to return if this is Nothing

        Returns:
            This Maybe if Some, otherwise default

        Example:
            >>> Maybe.some(5).or_else(Maybe.some(10))  # Some(5)
            >>> Maybe.some_none().or_else(Maybe.some(10))  # Some(None)
            >>> Maybe.nothing().or_else(Maybe.some(10))  # Some(10)
        """
        return self if self._is_defined else default

    @override
    def __repr__(self) -> str:
        if not self._is_defined:
            return "Nothing"
        return f"Some({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Maybe):
            return False
        # Two Maybes are equal if both are Nothing or both have same value and defined state
        if not self._is_defined and not other._is_defined:
            return True
        if self._is_defined != other._is_defined:
            return False
        return self._value == other._value


__all__ = ["Maybe"]
