# Validation Builders - Declarative Validation

Build complex validation rules declaratively with composable validators.

## Overview

Validation builders enable:
- Declarative validation rules
- Composable validators
- Clear error messages
- Reusable validation logic
- Schema-based validation

## Basic Validation Builder

```python
from typing import Callable, Any, TypeVar, Generic

T = TypeVar('T')

class ValidationBuilder(Generic[T]):
    """Build validation rules step by step"""

    def __init__(self):
        self._validators: list[Callable[[T], bool]] = []
        self._error_messages: list[str] = []

    def required(self, message: str = "This field is required") -> 'ValidationBuilder[T]':
        """Value must be present"""
        self._validators.append(lambda x: x is not None and x != "")
        self._error_messages.append(message)
        return self

    def min_length(self, n: int, message: str = None) -> 'ValidationBuilder[T]':
        """Minimum length for strings/lists"""
        msg = message or f"Must be at least {n} characters"
        self._validators.append(lambda x: len(x) >= n if x else False)
        self._error_messages.append(msg)
        return self

    def max_length(self, n: int, message: str = None) -> 'ValidationBuilder[T]':
        """Maximum length for strings/lists"""
        msg = message or f"Must be at most {n} characters"
        self._validators.append(lambda x: len(x) <= n if x else False)
        self._error_messages.append(msg)
        return self

    def custom(self, predicate: Callable[[T], bool], message: str) -> 'ValidationBuilder[T]':
        """Custom validation rule"""
        self._validators.append(predicate)
        self._error_messages.append(message)
        return self

    def one_of(self, options: list, message: str = None) -> 'ValidationBuilder[T]':
        """Value must be one of the options"""
        msg = message or f"Must be one of: {', '.join(map(str, options))}"
        self._validators.append(lambda x: x in options)
        self._error_messages.append(msg)
        return self

    def validate(self, value: T) -> 'ValidationResult':
        """Run all validations"""
        errors = []

        for i, validator in enumerate(self._validators):
            if not validator(value):
                errors.append(self._error_messages[i])

        return ValidationResult(success=len(errors) == 0, errors=errors)


@dataclass
class ValidationResult:
    success: bool
    errors: list[str]

    @property
    def error_message(self) -> str | None:
        return "; ".join(self.errors) if self.errors else None


# === Usage ===

name_validator = (
    ValidationBuilder()
    .required()
    .min_length(2)
    .max_length(50)
)

result = name_validator.validate("Alice")
print(result.success)  # True

result = name_validator.validate("")
print(result.success)       # False
print(result.error_message) # "This field is required; Must be at least 2 characters"
```

## Email Validator

```python
class EmailValidator(ValidationBuilder[str]):
    """Specialized email validator"""

    def __init__(self):
        super().__init__()

    def email(self, message: str = "Invalid email format") -> 'EmailValidator':
        """Validate email format"""
        def is_email(value: str) -> bool:
            if not value:
                return False
            parts = value.split("@")
            if len(parts) != 2:
                return False
            local, domain = parts
            return "." in domain and len(local) > 0 and len(domain) > 0

        self._validators.append(is_email)
        self._error_messages.append(message)
        return self


# === Usage ===

email_validator = EmailValidator().email().required()

result = email_validator.validate("user@example.com")
print(result.success)  # True

result = email_validator.validate("invalid")
print(result.success)       # False
print(result.errors)        # ["Invalid email format"]
```

## Schema Validation

```python
from typing import TypedDict, Type, get_type_hints

class Field:
    """Schema field definition"""

    def __init__(
        self,
        type_hint: Type,
        required: bool = False,
        default: Any = None,
        validator: ValidationBuilder | None = None
    ):
        self.type_hint = type_hint
        self.required = required
        self.default = default
        self.validator = validator


class Schema:
    """Schema validator for dictionaries"""

    def __init__(self, **fields: Field):
        self.fields = fields

    def validate(self, data: dict) -> 'ValidationResult':
        """Validate entire schema"""
        errors = []

        for name, field in self.fields.items():
            value = data.get(name)

            # Check required
            if field.required and value is None:
                errors.append(f"{name} is required")
                continue

            # Skip other validations if None and not required
            if value is None:
                continue

            # Type check
            if not isinstance(value, field.type_hint):
                errors.append(f"{name} must be {field.type_hint.__name__}")
                continue

            # Custom validation
            if field.validator:
                result = field.validator.validate(value)
                if not result.success:
                    errors.extend([f"{name}: {e}" for e in result.errors])

        return ValidationResult(success=len(errors) == 0, errors=errors)


# === Usage ===

user_schema = Schema(
    name=Field(str, required=True, validator=ValidationBuilder().min_length(2)),
    email=Field(str, required=True, validator=EmailValidator().email()),
    age=Field(int, required=False, validator=ValidationBuilder().custom(lambda x: x >= 0, "Must be positive")),
    country=Field(str, required=False, default="US")
)

data = {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
}

result = user_schema.validate(data)
print(result.success)  # True

invalid_data = {
    "name": "A",
    "email": "invalid",
    "age": -5
}

result = user_schema.validate(invalid_data)
print(result.success)  # False
print(result.errors)
# ["name: Must be at least 2 characters", "email: Invalid email format", "age: Must be positive"]
```

## Async Validation

