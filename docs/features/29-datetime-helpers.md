# Date/Time Helpers - Temporal Operations

Simplify date and time operations with functional helpers.

## Overview

DateTime helpers enable:
- Easy date arithmetic
- Range operations
- Timezone handling
- Formatting/parsing
- Duration calculations

## Date Arithmetic

```python
from datetime import datetime, date, timedelta, timezone
from typing import Any

class DateDelta:
    """Date arithmetic helpers"""

    @staticmethod
    def days(n: int) -> timedelta:
        return timedelta(days=n)

    @staticmethod
    def weeks(n: int) -> timedelta:
        return timedelta(weeks=n)

    @staticmethod
    def hours(n: int) -> timedelta:
        return timedelta(hours=n)

    @staticmethod
    def minutes(n: int) -> timedelta:
        return timedelta(minutes=n)

    @staticmethod
    def seconds(n: int) -> timedelta:
        return timedelta(seconds=n)

    @staticmethod
    def milliseconds(n: int) -> timedelta:
        return timedelta(milliseconds=n)

    @staticmethod
    def microseconds(n: int) -> timedelta:
        return timedelta(microseconds=n)


# === Usage ===

from datetime import datetime

now = datetime.now()

tomorrow = now + DateDelta.days(1)
next_week = now + DateDelta.weeks(1)
in_two_hours = now + DateDelta.hours(2)

print(tomorrow)
print(next_week)
print(in_two_hours)
```

## Date Range

```python
from dataclasses import dataclass
from typing import Generator, Any

@dataclass
class DateRange:
    """Date range for operations"""

    start: Any
    end: Any

    def __contains__(self, date: Any) -> bool:
        """Check if date is in range"""
        return self.start <= date <= self.end

    def duration(self) -> timedelta:
        """Get duration"""
        return self.end - self.start

    def days(self) -> int:
        """Number of days in range"""
        return (self.end - self.start).days + 1

    def overlaps(self, other: 'DateRange') -> bool:
        """Check if ranges overlap"""
        return not (self.end < other.start or self.start > other.end)

    def iter_days(self) -> Generator[date, None, None]:
        """Iterate over days in range"""

        current = self.start
        while current <= self.end:
            yield current
            current += timedelta(days=1)

    def __iter__(self) -> Generator:
        return self.iter_days()

    def __repr__(self) -> str:
        return f"DateRange({self.start} to {self.end})"


# === Usage ===

from datetime import date

range1 = DateRange(date(2024, 1, 1), date(2024, 1, 31))
range2 = DateRange(date(2024, 1, 15), date(2024, 2, 15))

print(date(2024, 1, 15) in range1)  # True
print(range1.overlaps(range2))     # True

# Iterate
for day in range1:
    print(day)

print(range1.days())  # 31
print(range1.duration())  # 30 days, 0:00:00
```

## Time Helpers

```python
class TimeHelper:
    """Time manipulation helpers"""

    @staticmethod
    def now(tz: timezone | None = None) -> datetime:
        """Get current time"""

        if tz:
            return datetime.now(tz)
        return datetime.now()

    @staticmethod
    def today() -> date:
        """Get today's date"""
        return date.today()

    @staticmethod
    def unix_timestamp(dt: datetime) -> int:
        """Get Unix timestamp"""
        return int(dt.timestamp())

    @staticmethod
    def from_timestamp(ts: int) -> datetime:
        """Create datetime from Unix timestamp"""
        return datetime.fromtimestamp(ts)

    @staticmethod
    def parse(date_string: str, format: str) -> datetime:
        """Parse date string"""
        return datetime.strptime(date_string, format)

    @staticmethod
    def format(dt: datetime, format: str) -> str:
        """Format datetime"""
        return dt.strftime(format)


# === Usage ===

now = TimeHelper.now()
print(now)

timestamp = TimeHelper.unix_timestamp(now)
print(timestamp)

dt = TimeHelper.from_timestamp(1704067200)
print(dt)

parsed = TimeHelper.parse("2024-01-01", "%Y-%m-%d")
print(parsed)

formatted = TimeHelper.format(now, "%Y-%m-%d %H:%M")
print(formatted)
```

## Timezone Helpers

```python
from zoneinfo import ZoneInfo

class TzHelper:
    """Timezone helpers"""

    @staticmethod
    def in_timezone(dt: datetime, tz_name: str) -> datetime:
        """Convert datetime to timezone"""

        tz = ZoneInfo(tz_name)
        return dt.astimezone(tz)

    @staticmethod
    def utc(dt: datetime) -> datetime:
        """Convert to UTC"""

        return dt.astimezone(ZoneInfo("UTC"))

    @staticmethod
    def local_to_utc(dt: datetime) -> datetime:
        """Convert local time to UTC"""

        return dt.astimezone(ZoneInfo("UTC"))

    @staticmethod
    def now_in(tz_name: str) -> datetime:
        """Get current time in timezone"""

        tz = ZoneInfo(tz_name)
        return datetime.now(tz)


# === Usage ===

now = TimeHelper.now()

# Convert to Paris time
in_paris = TzHelper.in_timezone(now, "Europe/Paris")
print(in_paris)

# Convert to UTC
in_utc = TzHelper.utc(now)
print(in_utc)

# Get time in Tokyo
in_tokyo = TzHelper.now_in("Asia/Tokyo")
print(in_tokyo)
```

