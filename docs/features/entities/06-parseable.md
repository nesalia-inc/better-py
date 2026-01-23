# Parseable: Parse Text to Typed Values

**Parseable** is a protocol for objects that can be **parsed from text** - converting strings into typed values with proper error handling.

## Overview

```python
@runtime_checkable
class Parseable(Protocol[T]):
    """Objects that can be parsed from text"""

    @classmethod
    def parse(cls, text: str) -> Result[T, ParseError]:
        """Parse from string"""
        ...

    @classmethod
    def try_parse(cls, text: str) -> Maybe[T]:
        """Try parsing, return None on failure"""
        ...
```

## Core Concepts

### Parse vs Try Parse

```python
# parse: Returns Result with error details
result = ParseableInt.parse("42")
# Ok(42)

result = ParseableInt.parse("invalid")
# Error(ParseError("Invalid integer: invalid"))

# try_parse: Returns Maybe (no error info)
result = ParseableInt.try_parse("42")
# Some(42)

result = ParseableInt.try_parse("invalid")
# None_
```

## Implementations

### ParseableInt

```python
@dataclass(frozen=True, slots=True)
class ParseableInt:
    """Parseable integer"""

    value: int

    @classmethod
    def parse(cls, text: str) -> Result['ParseableInt', ParseError]:
        """Parse integer from string"""
        try:
            return Ok(cls(int(text)))
        except ValueError as e:
            return Error(ParseError(f"Invalid integer: {text}", text))

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableInt]':
        """Try parsing, return None on failure"""
        try:
            return Some(cls(int(text)))
        except ValueError:
            return None_

    @classmethod
    def parse_with_range(
        cls,
        text: str,
        min_val: int | None = None,
        max_val: int | None = None
    ) -> Result['ParseableInt', ParseError]:
        """Parse integer with range validation"""

        result = cls.parse(text)
        if result.is_error():
            return result

        value = result.unwrap().value

        if min_val is not None and value < min_val:
            return Error(ParseError(f"Integer {value} below minimum {min_val}", text))

        if max_val is not None and value > max_val:
            return Error(ParseError(f"Integer {value} above maximum {max_val}", text))

        return Ok(cls(value))

    def to_int(self) -> int:
        return self.value

    def __int__(self) -> int:
        return self.value
```

#### Usage Examples

```python
# Parse
result = ParseableInt.parse("42")
if result.is_ok():
    value = result.unwrap()
    print(value.value)  # 42

# Parse error
result = ParseableInt.parse("invalid")
if result.is_error():
    error = result.error
    print(error.message)  # "Invalid integer: invalid"

# Try parse
maybe = ParseableInt.try_parse("42")
if maybe.is_some():
    value = maybe.unwrap()
    print(value.value)  # 42

# With range
result = ParseableInt.parse_with_range("42", min_val=1, max_val=100)
# Ok(ParseableInt(42))

result = ParseableInt.parse_with_range("150", min_val=1, max_val=100)
# Error(ParseError("Integer 150 above maximum 100"))
```

### ParseableFloat

```python
@dataclass(frozen=True, slots=True)
class ParseableFloat:
    """Parseable float"""

    value: float

    @classmethod
    def parse(cls, text: str) -> Result['ParseableFloat', ParseError]:
        """Parse float from string"""
        try:
            return Ok(cls(float(text)))
        except ValueError as e:
            return Error(ParseError(f"Invalid float: {text}", text))

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableFloat]':
        """Try parsing, return None on failure"""
        try:
            return Some(cls(float(text)))
        except ValueError:
            return None_

    def to_float(self) -> float:
        return self.value

    def __float__(self) -> float:
        return self.value
```

#### Usage Examples

```python
result = ParseableFloat.parse("3.14")
# Ok(ParseableFloat(3.14))

result = ParseableFloat.parse("invalid")
# Error(ParseError("Invalid float: invalid"))
```

### ParseableBool

```python
@dataclass(frozen=True, slots=True)
class ParseableBool:
    """Parseable boolean"""

    value: bool

    # Accepted values
    TRUE_VALUES = {"true", "1", "yes", "on", "t", "y"}
    FALSE_VALUES = {"false", "0", "no", "off", "f", "n"}

    @classmethod
    def parse(cls, text: str) -> Result['ParseableBool', ParseError]:
        """Parse boolean from string"""
        normalized = text.strip().lower()

        if normalized in cls.TRUE_VALUES:
            return Ok(cls(True))

        if normalized in cls.FALSE_VALUES:
            return Ok(cls(False))

        return Error(ParseError(
            f"Invalid boolean: {text} (expected: {', '.join(sorted(cls.TRUE_VALUES | cls.FALSE_VALUES))})",
            text
        ))

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableBool]':
        """Try parsing, return None on failure"""
        result = cls.parse(text)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

    def to_bool(self) -> bool:
        return self.value

    def __bool__(self) -> bool:
        return self.value
```

