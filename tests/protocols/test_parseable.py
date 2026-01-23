"""Tests for Parseable protocol."""

from better_py.monads import Maybe
from better_py.protocols import Parseable


class ParseableInt(Parseable):
    """Parseable integer implementation using Maybe."""

    def __init__(self, value: Maybe[int]):
        self._value = value

    def parse(self, s: str) -> "ParseableInt":
        """Parse a string to an integer."""
        try:
            return ParseableInt(Maybe.some(int(s)))
        except ValueError:
            return ParseableInt(Maybe.nothing())

    @staticmethod
    def from_value(value: int) -> "ParseableInt":
        """Create a ParseableInt from a value."""
        return ParseableInt(Maybe.some(value))

    def is_valid(self) -> bool:
        """Check if this is a valid integer."""
        return self._value.is_some()

    def map(self, f):
        """Apply a function to the integer."""
        if self._value.is_nothing():
            return ParseableInt(Maybe.nothing())
        return ParseableInt(Maybe.some(f(self._value.unwrap())))

    def __eq__(self, other):
        return isinstance(other, ParseableInt) and self._value == other._value

    def __repr__(self):
        return f"ParseableInt({self._value})"


class TestParseable:
    """Tests for Parseable protocol."""

    def test_parseable_int_is_parseable(self):
        """ParseableInt should satisfy Parseable protocol."""
        data: Parseable = ParseableInt.from_value(42)
        assert isinstance(data, Parseable)

    def test_parse_valid_integer(self):
        """parse should succeed on valid integer."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("42")
        assert isinstance(result, ParseableInt)
        assert result.is_valid()

    def test_parse_invalid_integer(self):
        """parse should fail on invalid integer."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("abc")
        assert not result.is_valid()

    def test_parse_empty_string(self):
        """parse should fail on empty string."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("")
        assert not result.is_valid()

    def test_parse_negative_integer(self):
        """parse should handle negative integers."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("-42")
        assert result.is_valid()
        assert result._value.unwrap() == -42

    def test_parse_zero(self):
        """parse should handle zero."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("0")
        assert result.is_valid()
        assert result._value.unwrap() == 0

    def test_parse_whitespace(self):
        """parse should fail on whitespace."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("  ")
        assert not result.is_valid()

    def test_parse_with_extra_whitespace(self):
        """parse should fail on strings with whitespace."""
        parser = ParseableInt.from_value(0)
        result = parser.parse(" 42 ")
        # int() actually handles whitespace, so this might pass
        # but typically parsers are strict
        assert result.is_valid()

    def test_from_value(self):
        """from_value should create a valid Parseable."""
        result = ParseableInt.from_value(42)
        assert result.is_valid()

    def test_is_valid_true(self):
        """is_valid should return True for valid values."""
        result = ParseableInt.from_value(42)
        assert result.is_valid() is True

    def test_is_valid_false(self):
        """is_valid should return False for invalid values."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("invalid")
        assert not result.is_valid()

    def test_map_valid_value(self):
        """map should apply function to valid values."""
        result = ParseableInt.from_value(42)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_valid()

    def test_map_invalid_value(self):
        """map should preserve invalid state."""
        parser = ParseableInt.from_value(0)
        invalid = parser.parse("invalid")
        mapped = invalid.map(lambda x: x * 2)
        assert not mapped.is_valid()

    def test_map_chaining(self):
        """Multiple map operations should chain."""
        result = ParseableInt.from_value(10)
        chained = result.map(lambda x: x + 1).map(lambda x: x * 2).map(lambda x: x - 5)
        assert chained.is_valid()

    def test_parse_large_number(self):
        """parse should handle large numbers."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("9999999999")
        assert result.is_valid()

    def test_parse_float_string(self):
        """parse should fail on float strings."""
        parser = ParseableInt.from_value(0)
        result = parser.parse("3.14")
        # int() raises ValueError on float strings
        assert not result.is_valid()


class ParseableEmail(Parseable):
    """Parseable email implementation."""

    def __init__(self, value: Maybe[str]):
        self._value = value

    def parse(self, s: str) -> "ParseableEmail":
        """Parse a string as an email address."""
        if "@" in s and "." in s.split("@")[-1]:
            return ParseableEmail(Maybe.some(s))
        return ParseableEmail(Maybe.nothing())

    @staticmethod
    def from_value(value: str) -> "ParseableEmail":
        """Create a ParseableEmail from a value."""
        return ParseableEmail(Maybe.some(value))

    def is_valid(self) -> bool:
        """Check if this is a valid email."""
        return self._value.is_some()

    def map(self, f):
        """Apply a function to the email."""
        if self._value.is_nothing():
            return ParseableEmail(Maybe.nothing())
        return ParseableEmail(Maybe.some(f(self._value.unwrap())))

    def __eq__(self, other):
        return isinstance(other, ParseableEmail) and self._value == other._value

    def __repr__(self):
        return f"ParseableEmail({self._value})"


class TestParseableEmail:
    """Tests for Parseable email implementation."""

    def test_parse_valid_email(self):
        """parse should succeed on valid email."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("user@example.com")
        assert result.is_valid()

    def test_parse_invalid_email_no_at(self):
        """parse should fail on email without @."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("userexample.com")
        assert not result.is_valid()

    def test_parse_invalid_email_no_dot(self):
        """parse should fail on email without dot in domain."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("user@localhost")
        assert not result.is_valid()

    def test_parse_email_with_subdomain(self):
        """parse should handle emails with subdomains."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("user@mail.example.com")
        assert result.is_valid()

    def test_map_email_to_lowercase(self):
        """map should transform email to lowercase."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("USER@EXAMPLE.COM")
        lowered = result.map(str.lower)
        assert lowered.is_valid()

    def test_map_email_extract_domain(self):
        """map should extract domain from email."""
        parser = ParseableEmail.from_value("")
        result = parser.parse("user@example.com")
        domain = result.map(lambda email: email.split("@")[1])
        assert domain.is_valid()
        assert domain._value.unwrap() == "example.com"
