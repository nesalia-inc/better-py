# Validation - Accumulate Errors

Accumulate multiple validation errors using composable validator classes.

## Overview

`Validation` accumulates errors instead of failing on first error:
- `Success(value)` - All validations passed
- `Errors(exceptions)` - One or more validation failures (Exception objects)

## Protocol-Based Design

```python
from typing import Protocol, TypeVar, Generic, Type, runtime_checkable
from abc import abstractmethod

T = TypeVar('T')

@runtime_checkable
class Validator(Protocol[T]):
    """Protocol for validators - compile-time and runtime checkable"""

    def validate(self, value: T) -> Validation:
        """Validate value and return Validation result"""
        ...


@dataclass
class Validation:
    """Validation result"""

    value: Any | None
    errors: list[Exception]

    def is_success(self) -> bool:
        return len(self.errors) == 0

    def is_errors(self) -> bool:
        return len(self.errors) > 0

    def get(self) -> T:
        if self.is_errors():
            raise ValueError(f"Cannot get value from failed validation")
        return self.value

    @classmethod
    def success(cls, value: T) -> 'Validation':
        return cls(value, [])

    @classmethod
    def errors_(cls, *errors: Exception) -> 'Validation':
        return cls(None, list(errors))

    def accumulate(self, other: 'Validation') -> 'Validation':
        """Accumulate errors from another Validation"""

        return Validation(
            self.value if self.is_success() else other.value,
            self.errors + other.errors
        )
```

## Base Validator Class

```python
class BaseValidator(Generic[T]):
    """Base class for validators"""

    def __init__(self):
        self._validators: list[Callable[[T], Exception | None]] = []

    def validate(self, value: T) -> Validation:
        """Run all validation rules"""

        errors = []

        for validator in self._validators:
            error = validator(value)
            if error is not None:
                errors.append(error)

        if errors:
            return Validation.errors_(*errors)

        return Validation.success(value)

    def __call__(self, value: T) -> Validation:
        """Convenient: validator(value) instead of validator.validate(value)"""
        return self.validate(value)

    def add_rule(self, predicate: Callable[[T], bool], error: Exception) -> 'BaseValidator[T]':

        def rule(value: T):
            if not predicate(value):
                return error
            return None

        self._validators.append(rule)
        return self
```

## Concrete Validator Classes

```python
class StringValidator(BaseValidator[str]):
    """Validator for string values"""

    @classmethod
    def create(cls) -> 'StringValidator':
        return cls()

    def min_length(self, n: int, error_type: Type[Exception] = ValidationError) -> 'StringValidator':
        """Minimum length validation"""

        def predicate(value: str):
            return len(value) >= n

        return self.add_rule(
            predicate,
            error_type(f"String must be at least {n} characters")
        )

    def max_length(self, n: int, error_type: Type[Exception] = ValidationError) -> 'StringValidator':
        """Maximum length validation"""

        def predicate(value: str):
            return len(value) <= n

        return self.add_rule(
            predicate,
            error_type(f"String must be at most {n} characters")
        )

    def matches(self, pattern: str, error_type: Type[Exception] = ValidationError) -> 'StringValidator':
        """Regex match validation"""

        import re
        regex = re.compile(pattern)

        def predicate(value: str):
            return bool(regex.match(value))

        return self.add_rule(
            predicate,
            error_type(f"String must match pattern: {pattern}")
        )

    def contains(self, substring: str, error_type: Type[Exception] = ValidationError) -> 'StringValidator':
        """Contains substring validation"""

        def predicate(value: str):
            return substring in value

        return self.add_rule(
            predicate,
            error_type(f"String must contain '{substring}'")
        )

    def email(self, error_type: Type[Exception] = ValidationError) -> 'StringValidator':
        """Email format validation"""

        def predicate(value: str) -> bool:
            parts = value.split("@")
            if len(parts) != 2:
                return False
            local, domain = parts
            return "." in domain and len(local) > 0 and len(domain) > 0

        return self.add_rule(predicate, error_type("Invalid email format"))


# === Usage ===
name_validator = (
    StringValidator.create()
    .min_length(2)
    .max_length(50)
    .matches(r"^[a-zA-Z\s]+$")
)

result = name_validator.validate("Alice")
# Validation.success({"name": "Alice"})

result = name_validator.validate("A")
# Validation.errors_(ValidationError("String must be at least 2 characters"))
```

## Integer Validator

