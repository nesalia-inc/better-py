"""Persistent set for functional programming.

A PersistentSet is an immutable set with structural sharing.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Reducible

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class PersistentSet(Reducible[T], Generic[T]):
    """Immutable set with structural sharing.

    A PersistentSet is an immutable set that never mutates.
    Operations that would "modify" the set instead return new sets
    while sharing structure with the original.

    Type Parameters:
        T: The element type (must be hashable)

    Example:
        >>> s = PersistentSet.of(1, 2, 3)
        >>> new_s = s.add(4)
        >>> s  # Still {1, 2, 3}
        >>> new_s  # {1, 2, 3, 4}
    """

    _data: set[T]

    def __init__(self, data: set[T] | None = None) -> None:
        """Initialize the set.

        Args:
            data: Optional set to initialize with
        """
        object.__setattr__(self, "_data", set(data) if data else set())

    @staticmethod
    def empty() -> PersistentSet[T]:
        """Create an empty set.

        Returns:
            An empty PersistentSet

        Example:
            >>> PersistentSet.empty()
            PersistentSet()
        """
        return PersistentSet()

    @staticmethod
    def of(*items: T) -> PersistentSet[T]:
        """Create a set from items.

        Args:
            *items: Items to add to the set

        Returns:
            A new PersistentSet containing the items

        Example:
            >>> PersistentSet.of(1, 2, 3)
            PersistentSet({1, 2, 3})
        """
        return PersistentSet(set(items))

    @staticmethod
    def from_iterable(items: Iterable[T]) -> PersistentSet[T]:
        """Create a set from an iterable.

        Args:
            items: Iterable of items

        Returns:
            A new PersistentSet containing the items

        Example:
            >>> PersistentSet.from_iterable([1, 2, 3])
            PersistentSet({1, 2, 3})
        """
        return PersistentSet(set(items))

    def is_empty(self) -> bool:
        """Check if the set is empty.

        Returns:
            True if empty, False otherwise

        Example:
            >>> PersistentSet.empty().is_empty()  # True
            >>> PersistentSet.of(1).is_empty()  # False
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Get the number of elements.

        Returns:
            The number of unique elements

        Example:
            >>> PersistentSet.of(1, 2, 3).size()  # 3
        """
        return len(self._data)

    def contains(self, item: T) -> bool:
        """Check if an item is in the set.

        Args:
            item: The item to check

        Returns:
            True if item is in the set, False otherwise

        Example:
            >>> PersistentSet.of(1, 2, 3).contains(2)  # True
            >>> PersistentSet.of(1, 2, 3).contains(4)  # False
        """
        return item in self._data

    def add(self, item: T) -> PersistentSet[T]:
        """Add an item to the set.

        Args:
            item: Item to add

        Returns:
            A new set with the item

        Example:
            >>> s = PersistentSet.of(1, 2)
            >>> s.add(3)  # PersistentSet({1, 2, 3})
        """
        new_data = set(self._data)
        new_data.add(item)
        return PersistentSet(new_data)

    def remove(self, item: T) -> PersistentSet[T]:
        """Remove an item from the set.

        Args:
            item: Item to remove

        Returns:
            A new set without the item

        Example:
            >>> s = PersistentSet.of(1, 2, 3)
            >>> s.remove(2)  # PersistentSet({1, 3})
        """
        new_data = set(self._data)
        new_data.discard(item)
        return PersistentSet(new_data)

    def union(self, other: PersistentSet[T]) -> PersistentSet[T]:
        """Get the union of two sets.

        Args:
            other: Another set

        Returns:
            A new set with elements from both sets

        Example:
            >>> s1 = PersistentSet.of(1, 2)
            >>> s2 = PersistentSet.of(2, 3)
            >>> s1.union(s2)  # PersistentSet({1, 2, 3})
        """
        return PersistentSet(self._data | other._data)

    def intersection(self, other: PersistentSet[T]) -> PersistentSet[T]:
        """Get the intersection of two sets.

        Args:
            other: Another set

        Returns:
            A new set with elements in both sets

        Example:
            >>> s1 = PersistentSet.of(1, 2)
            >>> s2 = PersistentSet.of(2, 3)
            >>> s1.intersection(s2)  # PersistentSet({2})
        """
        return PersistentSet(self._data & other._data)

    def difference(self, other: PersistentSet[T]) -> PersistentSet[T]:
        """Get the difference of two sets.

        Args:
            other: Another set

        Returns:
            A new set with elements in self but not in other

        Example:
            >>> s1 = PersistentSet.of(1, 2)
            >>> s2 = PersistentSet.of(2, 3)
            >>> s1.difference(s2)  # PersistentSet({1})
        """
        return PersistentSet(self._data - other._data)

    def is_subset(self, other: PersistentSet[T]) -> bool:
        """Check if this set is a subset of another.

        Args:
            other: Another set

        Returns:
            True if all elements of self are in other

        Example:
            >>> s1 = PersistentSet.of(1, 2)
            >>> s2 = PersistentSet.of(1, 2, 3)
            >>> s1.is_subset(s2)  # True
        """
        return self._data <= other._data

    def is_superset(self, other: PersistentSet[T]) -> bool:
        """Check if this set is a superset of another.

        Args:
            other: Another set

        Returns:
            True if all elements of other are in self

        Example:
            >>> s1 = PersistentSet.of(1, 2, 3)
            >>> s2 = PersistentSet.of(1, 2)
            >>> s1.is_superset(s2)  # True
        """
        return self._data >= other._data

    def map(self, f: Callable[[T], T]) -> "PersistentSet[T]":
        """Apply a function to all elements.

        Args:
            f: Function to apply

        Returns:
            A new set with transformed elements

        Example:
            >>> PersistentSet.of(1, 2, 3).map(lambda x: x * 2)
            PersistentSet({2, 4, 6})
        """
        return PersistentSet({f(x) for x in self._data})

    def filter(self, predicate: Callable[[T], bool]) -> PersistentSet[T]:
        """Filter elements by a predicate.

        Args:
            predicate: Function to test each element

        Returns:
            A new set with elements that pass the predicate

        Example:
            >>> PersistentSet.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0)
            PersistentSet({2, 4})
        """
        return PersistentSet({x for x in self._data if predicate(x)})

    def reduce(self, f: Callable[[U, T], U], initial: U) -> U:
        """Reduce the set to a single value.

        Args:
            f: Function to combine values
            initial: Initial value

        Returns:
            The reduced value

        Example:
            >>> PersistentSet.of(1, 2, 3).reduce(lambda x, y: x + y, 0)
            6
        """
        result = initial
        for item in self._data:
            result = f(result, item)
        return result

    def fold_left(self, f: Callable[[U, T], U], initial: U) -> U:
        """Left-associative fold (alias for reduce).

        Args:
            f: Function to combine values
            initial: Initial value

        Returns:
            The folded value

        Example:
            >>> PersistentSet.of(1, 2, 3).fold_left(lambda x, y: x - y, 0)
            -6
        """
        return self.reduce(f, initial)

    def to_set(self) -> set[T]:
        """Convert to a Python set.

        Returns:
            A Python set with the same elements

        Example:
            >>> PersistentSet.of(1, 2, 3).to_set()
            {1, 2, 3}
        """
        return set(self._data)

    @override
    def __repr__(self) -> str:
        if not self._data:
            return "PersistentSet()"
        return f"PersistentSet({self._data})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PersistentSet):
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        return hash(frozenset(self._data))

    def __iter__(self) -> Iterator[T]:
        """Iterate over elements."""
        return iter(self._data)

    def __len__(self) -> int:
        """Get the size."""
        return len(self._data)

    def __contains__(self, item: T) -> bool:
        """Check if item is in set."""
        return item in self._data


__all__ = ["PersistentSet"]
