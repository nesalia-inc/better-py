# Predicate Combinators - Logic Composition

Combine and compose logical predicates for readable condition checks.

## Overview

Predicate combinators enable:
- Composable logical conditions
- Readable complex predicates
- Reusable condition fragments
- Type-safe comparisons
- Fluent API

## Basic Predicate

```python
from typing import Callable, TypeVar, Any
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Predicate:
    """Composable predicate"""

    _test: Callable[[T], bool]

    def __call__(self, value: T) -> bool:
        return self._test(value)

    def __and__(self, other: 'Predicate') -> 'Predicate':
        """AND: p1 & p2"""

        def and_test(value):
            return self(value) and other(value)

        return Predicate(and_test)

    def __or__(self, other: 'Predicate') -> 'Predicate':
        """OR: p1 | p2"""

        def or_test(value):
            return self(value) or other(value)

        return Predicate(or_test)

    def __invert__(self) -> 'Predicate':
        """NOT: ~p"""

        def not_test(value):
            return not self(value)

        return Predicate(not_test)

    def __xor__(self, other: 'Predicate') -> 'Predicate':
        """XOR: p1 ^ p2"""

        def xor_test(value):
            return self(value) != other(value)

        return Predicate(xor_test)


# === Usage ===

is_positive = Predicate(lambda x: x > 0)
is_even = Predicate(lambda x: x % 2 == 0)

positive_and_even = is_positive & is_even
positive_or_even = is_positive | is_even
not_positive = ~is_positive

print(positive_and_even(4))   # True
print(positive_and_even(3))   # False (not even)
print(positive_or_even(-2))   # True (even)
print(not_positive(-5))       # True
```

## Comparison Predicates

```python
class Comparison:
    """Comparison predicate builders"""

    @staticmethod
    def gt(value: Any) -> Predicate:
        """Greater than"""
        return Predicate(lambda x: x > value)

    @staticmethod
    def gte(value: Any) -> Predicate:
        """Greater than or equal"""
        return Predicate(lambda x: x >= value)

    @staticmethod
    def lt(value: Any) -> Predicate:
        """Less than"""
        return Predicate(lambda x: x < value)

    @staticmethod
    def lte(value: Any) -> Predicate:
        """Less than or equal"""
        return Predicate(lambda x: x <= value)

    @staticmethod
    def eq(value: Any) -> Predicate:
        """Equal to"""
        return Predicate(lambda x: x == value)

    @staticmethod
    def ne(value: Any) -> Predicate:
        """Not equal to"""
        return Predicate(lambda x: x != value)

    @staticmethod
    def in_range(min_val: Any, max_val: Any) -> Predicate:
        """In inclusive range"""
        return Predicate(lambda x: min_val <= x <= max_val)

    @staticmethod
    def one_of(*values: Any) -> Predicate:
        """One of the values"""
        return Predicate(lambda x: x in values)


# === Usage ===

age = Comparison.in_range(18, 65)
priority = Comparison.one_of("high", "urgent", "critical")

print(age(25))      # True
print(age(15))      # False
print(priority("high"))  # True
```

## String Predicates

```python
class StringPredicates:
    """String-specific predicates"""

    @staticmethod
    def contains(substring: str, case_sensitive: bool = True) -> Predicate:
        """Contains substring"""

        if case_sensitive:
            return Predicate(lambda x: substring in x)
        else:
            substring_lower = substring.lower()
            return Predicate(lambda x: substring_lower in x.lower())

    @staticmethod
    def starts_with(prefix: str) -> Predicate:
        """Starts with prefix"""
        return Predicate(lambda x: x.startswith(prefix))

    @staticmethod
    def ends_with(suffix: str) -> Predicate:
        """Ends with suffix"""
        return Predicate(lambda x: x.endswith(suffix))

    @staticmethod
    def matches(pattern: str) -> Predicate:
        """Matches regex pattern"""
        import re
        regex = re.compile(pattern)
        return Predicate(lambda x: bool(regex.match(x)))

    @staticmethod
    def length(min_len: int = 0, max_len: int | None = None) -> Predicate:
        """String length in range"""

        def check_length(s: str) -> bool:
            l = len(s)
            if l < min_len:
                return False
            if max_len is not None and l > max_len:
                return False
            return True

        return Predicate(check_length)

    @staticmethod
    def email() -> Predicate:
        """Valid email format"""

        def is_email(s: str) -> bool:
            parts = s.split("@")
            if len(parts) != 2:
                return False
            local, domain = parts
            return "." in domain and len(local) > 0 and len(domain) > 0

        return Predicate(is_email)


# === Usage ===

valid_name = StringPredicates.length(min_len=2, max_len=50)
valid_email = StringPredicates.email()
has_http = StringPredicates.starts_with("http")

print(valid_name("Alice"))  # True
print(valid_name("A"))      # False
print(valid_email("user@example.com"))  # True
```

## Collection Predicates

