# Traversable: Collections with Effects

**Traversable** is a protocol for collections that can be **traversed with effects** - transforming collections of effectful values into effects of collections.

## Overview

```python
@runtime_checkable
class Traversable(Protocol[T]):
    """Collections that can be traversed with effects"""

    def traverse(self, func: Callable[[T], Result[U, E]]) -> Result[list[U], E]:
        """Transform each element, collect effects"""
        ...

    def sequence(self, results: Iterable[Result[T, E]]) -> Result[list[T], E]:
        """Invert: collection of effects → effect of collection"""
        ...
```

## Core Concepts

### traverse vs map

```python
# map: No effects
numbers = [1, 2, 3, 4]
doubled = map(lambda x: x * 2, numbers)  # [2, 4, 6, 8]

# traverse: With effects
def safe_divide(x: int) -> Result[float, Exception]:
    if x == 0:
        return Error(DivisionByZero())
    return Ok(10.0 / x)

numbers = [1, 2, 0, 4]
result = traverse(safe_divide, numbers)  # Error(DivisionByZero)
```

### sequence

```python
# sequence: Convert list[Result[T]] to Result[list[T]]
results = [Ok(1), Ok(2), Ok(3)]
sequenced = sequence(results)  # Ok([1, 2, 3])

results = [Ok(1), Error("fail"), Ok(3)]
sequenced = sequence(results)  # Error("fail")
```

## Implementations

### TraversableList

```python
@dataclass(frozen=True, slots=True)
class TraversableList(Generic[T]):
    """List with traverse operations"""

    _data: list[T]

    # === traverse ===

    def traverse(
        self,
        func: Callable[[T], Result[U, E]]
    ) -> Result['TraversableList[U]', E]:
        """Transform each element, collect Results"""
        results = []

        for item in self._data:
            result = func(item)
            if result.is_error():
                return Error(result.error)
            results.append(result.unwrap())

        return Ok(TraversableList(results))

    def traverse_maybe(
        self,
        func: Callable[[T], Maybe[U]]
    ) -> 'Maybe[TraversableList[U]]':
        """Transform with Maybe-returning function"""
        results = []

        for item in self._data:
            maybe = func(item)
            if maybe.is_none():
                return None_
            results.append(maybe.unwrap())

        return Some(TraversableList(results))

    def traverse_async(
        self,
        func: Callable[[T], Awaitable[Result[U, E]]]
    ) -> Awaitable[Result['TraversableList[U]', E]]:
        """Transform with async Result-returning function"""
        import asyncio

        async def inner():
            results = []
            for item in self._data:
                result = await func(item)
                if result.is_error():
                    return Error(result.error)
                results.append(result.unwrap())
            return Ok(TraversableList(results))

        return inner()

    # === sequence ===

    def sequence_results(
        self,
        results: Iterable[Result[T, E]]
    ) -> Result['TraversableList[T]', E]:
        """Convert Iterable[Result[T]] to Result[TraversableList[T]]"""
        values = []

        for result in results:
            if result.is_error():
                return Error(result.error)
            values.append(result.unwrap())

        return Ok(TraversableList(values))

    def sequence_maybes(
        self,
        maybes: Iterable[Maybe[T]]
    ) -> 'Maybe[TraversableList[T]]':
        """Convert Iterable[Maybe[T]] to Maybe[TraversableList[T]]"""
        values = []

        for maybe in maybes:
            if maybe.is_none():
                return None_
            values.append(maybe.unwrap())

        return Some(TraversableList(values))

    # === Validation traverse ===

    def traverse_validate(
        self,
        func: Callable[[T], Validation]
    ) -> Validation:
        """Traverse with Validation (accumulate errors)"""
        all_values = []
        all_errors = []

        for item in self._data:
            validation = func(item)
            if validation.is_errors():
                all_errors.extend(validation.errors)
            else:
                all_values.append(validation.get())

        if all_errors:
            return Validation.errors_(*all_errors)
        return Validation.success(TraversableList(all_values))

    def sequence_validations(
        self,
        validations: Iterable[Validation]
    ) -> Validation:
        """Sequence Validations (accumulate errors)"""
        all_values = []
        all_errors = []

        for validation in validations:
            if validation.is_errors():
                all_errors.extend(validation.errors)
            else:
                all_values.append(validation.get())

        if all_errors:
            return Validation.errors_(*all_errors)
        return Validation.success(TraversableList(all_values))

    # === Utility ===

    def to_list(self) -> list[T]:
        return self._data.copy()

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
```

