# Combinable: Objects That Can Be Combined

**Combinable** is a protocol for objects that can be **combined** or **merged** together. This is the functional equivalent of algebraic structures like Semigroups and Monoids.

## Overview

```python
@runtime_checkable
class Combinable(Protocol[T]):
    """Any object that can be combined"""

    def combine(self, other: T) -> T:
        """Combine with another object"""
        ...

    @classmethod
    def empty(cls) -> T:
        """Empty element (identity for combine)"""
        ...
```

## Core Concepts

### Semigroup: Has `combine`

```python
# Can combine two values
result = value1.combine(value2)
```

### Monoid: Has `combine` and `empty`

```python
# Has identity element
result = Combinable.empty().combine(value)  # = value
result = value.combine(Combinable.empty())  # = value
```

## Implementations

### CombinableList (Concatenation)

```python
@dataclass(frozen=True, slots=True)
class CombinableList(Generic[T]):
    """List that combines by concatenation"""

    _data: list[T]

    def combine(self, other: 'CombinableList[T]') -> 'CombinableList[T]':
        """Concatenate lists"""
        return CombinableList(self._data + other._data)

    @classmethod
    def empty(cls) -> 'CombinableList[T]':
        """Empty list"""
        return CombinableList([])

    def __add__(self, other: 'CombinableList[T]') -> 'CombinableList[T]':
        """Operator: +"""
        return self.combine(other)

    # === Additional operations ===

    def repeat(self, n: int) -> 'CombinableList[T]':
        """Repeat list n times"""
        return CombinableList(self._data * n)

    def interleave(self, other: 'CombinableList[T]') -> 'CombinableList[T]':
        """Interleave two lists"""
        result = []
        min_len = min(len(self._data), len(other._data))
        for i in range(min_len):
            result.append(self._data[i])
            result.append(other._data[i])
        result.extend(self._data[min_len:])
        result.extend(other._data[min_len:])
        return CombinableList(result)

    def zip(self, other: 'CombinableList[U]') -> 'CombinableList[tuple[T, U]]':
        """Zip two lists"""
        return CombinableList(list(zip(self._data, other._data)))

    def to_list(self) -> list[T]:
        return self._data.copy()
```

#### Usage Examples

```python
# Create
list1 = CombinableList([1, 2, 3])
list2 = CombinableList([4, 5, 6])

# Combine
combined = list1.combine(list2)  # [1, 2, 3, 4, 5, 6]

# Using operator
combined = list1 + list2  # [1, 2, 3, 4, 5, 6]

# Empty identity
empty = CombinableList.empty()
result = empty.combine(list1)  # [1, 2, 3]
result = list1.combine(empty)  # [1, 2, 3]

# Repeat
repeated = list1.repeat(3)  # [1, 2, 3, 1, 2, 3, 1, 2, 3]

# Interleave
interleaved = list1.interleave(list2)  # [1, 4, 2, 5, 3, 6]

# Zip
zipped = list1.zip(CombinableList(['a', 'b', 'c']))  # [(1, 'a'), (2, 'b'), (3, 'c')]
```

### CombinableDict (Merge)

```python
@dataclass(frozen=True, slots=True)
class CombinableDict(Generic[K, V]):
    """Dict that combines by merging"""

    _data: dict[K, V]

    def combine(self, other: 'CombinableDict[K, V]') -> 'CombinableDict[K, V]':
        """Merge dicts (other takes precedence)"""
        return CombinableDict({**self._data, **other._data})

    @classmethod
    def empty(cls) -> 'CombinableDict[K, V]':
        """Empty dict"""
        return CombinableDict({})

    def __add__(self, other: 'CombinableDict[K, V]') -> 'CombinableDict[K, V]':
        """Operator: +"""
        return self.combine(other)

    # === Merge strategies ===

    def combine_with(
        self,
        other: 'CombinableDict[K, V]',
        resolve: Callable[[V, V], V]
    ) -> 'CombinableDict[K, V]':
        """Merge with conflict resolution"""
        result = dict(self._data)
        for key, value in other._data.items():
            if key in result:
                result[key] = resolve(result[key], value)
            else:
                result[key] = value
        return CombinableDict(result)

    def deep_combine(self, other: 'CombinableDict[K, V]') -> 'CombinableDict[K, V]':
        """Deep merge for nested dicts"""
        result = dict(self._data)
        for key, value in other._data.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = CombinableDict(result[key]).deep_combine(CombinableDict(value))._data
            else:
                result[key] = value
        return CombinableDict(result)

    def to_dict(self) -> dict[K, V]:
        return self._data.copy()
```

