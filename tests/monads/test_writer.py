"""Tests for Writer monad."""

from better_py.monads import Writer


class TestWriter:
    """Tests for Writer monad."""

    def test_writer_tell(self):
        """tell should extract log and value."""
        writer = Writer(["log1", "log2"], 42)
        log, value = writer.tell()
        assert log == ["log1", "log2"]
        assert value == 42

    def test_writer_map(self):
        """map should transform the value."""
        writer = Writer(["log"], 5).map(lambda x: x * 2)
        log, value = writer.tell()
        assert log == ["log"]
        assert value == 10

    def test_writer_flat_map(self):
        """flat_map should chain computations and accumulate logs."""
        def add_log(x):
            return Writer([f"processed {x}"], x + 1)

        writer = Writer(["start"], 5).flat_map(add_log)
        log, value = writer.tell()
        assert log == ["start", "processed 5"]
        assert value == 6

    def test_writer_listen(self):
        """listen should extract log and value as a pair."""
        writer = Writer(["log"], 42).listen()
        log, value = writer.tell()
        assert value == (["log"], 42)

    def test_writer_pass(self):
        """pass_ should use log as both log and value."""
        writer = Writer(["log"], 42).pass_()
        log, value = writer.tell()
        assert log == ["log"]
        assert value == ["log"]

    def test_writer_tell_log(self):
        """tell_log should create a Writer with only a log."""
        writer = Writer.tell_log(["entry"])
        log, value = writer.tell()
        assert log == ["entry"]
        assert value is None

    def test_writer_accumulation(self):
        """Logs should accumulate through flat_map."""
        def step1(x):
            return Writer(["step1"], x + 1)

        def step2(x):
            return Writer(["step2"], x * 2)

        result = Writer(["init"], 5).flat_map(step1).flat_map(step2)
        log, value = result.tell()
        assert log == ["init", "step1", "step2"]
        assert value == 12  # ((5 + 1) * 2)
