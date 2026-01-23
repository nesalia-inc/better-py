"""Tests for Result monad bind/flatMap operations."""

import pytest

from better_py.monads import Result


class TestResultBind:
    """Tests for bind operation (monadic chain)."""

    def test_bind_ok(self):
        """bind should apply function and unwrap result."""

        def double(x):
            return Result.ok(x * 2)

        result = Result.ok(5).bind(double)
        assert result.is_ok()
        assert result.unwrap() == 10

    def test_bind_error(self):
        """bind should return Error for Error."""

        def double(x):
            return Result.ok(x * 2)

        result = Result.error("failed").bind(double)
        assert result.is_error()
        assert result.unwrap_error() == "failed"

    def test_bind_preserves_error(self):
        """bind should preserve Error through chain."""

        def divide(x):
            return Result.ok(10 / x) if x != 0 else Result.error("Div by zero")

        result = Result.ok(0).bind(divide)
        assert result.is_error()
        assert result.unwrap_error() == "Div by zero"

    def test_bind_chain(self):
        """Multiple bind operations should chain."""

        def add_one(x):
            return Result.ok(x + 1)

        def double(x):
            return Result.ok(x * 2)

        result = Result.ok(5).bind(add_one).bind(double)
        assert result.unwrap() == 12  # (5 + 1) * 2

    def test_bind_with_failing_operation(self):
        """bind should short-circuit on Error."""

        def divide(x):
            return Result.ok(10 / x) if x != 0 else Result.error("Div by zero")

        def add_one(x):
            return Result.ok(x + 1)

        result = Result.ok(0).bind(divide).bind(add_one)
        assert result.is_error()

    def test_bind_type_change(self):
        """bind can change the contained type."""

        def to_string(x):
            return Result.ok(str(x))

        result = Result.ok(42).bind(to_string)
        assert result.unwrap() == "42"


class TestResultFlatMap:
    """Tests for flat_map operation."""

    def test_flat_map_ok(self):
        """flat_map should work like bind."""
        result = Result.ok(5).flat_map(lambda x: Result.ok(x * 2))
        assert result.unwrap() == 10

    def test_flat_map_error(self):
        """flat_map should return Error for Error."""
        result = Result.error("failed").flat_map(lambda x: Result.ok(x * 2))
        assert result.is_error()


class TestResultAndThen:
    """Tests for and_then operation."""

    def test_and_then_ok(self):
        """and_then should work like bind."""
        result = Result.ok(5).and_then(lambda x: Result.ok(x * 2))
        assert result.unwrap() == 10

    def test_and_then_chaining_readable(self):
        """and_then should provide readable chaining."""

        def validate_positive(x):
            return Result.ok(x) if x > 0 else Result.error("Not positive")

        def validate_even(x):
            return Result.ok(x) if x % 2 == 0 else Result.error("Not even")

        result = Result.ok(4).and_then(validate_positive).and_then(validate_even)
        assert result.unwrap() == 4

    def test_and_then_short_circuits(self):
        """and_then should short-circuit on failure."""

        def validate_positive(x):
            return Result.ok(x) if x > 0 else Result.error("Not positive")

        def validate_even(x):
            return Result.ok(x) if x % 2 == 0 else Result.error("Not even")

        result = Result.ok(-4).and_then(validate_positive).and_then(validate_even)
        assert result.is_error()


class TestResultMapError:
    """Tests for map_error operation."""

    def test_map_error_on_ok(self):
        """map_error should preserve Ok."""
        result = Result.ok(42).map_error(str.upper)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_map_error_on_error(self):
        """map_error should apply function to error."""
        result = Result.error("failed").map_error(str.upper)
        assert result.is_error()
        assert result.unwrap_error() == "FAILED"

    def test_map_error_chain(self):
        """map_error can be chained."""
        result = Result.error("failed").map_error(str.upper).map_error(lambda x: x + "!")
        assert result.unwrap_error() == "FAILED!"

    def test_map_preserves_ok(self):
        """map_error should preserve Ok state (not value) through chain."""
        result = Result.ok(42).map_error(str.upper).map(lambda x: x * 2)
        assert result.is_ok()
        assert result.unwrap() == 84


class TestResultOrElse:
    """Tests for or_else operation."""

    def test_or_else_ok(self):
        """or_else should return this Result if Ok."""
        result = Result.ok(5).or_else(Result.ok(10))
        assert result.unwrap() == 5

    def test_or_else_error(self):
        """or_else should return default if Error."""
        result = Result.error("failed").or_else(Result.ok(10))
        assert result.unwrap() == 10

    def test_or_else_error_with_error(self):
        """or_else with Error for both should return Error."""
        result = Result.error("failed").or_else(Result.error("also failed"))
        assert result.is_error()

    def test_or_else_chaining(self):
        """or_else can chain fallbacks."""
        result = (
            Result.error("failed")
            .or_else(Result.error("retry"))
            .or_else(Result.error("final"))
            .or_else(Result.ok(42))
        )
        assert result.unwrap() == 42


