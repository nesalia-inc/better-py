# Configurable: Configuration Management

**Configurable** is a protocol for objects that can be **configured from multiple sources** - environment variables, config files, CLI arguments, with type-safe validation.

## Overview

```python
@runtime_checkable
class Configurable(Protocol[T]):
    """Objects that can be configured"""

    @classmethod
    def from_config(cls, config: dict | 'Config') -> T:
        """Create from configuration"""
        ...

    def to_config(self) -> dict:
        """Export to configuration dict"""
        ...
```

## Core Concepts

### Configuration Sources

- **Environment variables**: `DB_HOST`, `DB_PORT`
- **Config files**: JSON, YAML, TOML, INI
- **CLI arguments**: `--db-host localhost`
- **Defaults**: Hardcoded fallbacks
- **Overrides**: Runtime configuration

### Priority (Low to High)

1. Defaults
2. Config file
3. Environment variables
4. CLI arguments
5. Runtime overrides

## Implementations

### Config Entity

```python
from dataclasses import dataclass, field
import os
import json
from pathlib import Path
from typing import Any

@dataclass(frozen=True, slots=True)
class Config:
    """Configuration container"""

    values: dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split(".")
        value = self.values

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_required(self, key: str) -> Any:
        """Get required config value"""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required config key missing: {key}")
        return value

    def set(self, key: str, value: Any) -> 'Config':
        """Return new config with key set"""
        keys = key.split(".")
        new_values = dict(self.values)

        current = new_values
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

        return Config(new_values)

    def update(self, **kwargs) -> 'Config':
        """Return new config with updates"""
        return Config({**self.values, **kwargs})

    def merge(self, other: 'Config') -> 'Config':
        """Merge with other (other takes precedence)"""
        return Config({**self.values, **other.values})

    def to_dict(self) -> dict:
        return self.values.copy()

    @classmethod
    def empty(cls) -> 'Config':
        """Empty config"""
        return cls({})

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """Create from dict"""
        return cls(dict(data))

    @classmethod
    def from_json(cls, path: str) -> 'Config':
        """Load from JSON file"""
        with open(path) as f:
            return cls(json.load(f))

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """Load from YAML file"""
        import yaml
        with open(path) as f:
            return cls(yaml.safe_load(f))

    @classmethod
    def from_env(cls, prefix: str = "") -> 'Config':
        """Load from environment variables"""
        values = {}

        for key, value in os.environ.items():
            if prefix and not key.startswith(prefix):
                continue

            # Remove prefix and convert to nested dict
            config_key = key[len(prefix):] if prefix else key
            config_key = config_key.lower()

            # Convert __ to .
            config_key = config_key.replace("__", ".")

            # Set value
            current = values
            parts = config_key.split(".")
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Try to parse as JSON for complex types
            try:
                current[parts[-1]] = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                current[parts[-1]] = value

        return cls(values)

    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Load from file (auto-detect format)"""
        path_obj = Path(path)

        if path_obj.suffix == ".json":
            return cls.from_json(path)
        elif path_obj.suffix in [".yaml", ".yml"]:
            return cls.from_yaml(path)
        elif path_obj.suffix == ".toml":
            return cls.from_toml(path)
        else:
            raise ValueError(f"Unsupported config format: {path_obj.suffix}")

    @classmethod
    def from_toml(cls, path: str) -> 'Config':
        """Load from TOML file"""
        try:
            import tomli
        except ImportError:
            import tomllib as tomli

        with open(path, "rb") as f:
            return cls(tomli.load(f))

    def to_json(self, path: str) -> None:
        """Save to JSON file"""
        with open(path, "w") as f:
            json.dump(self.values, f, indent=2)

    def to_yaml(self, path: str) -> None:
        """Save to YAML file"""
        import yaml
        with open(path, "w") as f:
            yaml.dump(self.values, f)
```

#### Usage Examples

```python
# From dict
config = Config.from_dict({
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Get values
host = config.get("database.host")  # "localhost"
port = config.get("database.port", 3306)  # 5432

# Set values
config2 = config.set("database.ssl", True)

# From environment
# $ export DB__HOST=localhost
# $ export DB__PORT=5432
config = Config.from_env(prefix="DB_")
# {"host": "localhost", "port": 5432}

# From file
config = Config.from_file("config.json")

# Merge configs
defaults = Config.from_dict({"host": "localhost", "port": 5432})
overrides = Config.from_dict({"port": 3306})
merged = defaults.merge(overrides)
# {"host": "localhost", "port": 3306}
```

### Configurable Protocol

```python
@runtime_checkable
class Configurable(Protocol[T]):
    """Objects that can be configured"""

    @classmethod
    def from_config(cls, config: Config | dict) -> T:
        """Create from configuration"""
        ...

    def to_config(self) -> Config:
        """Export to configuration"""
        ...
```

