"""Tests for Validable protocol."""

from better_py.protocols import Validable


class ValidatedValue(Validable):
    """Simple validated value implementation."""

    def __init__(self, value: int, errors: list[str] | None = None):
        self._value = value
        self._errors = errors or []

    def is_valid(self) -> bool:
        """Check if this is a valid value."""
        return len(self._errors) == 0

    def is_invalid(self) -> bool:
        """Check if this is invalid."""
        return len(self._errors) > 0

    def validate(self, *validators):
        """Apply validators to the value."""
        errors = []
        for validator in validators:
            if not validator(self._value):
                errors.append(f"Validation failed: {validator.__name__}")

        if errors:
            return ValidatedValue(self._value, self._errors + errors)
        return ValidatedValue(self._value, self._errors)

    def map(self, f):
        """Apply a function to the value."""
        if self.is_invalid():
            return ValidatedValue(self._value, self._errors)
        try:
            return ValidatedValue(f(self._value), self._errors)
        except Exception:
            return ValidatedValue(self._value, self._errors + ["Map failed"])

    def map_errors(self, f):
        """Apply a function to the errors."""
        return ValidatedValue(self._value, f(self._errors))

    def get_errors(self) -> list:
        """Get the list of errors."""
        return self._errors

    def __eq__(self, other):
        return isinstance(other, ValidatedValue) and self._value == other._value and self._errors == other._errors

    def __repr__(self):
        if self.is_valid():
            return f"Valid({self._value})"
        return f"Invalid({self._value}, errors={self._errors})"


# Test validators
def is_positive(x: int) -> bool:
    """Check if value is positive."""
    return x > 0


def is_even(x: int) -> bool:
    """Check if value is even."""
    return x % 2 == 0


def is_less_than_100(x: int) -> bool:
    """Check if value is less than 100."""
    return x < 100