```python
class IntValidator(BaseValidator[int]):
    """Validator for integer values"""

    @classmethod
    def create(cls) -> 'IntValidator':
        return cls()

    def positive(self, error_type: Type[Exception] = ValidationError) -> 'IntValidator':
        """Must be positive"""

        return self.add_rule(
            lambda x: x > 0,
            error_type("Must be positive")
        )

    def non_negative(self, error_type: Type[Exception] = ValidationError) -> 'IntValidator':
        """Must be non-negative"""

        return self.add_rule(
            lambda x: x >= 0,
            error_type("Must be non-negative")
        )

    def range(self, min_val: int, max_val: int, error_type: Type[Exception] = ValidationError) -> 'IntValidator':
        """Must be in range [min_val, max_val]"""

        def predicate(value: int):
            return min_val <= value <= max_val

        return self.add_rule(
            predicate,
            error_type(f"Must be between {min_val} and {max_val}")
        )

    def one_of(self, *options: int, error_type: Type[Exception] = ValidationError) -> 'IntValidator':
        """Must be one of the options"""

        return self.add_rule(
            lambda x: x in options,
            error_type(f"Must be one of: {options}")
        )


# === Usage ===
age_validator = (
    IntValidator.create()
    .range(18, 120)
    .one_of(18, 21, 25, 30, 40, 50, 60, 65)
)

result = age_validator.validate(25)
# Validation.success(25)
```

## Dict Validator

```python
class DictValidator(BaseValidator[dict]):
    """Validator for dictionaries"""

    @classmethod
    def create(cls) -> 'DictValidator':
        return cls()

    def required_keys(self, *keys: str, error_type: Type[Exception] = ValidationError) -> 'DictValidator':
        """Require specific keys"""

        def predicate(value: dict):
            return all(key in value for key in keys)

        return self.add_rule(
            predicate,
            error_type(f"Missing required keys: {keys}")
        )

    def key_type(self, key: str, expected_type: Type, error_type: Type[Exception] = ValidationError) -> 'DictValidator':
        """Key must be of specific type"""

        def predicate(value: dict):
            if key not in value:
                return True  # Missing keys handled separately
            return isinstance(value[key], expected_type)

        return self.add_rule(
            predicate,
            error_type(f"Key '{key}' must be {expected_type.__name__}")
        )

    def nested(self, key: str, validator: Validator, error_type: Type[Exception] = ValidationError) -> 'DictValidator':
        """Validate nested dictionary using another validator"""

        def predicate(value: dict):
            if key not in value:
                return True  # Missing keys handled separately
            result = validator.validate(value[key])
            return result.is_success()

        def rule(value: dict):
            if key not in value:
                return error_type(f"Missing key: {key}")
            result = validator.validate(value[key])
            if result.is_errors():
                return result.errors[0]  # Return first error
            return None

        self._validators.append(rule)
        return self


# === Usage ===
user_data_validator = (
    DictValidator.create()
    .required_keys("name", "email")
    .key_type("age", int)
)

result = user_data_validator.validate({
    "name": "Alice",
    "email": "alice@example.com"
})

result = user_data_validator.validate({"name": "Bob"})
# Validation.errors_(ValidationError("Missing required keys: ('email',)"))
```

## Field Validator Builder

```python
class FieldValidator(Generic[T]):
    """Fluent builder for field validation"""

    def __init__(self, field_name: str, value: T | None = None):
        self.field_name = field_name
        self._value = value
        self._validator: BaseValidator[T] | None = None
        self._required: bool = False

    def of_type(self, validator: BaseValidator[T]) -> 'FieldValidator[T]':
        """Set validator for this field"""
        self._validator = validator
        return self

    def required(self, error_type: Type[Exception] = ValidationError) -> 'FieldValidator[T]':
        """Mark field as required"""

        self._required = True

        if self._validator:
            def rule(value):
                if value is None or value == "":
                    return error_type(f"Field '{self.field_name}' is required")
                return None

            # Run validator
            result = self._validator.validate(value)
            return result.errors[0] if result.is_errors() else None

            self._validator.add_rule(rule, error_type("dummy"))

        return self

    def validate(self) -> Validation:

        value = self._value

        # Check required
        if self._required and (value is None or value == ""):
            return Validation.errors_(ValidationError(f"Field '{self.field_name}' is required"))

        # Run validator if present
        if self._validator and value is not None:
            return self._validator.validate(value)

        return Validation.success(value)
```

## Schema Builder Class

