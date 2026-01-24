"""Persistent map for functional programming.

A PersistentMap is an immutable dictionary with structural sharing.
"""

from __future__ import annotations

from collections.abc import Callable, ItemsView, Iterable, Iterator, KeysView, ValuesView
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing_extensions import override

from better_py.protocols import Mappable1

K = TypeVar("K")
V = TypeVar("V")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class PersistentMap(Mappable1[tuple[K, V]], Generic[K, V]):
    """Immutable map with structural sharing.

    A PersistentMap is an immutable dictionary that never mutates.
    Operations that would "modify" the map instead return new maps
    while sharing structure with the original.

    Type Parameters:
        K: The key type
        V: The value type

    Example:
        >>> m = PersistentMap.of({"a": 1, "b": 2})
        >>> new_m = m.set("c", 3)
        >>> m  # Still {"a": 1, "b": 2}
        >>> new_m  # {"a": 1, "b": 2, "c": 3}
    """

    _data: dict[K, V]

    def __init__(self, data: dict[K, V] | None = None) -> None:
        """Initialize the map.

        Args:
            data: Optional dictionary to initialize with
        """
        object.__setattr__(self, "_data", dict(data) if data else {})

    @staticmethod
    def empty() -> PersistentMap[K, V]:
        """Create an empty map.

        Returns:
            An empty PersistentMap

        Example:
            >>> PersistentMap.empty()
            PersistentMap()
        """
        return PersistentMap()

    @staticmethod
    def of(data: dict[K, V]) -> PersistentMap[K, V]:
        """Create a map from a dictionary.

        Args:
            data: Dictionary to create from

        Returns:
            A new PersistentMap with the key-value pairs

        Example:
            >>> PersistentMap.of({"a": 1, "b": 2})
            PersistentMap({'a': 1, 'b': 2})
        """
        return PersistentMap(dict(data))

    @staticmethod
    def from_iterable(items: Iterable[tuple[K, V]]) -> PersistentMap[K, V]:
        """Create a map from an iterable of key-value pairs.

        Args:
            items: Iterable of (key, value) tuples

        Returns:
            A new PersistentMap containing the pairs

        Example:
            >>> PersistentMap.from_iterable([("a", 1), ("b", 2)])
            PersistentMap({'a': 1, 'b': 2})
        """
        return PersistentMap(dict(items))

    def is_empty(self) -> bool:
        """Check if the map is empty.

        Returns:
            True if empty, False otherwise

        Example:
            >>> PersistentMap.empty().is_empty()  # True
            >>> PersistentMap.of({"a": 1}).is_empty()  # False
        """
        return len(self._data) == 0

    def size(self) -> int:
        """Get the number of entries.

        Returns:
            The number of key-value pairs

        Example:
            >>> PersistentMap.of({"a": 1, "b": 2}).size()  # 2
        """
        return len(self._data)

    def get(self, key: K) -> V | None:
        """Get a value by key.

        Args:
            key: The key to look up

        Returns:
            The value, or None if key not found

        Example:
            >>> PersistentMap.of({"a": 1}).get("a")  # 1
            >>> PersistentMap.of({"a": 1}).get("b")  # None
        """
        return self._data.get(key)

    def get_or_else(self, key: K, default: V) -> V:
        """Get a value or return a default.

        Args:
            key: The key to look up
            default: The default value

        Returns:
            The value, or default if key not found

        Example:
            >>> PersistentMap.of({"a": 1}).get_or_else("b", 0)  # 0
        """
        return self._data.get(key, default)

    def contains_key(self, key: K) -> bool:
        """Check if a key exists.

        Args:
            key: The key to check

        Returns:
            True if key exists, False otherwise

        Example:
            >>> PersistentMap.of({"a": 1}).contains_key("a")  # True
            >>> PersistentMap.of({"a": 1}).contains_key("b")  # False
        """
        return key in self._data

    def set(self, key: K, value: V) -> PersistentMap[K, V]:
        """Set a key-value pair.

        Args:
            key: The key
            value: The value

        Returns:
            A new map with the key-value pair

        Example:
            >>> m = PersistentMap.of({"a": 1})
            >>> m.set("b", 2)  # PersistentMap({'a': 1, 'b': 2})
        """
        new_data = dict(self._data)
        new_data[key] = value
        return PersistentMap(new_data)

    def delete(self, key: K) -> PersistentMap[K, V]:
        """Remove a key.

        Args:
            key: The key to remove

        Returns:
            A new map without the key

        Example:
            >>> m = PersistentMap.of({"a": 1, "b": 2})
            >>> m.delete("a")  # PersistentMap({'b': 2})
        """
        new_data = dict(self._data)
        new_data.pop(key, None)
        return PersistentMap(new_data)

    def keys(self) -> KeysView[K]:
        """Get the keys.

        Returns:
            A view of all keys

        Example:
            >>> list(PersistentMap.of({"a": 1, "b": 2}).keys())
            ['a', 'b']
        """
        return self._data.keys()

    def values(self) -> ValuesView[V]:
        """Get the values.

        Returns:
            A view of all values

        Example:
            >>> list(PersistentMap.of({"a": 1, "b": 2}).values())
            [1, 2]
        """
        return self._data.values()

    def items(self) -> ItemsView[K, V]:
        """Get the key-value pairs.

        Returns:
            A view of all key-value pairs

        Example:
            >>> list(PersistentMap.of({"a": 1, "b": 2}).items())
            [('a', 1), ('b', 2)]
        """
        return self._data.items()

    def map(self, f: Callable[[K, V], U]) -> PersistentMap[K, U]:
        """Apply a function to all values.

        Args:
            f: Function taking (key, value) and returning new value

        Returns:
            A new map with transformed values

        Example:
            >>> PersistentMap.of({"a": 1}).map(lambda k, v: v * 2)
            PersistentMap({'a': 2})
        """
        new_data = {k: f(k, v) for k, v in self._data.items()}
        return PersistentMap(new_data)

    def map_values(self, f: Callable[[V], U]) -> PersistentMap[K, U]:
        """Apply a function to all values (keys unchanged).

        Args:
            f: Function taking value and returning new value

        Returns:
            A new map with transformed values

        Example:
            >>> PersistentMap.of({"a": 1}).map_values(lambda v: v * 2)
            PersistentMap({'a': 2})
        """
        new_data = {k: f(v) for k, v in self._data.items()}
        return PersistentMap(new_data)

    def map_keys(self, f: Callable[[K], U]) -> PersistentMap[U, V]:
        """Apply a function to all keys (values unchanged).

        Args:
            f: Function taking key and returning new key

        Returns:
            A new map with transformed keys

        Example:
            >>> PersistentMap.of({1: "a"}).map_keys(lambda k: k * 2)
            PersistentMap({2: 'a'})
        """
        new_data = {f(k): v for k, v in self._data.items()}
        return PersistentMap(new_data)

    def merge(self, other: PersistentMap[K, V]) -> PersistentMap[K, V]:
        """Merge two maps.

        Args:
            other: Another map to merge with

        Returns:
            A new map with combined entries (other takes precedence)

        Example:
            >>> m1 = PersistentMap.of({"a": 1})
            >>> m2 = PersistentMap.of({"b": 2})
            >>> m1.merge(m2)  # PersistentMap({'a': 1, 'b': 2})
        """
        new_data = dict(self._data)
        new_data.update(other._data)
        return PersistentMap(new_data)

    def to_dict(self) -> dict[K, V]:
        """Convert to a Python dict.

        Returns:
            A Python dict with the same entries

        Example:
            >>> PersistentMap.of({"a": 1}).to_dict()
            {'a': 1}
        """
        return dict(self._data)

    @override
    def __repr__(self) -> str:
        return f"PersistentMap({self._data!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PersistentMap):
            return False
        return self._data == other._data

    def __hash__(self) -> int:
        return hash(tuple(sorted(self._data.items())))

    def __iter__(self) -> Iterator[K]:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Get the size."""
        return len(self._data)


__all__ = ["PersistentMap"]
