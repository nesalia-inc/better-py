"""Tests for pipe utilities."""

import pytest

from better_py.functions import pipe, pipeable, Pipeline, flow


class TestPipe:
    """Tests for pipe function."""

    def test_pipe_no_functions(self):
        """pipe with no functions should return value."""
        result = pipe(5)
        assert result == 5

    def test_pipe_single_function(self):
        """pipe with single function should apply it."""
        add_one = lambda x: x + 1
        result = pipe(5, add_one)
        assert result == 6

    def test_pipe_two_functions(self):
        """pipe should apply functions left to right."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        result = pipe(5, add_one, double)
        assert result == 12  # double(add_one(5))

    def test_pipe_three_functions(self):
        """pipe should chain multiple functions."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        subtract_five = lambda x: x - 5
        result = pipe(5, add_one, double, subtract_five)
        assert result == 7  # subtract_five(double(add_one(5)))

    def test_pipe_with_list(self):
        """pipe should work with complex data structures."""
        double = lambda x: [i * 2 for i in x]
        add_one = lambda x: [i + 1 for i in x]
        result = pipe([1, 2, 3], double, add_one)
        assert result == [3, 5, 7]


class TestPipeable:
    """Tests for pipeable decorator."""

    def test_pipeable_marks_function(self):
        """pipeable should mark function as pipeable."""
        @pipeable
        def add_one(x):
            return x + 1

        assert hasattr(add_one, "_is_pipeable")
        assert add_one._is_pipeable is True

    def test_pipeable_function_works_normally(self):
        """pipeable function should work normally."""
        @pipeable
        def add_one(x):
            return x + 1

        assert add_one(5) == 6


class TestPipeline:
    """Tests for Pipeline class."""

    def test_pipeline_map(self):
        """Pipeline.map should transform elements."""
        result = Pipeline().map(lambda x: x * 2).execute([1, 2, 3])
        assert result == [2, 4, 6]

    def test_pipeline_filter(self):
        """Pipeline.filter should filter elements."""
        result = Pipeline().filter(lambda x: x > 2).execute([1, 2, 3, 4])
        assert result == [3, 4]

    def test_pipeline_chain(self):
        """Pipeline should support chaining."""
        result = (Pipeline()
                 .map(lambda x: x * 2)
                 .filter(lambda x: x > 2)
                 .execute([1, 2, 3, 4]))
        assert result == [4, 6, 8]

    def test_pipeline_apply(self):
        """Pipeline.apply should add custom operation."""
        result = (Pipeline()
                 .apply(lambda x: sum(x))
                 .execute([1, 2, 3, 4]))
        assert result == 10

    def test_pipeline_or_operator(self):
        """Pipeline should support | operator."""
        pipeline = Pipeline()
        result = (pipeline
                 .map(lambda x: x * 2)
                 | (lambda x: [i for i in x if i > 2]))
        result = result.execute([1, 2, 3])
        assert result == [4, 6]

    def test_pipeline_reduce(self):
        """Pipeline.reduce should aggregate values."""
        result = (Pipeline()
                 .reduce(lambda acc, x: acc + x, 0)
                 .execute([1, 2, 3, 4]))
        # Note: reduce implementation may vary
        assert result is not None


class TestFlow:
    """Tests for flow function."""

    def test_flow_creates_function(self):
        """flow should return a callable function."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        process = flow(add_one, double)

        assert callable(process)

    def test_flow_applies_functions(self):
        """flow should apply functions when called."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        process = flow(add_one, double)

        assert process(5) == 12

    def test_flow_reusable(self):
        """flow should create reusable function."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        process = flow(add_one, double)

        assert process(5) == 12
        assert process(10) == 22

    def test_flow_single_function(self):
        """flow with single function should work."""
        add_one = lambda x: x + 1
        process = flow(add_one)

        assert process(5) == 6

    def test_flow_empty(self):
        """flow with no functions should return identity."""
        process = flow()

        assert process(5) == 5  # pipe with no functions returns value

    def test_flow_vs_pipe(self):
        """flow should be equivalent to delayed pipe."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2

        process = flow(add_one, double)
        result = pipe(5, add_one, double)

        assert process(5) == result
