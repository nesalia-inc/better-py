"""Tests for Reader monad."""

from better_py.monads import Reader


class TestReader:
    """Tests for Reader monad."""

    def test_reader_ask(self):
        """ask should return the environment."""
        env = {"key": "value"}
        result = Reader.ask().run(env)
        assert result == env

    def test_reader_map(self):
        """map should transform the result."""
        reader = Reader(lambda env: env["value"]).map(lambda x: x * 2)
        result = reader.run({"value": 5})
        assert result == 10

    def test_reader_flat_map(self):
        """flat_map should chain computations."""
        def add_offset(x):
            return Reader(lambda env: x + env.get("offset", 0))

        reader = Reader(lambda env: env["value"]).flat_map(add_offset)
        result = reader.run({"value": 5, "offset": 3})
        assert result == 8

    def test_reader_local(self):
        """local should modify the environment."""
        reader = Reader(lambda env: env["key"]).local(lambda env: {**env, "key": "modified"})
        result = reader.run({"key": "original"})
        assert result == "modified"

    def test_reader_composition(self):
        """Multiple operations should compose."""
        reader = (
            Reader(lambda env: env["a"])
            .map(lambda x: x * 2)
            .flat_map(lambda x: Reader(lambda env: x + env["b"]))
        )
        result = reader.run({"a": 5, "b": 3})
        assert result == 13  # (5 * 2) + 3

    def test_reader_dependency_injection(self):
        """Reader can be used for dependency injection."""
        config = {"db_host": "localhost", "db_port": 5432}

        get_db_host = Reader(lambda env: env["db_host"])
        get_db_port = Reader(lambda env: env["db_port"])

        host = get_db_host.run(config)
        port = get_db_port.run(config)

        assert host == "localhost"
        assert port == 5432