```python
class AsyncValidator(Generic[T]):
    """Async validation builder"""

    def __init__(self):
        self._validators: list[Callable[[T], Any]] = []
        self._error_messages: list[str] = []

    def custom_async(self, predicate: Callable[[T], Any], message: str) -> 'AsyncValidator[T]':
        """Add async validation rule"""
        self._validators.append(predicate)
        self._error_messages.append(message)
        return self

    async def validate(self, value: T) -> ValidationResult:
        """Run async validations"""
        errors = []

        for i, validator in enumerate(self._validators):
            result = validator(value)
            if isinstance(result, Awaitable):
                result = await result

            if not result:
                errors.append(self._error_messages[i])

        return ValidationResult(success=len(errors) == 0, errors=errors)


# === Usage ===

async def check_email_exists(email: str) -> bool:
    """Check if email already exists in database"""
    await asyncio.sleep(0.1)
    return email not in ["taken@example.com"]

email_validator = (
    AsyncValidator()
    .custom_async(lambda x: "@" in x, "Invalid format")
    .custom_async(check_email_exists, "Email already taken")
)

async def main():
    result = await email_validator.validate("new@example.com")
    print(result.success)  # True

asyncio.run(main())
```

## Nested Validation

```python
def validate_nested(data: dict, path: str, schema: Schema) -> ValidationResult:
    """Validate nested schema"""

    nested_data = data.get(path, {})
    result = schema.validate(nested_data)

    if not result.success:
        # Prefix errors with path
        errors = [f"{path}.{e}" for e in result.errors]
        return ValidationResult(success=False, errors=errors)

    return result


# === Usage ===

address_schema = Schema(
    street=Field(str, required=True),
    city=Field(str, required=True),
    country=Field(str, required=True)
)

user_schema_with_address = Schema(
    name=Field(str, required=True),
    address=Field(dict, required=True)
)

data = {
    "name": "Alice",
    "address": {
        "street": "123 Main St",
        "city": "Paris",
        "country": "France"
    }
}

result = user_schema_with_address.validate(data)
if result.success:
    # Also validate nested address
    address_result = address_schema.validate(data["address"])
    print(address_result.success)  # True
```

## Validation with Result Type

```python
from typing import TypeVar, Generic

E = TypeVar('E')

class Validated:
    """Helper for chaining validation with Result"""

    @staticmethod
    def from_result(result: ValidationResult) -> Result:
        """Convert validation result to Result type"""
        if result.success:
            return Result.ok(result.data)
        return Result.error(result.errors)


# === Usage ===

def register_user(data: dict) -> Result[User, list[str]]:
    """Register user with validation"""

    # Validate
    result = user_schema.validate(data)
    if not result.success:
        return Result.error(result.errors)

    # Create user
    user = User(
        name=data["name"],
        email=data["email"],
        age=data.get("age", 0)
    )

    return Result.ok(user)


match register_user(user_data):
    case Ok(user):
        return {"success": True, "user": user}
    case Error(errors):
        return {"success": False, "errors": errors}
```

## Field Validators Library

```python
class Validators:
    """Common validators"""

    @staticmethod
    def email() -> ValidationBuilder:
        return EmailValidator().email()

    @staticmethod
    def url() -> ValidationBuilder:
        return ValidationBuilder().custom(
            lambda x: x.startswith(("http://", "https://")),
            "Must be a valid URL"
        )

    @staticmethod
    def positive() -> ValidationBuilder:
        return ValidationBuilder().custom(
            lambda x: x > 0,
            "Must be positive"
        )

    @staticmethod
    def non_negative() -> ValidationBuilder:
        return ValidationBuilder().custom(
            lambda x: x >= 0,
            "Must be non-negative"
        )

    @staticmethod
    def range(min_val: int, max_val: int) -> ValidationBuilder:
        return ValidationBuilder().custom(
            lambda x: min_val <= x <= max_val,
            f"Must be between {min_val} and {max_val}"
        )

    @staticmethod
    def matches(pattern: str, message: str = None) -> ValidationBuilder:
        import re
        regex = re.compile(pattern)
        msg = message or f"Must match pattern: {pattern}"
        return ValidationBuilder().custom(
            lambda x: bool(regex.match(x)),
            msg
        )


# === Usage ===

password_validator = (
    ValidationBuilder()
    .min_length(8, "Password too short")
    .custom(Validators.matches(r".*[A-Z].*"), "Must contain uppercase")
    .custom(Validators.matches(r".*[0-9].*"), "Must contain number")
)
```

## DX Benefits

✅ **Declarative**: Rules defined declaratively
✅ **Reusable**: Share validators across project
✅ **Composable**: Combine multiple validators
✅ **Clear errors**: Helpful error messages
✅ **Type-safe**: Works with static type checkers

## Best Practices

```python
# ✅ Good: Reusable validators
email_validator = EmailValidator().email()

# ✅ Good: Descriptive error messages
.min_length(2, "Name too short")

# ✅ Good: Compose complex validators
password = (ValidationBuilder()
    .min_length(8)
    .custom(has_uppercase, "Need uppercase")
    .custom(has_number, "Need number"))

# ❌ Bad: Vague errors
.custom(lambda x: x > 0, "Invalid")

# ❌ Bad: Too much in one validator
# Break into smaller, named validators
```
