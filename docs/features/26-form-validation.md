# Form/Schema Validation - Data Shape Validation

Validate form data and schemas with type checking and custom rules.

## Overview

Form validation enables:
- Declarative validation rules
- Nested schema validation
- Custom validators
- Clear error messages
- Type coercion

## Field Definition

```python
from typing import Any, Callable, Type, Generic
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Field:
    """Schema field definition"""

    name: str
    type: Type
    required: bool = False
    default: Any = None
    validator: Callable | None = None
    coerce: Callable | None = None


@dataclass
class FieldError:
    """Field validation error"""

    field: str
    message: str
    value: Any


@dataclass
class ValidationResult:
    """Validation result"""

    valid: bool
    errors: list[FieldError]
    data: dict | None

    @property
    def error_messages(self) -> dict[str, str]:
        """Get errors as dict"""

        return {e.field: e.message for e in self.errors}


# === Usage ===

name_field = Field(
    name="name",
    type=str,
    required=True,
    validator=lambda x: len(x) >= 2
)

age_field = Field(
    name="age",
    type=int,
    required=False,
    default=18,
    validator=lambda x: x >= 0
)
```

## Schema Builder

```python
class Schema:
    """Schema validator"""

    def __init__(self, **fields: Field):
        self.fields = fields

    def validate(self, data: dict) -> ValidationResult:
        """Validate data against schema"""

        errors = []
        validated = {}

        for field_name, field in self.fields.items():
            value = data.get(field_name)

            # Check required
            if field.required and value is None:
                errors.append(FieldError(
                    field=field_name,
                    message=f"{field_name} is required",
                    value=value
                ))
                continue

            # Skip if None and not required
            if value is None:
                validated[field_name] = field.default
                continue

            # Coerce type
            if field.coerce:
                try:
                    value = field.coerce(value)
                except Exception as e:
                    errors.append(FieldError(
                        field=field_name,
                        message=f"Invalid {field_name}: {str(e)}",
                        value=value
                    ))
                    continue

            # Type check
            if not isinstance(value, field.type):
                errors.append(FieldError(
                    field=field_name,
                    message=f"{field_name} must be {field.type.__name__}",
                    value=value
                ))
                continue

            # Custom validation
            if field.validator and not field.validator(value):
                errors.append(FieldError(
                    field=field_name,
                    message=f"{field_name} is invalid",
                    value=value
                ))
                continue

            validated[field_name] = value

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            data=validated if len(errors) == 0 else None
        )

    def __call__(self, data: dict) -> ValidationResult:
        return self.validate(data)


# === Usage ===

user_schema = Schema(
    name=Field("name", str, required=True, validator=lambda x: len(x) >= 2),
    email=Field("email", str, required=True, validator=lambda x: "@" in x and "." in x),
    age=Field("age", int, required=False, default=18, validator=lambda x: x >= 0),
    country=Field("country", str, required=False, default="US")
)

# Valid data
result = user_schema.validate({
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
})

print(result.valid)  # True
print(result.data)   # {"name": "Alice", "email": "alice@example.com", "age": 25, "country": "US"}

# Invalid data
result = user_schema.validate({
    "name": "A",
    "email": "invalid"
})

print(result.valid)  # False
print(result.error_messages)
# {"name": "name is invalid", "email": "email is invalid"}
```

## Nested Schemas

```python
class NestedSchema:
    """Nested schema validator"""

    def __init__(self, schema: Schema, required: bool = False):
        self.schema = schema
        self.required = required

    def validate(self, data: dict, field_name: str) -> tuple[bool, list[FieldError], dict | None]:

        value = data.get(field_name)

        if value is None:
            if self.required:
                return False, [FieldError(field_name, f"{field_name} is required", None)], None
            return True, [], {}

        if not isinstance(value, dict):
            return False, [FieldError(field_name, f"{field_name} must be an object", value)], None

        result = self.schema.validate(value)

        if not result.valid:
            # Prefix field names
            errors = [
                FieldError(f"{field_name}.{e.field}", e.message, e.value)
                for e in result.errors
            ]
            return False, errors, None

        return True, [], result.data


# === Usage ===

address_schema = Schema(
    street=Field("street", str, required=True),
    city=Field("city", str, required=True),
    country=Field("country", str, required=True)
)

user_with_address = Schema(
    name=Field("name", str, required=True),
    address=Field("address", dict, required=True)  # Will be validated separately
)

# Or use nested schema
def validate_with_nested(data: dict, schema: Schema, nested: dict[str, NestedSchema]):

    errors = []
    validated = {}

    # Validate main schema
    result = schema.validate(data)
    if not result.valid:
        errors.extend(result.errors)
    else:
        validated.update(result.data or {})

    # Validate nested schemas
    for field_name, nested_schema in nested.items():
        valid, field_errors, field_data = nested_schema.validate(data, field_name)
        if not valid:
            errors.extend(field_errors)
        elif field_data:
            validated[field_name] = field_data

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        data=validated if len(errors) == 0 else None
    )


result = validate_with_nested(
    user_data,
    user_with_address,
    nested={"address": NestedSchema(address_schema, required=True)}
)
```

