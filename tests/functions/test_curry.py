"""Tests for curry functions."""

import pytest

from better_py.functions import curry, partial_right, flip
from better_py.functions.curry import _


class TestCurry:
    """Tests for curry function."""

    def test_curry_single_argument(self):
        """curried function with all arguments at once."""
        def add(x, y):
            return x + y

        curried = curry(add)
        assert curried(2, 3) == 5

    def test_curry_partial_application(self):
        """curried function should support partial application."""
        def add(x, y, z):
            return x + y + z

        curried = curry(add)
        add_5 = curried(2, 3)
        assert add_5(10) == 15

    def test_curry_one_at_a_time(self):
        """curried function should accept one argument at a time."""
        def add(x, y, z):
            return x + y + z

        curried = curry(add)
        assert curried(2)(3)(10) == 15

    def test_curry_mixed(self):
        """curried function should support mixed application."""
        def add(x, y, z):
            return x + y + z

        curried = curry(add)
        assert curried(2, 3)(10) == 15
        assert curried(2)(3, 10) == 15

    def test_curry_with_kwargs(self):
        """curried function should support keyword arguments."""
        def greet(name, greeting):
            return f"{greeting}, {name}!"

        curried = curry(greet)
        assert curried("World", greeting="Hello") == "Hello, World!"

    def test_curry_preserves_function_name(self):
        """curried function should wrap the original."""
        def my_func(x, y):
            return x + y

        curried = curry(my_func)
        # The curried function should still work like the original
        assert curried(2, 3) == 5
        # And it should be callable
        assert callable(curried)


class TestPartialRight:
    """Tests for partial_right function."""

    def test_partial_right_basic(self):
        """partial_right should apply arguments from right."""
        def subtract(x, y):
            return x - y

        sub_from_10 = partial_right(subtract, 10)
        assert sub_from_10(5) == -5  # 5 - 10

    def test_partial_right_multiple_args(self):
        """partial_right should work with multiple right arguments."""
        def func(a, b, c):
            return (a, b, c)

        partial_func = partial_right(func, 3, 2)
        assert partial_func(1) == (1, 3, 2)

    def test_partial_right_with_kwargs(self):
        """partial_right should support keyword arguments."""
        def greet(name, greeting):
            return f"{greeting}, {name}!"

        greet_hello = partial_right(greet, greeting="Hello")
        assert greet_hello("World") == "Hello, World!"

    def test_partial_right_too_many_args(self):
        """partial_right should raise on too many arguments."""
        def func(a, b):
            return a + b

        partial_func = partial_right(func, 1)
        with pytest.raises(TypeError):
            partial_func(2, 3)  # Too many total arguments


class TestFlip:
    """Tests for flip function."""

    def test_flip_basic(self):
        """flip should reverse first two arguments."""
        def subtract(x, y):
            return x - y

        flipped = flip(subtract)
        assert flipped(5, 10) == 5  # subtract(10, 5)

    def test_flip_with_strings(self):
        """flip should work with any orderable type."""
        def concat(a, b):
            return a + b

        flipped = flip(concat)
        assert flipped("Hello", "World") == "WorldHello"

    def test_flip_preserves_function(self):
        """flipped function should work like original with args swapped."""
        def divide(x, y):
            return x / y

        flipped = flip(divide)
        assert flipped(10, 2) == divide(2, 10) == 0.2


class TestPlaceholder:
    """Tests for placeholder functionality."""

    def test_placeholder_repr(self):
        """placeholder should have correct repr."""
        assert repr(_) == "_"

    def test_placeholder_is_singleton(self):
        """placeholder should be a consistent instance."""
        # The placeholder _ is defined at module level
        _1 = _
        _2 = _
        assert _1 is _2


class TestCurryWithDefaults:
    """Tests for curry with default parameters."""

    def test_curry_with_defaults_uses_defaults_at_call_time(self):
        """curry should not apply defaults early, but use them at final call."""
        def func(a, b, c=10, d=20):
            return a + b + c + d

        curried = curry(func)

        # Should wait for a and b, then apply defaults
        result = curried(1)(2)
        assert result == 33  # 1 + 2 + 10 + 20

    def test_curry_with_defaults_can_override_first_default(self):
        """curry should allow overriding the first default parameter."""
        def func(a, b, c=10, d=20):
            return a + b + c + d

        curried = curry(func)

        # Provide a, b, and override c
        result = curried(1)(2, 5)
        assert result == 28  # 1 + 2 + 5 + 20

    def test_curry_with_defaults_can_override_all_defaults(self):
        """curry should allow overriding all default parameters."""
        def func(a, b, c=10, d=20):
            return a + b + c + d

        curried = curry(func)

        # Provide a, b, and override both c and d
        result = curried(1)(2, 5, 3)
        assert result == 11  # 1 + 2 + 5 + 3

    def test_curry_with_defaults_mixed_application(self):
        """curry with defaults should support mixed application styles."""
        def func(a, b, c=10, d=20):
            return a + b + c + d

        curried = curry(func)

        # Can provide multiple args at once
        result1 = curried(1, 2)  # Uses defaults
        assert result1 == 33

        result2 = curried(1, 2, 5)  # Override c
        assert result2 == 28

        result3 = curried(1, 2, 5, 3)  # Override c and d
        assert result3 == 11

    def test_curry_with_all_defaults(self):
        """curry should work with functions that have all default parameters."""
        def func(a=1, b=2, c=3):
            return a + b + c

        curried = curry(func)

        # Should be callable with no args (all defaults)
        result = curried()
        assert result == 6  # 1 + 2 + 3

        # Should allow overriding defaults
        result2 = curried(10)
        assert result2 == 15  # 10 + 2 + 3