#### Usage Examples

```python
result = ParseableBool.parse("true")
# Ok(ParseableBool(True))

result = ParseableBool.parse("yes")
# Ok(ParseableBool(True))

result = ParseableBool.parse("0")
# Ok(ParseableBool(False))

result = ParseableBool.parse("invalid")
# Error(ParseError("Invalid boolean: invalid ..."))
```

### ParseableEmail

```python
import re

@dataclass(frozen=True, slots=True)
class ParseableEmail:
    """Parseable email address"""

    value: str
    local: str
    domain: str

    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    )

    @classmethod
    def parse(cls, text: str) -> Result['ParseableEmail', ParseError]:
        """Parse email from string"""
        if not cls.EMAIL_REGEX.match(text):
            return Error(ParseError(f"Invalid email format: {text}", text))

        local, domain = text.split("@")
        return cls(text, local, domain)

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableEmail]':
        """Try parsing, return None on failure"""
        result = cls.parse(text)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

    def is_free_email(self) -> bool:
        """Check if using free email provider"""
        free_domains = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}
        return self.domain.lower() in free_domains

    def to_str(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value
```

#### Usage Examples

```python
result = ParseableEmail.parse("user@example.com")
# Ok(ParseableEmail(value="user@example.com", local="user", domain="example.com"))

email = result.unwrap()
print(email.local)   # "user"
print(email.domain)  # "example.com"
print(email.is_free_email())  # False

result = ParseableEmail.parse("invalid")
# Error(ParseError("Invalid email format: invalid"))
```

### ParseableURL

```python
from urllib.parse import urlparse

@dataclass(frozen=True, slots=True)
class ParseableURL:
    """Parseable URL"""

    value: str
    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @classmethod
    def parse(cls, text: str) -> Result['ParseableURL', ParseError]:
        """Parse URL from string"""
        try:
            parsed = urlparse(text)

            if not parsed.scheme or not parsed.netloc:
                return Error(ParseError(f"Invalid URL: {text}", text))

            return cls(
                text,
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            )
        except Exception as e:
            return Error(ParseError(f"Invalid URL: {text}", text))

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableURL]':
        """Try parsing, return None on failure"""
        result = cls.parse(text)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

    def is_secure(self) -> bool:
        """Check if using HTTPS"""
        return self.scheme == "https"

    def is_absolute(self) -> bool:
        """Check if absolute URL"""
        return bool(self.netloc)

    def to_str(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value
```

#### Usage Examples

```python
result = ParseableURL.parse("https://example.com/path?query=value#frag")
# Ok(ParseableURL(...))

url = result.unwrap()
print(url.scheme)   # "https"
print(url.netloc)   # "example.com"
print(url.path)     # "/path"
print(url.is_secure())  # True
```

### ParseableDate

```python
from datetime import datetime

@dataclass(frozen=True, slots=True)
class ParseableDate:
    """Parseable date"""

    value: datetime
    format: str

    @classmethod
    def parse(cls, text: str, format: str = "%Y-%m-%d") -> Result['ParseableDate', ParseError]:
        """Parse date from string"""
        try:
            value = datetime.strptime(text, format)
            return cls(value, format)
        except ValueError as e:
            return Error(ParseError(f"Invalid date ({format}): {text}", text))

    @classmethod
    def try_parse(cls, text: str, format: str = "%Y-%m-%d") -> 'Maybe[ParseableDate]':
        """Try parsing, return None on failure"""
        result = cls.parse(text, format)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

    @classmethod
    def parse_iso(cls, text: str) -> Result['ParseableDate', ParseError]:
        """Parse ISO 8601 date"""
        return cls.parse(text, "%Y-%m-%dT%H:%M:%S")

    def to_datetime(self) -> datetime:
        return self.value

    def format_date(self, format: str) -> str:
        """Format date to string"""
        return self.value.strftime(format)

    def __str__(self) -> str:
        return self.format_date(self.format)
```

#### Usage Examples

```python
result = ParseableDate.parse("2024-01-15")
# Ok(ParseableDate(datetime(2024, 1, 15), "%Y-%m-%d"))

date = result.unwrap()
print(date.format_date("%d/%m/%Y"))  # "15/01/2024"

# ISO format
result = ParseableDate.parse_iso("2024-01-15T10:30:00")
# Ok(ParseableDate(datetime(2024, 1, 15, 10, 30, 0), "%Y-%m-%dT%H:%M:%S"))
```

### ParseableJSON

