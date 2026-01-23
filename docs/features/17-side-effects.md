# Side Effect Tracking - Explicit Effect Management

Track and manage side effects explicitly without monadic jargon.

## Overview

Side effect tracking enables:
- Explicit effect declaration
- Separate pure and impure code
- Testable business logic
- Clear effect boundaries
- Type-safe effect checking

## Pure Function Decorator

```python
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

def pure(func: Callable) -> Callable:
    """Mark function as pure (no side effects)"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper._pure = True
    return wrapper


def is_pure(func: Callable) -> bool:
    """Check if function is marked as pure"""
    return getattr(func, '_pure', False)


# === Usage ===

@pure
def calculate_total(items: list[dict]) -> float:
    """Pure calculation - no side effects"""
    return sum(item['price'] * item['quantity'] for item in items)

@pure
def apply_discount(total: float, discount: float) -> float:
    """Pure discount application"""
    return total * (1 - discount)

print(is_pure(calculate_total))  # True
```

## Effect Markers

```python
from enum import Enum
from typing import Callable
from functools import wraps

class Effect(Enum):
    IO = "io"
    DATABASE = "database"
    NETWORK = "network"
    STATE = "state"
    LOGGING = "logging"


def has_effects(*effects: Effect) -> Callable:
    """Mark function with specific effects"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._effects = effects
        return wrapper

    return decorator


def get_effects(func: Callable) -> list[Effect]:
    """Get effects of function"""
    return getattr(func, '_effects', [])


# === Usage ===

@has_effects(Effect.DATABASE)
def save_user(user: dict) -> int:
    """Save user to database"""
    db.insert(user)
    return user['id']

@has_effects(Effect.NETWORK, Effect.LOGGING)
def fetch_api(url: str) -> dict:
    """Fetch from API"""
    logger.info(f"Fetching {url}")
    return requests.get(url).json()

print(get_effects(save_user))  # [Effect.DATABASE]
```

## Effect Checking

```python
class EffectChecker:
    """Check for unwanted effects in code"""

    @staticmethod
    def requires_pure(func: Callable) -> None:
        """Ensure function has no effects"""
        effects = get_effects(func)
        if effects or not is_pure(func):
            raise ValueError(f"Function {func.__name__} must be pure")

    @staticmethod
    def prohibits(*prohibited: Effect) -> Callable:
        """Decorator that prohibits certain effects"""

        def decorator(func: Callable) -> Callable:
            effects = get_effects(func)

            for prohibited_effect in prohibited:
                if prohibited_effect in effects:
                    raise ValueError(
                        f"Function {func.__name__} cannot have "
                        f"{prohibited_effect.value} effect"
                    )

            return func

        return decorator


# === Usage ===

@prohibits(Effect.DATABASE, Effect.NETWORK)
def process_payment(amount: float) -> dict:
    """Process payment without I/O"""
    return {
        "amount": amount,
        "fee": amount * 0.02,
        "total": amount * 1.02
    }  # Pure calculation

# This would raise error:
# @prohibits(Effect.DATABASE)
# def save_to_db(data):
#     db.save(data)
```

## Pure / Effect Separation

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class PureValue:
    """Container for pure values"""

    value: T

    def map(self, func):
        """Apply pure function"""
        return PureValue(func(self.value))


@dataclass
class SideEffect:
    """Marker for side effects"""

    description: str
    effect: Effect


class EffectSeparator:
    """Separate pure logic from side effects"""

    def __init__(self):
        self.pure_operations = []
        self.effects = []

    def pure(self, func: Callable, *args, **kwargs) -> 'EffectSeparator':
        """Add pure operation"""
        result = func(*args, **kwargs)
        self.pure_operations.append(result)
        return self

    def effect(self, description: str, effect: Effect, func: Callable, *args, **kwargs):
        """Add side effect"""
        result = func(*args, **kwargs)
        self.effects.append(SideEffect(description, effect))
        return self

    def execute(self):
        """Execute all operations"""
        return {
            "pure_results": self.pure_operations,
            "effects": self.effects
        }


# === Usage ===

def register_user_pure(data: dict) -> dict:
    """Pure user creation logic"""
    return {
        "name": data["name"].strip().title(),
        "email": data["email"].lower(),
        "created_at": datetime.now()
    }

def save_user_effect(user: dict):
    """Side effect: save to database"""
    db.users.insert(user)

separator = EffectSeparator()