### Configurable Dataclass

```python
@dataclass(frozen=True, slots=True)
class DatabaseConfig(Configurable):
    """Database configuration"""

    host: str = "localhost"
    port: int = 5432
    database: str = "mydb"
    username: str = "user"
    password: str = ""
    ssl: bool = False
    pool_size: int = 10

    @classmethod
    def from_config(cls, config: Config | dict) -> 'DatabaseConfig':
        """Create from configuration"""
        if isinstance(config, dict):
            config = Config.from_dict(config)

        return cls(
            host=config.get("database.host", "localhost"),
            port=config.get("database.port", 5432),
            database=config.get("database.database", "mydb"),
            username=config.get("database.username", "user"),
            password=config.get("database.password", ""),
            ssl=config.get("database.ssl", False),
            pool_size=config.get("database.pool_size", 10)
        )

    def to_config(self) -> Config:
        """Export to configuration"""
        return Config.from_dict({
            "database": {
                "host": self.host,
                "port": self.port,
                "database": self.database,
                "username": self.username,
                "password": self.password,
                "ssl": self.ssl,
                "pool_size": self.pool_size
            }
        })

    def validate(self) -> Validation:
        """Validate configuration"""
        errors = []

        if not self.host:
            errors.append(ValidationError("Database host is required"))

        if not (1 <= self.port <= 65535):
            errors.append(ValidationError(f"Invalid port: {self.port}"))

        if not self.database:
            errors.append(ValidationError("Database name is required"))

        if self.pool_size < 1:
            errors.append(ValidationError("Pool size must be >= 1"))

        if errors:
            return Validation.errors_(*errors)
        return Validation.success(self)

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Load from environment"""
        return cls.from_config(Config.from_env(prefix="DB_"))
```

#### Usage Examples

```python
# From config
config = Config.from_dict({
    "database": {
        "host": "remotehost",
        "port": 3306
    }
})

db_config = DatabaseConfig.from_config(config)
# DatabaseConfig(host="remotehost", port=3306, ...)

# From environment
# $ export DB__HOST=localhost
# $ export DB__PORT=5432
db_config = DatabaseConfig.from_env()

# Validate
result = db_config.validate()
if result.is_errors():
    for error in result.errors:
        print(error)
```

### ConfigBuilder

```python
@dataclass
class ConfigBuilder:
    """Fluent builder for configuration"""

    _defaults: Config = field(default_factory=Config.empty)
    _config_file: str | None = None
    _env_prefix: str | None = None
    _overrides: Config = field(default_factory=Config.empty)

    def with_defaults(self, defaults: dict) -> 'ConfigBuilder':
        """Set default values"""
        return Replace(self, _defaults=Config.from_dict(defaults))

    def with_config_file(self, path: str) -> 'ConfigBuilder':
        """Load config from file"""
        return Replace(self, _config_file=path)

    def with_env(self, prefix: str = "") -> 'ConfigBuilder':
        """Load from environment"""
        return Replace(self, _env_prefix=prefix)

    def with_overrides(self, overrides: dict) -> 'ConfigBuilder':
        """Set runtime overrides"""
        return Replace(self, _overrides=Config.from_dict(overrides))

    def build(self) -> Config:
        """Build final config (merges all sources)"""
        config = self._defaults

        # Load config file
        if self._config_file:
            config = config.merge(Config.from_file(self._config_file))

        # Load from environment
        if self._env_prefix:
            config = config.merge(Config.from_env(self._env_prefix))

        # Apply overrides
        config = config.merge(self._overrides)

        return config

# Usage
config = (
    ConfigBuilder()
    .with_defaults({"host": "localhost", "port": 5432})
    .with_config_file("config.json")
    .with_env(prefix="APP_")
    .with_overrides({"port": 3306})
    .build()
)
```

### TypedConfig

```python
@dataclass(frozen=True, slots=True)
class TypedConfig(Generic[T]):
    """Type-safe configuration container"""

    config: Config
    _type: type[T] = field(init=False)

    @classmethod
    def for_type(cls, config_type: type[T]) -> 'TypedConfig[T]':
        """Create typed config for a Configurable type"""
        return cls(
            config=config_type().to_config(),
            _type=config_type
        )

    def load(self, path: str | None = None) -> T:
        """Load configuration and create typed object"""
        if path:
            self.config = self.config.merge(Config.from_file(path))

        return self._type.from_config(self.config)

    @classmethod
    def from_file(cls, config_type: type[T], path: str) -> T:
        """Load typed config from file"""
        config = Config.from_file(path)
        return config_type.from_config(config)

    @classmethod
    def from_env(cls, config_type: type[T], prefix: str = "") -> T:
        """Load typed config from environment"""
        config = Config.from_env(prefix=prefix)
        return config_type.from_config(config)

# Usage
db_config = TypedConfig.from_file(DatabaseConfig, "database.json")
# Or
db_config = TypedConfig.from_env(DatabaseConfig, prefix="DB_")
```