#### Usage Examples

```python
# Create
numbers = TraversableList([1, 2, 3, 4])

# traverse with Result
def safe_divide(x: int) -> Result[float, Exception]:
    if x == 0:
        return Error(ZeroDivisionError("Division by zero"))
    return Ok(10.0 / x)

result = numbers.traverse(safe_divide)
# Ok(TraversableList([10.0, 5.0, 3.333..., 2.5]))

# With error
numbers = TraversableList([1, 2, 0, 4])
result = numbers.traverse(safe_divide)
# Error(ZeroDivisionError("Division by zero"))

# traverse with Maybe
def get_user(id: int) -> Maybe[User]:
    return fetch_user(id)

ids = TraversableList([1, 2, 3])
users = ids.traverse_maybe(get_user)
# Some(TraversableList([User(1), User(2), User(3)]))

# sequence Results
results = [Ok(1), Ok(2), Ok(3)]
sequenced = TraversableList.sequence_results(results)
# Ok(TraversableList([1, 2, 3]))

results = [Ok(1), Error("fail"), Ok(3)]
sequenced = TraversableList.sequence_results(results)
# Error("fail")

# traverse with Validation (accumulate errors)
def validate_int(x: str) -> Validation:
    try:
        return Validation.success(int(x))
    except ValueError:
        return Validation.errors_(ValidationError(f"Invalid int: {x}"))

inputs = TraversableList(["1", "2", "abc", "4"])
result = inputs.traverse_validate(validate_int)
# Errors([ValidationError("Invalid int: abc")])
```

### TraversableDict

```python
@dataclass(frozen=True, slots=True)
class TraversableDict(Generic[K, V]):
    """Dict with traverse operations"""

    _data: dict[K, V]

    def traverse_values(
        self,
        func: Callable[[V], Result[U, E]]
    ) -> Result['TraversableDict[K, U]', E]:
        """Transform values with Result"""
        result_dict = {}

        for key, value in self._data.items():
            result = func(value)
            if result.is_error():
                return Error(result.error)
            result_dict[key] = result.unwrap()

        return Ok(TraversableDict(result_dict))

    def traverse_items(
        self,
        func: Callable[[tuple[K, V]], Result[U, E]]
    ) -> Result['TraversableDict[K, U]', E]:
        """Transform items with Result"""
        result_dict = {}

        for item in self._data.items():
            result = func(item)
            if result.is_error():
                return Error(result.error)
            result_dict[item[0]] = result.unwrap()

        return Ok(TraversableDict(result_dict))

    def sequence_values(
        self,
        results: dict[K, Result[V, E]]
    ) -> Result['TraversableDict[K, V]', E]:
        """Sequence dict of Results"""
        result_dict = {}

        for key, result in results.items():
            if result.is_error():
                return Error(result.error)
            result_dict[key] = result.unwrap()

        return Ok(TraversableDict(result_dict))

    def to_dict(self) -> dict[K, V]:
        return self._data.copy()
```

#### Usage Examples

```python
# Create
data = TraversableDict({
    "a": 1,
    "b": 2,
    "c": 3,
})

# traverse values
def double(x: int) -> Result[int, Exception]:
    return Ok(x * 2)

result = data.traverse_values(double)
# Ok(TraversableDict({"a": 2, "b": 4, "c": 6}))

# sequence values
results = {
    "a": Ok(1),
    "b": Ok(2),
    "c": Error("fail"),
}
sequenced = TraversableDict.sequence_values(results)
# Error("fail")
```

## Advanced Patterns

### Parallel traverse

```python
@dataclass(frozen=True, slots=True)
class TraversableList(Generic[T]):
    _data: list[T]

    async def traverse_parallel(
        self,
        func: Callable[[T], Awaitable[Result[U, E]]]
    ) -> Result['TraversableList[U]', E]:
        """Traverse in parallel (async)"""
        import asyncio

        results = await asyncio.gather(
            *[func(item) for item in self._data],
            return_exceptions=True
        )

        values = []
        for result in results:
            if isinstance(result, Exception):
                return Error(result)
            if result.is_error():
                return Error(result.error)
            values.append(result.unwrap())

        return Ok(TraversableList(values))
```

