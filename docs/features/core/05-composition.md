# Composition: Patterns for Combining Operations

Composition is the heart of functional programming. Instead of nested function calls or complex control flow, we **compose** simple operations into pipelines.

## Why Composition?

### ❌ Nested Function Calls

```python
# Hard to read
result = save(transform(validate(fetch_user(user_id))))

# Execution order: fetch_user → validate → transform → save
# But written: save → transform → validate → fetch_user
# Inside-out reading!
```

### ❌ Intermediate Variables

```python
# Verbose
user = fetch_user(user_id)
validated = validate(user)
transformed = transform(validated)
result = save(transformed)
```

### ✅ Composition

```python
# Natural reading order
result = (
    fetch_user(user_id)
    | validate
    | transform
    | save
)

# Clear: fetch → validate → transform → save
```

## Composition Patterns

### 1. Method Chaining

```python
class MappableList(Generic[T]):
    def map(self, func: Callable[[T], U]) -> 'MappableList[U]':
        return MappableList([func(x) for x in self._data])

    def filter(self, predicate: Callable[[T], bool]) -> 'MappableList[T]':
        return MappableList([x for x in self._data if predicate(x)])

    def reduce(self, func: Callable[[T, T], T]) -> T:
        result = self._data[0]
        for item in self._data[1:]:
            result = func(result, item)
        return result

# Chain operations
result = (
    MappableList([1, 2, 3, 4, 5])
    .filter(lambda x: x % 2 == 0)  # [2, 4]
    .map(lambda x: x * 2)          # [4, 8]
    .reduce(lambda a, b: a + b)    # 12
)
```

**Benefits**:
- ✅ Natural reading order (left to right)
- ✅ No intermediate variables
- ✅ Type-safe (IDE tracks types)

### 2. Pipe Operator (`|`)

```python
class Maybe(Generic[T]):
    def __or__(self, func: Callable[[T], U]) -> 'Maybe[U]':
        """Pipe operator for composition"""
        if self.is_none():
            return None_
        return Some(func(self.value))

def fetch_user(id: int) -> Maybe[dict]:
    ...

def validate_user(user: dict) -> Maybe[dict]:
    ...

def get_profile(user: dict) -> Maybe[dict]:
    ...

# Compose with pipe operator
result = (
    Some(user_id)
    | fetch_user
    | validate_user
    | get_profile
)

# Equivalent to:
# result = get_profile(validate_user(fetch_user(user_id)))
```

**Benefits**:
- ✅ Visual pipeline
- ✅ Short-circuits on None
- ✅ Natural Python syntax

### 3. then / and_then Composition

```python
class Result(Generic[T, E]):
    def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Chain Result-returning functions"""
        if self.is_error():
            return Error(self.error)
        return func(self.value)

# Functions returning Result
def fetch_user(id: int) -> Result[User, Exception]: ...

def validate_user(user: User) -> Result[User, ValidationError]: ...

def save_user(user: User) -> Result[User, DatabaseError]: ...

# Compose with and_then
result = (
    fetch_user(user_id)
    .and_then(validate_user)
    .and_then(save_user)
)

# Short-circuits on first error
```

### 4. Compose Function

```python
def compose(*funcs: Callable) -> Callable:
    """Compose functions right to left"""
    def composed(value):
        result = value
        for func in reversed(funcs):
            result = func(result)
        return result
    return composed

# Usage
add_one = lambda x: x + 1
double = lambda x: x * 2
square = lambda x: x ** 2

pipeline = compose(square, double, add_one)
result = pipeline(3)  # ((3 + 1) * 2) ^ 2 = 64

# Alternative: pipe (left to right)
def pipe(*funcs: Callable) -> Callable:
    """Pipe functions left to right"""
    def composed(value):
        result = value
        for func in funcs:
            result = func(result)
        return result
    return composed

pipeline = pipe(add_one, double, square)
result = pipeline(3)  # (((3 + 1) * 2) ^ 2 = 64
```

### 5. Fluent Builder Pattern

```python
class QueryBuilder:
    """Fluent SQL-like query builder"""

    def __init__(self):
        self._select = []
        self._from = None
        self._where = []
        self._order_by = []
        self._limit = None

    def select(self, *columns: str) -> 'QueryBuilder':
        self._select.extend(columns)
        return self

    def from_(self, table: str) -> 'QueryBuilder':
        self._from = table
        return self

    def where(self, condition: str) -> 'QueryBuilder':
        self._where.append(condition)
        return self

    def order_by(self, *columns: str) -> 'QueryBuilder':
        self._order_by.extend(columns)
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        self._limit = n
        return self

    def build(self) -> str:
        # Build SQL query
        parts = []

        if self._select:
            parts.append(f"SELECT {', '.join(self._select)}")

        if self._from:
            parts.append(f"FROM {self._from}")

        if self._where:
            parts.append(f"WHERE {' AND '.join(self._where)}")

        if self._order_by:
            parts.append(f"ORDER BY {', '.join(self._order_by)}")

        if self._limit:
            parts.append(f"LIMIT {self._limit}")

        return " ".join(parts)

# Usage
query = (
    QueryBuilder()
    .select("name", "email", "created_at")
    .from_("users")
    .where("active = TRUE")
    .where("age >= 18")
    .order_by("created_at DESC")
    .limit(10)
    .build()
)

# SELECT name, email, created_at FROM users WHERE active = TRUE AND age >= 18 ORDER BY created_at DESC LIMIT 10
```