class TestResultMonadLaws:
    """Tests for monad laws."""

    def test_left_identity(self):
        """Left identity: bind(f) == f(a) for Ok(a)."""

        def f(x):
            return Result.ok(x * 2)

        value = 5
        result1 = Result.ok(value).bind(f)
        result2 = f(value)
        assert result1 == result2

    def test_right_identity(self):
        """Right identity: bind(Result.ok) == identity."""
        result = Result.ok(42)
        mapped = result.bind(Result.ok)
        assert mapped == result

    def test_associativity(self):
        """Associativity: bind(f).bind(g) == bind(lambda x: f(x).bind(g))."""

        def f(x):
            return Result.ok(x + 1)

        def g(x):
            return Result.ok(x * 2)

        result = Result.ok(5)

        result1 = result.bind(f).bind(g)
        result2 = result.bind(lambda x: f(x).bind(g))

        assert result1 == result2

    def test_map_then_bind_vs_bind(self):
        """map(f).bind(g) == bind(lambda x: g(f(x)))."""

        def f(x):
            return x * 2

        def g(x):
            return Result.ok(x + 1)

        result = Result.ok(5)

        result1 = result.map(f).bind(g)
        result2 = result.bind(lambda x: g(f(x)))

        assert result1 == result2


class TestResultPracticalExamples:
    """Practical usage examples."""

    def test_safe_division_chain(self):
        """Chain safe division operations."""

        def safe_divide(a, b):
            return Result.ok(a / b) if b != 0 else Result.error("Division by zero")

        def safe_add(a, b):
            return Result.ok(a + b)

        # (10 / 2) + 3 = 8
        result = Result.ok(10).bind(lambda x: safe_divide(x, 2)).bind(lambda x: safe_add(x, 3))
        assert result.unwrap() == 8.0

    def test_validation_chain(self):
        """Chain validation operations."""

        def validate_positive(x):
            return Result.ok(x) if x > 0 else Result.error("Not positive")

        def validate_even(x):
            return Result.ok(x) if x % 2 == 0 else Result.error("Not even")

        def validate_range(x):
            return Result.ok(x) if x <= 100 else Result.error("Too large")

        result = Result.ok(4).bind(validate_positive).bind(validate_even).bind(validate_range)
        assert result.unwrap() == 4

    def test_error_accumulation(self):
        """Map error to provide more context."""

        def process(x):
            if x < 0:
                return Result.error("Negative")
            if x > 100:
                return Result.error("Too large")
            return Result.ok(x)

        result = Result.ok(150).bind(process).map_error(lambda e: f"Validation failed: {e}")
        assert result.is_error()
        assert result.unwrap_error() == "Validation failed: Too large"

    def test_nested_operations(self):
        """Nested operations with bind."""

        def get_user(id):
            if id == 1:
                return Result.ok({"id": 1, "name": "Alice"})
            return Result.error("User not found")

        def get_email(user):
            if user["name"] == "Alice":
                return Result.ok("alice@example.com")
            return Result.error("Email not found")

        result = Result.ok(1).bind(get_user).bind(get_email)
        assert result.unwrap() == "alice@example.com"

    def test_flat_map_vs_map(self):
        """flat_map vs map for nested structures."""
        # map returns Result[Result[int]]
        mapped = Result.ok(5).map(lambda x: Result.ok(x * 2))

        # flat_map returns Result[int]
        flat_mapped = Result.ok(5).flat_map(lambda x: Result.ok(x * 2))

        assert mapped.is_ok()
        assert mapped.unwrap().is_ok()
        assert flat_mapped.unwrap() == 10

    def test_error_recovery_with_or_else(self):
        """or_else can provide fallback on error."""

        def risky_operation(x):
            return Result.ok(x) if x > 0 else Result.error("Negative")

        # First attempt fails, second succeeds
        result = Result.ok(-5).bind(risky_operation).or_else(Result.ok(0))
        assert result.unwrap() == 0

    def test_map_error_for_error_enrichment(self):
        """map_error can add context to errors."""

        def parse_int(s):
            try:
                return Result.ok(int(s))
            except ValueError:
                return Result.error("Invalid integer")

        result = parse_int("abc").map_error(lambda e: f"Parse error: {e}")
        assert result.is_error()
        assert "Parse error: Invalid integer" in result.unwrap_error()
