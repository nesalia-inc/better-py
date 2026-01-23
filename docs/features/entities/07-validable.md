# Validable: Data Validation Entities

**Validable** is a protocol for objects that can **validate themselves** - ensuring data integrity with structured error reporting.

## Overview

```python
@runtime_checkable
class Validable(Protocol[T]):
    """Objects that can validate themselves"""

    def validate(self) -> Validation:
        """Validate this object"""
        ...

    @classmethod
    def validator(cls) -> 'Validator[T]':
        """Get validator for this type"""
        ...
```

## Core Concepts

### Validation vs Parsing

```python
# Parsing: String → Object (with error)
result = ParseableInt.parse("42")

# Validation: Object → Valid (with errors)
user = User(name="", age=-1)
result = user.validate()  # Errors(["Name required", "Age must be positive"])
```

## Implementation

### Validable Dataclass

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class ValidableDataclass:
    """Mixin for dataclasses with validation"""

    def validate(self) -> Validation:
        """Validate all fields"""
        errors = []

        for field_info in dataclasses.fields(self):
            value = getattr(self, field_info.name)

            # Check if required
            if value is None or (isinstance(value, str) and not value):
                if field_info.default is dataclasses.MISSING:
                    errors.append(ValidationError(f"Field '{field_info.name}' is required"))

            # Run field validator if present
            if hasattr(self, f"_validate_{field_info.name}"):
                field_errors = getattr(self, f"_validate_{field_info.name}")(value)
                if field_errors:
                    errors.extend(field_errors)

        if errors:
            return Validation.errors_(*errors)
        return Validation.success(self)

    @classmethod
    def validator(cls) -> 'Validator[T]':
        """Get validator for this class"""
        return DataclassValidator(cls)
```

### Validable User Example

```python
@dataclass(frozen=True, slots=True)
class User(ValidableDataclass):
    """User with validation"""
    name: str
    email: str
    age: int
    active: bool = True

    def _validate_name(self, value: str) -> list[Exception] | None:
        """Validate name"""
        errors = []

        if len(value) < 2:
            errors.append(ValidationError("Name must be at least 2 characters"))

        if len(value) > 50:
            errors.append(ValidationError("Name must be at most 50 characters"))

        return errors if errors else None

    def _validate_email(self, value: str) -> list[Exception] | None:
        """Validate email"""
        if "@" not in value or "." not in value.split("@")[1]:
            return [ValidationError("Invalid email format")]
        return None

    def _validate_age(self, value: int) -> list[Exception] | None:
        """Validate age"""
        errors = []

        if value < 0:
            errors.append(ValidationError("Age cannot be negative"))

        if value > 150:
            errors.append(ValidationError("Age unrealistic (>150)"))

        return errors if errors else None

# Usage
user = User(
    name="A",
    email="invalid",
    age=-1
)

result = user.validate()
# Validation.errors_(
#     ValidationError("Name must be at least 2 characters"),
#     ValidationError("Invalid email format"),
#     ValidationError("Age cannot be negative")
# )

# Valid user
user = User(
    name="Alice",
    email="alice@example.com",
    age=30
)

result = user.validate()
# Validation.success(User(...))
```

### Validator Protocol

```python
@runtime_checkable
class Validator(Protocol[T]):
    """Validator protocol"""

    def validate(self, value: T) -> Validation:
        """Validate value"""
        ...

    def __call__(self, value: T) -> Validation:
        """Convenient: validator(value)"""
        return self.validate(value)
