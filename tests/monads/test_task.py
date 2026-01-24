"""Tests for Task monad."""


from better_py.monads import Task


class TestTask:
    """Tests for Task monad."""

    def test_run(self):
        """run should execute the computation."""
        task = Task(lambda: 42)
        assert task.run() == 42

    def test_run_caches_result(self):
        """run should cache the result."""
        calls = [0]

        def computation():
            calls[0] += 1
            return 42

        task = Task(computation)
        assert task.run() == 42
        assert calls[0] == 1
        assert task.run() == 42
        assert calls[0] == 1  # Not called again

    def test_peek_uncached(self):
        """peek should return None if not cached."""
        task = Task(lambda: 42)
        assert task.peek() is None

    def test_peek_cached(self):
        """peek should return cached value."""
        task = Task(lambda: 42)
        task.run()
        assert task.peek() == 42

    def test_is_cached_false(self):
        """is_cached should return False if not cached."""
        task = Task(lambda: 42)
        assert not task.is_cached()

    def test_is_cached_true(self):
        """is_cached should return True if cached."""
        task = Task(lambda: 42)
        task.run()
        assert task.is_cached()

    def test_map(self):
        """map should transform the result."""
        task = Task(lambda: 5).map(lambda x: x * 2)
        assert task.run() == 10

    def test_map_cached(self):
        """map should use cached result."""
        calls = [0]

        def computation():
            calls[0] += 1
            return 5

        task = Task(computation)
        mapped = task.map(lambda x: x * 2)
        assert mapped.run() == 10
        assert calls[0] == 1
        assert mapped.run() == 10
        assert calls[0] == 1

    def test_flat_map(self):
        """flat_map should chain computations."""
        task = Task(lambda: 5).flat_map(lambda x: Task(lambda: x * 2))
        assert task.run() == 10

    def test_flat_map_caches_both(self):
        """flat_map should cache both tasks."""
        calls1 = [0]
        calls2 = [0]

        def computation1():
            calls1[0] += 1
            return 5

        def computation2():
            calls2[0] += 1
            return 10

        task = Task(computation1).flat_map(lambda _: Task(computation2))
        assert task.run() == 10
        assert calls1[0] == 1
        assert calls2[0] == 1
        assert task.run() == 10
        assert calls1[0] == 1
        assert calls2[0] == 1

    def test_and_then(self):
        """and_then should sequence computations."""
        order = []

        task1 = Task(lambda: (order.append(1), 5)[1])
        task2 = Task(lambda: (order.append(2), 10)[1])
        result = task1.and_then(task2).run()
        assert result == 10
        assert order == [1, 2]

    def test_filter_passes(self):
        """filter should keep value if predicate passes."""
        task = Task(lambda: 5).filter(lambda x: x > 3)
        assert task.run() == 5

    def test_filter_fails(self):
        """filter should return None if predicate fails."""
        task = Task(lambda: 2).filter(lambda x: x > 3)
        assert task.run() is None

    def test_zip(self):
        """zip should combine two tasks."""
        task1 = Task(lambda: 5)
        task2 = Task(lambda: "hello")
        result = task1.zip(task2).run()
        assert result == (5, "hello")

    def test_zip_caches_both(self):
        """zip should cache both results."""
        calls1 = [0]
        calls2 = [0]

        def computation1():
            calls1[0] += 1
            return 5

        def computation2():
            calls2[0] += 1
            return "hello"

        task1 = Task(computation1)
        task2 = Task(computation2)
        zipped = task1.zip(task2)
        assert zipped.run() == (5, "hello")
        assert calls1[0] == 1
        assert calls2[0] == 1
        assert zipped.run() == (5, "hello")
        assert calls1[0] == 1
        assert calls2[0] == 1

    def test_memoize(self):
        """memoize should cache results."""
        calls = [0]

        def computation():
            calls[0] += 1
            return 42

        task = Task(computation).memoize()
        assert task.run() == 42
        assert calls[0] == 1
        assert task.run() == 42
        assert calls[0] == 1

    def test_memoize_with_max_size(self):
        """memoize should respect max_size."""
        task = Task(lambda: 42).memoize(max_size=1)
        assert task.run() == 42
        assert task.is_cached()

    def test_pure(self):
        """pure should lift a value."""
        task = Task.pure(42)
        assert task.run() == 42

    def test_delay_with_function(self):
        """delay should delay function evaluation."""
        calls = [0]

        def computation():
            calls[0] += 1
            return 42

        task = Task.delay(computation)
        assert calls[0] == 0
        assert task.run() == 42
        assert calls[0] == 1

    def test_delay_with_value(self):
        """delay should wrap a value."""
        task = Task.delay(42)
        assert task.run() == 42

    def test_from_io(self):
        """from_io should convert IO to Task."""
        from better_py.monads import IO

        io = IO(lambda: 42)
        task = Task.from_io(io)
        assert task.run() == 42

    def test_equality_same_result(self):
        """Task instances are compared by identity, not result."""
        task1 = Task(lambda: 42)
        task2 = Task(lambda: 42)
        # Different instances are not equal, even if they produce the same result
        assert task1 != task2
        # Same instance is equal to itself
        assert task1 == task1

    def test_equality_different_results(self):
        """Task instances with different results should not be equal."""
        task1 = Task(lambda: 42)
        task2 = Task(lambda: 43)
        assert task1 != task2

    def test_equality_different_types(self):
        """Task should not be equal to non-Task."""
        task = Task(lambda: 42)
        assert task != 42

    def test_repr_uncached(self):
        """repr should show uncached status."""
        task = Task(lambda: 42)
        assert repr(task) == "Task(cached=False)"

    def test_repr_cached(self):
        """repr should show cached status."""
        task = Task(lambda: 42)
        task.run()
        assert repr(task) == "Task(cached=True)"

    def test_equality_no_side_effects(self):
        """Task equality should not execute the computation."""
        count = [0]

        def computation():
            count[0] += 1
            return 42

        task1 = Task(computation)
        task2 = Task(computation)

        result = task1 == task2

        # Side effects should not occur during equality check
        assert count[0] == 0, f"Equality check executed side effects: {count[0]} executions"