## Advanced Patterns

### Secret Management

```python
@dataclass(frozen=True, slots=True)
class SecretsConfig:
    """Configuration for secrets (never logged)"""

    _secrets: dict[str, str]

    @classmethod
    def from_env(cls, prefix: str = "SECRET_") -> 'SecretsConfig':
        """Load secrets from environment"""
        secrets = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                secret_key = key[len(prefix):].lower()
                secrets[secret_key] = value
        return cls(secrets)

    def get(self, key: str) -> str:
        """Get secret"""
        if key not in self._secrets:
            raise ValueError(f"Secret not found: {key}")
        return self._secrets[key]

    def __repr__(self) -> str:
        return f"SecretsConfig({len(self._secrets)} secrets)"

    def __str__(self) -> str:
        return self.__repr__()
```

### Profile-Based Configuration

```python
@dataclass
class ProfileConfig:
    """Configuration with profiles (dev, test, prod)"""

    profile: str = "dev"
    configs: dict[str, Config] = field(default_factory=dict)

    def add_profile(self, name: str, config: Config) -> 'ProfileConfig':
        """Add profile configuration"""
        self.configs[name] = config
        return self

    def get_config(self) -> Config:
        """Get configuration for current profile"""
        # Start with base config
        config = self.configs.get("base", Config.empty())

        # Merge profile-specific config
        if self.profile in self.configs:
            config = config.merge(self.configs[self.profile])

        return config

    @classmethod
    def from_directory(cls, directory: str, profile: str = "dev") -> 'ProfileConfig':
        """Load profiles from directory"""
        import yaml

        config = cls(profile=profile)

        for path in Path(directory).glob("*.yaml"):
            profile_name = path.stem
            with open(path) as f:
                profile_config = Config.from_dict(yaml.safe_load(f))
                config.add_profile(profile_name, profile_config)

        return config

# Usage
config = ProfileConfig.from_directory("./config", profile="prod")
final_config = config.get_config()
```

### Config Validation

```python
@dataclass
class ValidatedConfig(Generic[T]):
    """Configuration with built-in validation"""

    config: Config
    validator: Validator[Config]

    def validate(self) -> Validation:
        """Validate configuration"""
        return self.validator.validate(self.config)

    def get_validated(self) -> Result[T, Exception]:
        """Get typed config if valid"""
        result = self.validate()
        if result.is_errors():
            return Error(ValidationError(result.errors))
        return Ok(self.config)
```

## Protocol Compliance

```python
@runtime_checkable
class Configurable(Protocol[T]):
    @classmethod
    def from_config(cls, config): ...
    def to_config(self): ...

@dataclass
class CustomConfigurable:
    value: int = 42

    @classmethod
    def from_config(cls, config):
        if isinstance(config, dict):
            config = Config.from_dict(config)
        return cls(config.get("value", 42))

    def to_config(self):
        return Config.from_dict({"value": self.value})

# CustomConfigurable is Configurable!
isinstance(CustomConfigurable, Configurable)  # True (protocol)
```

## Best Practices

### ✅ Do: Use environment variables for secrets

```python
# Good: Secrets from environment
password = os.getenv("DB_PASSWORD")

# Bad: Secrets in config files
# config.json: {"password": "secret123"}
```

### ✅ Do: Validate configuration early

```python
# Good: Validate on startup
config = DatabaseConfig.from_env()
result = config.validate()
if result.is_errors():
    raise ConfigError(result.errors)
```

### ❌ Don't: Mix configuration sources without priority

```python
# Bad: Unclear priority
config = defaults
config = config.update(env_vars)  # Which wins?
config = config.update(cli_args)

# Good: Clear merge order
config = defaults.merge(file_config).merge(env_config).merge(cli_config)
```

## Summary

**Configurable** protocol:
- ✅ Load from multiple sources (dict, JSON, YAML, ENV)
- ✅ Type-safe configuration objects
- ✅ Validation support
- ✅ Builder pattern for complex config
- ✅ Profile-based configuration
- ✅ Secret management

**Key benefit**: **Centralized configuration** with **type safety** and **validation**.

---

**End of Functional Entities**

Next steps:
- See [Core Concepts](../core/) for foundational patterns
- See [Monads](../monads/) for error handling
- See [Examples](../examples/) for practical usage
