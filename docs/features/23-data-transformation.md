# Data Transformation - ETL Pipelines

Build data transformation pipelines for ETL operations.

## Overview

Data transformation enables:
- Clean ETL pipeline structure
- Composable transformations
- Error handling
- Progress tracking
- Type safety

## Basic Transformation Pipeline

```python
from typing import Callable, TypeVar, Generic, Any
from dataclasses import dataclass

T = TypeVar('T')
U = TypeVar('U')

class TransformStep:
    """Single transformation step"""

    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func

    def __call__(self, data: Any) -> Any:
        return self.func(data)


class Pipeline:
    """Data transformation pipeline"""

    def __init__(self, name: str = "pipeline"):
        self.name = name
        self._steps: list[TransformStep] = []

    def step(self, func: Callable, name: str | None = None) -> 'Pipeline':
        """Add transformation step"""

        step_name = name or func.__name__
        self._steps.append(TransformStep(step_name, func))
        return self

    def map(self, func: Callable) -> 'Pipeline':
        """Add map step"""
        return self.step(func, "map")

    def filter(self, predicate: Callable) -> 'Pipeline':
        """Add filter step"""

        def filter_step(data):
            if isinstance(data, list):
                return [item for item in data if predicate(item)]
            return data if predicate(data) else None

        return self.step(filter_step, "filter")

    def validate(self, validator: Callable) -> 'Pipeline':
        """Add validation step"""

        def validate_step(data):
            if not validator(data):
                raise ValueError(f"Validation failed: {validator.__name__}")
            return data

        return self.step(validate_step, "validate")

    def __call__(self, data: Any) -> Any:
        """Execute pipeline"""

        result = data
        for step in self._steps:
            result = step(result)
        return result

    def __or__(self, other: 'Pipeline') -> 'Pipeline':
        """Combine pipelines: pipeline1 | pipeline2"""

        combined = Pipeline(f"{self.name} | {other.name}")
        combined._steps = self._steps + other._steps
        return combined


# === Usage ===

def extract_fields(data: dict) -> dict:
    """Extract specific fields"""
    return {
        "name": data.get("name", "").strip(),
        "email": data.get("email", "").lower(),
        "age": data.get("age", 0)
    }

def normalize_types(data: dict) -> dict:
    """Normalize data types"""
    return {
        **data,
        "age": int(data.get("age", 0))
    }

def validate_data(data: dict) -> bool:
    """Validate data"""
    return (
        len(data.get("name", "")) >= 2
        and "@" in data.get("email", "")
        and data.get("age", 0) >= 0
    )

def enrich_user(data: dict) -> dict:
    """Enrich with computed fields"""
    return {
        **data,
        "created_at": datetime.now(),
        "is_adult": data["age"] >= 18,
        "email_domain": data["email"].split("@")[1]
    }

# Build pipeline
process_user = (
    Pipeline("process_user")
    .step(extract_fields)
    .step(normalize_types)
    .validate(validate_data)
    .step(enrich_user)
)

result = process_user({
    "name": "  alice  ",
    "email": "ALICE@EXAMPLE.COM",
    "age": "25"
})

print(result)
# {
#     "name": "alice",
#     "email": "alice@example.com",
#     "age": 25,
#     "created_at": ...,
#     "is_adult": True,
#     "email_domain": "example.com"
# }
```

## Error Handling in Pipeline

```python
from typing import TypeVar, Generic

class PipelineError:
    """Pipeline error with context"""

    def __init__(self, step: str, error: Exception, data: Any):
        self.step = step
        self.error = error
        self.data = data

    def __repr__(self):
        return f"PipelineError(step={self.step}, error={self.error})"


class SafePipeline(Pipeline):
    """Pipeline with error handling"""

    def __init__(self, name: str = "safe_pipeline", stop_on_error: bool = True):
        super().__init__(name)
        self.stop_on_error = stop_on_error
        self.errors: list[PipelineError] = []

    def __call__(self, data: Any) -> Any:

        self.errors.clear()
        result = data

        for step in self._steps:
            try:
                result = step(result)

            except Exception as e:
                error = PipelineError(step.name, e, result)
                self.errors.append(error)

                if self.stop_on_error:
                    raise error

        return result

    def get_errors(self) -> list[PipelineError]:
        return self.errors.copy()

    def has_errors(self) -> bool:
        return len(self.errors) > 0


# === Usage ===

safe_pipeline = (
    SafePipeline("safe_process", stop_on_error=False)
    .step(extract_fields)
    .step(normalize_types)
    .step(validate_data)  # Might fail
)

result = safe_pipeline(invalid_data)

if safe_pipeline.has_errors():
    for error in safe_pipeline.get_errors():
        print(f"Error in {error.step}: {error.error}")
```

## Batch Processing

```python
def batch_pipeline(
    pipeline: Pipeline,
    batch_size: int = 100
) -> Callable:

    def process_batch(items: list) -> list:
        """Process items in batches"""

        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            results.extend(pipeline(batch))

        return results

    return process_batch


# === Usage ===

process_users_batch = batch_pipeline(process_user, batch_size=50)

all_users = [user1, user2, user3, ...]  # 1000 users
processed = process_users_batch(all_users)
```

