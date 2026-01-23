"""Property-based tests for Result monad.

Tests the monad laws and other properties using Hypothesis.
"""

import hypothesis.strategies as st
from hypothesis import given

from better_py.monads import Result


class TestResultMonadLaws:
    """Tests for Result monad laws."""

    @given(st.integers())
    def test_left_identity(self, value):
        """Left identity: Result.ok(x).bind(f) == f(x)"""
        def f(x):
            return Result.ok(x * 2)

        result = Result.ok(value).bind(f)
        expected = f(value)
        assert result == expected

    @given(st.integers())
    def test_right_identity(self, value):
        """Right identity: Result.ok(x).bind(Result.ok) == Result.ok(x)"""
        result = Result.ok(value).bind(Result.ok)
        assert result == Result.ok(value)

    @given(st.integers(), st.integers())
    def test_associativity(self, x, y):
        """Associativity: (r.bind(f)).bind(g) == r.bind(x => f(x).bind(g))"""
        def f(x):
            return Result.ok(x + y)

        def g(x):
            return Result.ok(x * 2)

        # Left side: (r.bind(f)).bind(g)
        left = Result.ok(x).bind(f).bind(g)

        # Right side: r.bind(lambda x: f(x).bind(g))
        right = Result.ok(x).bind(lambda val: f(val).bind(g))

        assert left == right

    def test_error_left_identity(self):
        """Left identity with Error short-circuits."""
        result = Result.error("fail").bind(Result.ok)
        assert result.is_error()

    def test_error_bind_short_circuits(self):
        """bind on Error returns Error without calling function."""
        call_count = [0]

        def f(x):
            call_count[0] += 1
            return Result.ok(x * 2)

        result = Result.error("fail").bind(f)
        assert result.is_error()
        assert call_count[0] == 0


class TestResultProperties:
    """Other properties of Result."""

    @given(st.integers())
    def test_map_preserves_error(self, value):
        """map preserves Error."""
        result = Result.error("fail").map(lambda x: x * 2)
        assert result.is_error()

    @given(st.integers())
    def test_map_error_preserves_ok(self, value):
        """map_error preserves Ok."""
        result = Result.ok(value).map_error(lambda e: f"Error: {e}")
        assert result.is_ok()

    @given(st.integers())
    def test_equality(self, value):
        """Result equality works correctly."""
        result1 = Result.ok(value)
        result2 = Result.ok(value)
        assert result1 == result2

        # Ok != Error with same value
        error_result = Result.error(value)
        assert result1 != error_result

    @given(st.integers(), st.integers())
    def test_or_else_provides_default(self, value, default):
        """or_else provides default Result for errors."""
        ok_result = Result.ok(value)
        error_result = Result.error("fail")

        assert ok_result.or_else(Result.ok(default)) == ok_result
        assert error_result.or_else(Result.ok(default)).unwrap() == default


class TestResultImmutability:
    """Tests for immutability guarantees."""

    @given(st.integers())
    def test_operations_dont_modify_original(self, value):
        """All operations return new instances."""
        original = Result.ok(value)

        # Various operations
        _ = original.map(lambda x: x * 2)
        _ = original.map_error(lambda _: "error")
        _ = original.bind(lambda x: Result.ok(x + 1))

        # Original should be unchanged
        assert original.unwrap() == value


class TestResultEdgeCases:
    """Edge cases and corner cases."""

    @given(st.integers(), st.integers())
    def test_map_and_map_error(self, value, multiplier):
        """map and map_error work correctly for both Ok and Error."""
        # Ok case - map applies
        ok_result = Result.ok(value)
        mapped = ok_result.map(lambda x: x * multiplier)
        assert mapped.is_ok()
        assert mapped.unwrap() == value * multiplier

        # Error case - map_error applies
        error_result = Result.error("test error")
        mapped_error = error_result.map_error(lambda e: f"Error: {e}")
        assert mapped_error.is_error()
        assert mapped_error.unwrap_error() == "Error: test error"


__all__ = ["TestResultMonadLaws", "TestResultProperties", "TestResultImmutability", "TestResultEdgeCases"]