```python
class ValidationSchema:
    """Schema for validating complete data structures"""

    def __init__(self):
        self._fields: dict[str, FieldValidator] = {}

    def field(self, name: str, value: Any = None) -> FieldValidator:
        """Add or get field validator"""

        if name not in self._fields:
            field = FieldValidator(name, value)
            self._fields[name] = field
        else:
            field = self._fields[name]
            if value is not None:
                field._value = value

        return field

    def validate(self, data: dict) -> Validation:

        # Update field values
        for name, field in self._fields.items():
            if name in data:
                field._value = data[name]

        # Validate all fields
        all_errors = []

        for field_name, field in self._fields.items():
            result = field.validate()
            all_errors.extend([
                error for error in result.errors
                if error is not None
            ])

        if all_errors:
            return Validation.errors_(*all_errors)

        # Build validated data
        validated_data = {
            name: field.validate().get()
            for name, field in self._fields.items()
        }

        return Validation.success(validated_data)


# === Usage ===
schema = ValidationSchema()

(
    schema
    .field("name", "A")
    .of_type(StringValidator.create().min_length(2).max_length(50))
    .required()
)

(
    schema
    .field("email")
    .of_type(StringValidator.create().email())
    .required()
)

(
    schema
    .field("age", 25)
    .of_type(IntValidator.create().range(18, 120))
)

result = schema.validate({
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
})

# Validation.success({"name": "Alice", "email": "alice@example.com", "age": 25})
```

## Custom Exception Classes

```python
# Define domain-specific exceptions
class DomainException(Exception):
    """Base exception for domain"""
    pass

class FieldRequired(DomainException):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Field '{field}' is required")

class InvalidFormat(DomainException):
    def __init__(self, field: str, expected: str):
        self.field = field
        self.expected = expected
        super().__init__(f"Field '{field}' must be {expected}")

class OutOfRange(DomainException):
    def __init__(self, field: str, min_val: int, max_val: int, actual: int):
        self.field = field
        self.min_val = min_val
        self.max_val = max_val
        self.actual = actual
        super().__init__(f"Field '{field}' value {actual} not in range [{min_val}, {max_val}]")


# Use custom exceptions with validators
class TypedStringValidator(StringValidator):
    """String validator with custom exceptions"""

    def min_length(self, n: int) -> 'TypedStringValidator':

        def predicate(value: str):
            return len(value) >= n

        return self.add_rule(
            predicate,
            InvalidFormat("string", f"at least {n} characters")
        )

    def matches_email(self) -> 'TypedStringValidator':

        def predicate(value: str):
            parts = value.split("@")
            return len(parts) == 2 and "." in parts[1]

        return self.add_rule(
            predicate,
            InvalidFormat("string", "valid email format")
        )


# === Usage ===
email_validator = TypedStringValidator.create().min_length(5).matches_email()

result = email_validator.validate("test")
# Validation.errors_(InvalidFormat("string", "valid email format"))
```

## Composable Validation Mixins

```python
class RequiredMixin:
    """Mixin for required field validation"""

    def required(self, error_type: Type[Exception] = FieldRequired) -> BaseValidator[T]:

        def rule(value: T):
            if value is None or (isinstance(value, str) and not value):
                return error_type(self._field_name if hasattr(self, '_field_name') else 'value')
            return None

        self._validators.append(rule)
        return self


class EmailValidationMixin:
    """Mixin for email validation methods"""

    def is_email(self, error_type: Type[Exception] = InvalidFormat) -> BaseValidator[str]:

        def predicate(value: str):
            parts = value.split("@")
            return len(parts) == 2 and "." in parts[1]

        return self.add_rule(
            predicate,
            error_type("string", "valid email format")
        )


class SmartStringValidator(RequiredMixin, EmailValidationMixin, StringValidator):
    """String validator with mixins - multiple inheritance"""

    def __init__(self, field_name: str):
        super().__init__()
        self._field_name = field_name


# === Usage ===
email_field = SmartStringValidator("email").required().is_email()

result = email_field.validate("")
# Validation.errors_(FieldRequired("email"))

result = email_field.validate("invalid")
# Validation.errors_(InvalidFormat("string", "valid email format"))
```

## DX Benefits

✅ **OOP design**: Validators as classes with inheritance
✅ **Protocol compliance**: `Validator[T]` for type checking
✅ **Reusable**: Create validators once, use everywhere
✅ **Composable**: Chain validation rules fluently
✅ **Type-safe**: Full generic typing support
✅ **Autocompletion**: IDE shows available methods
✅ **Custom exceptions**: Structured error objects

## Best Practices

```python
# ✅ Good: Class-based validators
class UserValidator(BaseValidator[dict]):
    pass

# ✅ Good: Protocol compliance
class Validator(Protocol[T]):
    def validate(self, value: T) -> Validation: ...

# ✅ Good: Inheritance and mixins
class SmartValidator(RequiredMixin, BaseValidator):
    pass

# ✅ Good: Custom exception classes
class UserNotFound(DomainException):
    def __init__(self, user_id: int):
        self.user_id = user_id

# ❌ Bad: Function-based validators
# Use classes for better OOP design

# ❌ Bad: Generic exceptions
# Use specific exception types with attributes
```
