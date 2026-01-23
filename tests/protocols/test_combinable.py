"""Tests for Combinable protocol."""

import pytest

from better_py.protocols import T
from better_py.protocols.combinable import Combinable, Monoid


class AddableNumber:
    """Simple number class implementing Combinable."""

    def __init__(self, value):
        self.value = value

    def combine(self, other):
        """Combine by adding values."""
        return AddableNumber(self.value + other.value)

    def __eq__(self, other):
        return isinstance(other, AddableNumber) and self.value == other.value

    def __repr__(self):
        return f"AddableNumber({self.value})"


class MultiplicativeMonoid:
    """Number class implementing Monoid with multiplication."""

    def __init__(self, value):
        self.value = value

    def combine(self, other):
        """Combine by multiplying values."""
        return MultiplicativeMonoid(self.value * other.value)

    @staticmethod
    def identity():
        """Identity for multiplication is 1."""
        return MultiplicativeMonoid(1)

    def __eq__(self, other):
        return isinstance(other, MultiplicativeMonoid) and self.value == other.value

    def __repr__(self):
        return f"MultiplicativeMonoid({self.value})"


class StringMonoid:
    """String class implementing Monoid with concatenation."""

    def __init__(self, value):
        self.value = value

    def combine(self, other):
        """Combine by concatenating strings."""
        return StringMonoid(self.value + other.value)

    @staticmethod
    def identity():
        """Identity for concatenation is empty string."""
        return StringMonoid("")

    def __eq__(self, other):
        return isinstance(other, StringMonoid) and self.value == other.value

    def __repr__(self):
        return f"StringMonoid({self.value!r})"


class ListMonoid:
    """List class implementing Monoid with concatenation."""

    def __init__(self, items):
        self.items = items

    def combine(self, other):
        """Combine by concatenating lists."""
        return ListMonoid(self.items + other.items)

    @staticmethod
    def identity():
        """Identity for concatenation is empty list."""
        return ListMonoid([])

    def __eq__(self, other):
        return isinstance(other, ListMonoid) and self.items == other.items

    def __repr__(self):
        return f"ListMonoid({self.items!r})"


class TestCombinableProtocol:
    """Tests for Combinable protocol."""

    def test_addable_number_is_combinable(self):
        """AddableNumber should satisfy Combinable protocol."""
        num: Combinable = AddableNumber(5)
        assert isinstance(num, Combinable)

    def test_combine_adds_values(self):
        """combine should add values."""
        num1 = AddableNumber(10)
        num2 = AddableNumber(20)
        result = num1.combine(num2)
        assert result.value == 30

    def test_combine_returns_new_instance(self):
        """combine should return a new instance."""
        num1 = AddableNumber(10)
        num2 = AddableNumber(20)
        result = num1.combine(num2)
        assert result is not num1
        assert result is not num2

    def test_combine_chaining(self):
        """Multiple combine operations should chain."""
        num1 = AddableNumber(5)
        num2 = AddableNumber(10)
        num3 = AddableNumber(15)
        result = num1.combine(num2).combine(num3)
        assert result.value == 30

    def test_combine_associative(self):
        """combine should be associative: (a + b) + c == a + (b + c)."""
        a = AddableNumber(5)
        b = AddableNumber(10)
        c = AddableNumber(15)

        result1 = a.combine(b).combine(c)
        result2 = a.combine(b.combine(c))

        assert result1 == result2

    def test_combine_with_zero(self):
        """combine with zero should work."""
        num1 = AddableNumber(10)
        num2 = AddableNumber(0)
        result = num1.combine(num2)
        assert result.value == 10


class TestMonoidProtocol:
    """Tests for Monoid protocol."""

    def test_multiplicative_is_monoid(self):
        """MultiplicativeMonoid should satisfy Monoid protocol."""
        num: Monoid = MultiplicativeMonoid(5)
        assert isinstance(num, Monoid)

    def test_string_is_monoid(self):
        """StringMonoid should satisfy Monoid protocol."""
        s: Monoid = StringMonoid("hello")
        assert isinstance(s, Monoid)

    def test_list_is_monoid(self):
        """ListMonoid should satisfy Monoid protocol."""
        lst: Monoid = ListMonoid([1, 2, 3])
        assert isinstance(lst, Monoid)

    def test_identity_left_law(self):
        """identity().combine(x) == x (left identity)."""
        x = MultiplicativeMonoid(5)
        result = MultiplicativeMonoid.identity().combine(x)
        assert result == x

    def test_identity_right_law(self):
        """x.combine(identity()) == x (right identity)."""
        x = StringMonoid("hello")
        result = x.combine(StringMonoid.identity())
        assert result == x

    def test_identity_for_multiplication(self):
        """Identity for multiplication should be 1."""
        assert MultiplicativeMonoid.identity().value == 1

    def test_identity_for_string_concatenation(self):
        """Identity for string concatenation should be empty string."""
        assert StringMonoid.identity().value == ""

    def test_identity_for_list_concatenation(self):
        """Identity for list concatenation should be empty list."""
        assert ListMonoid.identity().items == []

    def test_combine_with_identity_multiplication(self):
        """Combining with identity should not change value (multiplication)."""
        x = MultiplicativeMonoid(10)
        result1 = x.combine(MultiplicativeMonoid.identity())
        result2 = MultiplicativeMonoid.identity().combine(x)
        assert result1 == x
        assert result2 == x

    def test_combine_with_identity_string(self):
        """Combining with identity should not change value (string)."""
        x = StringMonoid("hello")
        result1 = x.combine(StringMonoid.identity())
        result2 = StringMonoid.identity().combine(x)
        assert result1 == x
        assert result2 == x

    def test_combine_with_identity_list(self):
        """Combining with identity should not change value (list)."""
        x = ListMonoid([1, 2, 3])
        result1 = x.combine(ListMonoid.identity())
        result2 = ListMonoid.identity().combine(x)
        assert result1 == x
        assert result2 == x

    def test_combine_strings(self):
        """combine should concatenate strings."""
        s1 = StringMonoid("hello")
        s2 = StringMonoid(" ")
        s3 = StringMonoid("world")
        result = s1.combine(s2).combine(s3)
        assert result.value == "hello world"

    def test_combine_lists(self):
        """combine should concatenate lists."""
        l1 = ListMonoid([1, 2])
        l2 = ListMonoid([3, 4])
        l3 = ListMonoid([5, 6])
        result = l1.combine(l2).combine(l3)
        assert result.items == [1, 2, 3, 4, 5, 6]

    def test_associative_with_identity(self):
        """Monoid laws should hold with identity."""
        x = StringMonoid("a")
        y = StringMonoid("b")
        z = StringMonoid("c")
        identity = StringMonoid.identity()

        # Associativity: (x + y) + z == x + (y + z)
        result1 = x.combine(y).combine(z)
        result2 = x.combine(y.combine(z))
        assert result1 == result2

        # Left identity: identity + x == x
        result3 = identity.combine(x)
        assert result3 == x

        # Right identity: x + identity == x
        result4 = x.combine(identity)
        assert result4 == x

    def test_multiple_combine_with_identity(self):
        """Multiple combines with identity should preserve value."""
        x = MultiplicativeMonoid(5)
        identity = MultiplicativeMonoid.identity()

        result = x.combine(identity).combine(identity).combine(identity)
        assert result == x
