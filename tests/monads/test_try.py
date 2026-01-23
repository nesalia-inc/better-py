"""Tests for Try monad."""


from better_py.monads import Try


class TestTryConstruction:
    """Tests for Try construction."""

    def test_of_success(self):
        """of should create Success when function succeeds."""
        result = Try.of(lambda: 42)
        assert result.is_success()
        assert result.get() == 42

    def test_of_failure(self):
        """of should create Failure when function raises."""
        result = Try.of(lambda: int("abc"))
        assert result.is_failure()
        assert isinstance(result.get_exception(), ValueError)

    def test_success_creation(self):
        """success should create a Success variant."""
        result = Try.success(42)
        assert result.is_success()
        assert result.get() == 42

    def test_failure_creation(self):
        """failure should create a Failure variant."""
        exc = ValueError("error")
        result = Try.failure(exc)
        assert result.is_failure()
        assert result.get_exception() == exc

    def test_success_repr(self):
        """Success should have correct repr."""
        result = Try.success(42)
        assert repr(result) == "Success(42)"

    def test_failure_repr(self):
        """Failure should have correct repr."""
        result = Try.failure(ValueError("error"))
        assert "Failure" in repr(result)
        assert "ValueError" in repr(result)


class TestTryGet:
    """Tests for getting values."""

    def test_get_success(self):
        """get should return Success value."""
        result = Try.success(42)
        assert result.get() == 42

    def test_get_failure(self):
        """get should return None for Failure."""
        result = Try.failure(ValueError("error"))
        assert result.get() is None

    def test_get_exception_success(self):
        """get_exception should return None for Success."""
        result = Try.success(42)
        assert result.get_exception() is None

    def test_get_exception_failure(self):
        """get_exception should return exception for Failure."""
        exc = ValueError("error")
        result = Try.failure(exc)
        assert result.get_exception() == exc

    def test_get_or_else_success(self):
        """get_or_else should return value for Success."""
        result = Try.success(42)
        assert result.get_or_else(0) == 42

    def test_get_or_else_failure(self):
        """get_or_else should return default for Failure."""
        result = Try.failure(ValueError("error"))
        assert result.get_or_else(0) == 0


class TestTryRecover:
    """Tests for recover operation."""

    def test_recover_failure(self):
        """recover should handle exception with function."""
        result = Try.failure(ValueError("error")).recover(lambda _e: 0)
        assert result.is_success()
        assert result.get() == 0

    def test_recover_success(self):
        """recover should preserve Success."""
        result = Try.success(42).recover(lambda _e: 0)
        assert result.is_success()
        assert result.get() == 42

    def test_recover_with_exception(self):
        """recover should preserve Failure if handler raises."""
        result = Try.failure(ValueError("error")).recover(lambda _e: int("abc"))
        assert result.is_failure()


class TestTryMap:
    """Tests for map operation."""

    def test_map_success(self):
        """map should apply function to Success value."""
        result = Try.success(5).map(lambda x: x * 2)
        assert result.is_success()
        assert result.get() == 10

    def test_map_failure(self):
        """map should preserve Failure."""
        result = Try.failure(ValueError("error")).map(lambda x: x * 2)
        assert result.is_failure()

    def test_map_with_exception(self):
        """map should catch exceptions."""
        result = Try.success(5).map(lambda _x: int("abc"))
        assert result.is_failure()

    def test_map_chain(self):
        """Multiple map operations should chain."""
        result = Try.success(5).map(lambda x: x + 1).map(lambda x: x * 2).map(lambda x: x - 3)
        assert result.get() == 9  # ((5 + 1) * 2) - 3


class TestTryFlatMap:
    """Tests for flat_map operation."""

    def test_flat_map_success(self):
        """flat_map should apply function and unwrap."""
        def double(x):
            return Try.success(x * 2)

        result = Try.success(5).flat_map(double)
        assert result.is_success()
        assert result.get() == 10

    def test_flat_map_failure(self):
        """flat_map should return Failure for Failure."""
        def double(x):
            return Try.success(x * 2)

        result = Try.failure(ValueError("error")).flat_map(double)
        assert result.is_failure()

    def test_flat_map_preserves_failure(self):
        """flat_map should preserve Failure through chain."""
        def divide(x):
            return Try.of(lambda: 10 / x)

        result = Try.success(0).flat_map(divide)
        assert result.is_failure()

    def test_flat_map_chain(self):
        """Multiple flat_map operations should chain."""
        def add_one(x):
            return Try.success(x + 1)

        def double(x):
            return Try.success(x * 2)

        result = Try.success(5).flat_map(add_one).flat_map(double)
        assert result.get() == 12  # (5 + 1) * 2


