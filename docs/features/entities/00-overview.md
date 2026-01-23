# Functional Entities: Overview

**Functional Entities** are objects that represent functional concepts. Each entity is immutable, type-safe, and implements protocols for composability.

## Core Entities

### 1. Maybe
Represents optional values - `Some(value)` or `None_`.

**Use when**: A value might not exist.

```python
user = fetch_user(42)
if user.is_some():
    name = user.unwrap().name
```

**See**: [Maybe](./01-mappable.md#maybe-entity)

---

### 2. Result
Represents success (`Ok(value)`) or failure (`Error(exception)`).

**Use when**: An operation can fail with known errors.

```python
result = fetch_user(42)
if result.is_ok():
    user = result.unwrap()
else:
    handle_error(result.error)
```

**See**: [Result](../monads/02-result.md)

---

### 3. Validator
Validates data of a specific type.

**Use when**: You need to validate input with rules.

```python
email_validator = (
    StringValidator.create()
    .min_length(5)
    .email()
    .required()
)

result = email_validator.validate(user_input)
```

**See**: [Validator](./07-validable.md)

---

## Collection Entities

### 4. Mappable
**Protocol**: Objects that can be transformed.

**Implementations**: `MappableList`, `MappableDict`, `MappableSet`

```python
numbers = MappableList([1, 2, 3])
doubled = numbers.map(lambda x: x * 2)
```

**See**: [Mappable](./01-mappable.md)

---

### 5. Reducible
**Protocol**: Objects that can be reduced to a single value.

**Implementations**: `ReducibleList`, `ReducibleDict`

```python
numbers = ReducibleList([1, 2, 3, 4])
sum_ = numbers.reduce(lambda a, b: a + b)  # 10
```

**See**: [Reducible](./02-reducible.md)

---

### 6. Combinable
**Protocol**: Objects that can be combined.

**Implementations**: `CombinableList`, `CombinableDict`, `CombinableInt`

```python
list1 = CombinableList([1, 2])
list2 = CombinableList([3, 4])
combined = list1.combine(list2)  # [1, 2, 3, 4]
```

**See**: [Combinable](./03-combinable.md)

---

### 7. Updatable
**Protocol**: Objects that support immutable updates.

**Implementations**: `ImmutableDict`, `ImmutableList`, `ImmutableDataclass`

```python
config = ImmutableDict({"host": "localhost"})
new_config = config.set_in("database.port", 5432)
```

**See**: [Updatable](./04-updatable.md)

---

### 8. Traversable
**Protocol**: Objects that can be traversed with effects.

**Implementations**: `TraversableList`, `TraversableDict`

```python
list_of_results = TraversableList([Ok(1), Ok(2), Ok(3)])
result = list_of_results.sequence()  # Ok([1, 2, 3])
```

**See**: [Traversable](./05-traversable.md)

---

## I/O Entities

### 9. Parseable
**Protocol**: Objects that can be parsed from text.

**Implementations**: `ParseableInt`, `ParseableFloat`, `ParseableEmail`

```python
email = ParseableEmail.parse("user@example.com")
if email.is_success():
    value = email.get()
```

**See**: [Parseable](./06-parseable.md)

---

### 10. Cacheable
**Protocol**: Objects that can be cached.

**Implementations**: `CacheableModel`, `CacheableDict`

```python
@dataclass(frozen=True)
class User(Cacheable):
    id: int
    name: str

    @property
    def cache_key(self) -> str:
        return f"user:{self.id}"
```

**See**: [Cacheable](./08-cacheable.md)

---

### 11. Parallelizable
**Protocol**: Objects that can be processed in parallel.

**Implementations**: `ParallelList`, `AsyncList`

```python
items = ParallelList([1, 2, 3, 4, 5])
results = items.par_map(lambda x: expensive_computation(x))
```

**See**: [Parallelizable](./09-parallelizable.md)

---

## Reference Table

| Entity | Protocol | Purpose | Generic |
|--------|----------|---------|---------|
| **Maybe** | Optional | Optional values | `T` |
| **Result** | - | Success/failure | `T, E` |
| **Try** | - | Exception handling | `T` |
| **Validator** | Validable | Data validation | `T` |
| **Mappable** | Mappable | Transformable | `T → U` |
| **Reducible** | Reducible | Reducible | `T` |
| **Combinable** | Combinable | Combinable | `T` |
| **Updatable** | Updatable | Immutable updates | `T` |
| **Traversable** | Traversable | Traverse with effects | `T` |
| **Parseable** | Parseable | Parse from text | `T` |
| **Cacheable** | Cacheable | Cacheable | `T` |
| **Parallelizable** | Parallelizable | Parallel processing | `T → U` |
| **Resilient** | Resilient | Retry/timeout | `T` |
| **Configurable** | Configurable | Configuration | `T` |

## Entity Characteristics

All functional entities share these characteristics:

### ✅ Immutable

```python
@dataclass(frozen=True, slots=True)
class ImmutableDict:
    _data: dict

    def update(self, **kwargs) -> 'ImmutableDict':
        # Returns NEW instance
        return ImmutableDict({**self._data, **kwargs})
```

### ✅ Generic

```python
class MappableList(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'MappableList[U]': ...
```

### ✅ Protocol-Based

```python
@runtime_checkable
class Mappable(Protocol[T]):
    def map(self, func): ...

# Any class with map() is Mappable
```

### ✅ Composable

```python
# Method chaining
result = (
    fetch_user(id)
    .map(lambda u: u.name)
    .filter(lambda n: len(n) > 0)
)

# Pipe operator
result = Some(id) | fetch_user | validate_user
```

### ✅ Type-Safe

```python
# Type inference works
numbers: MappableList[int] = MappableList([1, 2, 3])
strings: MappableList[str] = numbers.map(str)
```

## Usage Patterns

### Pattern 1: Single Operation

```python
# Direct usage
result = fetch_user(42)
if result.is_ok():
    user = result.unwrap()
```

### Pattern 2: Chaining

```python
# Method chaining
result = (
    MappableList([1, 2, 3, 4, 5])
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x * 2)
    .reduce(lambda a, b: a + b)
)
```

### Pattern 3: Composition

```python
# Function composition
pipeline = compose(
    fetch_user,
    validate_user,
    get_profile
)

result = pipeline(user_id)
```

### Pattern 4: Pipe Operator

```python
# Visual pipeline
result = (
    Some(user_id)
    | fetch_user
    | validate_user
    | get_profile
)
```

## Creating Custom Entities

### Step 1: Define Protocol

```python
@runtime_checkable
class MyProtocol(Protocol[T]):
    def my_operation(self) -> T: ...
```

### Step 2: Implement Entity

```python
@dataclass(frozen=True, slots=True)
class MyEntity(Generic[T]):
    _data: T

    def my_operation(self) -> T:
        return self._data
```

### Step 3: Use Entity

```python
entity = MyEntity(42)
result = entity.my_operation()  # 42
```

## Summary

**Functional Entities** are:
- Objects representing functional concepts
- Immutable (frozen dataclasses)
- Generic (type-safe)
- Protocol-compliant (duck typing)
- Composable (method chaining, pipe operators)

**Core idea**: Think of functional concepts as **living entities** with behavior, not just functions.

---

**Next**: See [Mappable](./01-mappable.md) for the transformable protocol.
