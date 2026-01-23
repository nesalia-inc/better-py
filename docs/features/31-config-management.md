# Config Management - Configuration Handling

Manage application configuration with type safety and validation.

## Overview

Config management enables:
- Multiple config sources
- Type-safe access
- Environment variable support
- Validation
- Default values

## Basic Configuration

```python
from typing import Any, TypeVar, Generic, Type, get_type_hints
from dataclasses import dataclass
from pathlib import Path
import os

T = TypeVar('T')

class ConfigError(Exception):
    """Configuration error"""

    pass


@dataclass
class ConfigValue:
    """Typed configuration value"""

    key: str
    value: Any
    type_hint: Type | None
    required: bool = False
    default: Any = None
    validator: Callable | None = None

    def get(self) -> Any:

        if self.value is None:
            if self.required:
                raise ConfigError(f"Required config key missing: {self.key}")
            return self.default

        # Type coerce
        if self.type_hint:
            try:
                if self.type_hint == bool:
                    return self._to_bool(self.value)
                return self.type_hint(self.value)
            except (ValueError, TypeError) as e:
                raise ConfigError(
                    f"Config key '{self.key}' must be {self.type_hint.__name__}"
                ) from e

        return self.value

    def _to_bool(self, value: Any) -> bool:
        """Convert to bool"""

        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        if isinstance(value, (int, float)):
            return bool(value)
        raise ValueError(f"Cannot convert {value} to bool")

    def validate(self) -> None:

        value = self.get()

        if self.validator:
            if not self.validator(value):
                raise ConfigError(f"Config key '{self.key}' failed validation")


class Config:
    """Configuration manager"""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self._values: dict[str, ConfigValue] = {}

    def set(self, key: str, value: Any, **kwargs) -> 'Config':
        """Set config value"""

        config_value = ConfigValue(key=key, value=value, **kwargs)
        self._values[key] = config_value
        return self

    def load_dict(self, data: dict) -> 'Config':
        """Load from dictionary"""

        for key, value in data.items():
            self._values[key] = ConfigValue(key=key, value=value)

        return self

    def load_env(self, prefix: str = "") -> 'Config':

        full_prefix = f"{self.prefix}{prefix}"

        for key, value in os.environ.items():

            if full_prefix and not key.startswith(full_prefix):
                continue

            config_key = key[len(full_prefix):] if full_prefix else key
            config_key = config_key.lower()

            self._values[config_key] = ConfigValue(
                key=config_key,
                value=value
            )

        return self

    def load_file(self, filepath: str | Path) -> 'Config':
        """Load from config file (JSON/YAML)"""

        filepath = Path(filepath)

        if not filepath.exists():
            raise ConfigError(f"Config file not found: {filepath}")

        if filepath.suffix == ".json":
            import json
            with open(filepath) as f:
                data = json.load(f)
        elif filepath.suffix in (".yml", ".yaml"):
            import yaml
            with open(filepath) as f:
                data = yaml.safe_load(f)
        else:
            raise ConfigError(f"Unsupported config file: {filepath}")

        return self.load_dict(data)

    def get(self, key: str, default: Any = None) -> Any:

        if key not in self._values:
            return default

        return self._values[key].get()

    def get_int(self, key: str, default: int = 0) -> int:
        return self.get(key, default)

    def get_str(self, key: str, default: str = "") -> str:
        return self.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        return self.get(key, default)

    def get_float(self, key: str, default: float = 0.0) -> float:
        return self.get(key, default)

    def require(self, key: str, type_hint: Type | None = None) -> Any:

        if key not in self._values:
            raise ConfigError(f"Required config key missing: {key}")

        if type_hint:
            self._values[key].type_hint = type_hint
            self._values[key].required = True

        return self._values[key].get()

    def validate_all(self) -> None:

        for config_value in self._values.values():
            config_value.validate()


# === Usage ===

config = Config(prefix="APP_")

# Set values
config.set("debug", True, type_hint=bool)
config.set("port", 8000, type_hint=int, default=8000)
config.set("host", "localhost", type_hint=str)

# Load from dict
config.load_dict({
    "database_url": "postgresql://localhost/mydb",
    "max_connections": 10
})

# Access
print(config.get_bool("debug"))  # True
print(config.get_int("port"))    # 8000
print(config.get_str("host"))    # "localhost"
```

## Environment Variables

