# better-py

> Functional programming patterns for Python - pragmatic, type-safe, and developer-friendly.

[![CI](https://github.com/nesalia-inc/better-py/actions/workflows/pr.yml/badge.svg)](https://github.com/nesalia-inc/better-py/actions/workflows/pr.yml)
[![Coverage](https://codecov.io/gh/nesalia-inc/better-py/badge.svg)](https://codecov.io/gh/nesalia-inc/better-py)
[![PyPI](https://img.shields.io/pypi/v/better-py)](https://pypi.org/project/better-py/)
[![Python](https://img.shields.io/pypi/pyversions/better-py)](https://pypi.org/project/better-py/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## ✨ Features

**Monads & Functional Types**
- `Maybe[T]` - Handle optional values safely
- `Result<T, E>` - Explicit error handling
- `Either<L, R>` - Two-value alternatives
- `Validation<T, E>` - Accumulate validation errors
- And more: `Try`, `IO`, `Reader`, `Writer`, `State`, `Task`, etc.

**Functional Collections**
- `MappableList[T]` - List with functional operations
- `ImmutableDict[K, V]` - Safe immutable dictionaries
- `LazySequence[T]` - Lazy evaluation sequences
- `BidirectionalMap[K, V]` - Two-way lookups

**Function Utilities**
- `curry(f)` - Incremental argument application
- `compose(f, g)` - Function composition
- `pipe(value, f, g)` - Left-to-right pipelines
- `partial(f, ...)` - Fix function arguments

**OOP-First Design**
- Protocol-based (like `collections.abc`)
- Generic types with full type hints
- Method chaining and fluent APIs
- Modern Python patterns (dataclasses, protocols, etc.)

## 🚀 Quick Start

```python
from better_py import Maybe, Result, pipe

# Maybe: Safe optional handling
user = Maybe.from_value(get_user(id))
name = user.map(lambda u: u.name).unwrap_or_else(lambda: "Guest")

# Result: Explicit error handling
def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Result.error("Division by zero")
    return Result.ok(a / b)

result = divide(10, 2)
if result.is_ok():
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.unwrap_error()}")

# Pipe: Data pipelines
result = pipe(
    data,
    validate,
    transform,
    save
)
```

## 📦 Installation

```bash
# Install from PyPI
pip install better-py

# Or with uv (recommended)
uv pip install better-py
```

**Requirements**: Python 3.11+

## 📚 Documentation

- [Getting Started](https://nesalia-inc.github.io/better-py)
- [API Reference](https://nesalia-inc.github.io/better-py/api)
- [Core Concepts](https://nesalia-inc.github.io/better-py/features/core)
- [Monads Guide](https://nesalia-inc.github.io/better-py/features/monads)
- [Examples](https://nesalia-inc.github.io/better-py/examples)

## 💡 Why better-py?

### Pragmatic FP

Not academic functional programming - practical patterns that make software development easier.

### Type-Safe

Full type hints with mypy strict mode. Catch errors before runtime.

### OOP-First

Everything is an object. Operations are functional. Works naturally with Python.

### Developer-Friendly

Clear error messages, helpful APIs, extensive documentation.

## 🎯 Use Cases

```python
# REST API error handling
from better_py import Result

async def get_user(id: int) -> Result[User, Error]:
    user = await db.fetch_user(id)
    if not user:
        return Result.error(Error("User not found"))
    return Result.ok(user)

# Data validation
from better_py import Validation

email_validated = Validation.validate(email, EmailValidator())
password_validated = Validation.validate(password, PasswordValidator())

user_validation = email_validated.and_then(password_validated)
if user_validation.is_valid():
    create_user(email, password)

# Data processing pipeline
from better_py import pipe

result = pipe(
    raw_data,
    clean,
    validate,
    transform,
    load_to_db
)
```

## 🏗️ Project Status

**Current Version**: 0.1.0 (Alpha)

**What's Working**:
- ✅ Documentation framework
- ✅ CI/CD pipeline
- ✅ Type system design

**In Development**:
- 🔄 Core protocols (Mappable, Reducible, etc.)
- 🔄 Monad implementations
- 🔄 Functional collections
- 🔄 Function utilities

**Planned**:
- 📋 More monads (Writer, State, etc.)
- 📋 Performance benchmarks
- 📋 Integration examples (FastAPI, SQLAlchemy, etc.)

See [Issues](https://github.com/nesalia-inc/better-py/issues) for detailed roadmap.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Quick start:
```bash
# Clone repository
git clone https://github.com/nesalia-inc/better-py.git
cd better-py

# Install with uv
uv venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv sync --all-extras

# Run tests
uv run pytest

# Run checks
uv run ruff check .
uv run mypy better_py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Inspired by:
- [toolz](https://github.com/pytoolz/toolz)
- [returns](https://github.com/dry-python/returns)
- [cats](https://github.com/typelevel/cats)
- [scalaz](https://github.com/scalaz/scalaz)

## 📮 Contact

- GitHub: [nesalia-inc/better-py](https://github.com/nesalia-inc/better-py)
- Issues: [GitHub Issues](https://github.com/nesalia-inc/better-py/issues)

---

Made with ❤️ by [nesalia-inc](https://github.com/nesalia-inc)
