"""Pipe utilities for data flow programming.

Pipe operations allow you to chain functions in a readable left-to-right manner,
similar to Unix pipes or F#'s pipe operator.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


def pipe(value: T, *functions: Callable[[T], U]) -> U:
    """Pipe a value through a series of functions.

    Applies functions to value in left-to-right order.
    pipe(x, f, g, h) is equivalent to h(g(f(x))).

    Args:
        value: Initial value
        *functions: Functions to apply in sequence

    Returns:
        The result after applying all functions

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> pipe(5, add_one, double)  # double(add_one(5)) = 12
        12

    Note:
        This is the eager version. For lazy evaluation, consider using
        a generator-based approach.
    """
    result = value
    for func in functions:
        result = func(result)
    return result


def pipeable(func: Callable[[T], U]) -> Callable[[T], U]:
    """Convert a function into a pipeable function.

    A pipeable function can be used in pipe operations.

    Args:
        func: Function to make pipeable

    Returns:
        The same function (marked as pipeable)

    Example:
        >>> @pipeable
        ... def add_one(x):
        ...     return x + 1
        >>> pipe(5, add_one)  # 6
        6
    """
    func._is_pipeable = True  # type: ignore
    return func


class Pipeline:
    """A composable pipeline for data transformations.

    Provides a fluent interface for chaining operations.

    Example:
        >>> pipeline = Pipeline()
        >>> result = (pipeline
        ...     .map(lambda x: x * 2)
        ...     .filter(lambda x: x > 5)
        ...     .execute([1, 2, 3, 4]))
        [6, 8]
    """

    def __init__(self, initial_value: T | None = None) -> None:
        """Initialize the pipeline.

        Args:
            initial_value: Optional initial value
        """
        self._value = initial_value
        self._operations: list[Callable] = []

    def map(self, func: Callable[[T], U]) -> Pipeline:
        """Add a map operation to the pipeline.

        Args:
            func: Function to apply to each element

        Returns:
            Self for chaining
        """
        self._operations.append(lambda x: [func(item) for item in x])
        return self

    def filter(self, predicate: Callable[[T], bool]) -> Pipeline:
        """Add a filter operation to the pipeline.

        Args:
            predicate: Function to test each element

        Returns:
            Self for chaining
        """
        self._operations.append(lambda x: [item for item in x if predicate(item)])
        return self

    def reduce(self, func: Callable, initial: U) -> Pipeline:
        """Add a reduce operation to the pipeline.

        Args:
            func: Function to combine values (signature: (acc, value) -> new_acc)
            initial: Initial value

        Returns:
            Self for chaining
        """
        def reduce_op(x):
            if isinstance(x, list):
                result = initial
                for item in x:
                    result = func(result, item)
                return result
            return func(initial, x)

        self._operations.append(reduce_op)
        return self

    def apply(self, func: Callable[[T], U]) -> Pipeline:
        """Add a custom operation to the pipeline.

        Args:
            func: Function to apply

        Returns:
            Self for chaining
        """
        self._operations.append(func)
        return self

    def execute(self, value: T) -> U:
        """Execute the pipeline on a value.

        Args:
            value: Value to process

        Returns:
            The result after all operations
        """
        result = value
        for operation in self._operations:
            result = operation(result)
        return result

    def __or__(self, other: Callable[[T], U]) -> Pipeline:
        """Support pipe syntax with | operator.

        Args:
            other: Function to pipe to

        Returns:
            New pipeline with the operation added
        """
        new_pipeline = Pipeline()
        new_pipeline._operations = self._operations.copy()
        new_pipeline._operations.append(other)
        return new_pipeline


def flow(*functions: Callable) -> Callable:
    """Create a reusable flow from functions.

    Similar to pipe but returns a function that can be called later.

    Args:
        *functions: Functions to compose

    Returns:
        A function that applies all functions when called

    Example:
        >>> add_one = lambda x: x + 1
        >>> double = lambda x: x * 2
        >>> process = flow(add_one, double)
        >>> process(5)  # 12
        12
    """
    def flowed(value: T) -> U:
        return pipe(value, *functions)
    return flowed


__all__ = ["pipe", "pipeable", "Pipeline", "flow"]