#### Usage Examples

```python
# Create
dict1 = CombinableDict({"a": 1, "b": 2})
dict2 = CombinableDict({"b": 3, "c": 4})

# Combine (other wins)
merged = dict1.combine(dict2)  # {"a": 1, "b": 3, "c": 4}

# Using operator
merged = dict1 + dict2  # {"a": 1, "b": 3, "c": 4}

# Empty identity
empty = CombinableDict.empty()
result = empty.combine(dict1)  # {"a": 1, "b": 2}

# With conflict resolution
merged = dict1.combine_with(
    dict2,
    resolve=lambda old, new: old + new  # Sum conflicts
)
# {"a": 1, "b": 5, "c": 4}

# Deep merge
dict1 = CombinableDict({"config": {"host": "localhost"}})
dict2 = CombinableDict({"config": {"port": 5432}})
merged = dict1.deep_combine(dict2)
# {"config": {"host": "localhost", "port": 5432}}
```

### CombinableInt (Addition)

```python
@dataclass(frozen=True, slots=True)
class CombinableInt:
    """Int that combines by addition"""

    value: int

    def combine(self, other: 'CombinableInt') -> 'CombinableInt':
        """Add values"""
        return CombinableInt(self.value + other.value)

    @classmethod
    def empty(cls) -> 'CombinableInt':
        """Zero"""
        return CombinableInt(0)

    def __add__(self, other: 'CombinableInt') -> 'CombinableInt':
        """Operator: +"""
        return self.combine(other)

    # === Additional operations ===

    def multiply(self, n: int) -> 'CombinableInt':
        """Multiply by scalar"""
        return CombinableInt(self.value * n)

    def to_int(self) -> int:
        return self.value
```

#### Usage Examples

```python
# Create
int1 = CombinableInt(5)
int2 = CombinableInt(3)

# Combine (add)
sum_ = int1.combine(int2)  # CombinableInt(8)

# Using operator
sum_ = int1 + int2  # CombinableInt(8)

# Empty identity
zero = CombinableInt.empty()
result = zero.combine(int1)  # CombinableInt(5)

# Multiply
multiplied = int1.multiply(3)  # CombinableInt(15)
```

### CombinableString (Concatenation)

```python
@dataclass(frozen=True, slots=True)
class CombinableString:
    """String that combines by concatenation"""

    value: str

    def combine(self, other: 'CombinableString') -> 'CombinableString':
        """Concatenate strings"""
        return CombinableString(self.value + other.value)

    @classmethod
    def empty(cls) -> 'CombinableString':
        """Empty string"""
        return CombinableString("")

    def __add__(self, other: 'CombinableString') -> 'CombinableString':
        """Operator: +"""
        return self.combine(other)

    # === Additional operations ===

    def repeat(self, n: int) -> 'CombinableString':
        """Repeat string"""
        return CombinableString(self.value * n)

    def separate(self, separator: 'CombinableString') -> 'CombinableString':
        """Add separator between"""
        return separator.combine(self)

    def to_str(self) -> str:
        return self.value
```

#### Usage Examples

```python
# Create
str1 = CombinableString("Hello")
str2 = CombinableString("World")

# Combine (concat)
combined = str1.combine(str2)  # "HelloWorld"

# Using operator
combined = str1 + str2  # "HelloWorld"

# With separator
space = CombinableString(" ")
result = str1.separate(space).combine(str2)  # "Hello World"

# Repeat
repeated = str1.repeat(3)  # "HelloHelloHello"
```

### CombinableSet (Union)

```python
@dataclass(frozen=True, slots=True)
class CombinableSet(Generic[T]):
    """Set that combines by union"""

    _data: set[T]

    def combine(self, other: 'CombinableSet[T]') -> 'CombinableSet[T]':
        """Union of sets"""
        return CombinableSet(self._data | other._data)

    @classmethod
    def empty(cls) -> 'CombinableSet[T]':
        """Empty set"""
        return CombinableSet(set())

    def __add__(self, other: 'CombinableSet[T]') -> 'CombinableSet[T]':
        """Operator: +"""
        return self.combine(other)

    # === Set operations ===

    def intersect(self, other: 'CombinableSet[T]') -> 'CombinableSet[T]':
        """Intersection"""
        return CombinableSet(self._data & other._data)

    def difference(self, other: 'CombinableSet[T]') -> 'CombinableSet[T]':
        """Difference"""
        return CombinableSet(self._data - other._data)

    def to_set(self) -> set[T]:
        return self._data.copy()
```

