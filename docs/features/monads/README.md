# Monads - Functional Error Handling

Practical monadic types for error handling, optional values, and side effects.

## 📚 Monad Types

### [Maybe](./01-maybe.md)
Handle optional values without `None` checks.

### [Result](./02-result.md)
Explicit error handling without exceptions (errors are Exception objects).

### [AsyncResult](./03-async-result.md)
Async error handling for coroutines.

### [Try](./04-try.md)
Exception handling as a value.

### [Either](./05-either.md)
Two disjoint types for validation.

### [Validation](./06-validation.md)
Accumulate multiple errors.

### [Reader](./07-reader.md)
Dependency injection monad.

### [Writer](./08-writer.md)
Logging monad.

### [State](./09-state.md)
State management monad.

### [IO](./10-io.md)
Explicit side effects.

### [Unit](./11-unit.md)
Void return type for functions.

### [Task](./12-task.md)
Lazy coroutine wrapper.

### [AsyncMaybe](./13-async-maybe.md)
Async optional values.

---

## 📊 Quick Comparison

| Monad | Use Case | Example |
|-------|----------|---------|
| `Maybe` | Optional values | Database fetch that might not exist |
| `Result` | Known errors | API call with error cases |
| `AsyncResult` | Async errors | Async API calls |
| `Try` | Exceptions | File I/O, network calls |
| `Either` | Two possibilities | Left (error) or Right (success) |
| `Validation` | Multiple errors | Form validation |
| `Reader` | Dependencies | Database connection, logger |
| `Writer` | Logging | Audit trail |
| `State` | Mutable state | Counters, accumulators |
| `IO` | Side effects | File operations, console output |
| `Unit` | Void functions | Functions with no return value |
| `Task` | Lazy coroutines | Deferred async computation |
| `AsyncMaybe` | Async optionals | Async cache lookups |

## 🎯 DX Principles

### No Jargon
- Practical names, not theory
- `maybe` instead of `option`
- `result` instead of `either`
- `try_` instead of `exception`

### Pythonic Integration
- Works with `match/case`
- Supports unpacking
- Compatible with type hints

### Fluent API
```python
value | operation1 | operation2 | operation3
```

---

## 🔗 Common Operations

All monads support:

```python
# Transform value
monad.map(func)

# Chain monadic operations
monad.then(func)  # or monad | func

# Provide default
monad.unwrap_or(default)

# Pattern matching
match monad:
    case Some(value): ...
    case None: ...
```
