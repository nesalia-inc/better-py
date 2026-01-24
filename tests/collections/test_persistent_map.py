"""Tests for PersistentMap."""

import pytest

from better_py.collections import PersistentMap


class TestPersistentMap:
    """Tests for PersistentMap."""

    def test_empty_creation(self):
        """empty should create an empty map."""
        m = PersistentMap.empty()
        assert m.is_empty()
        assert m.size() == 0

    def test_of_creation(self):
        """of should create a map from dict."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert not m.is_empty()
        assert m.size() == 2

    def test_from_iterable(self):
        """from_iterable should create a map from pairs."""
        m = PersistentMap.from_iterable([("a", 1), ("b", 2)])
        assert m.size() == 2
        assert m.get("a") == 1

    def test_get(self):
        """get should return value for key."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert m.get("a") == 1
        assert m.get("b") == 2

    def test_get_missing_key(self):
        """get should return None for missing key."""
        m = PersistentMap.of({"a": 1})
        assert m.get("b") is None

    def test_get_or_else(self):
        """get_or_else should return value or default."""
        m = PersistentMap.of({"a": 1})
        assert m.get_or_else("a", 0) == 1
        assert m.get_or_else("b", 0) == 0

    def test_contains_key(self):
        """contains_key should check for key existence."""
        m = PersistentMap.of({"a": 1})
        assert m.contains_key("a")
        assert not m.contains_key("b")

    def test_set(self):
        """set should add or update a key."""
        m = PersistentMap.of({"a": 1})
        m2 = m.set("b", 2)
        assert m.get("b") is None
        assert m2.get("b") == 2

    def test_set_update(self):
        """set should update existing key."""
        m = PersistentMap.of({"a": 1})
        m2 = m.set("a", 2)
        assert m.get("a") == 1
        assert m2.get("a") == 2

    def test_delete(self):
        """delete should remove a key."""
        m = PersistentMap.of({"a": 1, "b": 2})
        m2 = m.delete("a")
        assert m.contains_key("a")
        assert not m2.contains_key("a")
        assert m2.get("b") == 2

    def test_delete_missing_key(self):
        """delete should handle missing key gracefully."""
        m = PersistentMap.of({"a": 1})
        m2 = m.delete("b")
        assert m2.size() == 1

    def test_keys(self):
        """keys should return all keys."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert set(m.keys()) == {"a", "b"}

    def test_values(self):
        """values should return all values."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert set(m.values()) == {1, 2}

    def test_items(self):
        """items should return all pairs."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert set(m.items()) == {("a", 1), ("b", 2)}

    def test_map(self):
        """map should transform values."""
        m = PersistentMap.of({"a": 1, "b": 2})
        result = m.map(lambda k, v: v * 2)
        assert result.get("a") == 2
        assert result.get("b") == 4

    def test_map_values(self):
        """map_values should transform values only."""
        m = PersistentMap.of({"a": 1, "b": 2})
        result = m.map_values(lambda v: v * 2)
        assert result.get("a") == 2
        assert result.get("b") == 4

    def test_map_keys(self):
        """map_keys should transform keys only."""
        m = PersistentMap.of({1: "a", 2: "b"})
        result = m.map_keys(lambda k: k * 2)
        assert result.get(2) == "a"
        assert result.get(4) == "b"

    def test_merge(self):
        """merge should combine two maps."""
        m1 = PersistentMap.of({"a": 1})
        m2 = PersistentMap.of({"b": 2})
        result = m1.merge(m2)
        assert result.size() == 2
        assert result.get("a") == 1
        assert result.get("b") == 2

    def test_merge_overlap(self):
        """merge should favor other map in overlaps."""
        m1 = PersistentMap.of({"a": 1})
        m2 = PersistentMap.of({"a": 2})
        result = m1.merge(m2)
        assert result.get("a") == 2

    def test_to_dict(self):
        """to_dict should convert to Python dict."""
        m = PersistentMap.of({"a": 1, "b": 2})
        result = m.to_dict()
        assert result == {"a": 1, "b": 2}
        assert isinstance(result, dict)

    def test_iteration(self):
        """should iterate over keys."""
        m = PersistentMap.of({"a": 1, "b": 2})
        keys = list(m)
        assert set(keys) == {"a", "b"}

    def test_len(self):
        """len should return size."""
        m = PersistentMap.of({"a": 1, "b": 2})
        assert len(m) == 2

    def test_repr_empty(self):
        """repr of empty should show empty dict."""
        m = PersistentMap.empty()
        assert "PersistentMap" in repr(m)

    def test_repr_with_items(self):
        """repr should show items."""
        m = PersistentMap.of({"a": 1})
        assert "PersistentMap" in repr(m)
        assert "'a'" in repr(m)

    def test_equality(self):
        """maps with same entries should be equal."""
        m1 = PersistentMap.of({"a": 1, "b": 2})
        m2 = PersistentMap.of({"a": 1, "b": 2})
        assert m1 == m2

    def test_inequality(self):
        """maps with different entries should not be equal."""
        m1 = PersistentMap.of({"a": 1})
        m2 = PersistentMap.of({"a": 2})
        assert m1 != m2

    def test_equality_different_types(self):
        """map should not equal non-map."""
        m = PersistentMap.of({"a": 1})
        assert m != {"a": 1}

    def test_hash(self):
        """maps should be hashable."""
        m1 = PersistentMap.of({"a": 1, "b": 2})
        m2 = PersistentMap.of({"a": 1, "b": 2})
        assert hash(m1) == hash(m2)

    def test_immutability(self):
        """original map should be unchanged by operations."""
        m = PersistentMap.of({"a": 1})
        m2 = m.set("b", 2).delete("a")
        assert m.to_dict() == {"a": 1}
        assert m2.to_dict() == {"b": 2}

    def test_map_keys_collision_loses_data(self):
        """map_keys should lose data on key collisions (last wins)."""
        m = PersistentMap.of({1: "a", 2: "b", 3: "c"})
        result = m.map_keys(lambda k: k // 2)
        # Iteration order: 1, 2, 3
        # 1 // 2 = 0 -> 'a'
        # 2 // 2 = 1 -> 'b' (gets overwritten)
        # 3 // 2 = 1 -> 'c'
        assert result.size() == 2
        assert result.get(0) == "a"
        assert result.get(1) == "c"  # Last value wins

    def test_map_keys_no_collision(self):
        """map_keys should work correctly when no collisions occur."""
        m = PersistentMap.of({1: "a", 2: "b"})
        result = m.map_keys(lambda k: k * 2)
        assert result.size() == 2
        assert result.get(2) == "a"
        assert result.get(4) == "b"

    def test_map_keys_collect_with_collisions(self):
        """map_keys_collect should collect values on key collisions."""
        m = PersistentMap.of({1: "a", 2: "b", 3: "c"})
        result = m.map_keys_collect(lambda k: k // 2)
        # Iteration order: 1, 2, 3
        # 1 // 2 = 0 -> ['a']
        # 2 // 2 = 1 -> ['b']
        # 3 // 2 = 1 -> ['b', 'c']
        assert result.size() == 2
        assert result.get(0) == ["a"]
        assert result.get(1) == ["b", "c"]

    def test_map_keys_collect_no_collisions(self):
        """map_keys_collect should wrap single values in lists."""
        m = PersistentMap.of({1: "a", 2: "b"})
        result = m.map_keys_collect(lambda k: k * 2)
        assert result.size() == 2
        assert result.get(2) == ["a"]
        assert result.get(4) == ["b"]

    def test_map_keys_collect_empty(self):
        """map_keys_collect should handle empty map."""
        m = PersistentMap.empty()
        result = m.map_keys_collect(lambda k: k * 2)
        assert result.is_empty()
