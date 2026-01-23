"""Function composition utilities.

Function composition is the process of combining two or more functions
to create a new function. The composition of functions f and g is a function
that takes x and returns f(g(x)).
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


def compose(*functions: Callable[[T], U]) -> Callable[[T], U]:
    """Compose functions from right to left.

    Composes functions so that compose(f, g, h)(x) is equivalent to f(g(h(x))).

    Args:
        *functions: Functions to compose, applied right to left

    Returns:
        A composed function

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> compose(double, add_one)(5)  # double(add_one(5)) = 12
        12

    Note:
        Functions are applied right to left (mathematical convention).
        For left-to-right composition, use compose_left or pipe.
    """
    if not functions:
        raise ValueError("At least one function must be provided")

    if len(functions) == 1:
        return functions[0]

    def composed(x: T) -> U:
        result = x
        for func in reversed(functions):
            result = func(result)
        return result

    return composed


def compose_left(*functions: Callable[[T], U]) -> Callable[[T], U]:
    """Compose functions from left to right.

    Composes functions so that compose_left(f, g, h)(x) is equivalent to h(g(f(x))).

    Args:
        *functions: Functions to compose, applied left to right

    Returns:
        A composed function

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> compose_left(add_one, double)(5)  # double(add_one(5)) = 12
        12

    Note:
        Functions are applied left to right (pipeline convention).
        This is equivalent to pipe but returns a function.
    """
    if not functions:
        raise ValueError("At least one function must be provided")

    if len(functions) == 1:
        return functions[0]

    def composed(x: T) -> U:
        result = x
        for func in functions:
            result = func(result)
        return result

    return composed


def decorator(func: Callable[[T], U]) -> Callable[[Callable[..., T]], Callable[..., U]]:
    """Create a decorator from a function.

    Converts a function that takes a value and returns a transformed value
    into a decorator that transforms the return value of a function.

    Args:
        func: Function to transform return values

    Returns:
        A decorator function

    Example:
        >>> def double(x):
        ...     return x * 2
        >>> @decorator(double)
        ... def my_func():
        ...     return 5
        >>> my_func()  # 10
        10
    """
    def wrapper(f: Callable[..., T]) -> Callable[..., U]:
        @wraps(f)
        def wrapped(*args, **kwargs):
            return func(f(*args, **kwargs))
        return wrapped
    return wrapper


__all__ = ["compose", "compose_left", "decorator"]