result = (
    separator
    .pure(register_user_pure, {"name": "alice", "email": "ALICE@EXAMPLE.COM"})
    .effect("Save user to database", Effect.DATABASE, save_user_effect, result.pure_operations[0])
    .execute()
)
```

## IO Monad Style (Without the Name)

```python
class Effectful:
    """Container for effectful computations"""

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute the effect"""
        return self.func(*self.args, **self.kwargs)

    def map(self, func):
        """Apply function to result"""

        def run_mapped():
            result = self.run()
            return func(result)

        return Effectful(run_mapped)

    def then(self, next_effect):
        """Chain with another effect"""

        def run_chained():
            result = self.run()
            return next_effect(result).run()

        return Effectful(run_chained)


# === Usage ===

def fetch_user(id: int) -> dict:
    return {"id": id, "name": "Alice"}

def fetch_posts(user: dict) -> list:
    return [{"id": 1, "title": "Post 1", "user_id": user["id"]}]

def count_posts(posts: list) -> int:
    return len(posts)

# Build effect chain
program = (
    Effectful(fetch_user, 1)
    .then(lambda user: Effectful(fetch_posts, user))
    .map(count_posts)
)

post_count = program.run()
print(post_count)  # 1
```

## Testable Effects

```python
from typing import Protocol, TypeVar

T = TypeVar('T')

class Effect(Protocol[T]):
    """Protocol for effectful operations"""

    def execute(self) -> T:
        """Execute the effect"""
        ...


class RealDatabase:
    """Real database effect"""

    def execute(self) -> Any:
        return db.query("SELECT * FROM users")


class FakeDatabase:
    """Fake database for testing"""

    def __init__(self, data: list):
        self.data = data

    def execute(self) -> Any:
        return self.data


def get_users(db: Effect) -> list:
    """Get users - testable with real or fake db"""
    return db.execute()


# === Usage ===

# Production
real_db = RealDatabase()
users = get_users(real_db)

# Testing
fake_db = FakeDatabase([{"id": 1, "name": "Alice"}])
test_users = get_users(fake_db)
```

## Transaction Boundary

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def transaction_boundary():
    """Mark transaction boundaries"""

    print("Transaction started")
    try:
        yield
        print("Transaction committed")
    except Exception as e:
        print(f"Transaction rolled back: {e}")
        raise


class Transactional:
    """Mark operations as transactional"""

    def __init__(self, in_transaction: bool = False):
        self.in_transaction = in_transaction

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.in_transaction:
                with transaction_boundary():
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper


# === Usage ===

@Transactional(in_transaction=True)
def transfer_money(from_account: int, to_account: int, amount: float):
    """Transfer money transactionally"""
    accounts.debit(from_account, amount)
    accounts.credit(to_account, amount)

transfer_money(1, 2, 100.0)
# Output:
# Transaction started
# Transaction committed
```

## Effect Validation

```python
class EffectValidator:
    """Validate effects are used correctly"""

    def __init__(self):
        self.allowed_effects: set[Effect] = set()

    def allow(self, *effects: Effect):
        """Allow specific effects"""
        self.allowed_effects.update(effects)
        return self

    def validate(self, func: Callable):
        """Validate function only uses allowed effects"""

        effects = get_effects(func)
        for effect in effects:
            if effect not in self.allowed_effects:
                raise ValueError(
                    f"Function {func.__name__} uses {effect.value} "
                    f"which is not allowed"
                )

        return func


# === Usage ===

validator = EffectValidator().allow(Effect.LOGGING)

@validator.validate
@has_effects(Effect.LOGGING)
def log_message(message: str):
    logger.info(message)

# This would raise error:
# @validator.validate
# @has_effects(Effect.DATABASE)
# def save_to_db(data):
#     ...
```

## DX Benefits

✅ **Explicit**: Effects are declared, not hidden
✅ **Testable**: Pure logic is easily testable
✅ **Safe**: Compiler/checker can verify effects
✅ **Clear**: Effect boundaries are obvious
✅ **Flexible**: Mix pure and effectful code

## Best Practices

```python
# ✅ Good: Mark pure functions
@pure
def calculate_discount(total, rate):
    return total * rate

# ✅ Good: Declare effects
@has_effects(Effect.DATABASE)
def save_user(user):
    db.insert(user)

# ✅ Good: Separate pure and effectful
pure_data = process(raw_data)
save(pure_data)

# ❌ Bad: Hidden effects
def process(data):
    result = calculate(data)
    db.save(result)  # Hidden side effect!
    return result
```
