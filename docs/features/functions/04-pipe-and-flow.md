# Pipe & Flow: Data Pipeline Patterns

Flow data through function pipelines with left-to-right readable transformations.

## Overview

```python
from mfn.functions import pipe, flow

# Pipe value through functions
result = pipe(
    data,
    validate,
    transform,
    save
)

# Flow with operators
result = flow(
    data,
    map(str),
    filter(lambda x: len(x) > 0),
    list
)
```

## pipe() - Basic Pipeline

### Sequential Processing

```python
from mfn.functions import pipe

def validate(data):
    if not data:
        raise ValueError("Empty data")
    return data

def transform(data):
    return [x * 2 for x in data]

def save(data):
    database.insert(data)
    return data

# Pipe through pipeline
result = pipe(
    [1, 2, 3, 4, 5],
    validate,
    transform,
    save
)
```

### Error Handling

```python
from mfn.functions import pipe

# Pipe with Result
result = pipe(
    user_id,
    fetch_user,      # Result[User, Error]
    validate_user,   # Result[User, Error]
    save_user,       # Result[User, Error]
)

# Short-circuits on first Error
```

### Async Pipe

```python
from mfn.functions import async_pipe

async def process(id):
    return await async_pipe(
        id,
        fetch_user,
        validate,
        save
    )
```

## flow() - Method Chaining

### Basic flow()

```python
from mfn.functions import flow

# Flow with methods
result = flow(
    [1, -2, 3, -4, 5],
    filter(lambda x: x > 0),    # [1, 3, 5]
    map(lambda x: x * 2),       # [2, 6, 10]
    lambda nums: sum(nums)      # 18
)
```

### Object Methods

```python
from mfn.functions import flow

# Flow with object methods
result = flow(
    "  hello world  ",
    str.strip,           # "hello world"
    str.upper,           # "HELLO WORLD"
    lambda s: s.split()  # ["HELLO", "WORLD"]
)
```

### With Collections

```python
from mfn.functions import flow
from mfn.collections import MappableList

result = flow(
    [1, 2, 3, 4, 5],
    MappableList,
    lambda l: l.filter(lambda x: x % 2 == 0),
    lambda l: l.map(lambda x: x * 2),
    lambda l: l.to_list()
)
# [4, 8]
```

## Pipeline Builders

### Pipeline Class

```python
from mfn.functions import pipe

class Pipeline:
    """Build processing pipeline"""

    def __init__(self):
        self.steps = []

    def add_step(self, func):
        self.steps.append(func)
        return self

    def pipe(self, data):
        return pipe(data, *self.steps)

# Build pipeline
pipeline = Pipeline()
pipeline.add_step(validate)
pipeline.add_step(transform)
pipeline.add_step(save)

result = pipeline.process(raw_data)
```

### Fluent Builder

```python
class PipelineBuilder:
    """Fluent pipeline builder"""

    def __init__(self):
        self.steps = []

    def map(self, func):
        self.steps.append(lambda data: map(func, data))
        return self

    def filter(self, predicate):
        self.steps.append(lambda data: filter(predicate, data))
        return self

    def reduce(self, func, initial):
        self.steps.append(lambda data: reduce(func, data, initial))
        return self

    def build(self):
        return lambda data: pipe(data, *self.steps)

# Use
pipeline = (
    PipelineBuilder()
    .map(lambda x: x * 2)
    .filter(lambda x: x > 0)
    .reduce(lambda a, b: a + b, 0)
)

result = pipeline([1, 2, 3, 4, 5])  # 30
```

## Advanced Patterns

### Branching Pipeline

```python
from mfn.functions import pipe

def route(data, condition):
    """Route data through different paths"""
    if condition(data):
        return pipe(data, process_a, save_a)
    else:
        return pipe(data, process_b, save_b)

# Usage
result = route(data, lambda d: d["type"] == "a")
```

### Parallel Pipe

```python
from mfn.functions import parallel_pipe

def parallel_pipe(data, *funcs):
    """Pipe through functions in parallel"""
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda f: f(data), funcs))
    return results

# Usage
results = parallel_pipe(
    data,
    validate,
    transform,
    check_quality
)
```

