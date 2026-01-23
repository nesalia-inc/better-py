"""Tests for compose functions."""

import pytest

from better_py.functions import compose, compose_left


class TestCompose:
    """Tests for compose function."""

    def test_compose_single_function(self):
        """compose with single function should return that function."""
        f = lambda x: x * 2
        composed = compose(f)
        assert composed(5) == 10

    def test_compose_two_functions(self):
        """compose should apply functions right to left."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        composed = compose(double, add_one)
        assert composed(5) == 12  # double(add_one(5))

    def test_compose_three_functions(self):
        """compose should apply multiple functions right to left."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        subtract_five = lambda x: x - 5
        composed = compose(subtract_five, double, add_one)
        assert composed(5) == 7  # subtract_five(double(add_one(5)))

    def test_compose_empty_raises(self):
        """compose with no functions should raise ValueError."""
        with pytest.raises(ValueError):
            compose()

    def test_compose_preserves_arguments(self):
        """compose should work with functions that return tuples."""
        def make_pair(x):
            return (x, x * 2)

        def add_pair(pair):
            a, b = pair
            return a + b

        composed = compose(add_pair, make_pair)
        assert composed(5) == 15  # add_pair(make_pair(5)) = add_pair((5, 10))


class TestComposeLeft:
    """Tests for compose_left function."""

    def test_compose_left_single_function(self):
        """compose_left with single function should return that function."""
        f = lambda x: x * 2
        composed = compose_left(f)
        assert composed(5) == 10

    def test_compose_left_two_functions(self):
        """compose_left should apply functions left to right."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        composed = compose_left(add_one, double)
        assert composed(5) == 12  # double(add_one(5))

    def test_compose_left_three_functions(self):
        """compose_left should apply multiple functions left to right."""
        add_one = lambda x: x + 1
        double = lambda x: x * 2
        subtract_five = lambda x: x - 5
        composed = compose_left(add_one, double, subtract_five)
        assert composed(5) == 7  # subtract_five(double(add_one(5)))

    def test_compose_left_empty_raises(self):
        """compose_left with no functions should raise ValueError."""
        with pytest.raises(ValueError):
            compose_left()

    def test_compose_left_vs_compose(self):
        """compose_left should be opposite order of compose."""
        f = lambda x: x * 2
        g = lambda x: x + 1

        assert compose(f, g)(5) == compose_left(g, f)(5)


class TestDecorator:
    """Tests for decorator function."""

    def test_decorator_transforms_return_value(self):
        """decorator should transform function return value."""
        from better_py.functions.compose import decorator

        double = lambda x: x * 2

        @decorator(double)
        def get_value():
            return 5

        assert get_value() == 10

    def test_decorator_preserves_function_name(self):
        """decorator should preserve original function name."""
        from better_py.functions.compose import decorator
        import functools

        transform = lambda x: x

        @decorator(transform)
        def my_function():
            return 5

        assert my_function.__name__ == "my_function"

    def test_decorator_with_arguments(self):
        """decorator should work with function arguments."""
        from better_py.functions.compose import decorator

        add_one = lambda x: x + 1

        @decorator(add_one)
        def add(a, b):
            return a + b

        assert add(2, 3) == 6