### Short-circuit vs Accumulate

```python
# traverse: Short-circuits on first error
def traverse_short_circuit(items, func):
    for item in items:
        result = func(item)
        if result.is_error():
            return Error(result.error)
    return Ok(values)

# traverse_validate: Accumulates all errors
def traverse_accumulate(items, func):
    all_errors = []
    all_values = []

    for item in items:
        result = func(item)
        if result.is_errors():
            all_errors.extend(result.errors)
        else:
            all_values.append(result.get())

    if all_errors:
        return Validation.errors_(*all_errors)
    return Validation.success(all_values)
```

### With index

```python
@dataclass(frozen=True, slots=True)
class TraversableList(Generic[T]):
    _data: list[T]

    def traverse_with_index(
        self,
        func: Callable[[int, T], Result[U, E]]
    ) -> Result['TraversableList[U]', E]:
        """Traverse with index available"""
        results = []

        for i, item in enumerate(self._data):
            result = func(i, item)
            if result.is_error():
                return Error(result.error)
            results.append(result.unwrap())

        return Ok(TraversableList(results))

# Usage
numbers = TraversableList([10, 20, 30])
result = numbers.traverse_with_index(
    lambda i, x: Ok(x + i)  # Add index
)
# Ok(TraversableList([10, 21, 32]))
```

### traverse followed by sequence

```python
# Law: traverse(func) === sequence(map(func, items))

def traverse(items, func):
    return sequence(map(func, items))

# These are equivalent
items = [1, 2, 3]
func = lambda x: Ok(x * 2)

result1 = traverse(items, func)
result2 = sequence(map(func, items))  # Same result
```

## Protocol Compliance

```python
@runtime_checkable
class Traversable(Protocol[T]):
    def traverse(self, func): ...
    def sequence(self, results): ...

class CustomTraversable:
    def __init__(self, items):
        self._items = items

    def traverse(self, func):
        results = []
        for item in self._items:
            result = func(item)
            if result.is_error():
                return Error(result.error)
            results.append(result.unwrap())
        return Ok(CustomTraversable(results))

    def sequence(self, results):
        values = []
        for result in results:
            if result.is_error():
                return Error(result.error)
            values.append(result.unwrap())
        return Ok(CustomTraversable(values))

# CustomTraversable is Traversable!
isinstance(CustomTraversable([]), Traversable)  # True
```

## Relationship with Other Concepts

### Traversable vs Mappable

```python
# Mappable: Transform values
class Mappable:
    def map(self, func):
        return Mappable([func(x) for x in self._data])

# Traversable: Transform with effects
class Traversable:
    def traverse(self, func):
        results = [func(x) for x in self._data]
        return sequence(results)  # Turn effects inside out
```

### Traversable vs Foldable

```python
# Foldable: Reduce to single value
class Foldable:
    def fold_left(self, initial, func):
        result = initial
        for item in self._data:
            result = func(result, item)
        return result

# Traversable: Reduce effects
class Traversable:
    def traverse(self, func):
        # Similar to fold_left, but accumulates effects
        ...
```

## Best Practices

### ✅ Do: Use traverse for validation

```python
# Good: Traverse with Validation (accumulates errors)
inputs = TraversableList(["1", "2", "invalid"])
result = inputs.traverse_validate(validate_int)
# All errors reported at once
```

### ✅ Do: Use sequence for converting collections

```python
# Good: Convert list[Result[T]] to Result[list[T]]
results = [Ok(1), Ok(2), Ok(3)]
sequenced = sequence(results)  # Ok([1, 2, 3])
```

### ❌ Don't: Use traverse when map suffices

```python
# Unnecessary: No effects in function
def double(x: int) -> int:
    return x * 2

result = items.traverse(lambda x: Ok(double(x)))  # Overkill

# Better
result = items.map(double)  # Simple
```

## Summary

**Traversable** protocol:
- ✅ Transform collections with effects (`traverse`)
- ✅ Invert collections of effects (`sequence`)
- ✅ Works with Result, Maybe, Validation
- ✅ Short-circuit (Result/Maybe) or accumulate (Validation) errors
- ✅ Async traversal available

**Key insight**: **Traversable turns effects "inside out"** - from `F[G[T]]` to `G[F[T]]`.

---

**Next**: See [Parseable](./06-parseable.md) for parseable entities.
