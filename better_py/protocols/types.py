"""Core type definitions for better-py.

This module provides the fundamental TypeVar definitions used throughout
the library for generic type annotations.
"""

from typing import TypeVar

# Generic type variables
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
K = TypeVar("K")
E = TypeVar("E")  # Error type
W = TypeVar("W")  # Writer / Accumulator type
S = TypeVar("S")  # State type
R = TypeVar("R")  # Reader / Environment type

# Covariant type variables (for containers)
T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)

# Contravariant type variables (for consumers)
T_contra = TypeVar("T_contra", contravariant=True)


__all__ = [
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