### Conditional Pipe

```python
def pipe_if(data, condition, func):
    """Apply func only if condition"""
    if condition(data):
        return func(data)
    return data

# Usage
result = pipe(
    raw_data,
    lambda d: pipe_if(d, d.get("debug"), log_debug),
    process
)
```

### tee() - Tap Side Effects

```python
from mfn.functions import tee, pipe

def log(data):
    print(f"Processing: {data}")
    return data

# Tap in pipeline (like Unix tee)
result = pipe(
    data,
    tee(log),       # Log but pass through
    validate,
    transform
)
```

## pipe() vs flow()

```python
from mfn.functions import pipe, flow

# pipe: Standalone functions
result = pipe(
    [1, 2, 3],
    lambda x: [i*2 for i in x],
    lambda x: sum(x)
)

# flow: More readable for methods
result = flow(
    [1, 2, 3],
    lambda l: [i*2 for i in l],
    lambda l: sum(l)
)

# When to use:
# - pipe: Separate functions, clearer
# - flow: Inline lambdas, more compact
```

## Common Pipelines

### Data Processing

```python
from mfn.functions import pipe

def process_csv(text):
    return pipe(
        text,
        lambda s: s.strip(),
        lambda s: s.split(","),
        lambda parts: [int(p.strip()) for p in parts],
        lambda nums: sum(nums) / len(nums)
    )

result = process_csv("1, 2, 3, 4, 5")  # 3.0
```

### String Processing

```python
from mfn.functions import flow

def clean_text(text):
    return flow(
        text,
        str.strip,
        str.lower,
        lambda s: s.replace(" ", "_"),
        lambda s: s.replace("-", "_"),
    )

clean_text("  Hello-World  ")  # "hello_world"
```

### Validation Pipeline

```python
from mfn.functions import pipe

def validate_user(user_data):
    return pipe(
        user_data,
        validate_present,    # Check required fields
        validate_types,      # Check field types
        validate_format,      # Check formats
        validate_unique,     # Check uniqueness
        create_user           # Create user if all pass
    )
```

## Performance

Pipeline overhead is minimal:

```python
# Direct calls
v1 = f1(data)
v2 = f2(v1)
v3 = f3(v2)
# ~0.3µs

# Pipe
result = pipe(data, f1, f2, f3)
# ~0.35µs (slight overhead for wrapper)
```

## Best Practices

### ✅ Do: Keep pipelines simple

```python
# Good: Each step does one thing
pipe(data, validate, transform, save)
```

### ✅ Do: Use meaningful names

```python
# Good: Self-documenting
result = pipe(raw, extract_ids, fetch_users, combine)
```

### ✅ Do: Handle errors

```python
# Good: Short-circuit on error
pipe(data, Result.wrap(validate), Result.and_then(transform))
```

### ❌ Don't: Over-pipe

```python
# Bad: Too many steps, hard to debug
pipe(data, a, b, c, d, e, f, g, h, i, j)

# Better: Break into named sub-pipelines
validated = pipe(data, validate_1, validate_2)
processed = pipe(validated, transform_a, transform_b)
```

## Examples

### ETL Pipeline

```python
from mfn.functions import pipe

def etl_pipeline(raw_data):
    return pipe(
        raw_data,
        extract_data,       # Extract fields
        clean_data,         # Clean and normalize
        validate_data,      # Validate constraints
        transform_data,     # Business logic
        load_data           # Save to database
    )

result = etl_pipeline(raw_csv)
```

### Request Processing

```python
from mfn.functions import pipe

def handle_request(request):
    return pipe(
        request,
        authenticate,       # Verify user
        authorize,         # Check permissions
        validate_input,    # Validate payload
        process,           # Business logic
        respond            # Create response
    )

response = handle_request(http_request)
```

## See Also

- [Composition](./02-composition.md) - Function composition
- [Currying](./01-currying.md) - Incremental arguments
- [Partial Application](./03-partial-application.md) - Fix arguments
- [Function Utilities](./05-function-utilities.md) - tap, tee, trace

---

**Next**: [Function Utilities](./05-function-utilities.md)
