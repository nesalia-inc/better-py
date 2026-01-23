"""Tests for Reducible protocol."""

from collections.abc import Callable

from better_py.protocols import T, U
from better_py.protocols.reducible import Reducible, Reducible1


class ReducibleList:
    """Simple list implementation of Reducible."""

    def __init__(self, items):
        self.items = items

    def reduce(self, f: Callable[[U, T], U], initial: U) -> U:
        """Reduce items to single value."""
        result = initial
        for item in self.items:
            result = f(result, item)
        return result

    def fold_left(self, f: Callable[[U, T], U], initial: U) -> U:
        """Left-associative fold."""
        result = initial
        for item in self.items:
            result = f(result, item)
        return result

    def __eq__(self, other):
        return isinstance(other, ReducibleList) and self.items == other.items

    def __repr__(self):
        return f"ReducibleList({self.items!r})"


class TestReducibleProtocol:
    """Tests for Reducible protocol."""

    def test_reducible_list_is_reducible(self):
        """ReducibleList should satisfy Reducible protocol."""
        lst: Reducible[int] = ReducibleList([1, 2, 3, 4, 5])
        assert isinstance(lst, Reducible)

    def test_reduce_sum(self):
        """reduce should sum all elements."""
        lst = ReducibleList([1, 2, 3, 4, 5])
        result = lst.reduce(lambda acc, x: acc + x, 0)
        assert result == 15

    def test_reduce_product(self):
        """reduce should multiply all elements."""
        lst = ReducibleList([1, 2, 3, 4])
        result = lst.reduce(lambda acc, x: acc * x, 1)
        assert result == 24

    def test_reduce_with_strings(self):
        """reduce should work with strings."""
        lst = ReducibleList(["hello", " ", "world"])
        result = lst.reduce(lambda acc, x: acc + x, "")
        assert result == "hello world"

    def test_reduce_empty(self):
        """reduce should return initial value for empty collection."""
        lst = ReducibleList([])
        result = lst.reduce(lambda acc, x: acc + x, 42)
        assert result == 42

    def test_fold_left_subtraction(self):
        """fold_left should process left-to-right."""
        lst = ReducibleList([1, 2, 3])
        result = lst.fold_left(lambda acc, x: acc - x, 0)
        # ((0 - 1) - 2) - 3 = -6
        assert result == -6

    def test_fold_left_division(self):
        """fold_left should work with division."""
        lst = ReducibleList([100, 2, 5])
        result = lst.fold_left(lambda acc, x: acc / x, 1000.0)
        # ((1000.0 / 100) / 2) / 5 = 1.0
        assert result == 1.0

    def test_reduce_building_dict(self):
        """reduce should build complex structures."""
        lst = ReducibleList([("a", 1), ("b", 2), ("c", 3)])
        result = lst.reduce(lambda acc, x: {**acc, x[0]: x[1]}, {})
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_reduce_building_list(self):
        """reduce should build lists."""
        lst = ReducibleList([1, 2, 3, 4, 5])
        result = lst.reduce(lambda acc, x: acc + [x * 2], [])
        assert result == [2, 4, 6, 8, 10]

    def test_reduce_with_complex_function(self):
        """reduce should work with complex reduction functions."""

        def reducer(acc, x):
            if x % 2 == 0:
                return acc + [x]
            return acc

        lst = ReducibleList([1, 2, 3, 4, 5, 6])
        result = lst.reduce(reducer, [])
        assert result == [2, 4, 6]

    def test_reduce_find_max(self):
        """reduce should find maximum."""
        lst = ReducibleList([3, 1, 4, 1, 5, 9, 2, 6])
        result = lst.reduce(lambda acc, x: acc if acc > x else x, float("-inf"))
        assert result == 9

    def test_reduce_find_min(self):
        """reduce should find minimum."""
        lst = ReducibleList([3, 1, 4, 1, 5, 9, 2, 6])
        result = lst.reduce(lambda acc, x: acc if acc < x else x, float("inf"))
        assert result == 1

    def test_reduce_preserves_identity(self):
        """reduce with identity function should preserve structure."""
        lst = ReducibleList([1, 2, 3])
        result = lst.reduce(lambda acc, x: acc + [x], [])
        assert result == [1, 2, 3]

    def test_fold_left_matches_reduce(self):
        """fold_left should match reduce for same operation."""
        lst = ReducibleList([1, 2, 3, 4, 5])
        result1 = lst.reduce(lambda acc, x: acc + x, 0)
        result2 = lst.fold_left(lambda acc, x: acc + x, 0)
        assert result1 == result2


class TestReducible1Protocol:
    """Tests for Reducible1 protocol (simpler version)."""

    def test_reducible_list_is_reducible1(self):
        """ReducibleList should satisfy Reducible1 protocol."""
        lst: Reducible1 = ReducibleList([1, 2, 3])
        assert isinstance(lst, Reducible1)

    def test_reducible1_allows_untyped_reduce(self):
        """Reducible1 should allow untyped reduce implementations."""

        class UntypedReducible:
            def reduce(self, f, initial):
                result = initial
                for item in self.items:
                    result = f(result, item)
                return result

            def __init__(self, items):
                self.items = items

        lst: Reducible1 = UntypedReducible([1, 2, 3, 4, 5])
        result = lst.reduce(lambda acc, x: acc + x, 0)
        assert result == 15