## Date Comparison

```python
class DateCompare:
    """Date comparison helpers"""

    @staticmethod
    def is_before(dt1: Any, dt2: Any) -> bool:
        return dt1 < dt2

    @staticmethod
    def is_after(dt1: Any, dt2: Any) -> bool:
        return dt1 > dt2

    @staticmethod
    def is_same(dt1: Any, dt2: Any, granularity: str = "day") -> bool:

        if granularity == "day":
            return dt1.date() == dt2.date()
        elif granularity == "month":
            return dt1.year == dt2.year and dt1.month == dt2.month
        elif granularity == "year":
            return dt1.year == dt2.year
        elif granularity == "hour":
            return (
                dt1.year == dt2.year and
                dt1.month == dt2.month and
                dt1.day == dt2.day and
                dt1.hour == dt2.hour
            )
        return dt1 == dt2

    @staticmethod
    def is_between(dt: Any, start: Any, end: Any) -> bool:
        return start <= dt <= end

    @staticmethod
    def is_today(dt: Any) -> bool:
        return dt.date() == date.today()

    @staticmethod
    def is_past(dt: Any) -> bool:
        return dt < datetime.now()

    @staticmethod
    def is_future(dt: Any) -> bool:
        return dt > datetime.now()


# === Usage ===

now = TimeHelper.now()
past = now - timedelta(days=1)
future = now + timedelta(days=1)

print(DateCompare.is_before(past, now))    # True
print(DateCompare.is_after(future, now))   # True
print(DateCompare.is_today(now))           # True
print(DateCompare.is_past(past))           # True
print(DateCompare.is_future(future))        # True
```

## Date Builders

```python
class DateBuilder:
    """Build dates from components"""

    @staticmethod
    def create(year: int, month: int, day: int) -> date:
        return date(year, month, day)

    @staticmethod
    def create_datetime(
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0
    ) -> datetime:
        return datetime(year, month, day, hour, minute, second)

    @staticmethod
    def start_of_day(dt: Any) -> datetime:
        return datetime.combine(dt, datetime.min.time())

    @staticmethod
    def end_of_day(dt: Any) -> datetime:
        return datetime.combine(dt, datetime.max.time())

    @staticmethod
    def start_of_month(dt: Any) -> datetime:
        return datetime(dt.year, dt.month, 1)

    @staticmethod
    def end_of_month(dt: Any) -> datetime:

        if dt.month == 12:
            return datetime(dt.year + 1, 1, 1) - timedelta(seconds=1)

        return datetime(dt.year, dt.month + 1, 1) - timedelta(seconds=1)

    @staticmethod
    def start_of_week(dt: Any) -> datetime:
        """Monday of current week"""

        weekday = dt.weekday()
        return dt - timedelta(days=weekday)

    @staticmethod
    def end_of_week(dt: Any) -> datetime:
        """Sunday of current week"""

        start = DateBuilder.start_of_week(dt)
        return start + timedelta(days=6, hours=23, minutes=59, seconds=59)


# === Usage ===

dt = datetime(2024, 1, 15, 14, 30)

print(DateBuilder.start_of_day(dt))   # 2024-01-15 00:00:00
print(DateBuilder.end_of_day(dt))     # 2024-01-15 23:59:59
print(DateBuilder.start_of_month(dt)) # 2024-01-01 00:00:00
print(DateBuilder.end_of_month(dt))   # 2024-01-31 23:59:59
print(DateBuilder.start_of_week(dt))  # 2024-01-15 00:00:00 (Monday)
```

## Duration Helpers

```python
class DurationHelper:
    """Duration calculation helpers"""

    @staticmethod
    def between(start: Any, end: Any) -> timedelta:
        return end - start

    @staticmethod
    def in_seconds(delta: timedelta) -> float:
        return delta.total_seconds()

    @staticmethod
    def in_minutes(delta: timedelta) -> float:
        return delta.total_seconds() / 60

    @staticmethod
    def in_hours(delta: timedelta) -> float:
        return delta.total_seconds() / 3600

    @staticmethod
    def in_days(delta: timedelta) -> float:
        return delta.total_seconds() / 86400

    @staticmethod
    def humanize(delta: timedelta) -> str:
        """Human-readable duration"""

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h"
        else:
            days = seconds // 86400
            return f"{days}d"


# === Usage ===

start = datetime(2024, 1, 1, 10, 0)
end = datetime(2024, 1, 1, 14, 30)

duration = DurationHelper.between(start, end)

print(DurationHelper.in_seconds(duration))  # 16200.0
print(DurationHelper.in_minutes(duration))  # 270.0
print(DurationHelper.in_hours(duration))    # 4.5
print(DurationHelper.humanize(duration))    # "4h"
```

## DX Benefits

✅ **Simple**: Easy date arithmetic
✅ **Readable**: Clear duration formats
✅ **Flexible**: Works with date/datetime
✅ **Complete**: Timezone support
✅ **Type-safe**: Works with type checkers

## Best Practices

```python
# ✅ Good: Use deltas for arithmetic
next_week = now + DateDelta.weeks(1)

# ✅ Good: Timezone-aware
in_paris = TzHelper.in_timezone(now, "Europe/Paris")

# ✅ Good: Range checking
if date in DateRange(start, end):
    ...

# ❌ Bad: Manual timedelta
# Use DateDelta helpers instead
```
