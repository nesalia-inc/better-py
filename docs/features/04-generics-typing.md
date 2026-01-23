# Generics & Typing - Type Safety

Generic types for functional programming with full static type checker support.

## Overview

Python's typing system enables:
- Generic monads and functors
- Type-safe transformations
- IDE autocomplete and refactoring
- Runtime type introspection
- Better documentation

## Basic Generic Functor

```python
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')

class Maybe(Generic[T]):
    """Generic Maybe monad"""

    def __init__(self, value: T | None):
        self._value = value

    def map(self, f: Callable[[T], U]) -> 'Maybe[U]':
        """Map: T -> Maybe[U]"""
        if self._value is None:
            return Maybe(None)
        return Maybe(f(self._value))

    def flat_map(self, f: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """FlatMap: T -> Maybe[U]"""
        if self._value is None:
            return Maybe(None)
        return f(self._value)


# Type inference works!
maybe_int: Maybe[int] = Maybe(5)
maybe_str: Maybe[str] = maybe_int.map(lambda x: str(x))

# IDE knows the types
maybe_int.map(lambda x: x + 1)  # ✅ Correct
maybe_int.map(lambda x: x.length())  # ❌ Type error: int has no .length()
```

## Generic Result/Either Type

```python
from typing import TypeVar, Generic, Union

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result type that can be Ok(value) or Error(error)"""

    __slots__ = ('_value', '_is_ok')

    def __init__(self, value: T | E, is_ok: bool):
        self._value = value
        self._is_ok = is_ok

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(value, True)

    @classmethod
    def error(cls, error: E) -> 'Result[T, E]':
        return cls(error, False)

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        """Only applies to Ok values"""
        if self._is_ok:
            return Result.ok(f(self._value))  # type: ignore
        return Result.error(self._value)  # type: ignore

    def map_error(self, f: Callable[[E], E2]) -> 'Result[T, E2]':
        """Only applies to Error values"""
        if not self._is_ok:
            return Result.error(f(self._value))  # type: ignore
        return Result.ok(self._value)  # type: ignore

    def flat_map(self, f: Callable[[T], 'Result[U, E]') -> 'Result[U, E]':
        """Chain Results"""
        if self._is_ok:
            return f(self._value)  # type: ignore
        return Result.error(self._value)  # type: ignore


# Type-safe error handling
def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.error("Division by zero")
    return Result.ok(a / b)

result: Result[float, str] = divide(10, 2)
mapped: Result[str, str] = result.map(lambda x: f"Result: {x}")
```

## Callable Variance

```python
from typing import Protocol, TypeVar, Generic

T_co = TypeVar('T_co', covariant=True)  # Output (can be more specific)
T_contra = TypeVar('T_contra', contravariant=True)  # Input (can be more general)

class Functor(Protocol[T_co]):
    """Covariant functor - can be used where more general type expected"""

    def map(self, f: Callable[[T_co], U]) -> 'Maybe[U]': ...

# Maybe[int] can be used where Maybe[float] is expected
# (int is more specific than float, covariant)
```

## Type Guards

```python
from typing import TypeGuard, TypeVar

T = TypeVar('T')

def is_some(maybe: Maybe[T]) -> TypeGuard['Some[T]']:
    """Type guard for Some (non-None) values"""
    return bool(maybe)

def is_none(maybe: Maybe[T]) -> TypeGuard['None']:
    """Type guard for None values"""
    return not bool(maybe)


# Usage with type narrowing
maybe_value: Maybe[int] = Maybe(5)

if is_some(maybe_value):
    # Type is narrowed to Some[int]
    print(maybe_value._value + 10)
else:
    # Type is narrowed to None
    print("No value")
```

## Literal Types for Exact Values

```python
from typing import Literal

@dataclass
class ValidationError:
    field: str
    message: str

@dataclass
class NetworkError:
    code: Literal[400, 401, 403, 404, 500]
    message: str

ErrorType = ValidationError | NetworkError


def handle_error(error: ErrorType) -> str:
    if isinstance(error, NetworkError):
        # Type checker knows error is NetworkError
        match error.code:
            case 401:
                return "Unauthorized"
            case 404:
                return "Not found"
            case _:
                return f"HTTP {error.code}"
    else:
        return f"Validation failed: {error.field}"
```

## ParamSpec for Callable Wrappers

