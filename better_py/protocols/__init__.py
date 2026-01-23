"""Functional protocols for better-py.

This package contains Protocol-based definitions for functional programming
patterns, following the approach of collections.abc.
"""

from better_py.protocols.combinable import Combinable, Monoid
from better_py.protocols.mappable import Mappable, Mappable1
from better_py.protocols.parseable import Parseable
from better_py.protocols.reducible import Reducible, Reducible1
from better_py.protocols.traversable import Traversable
from better_py.protocols.types import (
    E,
    K,
    R,
    S,
    T,
    T_co,
    T_contra,
    U,
    U_co,
    V,
    W,
)
from better_py.protocols.updatable import DeepUpdatable, Updatable
from better_py.protocols.validable import Validable

__all__ = [
    # Core protocols
    "Mappable",
    "Mappable1",
    "Reducible",
    "Reducible1",
    "Combinable",
    "Monoid",
    "Updatable",
    "DeepUpdatable",
    "Traversable",
    "Parseable",
    "Validable",
    # Type variables
    "T",
    "U",
    "V",
    "K",
    "E",
    "W",
    "S",
    "R",
    "T_co",
    "U_co",
    "T_contra",
]