## Parallel Pipeline

```python
import concurrent.futures
from typing import Callable

def parallel_pipeline(
    pipeline: Pipeline,
    max_workers: int = 4
) -> Callable:

    def process_parallel(items: list) -> list:

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(pipeline, item) for item in items]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        return results

    return process_parallel


# === Usage ===

process_users_parallel = parallel_pipeline(process_user, max_workers=8)

users = [user1, user2, ...]  # Many users
processed = process_users_parallel(users)
```

## Conditional Pipeline

```python
class ConditionalPipeline(Pipeline):
    """Pipeline with conditional steps"""

    def __init__(self, name: str = "conditional"):
        super().__init__(name)
        self._conditional_steps: list[tuple[Callable, Pipeline]] = []

    def branch(
        self,
        condition: Callable,
        pipeline: Pipeline
    ) -> 'ConditionalPipeline':

        self._conditional_steps.append((condition, pipeline))
        return self

    def __call__(self, data: Any) -> Any:

        result = data

        # Execute unconditional steps
        for step in self._steps:
            result = step(result)

        # Execute conditional branches
        for condition, branch in self._conditional_steps:
            if condition(result):
                result = branch(result)

        return result


# === Usage ===

premium_pipeline = Pipeline("premium").step(add_premium_features)
free_pipeline = Pipeline("free").step(add_basic_features)

process_user = (
    ConditionalPipeline("user_process")
    .step(validate_user)
    .branch(
        condition=lambda u: u.is_premium,
        pipeline=premium_pipeline
    )
    .branch(
        condition=lambda u: not u.is_premium,
        pipeline=free_pipeline
    )
)
```

## Pipeline Composition

```python
class PipelineComposer:
    """Compose multiple pipelines"""

    @staticmethod
    def sequential(*pipelines: Pipeline) -> Pipeline:

        result = Pipeline("sequential")
        result._steps = []

        for pipeline in pipelines:
            result._steps.extend(pipeline._steps)

        return result

    @staticmethod
    def parallel(*pipelines: Pipeline) -> Pipeline:

        def parallel_step(data):
            return [pipeline(data) for pipeline in pipelines]

        return Pipeline("parallel").step(parallel_step)

    @staticmethod
    def merge(merge_func: Callable, *pipelines: Pipeline) -> Pipeline:

        def merge_step(data):
            results = [pipeline(data) for pipeline in pipelines]
            return merge_func(*results)

        return Pipeline("merge").step(merge_step)


# === Usage ===

extract = Pipeline("extract").step(extract_data)
transform = Pipeline("transform").step(transform_data)
load = Pipeline("load").step(load_data)

# Compose
etl = PipelineComposer.sequential(extract, transform, load)

data = etl(raw_data)
```

## Pipeline Metrics

```python
from time import time
from dataclasses import dataclass

@dataclass
class StepMetrics:
    """Metrics for a pipeline step"""

    name: str
    duration: float
    input_size: int
    output_size: int

    @property
    def filter_rate(self) -> float:
        if self.input_size == 0:
            return 0.0
        return 1.0 - (self.output_size / self.input_size)


class MeasuredPipeline(Pipeline):
    """Pipeline with metrics tracking"""

    def __init__(self, name: str = "measured"):
        super().__init__(name)
        self.metrics: list[StepMetrics] = []

    def __call__(self, data: Any) -> Any:

        self.metrics.clear()
        result = data

        for step in self._steps:
            start = time()

            input_size = len(result) if isinstance(result, list) else 1
            result = step(result)
            output_size = len(result) if isinstance(result, list) else 1

            duration = time() - start

            self.metrics.append(StepMetrics(
                name=step.name,
                duration=duration,
                input_size=input_size,
                output_size=output_size
            ))

        return result

    def get_metrics(self) -> list[StepMetrics]:
        return self.metrics.copy()

    def print_summary(self):
        """Print pipeline summary"""

        total_duration = sum(m.duration for m in self.metrics)

        print(f"\nPipeline: {self.name}")
        print(f"Total duration: {total_duration:.3f}s")
        print(f"Steps: {len(self.metrics)}")

        for metric in self.metrics:
            print(f"  - {metric.name}: {metric.duration:.3f}s "
                  f"({metric.input_size} -> {metric.output_size} items)")


# === Usage ===

measured = MeasuredPipeline("measured_etl")
measured.step(extract_fields)
measured.step(normalize_types)
measured.step(enrich_user)

result = measured(raw_data)
measured.print_summary()
```

## DX Benefits

✅ **Composable**: Build from simple steps
✅ **Reusable**: Share pipelines across project
✅ **Observable**: Track metrics and errors
✅ **Flexible**: Sync, async, parallel options
✅ **Maintainable**: Clear structure

## Best Practices

```python
# ✅ Good: Named steps for debugging
.step(extract_fields, "extract")

# ✅ Good: Small, focused steps
.step(normalize_name)
.step(validate_email)

# ✅ Good: Compose pipelines
etl = extract | transform | load

# ❌ Bad: Too much in one step
# Break into smaller, named steps
```
