# Generic Types: Type-Safe Functional Entities

Generic types enable **type-safe** functional entities that track transformations through the type system. Combined with protocols, they provide **compile-time guarantees** without runtime overhead.

## Why Generic Types?

### Without Generics

```python
# No type safety
def map(func, iterable):
    return [func(x) for x in iterable]

numbers = [1, 2, 3]
strings = map(str, numbers)  # What type is strings?
```

### With Generics

```python
# Type-safe
class MappableList(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'MappableList[U]': ...

numbers: MappableList[int] = MappableList([1, 2, 3])
strings: MappableList[str] = numbers.map(str)

# mypy knows:
# - numbers is MappableList[int]
# - strings is MappableList[str]
```

## Type Variables

### Basic TypeVar

```python
from typing import TypeVar, Generic

T = TypeVar('T')  # Any type

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

# Usage
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("hello")

int_box.get()  # Returns int
str_box.get()  # Returns str
```

### Multiple Type Variables

```python
T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')

class Result(Generic[T, E]):
    """Result with value type T and error type E"""
    def __init__(self, value: T | None, error: E | None):
        self.value = value
        self.error = error

    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """Transform value, keep error type"""
        if self.error:
            return Result(None, self.error)
        return Result(func(self.value), None)

# Usage
result: Result[int, Exception] = fetch_user()
mapped: Result[str, Exception] = result.map(lambda u: u.name)
```

### Bounded TypeVar

```python
T = TypeVar('T', bound=Animal)  # Must be Animal or subclass

class Shelter(Generic[T]):
    def adopt(self) -> T:
        """Returns animal of type T"""
        ...

class Dog(Animal): ...

dog_shelter: Shelter[Dog] = Shelter()
my_dog: Dog = dog_shelter.adopt()  # Returns Dog, not just Animal
```

### Constrained TypeVar

```python
T = TypeVar('T', int, float, str)  # Must be one of these

def double(value: T) -> T:
    """Double a value (only for int, float, str)"""
    return value + value  # Works for all three types

double(42)       # int -> 84
double(3.14)     # float -> 6.28
double("hello")  # str -> "hellohello"
double([1, 2])   # ❌ Type error!
```

## Covariance and Contravariance

### Covariant (Output Types)

```python
T_co = TypeVar('T_co', covariant=True)  # Read-only

class Box(Generic[T_co]):
    def __init__(self, value: T_co):
        self._value = value

    def get(self) -> T_co:
        return self._value

# Box[int] is subtype of Box[object]
def print_box(box: Box[object]):
    print(box.get())

int_box: Box[int] = Box(42)
print_box(int_box)  # ✅ Box[int] is compatible with Box[object]
```

### Contravariant (Input Types)

```python
T_contra = TypeVar('T_contra', contravariant=True)  # Write-only

class Sink(Generic[T_contra]):
    def send(self, value: T_contra):
        ...

# Sink[object] is subtype of Sink[int]
def int_sink(sink: Sink[int]):
    sink.send(42)

object_sink: Sink[object] = Sink()
int_sink(object_sink)  # ✅ Sink[object] is compatible with Sink[int]
```

### Invariant (Mutable Types)

```python
T = TypeVar('T')  # Invariant by default

class Cell(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

    def set(self, value: T):
        self.value = value

# Cell[int] is NOT compatible with Cell[object]
def use_cell(cell: Cell[object]):
    cell.set("string")  # Would break Cell[int]!

int_cell: Cell[int] = Cell(42)
use_cell(int_cell)  # ❌ Type error!
```

## Generic Protocols

### Protocol with Type Variables

```python
@runtime_checkable
class Mappable(Protocol[T]):
    """Any object that can be mapped over"""

    def map(self, func: Callable[[T], U]) -> 'Mappable[U]': ...

    def filter(self, predicate: Callable[[T], bool]) -> 'Mappable[T]': ...

# Classes implement Mappable by having map()
class SmartList(Generic[T]):
    def __init__(self, items: list[T]):
        self._data = items

    def map(self, func: Callable[[T], U]) -> 'SmartList[U]':
        return SmartList([func(x) for x in self._data])

    def filter(self, predicate: Callable[[T], bool]) -> 'SmartList[T]':
        return SmartList([x for x in self._data if predicate(x)])

# Type-safe
numbers: SmartList[int] = SmartList([1, 2, 3])
strings: SmartList[str] = numbers.map(str)
evens: SmartList[int] = numbers.filter(lambda x: x % 2 == 0)
```

### Multiple Protocol Methods

