# Pattern Matching - Structured Matching

Leverage Python 3.10+ `match/case` for expressive functional pattern matching.

## Overview

Pattern matching enables:
- Exhaustive checking
- Deconstruction of complex types
- Type-based branching
- Guards (conditions)
- Readable control flow

## Basic Pattern Matching

```python
from typing import Literal

def describe(value: int | str | list) -> str:
    match value:
        case 0:
            return "Zero"
        case int():
            return f"Integer: {value}"
        case str():
            return f"String: {value}"
        case list():
            return f"List with {len(value)} items"
        case _:
            return "Something else"


print(describe(5))          # "Integer: 5"
print(describe("hello"))    # "String: hello"
print(describe([1, 2, 3]))  # "List with 3 items"
```

## Matching Maybe Monads

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class Maybe(Generic[T]):
    value: T | None

    __match_args__ = ("value",)  # Enable pattern matching

    @classmethod
    def some(cls, value: T) -> 'Maybe[T]':
        return cls(value)

    @classmethod
    def none(cls) -> 'Maybe[T]':
        return cls(None)


def process(maybe: Maybe[int]) -> str:
    match maybe:
        case Maybe(None):
            return "No value"
        case Maybe(value):
            return f"Value: {value}"


print(process(Maybe.some(42)))   # "Value: 42"
print(process(Maybe.none()))     # "No value"
```

## Matching Result/Either

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T
    __match_args__ = ("value",)

@dataclass
class Error(Generic[E]):
    error: E
    __match_args__ = ("error",)

Result = Ok[T] | Error[E]


def handle_result(result: Result[int, str]) -> str:
    match result:
        case Ok(value):
            return f"Success: {value}"
        case Error(err):
            return f"Error: {err}"
        case _:
            return "Unknown"


print(handle_result(Ok(42)))       # "Success: 42"
print(handle_result(Error("fail"))) # "Error: fail"
```

## Guards in Patterns

```python
def classify_number(n: int) -> str:
    match n:
        case x if x < 0:
            return "Negative"
        case x if x == 0:
            return "Zero"
        case x if x % 2 == 0:
            return "Even positive"
        case _:
            return "Odd positive"


print(classify_number(-5))  # "Negative"
print(classify_number(0))   # "Zero"
print(classify_number(4))   # "Even positive"
print(classify_number(7))   # "Odd positive"
```

## Nested Pattern Matching

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class User:
    id: int
    name: str
    status: Literal['active', 'inactive', 'pending']

@dataclass
class Post:
    author: User
    content: str
    likes: int


def summarize(item: User | Post) -> str:
    match item:
        case User(status='active'):
            return f"Active user: {item.name}"
        case User(status='inactive'):
            return f"Inactive user: {item.name}"
        case User(status='pending'):
            return f"Pending user: {item.name}"
        case Post(author=User(name=name, status='active'), likes=likes) if likes > 100:
            return f"Viral post by {name} with {likes} likes"
        case Post(author=User(name=name), likes=likes):
            return f"Post by {name} with {likes} likes"


user = User(1, "Alice", "active")
post = Post(user, "Hello World", 150)

print(summarize(user))  # "Active user: Alice"
print(summarize(post))  # "Viral post by Alice with 150 likes"
```

## Matching with Sequences

```python
def analyze_sequence(seq: list | tuple) -> str:
    match seq:
        case []:
            return "Empty"
        case [x]:
            return f"Single: {x}"
        case [x, y]:
            return f"Pair: {x}, {y}"
        case [x, y, *rest]:
            return f"List starting with {x}, {y} and {len(rest)} more"
        case (x, y):
            return f"Tuple pair: {x}, {y}"
        case _:
            return "Other"


print(analyze_sequence([]))           # "Empty"
print(analyze_sequence([1]))          # "Single: 1"
print(analyze_sequence([1, 2]))       # "Pair: 1, 2"
print(analyze_sequence([1, 2, 3, 4])) # "List starting with 1, 2 and 2 more"
print(analyze_sequence((1, 2)))       # "Tuple pair: 1, 2"
```

## Matching with Dictionaries

```python
def process_request(data: dict) -> str:
    match data:
        case {'action': 'create', 'resource': resource}:
            return f"Create {resource}"
        case {'action': 'delete', 'id': id}:
            return f"Delete item {id}"
        case {'action': 'update', 'id': id, **rest}:
            fields = ', '.join(rest.keys())
            return f"Update {id}: {fields}"
        case _:
            return "Unknown action"