## Built-in Validators

```python
class Validators:
    """Common validators"""

    @staticmethod
    def email(value: str) -> bool:
        """Validate email format"""
        parts = value.split("@")
        if len(parts) != 2:
            return False
        local, domain = parts
        return "." in domain and len(local) > 0 and len(domain) > 0

    @staticmethod
    def url(value: str) -> bool:
        """Validate URL format"""
        return value.startswith(("http://", "https://"))

    @staticmethod
    def min_length(n: int) -> Callable:
        """Minimum length validator"""
        return lambda x: len(x) >= n

    @staticmethod
    def max_length(n: int) -> Callable:
        """Maximum length validator"""
        return lambda x: len(x) <= n

    @staticmethod
    def range(min_val: int, max_val: int) -> Callable:
        """Range validator"""
        return lambda x: min_val <= x <= max_val

    @staticmethod
    def positive() -> Callable:
        """Positive number validator"""
        return lambda x: x > 0

    @staticmethod
    def non_negative() -> Callable:
        """Non-negative number validator"""
        return lambda x: x >= 0

    @staticmethod
    def matches(pattern: str) -> Callable:
        """Regex match validator"""
        import re
        regex = re.compile(pattern)
        return lambda x: bool(regex.match(x))

    @staticmethod
    def one_of(*options) -> Callable:
        """One of validator"""
        return lambda x: x in options


# === Usage ===

password_schema = Schema(
    password=Field(
        "password",
        str,
        required=True,
        validator=lambda x: (
            len(x) >= 8 and
            any(c.isupper() for c in x) and
            any(c.isdigit() for c in x)
        )
    )
)

role_schema = Schema(
    role=Field(
        "role",
        str,
        required=True,
        validator=Validators.one_of("admin", "user", "guest")
    )
)
```

## Type Coercion

```python
class Coerce:
    """Type coercion helpers"""

    @staticmethod
    def to_int(value):
        """Convert to int"""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value.strip())
        if isinstance(value, float):
            return int(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to int")

    @staticmethod
    def to_float(value):
        """Convert to float"""
        if isinstance(value, float):
            return value
        if isinstance(value, str):
            return float(value.strip())
        if isinstance(value, int):
            return float(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to float")

    @staticmethod
    def to_bool(value):
        """Convert to bool"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, (int, float)):
            return bool(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to bool")

    @staticmethod
    def to_date(value, format: str = "%Y-%m-%d"):
        """Convert to date"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, format)
        raise ValueError(f"Cannot convert {type(value).__name__} to date")


# === Usage ===

config_schema = Schema(
    timeout=Field("timeout", int, required=False, default=30, coerce=Coerce.to_int),
    debug=Field("debug", bool, required=False, default=False, coerce=Coerce.to_bool),
    rate=Field("rate", float, required=False, default=1.0, coerce=Coerce.to_float)
)

data = {
    "timeout": "60",
    "debug": "true",
    "rate": "2.5"
}

result = config_schema.validate(data)
print(result.data)
# {"timeout": 60, "debug": True, "rate": 2.5}
```

## Schema Composition

```python
def compose_schemas(*schemas: Schema) -> Schema:
    """Compose multiple schemas"""

    fields = {}
    for schema in schemas:
        fields.update(schema.fields)

    return Schema(**fields)


# === Usage ===

base_user = Schema(
    name=Field("name", str, required=True),
    email=Field("email", str, required=True)
)

extended_user = Schema(
    age=Field("age", int, required=False),
    country=Field("country", str, required=False, default="US")
)

# Compose
full_user = compose_schemas(base_user, extended_user)
```

## DX Benefits

✅ **Declarative**: Schema as data
✅ **Reusable**: Share schemas
✅ **Clear errors**: Helpful messages
✅ **Type-safe**: Type checking
✅ **Flexible**: Custom validators

## Best Practices

```python
# ✅ Good: Reusable schemas
email_field = Field("email", str, validator=Validators.email())

# ✅ Good: Default values
Field("country", str, required=False, default="US")

# ✅ Good: Clear error messages
Field("age", int, validator=lambda x: x >= 0 or "Age must be positive")

# ❌ Bad: Too complex validators
# Break into named validators
```