class TestTryFold:
    """Tests for fold operation."""

    def test_fold_failure(self):
        """fold should apply on_failure function for Failure."""
        result = Try.failure(ValueError("error")).fold(
            on_failure=lambda e: f"Error: {e}",
            on_success=lambda v: f"Value: {v}"
        )
        assert "Error" in result

    def test_fold_success(self):
        """fold should apply on_success function for Success."""
        result = Try.success(42).fold(
            on_failure=lambda e: f"Error: {e}",
            on_success=lambda v: f"Value: {v}"
        )
        assert result == "Value: 42"

    def test_fold_with_complex_functions(self):
        """fold should work with complex transformation functions."""
        result = Try.success(42).fold(
            on_failure=lambda e: ["Error", str(e)],
            on_success=lambda v: ["Success", v, v * 2]
        )
        assert result == ["Success", 42, 84]


class TestTryToOption:
    """Tests for to_option conversion."""

    def test_to_option_success(self):
        """to_option should convert Success to Some."""
        result = Try.success(42).to_option()
        assert result.is_some()
        assert result.unwrap() == 42

    def test_to_option_failure(self):
        """to_option should convert Failure to Nothing."""
        result = Try.failure(ValueError("error")).to_option()
        assert result.is_nothing()


class TestTryEquality:
    """Tests for Try equality."""

    def test_success_equality(self):
        """Success values should be equal if values match."""
        result1 = Try.success(42)
        result2 = Try.success(42)
        assert result1 == result2

    def test_failure_equality(self):
        """Failure values should be equal if exceptions match."""
        exc = ValueError("error")
        result1 = Try.failure(exc)
        result2 = Try.failure(exc)
        assert result1 == result2

    def test_success_failure_inequality(self):
        """Success and Failure should not be equal."""
        success = Try.success(42)
        failure = Try.failure(ValueError("error"))
        assert success != failure

    def test_value_inequality(self):
        """Tries with different values should not be equal."""
        result1 = Try.success(42)
        result2 = Try.success(43)
        assert result1 != result2


class TestTryPracticalExamples:
    """Practical usage examples."""

    def test_safe_division(self):
        """Safely divide numbers."""
        def safe_divide(a, b):
            return Try.of(lambda: a / b)

        result = safe_divide(10, 2)
        assert result.is_success()
        assert result.get() == 5.0

    def test_division_by_zero(self):
        """Handle division by zero."""
        def safe_divide(a, b):
            return Try.of(lambda: a / b)

        result = safe_divide(10, 0)
        assert result.is_failure()
        assert isinstance(result.get_exception(), ZeroDivisionError)

    def test_parse_int(self):
        """Safely parse integer."""
        def parse_int(s):
            return Try.of(lambda: int(s))

        result = parse_int("42")
        assert result.is_success()
        assert result.get() == 42

    def test_parse_int_invalid(self):
        """Handle invalid integer string."""
        def parse_int(s):
            return Try.of(lambda: int(s))

        result = parse_int("abc")
        assert result.is_failure()
        assert isinstance(result.get_exception(), ValueError)

    def test_json_parse(self):
        """Safely parse JSON."""
        import json

        def parse_json(s):
            return Try.of(lambda: json.loads(s))

        result = parse_json('{"key": "value"}')
        assert result.is_success()
        assert result.get()["key"] == "value"

    def test_file_read(self):
        """Handle file reading errors."""
        def read_file(path):
            return Try.of(lambda: open(path).read())

        result = read_file("/nonexistent/file.txt")
        assert result.is_failure()
        assert isinstance(result.get_exception(), FileNotFoundError)

    def test_error_recovery(self):
        """Recover from errors with default values."""
        result = (
            Try.of(lambda: int("invalid"))
            .recover(lambda _e: 0)
            .map(lambda x: x * 2)
        )
        assert result.is_success()
        assert result.get() == 0

    def test_chained_operations(self):
        """Chain multiple operations that may fail."""
        def divide(x, y):
            return Try.of(lambda: x / y)

        result = (
            Try.of(lambda: 10)
            .flat_map(lambda x: divide(x, 2))
            .flat_map(lambda x: divide(x, 5))
        )
        assert result.is_success()
        assert result.get() == 1.0
