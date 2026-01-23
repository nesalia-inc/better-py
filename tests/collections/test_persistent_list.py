"""Tests for PersistentList."""

import pytest

from better_py.collections import PersistentList


class TestPersistentList:
    """Tests for PersistentList."""

    def test_empty_creation(self):
        """empty should create an empty list."""
        lst = PersistentList.empty()
        assert lst.is_empty()
        assert lst.length() == 0

    def test_of_creation(self):
        """of should create a list with items."""
        lst = PersistentList.of(1, 2, 3)
        assert not lst.is_empty()
        assert lst.length() == 3

    def test_from_iterable(self):
        """from_iterable should create a list from iterable."""
        lst = PersistentList.from_iterable([1, 2, 3])
        assert lst.length() == 3
        assert list(lst) == [1, 2, 3]

    def test_from_iterable_empty(self):
        """from_iterable with empty iterable should create empty list."""
        lst = PersistentList.from_iterable([])
        assert lst.is_empty()

    def test_prepend(self):
        """prepend should add item to front."""
        lst = PersistentList.of(2, 3)
        new_lst = lst.prepend(1)
        assert new_lst.to_list() == [1, 2, 3]
        assert lst.to_list() == [2, 3]  # Original unchanged

    def test_append(self):
        """append should add item to end."""
        lst = PersistentList.of(1, 2)
        new_lst = lst.append(3)
        assert new_lst.to_list() == [1, 2, 3]
        assert lst.to_list() == [1, 2]  # Original unchanged

    def test_append_empty(self):
        """append to empty should create single element list."""
        lst = PersistentList.empty()
        new_lst = lst.append(1)
        assert new_lst.to_list() == [1]

    def test_head(self):
        """head should return first element."""
        lst = PersistentList.of(1, 2, 3)
        assert lst.head() == 1

    def test_head_empty(self):
        """head of empty should return None."""
        lst = PersistentList.empty()
        assert lst.head() is None

    def test_tail(self):
        """tail should return rest of list."""
        lst = PersistentList.of(1, 2, 3)
        assert lst.tail().to_list() == [2, 3]

    def test_tail_empty(self):
        """tail of empty should return empty list."""
        lst = PersistentList.empty()
        assert lst.tail().is_empty()

    def test_tail_single(self):
        """tail of single element should return empty."""
        lst = PersistentList.of(1)
        assert lst.tail().is_empty()

    def test_get(self):
        """get should return element at index."""
        lst = PersistentList.of(1, 2, 3)
        assert lst.get(0) == 1
        assert lst.get(1) == 2
        assert lst.get(2) == 3

    def test_get_out_of_bounds(self):
        """get with out of bounds index should return None."""
        lst = PersistentList.of(1, 2, 3)
        assert lst.get(10) is None
        assert lst.get(-1) is None

    def test_get_empty(self):
        """get on empty list should return None."""
        lst = PersistentList.empty()
        assert lst.get(0) is None

    def test_map(self):
        """map should transform elements."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.map(lambda x: x * 2)
        assert result.to_list() == [2, 4, 6]
        assert lst.to_list() == [1, 2, 3]  # Original unchanged

    def test_map_empty(self):
        """map on empty should return empty."""
        lst = PersistentList.empty()
        result = lst.map(lambda x: x * 2)
        assert result.is_empty()

    def test_filter(self):
        """filter should keep elements passing predicate."""
        lst = PersistentList.of(1, 2, 3, 4, 5)
        result = lst.filter(lambda x: x % 2 == 0)
        assert result.to_list() == [2, 4]

    def test_filter_empty(self):
        """filter on empty should return empty."""
        lst = PersistentList.empty()
        result = lst.filter(lambda x: x % 2 == 0)
        assert result.is_empty()

    def test_filter_none_match(self):
        """filter with no matches should return empty."""
        lst = PersistentList.of(1, 3, 5)
        result = lst.filter(lambda x: x % 2 == 0)
        assert result.is_empty()

    def test_reduce(self):
        """reduce should combine elements."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.reduce(lambda x, y: x + y, 0)
        assert result == 6

    def test_reduce_empty(self):
        """reduce on empty should return initial."""
        lst = PersistentList.empty()
        result = lst.reduce(lambda x, y: x + y, 10)
        assert result == 10

    def test_reverse(self):
        """reverse should reverse the list."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.reverse()
        assert result.to_list() == [3, 2, 1]

    def test_reverse_empty(self):
        """reverse of empty should return empty."""
        lst = PersistentList.empty()
        result = lst.reverse()
        assert result.is_empty()

    def test_take(self):
        """take should return first n elements."""
        lst = PersistentList.of(1, 2, 3, 4, 5)
        result = lst.take(3)
        assert result.to_list() == [1, 2, 3]

    def test_take_zero(self):
        """take(0) should return empty list."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.take(0)
        assert result.is_empty()

    def test_take_more_than_length(self):
        """take with n > length should return full list."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.take(10)
        assert result.to_list() == [1, 2, 3]

    def test_drop(self):
        """drop should skip first n elements."""
        lst = PersistentList.of(1, 2, 3, 4, 5)
        result = lst.drop(2)
        assert result.to_list() == [3, 4, 5]

    def test_drop_zero(self):
        """drop(0) should return full list."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.drop(0)
        assert result.to_list() == [1, 2, 3]

    def test_drop_all(self):
        """drop all elements should return empty."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.drop(3)
        assert result.is_empty()

    def test_drop_more_than_length(self):
        """drop with n > length should return empty."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.drop(10)
        assert result.is_empty()

    def test_to_list(self):
        """to_list should convert to Python list."""
        lst = PersistentList.of(1, 2, 3)
        result = lst.to_list()
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_iteration(self):
        """should be iterable."""
        lst = PersistentList.of(1, 2, 3)
        result = [x * 2 for x in lst]
        assert result == [2, 4, 6]

    def test_len(self):
        """len should return length."""
        lst = PersistentList.of(1, 2, 3)
        assert len(lst) == 3

    def test_len_empty(self):
        """len of empty should return 0."""
        lst = PersistentList.empty()
        assert len(lst) == 0

    def test_repr_empty(self):
        """repr of empty should show PersistentList()."""
        lst = PersistentList.empty()
        assert repr(lst) == "PersistentList()"

    def test_repr_with_items(self):
        """repr should show items."""
        lst = PersistentList.of(1, 2, 3)
        assert repr(lst) == "PersistentList(1, 2, 3)"

    def test_equality(self):
        """lists with same elements should be equal."""
        lst1 = PersistentList.of(1, 2, 3)
        lst2 = PersistentList.of(1, 2, 3)
        assert lst1 == lst2

    def test_inequality(self):
        """lists with different elements should not be equal."""
        lst1 = PersistentList.of(1, 2, 3)
        lst2 = PersistentList.of(1, 2, 4)
        assert lst1 != lst2

    def test_equality_different_types(self):
        """list should not equal non-list."""
        lst = PersistentList.of(1, 2, 3)
        assert lst != [1, 2, 3]

    def test_hash(self):
        """lists should be hashable."""
        lst1 = PersistentList.of(1, 2, 3)
        lst2 = PersistentList.of(1, 2, 3)
        assert hash(lst1) == hash(lst2)

    def test_structural_sharing(self):
        """modifications should preserve original structure."""
        lst1 = PersistentList.of(2, 3)
        lst2 = lst1.prepend(1)
        lst3 = lst2.prepend(0)

        assert lst1.to_list() == [2, 3]
        assert lst2.to_list() == [1, 2, 3]
        assert lst3.to_list() == [0, 1, 2, 3]

        # Original lists should be unchanged
        assert lst1.to_list() == [2, 3]
        assert lst2.to_list() == [1, 2, 3]

    def test_chaining(self):
        """should support method chaining."""
        result = (
            PersistentList.of(1, 2, 3, 4, 5)
            .map(lambda x: x * 2)
            .filter(lambda x: x > 4)
            .take(3)
        )
        assert result.to_list() == [6, 8, 10]