```python
import json

@dataclass(frozen=True, slots=True)
class ParseableJSON:
    """Parseable JSON"""

    value: Any
    raw: str

    @classmethod
    def parse(cls, text: str) -> Result['ParseableJSON', ParseError]:
        """Parse JSON from string"""
        try:
            value = json.loads(text)
            return cls(value, text)
        except json.JSONDecodeError as e:
            return Error(ParseError(f"Invalid JSON: {e.msg}", text))

    @classmethod
    def try_parse(cls, text: str) -> 'Maybe[ParseableJSON]':
        """Try parsing, return None on failure"""
        result = cls.parse(text)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from dict"""
        if isinstance(self.value, dict):
            return self.value.get(key, default)
        return default

    def to_python(self) -> Any:
        """Get Python object"""
        return self.value

    def __str__(self) -> str:
        return self.raw
```

#### Usage Examples

```python
result = ParseableJSON.parse('{"name": "Alice", "age": 30}')
# Ok(ParseableJSON({"name": "Alice", "age": 30}, '{"name": "Alice", "age": 30}'))

json_obj = result.unwrap()
print(json_obj.get("name"))  # "Alice"
print(json_obj.get("age"))   # 30
```

## Advanced Patterns

### Multi-format Parsing

```python
@dataclass(frozen=True, slots=True)
class ParseableDate:
    value: datetime

    @classmethod
    def parse_auto(cls, text: str) -> Result['ParseableDate', ParseError]:
        """Try multiple formats"""
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in formats:
            result = cls.parse(text, fmt)
            if result.is_ok():
                return result

        return Error(ParseError(
            f"Could not parse date with any format: {text}",
            text
        ))
```

### Custom Validation

```python
@dataclass(frozen=True, slots=True)
class ParseableEmail:
    value: str

    @classmethod
    def parse_with_validation(
        cls,
        text: str,
        allowed_domains: set[str] | None = None,
        require_tls: bool = False
    ) -> Result['ParseableEmail', ParseError]:
        """Parse with custom validation"""

        result = cls.parse(text)
        if result.is_error():
            return result

        email = result.unwrap()
        domain = email.value.split("@")[1]

        if allowed_domains and domain not in allowed_domains:
            return Error(ParseError(
                f"Domain {domain} not in allowed domains",
                text
            ))

        if require_tls and not email.is_provider_supports_tls():
            return Error(ParseError(
                f"Provider {domain} does not support TLS",
                text
            ))

        return Ok(email)
```

### Combinator Parsing

```python
def parse_sequence(
    text: str,
    parsers: list[Callable[[str], Result[tuple, ParseError]]]
) -> Result[list, ParseError]:
    """Parse sequence of values"""

    results = []
    remaining = text.strip()

    for parser in parsers:
        result = parser(remaining)
        if result.is_error():
            return Error(result.error)

        value, remaining = result.unwrap()
        results.append(value)

    return Ok(results)

# Usage
def parse_int(text: str) -> Result[tuple[int, str], ParseError]:
    match = re.match(r'^\s*(\d+)(.*)', text)
    if not match:
        return Error(ParseError(f"Expected integer", text))
    value = int(match.group(1))
    remaining = match.group(2)
    return Ok((value, remaining))

result = parse_sequence("123 456 789", [parse_int, parse_int, parse_int])
# Ok([123, 456, 789])
```

## Protocol Compliance

```python
@runtime_checkable
class Parseable(Protocol[T]):
    @classmethod
    def parse(cls, text: str) -> Result[T, ParseError]: ...
    @classmethod
    def try_parse(cls, text: str) -> Maybe[T]: ...

class CustomParseable:
    def __init__(self, value):
        self.value = value

    @classmethod
    def parse(cls, text: str):
        try:
            return cls(cls._convert(text))
        except Exception as e:
            return Error(ParseError(str(e), text))

    @classmethod
    def try_parse(cls, text: str):
        result = cls.parse(text)
        if result.is_ok():
            return Some(result.unwrap())
        return None_

# CustomParseable is Parseable!
isinstance(CustomParseable, Parseable)  # True
```

## Best Practices

### ✅ Do: Provide detailed error messages

```python
# Good: Includes original text and expected format
return Error(ParseError(f"Invalid integer: {text}", text))
```

### ✅ Do: Support multiple formats

```python
# Good: Try common formats
ParseableDate.parse_auto("2024-01-15")  # OK
ParseableDate.parse_auto("15/01/2024")  # OK
```

### ❌ Don't: Hide parse errors

```python
# Bad: Silent failure
def parse(text):
    try:
        return int(text)
    except:
        return 0  # Lost error info!

# Good: Explicit error
def parse(text):
    try:
        return Ok(int(text))
    except ValueError:
        return Error(ParseError(f"Invalid int: {text}", text))
```

## Summary

**Parseable** protocol:
- ✅ Parse strings to typed values
- ✅ `parse()` - Returns Result with errors
- ✅ `try_parse()` - Returns Maybe (no errors)
- ✅ Built-in types: Int, Float, Bool, Email, URL, Date, JSON
- ✅ Custom validation support

**Key benefit**: **Type-safe parsing** with **explicit error handling**.

---

**Next**: See [Validable](./07-validable.md) for validable entities.
