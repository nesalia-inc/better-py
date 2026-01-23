"""Tests for Unit monad."""

from better_py.monads import Unit


class TestUnit:
    """Tests for Unit monad."""

    def test_unit_creation(self):
        """unit should create an empty Unit."""
        unit = Unit.unit()
        assert unit.value is None

    def test_unit_of(self):
        """of should create a Unit with a value."""
        unit = Unit.of(42)
        assert unit.value == 42

    def test_unit_repr(self):
        """Unit should have correct repr."""
        assert repr(Unit.unit()) == "Unit()"
        assert repr(Unit.of(42)) == "Unit(42)"

    def test_unit_map(self):
        """map should transform the value."""
        result = Unit.of(5).map(lambda x: x * 2)
        assert result.value == 10

    def test_unit_map_empty(self):
        """map on empty Unit should preserve emptiness."""
        result = Unit.unit().map(lambda x: x * 2)
        assert result.value is None

    def test_unit_equality(self):
        """Units should be equal if values match."""
        unit1 = Unit.of(42)
        unit2 = Unit.of(42)
        assert unit1 == unit2

    def test_unit_inequality(self):
        """Units with different values should not be equal."""
        unit1 = Unit.of(42)
        unit2 = Unit.of(43)
        assert unit1 != unit2