```

### Field Validators

#### StringValidator

```python
class StringValidator(BaseValidator[str]):
    """Validator for string values"""

    @classmethod
    def create(cls) -> 'StringValidator':
        return cls()

    def required(self, error: Exception = FieldRequired("value")) -> 'StringValidator':
        """Field is required"""
        def rule(value: str):
            if not value or not value.strip():
                return error
            return None
        self._rules.append(rule)
        return self

    def min_length(self, n: int, error_type: type = ValidationError) -> 'StringValidator':
        """Minimum length"""
        def rule(value: str):
            if len(value) < n:
                return error_type(f"Must be at least {n} characters")
            return None
        self._rules.append(rule)
        return self

    def max_length(self, n: int, error_type: type = ValidationError) -> 'StringValidator':
        """Maximum length"""
        def rule(value: str):
            if len(value) > n:
                return error_type(f"Must be at most {n} characters")
            return None
        self._rules.append(rule)
        return self

    def email(self, error_type: type = ValidationError) -> 'StringValidator':
        """Email format"""
        def rule(value: str):
            parts = value.split("@")
            if len(parts) != 2 or "." not in parts[1]:
                return error_type("Invalid email format")
            return None
        self._rules.append(rule)
        return self

    def matches(self, pattern: str, error_type: type = ValidationError) -> 'StringValidator':
        """Regex match"""
        import re
        regex = re.compile(pattern)
        def rule(value: str):
            if not regex.match(value):
                return error_type(f"Must match pattern: {pattern}")
            return None
        self._rules.append(rule)
        return self

    def one_of(self, *options: str, error_type: type = ValidationError) -> 'StringValidator':
        """Must be one of options"""
        def rule(value: str):
            if value not in options:
                return error_type(f"Must be one of: {', '.join(options)}")
            return None
        self._rules.append(rule)
        return self
```

#### IntValidator

```python
class IntValidator(BaseValidator[int]):
    """Validator for integer values"""

    @classmethod
    def create(cls) -> 'IntValidator':
        return cls()

    def positive(self, error_type: type = ValidationError) -> 'IntValidator':
        """Must be positive"""
        def rule(value: int):
            if value <= 0:
                return error_type("Must be positive")
            return None
        self._rules.append(rule)
        return self

    def non_negative(self, error_type: type = ValidationError) -> 'IntValidator':
        """Must be non-negative"""
        def rule(value: int):
            if value < 0:
                return error_type("Must be non-negative")
            return None
        self._rules.append(rule)
        return self

    def range(self, min_val: int, max_val: int, error_type: type = ValidationError) -> 'IntValidator':
        """Must be in range"""
        def rule(value: int):
            if not (min_val <= value <= max_val):
                return error_type(f"Must be between {min_val} and {max_val}")
            return None
        self._rules.append(rule)
        return self

    def one_of(self, *options: int, error_type: type = ValidationError) -> 'IntValidator':
        """Must be one of options"""
        def rule(value: int):
            if value not in options:
                return error_type(f"Must be one of: {options}")
            return None
        self._rules.append(rule)
        return self
```

### DictValidator

```python
class DictValidator(BaseValidator[dict]):
    """Validator for dictionaries"""

    @classmethod
    def create(cls) -> 'DictValidator':
        return cls()

    def required_keys(self, *keys: str, error_type: type = ValidationError) -> 'DictValidator':
        """Require specific keys"""
        def rule(value: dict):
            missing = [k for k in keys if k not in value]
            if missing:
                return error_type(f"Missing required keys: {', '.join(missing)}")
            return None
        self._rules.append(rule)
        return self

    def key_type(self, key: str, expected_type: type, error_type: type = ValidationError) -> 'DictValidator':
        """Key must be type"""
        def rule(value: dict):
            if key in value and not isinstance(value[key], expected_type):
                return error_type(f"Key '{key}' must be {expected_type.__name__}")
            return None
        self._rules.append(rule)
        return self

    def nested(self, key: str, validator: Validator, error_type: type = ValidationError) -> 'DictValidator':
        """Validate nested dict"""
        def rule(value: dict):
            if key in value:
                result = validator.validate(value[key])
                if result.is_errors():
                    return result.errors[0]
            return None
        self._rules.append(rule)
        return self
```

## Advanced Patterns

### Conditional Validation

```python
class ConditionalValidator(BaseValidator[dict]):
    """Validator with conditional rules"""

    def validate_if(
        self,
        condition: Callable[[dict], bool],
        validator: Validator
    ) -> 'ConditionalValidator':
        """Apply validator only if condition met"""

        def rule(value: dict):
            if condition(value):
                result = validator.validate(value)
                if result.is_errors():
                    return result.errors[0]
            return None

        self._rules.append(rule)
        return self

# Usage
user_validator = (
    DictValidator.create()
    .validate_if(
        lambda d: d.get("age", 0) < 18,
        StringValidator.create().required("guardian_name")
    )
)

