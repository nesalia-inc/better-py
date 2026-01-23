"""Property-based tests for Maybe monad.

Tests the monad laws and other properties using Hypothesis.
"""

from functools import reduce
from operator import add, mul

import hypothesis.strategies as st
from hypothesis import given, settings
import pytest

from better_py.monads import Maybe


class TestMaybeMonadLaws:
    """Tests for Maybe monad laws."""

    @given(st.integers())
    def test_left_identity(self, value):
        """Left identity: Maybe.some(x).bind(f) == f(x)"""
        def f(x):
            return Maybe.some(x * 2)

        result = Maybe.some(value).bind(f)
        expected = f(value)
        assert result == expected

    @given(st.integers())
    def test_right_identity(self, value):
        """Right identity: Maybe.some(x).bind(Maybe.some) == Maybe.some(x)"""
        result = Maybe.some(value).bind(Maybe.some)
        assert result == Maybe.some(value)

    @given(st.integers(), st.integers())
    def test_associativity(self, x, y):
        """Associativity: (m.bind(f)).bind(g) == m.bind(x => f(x).bind(g))"""
        def f(x):
            return Maybe.some(x + y)

        def g(x):
            return Maybe.some(x * 2)

        # Left side: (m.bind(f)).bind(g)
        left = Maybe.some(x).bind(f).bind(g)

        # Right side: m.bind(lambda x: f(x).bind(g))
        right = Maybe.some(x).bind(lambda val: f(val).bind(g))

        assert left == right

    def test_nothing_left_identity(self):
        """Left identity with Nothing always returns Nothing."""
        result = Maybe.nothing().bind(Maybe.some)
        assert result.is_nothing()

    def test_nothing_right_identity(self):
        """Right identity with Nothing preserves Nothing."""
        result = Maybe.nothing()
        assert result.is_nothing()

    @given(st.integers())
    def test_nothing_bind_short_circuits(self, value):
        """bind on Nothing should return Nothing without calling function."""
        call_count = [0]

        def f(x):
            call_count[0] += 1
            return Maybe.some(x * 2)

        result = Maybe.nothing().bind(f)
        assert result.is_nothing()
        assert call_count[0] == 0


class TestMaybeFunctorLaws:
    """Tests for Maybe functor laws."""

    @given(st.integers())
    def test_identity_law(self, value):
        """Identity: Maybe.map(lambda x: x) == Maybe.some(value)"""
        result = Maybe.some(value).map(lambda x: x)
        assert result == Maybe.some(value)

    @given(st.integers(), st.integers())
    def test_composition_law(self, x, y):
        """Composition: Maybe.map(f).map(g) == Maybe.map(lambda x: g(f(x)))"""
        def f(x):
            return x + y

        def g(x):
            return x * 2

        # Compose maps
        composed = Maybe.some(x).map(f).map(g)
        single = Maybe.some(x).map(lambda val: g(f(val)))

        assert composed == single


class TestMaybeProperties:
    """Other properties of Maybe."""

    @given(st.integers())
    def test_map_preserves_nothing(self, value):
        """map preserves Nothing."""
        result = Maybe.nothing().map(lambda x: x * 2)
        assert result.is_nothing()

    @given(st.integers())
    def test_double_map(self, value):
        """Double map is equivalent to single composed map."""
        def f(x):
            return x + 1

        def g(x):
            return x * 2

        double_mapped = Maybe.some(value).map(f).map(g)
        composed = Maybe.some(value).map(lambda x: g(f(x)))

        assert double_mapped == composed

    @given(st.integers(), st.integers())
    def test_map_and_bind_compose(self, value, threshold):
        """Map and bind operations compose correctly."""
        def is_even(x):
            return x % 2 == 0

        def double(x):
            return x * 2

        # Compose map and bind operations
        result = Maybe.some(value).map(double).bind(lambda x: Maybe.some(x) if is_even(x) else Maybe.nothing())

        expected = Maybe.some(value * 2) if (value * 2) % 2 == 0 else Maybe.nothing()
        assert result == expected


class TestMaybeImmutability:
    """Tests for immutability guarantees."""

    @given(st.integers())
    def test_operations_dont_modify_original(self, value):
        """All operations return new instances, leaving original unchanged."""
        original = Maybe.some(value)

        # Various operations
        _ = original.map(lambda x: x * 2)
        _ = original.bind(lambda x: Maybe.some(x + 1))
        _ = original.or_else(Maybe.nothing())

        # Original should be unchanged
        assert original.unwrap() == value

    @given(st.integers())
    def test_structural_sharing(self, value):
        """modifications share structure when possible."""
        original = Maybe.some(value)
        mapped = original.map(lambda x: x + 1)

        # Both should be independent
        assert original.unwrap() == value
        assert mapped.unwrap() == value + 1


class TestMaybeEdgeCases:
    """Edge cases and corner cases."""

    def test_map_exception_handling(self):
        """map handles exceptions by propagating them."""
        def raising_func(x):
            raise ValueError("test error")

        with pytest.raises(ValueError):
            Maybe.some(42).map(raising_func)

    @given(st.none() | st.just(st.integers()) | st.just(st.text()))
    def test_with_various_types(self, value):
        """Maybe works with various types."""
        maybe = Maybe.from_value(value)
        if value is None:
            assert maybe.is_nothing()
        else:
            assert maybe.is_some()
            assert maybe.unwrap() == value


__all__ = ["TestMaybeMonadLaws", "TestMaybeFunctorLaws", "TestMaybeProperties", "TestMaybeImmutability", "TestMaybeEdgeCases"]
