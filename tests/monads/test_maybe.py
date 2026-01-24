"""Tests for Maybe monad."""

import pytest

from better_py.monads import Maybe


class TestMaybeCreation:
    """Tests for creating Maybe instances."""

    def test_some_with_value(self):
        """some() should create a Maybe containing the value."""
        maybe = Maybe.some(42)
        assert maybe.is_some()
        assert not maybe.is_nothing()
        assert maybe.unwrap() == 42

    def test_some_with_none_creates_some_none(self):
        """some(None) creates Some(None) (None is a valid value)."""
        maybe = Maybe.some(None)
        assert maybe.is_some()
        assert not maybe.is_nothing()
        assert maybe.unwrap() is None

    def test_some_none_factory(self):
        """some_none() creates Some(None) explicitly."""
        maybe = Maybe.some_none()
        assert maybe.is_some()
        assert not maybe.is_nothing()
        assert maybe.unwrap() is None

    def test_some_none_vs_nothing(self):
        """some_none() should differ from nothing()."""
        some_none = Maybe.some_none()
        nothing = Maybe.nothing()
        assert some_none.is_some()
        assert nothing.is_nothing()
        assert some_none != nothing

    def test_nothing(self):
        """nothing() should create an empty Maybe."""
        maybe = Maybe.nothing()
        assert maybe.is_nothing()
        assert not maybe.is_some()

    def test_from_value_with_value(self):
        """from_value() should create Some when value is not None."""
        maybe = Maybe.from_value(42)
        assert maybe.is_some()
        assert maybe.unwrap() == 42

    def test_from_value_with_none(self):
        """from_value() should create Nothing when value is None."""
        maybe = Maybe.from_value(None)
        assert maybe.is_nothing()

    def test_from_value_with_zero(self):
        """from_value() should treat 0 as a valid value."""
        maybe = Maybe.from_value(0)
        assert maybe.is_some()
        assert maybe.unwrap() == 0

    def test_from_value_with_false(self):
        """from_value() should treat False as a valid value."""
        maybe = Maybe.from_value(False)
        assert maybe.is_some()
        assert maybe.unwrap() is False

    def test_from_value_with_empty_string(self):
        """from_value() should treat empty string as a valid value."""
        maybe = Maybe.from_value("")
        assert maybe.is_some()
        assert maybe.unwrap() == ""

    def test_from_value_with_empty_list(self):
        """from_value() should treat empty list as a valid value."""
        maybe = Maybe.from_value([])
        assert maybe.is_some()
        assert maybe.unwrap() == []


class TestMaybeInspection:
    """Tests for inspecting Maybe state."""

    def test_is_some_on_some(self):
        """is_some() should return True for Some."""
        assert Maybe.some(42).is_some() is True

    def test_is_some_on_nothing(self):
        """is_some() should return False for Nothing."""
        assert Maybe.nothing().is_some() is False

    def test_is_nothing_on_some(self):
        """is_nothing() should return False for Some."""
        assert Maybe.some(42).is_nothing() is False

    def test_is_nothing_on_nothing(self):
        """is_nothing() should return True for Nothing."""
        assert Maybe.nothing().is_nothing() is True


class TestMaybeUnwrap:
    """Tests for unwrapping Maybe values."""

    def test_unwrap_some(self):
        """unwrap() should return the contained value."""
        assert Maybe.some(42).unwrap() == 42

    def test_unwrap_nothing_raises(self):
        """unwrap() should raise ValueError for Nothing."""
        with pytest.raises(ValueError, match="Cannot unwrap Nothing"):
            Maybe.nothing().unwrap()

    def test_unwrap_or_some(self):
        """unwrap_or() should return the value for Some."""
        assert Maybe.some(42).unwrap_or(0) == 42

    def test_unwrap_or_nothing(self):
        """unwrap_or() should return the default for Nothing."""
        assert Maybe.nothing().unwrap_or(0) == 0

    def test_unwrap_or_else_some(self):
        """unwrap_or_else() should return the value for Some."""
        assert Maybe.some(42).unwrap_or_else(lambda: 0) == 42

    def test_unwrap_or_else_nothing(self):
        """unwrap_or_else() should call the supplier for Nothing."""
        assert Maybe.nothing().unwrap_or_else(lambda: 42) == 42

    def test_unwrap_or_else_not_called_for_some(self):
        """unwrap_or_else() should not call supplier for Some."""
        called = False

        def supplier():
            nonlocal called
            called = True
            return 0

        Maybe.some(42).unwrap_or_else(supplier)
        assert called is False


