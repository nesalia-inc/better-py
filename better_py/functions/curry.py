"""Currying and partial application utilities.

Currying is the process of converting a function that takes multiple arguments
into a sequence of functions that each take a single argument.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def curry(func: Callable[..., T]) -> Callable[..., T]:
    """Convert a function into a curried function.

    A curried function can be called with some arguments and will return
    a function waiting for the remaining arguments.

    Default parameters are NOT filled in automatically. The function executes
    when all required arguments (those without defaults) are provided. Optional
    parameters with defaults can be provided to override defaults.

    Args:
        func: Function to curry

    Returns:
        A curried version of the function

    Example:
        >>> def add(x, y, z):
        ...     return x + y + z
        >>> curried_add = curry(add)
        >>> curried_add(1)(2)(3)  # 6
        6
        >>> curried_add(1, 2)(3)  # 6
        6

    With defaults (defaults not applied until final call):
        >>> def func(a, b, c=10, d=20):
        ...     return a + b + c + d
        >>> curried = curry(func)
        >>> curried(1)(2)  # Uses defaults: 1 + 2 + 10 + 20 = 33
        33
        >>> curried(1)(2, 5)  # Override c: 1 + 2 + 5 + 20 = 28
        28
        >>> curried(1)(2, 5, 3)  # Override c and d: 1 + 2 + 5 + 3 = 11
        11
    """
    sig = signature(func)

    # Count required parameters (those without defaults)
    # Exclude VAR_POSITIONAL (*args) and VAR_KEYWORD (**kwargs)
    required_params = sum(
        1
        for p in sig.parameters.values()
        if p.default is p.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    )

    def curried(*args: Any, **kwargs: Any) -> Any:
        # Bind provided arguments (without applying defaults)
        bound = sig.bind_partial(*args, **kwargs)

        # Apply defaults only when we're ready to call the function
        # This ensures defaults are used at call time, not during currying
        if len(bound.arguments) >= required_params:
            bound.apply_defaults()
            return func(*bound.args, **bound.kwargs)

        # Otherwise return a function waiting for more arguments
        @wraps(func)
        def waiting(*more_args: Any, **more_kwargs: Any) -> Any:
            new_args = args + more_args
            new_kwargs = {**kwargs, **more_kwargs}
            return curried(*new_args, **new_kwargs)

        return waiting

    return curried


def partial_right(func: Callable[..., T], *args: Any, **kwargs: Any) -> Callable[..., T]:
    """Partially apply arguments from the right.

    Unlike functools.partial which applies from the left, this applies
    arguments from the right side.

    Args:
        func: Function to partially apply
        *args: Arguments to apply from the right
        **kwargs: Keyword arguments to apply

    Returns:
        A partially applied function

    Example:
        >>> def subtract(x, y):
        ...     return x - y
        >>> subtract_from_10 = partial_right(subtract, 10)
        >>> subtract_from_10(5)  # 5 - 10 = -5
        -5
    """
    sig = signature(func)

    def wrapped(*left_args: Any, **left_kwargs: Any) -> T:
        # Combine left args with right args
        total_args_needed = len(sig.parameters)
        right_args_count = len(args)
        left_args_count = len(left_args)

        if left_args_count + right_args_count > total_args_needed:
            raise TypeError(f"Too many arguments for {func.__name__}")

        # Apply right args first, then left args
        all_args = left_args + args
        all_kwargs = {**kwargs, **left_kwargs}

        return func(*all_args, **all_kwargs)

    return wrapped


def flip(func: Callable[[T, U], V]) -> Callable[[U, T], V]:
    """Flip the order of the first two arguments.

    Args:
        func: Function to flip

    Returns:
        Function with first two arguments flipped

    Example:
        >>> def subtract(x, y):
        ...     return x - y
        >>> flipped_subtract = flip(subtract)
        >>> flipped_subtract(5, 10)  # subtract(10, 5) = 5
        5
    """
    def flipped(y: U, x: T) -> V:
        return func(x, y)

    return flipped


class _Placeholder:
    """Placeholder for curried function arguments.

    Used to specify which arguments should be filled in partial application.

    Example:
        >>> from better_py.functions import _ as placeholder
        >>> def func(a, b, c):
        ...     return (a, b, c)
        >>> # Fill second argument now, leave first and third for later
    """

    def __repr__(self) -> str:
        return "_"


_ = _Placeholder()


__all__ = ["curry", "partial_right", "flip", "_"]
