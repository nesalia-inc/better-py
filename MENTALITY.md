# Design Philosophy: Functional Entities as Objects

## The Problem

**Pure Functional Programming** often feels academic and disconnected from Python:
- "What's a monad?" → *Users leave*
- Functions everywhere, no state management
- Feels like Haskell/Rust移植 to Python

**Traditional OOP** (Java-style) often creates unnecessary complexity:
- Over-engineered class hierarchies
- Design patterns galore
- Verbosity for simple tasks

**Our Approach**: **Functional Entities as Objects**

---

## Core Principle: Everything is an Object, Operations are Functional

We don't write *functions* that manipulate data. We create **objects that represent functional concepts**.

### Before: Traditional FP
```python
# Pure functional style
result = map(lambda x: x * 2, filter(lambda x: x > 0, numbers))
```

### After: Functional Entity as Object
```python
# Object representing a functional concept
numbers = MappableList([1, 2, 3, -4, 5])
result = numbers.filter(lambda x: x > 0).map(lambda x: x * 2)
```

**The difference**: `MappableList` is an **entity** that **has** functional capabilities, not just a target for functions.

---

## Inspiration: `collections.abc`

Just like Python's `collections.abc` defines protocols for containers, we define protocols for **functional behaviors**:

```python
# collections.abc approach
from collections.abc import Sequence, Mapping

class MyList(Sequence):
    def __getitem__(self, index): ...
    def __len__(self): ...
    # Now it's a Sequence! All Sequence methods work.

# Our approach
from mfn.abc import Mappable, Reducible

class SmartList(Mappable, Reducible):
    def map(self, func): ...      # Implements Mappable protocol
    def reduce(self, func): ...   # Implements Reducible protocol
    # Now it's functional! All functional compositions work.
```

---

## Key Characteristics

### 1. Protocol-Based Design

We use **Protocols** (structural typing), not rigid inheritance:

```python
@runtime_checkable
class Mappable(Protocol[T]):
    """Any object that can be mapped over"""
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

# Any class with map() is automatically Mappable
# No inheritance needed!
```

**Benefits**:
- Duck typing for functional patterns
- Works with existing classes
- Type checking with mypy
- Runtime introspection

### 2. Functional Entities, Not Functions

Each **functional concept** is an **entity** (class/object):

| Functional Concept | Object Entity | Example |
|-------------------|---------------|---------|
| Maybe value | `Maybe[T]` | `Some(42)`, `None_` |
| Result | `Result[T, E]` | `Ok(value)`, `Error(exception)` |
| Validator | `Validator[T]` | `StringValidator.create().min_length(5)` |
| Mappable collection | `MappableList[T]` | `[1, 2, 3].map(lambda x: x * 2)` |
| Parser | `Parser[T]` | `String("hello").parse(Int)` |

These aren't just data containers—they're **active entities** with behavior.

### 3. Composition Through Methods, Not Functions

```python
# ❌ Traditional FP: Functions everywhere
result = pipe(
    value,
    map(operation1),
    filter(predicate),
    reduce(combiner)
)

# ✅ Our approach: Method chaining
result = value.map(operation1).filter(predicate).reduce(combiner)
```

**Why?**
- Discoverability: IDE autocomplete shows available operations
- Intuitive: Python developers already do `list.append()`, not `append(list)`
- Type-safe: Method signatures are checked

### 4. Immutable State, Mutable Operations

Objects are **immutable** (frozen dataclasses), but operations **return new instances**:

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict(K, V):
    """Immutable dictionary that returns new instances on updates"""

    def update(self, **kwargs) -> 'ImmutableDict[K, V]':
        """Returns NEW instance, doesn't mutate self"""
        return ImmutableDict({**self._data, **kwargs})

    def set_in(self, path: str, value: Any) -> 'ImmutableDict[K, V]':
        """Immutable deep update"""
        ...

# Usage
d1 = ImmutableDict({"a": 1})
d2 = d1.update(b=2)  # d1 unchanged!
d3 = d2.set_in("nested.value", 42)  # d2 unchanged!
```

### 5. Generics & Type Safety

Every functional entity is **generic** and **type-safe**:

```python
class MappableList(Generic[T], Sequence[T]):
    def map(self, func: Callable[[T], U]) -> 'MappableList[U]': ...
    def filter(self, pred: Callable[[T], bool]) -> 'MappableList[T]': ...

# Type inference works
numbers: MappableList[int] = MappableList([1, 2, 3])
doubled: MappableList[str] = numbers.map(lambda x: str(x * 2))
```

mypy knows that `map(str)` transforms `MappableList[int]` → `MappableList[str]`.

### 6. Descriptors & Metaprogramming

We use **descriptors** for declarative behavior:

```python
class ValidatedField:
    """Descriptor for validated fields"""

    def __init__(self, validator: Validator):
        self.validator = validator

    def __get__(self, obj, owner):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, obj, value):
        result = self.validator.validate(value)
        if result.is_errors():
            raise ValidationError(result.errors)
        obj.__dict__[self.name] = value

# Usage
class User:
    name: ValidatedString = ValidatedField(
        StringValidator.create().min_length(2).max_length(50)
    )
    age: ValidatedInt = ValidatedField(
        IntValidator.create().range(18, 120)
    )
```

Validation is **declared** as metadata, not imperative code.

### 7. Context Managers & Side Effects

Side effects are **explicit** through context managers:

```python
class Resourceful(Generic[T], ContextManager):
    """Protocol for resources with automatic cleanup"""

    def __enter__(self) -> T: ...
    def __exit__(self, *exc) -> bool | None: ...

