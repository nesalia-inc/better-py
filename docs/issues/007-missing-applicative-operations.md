# Issue 007: Missing Applicative Operations (ap, lift2, zip)

## Description

The library only provides the `ap` (apply) method on the `Validation` monad. Other monads (`Maybe`, `Result`, `Either`) lack applicative operations, making the library inconsistent and preventing generic applicative patterns.

## What's Missing

### 1. `ap` Method (Apply)

Only `Validation` has `ap`. Missing from:
- `Maybe<T>`
- `Result<T, E>`
- `Either<L, R>`

### 2. `lift2` / `map2` Operations

Missing binary operations that combine two monadic values:
```python
# These don't exist:
Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.some(2))
# Should return: Maybe.some(3)

Result.map2(lambda x, y: x + y, Result.ok(1), Result.ok(2))
# Should return: Result.ok(3)
```

### 3. `zip` Operations

Missing zipping operations that combine multiple monadic values:
```python
# These don't exist:
Maybe.zip(Maybe.some(1), Maybe.some(2), Maybe.some(3))
# Should return: Maybe.some((1, 2, 3))
```

## Why This Matters

Applicative functors are essential for:
1. **Validating multiple independent values**
2. **Parallel computations**
3. **Combining configuration values**
4. **Functional form validation**

## Examples of Missing Functionality

### Example 1: Form Validation with Maybe

```python
# Current: Cannot do this cleanly
first_name = Maybe.of(get_first_name())
last_name = Maybe.of(get_last_name())
age = Maybe.of(get_age())

# Want: combine all three, fail if any is Nothing
# Missing: Maybe.lift3(lambda f, l, a: Person(f, l, a), first_name, last_name, age)
```

### Example 2: Parallel Requests with Result

```python
# Current: Must use nested bind
result1 = fetch_user(user_id)
result2 = fetch_preferences(user_id)

result = result1.bind(lambda user:
    result2.bind(lambda prefs:
        Result.ok(Display(user, prefs))
    )
)

# Could be: Result.zip(fetch_user(user_id), fetch_preferences(user_id))
#           .map(lambda pair: Display(pair[0], pair[1]))
```

### Example 3: Configuration Loading

```python
# Want to load config from multiple sources, fail if any fail
host = Result.ok(load_host())
port = Result.ok(load_port())
database = Result.ok(load_database())

# Missing: Result.lift3(lambda h, p, d: Config(h, p, d), host, port, database)
```

## Proposed API

### Add `ap` to all monads:

```python
# Maybe
def ap(self, other: Maybe[Callable[[T], U]]) -> Maybe[U]:
    """Apply a maybe function to this maybe value."""
    ...

# Result
def ap(self, other: Result[Callable[[T], U], E]) -> Result[U, E]:
    """Apply a result function to this result value."""
    ...

# Either
def ap(self, other: Either[L, Callable[[R], U]]) -> Either[L, U]:
    """Apply an either function to this either value."""
    ...
```

### Add `lift2` class methods:

```python
@staticmethod
def lift2(f: Callable[[A, B], C], ma: Maybe[A], mb: Maybe[B]) -> Maybe[C]:
    """Lift a binary function to operate on Maybe values."""
    return mb.ap(ma.map(lambda x: lambda y: f(x, y)))

@staticmethod
def lift3(f: Callable[[A, B, C], D],
          ma: Maybe[A], mb: Maybe[B], mc: Maybe[C]) -> Maybe[D]:
    """Lift a ternary function to operate on Maybe values."""
    ...

# Similar for Result and Either
```

### Add `zip` class methods:

```python
@staticmethod
def zip(*monads: Maybe[T]) -> Maybe[tuple[T, ...]]:
    """Combine multiple Maybe values into a tuple."""
    ...

# Similar for Result and Either
```

## Implementation Example

```python
# For Maybe
def ap(self, other: Maybe[Callable[[T], U]]) -> Maybe[U]:
    """Apply a maybe function to this maybe value.

    Example:
        >>> add = Maybe.some(lambda x: x + 1)
        >>> value = Maybe.some(5)
        >>> add.ap(value)  # Maybe.some(6)
    """
    if self.is_nothing() or other.is_nothing():
        return Maybe.nothing()
    assert self._value is not None
    assert other._value is not None
    return Maybe.some(other._value(self._value))

@staticmethod
def lift2(f: Callable[[A, B], C], ma: Maybe[A], mb: Maybe[B]) -> Maybe[C]:
    """Lift a binary function to operate on Maybe values.

    Example:
        >>> Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.some(2))
        Maybe.some(3)
    """
    return mb.ap(ma.map(lambda x: lambda y: f(x, y)))
```

## Related Issues

- Issue #001: Validation.ap() has bugs
- Issue #008: Inconsistent API design

## References

- Applicative Programming with Effects
- Haskell's Applicative typeclass
- Cats Scala's Applicative
- ZIO's Zipped applicative
