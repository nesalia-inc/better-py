"""Tests for IO monad."""

import pytest

from better_py.monads import IO


class TestIO:
    """Tests for IO monad."""

    def test_unsafe_run(self):
        """unsafe_run should execute the computation."""
        io = IO(lambda: 42)
        assert io.unsafe_run() == 42

    def test_unsafe_run_with_side_effect(self):
        """unsafe_run should execute side effects."""
        state = []

        def effect():
            state.append("executed")
            return "result"

        io = IO(effect)
        result = io.unsafe_run()
        assert result == "result"
        assert state == ["executed"]

    def test_map(self):
        """map should transform the result."""
        io = IO(lambda: 5).map(lambda x: x * 2)
        assert io.unsafe_run() == 10

    def test_flat_map(self):
        """flat_map should chain computations."""
        io = IO(lambda: 5).flat_map(lambda x: IO(lambda: x * 2))
        assert io.unsafe_run() == 10

    def test_flat_map_preserves_order(self):
        """flat_map should execute in order."""
        order = []

        io = IO(lambda: (order.append(1), 5)[1]).flat_map(
            lambda x: IO(lambda: (order.append(2), x * 2)[1])
        )
        result = io.unsafe_run()
        assert result == 10
        assert order == [1, 2]

    def test_and_then(self):
        """and_then should sequence computations."""
        order = []

        io1 = IO(lambda: order.append(1))
        io2 = IO(lambda: order.append(2))
        io1.and_then(io2).unsafe_run()
        assert order == [1, 2]

    def test_and_then_returns_second_result(self):
        """and_then should return second result."""
        io1 = IO(lambda: 5)
        io2 = IO(lambda: 10)
        result = io1.and_then(io2).unsafe_run()
        assert result == 10

    def test_filter_passes(self):
        """filter should keep value if predicate passes."""
        io = IO(lambda: 5).filter(lambda x: x > 3)
        assert io.unsafe_run() == 5

    def test_filter_fails(self):
        """filter should return None if predicate fails."""
        io = IO(lambda: 2).filter(lambda x: x > 3)
        assert io.unsafe_run() is None

    def test_recover_success(self):
        """recover should not affect successful computation."""
        io = IO(lambda: 42).recover(lambda _: 0)
        assert io.unsafe_run() == 42

    def test_recover_failure(self):
        """recover should handle exceptions."""
        io = IO(lambda: 1 / 0).recover(lambda _: 0)
        assert io.unsafe_run() == 0

    def test_recover_with_exception(self):
        """recover should pass exception to handler."""
        def handler(e):
            assert isinstance(e, ZeroDivisionError)
            return 0

        io = IO(lambda: 1 / 0).recover(handler)
        assert io.unsafe_run() == 0

    def test_retry_success_on_first_try(self):
        """retry should succeed immediately."""
        io = IO(lambda: 42).retry(3)
        assert io.unsafe_run() == 42

    def test_retry_success_after_failure(self):
        """retry should eventually succeed."""
        attempts = [0]

        def failing():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("not yet")
            return 42

        io = IO(failing).retry(5)
        assert io.unsafe_run() == 42
        assert attempts[0] == 3

    def test_retry_exhausted(self):
        """retry should raise after exhausting attempts."""
        io = IO(lambda: 1 / 0).retry(2)
        with pytest.raises(ZeroDivisionError):
            io.unsafe_run()

    def test_pure(self):
        """pure should lift a value."""
        io = IO.pure(42)
        assert io.unsafe_run() == 42

    def test_delay_with_function(self):
        """delay should delay function evaluation."""
        calls = [0]

        def computation():
            calls[0] += 1
            return 42

        io = IO.delay(computation)
        assert calls[0] == 0
        assert io.unsafe_run() == 42
        assert calls[0] == 1

    def test_delay_with_value(self):
        """delay should wrap a value."""
        io = IO.delay(42)
        assert io.unsafe_run() == 42

    def test_equality_same_function(self):
        """IO instances with same function should be equal."""
        func = lambda: 42
        io1 = IO(func)
        io2 = IO(func)
        assert io1 == io2

    def test_equality_different_functions(self):
        """IO instances with different functions should not be equal."""
        io1 = IO(lambda: 42)
        io2 = IO(lambda: 42)
        assert io1 != io2  # Different lambda functions

    def test_equality_different_results(self):
        """IO instances with different result functions should not be equal."""
        io1 = IO(lambda: 42)
        io2 = IO(lambda: 43)
        assert io1 != io2

    def test_equality_different_types(self):
        """IO should not be equal to non-IO."""
        io = IO(lambda: 42)
        assert io != 42

    def test_repr(self):
        """repr should show IO."""
        io = IO(lambda: 42)
        assert repr(io) == "IO(...)"


class TestIORegressionTests:
    """Regression tests to ensure fixed bugs don't resurface."""

    def test_equality_no_side_effects(self):
        """IO equality should not execute the computation.

        Regression test for issue #003: IO/Task equality side effects.
        """
        count = [0]

        def side_effect(x):
            count.append(1)
            return x

        io1 = IO(side_effect)
        io2 = IO(side_effect)

        result = io1 == io2

        # Side effects should not occur during equality check
        assert count[0] == 0, "Equality check executed side effects"
        assert result is True

    def test_equality_comparison_does_not_mutate(self):
        """IO equality should not mutate state."""
        state = {"value": 0}

        def mutate():
            state["value"] += 1
            return state["value"]

        io1 = IO(mutate)
        io2 = IO(mutate)

        # Compare multiple times
        _ = io1 == io2
        _ = io1 == io2
        _ = io1 == io2

        # State should be unchanged
        assert state["value"] == 0, "Equality check mutated state"
