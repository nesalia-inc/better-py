# Issue 013: Sum Type Classes vs Factory Methods Design

## Description

The current implementation of sum types (Maybe, Result, Either, Validation) uses factory methods on a single class, rather than separate concrete classes for each variant. This design is less intuitive and doesn't align with functional programming conventions.

**Current Design:**
```python
# Maybe
value = Maybe.some(42)
empty = Maybe.nothing()

# Result
success = Result.ok(42)
failure = Result.error("something went wrong")

# Either
right = Either.right(42)
left = Either.left("error")

# Validation
valid = Validation.valid(42)
invalid = Validation.invalid(["error1", "error2"])
```

**Proposed Design:**
```python
# Maybe
value = Some(42)
empty = Nothing()

# Result
success = Ok(42)
failure = Error("something went wrong")

# Either
right = Right(42)
left = Left("error")

# Validation
valid = Valid(42)
invalid = Invalid(["error1", "error2"])
```

## Impact

### 1. **Intuitiveness**
Separate classes are more intuitive for developers coming from:
- Functional languages (Haskell, Scala, OCaml)
- Rust with `Option<T>` and `Result<T, E>`
- TypeScript with pattern matching libraries
- Other FP libraries

The current design feels more "Java-esque" with static factory methods, which doesn't fit the functional paradigm.

### 2. **Type Clarity**
With separate classes:
```python
def process(value: Some[int]) -> str:  # Explicitly requires Some
    ...

# vs current
def process(value: Maybe[int]) -> str:  # Could be Some or Nothing
    if value.is_nothing():
        ...
```

### 3. **Pattern Matching**
Python 3.10+ pattern matching works better with separate classes:

```python
match value:
    case Some(x):
        print(f"Got {x}")
    case Nothing():
        print("No value")
```

### 4. **IDE Support**
Better IDE autocomplete and type inference:
- `Some(42)` clearly shows it's a `Some` instance
- Separate classes allow better documentation and hints

### 5. **Import Clarity**
```python
from better_py import Some, Nothing, Ok, Error, Left, Right, Valid, Invalid

# vs
from better_py import Maybe, Result, Either, Validation
```

## Migration Path

This is a **breaking change** that requires:

1. **Create Variant Classes**
   - `Some[T]` and `Nothing` extending `Maybe[T]`
   - `Ok[T]` and `Error[E]` extending `Result[T, E]`
   - `Left[L]` and `Right[R]` extending `Either[L, R]`
   - `Valid[T]` and `Invalid[E]` extending `Validation[T, E]`

2. **Maintain Backward Compatibility**
   - Keep factory methods as aliases initially
   - Deprecation warnings for old API
   - Migration guide in documentation

3. **Type System**
   - Update all type hints
   - Ensure protocols still work
   - Update tests

4. **Documentation Updates**
   - All examples using new API
   - Migration guide
   - Update both user docs and API reference

## Examples

### Current vs Proposed API

**Maybe:**
```python
# Current
Maybe.from_value(get_user())
Maybe.some(42)
Maybe.nothing()

# Proposed
Some(42)
Nothing()
Maybe.from_value(get_user())  # helper method still useful
```

**Result:**
```python
# Current
Result.ok(value)
Result.error(err)

# Proposed
Ok(value)
Error(err)
```

**Pattern Matching:**
```python
# Proposed - much cleaner
match result:
    case Ok(value):
        return process(value)
    case Error(err):
        return handle_error(err)
```

## Trade-offs

### Pros
- More idiomatic for FP
- Better pattern matching
- Clearer type semantics
- Better IDE support
- More intuitive API

### Cons
- Breaking change
- More top-level classes to import
- Slightly more complex class hierarchy
- Need for migration path

## Related Issues

- Issue #008: Maybe cannot contain None - Related to Maybe design
- Issue #007: Missing applicative operations - API design consistency

## References

- Rust's `Option<T>`: `Some(T)` and `None`
- Rust's `Result<T, E>`: `Ok(T)` and `Err(E)`
- Haskell's `Maybe`: `Just a` and `Nothing`
- Haskell's `Either`: `Left a` and `Right b`
- Scala's `Option`: `Some(a)` and `None`
- TypeScript's `fp-ts` library
- Python 3.10+ Structural Pattern Matching (PEP 634)

## Priority

**High** - This is a fundamental API design decision that affects the entire library's usability and adoption. Should be addressed before 1.0 release.