class TestMaybeMap:
    """Tests for map operation."""

    def test_map_some(self):
        """map() should apply function to Some value."""
        result = Maybe.some(5).map(lambda x: x * 2)
        assert result.is_some()
        assert result.unwrap() == 10

    def test_map_nothing(self):
        """map() should return Nothing for Nothing."""
        result = Maybe.nothing().map(lambda x: x * 2)
        assert result.is_nothing()

    def test_map_type_change(self):
        """map() can change the contained type."""
        result = Maybe.some(42).map(str)
        assert result.is_some()
        assert result.unwrap() == "42"

    def test_map_chain(self):
        """Multiple map operations should chain."""
        result = Maybe.some(5).map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: x / 2)
        assert result.unwrap() == 5.5

    def test_map_preserves_nothing(self):
        """map() should preserve Nothing through chain."""
        result = Maybe.nothing().map(lambda x: x * 2).map(lambda x: x + 1)
        assert result.is_nothing()

    def test_map_identity_law(self):
        """map(id) should equal identity."""
        maybe = Maybe.some(42)
        result = maybe.map(lambda x: x)
        assert result == maybe

    def test_map_with_complex_function(self):
        """map() should work with complex functions."""

        def transform(x: int) -> str:
            return f"Number: {x * 2}"

        result = Maybe.some(21).map(transform)
        assert result.unwrap() == "Number: 42"


class TestMaybeEquality:
    """Tests for Maybe equality."""

    def test_some_equals_some(self):
        """Two Some with same values should be equal."""
        assert Maybe.some(42) == Maybe.some(42)

    def test_some_not_equals_some_different_value(self):
        """Two Some with different values should not be equal."""
        assert Maybe.some(42) != Maybe.some(43)

    def test_nothing_equals_nothing(self):
        """Two Nothing should be equal."""
        assert Maybe.nothing() == Maybe.nothing()

    def test_some_not_equals_nothing(self):
        """Some should not equal Nothing."""
        assert Maybe.some(42) != Maybe.nothing()

    def test_maybe_not_equals_other_type(self):
        """Maybe should not equal other types."""
        assert Maybe.some(42) != 42
        assert Maybe.some(42) != "42"
        assert Maybe.nothing() != None


class TestMaybeRepr:
    """Tests for Maybe string representation."""

    def test_some_repr(self):
        """Some should have correct repr."""
        assert repr(Maybe.some(42)) == "Some(42)"
        assert repr(Maybe.some("hello")) == "Some('hello')"

    def test_nothing_repr(self):
        """Nothing should have correct repr."""
        assert repr(Maybe.nothing()) == "Nothing"


class TestMaybeMappable:
    """Tests for Mappable protocol compliance."""

    def test_maybe_is_mappable(self):
        """Maybe should satisfy Mappable protocol."""
        from better_py.protocols import Mappable

        maybe: Mappable[int] = Maybe.some(42)
        assert isinstance(maybe, Mappable)


class TestMaybeGenericTypes:
    """Tests for Maybe with generic types."""

    def test_maybe_with_int(self):
        """Maybe should work with int."""
        maybe: Maybe[int] = Maybe.some(42)
        assert maybe.unwrap() == 42

    def test_maybe_with_str(self):
        """Maybe should work with str."""
        maybe: Maybe[str] = Maybe.some("hello")
        assert maybe.unwrap() == "hello"

    def test_maybe_with_list(self):
        """Maybe should work with list."""
        maybe: Maybe[list[int]] = Maybe.some([1, 2, 3])
        assert maybe.unwrap() == [1, 2, 3]

    def test_maybe_with_dict(self):
        """Maybe should work with dict."""
        maybe: Maybe[str, int] = Maybe.some({"a": 1})
        assert maybe.unwrap() == {"a": 1}