## Advanced Composition

### 1. Kleisli Composition (Monad Composition)

```python
def kleisli(f: Callable[[T], 'Result[U, E]'], g: Callable[[U], 'Result[V, E]']) -> Callable[[T], 'Result[V, E]']:
    """Compose Result-returning functions"""
    def composed(x: T) -> Result[V, E]:
        result1 = f(x)
        if result1.is_error():
            return Error(result1.error)
        return g(result1.unwrap())
    return composed

# Functions returning Result
def fetch_user(id: int) -> Result[User, Exception]: ...

def get_profile(user: User) -> Result[Profile, Exception]: ...

def save_profile(profile: Profile) -> Result[Profile, Exception]: ...

# Compose with Kleisli
pipeline = kleisli(fetch_user, get_profile)
pipeline = kleisli(pipeline, save_profile)

result = pipeline(user_id)
```

### 2. Parallel Composition

```python
class Parallel(Generic[T]):
    """Run operations in parallel"""

    @staticmethod
    def map(func: Callable[[T], U], items: list[T]) -> list[U]:
        """Map function over items in parallel"""
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(func, items))
        return results

    @staticmethod
    def gather(*funcs: Callable[[], T]) -> list[T]:
        """Run multiple functions in parallel"""
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(func) for func in funcs]
            results = [f.result() for f in futures]
        return results

# Usage
results = Parallel.map(lambda x: x ** 2, [1, 2, 3, 4, 5])

user, posts, metadata = Parallel.gather(
    lambda: fetch_user(1),
    lambda: fetch_posts(1),
    lambda: fetch_metadata(1)
)
```

### 3. Conditional Composition

```python
class Maybe(Generic[T]):
    def map_if(self, predicate: Callable[[T], bool], func: Callable[[T], U]) -> 'Maybe[U]':
        """Map only if predicate is true"""
        if self.is_none():
            return None_
        if predicate(self.value):
            return Some(func(self.value))
        return None_

    def map_else(self, func: Callable[[T], U], default: U) -> U:
        """Map or return default"""
        if self.is_none():
            return default
        return func(self.value)

# Usage
result = (
    fetch_user(user_id)
    .map_if(lambda u: u.age >= 18, lambda u: u.profile)
    .map_else(lambda p: p.adult_content, default_content)
)
```

### 4. Async Composition

```python
class AsyncPipeline:
    """Async composition helpers"""

    @staticmethod
    def pipe(*funcs: Callable[[Awaitable], Awaitable]) -> Callable:
        """Pipe async functions"""
        async def composed(value):
            result = value
            for func in funcs:
                result = await func(result)
            return result
        return composed

    @staticmethod
    async def sequence(*async_funcs: Callable[[], Awaitable[T]]) -> list[T]:
        """Run async functions in sequence"""
        results = []
        for func in async_funcs:
            result = await func()
            results.append(result)
        return results

    @staticmethod
    async def parallel(*async_funcs: Callable[[], Awaitable[T]]) -> list[T]:
        """Run async functions in parallel"""
        import asyncio
        return await asyncio.gather(*(func() for func in async_funcs))

# Usage
async def main():
    result = await AsyncPipeline.pipe(
        fetch_user,
        validate_user,
        save_user
    )(user_id)

    user, posts, comments = await AsyncPipeline.parallel(
        lambda: fetch_user(1),
        lambda: fetch_posts(1),
        lambda: fetch_comments(1)
    )
```

## Composition with Protocols

### Composable Protocol

```python
@runtime_checkable
class Composable(Protocol[T]):
    """Object that can be composed"""

    def then(self, func: Callable[[T], U]) -> 'Composable[U]': ...

    def __or__(self, func: Callable[[T], U]) -> 'Composable[U]': ...

class Maybe(Generic[T]):
    def then(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
        if self.is_none():
            return None_
        return func(self.value)

    def __or__(self, func: Callable[[T], U]) -> 'Maybe[U]':
        if self.is_none():
            return None_
        return Some(func(self.value))

# Maybe implements Composable
def process(maybe: Composable[int]) -> Composable[str]:
    return maybe | str

result = process(Some(42))  # Some("42")
```

## Real-World Examples

### Example 1: Data Processing Pipeline

