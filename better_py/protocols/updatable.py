"""Updatable protocol for immutable updates.

The Updatable protocol defines the ability to update immutable data structures
in a type-safe way, returning new instances with modified values.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from better_py.protocols.types import T, T_co

K = type("K")  # Placeholder for key type


@runtime_checkable
class Updatable(Protocol[T]):
    """Protocol for immutable update operations.

    An Updatable type supports updating nested fields in immutable data
    structures, returning new instances with the modifications applied.

    Type Parameters:
        T: The type being updated

    Example:
        >>> data = {"user": {"name": "Alice", "age": 30}}
        >>> updated = set_in(data, ["user", "age"], 31)  # New instance with updated age
    """

    def set(self, key: str | int, value: object) -> T:
        """Set a field to a new value.

        Args:
            key: The field name or path
            value: The new value

        Returns:
            A new instance with the field updated

        Example:
            >>> result.set("name", "Bob")
        """
        ...

    def update(self, **changes: object) -> T:
        """Update multiple fields at once.

        Args:
            **changes: Field name to new value mappings

        Returns:
            A new instance with all fields updated

        Example:
            >>> result.update(name="Bob", age=25)
        """
        ...

    def delete(self, key: str | int) -> T:
        """Delete a field.

        Args:
            key: The field name to delete

        Returns:
            A new instance with the field removed

        Example:
            >>> result.delete("temporary_field")
        """
        ...

    def merge(self, other: dict[str, object] | T) -> T:
        """Merge another structure into this one.

        Args:
            other: Dictionary or structure to merge

        Returns:
            A new instance with merged data

        Example:
            >>> result.merge({"extra": "value"})
        """
        ...


@runtime_checkable
class DeepUpdatable(Protocol[T_co]):
    """Protocol for deep immutable updates.

    Supports updating nested fields using dot notation paths.
    """

    def set_in(self, path: list[str | int], value: object) -> T:
        """Set a nested field using a path.

        Args:
            path: List of keys/indices to navigate
            value: The value to set

        Returns:
            A new instance with the nested field updated

        Example:
            >>> data.set_in(["user", "preferences", "theme"], "dark")
        """
        ...

    def update_in(self, path: list[str | int], **changes: object) -> T:
        """Update multiple fields at a nested level.

        Args:
            path: List of keys/indices to navigate
            **changes: Field updates to apply

        Returns:
            A new instance with nested fields updated

        Example:
            >>> data.update_in(["user", "preferences"], theme="dark", notifications=True)
        """
        ...

    def delete_in(self, path: list[str | int], key: str | int) -> T:
        """Delete a field at a nested level.

        Args:
            path: List of keys/indices to navigate
            key: The key to delete at that level

        Returns:
            A new instance with the nested field removed

        Example:
            >>> data.delete_in(["user", "cache"], "temporary_data")
        """
        ...


__all__ = ["Updatable", "DeepUpdatable"]