```python
@runtime_checkable
class Reducible(Protocol[T]):
    """Structure that can be reduced"""

    def reduce(self, func: Callable[[T, T], T]) -> T: ...

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U: ...

    @abstractmethod
    def fold_right(self, initial: U, func: Callable[[T, U], U]) -> U: ...

class SmartList(Generic[T]):
    # Implements Reducible[T]

    def reduce(self, func: Callable[[T, T], T]) -> T:
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

    def fold_left(self, initial: U, func: Callable[[U, T], U]) -> U:
        result = initial
        for item in self._data:
            result = func(result, item)
        return result

    def fold_right(self, initial: U, func: Callable[[T, U], U]) -> U:
        result = initial
        for item in reversed(self._data):
            result = func(item, result)
        return result

# Type-safe
numbers: SmartList[int] = SmartList([1, 2, 3, 4])
sum_: int = numbers.reduce(lambda a, b: a + b)  # Returns int
result: str = numbers.fold_left("", lambda s, n: f"{s}{n}")  # Returns str
```

## Generic Classes

### Maybe Monad

```python
@dataclass(frozen=True, slots=True)
class Maybe(Generic[T]):
    """Maybe monad with generic type T"""

    value: T | None

    def is_some(self) -> bool:
        return self.value is not None

    def is_none(self) -> bool:
        return self.value is None

    def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """Transform Maybe[T] to Maybe[U]"""
        if self.value is None:
            return None_
        return Some(func(self.value))

    def flat_map(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        """Chain Maybe-returning functions"""
        if self.value is None:
            return None_
        return func(self.value)

    def unwrap_or(self, default: T) -> T:
        return self.value if self.value is not None else default

# Type inference
maybe_int: Maybe[int] = Some(42)
maybe_str: Maybe[str] = maybe_int.map(str)
maybe_user: Maybe[User] = maybe_int.map(lambda i: User(i))

# mypy tracks transformations
```

### Result Type

```python
@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    """Result with success type T and error type E"""

    value: T | None
    error: E | None

    def is_ok(self) -> bool:
        return self.error is None

    def is_error(self) -> bool:
        return self.error is not None

    def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
        """Transform value, keep error type"""
        if self.is_error():
            return Error(self.error)
        return Ok(func(self.value))

    def map_error(self, func: Callable[[E], F]) -> 'Result[T, F]':
        """Transform error, keep value type"""
        if self.is_ok():
            return Ok(self.value)
        return Error(func(self.error))

    def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Chain Result-returning functions"""
        if self.is_error():
            return Error(self.error)
        return func(self.value)

# Type inference
result1: Result[int, Exception] = fetch_user()
result2: Result[str, Exception] = result1.map(lambda u: u.name)
result3: Result[User, ValueError] = result1.map_error(lambda e: ValueError(str(e)))
```

### Validator Generic

```python
T = TypeVar('T')

@runtime_checkable
class Validator(Protocol[T]):
    """Validator protocol for type T"""

    def validate(self, value: T) -> Validation: ...

class BaseValidator(Generic[T]):
    """Base validator with generic type T"""

    def __init__(self):
        self._rules: list[Callable[[T], Exception | None]] = []

    def add_rule(self, predicate: Callable[[T], bool], error: Exception) -> 'BaseValidator[T]':
        def rule(value: T):
            if not predicate(value):
                return error
            return None
        self._rules.append(rule)
        return self

    def validate(self, value: T) -> Validation:
        for rule in self._rules:
            error = rule(value)
            if error is not None:
                return Validation.errors_(error)
        return Validation.success(value)

class StringValidator(BaseValidator[str]):
    """Validator specifically for strings"""

    def min_length(self, n: int) -> 'StringValidator':
        return self.add_rule(
            lambda s: len(s) >= n,
            ValidationError(f"Must be at least {n} characters")
        )

    def email(self) -> 'StringValidator':
        return self.add_rule(
            lambda s: "@" in s,
            ValidationError("Invalid email format")
        )

# Type-safe validators
email_validator: Validator[str] = StringValidator()
result = email_validator.validate("test@example.com")
```

## Generic Methods

### Methods with Own Type Variables

```python
class MappableList(Generic[T]):
    def __init__(self, items: list[T]):
        self._data = items

    # U is method-specific type variable
    def map(self, func: Callable[[T], U]) -> 'MappableList[U]':
        return MappableList([func(x) for x in self._data])

    # V is different method-specific type variable
    def flat_map(self, func: Callable[[T], 'MappableList[V]']) -> 'MappableList[V]':
        result = []
        for item in self._data:
            result.extend(func(item)._data)
        return MappableList(result)

# Usage
numbers: MappableList[int] = MappableList([1, 2, 3])
strings: MappableList[str] = numbers.map(str)
nested: MappableList[MappableList[int]] = numbers.map(lambda n: MappableList([n, n*2]))
flattened: MappableList[int] = numbers.flat_map(lambda n: MappableList([n, n*2]))
```

### Constraints on Generic Methods