```python
class EnvConfig:
    """Environment-based configuration"""

    def __init__(self, prefix: str = ""):
        self.prefix = prefix

    def get(self, key: str, default: Any = None, type_hint: Type | None = None) -> Any:

        env_key = f"{self.prefix}{key}".upper()

        if env_key not in os.environ:
            return default

        value = os.environ[env_key]

        if type_hint:
            config_value = ConfigValue(key=key, value=value, type_hint=type_hint)
            return config_value.get()

        return value

    def require(self, key: str, type_hint: Type | None = None) -> Any:

        env_key = f"{self.prefix}{key}".upper()

        if env_key not in os.environ:
            raise ConfigError(f"Required environment variable: {env_key}")

        value = os.environ[env_key]

        if type_hint:
            config_value = ConfigValue(key=key, value=value, type_hint=type_hint, required=True)
            return config_value.get()

        return value


# === Usage ===

# Set environment variables
os.environ["APP_DATABASE_URL"] = "postgresql://localhost/mydb"
os.environ["APP_PORT"] = "8000"
os.environ["APP_DEBUG"] = "true"

env = EnvConfig(prefix="APP_")

db_url = env.require("database_url")
port = env.get("port", type_hint=int, default=5432)
debug = env.get("debug", type_hint=bool, default=False)

print(db_url)  # "postgresql://localhost/mydb"
print(port)    # 8000
print(debug)   # True
```

## Typed Configuration

```python
from typing import Protocol

class TypedConfig(Protocol):
    """Typed configuration interface"""

    database_url: str
    port: int
    debug: bool


def create_typed_config() -> TypedConfig:
    """Create typed configuration from environment"""

    env = EnvConfig(prefix="APP_")

    class _Config:
        database_url = env.require("database_url")
        port = env.get("port", type_hint=int, default=8000)
        debug = env.get("debug", type_hint=bool, default=False)

    return _Config()  # type: ignore


# === Usage ===

config = create_typed_config()

# Type-safe access
print(config.database_url)  # str
print(config.port)          # int
print(config.debug)         # bool
```

## Configuration Layers

```python
class LayeredConfig:
    """Configuration with multiple layers"""

    def __init__(self):
        self.layers: list[Config] = []

    def add_layer(self, config: Config) -> 'LayeredConfig':
        """Add configuration layer"""

        self.layers.append(config)
        return self

    def get(self, key: str, default: Any = None) -> Any:

        # Search layers in reverse order (last added wins)
        for config in reversed(self.layers):
            if key in config._values:
                return config._values[key].get()

        return default


# === Usage ===

# Default config
defaults = Config()
defaults.set("port", 8000)
defaults.set("debug", False)

# File config
file_config = Config()
file_config.load_file("config.json")

# Environment config (highest priority)
env_config = Config()
env_config.load_env(prefix="APP_")

# Layer them
layered = LayeredConfig()
layered.add_layer(defaults)
layered.add_layer(file_config)
layered.add_layer(env_config)

# Env overrides file, file overrides defaults
print(layered.get("port"))
```

## Configuration Validation

```python
class ValidatedConfig:
    """Configuration with schema validation"""

    def __init__(self):
        self.config = Config()
        self.schema: dict[str, dict] = {}

    def add_field(
        self,
        key: str,
        type_hint: Type,
        required: bool = False,
        default: Any = None,
        validator: Callable | None = None
    ) -> 'ValidatedConfig':

        self.schema[key] = {
            "type_hint": type_hint,
            "required": required,
            "default": default,
            "validator": validator
        }

        return self

    def load(self, source: dict | Path | str) -> 'ValidatedConfig':

        if isinstance(source, dict):
            self.config.load_dict(source)
        elif isinstance(source, (Path, str)):
            self.config.load_file(source)

        return self

    def validate(self) -> Config:

        # Build config values from schema
        for key, spec in self.schema.items():

            value = self.config.get(key)

            self.config.set(
                key,
                value,
                type_hint=spec["type_hint"],
                required=spec["required"],
                default=spec["default"],
                validator=spec["validator"]
            )

        # Validate all
        self.config.validate_all()

        return self.config


# === Usage ===

validated = (
    ValidatedConfig()
    .add_field("database_url", str, required=True)
    .add_field("port", int, required=False, default=5432, validator=lambda x: 1 <= x <= 65535)
    .add_field("pool_size", int, required=False, default=10, validator=lambda x: x > 0)
    .load({
        "database_url": "postgresql://localhost/mydb",
        "port": 5433
    })
    .validate()
)

print(validated.get_str("database_url"))  # "postgresql://localhost/mydb"
print(validated.get_int("port"))          # 5433
print(validated.get_int("pool_size"))     # 10 (default)
```

## DX Benefits

✅ **Type-safe**: Typed access
✅ **Multiple sources**: Files, env, dicts
✅ **Layered**: Priority system
✅ **Validated**: Schema validation
✅ **Clear errors**: Helpful error messages

## Best Practices

```python
# ✅ Good: Prefix environment variables
EnvConfig(prefix="APP_")

# ✅ Good: Provide defaults
config.get("timeout", type_hint=int, default=30)

# ✅ Good: Validate
.add_field("port", int, validator=lambda x: 1 <= x <= 65535)

# ✅ Good: Layer configs
defaults -> file -> env

# ❌ Bad: Hardcoded config
# Use environment variables instead
```
