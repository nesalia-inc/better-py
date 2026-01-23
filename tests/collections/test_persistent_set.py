"""Tests for PersistentSet."""

import pytest

from better_py.collections import PersistentSet


class TestPersistentSet:
    """Tests for PersistentSet."""

    def test_empty_creation(self):
        """empty should create an empty set."""
        s = PersistentSet.empty()
        assert s.is_empty()
        assert s.size() == 0

    def test_of_creation(self):
        """of should create a set from items."""
        s = PersistentSet.of(1, 2, 3)
        assert not s.is_empty()
        assert s.size() == 3

    def test_from_iterable(self):
        """from_iterable should create a set from iterable."""
        s = PersistentSet.from_iterable([1, 2, 3])
        assert s.size() == 3
        assert s.contains(1)

    def test_from_iterable_with_duplicates(self):
        """from_iterable should deduplicate."""
        s = PersistentSet.from_iterable([1, 2, 2, 3])
        assert s.size() == 3

    def test_contains(self):
        """contains should check membership."""
        s = PersistentSet.of(1, 2, 3)
        assert s.contains(2)
        assert not s.contains(4)

    def test_add(self):
        """add should add an element."""
        s = PersistentSet.of(1, 2)
        s2 = s.add(3)
        assert not s.contains(3)
        assert s2.contains(3)

    def test_add_duplicate(self):
        """add should handle duplicates gracefully."""
        s = PersistentSet.of(1, 2)
        s2 = s.add(2)
        assert s.size() == 2
        assert s2.size() == 2

    def test_remove(self):
        """remove should remove an element."""
        s = PersistentSet.of(1, 2, 3)
        s2 = s.remove(2)
        assert s.contains(2)
        assert not s2.contains(2)
        assert s2.size() == 2

    def test_remove_missing(self):
        """remove should handle missing element gracefully."""
        s = PersistentSet.of(1, 2)
        s2 = s.remove(3)
        assert s2.size() == 2

    def test_union(self):
        """union should combine sets."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(2, 3)
        result = s1.union(s2)
        assert result.to_set() == {1, 2, 3}

    def test_intersection(self):
        """intersection should find common elements."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(2, 3)
        result = s1.intersection(s2)
        assert result.to_set() == {2}

    def test_difference(self):
        """difference should find elements in self but not other."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(2, 3)
        result = s1.difference(s2)
        assert result.to_set() == {1}

    def test_is_subset_true(self):
        """is_subset should return True when all elements are in other."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(1, 2, 3)
        assert s1.is_subset(s2)

    def test_is_subset_false(self):
        """is_subset should return False when not all elements are in other."""
        s1 = PersistentSet.of(1, 2, 4)
        s2 = PersistentSet.of(1, 2, 3)
        assert not s1.is_subset(s2)

    def test_is_superset_true(self):
        """is_superset should return True when contains all elements."""
        s1 = PersistentSet.of(1, 2, 3)
        s2 = PersistentSet.of(1, 2)
        assert s1.is_superset(s2)

    def test_is_superset_false(self):
        """is_superset should return False when doesn't contain all."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(1, 2, 3)
        assert not s1.is_superset(s2)

    def test_map(self):
        """map should transform elements."""
        s = PersistentSet.of(1, 2, 3)
        result = s.map(lambda x: x * 2)
        assert result.to_set() == {2, 4, 6}

    def test_filter(self):
        """filter should keep elements passing predicate."""
        s = PersistentSet.of(1, 2, 3, 4)
        result = s.filter(lambda x: x % 2 == 0)
        assert result.to_set() == {2, 4}

    def test_reduce(self):
        """reduce should combine elements."""
        s = PersistentSet.of(1, 2, 3)
        result = s.reduce(lambda x, y: x + y, 0)
        assert result == 6

    def test_reduce_empty(self):
        """reduce on empty should return initial."""
        s = PersistentSet.empty()
        result = s.reduce(lambda x, y: x + y, 10)
        assert result == 10

    def test_to_set(self):
        """to_set should convert to Python set."""
        s = PersistentSet.of(1, 2, 3)
        result = s.to_set()
        assert result == {1, 2, 3}
        assert isinstance(result, set)

    def test_iteration(self):
        """should be iterable."""
        s = PersistentSet.of(1, 2, 3)
        result = {x * 2 for x in s}
        assert result == {2, 4, 6}

    def test_len(self):
        """len should return size."""
        s = PersistentSet.of(1, 2, 3)
        assert len(s) == 3

    def test_contains_operator(self):
        """should support 'in' operator."""
        s = PersistentSet.of(1, 2, 3)
        assert 2 in s
        assert 4 not in s

    def test_repr_empty(self):
        """repr of empty should show PersistentSet()."""
        s = PersistentSet.empty()
        assert repr(s) == "PersistentSet()"

    def test_repr_with_items(self):
        """repr should show items."""
        s = PersistentSet.of(1, 2, 3)
        assert "PersistentSet" in repr(s)

    def test_equality(self):
        """sets with same elements should be equal."""
        s1 = PersistentSet.of(1, 2, 3)
        s2 = PersistentSet.of(1, 2, 3)
        assert s1 == s2

    def test_inequality(self):
        """sets with different elements should not be equal."""
        s1 = PersistentSet.of(1, 2)
        s2 = PersistentSet.of(1, 2, 3)
        assert s1 != s2

    def test_equality_different_types(self):
        """set should not equal non-set."""
        s = PersistentSet.of(1, 2, 3)
        assert s != {1, 2, 3}

    def test_hash(self):
        """sets should be hashable."""
        s1 = PersistentSet.of(1, 2, 3)
        s2 = PersistentSet.of(1, 2, 3)
        assert hash(s1) == hash(s2)

    def test_immutability(self):
        """original set should be unchanged by operations."""
        s = PersistentSet.of(1, 2)
        s2 = s.add(3).remove(1)
        assert s.to_set() == {1, 2}
        assert s2.to_set() == {2, 3}