```python
class SmartList(Generic[T]):
    def find_first(self, predicate: Callable[[T], bool]) -> 'Maybe[T]':
        """Find first item matching predicate"""
        for item in self._data:
            if predicate(item):
                return Some(item)
        return None_

    def max(self) -> T:
        """Get maximum - requires T to be comparable"""
        if not self._data:
            raise ValueError("Empty list")

        # This only works if T supports >
        result = self._data[0]
        for item in self._data[1:]:
            if item > result:  # ❌ Type error if T doesn't support >
                result = item
        return result

# Better: Use Protocol
class SupportsLessThan(Protocol[T]):
    def __lt__(self, other: T) -> bool: ...

T_ord = TypeVar('T_ord', bound=SupportsLessThan)

class SmartList(Generic[T_ord]):
    def max(self) -> T_ord:
        """Get maximum - T_ord must support <"""
        if not self._data:
            raise ValueError("Empty list")

        result = self._data[0]
        for item in self._data[1:]:
            if result < item:
                result = item
        return result
```

## Self-Referential Generics

### Recursive Types

```python
from typing import TypeVar

T = TypeVar('T')

class Tree(Generic[T]):
    """Binary tree with generic value type"""

    def __init__(
        self,
        value: T,
        left: 'Tree[T] | None' = None,
        right: 'Tree[T] | None' = None
    ):
        self.value = value
        self.left = left
        self.right = right

    def map(self, func: Callable[[T], U]) -> 'Tree[U]':
        """Transform tree"""
        return Tree(
            func(self.value),
            self.left.map(func) if self.left else None,
            self.right.map(func) if self.right else None
        )

    def traverse_inorder(self) -> list[T]:
        """Collect values in-order"""
        result = []
        if self.left:
            result.extend(self.left.traverse_inorder())
        result.append(self.value)
        if self.right:
            result.extend(self.right.traverse_inorder())
        return result

# Usage
tree = Tree(
    2,
    Tree(1),
    Tree(3, Tree(2.5), Tree(3.5))
)

# Type-safe transformations
string_tree: Tree[str] = tree.map(str)
values: list[int] = tree.traverse_inorder()  # [1, 2, 2.5, 3, 3.5]
```

## Generic Inheritance

### Extending Generic Classes

```python
class Mappable(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'Mappable[U]':
        raise NotImplementedError

class Reducible(Generic[T]):
    def reduce(self, func: Callable[[T, T], T]) -> T:
        raise NotImplementedError

# Multiple inheritance with generics
class SmartList(Mappable[T], Reducible[T], Generic[T]):
    def __init__(self, items: list[T]):
        self._data = items

    def map(self, func: Callable[[T], U]) -> 'SmartList[U]':
        return SmartList([func(x) for x in self._data])

    def reduce(self, func: Callable[[T, T], T]) -> T:
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

# SmartList[T] is both Mappable[T] and Reducible[T]
def process(items: Mappable[int]) -> Mappable[str]:
    return items.map(str)

def aggregate(items: Reducible[int]) -> int:
    return items.reduce(lambda a, b: a + b)

numbers = SmartList([1, 2, 3])
process(numbers)  # ✅ SmartList is Mappable
aggregate(numbers)  # ✅ SmartList is Reducible
```

## Best Practices

### ✅ Do: Use TypeVars for flexibility

```python
T = TypeVar('T')

class Box(Generic[T]):
    def get(self) -> T: ...
```

### ✅ Do: Bound TypeVars appropriately

```python
T = TypeVar('T', bound=Animal)  # Must be Animal

class Shelter(Generic[T]):
    def adopt(self) -> T: ...
```

### ✅ Do: Use covariant for read-only

```python
T_co = TypeVar('T_co', covariant=True)

class Box(Generic[T_co]):
    def get(self) -> T_co: ...
```

### ❌ Don't: Use covariant for mutable

```python
T_co = TypeVar('T_co', covariant=True)  # ❌ Wrong!

class Cell(Generic[T_co]):  # ❌ Should be invariant
    def set(self, value: T_co): ...  # ❌ Type unsound!
```

### ❌ Don't: Over-constrain TypeVars

```python
# Too restrictive
T = TypeVar('T', int, float)  # Only int or float

class Box(Generic[T]): ...  # Can't use Box[str]

# Better
T = TypeVar('T')  # Any type

class Box(Generic[T]): ...
```

## Summary

**Generic Types** provide:
- ✅ Type-safe transformations
- ✅ Compile-time guarantees
- ✅ Better IDE support
- ✅ Self-documenting code

**Key concepts**:
- `TypeVar` - Generic type parameters
- `bound=` - Constraint to base class
- Covariant - Read-only types (outputs)
- Contravariant - Write-only types (inputs)
- Invariant - Mutable types (default)

**For functional entities**:
- Track transformations through types
- `Maybe[T].map(f: T→U) → Maybe[U]`
- `Result[T, E].map(f: T→U) → Result[U, E]`
- `Validator[T]` validates type `T`

---

**Next**: See [Composition](./05-composition.md) for composition patterns.
