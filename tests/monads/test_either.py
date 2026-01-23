"""Tests for Either monad."""

import pytest

from better_py.monads import Either


class TestEitherConstruction:
    """Tests for Either construction."""

    def test_left_creation(self):
        """left should create a Left variant."""
        result = Either.left("error")
        assert result.is_left()
        assert not result.is_right()

    def test_right_creation(self):
        """right should create a Right variant."""
        result = Either.right(42)
        assert result.is_right()
        assert not result.is_left()

    def test_left_repr(self):
        """Left should have correct repr."""
        result = Either.left("error")
        assert repr(result) == "Left('error')"

    def test_right_repr(self):
        """Right should have correct repr."""
        result = Either.right(42)
        assert repr(result) == "Right(42)"


class TestEitherUnwrap:
    """Tests for unwrapping Either values."""

    def test_unwrap_left_on_left(self):
        """unwrap_left should return Left value."""
        result = Either.left("error")
        assert result.unwrap_left() == "error"

    def test_unwrap_left_on_right(self):
        """unwrap_left on Right should raise."""
        result = Either.right(42)
        try:
            result.unwrap_left()
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "Cannot unwrap_left Right" in str(e)

    def test_unwrap_right_on_right(self):
        """unwrap_right should return Right value."""
        result = Either.right(42)
        assert result.unwrap_right() == 42

    def test_unwrap_right_on_left(self):
        """unwrap_right on Left should raise."""
        result = Either.left("error")
        try:
            result.unwrap_right()
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            assert "Cannot unwrap_right Left" in str(e)


class TestEitherMap:
    """Tests for map operation."""

    def test_map_right(self):
        """map should apply function to Right value."""
        result = Either.right(5).map(lambda x: x * 2)
        assert result.is_right()
        assert result.unwrap_right() == 10

    def test_map_left(self):
        """map should preserve Left."""
        result = Either.left("error").map(lambda x: x * 2)
        assert result.is_left()
        assert result.unwrap_left() == "error"

    def test_map_chain(self):
        """Multiple map operations should chain."""
        result = Either.right(5).map(lambda x: x + 1).map(lambda x: x * 2).map(lambda x: x - 3)
        assert result.unwrap_right() == 9  # ((5 + 1) * 2) - 3


class TestEitherMapLeft:
    """Tests for map_left operation."""

    def test_map_left_on_left(self):
        """map_left should apply function to Left value."""
        result = Either.left("error").map_left(str.upper)
        assert result.is_left()
        assert result.unwrap_left() == "ERROR"

    def test_map_left_on_right(self):
        """map_left should preserve Right."""
        result = Either.right(42).map_left(str.upper)
        assert result.is_right()
        assert result.unwrap_right() == 42

    def test_map_left_chain(self):
        """Multiple map_left operations should chain."""
        result = Either.left("error").map_left(str.upper).map_left(lambda x: x + "!")
        assert result.unwrap_left() == "ERROR!"


class TestEitherFlatMap:
    """Tests for flat_map operation."""

    def test_flat_map_right(self):
        """flat_map should apply function and unwrap."""
        def double(x):
            return Either.right(x * 2)

        result = Either.right(5).flat_map(double)
        assert result.is_right()
        assert result.unwrap_right() == 10

    def test_flat_map_left(self):
        """flat_map should return Left for Left."""
        def double(x):
            return Either.right(x * 2)

        result = Either.left("error").flat_map(double)
        assert result.is_left()
        assert result.unwrap_left() == "error"

    def test_flat_map_preserves_left(self):
        """flat_map should preserve Left through chain."""
        def divide(x):
            return Either.right(10 / x) if x != 0 else Either.left("Div by zero")

        result = Either.right(0).flat_map(divide)
        assert result.is_left()
        assert result.unwrap_left() == "Div by zero"

    def test_flat_map_chain(self):
        """Multiple flat_map operations should chain."""
        def add_one(x):
            return Either.right(x + 1)

        def double(x):
            return Either.right(x * 2)

        result = Either.right(5).flat_map(add_one).flat_map(double)
        assert result.unwrap_right() == 12  # (5 + 1) * 2