```python
class DataFrame(Generic[T]):
    """Functional dataframe"""

    def __init__(self, data: list[T]):
        self._data = data

    def filter(self, predicate: Callable[[T], bool]) -> 'DataFrame[T]':
        return DataFrame([x for x in self._data if predicate(x)])

    def map(self, func: Callable[[T], U]) -> 'DataFrame[U]':
        return DataFrame([func(x) for x in self._data])

    def group_by(self, key: Callable[[T], Any]) -> dict[Any, list[T]]:
        groups = {}
        for item in self._data:
            k = key(item)
            if k not in groups:
                groups[k] = []
            groups[k].append(item)
        return groups

    def aggregate(self, func: Callable[[list[T]], U]) -> U:
        return func(self._data)

    def count(self) -> int:
        return len(self._data)

# Usage
data = DataFrame([
    {"name": "Alice", "age": 30, "department": "Engineering"},
    {"name": "Bob", "age": 25, "department": "Sales"},
    {"name": "Charlie", "age": 35, "department": "Engineering"},
])

result = (
    data
    .filter(lambda row: row["age"] >= 30)
    .map(lambda row: {**row, "is_senior": True})
    .group_by(lambda row: row["department"])
)

# {"Engineering": [{"name": "Alice", "age": 30, "department": "Engineering", "is_senior": True}, ...]}
```

### Example 2: HTTP Request Pipeline

```python
class RequestBuilder:
    """Fluent HTTP request builder"""

    def __init__(self):
        self._url = None
        self._method = "GET"
        self._headers = {}
        self._params = {}
        self._body = None
        self._timeout = 30
        self._retry = 0

    def url(self, url: str) -> 'RequestBuilder':
        self._url = url
        return self

    def method(self, method: str) -> 'RequestBuilder':
        self._method = method
        return self

    def header(self, key: str, value: str) -> 'RequestBuilder':
        self._headers[key] = value
        return self

    def param(self, key: str, value: Any) -> 'RequestBuilder':
        self._params[key] = value
        return self

    def body(self, body: dict) -> 'RequestBuilder':
        self._body = json.dumps(body)
        return self

    def timeout(self, seconds: int) -> 'RequestBuilder':
        self._timeout = seconds
        return self

    def retry(self, n: int) -> 'RequestBuilder':
        self._retry = n
        return self

    def send(self) -> Result[Response, Exception]:
        """Send request with retry"""
        import requests

        for attempt in range(self._retry + 1):
            try:
                response = requests.request(
                    method=self._method,
                    url=self._url,
                    headers=self._headers,
                    params=self._params,
                    data=self._body,
                    timeout=self._timeout
                )
                return Ok(response)
            except Exception as e:
                if attempt == self._retry:
                    return Error(e)
        return Error(RuntimeError("Max retries exceeded"))

# Usage
result = (
    RequestBuilder()
    .url("https://api.example.com/users")
    .method("POST")
    .header("Authorization", f"Bearer {token}")
    .header("Content-Type", "application/json")
    .body({"name": "Alice", "email": "alice@example.com"})
    .timeout(10)
    .retry(3)
    .send()
)

if result.is_ok():
    response = result.unwrap()
    print(response.json())
```

### Example 3: Validation Pipeline

```python
class ValidationPipeline:
    """Compose multiple validators"""

    def __init__(self):
        self._validators: list[Validator] = []

    def add(self, validator: Validator[T]) -> 'ValidationPipeline':
        self._validators.append(validator)
        return self

    def validate(self, value: T) -> Validation:
        """Run all validators, accumulate errors"""
        all_errors = []

        for validator in self._validators:
            result = validator.validate(value)
            if result.is_errors():
                all_errors.extend(result.errors)

        if all_errors:
            return Validation.errors_(*all_errors)
        return Validation.success(value)

# Usage
user_validator = (
    ValidationPipeline()
    .add(StringValidator().min_length(2).required())
    .add(IntValidator().range(18, 120))
    .add(EmailValidator().email())
)

result = user_validator.validate(user_input)
```

## Best Practices

### ✅ Do: Compose small operations

```python
# Small, single-purpose operations
result = (
    data
    .filter(is_active)
    .map(to_uppercase)
    .reduce(combine)
)
```

### ✅ Do: Use descriptive names

```python
def is_adult(user: User) -> bool:
    return user.age >= 18

def get_profile(user: User) -> Profile:
    return user.profile

result = fetch_user(id) | is_adult | get_profile
```

### ✅ Do: Handle errors in composition

```python
result = (
    fetch_user(id)
    .and_then(validate)
    .and_then(save)
    .map_error(lambda e: handle_error(e))
)
```

### ❌ Don't: Over-compose

```python
# Too many steps, hard to debug
result = a | b | c | d | e | f | g | h | i | j

# Better: Break into named functions
step1 = a | b | c
step2 = d | e | f
result = step1 | step2 | g | h
```

### ❌ Don't: Mix paradigms

```python
# Confusing: mixing methods and pipes
result = data.map(f).filter(g) | h

# Better: Be consistent
result = data.map(f) | g | h  # All pipes
# or
result = data.map(f).filter(g).apply(h)  # All methods
```

## Summary

**Composition patterns**:
- ✅ Method chaining - Natural for objects
- ✅ Pipe operator (`|`) - Visual pipeline
- ✅ `then`/`and_then` - Monad composition
- ✅ `compose`/`pipe` - Function composition
- ✅ Fluent builders - Declarative construction

**Key principles**:
- Small, composable operations
- Left-to-right reading
- Type-safe transformations
- Short-circuit on errors

**For functional entities**: Every method returns a new instance, enabling natural composition.

---

**Next**: See [Side Effects](./06-side-effects.md) for managing side effects.
