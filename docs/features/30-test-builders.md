# Test Builders - Property-Based Testing

Generate test cases automatically with property-based testing helpers.

## Overview

Test builders enable:
- Auto-generated test data
- Property-based testing
- Shrinking of failures
- Custom generators
- Replayable tests

## Basic Generators

```python
from typing import Callable, TypeVar, Any
from dataclasses import dataclass
import random

T = TypeVar('T')

@dataclass
class Gen:
    """Test data generator"""

    generate: Callable[[], T]

    def map(self, func: Callable[[T], Any]) -> 'Gen':
        """Map generated values"""

        def mapped():
            return func(self.generate())

        return Gen(mapped)

    def filter(self, predicate: Callable[[T], bool]) -> 'Gen':
        """Filter generated values"""

        def filtered():
            while True:
                value = self.generate()
                if predicate(value):
                    return value

        return Gen(filtered)

    def flat_map(self, func: Callable[[T], 'Gen']) -> 'Gen':
        """Chain generators"""

        def flat_mapped():
            value = self.generate()
            return func(value).generate()

        return Gen(flat_mapped)

    def sample(self, n: int = 10) -> list[T]:
        """Generate n samples"""
        return [self.generate() for _ in range(n)]


# === Built-in Generators ===

class Generators:
    """Common generators"""

    @staticmethod
    def int(min_val: int = -1000, max_val: int = 1000) -> Gen[int]:
        return Gen(lambda: random.randint(min_val, max_val))

    @staticmethod
    def float(min_val: float = 0.0, max_val: float = 1.0) -> Gen[float]:
        return Gen(lambda: random.uniform(min_val, max_val))

    @staticmethod
    def str(length: int = 10) -> Gen[str]:
        import string
        chars = string.ascii_letters + string.digits
        return Gen(lambda: ''.join(random.choice(chars) for _ in range(length)))

    @staticmethod
    def one_of(*options: T) -> Gen[T]:
        return Gen(lambda: random.choice(options))

    @staticmethod
    def list_of(gen: Gen, min_size: int = 0, max_size: int = 10) -> Gen[list]:
        def gen_list():
            size = random.randint(min_size, max_size)
            return [gen.generate() for _ in range(size)]

        return Gen(gen_list)

    @staticmethod
    def dict_of(str_gen: Gen, value_gen: Gen, min_size: int = 0, max_size: int = 10) -> Gen[dict]:
        def gen_dict():
            size = random.randint(min_size, max_size)
            return {
                str_gen.generate(): value_gen.generate()
                for _ in range(size)
            }

        return Gen(gen_dict)

    @staticmethod
    def constant(value: T) -> Gen[T]:
        return Gen(lambda: value)


# === Usage ===

# Generate random integers
int_gen = Generators.int(0, 100)
print(int_gen.sample(5))  # [42, 17, 83, 5, 91]

# Generate random strings
str_gen = Generators.str(10)
print(str_gen.sample(3))  # ['abc123XYZ', 'helloWORLD', 'Test1234']

# Generate lists
list_gen = Generators.list_of(Generators.int(), min_size=1, max_size=5)
print(list_gen.sample(2))  # [[1, 2], [42, 17, 83, 5]]
```

## Property-Based Testing

```python
from typing import Callable

class Property:
    """Property test"""

    def __init__(
        self,
        name: str,
        property_func: Callable,
        *generators: Gen
    ):
        self.name = name
        self.property_func = property_func
        self.generators = generators

    def check(self, iterations: int = 100) -> bool:
        """Check property"""

        for i in range(iterations):
            args = [gen.generate() for gen in self.generators]

            try:
                result = self.property_func(*args)
                if not result:
                    print(f"Property '{self.name}' failed on iteration {i}")
                    print(f"Args: {args}")
                    return False
            except Exception as e:
                print(f"Property '{self.name}' raised exception on iteration {i}")
                print(f"Args: {args}")
                print(f"Exception: {e}")
                return False

        print(f"Property '{self.name}' passed {iterations} tests")
        return True


def property(name: str, *generators: Gen):
    """Decorator for property tests"""

    def decorator(func: Callable) -> Property:
        return Property(name, func, *generators)

    return decorator


# === Usage ===

@property("reverse_twice", Generators.list_of(Generators.int()))
def prop_reverse_twice(lst: list) -> bool:
    """Reversing twice returns original"""

    return lst == lst[::-1][::-1]

@property("sort_ordered", Generators.list_of(Generators.int()))
def prop_sort_ordered(lst: list) -> bool:
    """Sorting produces ordered list"""

    sorted_lst = sorted(lst)
    return all(sorted_lst[i] <= sorted_lst[i+1] for i in range(len(sorted_lst)-1))

@property("add_commutative", Generators.int(), Generators.int())
def prop_add_commutative(a: int, b: int) -> bool:
    """Addition is commutative"""

    return a + b == b + a


# Run properties
prop_reverse_twice.check(100)
prop_sort_ordered.check(100)
prop_add_commutative.check(100)
```

## Test Shrinking