class TestValidable:
    """Tests for Validable protocol."""

    def test_validated_value_is_validable(self):
        """ValidatedValue should satisfy Validable protocol."""
        data: Validable = ValidatedValue(42)
        assert isinstance(data, Validable)

    def test_is_valid_true(self):
        """is_valid should return True for valid values."""
        result = ValidatedValue(42)
        assert result.is_valid() is True

    def test_is_valid_false(self):
        """is_valid should return False for invalid values."""
        result = ValidatedValue(42, errors=["Invalid"])
        assert result.is_valid() is False

    def test_is_invalid_false(self):
        """is_invalid should return False for valid values."""
        result = ValidatedValue(42)
        assert result.is_invalid() is False

    def test_is_invalid_true(self):
        """is_invalid should return True for invalid values."""
        result = ValidatedValue(42, errors=["Invalid"])
        assert result.is_invalid() is True

    def test_validate_with_passing_validators(self):
        """validate should succeed with passing validators."""
        result = ValidatedValue(4).validate(is_positive, is_even)
        assert result.is_valid()

    def test_validate_with_failing_validator(self):
        """validate should fail with failing validator."""
        result = ValidatedValue(3).validate(is_even)
        assert result.is_invalid()
        assert len(result.get_errors()) == 1

    def test_validate_with_multiple_failing_validators(self):
        """validate should accumulate errors from multiple validators."""
        result = ValidatedValue(-1).validate(is_positive, is_even, is_less_than_100)
        assert result.is_invalid()
        assert len(result.get_errors()) == 2  # Both is_positive and is_even fail

    def test_validate_accumulates_errors(self):
        """validate should accumulate errors from existing and new validators."""
        result = ValidatedValue(3, errors=["Initial error"]).validate(is_even)
        assert result.is_invalid()
        assert len(result.get_errors()) == 2

    def test_validate_empty_validators(self):
        """validate with no validators should return valid."""
        result = ValidatedValue(42).validate()
        assert result.is_valid()

    def test_map_valid_value(self):
        """map should apply function to valid values."""
        result = ValidatedValue(10)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_valid()

    def test_map_invalid_value(self):
        """map should preserve invalid state."""
        result = ValidatedValue(10, errors=["Error"])
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_invalid()
        assert mapped._value == 10  # Value unchanged

    def test_map_chaining(self):
        """Multiple map operations should chain."""
        result = ValidatedValue(10)
        chained = result.map(lambda x: x + 1).map(lambda x: x * 2).map(lambda x: x - 5)
        assert chained.is_valid()

    def test_map_errors_valid(self):
        """map_errors on valid value should keep it valid."""
        result = ValidatedValue(42)
        mapped = result.map_errors(lambda errs: [f"! {e}" for e in errs])
        assert mapped.is_valid()

    def test_map_errors_invalid(self):
        """map_errors should transform error messages."""
        result = ValidatedValue(42, errors=["Error 1", "Error 2"])
        mapped = result.map_errors(lambda errs: [f"! {e}" for e in errs])
        assert mapped.is_invalid()
        assert mapped.get_errors() == ["! Error 1", "! Error 2"]

    def test_get_errors_valid(self):
        """get_errors should return empty list for valid values."""
        result = ValidatedValue(42)
        assert result.get_errors() == []

    def test_get_errors_invalid(self):
        """get_errors should return list of errors."""
        errors = ["Error 1", "Error 2"]
        result = ValidatedValue(42, errors=errors)
        assert result.get_errors() == errors

    def test_validation_pipeline(self):
        """Complex validation pipeline with multiple steps."""
        result = (
            ValidatedValue(8)
            .validate(is_positive, is_even)
            .map(lambda x: x * 2)
            .validate(is_less_than_100)
        )
        assert result.is_valid()

    def test_validation_pipeline_with_failure(self):
        """Validation pipeline should fail on first error."""
        result = (
            ValidatedValue(101)
            .validate(is_positive)
            .validate(is_less_than_100)
            .map(lambda x: x * 2)
        )
        assert result.is_invalid()

    def test_equality_valid(self):
        """Valid values should be equal if values match."""
        result1 = ValidatedValue(42)
        result2 = ValidatedValue(42)
        assert result1 == result2

    def test_equality_invalid(self):
        """Invalid values should be equal if values and errors match."""
        result1 = ValidatedValue(42, errors=["Error"])
        result2 = ValidatedValue(42, errors=["Error"])
        assert result1 == result2

    def test_inequality_different_values(self):
        """ValidatedValues with different values should not be equal."""
        result1 = ValidatedValue(42)
        result2 = ValidatedValue(43)
        assert result1 != result2


class TestValidableComplexScenarios:
    """Tests for complex Validable scenarios."""

    def test_validate_form_data(self):
        """Simulate form validation with multiple fields."""
        username = ValidatedValue("user123")
        age = ValidatedValue(25)

        # Both are valid
        assert username.is_valid()
        assert age.is_valid()

    def test_accumulate_validation_errors(self):
        """Accumulate errors from multiple validation stages."""
        result = (
            ValidatedValue(0)
            .validate(is_positive)  # Fails
            .validate(is_even)  # Passes (0 is even)
        )
        assert result.is_invalid()
        assert "is_positive" in result.get_errors()[0]

    def test_map_with_exception_handling(self):
        """map should handle exceptions gracefully."""
        result = ValidatedValue(10)

        def raise_error(_x):
            raise ValueError("Test error")

        mapped = result.map(raise_error)
        assert mapped.is_invalid()
        assert "Map failed" in mapped.get_errors()

    def test_valid_to_invalid_transition(self):
        """Valid value can become invalid through validation."""
        result = ValidatedValue(5).validate(is_even)
        assert result.is_invalid()

    def test_invalid_remains_invalid(self):
        """Invalid value remains invalid through further validation."""
        result = ValidatedValue(3, errors=["Error"]).validate(is_positive)
        assert result.is_invalid()
        assert len(result.get_errors()) == 1  # No new errors added
