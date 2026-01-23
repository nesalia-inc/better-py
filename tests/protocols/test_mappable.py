"""Tests for Mappable protocol."""

from collections.abc import Callable

from better_py.protocols import T, U
from better_py.protocols.mappable import Mappable, Mappable1


class SimpleBox:
    """Simple container implementing Mappable."""

    def __init__(self, value):
        self.value = value

    def map(self, f: Callable[[T], U]) -> "SimpleBox":
        """Apply function to contained value."""
        return SimpleBox(f(self.value))

    def __eq__(self, other):
        return isinstance(other, SimpleBox) and self.value == other.value

    def __repr__(self):
        return f"SimpleBox({self.value!r})"


class TestMappableProtocol:
    """Tests for Mappable protocol."""

    def test_simple_box_is_mappable(self):
        """SimpleBox should satisfy Mappable protocol."""
        box: Mappable[int] = SimpleBox(5)
        assert isinstance(box, Mappable)

    def test_map_with_function(self):
        """map should apply function to contained value."""
        box = SimpleBox(5)
        result = box.map(lambda x: x * 2)
        assert result.value == 10

    def test_map_returns_new_instance(self):
        """map should return a new instance."""
        box = SimpleBox(5)
        result = box.map(lambda x: x)
        assert result is not box
        assert result.value == box.value

    def test_map_chain(self):
        """Multiple map operations should chain."""
        box = SimpleBox(5)
        result = box.map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: x / 2)
        assert result.value == 5.5

    def test_map_with_string(self):
        """map should work with string values."""
        box = SimpleBox("hello")
        result = box.map(str.upper)
        assert result.value == "HELLO"

    def test_map_with_list(self):
        """map should work with list values."""
        box = SimpleBox([1, 2, 3])
        result = box.map(len)
        assert result.value == 3

    def test_map_preserves_none(self):
        """map should preserve None values."""
        box = SimpleBox(None)
        result = box.map(lambda x: "not none" if x is not None else "none")
        assert result.value == "none"

    def test_map_with_complex_function(self):
        """map should work with complex transformations."""

        def transform(x: int) -> str:
            return f"Number: {x * 2}"

        box = SimpleBox(21)
        result = box.map(transform)
        assert result.value == "Number: 42"

    def test_map_identity_law(self):
        """map identity: map(id) == id."""
        box = SimpleBox(42)
        result = box.map(lambda x: x)
        assert result.value == box.value

    def test_map_composition_law(self):
        """map composition: map(f ∘ g) == map(g) ∘ map(f)."""

        def f(x: int) -> int:
            return x * 2

        def g(x: int) -> int:
            return x + 10

        box = SimpleBox(5)

        # map(f ∘ g)
        composed = box.map(lambda x: f(g(x)))

        # map(g) ∘ map(f)
        chained = box.map(g).map(f)

        assert composed.value == chained.value


class TestMappable1Protocol:
    """Tests for Mappable1 protocol (simpler version)."""

    def test_simple_box_is_mappable1(self):
        """SimpleBox should satisfy Mappable1 protocol."""
        box: Mappable1 = SimpleBox(5)
        assert isinstance(box, Mappable1)

    def test_mappable1_allows_untyped_map(self):
        """Mappable1 should allow untyped map implementations."""

        class UntypedBox:
            def map(self, f):
                return UntypedBox(f(self.value))

            def __init__(self, value):
                self.value = value

        box: Mappable1 = UntypedBox(5)
        result = box.map(lambda x: x * 2)
        assert result.value == 10
