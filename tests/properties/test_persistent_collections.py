"""Property-based tests for persistent collections.

Tests immutability, structural sharing, and correctness using Hypothesis.
"""

import hypothesis.strategies as st
from hypothesis import given, settings

from better_py.collections import PersistentList, PersistentMap, PersistentSet


class TestPersistentListImmutability:
    """Tests for PersistentList immutability guarantees."""

    @given(st.lists(st.integers()))
    def test_append_creates_new_list(self, values):
        """append always creates a new list."""
        original = PersistentList.from_iterable(values)
        modified = original.append(999)

        # Original should be unchanged
        assert original.to_list() == values
        assert modified.to_list() == values + [999]

    @given(st.lists(st.integers()))
    def test_prepend_creates_new_list(self, values):
        """prepend always creates a new list."""
        original = PersistentList.from_iterable(values)
        modified = original.prepend(999)

        # Original should be unchanged
        assert original.to_list() == values
        assert modified.to_list() == [999] + values

    @given(st.lists(st.integers()))
    def test_map_creates_new_list(self, values):
        """map always creates a new list."""
        original = PersistentList.from_iterable(values)

        def double(x):
            return x * 2

        modified = original.map(double)

        # Original should be unchanged
        assert original.to_list() == values
        assert modified.to_list() == [v * 2 for v in values]

    @given(st.lists(st.integers()), st.integers(min_value=0, max_value=10))
    def test_take_creates_new_list(self, values, n):
        """take always creates a new list."""
        original = PersistentList.from_iterable(values)
        modified = original.take(n)

        # Original should be unchanged
        assert original.length() == len(values)
        assert modified.to_list() == values[:n]

    @given(st.lists(st.integers()))
    def test_drop_creates_new_list(self, values):
        """drop always creates a new list."""
        original = PersistentList.from_iterable(values)
        modified = original.drop(2)

        # Original should be unchanged
        assert original.to_list() == values
        assert modified.to_list() == values[2:]

    @given(st.lists(st.integers()))
    def test_reverse_creates_new_list(self, values):
        """reverse always creates a new list."""
        original = PersistentList.from_iterable(values)
        modified = original.reverse()

        # Original should be unchanged
        assert original.to_list() == values
        assert modified.to_list() == list(reversed(values))


class TestPersistentListProperties:
    """Functional properties of PersistentList."""

    @given(st.lists(st.integers()))
    def test_length_matches_list(self, values):
        """length() matches len(to_list())."""
        lst = PersistentList.from_iterable(values)
        assert lst.length() == len(values)

    @given(st.lists(st.integers()))
    def test_head_returns_first_element(self, values):
        """head() returns first element or None."""
        lst = PersistentList.from_iterable(values)
        if values:
            assert lst.head() == values[0]
        else:
            assert lst.head() is None

    @given(st.lists(st.integers()))
    def test_tail_returns_rest(self, values):
        """tail() returns all elements except first."""
        lst = PersistentList.from_iterable(values)
        if values:
            assert lst.tail().to_list() == values[1:]
        else:
            assert lst.tail().is_empty()

    @given(st.lists(st.integers()))
    def test_get_returns_correct_element(self, values):
        """get(index) returns element at that index."""
        lst = PersistentList.from_iterable(values)
        for i, val in enumerate(values):
            assert lst.get(i) == val
        assert lst.get(len(values)) is None
        assert lst.get(-1) is None

    @given(st.lists(st.integers()), st.integers())
    def test_filter_removes_matching_elements(self, values, threshold):
        """filter removes elements that don't match predicate."""
        lst = PersistentList.from_iterable(values)

        def is_greater_than(x):
            return x > threshold

        result = lst.filter(is_greater_than)
        expected = [v for v in values if v > threshold]
        assert result.to_list() == expected

    @given(st.lists(st.integers()), st.integers())
    def test_take_n_returns_first_n(self, values, n):
        """take(n) returns first n elements."""
        lst = PersistentList.from_iterable(values)
        result = lst.take(n)
        assert result.to_list() == values[:n]

    @given(st.lists(st.integers()), st.integers(min_value=0))
    def test_drop_n_returns_rest(self, values, n):
        """drop(n) returns elements after first n."""
        lst = PersistentList.from_iterable(values)
        result = lst.drop(n)
        assert result.to_list() == values[n:]

    @given(st.lists(st.integers()))
    def test_reverse_reverses_elements(self, values):
        """reverse reverses the order of elements."""
        lst = PersistentList.from_iterable(values)
        result = lst.reverse()
        assert result.to_list() == list(reversed(values))

    @given(st.lists(st.integers(), min_size=2, max_size=5), st.integers(), st.integers())
    def test_append_twice(self, values, val1, val2):
        """Appending twice creates expected result."""
        lst = PersistentList.from_iterable(values)
        result = lst.append(val1).append(val2)
        expected = values + [val1, val2]
        assert result.to_list() == expected

    @given(st.lists(st.integers()))
    def test_prepend_append_order(self, values):
        """Prepend then append should maintain order."""
        lst = PersistentList.from_iterable(values)
        result = lst.prepend(-1).append(999)
        expected = [-1] + values + [999]
        assert result.to_list() == expected


