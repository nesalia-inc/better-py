# Philosophy: Functional Entities as Objects

This document summarizes the core philosophy of **MFN**: blending functional programming patterns with object-oriented design.

## The Core Idea

> **Everything is an object. Operations are functional.**

We don't write *functions* that manipulate data. We create **objects that represent functional concepts**.

## Why This Approach?

### ❌ Pure Functional Programming in Python
```python
# Feels alien to Python developers
result = pipe(
    data,
    map(lambda x: x * 2),
    filter(lambda x: x > 0),
    reduce(lambda a, b: a + b)
)
```

**Problems**:
- Feels like Haskell/Rust移植
- Unfamiliar to Python developers
- Verbose for simple operations
- Hard to discover available operations

### ❌ Traditional OOP (Java-style)
```python
# Over-engineered
abstract class AbstractDataProcessor:
    @abstractmethod
    def process(self): pass

class ConcreteDataProcessor(AbstractDataProcessor):
    def process(self): ...
```

**Problems**:
- Rigid class hierarchies
- Boilerplate for simple tasks
- Design patterns galore
- Verbose

### ✅ Our Approach: Functional Entities
```python
# Natural Python, functional behavior
result = (
    MappableList(data)
    .map(lambda x: x * 2)
    .filter(lambda x: x > 0)
    .reduce(lambda a, b: a + b)
)
```

**Benefits**:
- ✅ **Familiar**: Objects and methods are Pythonic
- ✅ **Discoverable**: IDE autocomplete shows operations
- ✅ **Immutable**: Objects are frozen, methods return new instances
- ✅ **Composable**: Chain operations naturally
- ✅ **Type-safe**: Full generic type hints

## Key Principles

### 1. Protocol-Based Design

Inspired by `collections.abc`, we use **Protocols** (structural typing):

```python
@runtime_checkable
class Mappable(Protocol[T]):
    """Any object that can be mapped over"""
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

# Any class with map() is automatically Mappable
class SmartList:
    def map(self, func): ...
    # SmartList is now Mappable! No inheritance needed.
```

### 2. Functional Entities, Not Functions

Each functional concept is an **entity** (object) with behavior:

| Functional Concept | Object Entity |
|-------------------|---------------|
| Optional value | `Maybe[T]` |
| Success/Failure | `Result[T, E]` |
| Validator | `Validator[T]` |
| Mappable collection | `MappableList[T]` |
| Immutable dict | `ImmutableDict[K, V]` |

### 3. Immutability by Default

Objects are **frozen** (dataclasses with `frozen=True, slots=True`):

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict:
    def update(self, **kwargs) -> 'ImmutableDict':
        # Returns NEW instance, doesn't mutate
        return ImmutableDict({**self._data, **kwargs})

d1 = ImmutableDict({"a": 1})
d2 = d1.update(b=2)  # d1 unchanged!
```

### 4. Composition Through Methods

Not `pipe(value, f, g, h)` but `value.map(f).filter(g)`:

```python
# Method chaining is natural in Python
result = (
    fetch_user(user_id)
    .validate()
    .transform(to_dto)
    .save()
)
```

### 5. Side Effects Are Explicit

Use **context managers** for side effects:

```python
with DatabaseConnection(url) as db:
    result = db.query("SELECT * FROM users")
    # Automatically cleaned up
```

## Examples

### Example 1: Maybe as Object

```python
# Not: def maybe_bind(m, f): return f(m.value) if m.value else None
# But: An object with methods

user = fetch_user(42)
if user.is_some():
    name = user.unwrap().name
else:
    print("Not found")

# Or with pipe operators
result = (
    Some(42)
    | fetch_user
    | validate_user
    | get_profile
)
```

### Example 2: Validation as Object

```python
# Not: def validate(data, rules): return errors
# But: A Validator object

email_validator = (
    StringValidator.create()
    .min_length(5)
    .email()
    .required()
)

result = email_validator.validate(user_input)
if result.is_success():
    value = result.get()
```

### Example 3: Immutable Updates

```python
# Not: immutable_update(data, "path.to.key", value)
# But: An object with methods

config = ImmutableDict({"database": {"host": "localhost"}})
new_config = config.set_in("database.host", "remotehost")

# Original unchanged
config["database"]["host"]  # "localhost"
new_config["database"]["host"]  # "remotehost"
```

## The Benefits

### For Python Developers
- ✅ Familiar: Objects, methods, protocols
- ✅ Discoverable: IDE autocomplete
- ✅ Type-safe: Full generic type hints
- ✅ Pythonic: Feels like idiomatic Python

### For Functional Programming
- ✅ Immutable: Frozen dataclasses
- ✅ Composable: Method chaining
- ✅ Type-safe: Generic types track transformations
- ✅ Pure: Side effects are explicit

### The Best of Both Worlds
- **OOP structure** (classes, protocols, inheritance)
- **FP patterns** (immutability, composition, type safety)
- **Pythonic** (descriptors, context managers, generators)
- **Practical** (solves real problems, not academic)

## Comparison

| Aspect | Pure FP | Traditional OOP | **Our Approach** |
|--------|---------|-----------------|------------------|
| Primary unit | Functions | Classes | **Functional Entities** |
| State | Immutable | Mutable | **Immutable objects** |
| Composition | Function comp | Method chaining | **Protocol methods** |
| Type system | Type classes | Inheritance | **Protocols + Generics** |
| Side effects | Monads (IO) | Everywhere | **Context managers** |
| Discovery | Read docs | Autocomplete | **Protocol + autocomplete** |

## Summary

Think of functional concepts as **living entities**:

- **Maybe** - Object that might have a value
- **Result** - Object that is success or failure
- **Validator** - Object that validates data
- **MappableList** - List that can be mapped

These entities **behave** functionally but **feel** like objects.

**Everything is an object. Operations are functional.**

---

**Next**: See [Protocols](./01-protocols.md) for protocol-based design details.