print(process_request({'action': 'create', 'resource': 'user'}))  # "Create user"
print(process_request({'action': 'delete', 'id': 42}))            # "Delete item 42"
print(process_request({'action': 'update', 'id': 1, 'name': 'Bob'}))  # "Update 1: name"
```

## Functional Error Handling

```python
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Result(Generic[T, E]):
    """Functional Result type with pattern matching support"""
    _value: T | None
    _error: E | None
    _is_ok: bool

    __match_args__ = ('_value', '_error', '_is_ok')

    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        return cls(value, None, True)

    @classmethod
    def error(cls, error: E) -> 'Result[T, E]':
        return cls(None, error, False)


def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.error("Division by zero")
    return Result.ok(a / b)


def handle_division(a: int, b: int) -> str:
    result = divide(a, b)

    match result:
        case Result(None, error, False):
            return f"Error: {error}"
        case Result(value, None, True):
            return f"Result: {value:.2f}"
        case _:
            return "Invalid state"


print(handle_division(10, 2))   # "Result: 5.00"
print(handle_division(10, 0))   # "Error: Division by zero"
```

## AST-like Pattern Matching

```python
from dataclasses import dataclass
from typing import TypeVar, Union

T = TypeVar('T')

@dataclass
class Literal:
    value: int

@dataclass
class Variable:
    name: str

@dataclass
class BinOp:
    op: str
    left: 'Expr'
    right: 'Expr'

Expr = Union[Literal, Variable, BinOp]


def eval_expr(expr: Expr, env: dict[str, int]) -> int:
    match expr:
        case Literal(value):
            return value
        case Variable(name):
            return env.get(name, 0)
        case BinOp(op='+', left=left, right=right):
            return eval_expr(left, env) + eval_expr(right, env)
        case BinOp(op='*', left=left, right=right):
            return eval_expr(left, env) * eval_expr(right, env)
        case BinOp(op='-', left=left, right=right):
            return eval_expr(left, env) - eval_expr(right, env)
        case _:
            raise ValueError(f"Unknown expression: {expr}")


# Expression: (5 + x) * y
expr = BinOp('*',
    left=BinOp('+',
        left=Literal(5),
        right=Variable('x')
    ),
    right=Variable('y')
)

env = {'x': 3, 'y': 2}
print(eval_expr(expr, env))  # 16: (5 + 3) * 2
```

## Type-based Dispatch

```python
from typing import Any

def process(value: Any) -> str:
    match type(value):
        case int:
            return f"Integer: {value}"
        case str:
            return f"String: '{value}'"
        case list:
            return f"List: [{', '.join(map(str, value))}]"
        case dict:
            return f"Dict: {len(value)} keys"
        case _:
            return f"Unknown: {type(value).__name__}"


print(process(42))                 # "Integer: 42"
print(process("hello"))            # "String: 'hello'"
print(process([1, 2, 3]))          # "List: [1, 2, 3]"
print(process({'a': 1, 'b': 2}))   # "Dict: 2 keys"
```

## Exhaustive Checking with Type Guards

```python
from typing import Literal, assert_never

Status = Literal['pending', 'running', 'completed', 'failed']

def get_status_message(status: Status) -> str:
    match status:
        case 'pending':
            return "Job is pending"
        case 'running':
            return "Job is running"
        case 'completed':
            return "Job completed successfully"
        case 'failed':
            return "Job failed"
        case _:
            # If we miss a case, type checker will catch it
            assert_never(status)

# If we add 'cancelled' to Status, mypy will error
# until we add a case for it above
```

## DX Benefits

✅ **Exhaustive**: Compiler checks all cases
✅ **Readable**: Control flow is clear
✅ **Type-safe**: Works with static type checkers
✅ **Declarative**: Intent is explicit
✅ **Powerful**: Guards, nested patterns, captures

## Best Practices

```python
# ✅ Good: Exhaustive matching
match value:
    case A(): return "A"
    case B(): return "B"
    case _: return "Other"

# ✅ Good: Using guards for conditions
case x if x > 0: return "Positive"

# ✅ Good: Capturing nested values
case User(name=n, age=a) if a >= 18: ...

# ❌ Bad: Redundant patterns (can be simplified)
case [x]:
    return x
case [y]:
    return y

# ❌ Avoid: Too broad patterns early
case _:  # This should be last
    return "default"
case x:  # Never reached!
    return x
```
