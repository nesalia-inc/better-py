"""Tests for Traversable protocol."""

import copy

from better_py.monads import Maybe
from better_py.protocols import Traversable


class TraversableList(Traversable):
    """Simple list implementing Traversable."""

    def __init__(self, items: list):
        self._items = list(items)

    def traverse(self, f):
        """Transform each item with an effectful function."""
        # Start with Maybe.some([])
        result = Maybe.some([])

        for item in self._items:
            # Apply f to get Maybe[value]
            item_maybe = f(item)

            # If any item returns Nothing, the whole traversal fails
            if item_maybe.is_nothing():
                return Maybe.nothing()

            # Otherwise, append to the accumulator
            value = item_maybe.unwrap()
            current_list = result.unwrap()
            result = Maybe.some(current_list + [value])

        return result

    def sequence(self):
        """Extract Maybes from a list of Maybes."""
        return self.traverse(lambda x: x)

    def __eq__(self, other):
        return isinstance(other, TraversableList) and self._items == other._items

    def __repr__(self):
        return f"TraversableList({self._items})"


class TestTraversable:
    """Tests for Traversable protocol."""

    def test_traversable_list_is_traversable(self):
        """TraversableList should satisfy Traversable protocol."""
        data: Traversable = TraversableList([])
        assert isinstance(data, Traversable)

    def test_traverse_with_all_success(self):
        """traverse should apply function to all elements."""
        data = TraversableList([1, 2, 3])
        result = data.traverse(lambda x: Maybe.some(x * 2))
        assert result.is_some()
        assert result.unwrap() == [2, 4, 6]

    def test_traverse_preserves_structure(self):
        """traverse should preserve the structure."""
        data = TraversableList([1, 2, 3])
        result = data.traverse(lambda x: Maybe.some(str(x)))
        assert result.unwrap() == ["1", "2", "3"]

    def test_traverse_empty_list(self):
        """traverse on empty list should return empty Maybe."""
        data = TraversableList([])
        result = data.traverse(lambda x: Maybe.some(x * 2))
        assert result.is_some()
        assert result.unwrap() == []

    def test_traverse_with_filtering(self):
        """traverse can be used for filtering."""
        data = TraversableList([1, 2, 3, 4, 5])
        # Only keep even numbers
        result = data.traverse(lambda x: Maybe.some(x) if x % 2 == 0 else Maybe.nothing())
        assert result.is_nothing()

    def test_traverse_with_none_values(self):
        """traverse should handle None values."""
        data = TraversableList([1, None, 3])
        result = data.traverse(lambda x: Maybe.some(x) if x is not None else Maybe.nothing())
        assert result.is_nothing()

    def test_traverse_type_change(self):
        """traverse can change the contained type."""
        data = TraversableList([1, 2, 3])
        result = data.traverse(lambda x: Maybe.some(f"num_{x}"))
        assert result.unwrap() == ["num_1", "num_2", "num_3"]

    def test_traverse_single_element(self):
        """traverse should work with single element."""
        data = TraversableList([42])
        result = data.traverse(lambda x: Maybe.some(x * 2))
        assert result.unwrap() == [84]

    def test_sequence_list_of_maybes(self):
        """sequence should extract Maybes from a list."""
        data = TraversableList([Maybe.some(1), Maybe.some(2), Maybe.some(3)])
        result = data.sequence()
        assert result.is_some()
        assert result.unwrap() == [1, 2, 3]

    def test_sequence_with_nothing(self):
        """sequence should fail if any element is Nothing."""
        data = TraversableList([Maybe.some(1), Maybe.nothing(), Maybe.some(3)])
        result = data.sequence()
        assert result.is_nothing()

    def test_sequence_empty_list(self):
        """sequence on empty list should return empty."""
        data = TraversableList([])
        result = data.sequence()
        assert result.is_some()
        assert result.unwrap() == []

    def test_sequence_single_maybe(self):
        """sequence should work with single Maybe."""
        data = TraversableList([Maybe.some(42)])
        result = data.sequence()
        assert result.unwrap() == [42]

    def test_sequence_all_nothing(self):
        """sequence with all Nothing should return Nothing."""
        data = TraversableList([Maybe.nothing(), Maybe.nothing()])
        result = data.sequence()
        assert result.is_nothing()

    def test_traverse_identity(self):
        """traverse with identity should preserve values."""
        data = TraversableList([1, 2, 3])
        result = data.traverse(lambda x: Maybe.some(x))
        assert result.unwrap() == [1, 2, 3]

    def test_traverse_composition(self):
        """Multiple traverse operations should compose."""
        data = TraversableList([1, 2, 3])
        # First traverse: double the values
        result1 = data.traverse(lambda x: Maybe.some(x * 2))
        # Second traverse: convert to string
        result2 = TraversableList(result1.unwrap()).traverse(lambda x: Maybe.some(str(x)))
        assert result2.unwrap() == ["2", "4", "6"]

    def test_traverse_immutability(self):
        """traverse should not modify the original."""
        data = TraversableList([1, 2, 3])
        original_items = copy.deepcopy(data._items)
        data.traverse(lambda x: Maybe.some(x * 2))
        assert data._items == original_items
