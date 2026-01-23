"""Tests for core type definitions."""

from better_py.protocols import (
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


class TestTypeVariables:
    """Tests for TypeVar definitions."""

    def test_t_exists(self):
        """T TypeVar should be importable."""
        assert T is not None

    def test_u_exists(self):
        """U TypeVar should be importable."""
        assert U is not None

    def test_v_exists(self):
        """V TypeVar should be importable."""
        assert V is not None

    def test_k_exists(self):
        """K TypeVar (Key) should be importable."""
        assert K is not None

    def test_e_exists(self):
        """E TypeVar (Error) should be importable."""
        assert E is not None

    def test_w_exists(self):
        """W TypeVar (Writer) should be importable."""
        assert W is not None

    def test_s_exists(self):
        """S TypeVar (State) should be importable."""
        assert S is not None

    def test_r_exists(self):
        """R TypeVar (Reader) should be importable."""
        assert R is not None

    def test_t_co_is_covariant(self):
        """T_co should be covariant."""
        assert T_co.__covariant__ is True

    def test_u_co_is_covariant(self):
        """U_co should be covariant."""
        assert U_co.__covariant__ is True

    def test_t_contra_is_contravariant(self):
        """T_contra should be contravariant."""
        assert T_contra.__contravariant__ is True

    def test_t_is_not_covariant_or_contravariant(self):
        """T should be invariant (default)."""
        assert T.__covariant__ is False
        assert T.__contravariant__ is False

    def test_type_variables_are_unique(self):
        """Each TypeVar should be unique."""
        type_vars = [T, U, V, K, E, W, S, R]
        assert len(set(type_vars)) == len(type_vars)

    def test_exports(self):
        """All type variables and protocols should be exported from __init__."""
        from better_py.protocols import __all__

        expected = {
            # Core protocols
            "Mappable",
            "Mappable1",
            "Reducible",
            "Reducible1",
            "Combinable",
            "Monoid",
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
        }
        assert set(__all__) == expected