#### Usage Examples

```python
# Create
set1 = CombinableSet({1, 2, 3})
set2 = CombinableSet({3, 4, 5})

# Combine (union)
combined = set1.combine(set2)  # {1, 2, 3, 4, 5}

# Intersect
intersection = set1.intersect(set2)  # {3}

# Difference
diff = set1.difference(set2)  # {1, 2}
```

## Advanced Patterns

### Combining Multiple Values

```python
# Combine list of combinable values
def combine_all(items: list[Combinable]) -> Combinable:
    """Combine all items using fold"""
    if not items:
        return Combinable.empty()

    result = items[0]
    for item in items[1:]:
        result = result.combine(item)
    return result

# Usage
lists = [
    CombinableList([1, 2]),
    CombinableList([3, 4]),
    CombinableList([5, 6]),
]
combined = combine_all(lists)  # [1, 2, 3, 4, 5, 6]
```

### Combining Results

```python
# Combine Results (keep first success or last error)
def combine_results(results: list[Result[T, E]]) -> Result[list[T], E]:
    """Combine list of Results into Result of lists"""

    values = []
    for result in results:
        if result.is_error():
            return Error(result.error)
        values.append(result.unwrap())

    return Ok(values)

# Usage
results = [
    Ok(1),
    Ok(2),
    Ok(3),
]
combined = combine_results(results)  # Ok([1, 2, 3])
```

### Combining Maybes

```python
# Combine Maybes (require all Some)
def combine_maybes(maybes: list[Maybe[T]]) -> Maybe[list[T]]:
    """Combine list of Maybes"""

    values = []
    for maybe in maybes:
        if maybe.is_none():
            return None_
        values.append(maybe.unwrap())

    return Some(values)

# Usage
maybes = [
    Some(1),
    Some(2),
    Some(3),
]
combined = combine_maybes(maybes)  # Some([1, 2, 3])

# With None
maybes = [Some(1), None_, Some(3)]
combined = combine_maybes(maybes)  # None_
```

### Combining Validations

```python
# Combine Validations (accumulate errors)
def combine_validations(validations: list[Validation]) -> Validation:
    """Combine list of Validations"""

    all_values = []
    all_errors = []

    for validation in validations:
        if validation.is_success():
            all_values.append(validation.value)
        else:
            all_errors.extend(validation.errors)

    if all_errors:
        return Validation.errors_(*all_errors)
    return Validation.success(all_values)

# Usage
validations = [
    Validation.success(1),
    Validation.success(2),
    Validation.success(3),
]
combined = combine_validations(validations)  # Success([1, 2, 3])

# With errors
validations = [
    Validation.success(1),
    Validation.errors_(ValidationError("Error 1")),
    Validation.errors_(ValidationError("Error 2")),
]
combined = combine_validations(validations)  # Errors([Error1, Error2])
```

## Protocol Compliance

```python
@runtime_checkable
class Combinable(Protocol[T]):
    def combine(self, other: T) -> T: ...
    @classmethod
    def empty(cls) -> T: ...

class CustomCombinable:
    def __init__(self, value):
        self.value = value

    def combine(self, other):
        return CustomCombinable(self.value + other.value)

    @classmethod
    def empty(cls):
        return CustomCombinable(0)

# CustomCombinable is Combinable!
isinstance(CustomCombinable(5), Combinable)  # True
```

## Best Practices

### ✅ Do: Provide empty for identity

```python
# Good: Has identity
result = Combinable.empty().combine(value)  # = value
```

### ✅ Do: Make combine associative

```python
# Good: (a.combine(b)).combine(c) == a.combine(b.combine(c))
```

### ❌ Don't: Mutate in combine

```python
# Bad: Mutates self
def combine(self, other):
    self._data.extend(other._data)
    return self

# Good: Returns new instance
def combine(self, other):
    return CombinableList(self._data + other._data)
```

## Summary

**Combinable** protocol:
- ✅ Combine objects with `combine()`
- ✅ Identity element with `empty()`
- ✅ Support for `+` operator
- ✅ Multiple implementations (list, dict, int, string, set)

**Implementations**:
- `CombinableList[T]` - Concatenation
- `CombinableDict[K, V]` - Merge
- `CombinableInt` - Addition
- `CombinableString` - Concatenation
- `CombinableSet[T]` - Union

**Key principle**: `combine()` should be **associative** and `empty()` should be the **identity element**.

---

**Next**: See [Updatable](./04-updatable.md) for immutable updates.
