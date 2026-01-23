# Writer - Logging Monad

Append log entries to a result while computing a value.

## Overview

`Writer` represents a computation that produces a value and a log:
- `Writer((value, logs))` - Value with accumulated logs

## Basic Usage

```python
from mfn import Writer

# Create Writer with value and log
result = Writer((42, ["Starting calculation"]))
result = result.tell("Step 1 complete")
result = result.tell("Step 2 complete")

# Get value and logs
value, logs = result.run()
# value: 42
# logs: ["Starting calculation", "Step 1 complete", "Step 2 complete"]
```

## Transformation

```python
from mfn import Writer

# Map: Transform value (keeps logs)
writer = Writer((5, ["Initial value"]))

result = writer.map(lambda x: x * 2)
# Writer((10, ["Initial value"]))

# Tell: Add log entry
result = writer.tell("Doubled the value")
# Writer((5, ["Initial value", "Doubled the value"]))
```

## Chaining Writers

```python
from mfn import Writer

def validate_name(name: str) -> Writer:

    errors = []

    if len(name) < 2:
        errors.append("Name too short")

    if len(name) > 50:
        errors.append("Name too long")

    if errors:
        return Writer((None, errors))

    return Writer((name.title(), ["Name validated"]))


def validate_email(email: str) -> Writer:

    errors = []

    if "@" not in email:
        errors.append("Email needs @")

    if "." not in email.split("@")[-1]:
        errors.append("Invalid domain")

    if errors:
        return Writer((None, errors))

    return Writer((email.lower(), ["Email validated"]))


# Chain writers
def validate_user(name: str, email: str) -> Writer:

    name_result = validate_name(name)
    email_result = validate_email(email)

    all_logs = name_result.logs + email_result.logs

    if name_result.value is None or email_result.value is None:
        return Writer((None, all_logs))

    return Writer((
        {"name": name_result.value, "email": email_result.value},
        all_logs
    ))


# Use
result = validate_user("bob", "BOB@EXAMPLE.COM")

user, logs = result.run()
# user: {"name": "Bob", "email": "bob@example.com"}
# logs: ["Name validated", "Email validated"]
```

## Accumulating Values

```python
from mfn import Writer

def count_words(text: str) -> Writer:

    words = text.split()
    count = len(words)

    logs = [
        f"Text: {text[:50]}...",
        f"Word count: {count}"
    ]

    return Writer((count, logs))


def count_characters(text: str) -> Writer:

    count = len(text)

    logs = [
        f"Character count: {count}"
    ]

    return Writer((count, logs))


def analyze_text(text: str) -> Writer:

    word_writer = count_words(text)
    char_writer = count_characters(text)

    word_count, word_logs = word_writer.run()
    char_count, char_logs = char_writer.run()

    all_logs = word_logs + char_logs

    return Writer((
        {
            "words": word_count,
            "characters": char_count
        },
        all_logs
    ))


# Use
result = analyze_text("Hello world")
metrics, logs = result.run()

# metrics: {"words": 2, "characters": 11}
# logs: [
#   "Text: Hello world...",
#   "Word count: 2",
#   "Character count: 11"
# ]
```

## Writer with List

```python
from mfn import Writer

class ListWriter:
    """Writer that appends to a list"""

    def __init__(self, value: Any):
        self.value = value
        self.logs: list = []

    def tell(self, message: str):
        """Add log entry"""

        self.logs.append(message)
        return self

    def map(self, func):
        """Transform value"""

        return ListWriter(func(self.value))

    def run(self):
        """Get value and logs"""

        return self.value, self.logs


# Use
def process(data: dict) -> ListWriter:

    writer = ListWriter(data)

    if "name" not in data:
        writer.tell("Missing name")

    if "email" not in data:
        writer.tell("Missing email")

    return writer


result = process({"name": "Alice"})
value, logs = result.run()

# value: {"name": "Alice"}
# logs: ["Missing email"]
```

## Writer with Counter

```python
from mfn import Writer

class CountWriter:
    """Writer that counts operations"""

    def __init__(self, value: Any):
        self.value = value
        self.count = 0

    def tell(self, operation: str):
        """Record operation"""

        self.count += 1
        return self

    def map(self, func):
        """Transform value"""

        return CountWriter(func(self.value))

    def run(self):
        """Get value and count"""

        return self.value, self.count


# Use
def sort_list(items: list) -> CountWriter:

    writer = CountWriter(items)
    writer.tell("Started sorting")

    sorted_items = sorted(items)
    writer.tell(f"Sorted {len(items)} items")

    return writer


result = sort_list([3, 1, 2])
value, count = result.run()

# value: [1, 2, 3]
# count: 2
```

## Combining Writers

```python
from mfn import Writer

def combine_writers(*writers: Writer) -> Writer:

    all_values = []
    all_logs = []

    for writer in writers:
        value, logs = writer.run()
        all_values.append(value)
        all_logs.extend(logs)

    return Writer((all_values, all_logs))


# Use
result = combine_writers(
    Writer((1, ["Log 1"])),
    Writer((2, ["Log 2"])),
    Writer((3, ["Log 3"]))
)

values, logs = result.run()

# values: [1, 2, 3]
# logs: ["Log 1", "Log 2", "Log 3"]
```

## DX Benefits

✅ **Audit trail**: All operations logged
✅ **Debugging**: Trace execution
✅ **Composable**: Combine logs
✅ **Separation**: Logic separate from logging
✅ **Type-safe**: Logs are typed

## Best Practices

```python
# ✅ Good: Log meaningful messages
tell(f"Validated user {user_id}")

# ✅ Good: Log operations
tell("Database query executed")
tell("Cache updated")

# ✅ Good: Combine logs
combine_writers(writer1, writer2, writer3)

# ❌ Bad: Over-logging
# Log important events only

# ❌ Bad: Logging in wrong place
# Use Writer to keep logging with computation
```
