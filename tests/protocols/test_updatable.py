"""Tests for Updatable protocol."""

import copy

from better_py.protocols import DeepUpdatable, Updatable


class ImmutableDict(Updatable):
    """Simple immutable dict implementing Updatable."""

    def __init__(self, data: dict):
        self._data = dict(data)

    def set(self, key: str | int, value: object) -> "ImmutableDict":
        """Set a field to a new value."""
        new_data = {**self._data, key: value}
        return ImmutableDict(new_data)

    def update(self, **changes: object) -> "ImmutableDict":
        """Update multiple fields at once."""
        new_data = {**self._data, **changes}
        return ImmutableDict(new_data)

    def delete(self, key: str | int) -> "ImmutableDict":
        """Delete a field."""
        new_data = {k: v for k, v in self._data.items() if k != key}
        return ImmutableDict(new_data)

    def merge(self, other: dict) -> "ImmutableDict":
        """Merge another dict into this one."""
        new_data = {**self._data, **other}
        return ImmutableDict(new_data)

    def get(self, key: str | int | None = None, default=None):
        if key is None:
            return self._data
        return self._data.get(key, default)

    def __eq__(self, other):
        return isinstance(other, ImmutableDict) and self._data == other._data

    def __repr__(self):
        return f"ImmutableDict({self._data})"


class DeepImmutableDict(DeepUpdatable):
    """Deeply nested immutable dict implementing DeepUpdatable."""

    def __init__(self, data):
        self._data = data

    def set_in(self, path: list[str | int], value: object) -> "DeepImmutableDict":
        """Set a nested field using a path."""
        new_data = copy.deepcopy(self._data)
        current = new_data

        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[path[-1]] = value
        return DeepImmutableDict(new_data)

    def update_in(self, path: list[str | int], **changes: object) -> "DeepImmutableDict":
        """Update multiple fields at a nested level."""
        new_data = copy.deepcopy(self._data)
        current = new_data

        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        if path[-1] not in current:
            current[path[-1]] = {}
        elif not isinstance(current[path[-1]], dict):
            # If it's not a dict, replace it
            current[path[-1]] = {}

        current[path[-1]].update(changes)
        return DeepImmutableDict(new_data)

    def delete_in(self, path: list[str | int], key: str | int) -> "DeepImmutableDict":
        """Delete a field at a nested level.

        The path specifies the parent dict, and key is the field to delete from that parent.
        For example, delete_in(["user", "cache"], "temp") deletes the "temp" key from the cache dict.

        Note: Empty parent dicts are NOT automatically cleaned up.
        """
        new_data = copy.deepcopy(self._data)
        current = new_data

        # Navigate to the parent dict
        for p in path:
            if p in current and isinstance(current[p], dict):
                current = current[p]
            else:
                # Path doesn't exist, return unchanged
                return DeepImmutableDict(new_data)

        # Delete the key from the parent dict
        if key in current:
            del current[key]

        return DeepImmutableDict(new_data)

    def get(self):
        return self._data

    def __eq__(self, other):
        return isinstance(other, DeepImmutableDict) and self._data == other._data

    def __repr__(self):
        return f"DeepImmutableDict({self._data})"


class TestUpdatable:
    """Tests for Updatable protocol."""

    def test_immutable_dict_is_updatable(self):
        """ImmutableDict should satisfy Updatable protocol."""
        data: Updatable = ImmutableDict({})
        assert isinstance(data, Updatable)

    def test_set_single_field(self):
        """set should update a single field."""
        data = ImmutableDict({"name": "Alice"})
        updated = data.set("age", 30)
        assert updated.get("name") == "Alice"
        assert updated.get("age") == 30
        assert data.get("age") is None  # Original unchanged

    def test_set_multiple_fields(self):
        """Multiple set operations should chain."""
        data = ImmutableDict({})
        result = data.set("name", "Bob").set("age", 25).set("city", "NYC")
        assert result.get("name") == "Bob"
        assert result.get("age") == 25
        assert result.get("city") == "NYC"

    def test_update_multiple_fields(self):
        """update should change multiple fields at once."""
        data = ImmutableDict({"name": "Alice", "age": 30, "city": "London"})
        updated = data.update(age=31, city="Paris")
        assert updated.get("age") == 31
        assert updated.get("city") == "Paris"
        assert updated.get("name") == "Alice"  # Unchanged

    def test_delete_field(self):
        """delete should remove a field."""
        data = ImmutableDict({"name": "Alice", "age": 30})
        updated = data.delete("age")
        assert "age" not in updated.get()
        assert updated.get("name") == "Alice"

    def delete_missing_field(self):
        """delete should handle missing fields gracefully."""
        data = ImmutableDict({"name": "Alice"})
        updated = data.delete("missing")
        assert updated.get("name") == "Alice"

    def merge_dicts(self):
        """merge should combine two dicts."""
        data = ImmutableDict({"a": 1, "b": 2})
        result = data.merge({"b": 3, "c": 4})
        assert result.get("a") == 1
        assert result.get("b") == 3  # Overwritten
        assert result.get("c") == 4

    def merge_empty_dict(self):
        """merge with empty dict should return unchanged data."""
        data = ImmutableDict({"a": 1, "b": 2})
        result = data.merge({})
        assert result == data

    def set_preserves_immutability(self):
        """set should return a new instance."""
        data = ImmutableDict({"value": 1})
        updated = data.set("value", 2)
        assert data is not updated
        assert data.get("value") == 1
        assert updated.get("value") == 2

    def update_preserves_immutability(self):
        """update should return a new instance."""
        data = ImmutableDict({"value": 1})
        updated = data.update(value=2)
        assert data is not updated
        assert data.get("value") == 1
        assert updated.get("value") == 2