```python
@dataclass
class ShrinkResult:
    """Shrunk failure case"""

    value: Any
    steps: int

class Shrinking:
    """Shrink failing test cases"""

    @staticmethod
    def shrink_int(value: int) -> list[int]:
        """Shrink integer"""

        candidates = [0]
        if value != 0:
            candidates.append(value // 2)

        if value > 0:
            candidates.extend(range(1, min(value, 10)))
        elif value < 0:
            candidates.extend(range(-1, max(value, -10), -1))

        return candidates

    @staticmethod
    def shrink_list(lst: list) -> list[list]:
        """Shrink list"""

        # Try removing elements
        candidates = [[]]

        for i in range(len(lst)):
            candidates.append(lst[:i] + lst[i+1:])

        # Try shrinking first few elements
        if len(lst) > 1:
            candidates.append(lst[:1])
            candidates.append(lst[:2])

        return candidates

    @staticmethod
    def find_minimal(
        value: Any,
        property_func: Callable,
        shrink_func: Callable
    ) -> ShrinkResult:

        current = value
        steps = 0

        while True:
            shrinks = shrink_func(current)

            found_shrink = False
            for shrink in shrinks:

                if property_func(shrink):
                    current = shrink
                    found_shrink = True
                    steps += 1
                    break

            if not found_shrink:
                break

        return ShrinkResult(current, steps)


# === Usage ===

def failing_property(lst: list) -> bool:
    """Property that fails for non-empty lists"""

    if len(lst) == 0:
        return True

    # Fails if list has duplicates
    return len(lst) == len(set(lst))


# Find minimal failing case
original = [1, 2, 3, 2, 4, 5, 3]
result = Shrinking.find_minimal(
    original,
    lambda x: not failing_property(x),  # We want it to fail
    Shrinking.shrink_list
)

print(f"Minimal failing: {result.value}")  # [1, 1] or [1, 2, 2]
print(f"Steps: {result.steps}")
```

## ForAll Testing

```python
def for_all(*generators: Gen):
    """Universal quantifier for testing"""

    def decorator(property_func: Callable) -> Property:
        return Property(
            property_func.__name__,
            property_func,
            *generators
        )

    return decorator


# === Usage ===

@for_all(Generators.int(), Generators.int(), Generators.int())
def prop_add_associative(a: int, b: int, c: int) -> bool:
    """Addition is associative"""

    return (a + b) + c == a + (b + c)

@for_all(Generators.str())
def prop_str_length(s: str) -> bool:
    """String length is non-negative"""

    return len(s) >= 0

prop_add_associative.check(100)
prop_str_length.check(100)
```

## Custom Generators

```python
class EmailGen:
    """Email generator"""

    @staticmethod
    def create() -> Gen[str]:

        domains = ["example.com", "test.org", "demo.net", "mail.io"]

        def gen_email():
            username = Generators.str(5, 15).generate().lower()
            domain = random.choice(domains)
            return f"{username}@{domain}"

        return Gen(gen_email)


class UserGen:
    """User generator"""

    @staticmethod
    def create() -> Gen[dict]:

        def gen_user():
            return {
                "id": Generators.int(1, 1000).generate(),
                "name": Generators.str(3, 20).generate(),
                "email": EmailGen.create().generate(),
                "age": Generators.int(18, 80).generate(),
                "active": Generators.one_of(True, False).generate()
            }

        return Gen(gen_user)


# === Usage ===

email_gen = EmailGen.create()
print(email_gen.sample(5))

user_gen = UserGen.create()
print(user_gen.sample(3))
```

## State Machine Testing

```python
class Command:
    """State machine command"""

    def __init__(self, name: str, execute: Callable, check: Callable):
        self.name = name
        self.execute = execute
        self.check = check


class StateMachineTest:
    """Test state machine"""

    def __init__(self, initial_state):
        self.state = initial_state
        self.commands: list[Command] = []
        self.history: list = []

    def command(self, name: str):
        """Decorator for commands"""

        def decorator(func: Callable) -> Callable:

            def wrapper(*args, **kwargs):
                # Execute command
                result = func(self.state, *args, **kwargs)

                # Record history
                self.history.append({
                    "command": name,
                    "args": args,
                    "result": result
                })

                return result

            # Register as command
            self.commands.append(Command(name, wrapper, lambda: True))
            return wrapper

        return decorator

    def run_commands(self, num_commands: int, gen: Gen):
        """Run random commands"""

        for _ in range(num_commands):
            cmd = random.choice(self.commands)
            args = gen.generate()
            cmd.execute(*args)

    def verify(self):
        """Verify state machine"""

        return all(cmd.check() for cmd in self.commands)


# === Usage ===

class CounterTest(StateMachineTest):

    def __init__(self):
        super().__init__(0)

    @StateMachineTest.command
    def increment(self, state):
        self.state = state + 1
        return self.state

    @StateMachineTest.command
    def add(self, state, n: int):
        self.state = state + n
        return self.state

test = CounterTest()
test.run_commands(10, Generators.int(1, 10))
```

## DX Benefits

✅ **Automated**: Auto-generate test cases
✅ **Thorough**: Find edge cases
✅ **Shrinking**: Minimal failing examples
✅ **Replayable**: Same random seeds
✅ **Composable**: Combine generators

## Best Practices

```python
# ✅ Good: Test properties
@for_all(Generators.int(), Generators.int())
def prop_add_commutative(a, b):
    return a + b == b + a

# ✅ Good: Use shrinking
# Helps find minimal failing case

# ✅ Good: Custom generators
class EmailGen:
    @staticmethod
    def create():
        return Gen(...)

# ❌ Bad: Only testing specific values
# Properties should test many random inputs
```