```python
from typing import ParamSpec, Callable, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

def memoize(func: Callable[P, R]) -> Callable[P, R]:
    """Memoization decorator that preserves signature"""
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


# Type checking knows original signature
@memoize
def add(a: int, b: int) -> int:
    return a + b

# IDE shows: (a: int, b: int) -> int
result: int = add(1, 2)
```

## Self Type

```python
from typing import Self

class Maybe(Generic[T]):
    def map(self, f: Callable[[T], U]) -> 'Maybe[U]':
        ...

    def filter(self, predicate: Callable[[T], bool]) -> Self:
        """Returns Self for method chaining"""
        if self._value is not None and predicate(self._value):
            return self
        return Maybe(None)


# Type checker knows return type is Maybe[T], not just Maybe
maybe: Maybe[int] = Maybe(5)
filtered: Maybe[int] = maybe.filter(lambda x: x > 0)
```

## Type Aliases for Clarity

```python
from typing import TypeAlias

# Clear domain-specific types
UserId: TypeAlias = int
Email: TypeAlias = str
Url: TypeAlias = str

# Functional type aliases
Predicate: TypeAlias = Callable[[T], bool]
Mapper: TypeAlias = Callable[[T], U]
Reducer: TypeAlias = Callable[[U, T], U]

# Common signatures
AsyncResult: TypeAlias = Coroutine[Any, Any, Result[T, E]]
Validator: TypeAlias = Callable[[T], Result[T, str]]


def validate_email(email: str) -> Result[Email, str]:
    if "@" in email:
        return Result.ok(email)
    return Result.error("Invalid email")


# More readable function signatures
def fetch_user(id: UserId) -> AsyncResult[User, str]:
    ...
```

## Overloads for Better Inference

```python
from typing import overload

class Maybe(Generic[T]):
    @overload
    def get_or_else(self, default: T) -> T: ...

    @overload
    def get_or_else(self, default: None) -> T | None: ...

    def get_or_else(self, default: T | None) -> T | None:
        return self._value if self._value is not None else default


# Type checker infers return type correctly
maybe_int: Maybe[int] = Maybe(5)

val1: int = maybe_int.get_or_else(0)  # int
val2: int | None = maybe_int.get_or_else(None)  # int | None
```

## TypedDict for Structured Data

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str


def parse_user(data: dict) -> Result[User, str]:
    """Parse dict into typed User"""
    try:
        user: User = {
            'id': data['id'],
            'name': data['name'],
            'email': data['email']
        }
        return Result.ok(user)
    except KeyError as e:
        return Result.error(f"Missing field: {e}")


# Access is type-checked
user = User(id=1, name="Alice", email="alice@example.com")
print(user['id'])     # ✅ OK
print(user['invalid'])  # ❌ Type error
```

## Protocol for Structural Typing

```python
from typing import Protocol

class SupportsAdd(Protocol):
    """Protocol for types that support addition"""

    def __add__(self, other: Any) -> Any: ...


T = TypeVar('T', bound=SupportsAdd)

def sum_all(items: list[T]) -> T:
    """Sum any type that supports __add__"""
    result: T = items[0]
    for item in items[1:]:
        result = result + item  # type: ignore
    return result


# Works with ints, floats, strings, lists, etc.
print(sum_all([1, 2, 3]))      # int: 6
print(sum_all(['a', 'b']))     # str: "ab"
```

## Type Checking Commands

```bash
# Mypy
mypy src/ --strict

# Pyright
pyright src/

# Ruff type checking
ruff check src/ --select F
```

## DX Benefits

✅ **Catch errors early**: Type errors at dev time
✅ **Better autocomplete**: IDE knows types
✅ **Self-documenting**: Types serve as docs
✅ **Refactoring**: Safe code changes
✅ **Runtime hints**: Optional runtime validation

## Best Practices

```python
# ✅ Good: Use TypeVar for generic types
T = TypeVar('T')
class Maybe(Generic[T]): ...

# ✅ Good: Use Protocol for behavior
class Functor(Protocol): ...

# ✅ Good: Type aliases for clarity
UserId: TypeAlias = int

# ❌ Bad: Any type
def process(value: Any):  # No type safety!
    ...

# ❌ Bad: Ignoring type errors
result = cast(Result[int], value)  # Defeats purpose
```
