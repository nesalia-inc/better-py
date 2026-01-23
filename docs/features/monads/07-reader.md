# Reader - Dependency Injection

Handle dependencies and environment with the Reader monad.

## Overview

`Reader` represents a computation that depends on an environment/context:
- `Reader(func)` - Function that takes environment and returns value

## Basic Usage

```python
from mfn import Reader

# Create Reader
def greet(environment: dict) -> str:
    name = environment.get("name", "Guest")
    return f"Hello, {name}!"

reader = Reader(greet)

# Run with environment
env = {"name": "Alice"}
result = reader.run(env)
# "Hello, Alice!"

# Different environment
env = {"name": "Bob"}
result = reader.run(env)
# "Hello, Bob!"
```

## Transformation

```python
from mfn import Reader

# Map: Transform output
def upper_case(greeting: str) -> str:
    return greeting.upper()

reader = Reader(lambda env: f"Hello, {env.get('name', 'Guest')}!")
result = reader.map(upper_case).run({"name": "Alice"})
# "HELLO, ALICE!"

# Then: Chain Reader-returning function
def get_user(env: dict) -> Reader:

    def get_posts(user: dict):
        db = env["database"]
        posts = db.get_posts(user["id"])
        return posts

    return Reader(lambda e: get_posts(e.get("user", {})))
```

## Composing Readers

```python
from mfn import Reader

def read_config(env: dict) -> dict:
    """Read configuration from environment"""
    return env.get("config", {})

def get_database(config: dict) -> Reader:

    def connect(env: dict):
        db_url = config.get("database_url")
        return Database(db_url)

    return Reader(connect)

def get_users(db: Database) -> list:
    """Get users from database"""
    return db.query("SELECT * FROM users")


# Compose
def fetch_users(env: dict) -> list:

    config = read_config(env)
    db_reader = get_database(config)
    db = db_reader.run(env)
    return get_users(db)


# Or with helpers
def compose_reader() -> Reader:

    def inner(env: dict):
        config = read_config(env)
        db = get_database(config).run(env)
        return get_users(db)

    return Reader(inner)
```

## Common Dependencies

```python
from mfn import Reader

class AppContext:
    """Application context"""

    def __init__(
        self,
        database: Database,
        cache: Cache,
        logger: Logger,
        config: dict
    ):
        self.database = database
        self.cache = cache
        self.logger = logger
        self.config = config


def create_user(data: dict) -> Reader:

    def inner(context: AppContext):
        # Use dependencies from context
        existing = context.database.find_user(data["email"])

        if existing:
            context.logger.warning(f"User exists: {data['email']}")
            raise ValueError("User already exists")

        user = context.database.create_user(data)
        context.cache.set(f"user:{user.id}", user)

        context.logger.info(f"Created user: {user.id}")

        return user

    return Reader(inner)


# Use
context = AppContext(db, cache, logger, config)
user = create_user({"email": "alice@example.com"}).run(context)
```

## Local Context

```python
from mfn import Reader

def with_local_env(reader: Reader, updates: dict) -> Reader:

    def inner(env: dict):
        new_env = {**env, **updates}
        return reader.run(new_env)

    return Reader(inner)


# Use
base_reader = Reader(lambda env: env["value"])

result = base_reader.run({"value": 42})
# 42

# Override environment
result = with_local_env(base_reader, {"value": 100}).run({})
# 100
```

## Asking for Dependencies

```python
from mfn import Reader

# Helper to ask for specific dependency
def ask(key: str) -> Reader:

    def inner(env: dict):
        if key not in env:
            raise ValueError(f"Missing dependency: {key}")
        return env[key]

    return Reader(inner)


# Use
def process_user() -> Reader:

    def inner(env: dict):
        # Ask for dependencies
        db = ask("database").run(env)
        cache = ask("cache").run(env)

        # Use them
        user = cache.get("user:1") or db.find_user(1)
        return user

    return Reader(inner)
```

## Combining Multiple Readers

```python
from mfn import Reader

def merge_readers(*readers: Reader) -> Reader:

    def inner(env: dict):
        return [reader.run(env) for reader in readers]

    return Reader(inner)


# Use
def get_config(env: dict) -> dict:
    return env.get("config", {})

def get_database(env: dict) -> Database:
    return env.get("database")

def get_logger(env: dict) -> Logger:
    return env.get("logger")

all_deps = merge_readers(
    Reader(get_config),
    Reader(get_database),
    Reader(get_logger)
)

config, db, logger = all_deps.run(app_context)
```

## Partial Application

```python
from mfn import Reader

def fetch_user(user_id: int) -> Reader:

    def inner(env: dict):
        db = env["database"]
        return db.find_user(user_id)

    return Reader(inner)

def fetch_posts(user_id: int) -> Reader:

    def inner(env: dict):
        db = env["database"]
        return db.get_posts(user_id)

    return Reader(inner)

# Partial application
def get_user_data(user_id: int) -> Reader:

    def inner(env: dict):
        user = fetch_user(user_id).run(env)
        posts = fetch_posts(user_id).run(env)

        return {
            "user": user,
            "posts": posts
        }

    return Reader(inner)


# Use
data = get_user_data(1).run(app_context)
```

## DX Benefits

✅ **Explicit**: Dependencies are visible
✅ **Testable**: Easy to inject test doubles
✅ **Composable**: Combine dependent operations
✅ **No globals**: Pass context explicitly
✅ **Flexible**: Change context per call

## Best Practices

```python
# ✅ Good: Explicit dependencies
def create_user(data: dict) -> Reader:
    # db, cache, logger come from environment

# ✅ Good: Type the environment
class AppContext:
    db: Database
    cache: Cache

# ✅ Good: Compose readers
merge_readers(fetch_user, fetch_posts)

# ❌ Bad: Global dependencies
# Don't use global variables

# ❌ Bad: Hidden dependencies
# Make all dependencies explicit in environment
```