```python
class CollectionPredicates:
    """Collection-specific predicates"""

    @staticmethod
    def empty() -> Predicate:
        """Is empty"""
        return Predicate(lambda x: len(x) == 0)

    @staticmethod
    def not_empty() -> Predicate:
        """Is not empty"""
        return Predicate(lambda x: len(x) > 0)

    @staticmethod
    def contains(item: Any) -> Predicate:
        """Contains item"""
        return Predicate(lambda x: item in x)

    @staticmethod
    def size(n: int) -> Predicate:
        """Has exact size"""
        return Predicate(lambda x: len(x) == n)

    @staticmethod
    def size_at_least(n: int) -> Predicate:
        """Size at least n"""
        return Predicate(lambda x: len(x) >= n)

    @staticmethod
    def size_at_most(n: int) -> Predicate:
        """Size at most n"""
        return Predicate(lambda x: len(x) <= n)

    @staticmethod
    def all(predicate: Predicate) -> Predicate:
        """All elements satisfy predicate"""

        def all_test(collection):
            return all(predicate(item) for item in collection)

        return Predicate(all_test)

    @staticmethod
    def any(predicate: Predicate) -> Predicate:
        """Any element satisfies predicate"""

        def any_test(collection):
            return any(predicate(item) for item in collection)

        return Predicate(any_test)

    @staticmethod
    def none(predicate: Predicate) -> Predicate:
        """No element satisfies predicate"""

        def none_test(collection):
            return not any(predicate(item) for item in collection)

        return Predicate(none_test)


# === Usage ===

has_items = CollectionPredicates.not_empty()
has_5_items = CollectionPredicates.size(5)
has_positive = CollectionPredicates.all(Comparison.gt(0))

print(has_items([1, 2, 3]))        # True
print(has_5_items([1, 2, 3, 4, 5])) # True
print(has_positive([1, 2, -3]))    # False
```

## Object Attribute Predicates

```python
class AttrPredicates:
    """Object attribute predicates"""

    @staticmethod
    def attr(attr_name: str, predicate: Predicate | None = None) -> Predicate:
        """Check attribute value"""

        if predicate is None:
            return Predicate(lambda obj: hasattr(obj, attr_name))

        def check_attr(obj):
            if not hasattr(obj, attr_name):
                return False
            return predicate(getattr(obj, attr_name))

        return Predicate(check_attr)

    @staticmethod
    def has_attr(attr_name: str) -> Predicate:
        """Has attribute"""
        return Predicate(lambda obj: hasattr(obj, attr_name))


# === Usage ===

@dataclass
class User:
    name: str
    age: int
    email: str

is_adult = AttrPredicates.attr("age", Comparison.gte(18))
named_alice = AttrPredicates.attr("name", Comparison.eq("Alice"))

user = User("Alice", 25, "alice@example.com")

print(is_adult(user))    # True
print(named_alice(user)) # True
```

## Predicate Builder

```python
class PredicateBuilder:
    """Fluent predicate builder"""

    def __init__(self):
        self._predicates: list[Predicate] = []

    def must(self, predicate: Predicate) -> 'PredicateBuilder':
        """Add required predicate"""
        self._predicates.append(predicate)
        return self

    def should(self, predicate: Predicate) -> 'PredicateBuilder':
        """Add optional predicate"""
        self._predicates.append(predicate)
        return self

    def build(self, combine: str = "and") -> Predicate:
        """Build final predicate"""

        if not self._predicates:
            return Predicate(lambda x: True)

        if combine == "and":
            result = self._predicates[0]
            for pred in self._predicates[1:]:
                result = result & pred
            return result

        elif combine == "or":
            result = self._predicates[0]
            for pred in self._predicates[1:]:
                result = result | pred
            return result

        raise ValueError(f"Unknown combine: {combine}")


# === Usage ===

valid_user = (
    PredicateBuilder()
    .must(StringPredicates.length(min_len=2))
    .must(StringPredicates.email())
    .build()
)

print(valid_user("alice@example.com"))  # True
print(valid_user("a@b.co"))            # False (name too short)
```

## Custom Predicates

```python
def custom_predicate(func: Callable[[T], bool]) -> Predicate:
    """Create custom predicate"""

    return Predicate(func)


def predicate_from_regex(pattern: str) -> Predicate:
    """Create predicate from regex"""

    import re
    compiled = re.compile(pattern)

    def matches(value: str) -> bool:
        return bool(compiled.search(value))

    return Predicate(matches)


# === Usage ===

is_hex_color = predicate_from_regex(r'^#[0-9A-Fa-f]{6}$')

print(is_hex_color("#FF5733"))  # True
print(is_hex_color("red"))      # False
```

## Conditional Execution

```python
class Conditional:
    """Execute code based on predicates"""

    @staticmethod
    def if_then_else(
        predicate: Predicate,
        then_branch: Callable,
        else_branch: Callable | None = None
    ) -> Callable:

        def execute(value):
            if predicate(value):
                return then_branch(value)

            if else_branch:
                return else_branch(value)

            return None

        return execute

    @staticmethod
    def switch(cases: list[tuple[Predicate, Callable]]) -> Callable:
        """Switch on predicates"""

        def execute(value):
            for predicate, handler in cases:
                if predicate(value):
                    return handler(value)
            return None

        return execute


# === Usage ===

handle_number = Conditional.if_then_else(
    Comparison.gt(0),
    lambda x: f"Positive: {x}",
    lambda x: f"Non-positive: {x}"
)

print(handle_number(5))   # "Positive: 5"
print(handle_number(-5))  # "Non-positive: -5"

# Switch
grade_handler = Conditional.switch([
    (Comparison.gte(90), lambda x: "A"),
    (Comparison.gte(80), lambda x: "B"),
    (Comparison.gte(70), lambda x: "C"),
    (Comparison.gte(60), lambda x: "D"),
])

print(grade_handler(85))  # "B"
```

## DX Benefits

✅ **Composable**: Combine simple predicates into complex ones
✅ **Reusable**: Define once, use everywhere
✅ **Readable**: Complex logic becomes clear
✅ **Type-safe**: Works with static type checkers
✅ **Testable**: Individual predicates easily tested

## Best Practices

```python
# ✅ Good: Named predicates
is_adult_user = has_account & is_18_plus & is_active

# ✅ Good: Compose from simple parts
is_valid_email = has "@" & has "." & local_part_not_empty

# ✅ Good: Use with filter
valid_users = filter(is_valid_user, all_users)

# ❌ Bad: Inline complex logic
# Don't: filter(lambda x: x.age >= 18 and x.email and x.active, users)
```