class TestEitherSwap:
    """Tests for swap operation."""

    def test_swap_left_to_right(self):
        """swap should convert Left to Right."""
        result = Either.left(1).swap()
        assert result.is_right()
        assert result.unwrap_right() == 1

    def test_swap_right_to_left(self):
        """swap should convert Right to Left."""
        result = Either.right(2).swap()
        assert result.is_left()
        assert result.unwrap_left() == 2


class TestEitherFold:
    """Tests for fold operation."""

    def test_fold_left(self):
        """fold should apply on_left function for Left."""
        result = Either.left("error").fold(
            on_left=lambda e: f"Error: {e}",
            on_right=lambda v: f"Value: {v}"
        )
        assert result == "Error: error"

    def test_fold_right(self):
        """fold should apply on_right function for Right."""
        result = Either.right(42).fold(
            on_left=lambda e: f"Error: {e}",
            on_right=lambda v: f"Value: {v}"
        )
        assert result == "Value: 42"

    def test_fold_with_complex_functions(self):
        """fold should work with complex transformation functions."""
        result = Either.right(42).fold(
            on_left=lambda e: ["Error", e],
            on_right=lambda v: ["Success", v, v * 2]
        )
        assert result == ["Success", 42, 84]


class TestEitherEquality:
    """Tests for Either equality."""

    def test_left_equality(self):
        """Left values should be equal if values match."""
        result1 = Either.left("error")
        result2 = Either.left("error")
        assert result1 == result2

    def test_right_equality(self):
        """Right values should be equal if values match."""
        result1 = Either.right(42)
        result2 = Either.right(42)
        assert result1 == result2

    def test_left_right_inequality(self):
        """Left and Right should not be equal."""
        left = Either.left(42)
        right = Either.right(42)
        assert left != right

    def test_value_inequality(self):
        """Eithers with different values should not be equal."""
        result1 = Either.right(42)
        result2 = Either.right(43)
        assert result1 != result2


class TestEitherPracticalExamples:
    """Practical usage examples."""

    def test_safe_division_chain(self):
        """Chain safe division operations with Either."""
        def safe_divide(a, b):
            return Either.right(a / b) if b != 0 else Either.left("Division by zero")

        result = Either.right(10).flat_map(lambda x: safe_divide(x, 2))
        assert result.is_right()
        assert result.unwrap_right() == 5.0

    def test_validation_pipeline(self):
        """Validate a value through multiple stages."""
        def validate_positive(x):
            return Either.right(x) if x > 0 else Either.left("Not positive")

        def validate_even(x):
            return Either.right(x) if x % 2 == 0 else Either.left("Not even")

        def validate_range(x):
            return Either.right(x) if x <= 100 else Either.left("Too large")

        result = Either.right(4).flat_map(validate_positive).flat_map(validate_even).flat_map(validate_range)
        assert result.is_right()
        assert result.unwrap_right() == 4

    def test_error_recovery_with_fold(self):
        """fold can provide error recovery."""
        result = Either.left("Database error").fold(
            on_left=lambda e: f"Using cache: {e}",
            on_right=lambda v: f"Fresh data: {v}"
        )
        assert result == "Using cache: Database error"

    def test_nested_operations(self):
        """Nested operations with flat_map."""
        def get_user(id):
            if id == 1:
                return Either.right({"id": 1, "name": "Alice"})
            return Either.left("User not found")

        def get_email(user):
            if user["name"] == "Alice":
                return Either.right("alice@example.com")
            return Either.left("Email not found")

        result = Either.right(1).flat_map(get_user).flat_map(get_email)
        assert result.is_right()
        assert result.unwrap_right() == "alice@example.com"

    def test_map_for_transformation(self):
        """map can transform successful values."""
        result = Either.right("hello").map(str.upper).map(lambda x: x + "!")
        assert result.unwrap_right() == "HELLO!"

    def test_map_left_for_error_enrichment(self):
        """map_left can add context to errors."""
        result = (
            Either.left("connection failed")
            .map_left(lambda e: f"Network: {e}")
            .map_left(lambda e: f"Retry: {e}")
        )
        assert result.unwrap_left() == "Retry: Network: connection failed"
