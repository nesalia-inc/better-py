"""
better-py: Functional programming patterns for Python

A modern, pragmatic approach to functional programming in Python.

Features:
- Monads (Maybe, Result, Either, Validation, Try, Reader, Writer, State, Unit, AsyncMaybe, AsyncResult, IO, Task)
- Protocols (Mappable, Reducible, Combinable, Updatable, Traversable, Parseable, Validable)
- Collections (PersistentList, PersistentMap, PersistentSet)
- Functions (compose, curry, pipe, flow)
"""

__version__ = "0.2.0"
__author__ = "nesalia-inc"
__license__ = "MIT"

# Re-export protocols
# Re-export collections
from better_py.collections import PersistentList, PersistentMap, PersistentSet

# Re-export functions
from better_py.functions import (
    Pipeline,
    compose,
    compose_left,
    curry,
    flip,
    flow,
    partial_right,
    pipe,
    pipeable,
)

# Re-export monads
from better_py.monads import (
    AsyncMaybe,
    AsyncResult,
    Either,
    Error,
    IO,
    Invalid,
    Left,
    Maybe,
    Nothing,
    Ok,
    Reader,
    Result,
    Right,
    Some,
    State,
    Task,
    Try,
    Unit,
    Valid,
    Validation,
    Writer,
)
from better_py.protocols import (
    Combinable,
    DeepUpdatable,
    Mappable,
    Monoid,
    Parseable,
    Reducible,
    Traversable,
    Updatable,
    Validable,
)

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # Protocols
    "Mappable",
    "Reducible",
    "Combinable",
    "Monoid",
    "Updatable",
    "DeepUpdatable",
    "Traversable",
    "Parseable",
    "Validable",
    # Monads
    "Maybe",
    "Some",
    "Nothing",
    "Result",
    "Ok",
    "Error",
    "Either",
    "Left",
    "Right",
    "Validation",
    "Valid",
    "Invalid",
    "Try",
    "Reader",
    "Writer",
    "State",
    "Unit",
    "AsyncMaybe",
    "AsyncResult",
    "IO",
    "Task",
    # Collections
    "PersistentList",
    "PersistentMap",
    "PersistentSet",
    # Functions
    "compose",
    "compose_left",
    "curry",
    "flip",
    "partial_right",
    "pipe",
    "pipeable",
    "Pipeline",
    "flow",
]