# Requires guardian_name if age < 18
```

### Cross-Field Validation

```python
@dataclass(frozen=True, slots=True)
class PasswordChange(ValidableDataclass):
    """Password change with cross-field validation"""

    current_password: str
    new_password: str
    confirm_password: str

    def _validate_new_password(self, value: str) -> list[Exception] | None:
        errors = []

        if len(value) < 8:
            errors.append(ValidationError("Password must be at least 8 characters"))

        if not any(c.isupper() for c in value):
            errors.append(ValidationError("Password must contain uppercase letter"))

        if not any(c.isdigit() for c in value):
            errors.append(ValidationError("Password must contain digit"))

        return errors if errors else None

    def validate(self) -> Validation:
        """Validate including cross-field checks"""
        # First validate fields
        result = super().validate()
        if result.is_errors():
            return result

        # Then cross-field validation
        errors = []

        if self.new_password != self.confirm_password:
            errors.append(ValidationError("Passwords do not match"))

        if self.new_password == self.current_password:
            errors.append(ValidationError("New password must differ from current"))

        if errors:
            return Validation.errors_(*errors)

        return Validation.success(self)
```

### Async Validation

```python
class AsyncValidator(Generic[T]):
    """Async validator"""

    def __init__(self):
        self._rules: list[Callable[[T], Awaitable[Exception | None]]] = []

    async def validate(self, value: T) -> Validation:
        """Validate asynchronously"""
        errors = []

        for rule in self._rules:
            error = await rule(value)
            if error is not None:
                errors.append(error)

        if errors:
            return Validation.errors_(*errors)
        return Validation.success(value)

    def add_rule(
        self,
        rule: Callable[[T], Awaitable[Exception | None]]
    ) -> 'AsyncValidator[T]':
        self._rules.append(rule)
        return self

# Usage
async def check_email_unique(email: str) -> Exception | None:
    exists = await db.users.find_by_email(email)
    if exists:
        return ValidationError("Email already registered")
    return None

async_validator = AsyncValidator[dict]()
async_validator.add_rule(
    lambda data: check_email_unique(data.get("email", ""))
)

result = await async_validator.validate({"email": "test@example.com"})
```

## Protocol Compliance

```python
@runtime_checkable
class Validable(Protocol[T]):
    def validate(self) -> Validation: ...
    @classmethod
    def validator(cls) -> Validator[T]: ...

class CustomValidable:
    def __init__(self, value):
        self.value = value

    def validate(self) -> Validation:
        if self.value < 0:
            return Validation.errors_(ValidationError("Must be positive"))
        return Validation.success(self)

    @classmethod
    def validator(cls):
        return CustomValidator()

# CustomValidable is Validable!
isinstance(CustomValidable(0), Validable)  # True
```

## Integration with Descriptors

```python
class ValidatedField:
    """Descriptor for validated fields"""

    def __init__(self, validator: Validator, required: bool = False):
        self.validator = validator
        self.required = required

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        # Validate before setting
        result = self.validator.validate(value)
        if result.is_errors():
            raise ValidationError(result.errors[0])
        obj.__dict__[self.name] = value

# Usage
class User:
    name = ValidatedField(
        StringValidator.create().min_length(2).max_length(50),
        required=True
    )
    email = ValidatedField(
        StringValidator.create().email(),
        required=True
    )

user = User()
user.name = "A"  # Raises ValidationError!
```

## Best Practices

### ✅ Do: Validate invariants

```python
# Good: Enforce business rules
def validate(self) -> Validation:
    if self.end_date < self.start_date:
        return Validation.errors_(ValidationError("End date before start date"))
```

### ✅ Do: Accumulate all errors

```python
# Good: Report all errors at once
errors = []
for field in fields:
    if not valid(field):
        errors.append(error)
return Validation.errors_(*errors)
```

### ❌ Don't: Validate on init

```python
# Bad: Fails fast, can't create invalid objects
class User:
    def __init__(self, name):
        if not name:
            raise ValueError("Name required")
        self.name = name

# Good: Validate explicitly
class User:
    def __init__(self, name):
        self.name = name

    def validate(self) -> Validation:
        if not self.name:
            return Validation.errors_(ValidationError("Name required"))
        return Validation.success(self)
```

## Summary

**Validable** protocol:
- ✅ Objects validate themselves
- ✅ `validate()` returns Validation
- ✅ Field-level validators
- ✅ Cross-field validation
- ✅ Async validation support
- ✅ Descriptor integration

**Key benefit**: **Self-documenting validation** with **structured errors**.

---

**Next**: See [Cacheable](./08-cacheable.md) for cacheable entities.