class TestMaybeApplicative:
    """Tests for Maybe applicative operations."""

    def test_ap_both_some(self):
        """ap should apply function when both are Some."""
        add = Maybe.some(lambda x: x + 1)
        value = Maybe.some(5)
        result = value.ap(add)
        assert result.is_some()
        assert result.unwrap() == 6

    def test_ap_function_nothing(self):
        """ap should return Nothing when function is Nothing."""
        nothing_fn = Maybe.nothing()
        value = Maybe.some(5)
        result = nothing_fn.ap(value)
        assert result.is_nothing()

    def test_ap_value_nothing(self):
        """ap should return Nothing when value is Nothing."""
        add = Maybe.some(lambda x: x + 1)
        nothing_value = Maybe.nothing()
        result = add.ap(nothing_value)
        assert result.is_nothing()

    def test_ap_both_nothing(self):
        """ap should return Nothing when both are Nothing."""
        nothing_fn = Maybe.nothing()
        nothing_value = Maybe.nothing()
        result = nothing_fn.ap(nothing_value)
        assert result.is_nothing()

    def test_lift2_both_some(self):
        """lift2 should apply function when both are Some."""
        result = Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.some(2))
        assert result.is_some()
        assert result.unwrap() == 3

    def test_lift2_first_nothing(self):
        """lift2 should return Nothing when first is Nothing."""
        result = Maybe.lift2(lambda x, y: x + y, Maybe.nothing(), Maybe.some(2))
        assert result.is_nothing()

    def test_lift2_second_nothing(self):
        """lift2 should return Nothing when second is Nothing."""
        result = Maybe.lift2(lambda x, y: x + y, Maybe.some(1), Maybe.nothing())
        assert result.is_nothing()

    def test_lift3_all_some(self):
        """lift3 should apply function when all are Some."""
        result = Maybe.lift3(lambda x, y, z: x + y + z, Maybe.some(1), Maybe.some(2), Maybe.some(3))
        assert result.is_some()
        assert result.unwrap() == 6

    def test_lift3_one_nothing(self):
        """lift3 should return Nothing when any is Nothing."""
        result = Maybe.lift3(lambda x, y, z: x + y + z, Maybe.some(1), Maybe.nothing(), Maybe.some(3))
        assert result.is_nothing()

    def test_zip_all_some(self):
        """zip should combine all Some values into a tuple."""
        result = Maybe.zip(Maybe.some(1), Maybe.some(2), Maybe.some(3))
        assert result.is_some()
        assert result.unwrap() == (1, 2, 3)

    def test_zip_one_nothing(self):
        """zip should return Nothing when any is Nothing."""
        result = Maybe.zip(Maybe.some(1), Maybe.nothing(), Maybe.some(3))
        assert result.is_nothing()

    def test_zip_empty(self):
        """zip should return Some(()) when no arguments."""
        result = Maybe.zip()
        assert result.is_some()
        assert result.unwrap() == ()

    def test_zip_single(self):
        """zip should work with a single value."""
        result = Maybe.zip(Maybe.some(42))
        assert result.is_some()
        assert result.unwrap() == (42,)


class TestMaybeSomeNoneOperations:
    """Tests for operations with Some(None)."""

    def test_some_none_map(self):
        """map should work with Some(None)."""
        result = Maybe.some_none().map(lambda x: x or "default")
        assert result.is_some()
        assert result.unwrap() == "default"

    def test_some_none_flat_map(self):
        """flat_map should work with Some(None)."""
        def handle_none(x):
            if x is None:
                return Maybe.some("was None")
            return Maybe.some(f"was {x}")

        result = Maybe.some_none().flat_map(handle_none)
        assert result.is_some()
        assert result.unwrap() == "was None"

    def test_some_none_unwrap_or(self):
        """unwrap_or should return None (the contained value), not default."""
        result = Maybe.some_none().unwrap_or("default")
        assert result is None

    def test_some_none_or_else(self):
        """or_else should return Some(None), not default."""
        result = Maybe.some_none().or_else(Maybe.some("default"))
        assert result.is_some()
        assert result.unwrap() is None

    def test_some_none_equality(self):
        """Two Some(None) should be equal."""
        assert Maybe.some_none() == Maybe.some_none()
        assert Maybe.some(None) == Maybe.some_none()

    def test_some_none_repr(self):
        """Some(None) should have correct repr."""
        assert repr(Maybe.some_none()) == "Some(None)"

    def test_some_none_in_zip(self):
        """zip should work with Some(None)."""
        result = Maybe.zip(Maybe.some(1), Maybe.some_none(), Maybe.some(3))
        assert result.is_some()
        assert result.unwrap() == (1, None, 3)

    def test_some_none_in_lift2(self):
        """lift2 should work with Some(None)."""
        result = Maybe.lift2(lambda x, y: f"{x}-{y}", Maybe.some(1), Maybe.some_none())
        assert result.is_some()
        assert result.unwrap() == "1-None"
