"""Tests for Writer monad."""

from better_py.monads import Writer, list_writer, str_writer, sum_writer
from better_py.protocols import Monoid


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


class TestWriterMonoidProtocol:
    """Tests for Writer with custom Monoid protocol."""

    def test_custom_monoid_with_combine(self):
        """Writer should use Monoid.combine() when available."""
        class ProductLog(Monoid):
            """A monoid that combines using multiplication."""

            def __init__(self, value: int):
                self.value = value

            def combine(self, other: "ProductLog") -> "ProductLog":
                return ProductLog(self.value * other.value)

            @staticmethod
            def identity() -> "ProductLog":
                return ProductLog(1)

            def __eq__(self, other):
                return isinstance(other, ProductLog) and self.value == other.value

            def __repr__(self):
                return f"ProductLog({self.value})"

        # Create Writer with custom monoid log
        w1 = Writer(ProductLog(3), "a")
        w2 = Writer(ProductLog(4), "b")

        # flat_map should use ProductLog.combine (multiplication)
        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log.value == 12  # 3 * 4, not 3 + 4
        assert value == "b"

    def test_backward_compatibility_with_plus_operator(self):
        """Writer should fall back to + operator for types without Monoid."""
        # list uses + operator and doesn't implement Monoid protocol
        w1 = Writer([1, 2], "a")
        w2 = Writer([3, 4], "b")

        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log == [1, 2, 3, 4]  # Uses + for concatenation
        assert value == "b"


class TestWriterFactoryFunctions:
    """Tests for Writer convenience factory functions."""

    def test_list_writer(self):
        """list_writer should create Writer with list log."""
        w1 = list_writer([1, 2], "first")
        w2 = list_writer([3, 4], "second")

        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log == [1, 2, 3, 4]
        assert value == "second"

    def test_str_writer(self):
        """str_writer should create Writer with string log."""
        w1 = str_writer("hello ", "first")
        w2 = str_writer("world", "second")

        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log == "hello world"
        assert value == "second"

    def test_sum_writer_int(self):
        """sum_writer should create Writer with int log."""
        w1 = sum_writer(5, "first")
        w2 = sum_writer(3, "second")

        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log == 8  # 5 + 3
        assert value == "second"

    def test_sum_writer_float(self):
        """sum_writer should create Writer with float log."""
        w1 = sum_writer(2.5, "first")
        w2 = sum_writer(1.5, "second")

        result = w1.flat_map(lambda _: w2)
        log, value = result.tell()
        assert log == 4.0  # 2.5 + 1.5
        assert value == "second"
