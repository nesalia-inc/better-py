"""Persistent list for functional programming.

A PersistentList is an immutable list with structural sharing,
providing O(1) prepend and O(n) index access.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable, Reducible

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class Node(Generic[T]):
    """A node in the persistent list."""
    head: T
    tail: Node[T] | None


@dataclass(frozen=True, slots=True)
class PersistentList(Mappable[T], Reducible[T], Generic[T]):
    """Immutable list with structural sharing.

    A PersistentList is a linked list that never mutates.
    Operations that would "modify" the list instead return new lists
    while sharing structure with the original.

    Type Parameters:
        T: The element type

    Example:
        >>> lst = PersistentList.of(1, 2, 3)
        >>> new_lst = lst.prepend(0)
        >>> lst  # Still (1, 2, 3)
        >>> new_lst  # (0, 1, 2, 3)
    """

    _node: Node[T] | None = None
    _length: int = 0

    @staticmethod
    def empty() -> PersistentList[T]:
        """Create an empty list.

        Returns:
            An empty PersistentList

        Example:
            >>> PersistentList.empty()
            PersistentList()
        """
        return PersistentList()

    @staticmethod
    def of(*items: T) -> PersistentList[T]:
        """Create a list from items.

        Args:
            *items: Items to add to the list

        Returns:
            A new PersistentList containing the items

        Example:
            >>> PersistentList.of(1, 2, 3)
            PersistentList(1, 2, 3)
        """
        result: PersistentList[T] = PersistentList()
        for item in reversed(items):
            result = result.prepend(item)
        return result

    @staticmethod
    def from_iterable(items: Iterable[T]) -> PersistentList[T]:
        """Create a list from an iterable.

        Args:
            items: Iterable of items

        Returns:
            A new PersistentList containing the items

        Example:
            >>> PersistentList.from_iterable([1, 2, 3])
            PersistentList(1, 2, 3)
        """
        result: PersistentList[T] = PersistentList()
        lst = list(items)
        for item in reversed(lst):
            result = result.prepend(item)
        return result

    def is_empty(self) -> bool:
        """Check if the list is empty.

        Returns:
            True if empty, False otherwise

        Example:
            >>> PersistentList.empty().is_empty()  # True
            >>> PersistentList.of(1).is_empty()  # False
        """
        return self._node is None

    def length(self) -> int:
        """Get the length of the list.

        Returns:
            The number of elements

        Example:
            >>> PersistentList.of(1, 2, 3).length()  # 3
        """
        return self._length

    def prepend(self, item: T) -> PersistentList[T]:
        """Add an item to the front of the list.

        Args:
            item: Item to prepend

        Returns:
            A new list with the item at the front

        Example:
            >>> lst = PersistentList.of(2, 3)
            >>> lst.prepend(1)  # PersistentList(1, 2, 3)
        """
        return PersistentList(Node(item, self._node), self._length + 1)

    def append(self, item: T) -> PersistentList[T]:
        """Add an item to the end of the list.

        Args:
            item: Item to append

        Returns:
            A new list with the item at the end

        Example:
            >>> lst = PersistentList.of(1, 2)
            >>> lst.append(3)  # PersistentList(1, 2, 3)
        """
        if self._node is None:
            return PersistentList(Node(item, None), 1)

        # Build new list in reverse then reverse back
        items = list(self)
        items.append(item)
        return PersistentList.from_iterable(items)

    def head(self) -> T | None:
        """Get the first element.

        Returns:
            The first element, or None if empty

        Example:
            >>> PersistentList.of(1, 2, 3).head()  # 1
            >>> PersistentList.empty().head()  # None
        """
        if self._node is None:
            return None
        return self._node.head

    def tail(self) -> PersistentList[T]:
        """Get all elements except the first.

        Returns:
            A new list without the first element

        Example:
            >>> PersistentList.of(1, 2, 3).tail()  # PersistentList(2, 3)
            >>> PersistentList.empty().tail()  # PersistentList()
        """
        if self._node is None:
            return PersistentList()
        return PersistentList(self._node.tail, self._length - 1)

    def get(self, index: int) -> T | None:
        """Get element at index.

        Args:
            index: The index to get

        Returns:
            The element at index, or None if out of bounds

        Example:
            >>> PersistentList.of(1, 2, 3).get(1)  # 2
            >>> PersistentList.of(1, 2, 3).get(10)  # None
        """
        if index < 0 or index >= self._length:
            return None

        current = self._node
        for _ in range(index):
            if current is None:
                return None
            current = current.tail

        return current.head if current else None

    def map(self, f) -> PersistentList[U]:
        """Apply a function to each element.

        Args:
            f: Function to apply

        Returns:
            A new list with f applied to each element

        Example:
            >>> PersistentList.of(1, 2, 3).map(lambda x: x * 2)
            PersistentList(2, 4, 6)
        """
        result: PersistentList[U] = PersistentList()
        for item in reversed(list(self)):
            result = result.prepend(f(item))
        return result

    def filter(self, predicate) -> PersistentList[T]:
        """Filter elements by a predicate.

        Args:
            predicate: Function to test each element

        Returns:
            A new list with elements that pass the predicate

        Example:
            >>> PersistentList.of(1, 2, 3, 4).filter(lambda x: x % 2 == 0)
            PersistentList(2, 4)
        """
        result: PersistentList[T] = PersistentList()
        for item in self:
            if predicate(item):
                result = result.append(item)
        return result

    def reduce(self, f, initial):
        """Reduce the list to a single value.

        Args:
            f: Function to combine values
            initial: Initial value

        Returns:
            The reduced value

        Example:
            >>> PersistentList.of(1, 2, 3).reduce(lambda x, y: x + y, 0)
            6
        """
        result = initial
        for item in self:
            result = f(result, item)
        return result

    def reverse(self) -> PersistentList[T]:
        """Reverse the list.

        Returns:
            A new list with elements in reverse order

        Example:
            >>> PersistentList.of(1, 2, 3).reverse()
            PersistentList(3, 2, 1)
        """
        result: PersistentList[T] = PersistentList()
        for item in self:
            result = result.prepend(item)
        return result

    def take(self, n: int) -> PersistentList[T]:
        """Take the first n elements.

        Args:
            n: Number of elements to take

        Returns:
            A new list with the first n elements

        Example:
            >>> PersistentList.of(1, 2, 3, 4, 5).take(3)
            PersistentList(1, 2, 3)
        """
        if n <= 0:
            return PersistentList()

        result: PersistentList[T] = PersistentList()
        current = self._node
        count = 0

        while current is not None and count < n:
            result = result.prepend(current.head)
            current = current.tail
            count += 1

        return result.reverse()

    def drop(self, n: int) -> PersistentList[T]:
        """Drop the first n elements.

        Args:
            n: Number of elements to drop

        Returns:
            A new list without the first n elements

        Example:
            >>> PersistentList.of(1, 2, 3, 4, 5).drop(2)
            PersistentList(3, 4, 5)
        """
        if n <= 0:
            return self

        current = self._node
        for _ in range(n):
            if current is None:
                return PersistentList()
            current = current.tail

        # Build new list from current node
        result: PersistentList[T] = PersistentList()
        items = []
        while current is not None:
            items.append(current.head)
            current = current.tail

        for item in reversed(items):
            result = result.prepend(item)

        return result

    def to_list(self) -> list[T]:
        """Convert to a Python list.

        Returns:
            A Python list with the same elements

        Example:
            >>> PersistentList.of(1, 2, 3).to_list()
            [1, 2, 3]
        """
        return list(self)

    @override
    def __iter__(self) -> Iterator[T]:
        """Iterate over elements."""
        current = self._node
        while current is not None:
            yield current.head
            current = current.tail

    @override
    def __len__(self) -> int:
        """Get the length."""
        return self._length

    @override
    def __repr__(self) -> str:
        if self._length == 0:
            return "PersistentList()"
        items = ", ".join(repr(item) for item in self)
        return f"PersistentList({items})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PersistentList):
            return False
        return list(self) == list(other)

    def __hash__(self) -> int:
        return hash(tuple(self))


__all__ = ["PersistentList"]