class TestPersistentMapImmutability:
    """Tests for PersistentMap immutability."""

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_set_creates_new_map(self, d):
        """set always creates a new map."""
        original = PersistentMap.of(d)
        modified = original.set("new_key", 999)

        # Original should be unchanged
        assert original.to_dict() == d
        assert modified.size() == len(d) + 1

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_delete_creates_new_map(self, d):
        """delete always creates a new map."""
        if d:
            key = next(iter(d.keys()))
            original = PersistentMap.of(d)
            modified = original.delete(key)

            # Original should be unchanged
            assert original.to_dict() == d
            assert key not in modified.to_dict()

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_merge_creates_new_map(self, d):
        """merge always creates a new map."""
        original = PersistentMap.of(d)
        additional = {"extra": 999}
        modified = original.merge(PersistentMap.of(additional))

        # Original should be unchanged
        assert original.to_dict() == d
        assert modified.size() == len(d) + 1


class TestPersistentMapProperties:
    """Functional properties of PersistentMap."""

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_size_matches_dict(self, d):
        """size() matches len(to_dict())."""
        m = PersistentMap.of(d)
        assert m.size() == len(d)

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_get_returns_correct_value(self, d):
        """get(key) returns value for that key."""
        m = PersistentMap.of(d)
        for key, value in d.items():
            assert m.get(key) == value
        assert m.get("nonexistent") is None

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_get_or_else_default(self, d):
        """get_or_else returns value or default."""
        m = PersistentMap.of(d)
        assert m.get_or_else("nonexistent", 999) == 999
        if d:
            key = next(iter(d.keys()))
            assert m.get_or_else(key, 999) == d[key]

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_map_values_transforms_all_values(self, d):
        """map_values transforms all values."""
        m = PersistentMap.of(d)

        def double(x):
            return x * 2

        result = m.map_values(double)
        for key, value in d.items():
            assert result.get(key) == value * 2

    @given(st.dictionaries(st.integers(), st.integers()))
    def test_contains_key_checks_existence(self, d):
        """contains_key returns True for existing keys."""
        m = PersistentMap.of(d)
        for key in d:
            assert m.contains_key(key)
        assert not m.contains_key("nonexistent")


class TestPersistentSetImmutability:
    """Tests for PersistentSet immutability."""

    @given(st.sets(st.integers()))
    def test_add_creates_new_set(self, s):
        """add always creates a new set."""
        original = PersistentSet.from_iterable(s)
        modified = original.add(999)

        # Original should be unchanged
        assert original.to_set() == s
        assert 999 in modified.to_set()

    @given(st.sets(st.integers()))
    def test_remove_creates_new_set(self, s):
        """remove always creates a new set."""
        if s:
            elem = next(iter(s))
            original = PersistentSet.from_iterable(s)
            modified = original.remove(elem)

            # Original should be unchanged
            assert original.to_set() == s
            assert elem not in modified.to_set()

    @given(st.sets(st.integers()))
    def test_union_creates_new_set(self, s):
        """union always creates a new set."""
        original = PersistentSet.from_iterable(s)
        other = PersistentSet.from_iterable({999})
        result = original.union(other)

        # Original should be unchanged
        assert original.to_set() == s
        assert 999 in result.to_set()

    @given(st.sets(st.integers()))
    def test_intersection_creates_new_set(self, s):
        """intersection always creates a new set."""
        if s:
            original = PersistentSet.from_iterable(s)
            other = PersistentSet.from_iterable(s)
            result = original.intersection(other)

            # Original should be unchanged
            assert original.to_set() == s
            assert result.to_set() == s


class TestPersistentSetProperties:
    """Functional properties of PersistentSet."""

    @given(st.sets(st.integers()))
    def test_size_matches_set(self, s):
        """size() matches len(to_set())."""
        pset = PersistentSet.from_iterable(s)
        assert pset.size() == len(s)

    @given(st.sets(st.integers()))
    def test_contains_checks_membership(self, s):
        """contains returns True for members."""
        pset = PersistentSet.from_iterable(s)
        for item in s:
            assert pset.contains(item)
        assert not pset.contains(999)

    @given(st.sets(st.integers()))
    def test_add_deduplicates(self, s):
        """add handles duplicates correctly."""
        pset = PersistentSet.from_iterable(s)
        result = pset.add(999).add(999)
        assert result.size() == pset.size() + 1
        assert result.to_set() == s | {999}

    @given(st.sets(st.integers()), st.sets(st.integers()))
    def test_union_combines_sets(self, s1, s2):
        """union combines both sets."""
        pset1 = PersistentSet.from_iterable(s1)
        pset2 = PersistentSet.from_iterable(s2)
        result = pset1.union(pset2)
        assert result.to_set() == s1 | s2

    @given(st.sets(st.integers()), st.sets(st.integers()))
    def test_intersection_finds_common(self, s1, s2):
        """intersection finds common elements."""
        pset1 = PersistentSet.from_iterable(s1)
        pset2 = PersistentSet.from_iterable(s2)
        result = pset1.intersection(pset2)
        assert result.to_set() == s1 & s2

    @given(st.sets(st.integers()), st.sets(st.integers()))
    def test_difference_finds_unique(self, s1, s2):
        """difference finds elements in s1 but not s2."""
        pset1 = PersistentSet.from_iterable(s1)
        pset2 = PersistentSet.from_iterable(s2)
        result = pset1.difference(pset2)
        assert result.to_set() == s1 - s2


__all__ = [
    "TestPersistentListImmutability",
    "TestPersistentListProperties",
    "TestPersistentMapImmutability",
    "TestPersistentMapProperties",
    "TestPersistentSetImmutability",
    "TestPersistentSetProperties",
]