# Usage
with DatabaseConnection(url) as db:
    result = db.query("SELECT * FROM users")
    # Automatically cleaned up
```

No manual `try/finally`—side effects are **structured**.

---

## Comparison Table

| Aspect | Pure FP | Traditional OOP | **Our Approach** |
|--------|---------|-----------------|------------------|
| **Primary unit** | Functions | Classes | **Functional Entities** |
| **State** | Immutable | Mutable | **Immutable objects** |
| **Composition** | Function composition | Method chaining | **Protocol-based methods** |
| **Type system** | Type classes | Inheritance | **Protocols + Generics** |
| **Side effects** | Monads (IO) | Everywhere | **Context managers** |
| **Validation** | Aplicative/Monad | N/A | **Validator classes** |
| **Error handling** | Either/Maybe | Exceptions | **Result objects + Exceptions** |
| **Discovery** | Read docs | IDE autocomplete | **Protocol + autocomplete** |

---

## Examples: Functional Entities in Action

### Example 1: Validation as Object

```python
# Not a function validator(data) that returns errors
# But a Validator object with behavior

email_validator = (
    StringValidator.create()
    .min_length(5)
    .email()
    .required()
)

result = email_validator.validate(user_input)

if result.is_success():
    value = result.get()
else:
    for error in result.errors:
        print(error)
```

### Example 2: Maybe as Object

```python
# Not a function that returns Optional[T]
# But a Maybe object with methods

user = fetch_user(id)
if user.is_some():
    name = user.unwrap().name
else:
    print("Not found")

# Or with pipe operators
result = (
    Some(user_id)
    | fetch_user
    | validate_user
    | get_profile
)
```

### Example 3: Immutable Updates as Object

```python
# Not immutable(data, update)
# But an ImmutableDict object with methods

config = ImmutableDict({
    "database": {"host": "localhost", "port": 5432}
})

# Returns new instance, doesn't mutate
new_config = config.set_in("database.host", "remotehost")

# Original unchanged
config["database"]["host"]  # "localhost"
new_config["database"]["host"]  # "remotehost"
```

---

## Benefits of This Approach

### For Python Developers

✅ **Familiar**: Objects, methods, protocols—idiomatic Python
✅ **Discoverable**: IDE autocomplete shows available operations
✅ **Type-safe**: Full generic type hints and mypy support
✅ **Composable**: Method chaining reads naturally
✅ **Explicit**: Side effects through context managers

### For Functional Programming

✅ **Immutable**: Objects are frozen, operations return new instances
✅ **Composable**: Protocols enable composition patterns
✅ **Type-safe**: Generic types track transformations
✅ **Pure**: Side effects are explicit and controlled
✅ **Expressive**: Complex behavior from simple entities

### The Best of Both Worlds

- **OOP structure** (classes, protocols, inheritance)
- **FP patterns** (immutability, composition, type safety)
- **Pythonic** (descriptors, context managers, generators)
- **Practical** (solves real problems, not academic)

---

## Anti-Patterns We Avoid

### ❌ Don't: Pure Functions for Everything

```python
# This feels alien in Python
def map(func, iterable):
    return [func(x) for x in iterable]

def filter(predicate, iterable):
    return [x for x in iterable if predicate(x)]

result = pipe(
    numbers,
    partial(map, lambda x: x * 2),
    partial(filter, lambda x: x > 0)
)
```

### ✅ Do: Objects with Methods

```python
# This feels Pythonic
result = (
    MappableList(numbers)
    .map(lambda x: x * 2)
    .filter(lambda x: x > 0)
)
```

### ❌ Don't: Rigid Class Hierarchies

```python
# Java-style: Too much inheritance
class Animal:
    def speak(self): pass

class Dog(Animal):
    def speak(self): return "Woof"

class Cat(Animal):
    def speak(self): return "Meow"
```

### ✅ Do: Protocol Compliance

```python
# Python-style: Protocol compliance

@runtime_checkable
class Speakable(Protocol):
    def speak(self) -> str: ...

class Dog:
    def speak(self) -> str: return "Woof"

class Cat:
    def speak(self) -> str: return "Meow"

# Both are Speakable! No inheritance needed.
```

### ❌ Don't: Academic Terminology

```python
# Confusing: "Kleisli category", "Applicative functor"
class KleisliArrow(Generic[S, T]):
    def bind(self, func): ...
```

### ✅ Do: Practical Names

```python
# Clear: "Validator", "Mappable", "Result"
class Validator(Generic[T]):
    def validate(self, value: T) -> Validation: ...
```

---

## Summary: The Mental Model

Think of **functional concepts as living entities**:

- **Maybe** isn't a "monad"—it's an object that **might** have a value
- **Result** isn't an "either monad"—it's an object that **is** success or failure
- **Validator** isn't a "functor"—it's an object that **validates** data
- **MappableList** isn't a "functor from Set to Set"—it's a list that **can be mapped**

These entities **behave** functionally (immutable, composable, type-safe) but **feel** like objects (methods, protocols, autocomplete).

**Everything is an object. Operations are functional.**

That's the **Functional Entity** approach.

---

## Reading List

If you're designing features with this mentality:

1. **`collections.abc`** - Protocol-based container design
2. **`typing.Protocol`** - Structural subtyping
3. **`dataclasses`** - Immutable data structures
4. **`contextlib`** - Context managers for side effects
5. **`functools`** - Higher-order functions (but wrapped in objects)
6. **Raymond Hettinger's talks** - Pythonic design patterns
7. **`attrs` or `pydantic`** - Modern class design inspiration
