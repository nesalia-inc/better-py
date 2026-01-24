"""Tests for Validation monad."""

import pytest

from better_py.monads import Validation


class TestValidationConstruction:
    """Tests for Validation construction."""

    def test_valid_creation(self):
        """valid should create a Valid variant."""
        result = Validation.valid(42)
        assert result.is_valid()
        assert not result.is_invalid()

    def test_invalid_with_list(self):
        """invalid should create an Invalid variant with list."""
        result = Validation.invalid(["error1", "error2"])
        assert result.is_invalid()
        assert not result.is_valid()
        assert result.unwrap_errors() == ["error1", "error2"]

    def test_invalid_with_single_error(self):
        """invalid should create an Invalid variant with single error."""
        result = Validation.invalid("error")
        assert result.is_invalid()
        assert result.unwrap_errors() == ["error"]

    def test_valid_repr(self):
        """Valid should have correct repr."""
        result = Validation.valid(42)
        assert repr(result) == "Valid(42)"

    def test_invalid_repr(self):
        """Invalid should have correct repr."""
        result = Validation.invalid(["error"])
        assert repr(result) == "Invalid(['error'])"


class TestValidationUnwrap:
    """Tests for unwrapping Validation values."""

    def test_unwrap_valid(self):
        """unwrap should return Valid value."""
        result = Validation.valid(42)
        assert result.unwrap() == 42

    def test_unwrap_invalid_raises(self):
        """unwrap on Invalid should raise."""
        result = Validation.invalid(["error"])
        with pytest.raises(ValueError) as exc_info:
            result.unwrap()
        assert "Cannot unwrap Invalid" in str(exc_info.value)

    def test_unwrap_errors_invalid(self):
        """unwrap_errors should return errors."""
        result = Validation.invalid(["error1", "error2"])
        assert result.unwrap_errors() == ["error1", "error2"]

    def test_unwrap_errors_valid_raises(self):
        """unwrap_errors on Valid should raise."""
        result = Validation.valid(42)
        with pytest.raises(ValueError) as exc_info:
            result.unwrap_errors()
        assert "Cannot unwrap_errors Valid" in str(exc_info.value)


class TestValidationMap:
    """Tests for map operation."""

    def test_map_valid(self):
        """map should apply function to Valid value."""
        result = Validation.valid(5).map(lambda x: x * 2)
        assert result.is_valid()
        assert result.unwrap() == 10

    def test_map_invalid(self):
        """map should preserve Invalid."""
        result = Validation.invalid(["error"]).map(lambda x: x * 2)
        assert result.is_invalid()
        assert result.unwrap_errors() == ["error"]

    def test_map_chain(self):
        """Multiple map operations should chain."""
        result = Validation.valid(5).map(lambda x: x + 1).map(lambda x: x * 2).map(lambda x: x - 3)
        assert result.unwrap() == 9  # ((5 + 1) * 2) - 3


class TestValidationMapErrors:
    """Tests for map_errors operation."""

    def test_map_errors_invalid(self):
        """map_errors should apply function to errors."""
        result = Validation.invalid(["error1", "error2"]).map_errors(
            lambda errs: [f"! {e}" for e in errs]
        )
        assert result.is_invalid()
        assert result.unwrap_errors() == ["! error1", "! error2"]

    def test_map_errors_valid(self):
        """map_errors should preserve Valid."""
        result = Validation.valid(42).map_errors(lambda errs: [f"! {e}" for e in errs])
        assert result.is_valid()
        assert result.unwrap() == 42


class TestValidationFlatMap:
    """Tests for flat_map operation."""

    def test_flat_map_valid(self):
        """flat_map should apply function and unwrap."""
        def double(x):
            return Validation.valid(x * 2)

        result = Validation.valid(5).flat_map(double)
        assert result.is_valid()
        assert result.unwrap() == 10

    def test_flat_map_invalid(self):
        """flat_map should return Invalid for Invalid."""
        def double(x):
            return Validation.valid(x * 2)

        result = Validation.invalid(["error"]).flat_map(double)
        assert result.is_invalid()
        assert result.unwrap_errors() == ["error"]

    def test_flat_map_preserves_invalid(self):
        """flat_map should preserve Invalid through chain."""
        def validate_positive(x):
            return Validation.valid(x) if x > 0 else Validation.invalid(["Not positive"])

        result = Validation.valid(-1).flat_map(validate_positive)
        assert result.is_invalid()
        assert result.unwrap_errors() == ["Not positive"]

    def test_flat_map_chain(self):
        """Multiple flat_map operations should chain."""
        def add_one(x):
            return Validation.valid(x + 1)

        def double(x):
            return Validation.valid(x * 2)

        result = Validation.valid(5).flat_map(add_one).flat_map(double)
        assert result.unwrap() == 12  # (5 + 1) * 2


