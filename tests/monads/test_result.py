"""Tests for Result monad."""

import pytest

from better_py.monads import Result


class TestResultCreation:
    """Tests for creating Result instances."""

    def test_ok_with_value(self):
        """ok() should create a Result containing the value."""
        result = Result.ok(42)
        assert result.is_ok()
        assert not result.is_error()
        assert result.unwrap() == 42

    def test_error_with_error(self):
        """error() should create a Result containing the error."""
        result = Result.error("Something went wrong")
        assert result.is_error()
        assert not result.is_ok()
        assert result.unwrap_error() == "Something went wrong"

    def test_from_value_with_value(self):
        """from_value() should create Ok when error is None."""
        result = Result.from_value(42)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_from_value_with_error(self):
        """from_value() should create Error when error is provided."""
        result = Result.from_value(42, "Error")
        assert result.is_error()
        assert result.unwrap_error() == "Error"

    def test_from_value_with_none_error(self):
        """from_value() should create Ok when error is None."""
        result = Result.from_value(42, None)
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_ok_with_zero(self):
        """ok() should treat 0 as a valid value."""
        result = Result.ok(0)
        assert result.is_ok()
        assert result.unwrap() == 0

    def test_ok_with_false(self):
        """ok() should treat False as a valid value."""
        result = Result.ok(False)
        assert result.is_ok()
        assert result.unwrap() is False

    def test_ok_with_empty_string(self):
        """ok() should treat empty string as a valid value."""
        result = Result.ok("")
        assert result.is_ok()
        assert result.unwrap() == ""

    def test_error_with_zero(self):
        """error() can contain 0 as error value."""
        result = Result.error(0)
        assert result.is_error()
        assert result.unwrap_error() == 0

    def test_error_with_false(self):
        """error() can contain False as error value."""
        result = Result.error(False)
        assert result.is_error()
        assert result.unwrap_error() is False


class TestResultInspection:
    """Tests for inspecting Result state."""

    def test_is_ok_on_ok(self):
        """is_ok() should return True for Ok."""
        assert Result.ok(42).is_ok() is True

    def test_is_ok_on_error(self):
        """is_ok() should return False for Error."""
        assert Result.error("failed").is_ok() is False

    def test_is_error_on_ok(self):
        """is_error() should return False for Ok."""
        assert Result.ok(42).is_error() is False

    def test_is_error_on_error(self):
        """is_error() should return True for Error."""
        assert Result.error("failed").is_error() is True


class TestResultUnwrap:
    """Tests for unwrapping Result values."""

    def test_unwrap_ok(self):
        """unwrap() should return the success value."""
        assert Result.ok(42).unwrap() == 42

    def test_unwrap_error_raises(self):
        """unwrap() should raise ValueError for Error."""
        with pytest.raises(ValueError, match="Cannot unwrap Error"):
            Result.error("failed").unwrap()

    def test_unwrap_or_ok(self):
        """unwrap_or() should return the value for Ok."""
        assert Result.ok(42).unwrap_or(0) == 42

    def test_unwrap_or_error(self):
        """unwrap_or() should return the default for Error."""
        assert Result.error("failed").unwrap_or(0) == 0

    def test_unwrap_or_else_ok(self):
        """unwrap_or_else() should return the value for Ok."""
        assert Result.ok(42).unwrap_or_else(lambda: 0) == 42

    def test_unwrap_or_else_error(self):
        """unwrap_or_else() should call the supplier for Error."""
        assert Result.error("failed").unwrap_or_else(lambda: 42) == 42

    def test_unwrap_or_else_not_called_for_ok(self):
        """unwrap_or_else() should not call supplier for Ok."""
        called = False

        def supplier():
            nonlocal called
            called = True
            return 0

        Result.ok(42).unwrap_or_else(supplier)
        assert called is False

    def test_unwrap_error_on_error(self):
        """unwrap_error() should return the error value."""
        assert Result.error("failed").unwrap_error() == "failed"

    def test_unwrap_error_on_ok_raises(self):
        """unwrap_error() should raise ValueError for Ok."""
        with pytest.raises(ValueError, match="Cannot unwrap_error Ok"):
            Result.ok(42).unwrap_error()


class TestResultMap:
    """Tests for map operation."""

    def test_map_ok(self):
        """map() should apply function to Ok value."""
        result = Result.ok(5).map(lambda x: x * 2)
        assert result.is_ok()
        assert result.unwrap() == 10

    def test_map_error(self):
        """map() should return Error for Error."""
        result = Result.error("failed").map(lambda x: x * 2)
        assert result.is_error()
        assert result.unwrap_error() == "failed"

    def test_map_type_change(self):
        """map() can change the contained type."""
        result = Result.ok(42).map(str)
        assert result.is_ok()
        assert result.unwrap() == "42"

    def test_map_chain(self):
        """Multiple map operations should chain."""
        result = Result.ok(5).map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: x / 2)
        assert result.unwrap() == 5.5

    def test_map_preserves_error(self):
        """map() should preserve Error through chain."""
        result = Result.error("failed").map(lambda x: x * 2).map(lambda x: x + 1)
        assert result.is_error()
        assert result.unwrap_error() == "failed"

    def test_map_identity_law(self):
        """map(id) should equal identity."""
        result = Result.ok(42)
        mapped = result.map(lambda x: x)
        assert mapped == result


