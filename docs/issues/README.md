# Known Issues and Problems

This directory contains documentation of known issues, bugs, and areas for improvement in the better-py library.

## Overview

These issues were identified during a comprehensive code review after achieving mypy --strict compliance. Passing type checking does not guarantee correct or optimal code.

## Issue Categories

### Critical (P0) - Must Fix

These are logic bugs that cause incorrect behavior:

- [**#001: Validation.ap() Does Not Accumulate Errors**](./001-validation-ap-no-error-accumulation.md)
  - Core promise of Validation monad is broken
  - Errors are not accumulated when both Validations are Invalid

- [**#002: State.map() and flat_map() Execute State Transformation Twice**](./002-state-double-execution.md)
  - Performance issue with double execution
  - Violates monad semantics

- [**#003: IO.__eq__() and Task.__eq__() Execute Side Effects**](./003-io-task-equality-side-effects.md)
  - Equality checks execute computations
  - Violates principle that equality should be pure

### High Priority (P1)

These issues significantly impact usability or performance:

- [**#004: PersistentList.append() Has O(n²) Performance**](./004-persistentlist-inefficient-append.md)
  - Converts entire list to Python list and back
  - Should use functional queue or prepend + reverse

- [**#005: PersistentList.drop() Creates Unnecessary Intermediate Lists**](./005-persistentlist-inefficient-drop.md)
  - O(n) time and space for what should be O(1) for linked lists
  - Creates intermediate Python list unnecessarily

- [**#006: PersistentMap.map_keys() Silently Loses Data on Key Collisions**](./006-persistentmap-mapkeys-silent-data-loss.md)
  - When mapping produces duplicate keys, values are silently lost
  - No way to specify collision resolution strategy

### Medium Priority (P2)

These are design limitations or inconsistencies:

- [**#007: Missing Applicative Operations (ap, lift2, zip)**](./007-missing-applicative-operations.md)
  - Only Validation has `ap` method
  - Maybe, Result, Either missing applicative operations

- [**#008: Maybe Cannot Distinguish None from Nothing**](./008-maybe-cannot-contain-none.md)
  - Cannot represent Some(None) vs Nothing
  - Common Python pattern where None is a valid value

- [**#009: Writer Assumes Monoid Uses + Operator**](./009-writer-assumes-monoid-plus-operator.md)
  - Limited to types with `+` operator
  - No way to use custom monoid types

- [**#010: curry() Uses apply_defaults() Unexpectedly**](./010-curry-unexpected-apply-defaults.md)
  - Default parameters filled in early
  - Violates standard currying semantics

- [**#012: Missing Test Coverage for Edge Cases**](./012-missing-test-coverage.md)
  - Many edge cases not tested
  - Missing property-based tests for monad laws
  - No performance regression tests

### Low Priority (P3)

Minor issues that don't significantly impact functionality:

- [**#011: PersistentList.get() Does Not Support Negative Indexing**](./011-persistentlist-no-negative-indexing.md)
  - Breaks Python's standard indexing convention
  - Minor usability issue

## Summary Statistics

| Severity | Count | Issues |
|----------|-------|--------|
| Critical (P0) | 3 | #001, #002, #003 |
| High (P1) | 3 | #004, #005, #006 |
| Medium (P2) | 5 | #007, #008, #009, #010, #012 |
| Low (P3) | 1 | #011 |
| **Total** | **12** | |

## Priority Matrix

```
Impact ─────────────────────────────────────►
High │     ┌───┐      ┌─────┐
    │  #1 │   │ #4, #5, #6
    │     └───┘      └─────┘
Mid  │  #2, #3   ┌──────────────────┐
    │           │ #7, #8, #9, #10, #12│
Low │           └──────────────────┘      ┌───┐ #11
    │                                      │   │
    └──────────────────────────────────────┴───┴────►
           Low          Frequency         High
```

## Recommended Fix Order

### Phase 1: Critical Bugs (Week 1)
1. Fix #001: Validation.ap() error accumulation
2. Fix #002: State double execution
3. Fix #003: IO/Task equality side effects

### Phase 2: High Priority (Week 2)
4. Document #004: PersistentList.append() performance
5. Fix #005: PersistentList.drop() intermediate lists
6. Add #006: map_keys() collision resolution

### Phase 3: Medium Priority (Week 3-4)
7. Add #007: Applicative operations to all monads
8. Consider #008: Maybe(None) distinction
9. Add #009: Monoid protocol for Writer
10. Fix #010: curry() default parameter handling
11. Add #012: Comprehensive test coverage

### Phase 4: Low Priority (Backlog)
12. Add #011: Negative indexing support

## Contributing

When fixing issues:

1. Read the issue document fully
2. Add tests that fail due to the bug
3. Fix the implementation
4. Verify tests pass
5. Add integration/property tests
6. Update documentation

## Reporting New Issues

To report new issues, create a new markdown file in this directory with:
- Clear title and description
- Code examples showing the problem
- Proposed fix(es)
- Related issues
- Test cases

Use the template from existing issues.

## See Also

- [Main README](../README.md)
- [Architecture Documentation](../architecture.md)
- [Testing Documentation](../testing.md)