class TestValidationAp:
    """Tests for ap (apply) operation."""

    def test_ap_both_valid(self):
        """ap should apply function when both are Valid."""
        add_one = Validation.valid(lambda x: x + 1)
        value = Validation.valid(5)
        result = add_one.ap(value)
        assert result.is_valid()
        assert result.unwrap() == 6

    def test_ap_invalid_function(self):
        """ap should return Invalid when function is Invalid."""
        invalid_fn = Validation.invalid(["error"])
        value = Validation.valid(5)
        result = invalid_fn.ap(value)
        assert result.is_invalid()

    def test_ap_invalid_value(self):
        """ap should return Invalid when value is Invalid."""
        fn = Validation.valid(lambda x: x + 1)
        invalid_value = Validation.invalid(["error"])
        result = fn.ap(invalid_value)
        assert result.is_invalid()

    def test_ap_both_invalid(self):
        """ap should return Invalid when both are Invalid."""
        invalid_fn = Validation.invalid(["error1"])
        invalid_value = Validation.invalid(["error2"])
        result = invalid_fn.ap(invalid_value)
        assert result.is_invalid()

    def test_ap_accumulates_errors(self):
        """ap should accumulate errors when both Validations are Invalid."""
        invalid_fn = Validation.invalid(["error1", "error2"])
        invalid_value = Validation.invalid(["error3"])
        result = invalid_fn.ap(invalid_value)

        assert result.is_invalid()
        assert result.unwrap_errors() == ["error1", "error2", "error3"]


class TestValidationFold:
    """Tests for fold operation."""

    def test_fold_invalid(self):
        """fold should apply on_invalid function for Invalid."""
        result = Validation.invalid(["error"]).fold(
            on_invalid=lambda errs: f"Errors: {errs}",
            on_valid=lambda v: f"Value: {v}"
        )
        assert result == "Errors: ['error']"

    def test_fold_valid(self):
        """fold should apply on_valid function for Valid."""
        result = Validation.valid(42).fold(
            on_invalid=lambda errs: f"Errors: {errs}",
            on_valid=lambda v: f"Value: {v}"
        )
        assert result == "Value: 42"

    def test_fold_with_complex_functions(self):
        """fold should work with complex transformation functions."""
        result = Validation.valid(42).fold(
            on_invalid=lambda errs: ["Error", errs],
            on_valid=lambda v: ["Success", v, v * 2]
        )
        assert result == ["Success", 42, 84]


class TestValidationToResult:
    """Tests for to_result conversion."""

    def test_to_result_valid(self):
        """to_result should convert Valid to Ok."""
        result = Validation.valid(42).to_result()
        assert result.is_ok()
        assert result.unwrap() == 42

    def test_to_result_invalid(self):
        """to_result should convert Invalid to Error."""
        result = Validation.invalid(["error"]).to_result()
        assert result.is_error()
        assert result.unwrap_error() == "error"


class TestValidationEquality:
    """Tests for Validation equality."""

    def test_valid_equality(self):
        """Valid values should be equal if values match."""
        result1 = Validation.valid(42)
        result2 = Validation.valid(42)
        assert result1 == result2

    def test_invalid_equality(self):
        """Invalid values should be equal if errors match."""
        result1 = Validation.invalid(["error"])
        result2 = Validation.invalid(["error"])
        assert result1 == result2

    def test_valid_invalid_inequality(self):
        """Valid and Invalid should not be equal."""
        valid = Validation.valid(42)
        invalid = Validation.invalid(["error"])
        assert valid != invalid

    def test_value_inequality(self):
        """Validations with different values should not be equal."""
        result1 = Validation.valid(42)
        result2 = Validation.valid(43)
        assert result1 != result2


class TestValidationPracticalExamples:
    """Practical usage examples."""

    def test_form_validation_accumulates_errors(self):
        """Form validation should accumulate all errors."""
        def validate_username(name):
            if len(name) < 3:
                return Validation.invalid(["Username too short"])
            if len(name) > 20:
                return Validation.invalid(["Username too long"])
            return Validation.valid(name)

        def validate_email(email):
            if "@" not in email:
                return Validation.invalid(["Invalid email"])
            return Validation.valid(email)

        # Test invalid username and email
        username_result = validate_username("ab")
        email_result = validate_email("invalid")

        assert username_result.is_invalid()
        assert email_result.is_invalid()

    def test_validation_pipeline(self):
        """Validate a value through multiple stages."""
        def validate_positive(x):
            return Validation.valid(x) if x > 0 else Validation.invalid(["Not positive"])

        def validate_even(x):
            return Validation.valid(x) if x % 2 == 0 else Validation.invalid(["Not even"])

        def validate_range(x):
            return Validation.valid(x) if x <= 100 else Validation.invalid(["Too large"])

        result = Validation.valid(4).flat_map(validate_positive).flat_map(validate_even).flat_map(validate_range)
        assert result.is_valid()
        assert result.unwrap() == 4

    def test_error_recovery_with_fold(self):
        """fold can provide error recovery."""
        result = Validation.invalid(["Database error", "Network error"]).fold(
            on_invalid=lambda errs: f"Using cache (errors: {', '.join(errs)})",
            on_valid=lambda v: f"Fresh data: {v}"
        )
        assert "Using cache" in result
        assert "Database error" in result
