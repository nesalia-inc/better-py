"""Tests for State monad."""

from better_py.monads import State


class TestState:
    """Tests for State monad."""

    def test_state_run(self):
        """run should execute the state computation."""
        state = State(lambda s: (s * 2, s + 1))
        value, new_state = state.run(5)
        assert value == 10
        assert new_state == 6

    def test_state_eval(self):
        """eval should return only the result value."""
        state = State(lambda s: (s * 2, s + 1))
        value = state.eval(5)
        assert value == 10

    def test_state_execute(self):
        """execute should return only the final state."""
        state = State(lambda s: (s * 2, s + 1))
        new_state = state.execute(5)
        assert new_state == 6

    def test_state_get(self):
        """get should return the current state."""
        state = State.get()
        value, new_state = state.run(42)
        assert value == 42
        assert new_state == 42

    def test_state_put(self):
        """put should replace the state."""
        state = State.put(100)
        value, new_state = state.run(0)
        assert value is None
        assert new_state == 100

    def test_state_modify(self):
        """modify should transform the state."""
        state = State.modify(lambda x: x * 2)
        value, new_state = state.run(5)
        assert value is None
        assert new_state == 10

    def test_state_map(self):
        """map should transform the result value."""
        state = State(lambda s: (s, s)).map(lambda x: x * 2)
        value, new_state = state.run(5)
        assert value == 10
        assert new_state == 5

    def test_state_flat_map(self):
        """flat_map should chain state computations."""
        def add_state(x):
            return State(lambda s: (x + s, s + 1))

        state = State(lambda s: (s, s)).flat_map(add_state)
        value, new_state = state.run(5)
        assert value == 10  # 5 + 5
        assert new_state == 6

    def test_state_counter(self):
        """State can be used to implement a counter."""
        def increment():
            return State.modify(lambda x: x + 1).flat_map(lambda _: State.get())

        # Increment 3 times and get final value
        counter = increment().flat_map(lambda _: increment()).flat_map(lambda _: increment())
        value, final_state = counter.run(0)
        assert final_state == 3
        assert value == 3


class TestStateRegressionTests:
    """Regression tests to ensure fixed bugs don't resurface."""

    def test_map_executes_once(self):
        """map should execute state transformation exactly once.

        Regression test for issue #002: State monad double execution bug.
        """
        count = [0]

        def counting_state(s):
            count[0] += 1
            return (s, s)

        state = State(counting_state)
        mapped = state.map(lambda x: x)
        result = mapped.run(0)

        assert count[0] == 1, f"Expected 1 execution, got {count[0]}"
        assert result == (0, 0)

    def test_flat_map_executes_once_per_step(self):
        """flat_map should execute each state transformation exactly once.

        Regression test for issue #002: State monad double execution bug.
        """
        count = [0]

        def counting_transform(x):
            count[0] += 1
            return State(lambda s: (x + s, s))

        state = State(lambda s: (10, s))
        result = state.flat_map(counting_transform).run(5)

        # Initial state (1) + flat_map (1) = 2 total executions
        assert count[0] == 1, f"Expected 1 execution in flat_map, got {count[0]}"
        assert result == (15, 5)
