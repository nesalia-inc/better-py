"""Tests for Maybe monad bind/flatMap operations."""

import pytest

from better_py.monads import Maybe


class TestMaybeBind:
    """Tests for bind operation (monadic chain)."""

    def test_bind_some(self):
        """bind should apply function and unwrap result."""

        def double(x):
            return Maybe.some(x * 2)

        result = Maybe.some(5).bind(double)
        assert result.is_some()
        assert result.unwrap() == 10

    def test_bind_nothing(self):
        """bind should return Nothing for Nothing."""

        def double(x):
            return Maybe.some(x * 2)

        result = Maybe.nothing().bind(double)
        assert result.is_nothing()

    def test_bind_preserves_nothing(self):
        """bind should preserve Nothing through chain."""

        def divide(x):
            return Maybe.some(10 / x) if x != 0 else Maybe.nothing()

        result = Maybe.some(0).bind(divide)
        assert result.is_nothing()

    def test_bind_chain(self):
        """Multiple bind operations should chain."""

        def add_one(x):
            return Maybe.some(x + 1)

        def double(x):
            return Maybe.some(x * 2)

        result = Maybe.some(5).bind(add_one).bind(double)
        assert result.unwrap() == 12  # (5 + 1) * 2

    def test_bind_with_failing_operation(self):
        """bind should short-circuit on Nothing."""

        def divide(x):
            return Maybe.some(10 / x) if x != 0 else Maybe.nothing()

        def add_one(x):
            return Maybe.some(x + 1)

        result = Maybe.some(0).bind(divide).bind(add_one)
        assert result.is_nothing()

    def test_bind_type_change(self):
        """bind can change the contained type."""

        def to_string(x):
            return Maybe.some(str(x))

        result = Maybe.some(42).bind(to_string)
        assert result.unwrap() == "42"


class TestMaybeFlatMap:
    """Tests for flat_map operation."""

    def test_flat_map_some(self):
        """flat_map should work like bind."""
        result = Maybe.some(5).flat_map(lambda x: Maybe.some(x * 2))
        assert result.unwrap() == 10

    def test_flat_map_nothing(self):
        """flat_map should return Nothing for Nothing."""
        result = Maybe.nothing().flat_map(lambda x: Maybe.some(x * 2))
        assert result.is_nothing()


class TestMaybeAndThen:
    """Tests for and_then operation."""

    def test_and_then_some(self):
        """and_then should work like bind."""
        result = Maybe.some(5).and_then(lambda x: Maybe.some(x * 2))
        assert result.unwrap() == 10

    def test_and_then_chaining_readable(self):
        """and_then should provide readable chaining."""

        def validate_positive(x):
            return Maybe.some(x) if x > 0 else Maybe.nothing()

        def validate_even(x):
            return Maybe.some(x) if x % 2 == 0 else Maybe.nothing()

        result = Maybe.some(4).and_then(validate_positive).and_then(validate_even)
        assert result.unwrap() == 4

    def test_and_then_short_circuits(self):
        """and_then should short-circuit on failure."""

        def validate_positive(x):
            return Maybe.some(x) if x > 0 else Maybe.nothing()

        def validate_even(x):
            return Maybe.some(x) if x % 2 == 0 else Maybe.nothing()

        result = Maybe.some(-4).and_then(validate_positive).and_then(validate_even)
        assert result.is_nothing()


class TestMaybeOrElse:
    """Tests for or_else operation."""

    def test_or_else_some(self):
        """or_else should return this Maybe if Some."""
        result = Maybe.some(5).or_else(Maybe.some(10))
        assert result.unwrap() == 5

    def test_or_else_nothing(self):
        """or_else should return default if Nothing."""
        result = Maybe.nothing().or_else(Maybe.some(10))
        assert result.unwrap() == 10

    def test_or_else_nothing_with_nothing(self):
        """or_else with Nothing for both should return Nothing."""
        result = Maybe.nothing().or_else(Maybe.nothing())
        assert result.is_nothing()

    def test_or_else_chaining(self):
        """or_else can chain fallbacks."""
        result = (
            Maybe.nothing()
            .or_else(Maybe.nothing())
            .or_else(Maybe.nothing())
            .or_else(Maybe.some(42))
        )
        assert result.unwrap() == 42


class TestMaybeMonadLaws:
    """Tests for monad laws."""

    def test_left_identity(self):
        """Left identity: bind(f) == f(a) for Some(a)."""

        def f(x):
            return Maybe.some(x * 2)

        value = 5
        result1 = Maybe.some(value).bind(f)
        result2 = f(value)
        assert result1 == result2

    def test_right_identity(self):
        """Right identity: bind(Maybe.some) == identity."""
        maybe = Maybe.some(42)
        result = maybe.bind(Maybe.some)
        assert result == maybe

    def test_associativity(self):
        """Associativity: bind(f).bind(g) == bind(lambda x: f(x).bind(g))."""

        def f(x):
            return Maybe.some(x + 1)

        def g(x):
            return Maybe.some(x * 2)

        maybe = Maybe.some(5)

        result1 = maybe.bind(f).bind(g)
        result2 = maybe.bind(lambda x: f(x).bind(g))

        assert result1 == result2

    def test_map_then_bind_vs_bind(self):
        """map(f).bind(g) == bind(lambda x: g(f(x)))."""

        def f(x):
            return x * 2

        def g(x):
            return Maybe.some(x + 1)

        maybe = Maybe.some(5)

        result1 = maybe.map(f).bind(g)
        result2 = maybe.bind(lambda x: g(f(x)))

        assert result1 == result2


class TestMaybePracticalExamples:
    """Practical usage examples."""

    def test_safe_division_chain(self):
        """Chain safe division operations."""

        def safe_divide(a, b):
            return Maybe.some(a / b) if b != 0 else Maybe.nothing()

        def safe_add(a, b):
            return Maybe.some(a + b)

        # (10 / 2) + 3 = 8
        result = Maybe.some(10).bind(lambda x: safe_divide(x, 2)).bind(lambda x: safe_add(x, 3))
        assert result.unwrap() == 8.0

    def test_validation_chain(self):
        """Chain validation operations."""

        def validate_positive(x):
            return Maybe.some(x) if x > 0 else Maybe.nothing()

        def validate_even(x):
            return Maybe.some(x) if x % 2 == 0 else Maybe.nothing()

        def validate_range(x):
            return Maybe.some(x) if x <= 100 else Maybe.nothing()

        result = Maybe.some(4).bind(validate_positive).bind(validate_even).bind(validate_range)
        assert result.unwrap() == 4

    def test_nested_operations(self):
        """Nested operations with bind."""

        def get_user(id):
            if id == 1:
                return Maybe.some({"id": 1, "name": "Alice"})
            return Maybe.nothing()

        def get_email(user):
            if user["name"] == "Alice":
                return Maybe.some("alice@example.com")
            return Maybe.nothing()

        result = Maybe.some(1).bind(get_user).bind(get_email)
        assert result.unwrap() == "alice@example.com"

    def test_flat_map_vs_map(self):
        """flat_map vs map for nested structures."""
        # map returns Maybe[Maybe[int]]
        mapped = Maybe.some(5).map(lambda x: Maybe.some(x * 2))

        # flat_map returns Maybe[int]
        flat_mapped = Maybe.some(5).flat_map(lambda x: Maybe.some(x * 2))

        assert mapped.is_some()
        assert mapped.unwrap().is_some()
        assert flat_mapped.unwrap() == 10