class TestResultEquality:
    """Tests for Result equality."""

    def test_ok_equals_ok(self):
        """Two Ok with same values should be equal."""
        assert Result.ok(42) == Result.ok(42)

    def test_ok_not_equals_ok_different_value(self):
        """Two Ok with different values should not be equal."""
        assert Result.ok(42) != Result.ok(43)

    def test_error_equals_error(self):
        """Two Error with same errors should be equal."""
        assert Result.error("failed") == Result.error("failed")

    def test_error_not_equals_error_different_value(self):
        """Two Error with different errors should not be equal."""
        assert Result.error("failed") != Result.error("other error")

    def test_ok_not_equals_error(self):
        """Ok should not equal Error."""
        assert Result.ok(42) != Result.error("failed")

    def test_result_not_equals_other_type(self):
        """Result should not equal other types."""
        assert Result.ok(42) != 42
        assert Result.ok(42) != "42"
        assert Result.error("failed") != None


class TestResultRepr:
    """Tests for Result string representation."""

    def test_ok_repr(self):
        """Ok should have correct repr."""
        assert repr(Result.ok(42)) == "Ok(42)"
        assert repr(Result.ok("hello")) == "Ok('hello')"

    def test_error_repr(self):
        """Error should have correct repr."""
        assert repr(Result.error("failed")) == "Error('failed')"
        assert repr(Result.error(42)) == "Error(42)"


class TestResultMappable:
    """Tests for Mappable protocol compliance."""

    def test_result_is_mappable(self):
        """Result should satisfy Mappable protocol."""
        from better_py.protocols import Mappable

        result: Mappable[int] = Result.ok(42)
        assert isinstance(result, Mappable)


class TestResultGenericTypes:
    """Tests for Result with generic types."""

    def test_result_with_int_error_str(self):
        """Result should work with int and str."""
        result: Result[int, str] = Result.ok(42)
        assert result.unwrap() == 42

    def test_result_with_str_error_int(self):
        """Result should work with str and int."""
        result: Result[str, int] = Result.ok("hello")
        assert result.unwrap() == "hello"

    def test_result_with_list_error_dict(self):
        """Result should work with list and dict."""
        result: Result[list[int], dict] = Result.ok([1, 2, 3])
        assert result.unwrap() == [1, 2, 3]

    def test_result_error_type(self):
        """Result error type should be preserved."""
        result: Result[int, str] = Result.error("failed")
        assert result.unwrap_error() == "failed"


class TestResultApplicative:
    """Tests for Result applicative operations."""

    def test_ap_both_ok(self):
        """ap should apply function when both are Ok."""
        add = Result.ok(lambda x: x + 1)
        value = Result.ok(5)
        result = value.ap(add)
        assert result.is_ok()
        assert result.unwrap() == 6

    def test_ap_function_error(self):
        """ap should return Error when function is Error."""
        error_fn = Result.error("bad")
        value = Result.ok(5)
        result = value.ap(error_fn)
        assert result.is_error()

    def test_ap_value_error(self):
        """ap should return Error when value is Error."""
        add = Result.ok(lambda x: x + 1)
        error_value = Result.error("bad")
        result = error_value.ap(add)
        assert result.is_error()

    def test_lift2_both_ok(self):
        """lift2 should apply function when both are Ok."""
        result = Result.lift2(lambda x, y: x + y, Result.ok(1), Result.ok(2))
        assert result.is_ok()
        assert result.unwrap() == 3

    def test_lift2_first_error(self):
        """lift2 should return Error when first is Error."""
        result = Result.lift2(lambda x, y: x + y, Result.error("bad"), Result.ok(2))
        assert result.is_error()

    def test_lift3_all_ok(self):
        """lift3 should apply function when all are Ok."""
        result = Result.lift3(lambda x, y, z: x + y + z, Result.ok(1), Result.ok(2), Result.ok(3))
        assert result.is_ok()
        assert result.unwrap() == 6

    def test_zip_all_ok(self):
        """zip should combine all Ok values into a tuple."""
        result = Result.zip(Result.ok(1), Result.ok(2), Result.ok(3))
        assert result.is_ok()
        assert result.unwrap() == (1, 2, 3)

    def test_zip_one_error(self):
        """zip should return Error when any is Error."""
        result = Result.zip(Result.ok(1), Result.error("bad"), Result.ok(3))
        assert result.is_error()