class TestDeepUpdatable:
    """Tests for DeepUpdatable protocol."""

    def test_deep_immutable_dict_is_deep_updatable(self):
        """DeepImmutableDict should satisfy DeepUpdatable protocol."""
        data: DeepUpdatable = DeepImmutableDict({})
        assert isinstance(data, DeepUpdatable)

    def test_set_in_nested_field(self):
        """set_in should update nested field."""
        data = DeepImmutableDict({"user": {"name": "Alice"}})
        updated = data.set_in(["user", "age"], 30)
        assert updated.get()["user"]["age"] == 30
        assert updated.get()["user"]["name"] == "Alice"

    def test_set_in_create_path(self):
        """set_in should create path if it doesn't exist."""
        data = DeepImmutableDict({})
        updated = data.set_in(["user", "preferences", "theme"], "dark")
        assert updated.get()["user"]["preferences"]["theme"] == "dark"

    def test_set_in_update_nested_dict(self):
        """set_in should update value in nested dict."""
        data = DeepImmutableDict({"config": {"db": {"host": "localhost"}}})
        updated = data.set_in(["config", "db", "port"], 5432)
        assert updated.get()["config"]["db"]["port"] == 5432

    def test_update_in_multiple_fields(self):
        """update_in should update multiple nested fields."""
        data = DeepImmutableDict({"user": {}})
        updated = data.update_in(["user"], name="Bob", age=25, city="NYC")
        assert updated.get()["user"]["name"] == "Bob"
        assert updated.get()["user"]["age"] == 25
        assert updated.get()["user"]["city"] == "NYC"

    def test_update_in_create_level(self):
        """update_in should create level if it doesn't exist."""
        data = DeepImmutableDict({})
        updated = data.update_in(["app", "config"], debug=True, verbose=False)
        assert updated.get()["app"]["config"]["debug"] is True
        assert updated.get()["app"]["config"]["verbose"] is False

    def test_delete_in_nested_field(self):
        """delete_in should remove nested field."""
        data = DeepImmutableDict({"user": {"cache": {"temp": "data"}}})
        updated = data.delete_in(["user", "cache"], "temp")
        assert "temp" not in updated.get()["user"]["cache"]
        assert updated.get()["user"]["cache"] == {}

    def test_delete_in_auto_cleanup(self):
        """delete_in does NOT auto-clean up empty dicts."""
        data = DeepImmutableDict({"user": {"cache": {"temp": "data"}}})
        updated = data.delete_in(["user", "cache"], "temp")
        # Empty cache dict remains
        assert "cache" in updated.get()["user"]
        assert updated.get()["user"]["cache"] == {}

    def test_delete_in_missing_key(self):
        """delete_in should handle missing keys gracefully."""
        data = DeepImmutableDict({"user": {"name": "Alice"}})
        updated = data.delete_in(["user", "missing"], "key")
        assert updated.get()["user"]["name"] == "Alice"

    def test_preserves_immutability(self):
        """Deep updates should preserve immutability."""
        data = DeepImmutableDict({"value": {"nested": 1}})
        updated = data.set_in(["value", "nested"], 2)
        assert data is not updated
        assert data.get()["value"]["nested"] == 1
        assert updated.get()["value"]["nested"] == 2

    def test_chained_operations(self):
        """Multiple deep update operations should chain."""
        data = DeepImmutableDict({})
        result = (
            data.set_in(["a"], 1)
            .set_in(["b"], 2)
            .set_in(["c", "d"], 3)
            .update_in(["a"], x=10)
            .delete_in(["c"], "d")
        )
        # update_in replaces scalar value with dict containing changes
        assert result.get()["a"] == {"x": 10}
        assert result.get()["b"] == 2
        # c now has an empty dict (no auto-cleanup)
        assert "c" in result.get()
        assert result.get()["c"] == {}
