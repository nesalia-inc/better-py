# Documentation Writing Guide

This guide explains how to write clear, human-friendly documentation for better-py. Our goal is to educate users, not just list APIs.

## Core Philosophy

**We teach concepts, not just document features.**

Users should understand:
- **Why** something exists (the problem it solves)
- **When** to use it (appropriate use cases)
- **How** it works (mental models)
- **What** the API looks like (code examples)

Good documentation feels like a knowledgeable developer sitting next to you, explaining concepts. Bad documentation feels like a robot reading from a specification.

## Writing Style

### 1. Prose Over Lists

**❌ Avoid: Excessive bullet points**

```markdown
## Creating Maybe Values

### Maybe.some()
- Wrap a value that exists
- Takes one parameter
- Returns Some(value)

### Maybe.nothing()
- Represents absence
- Takes no parameters
- Returns Nothing
```

**✅ Prefer: Explanatory paragraphs**

```markdown
## Creating Maybe Values

Maybe provides several ways to represent optional values in your code. The most common approach is to explicitly wrap a value that exists, or represent its absence when a value is missing. This makes your intent clear and helps avoid null pointer errors.

### Creating a value that exists

Use `Maybe.some()` to wrap a value that you know exists:

```python
user = Maybe.some({"id": 1, "name": "Alice"})
```

### Representing absence

When a value is missing, use `Maybe.nothing()` to explicitly represent this state:

```python
empty = Maybe.nothing()
```
```

**Why:** Paragraphs flow naturally and explain concepts. Lists are for enumerating items, not explaining ideas.

---

### 2. Explain Before You Show Code

**❌ Avoid: Code-first approach**

```markdown
## map()

Transform the value inside:

```python
Maybe.some(5).map(lambda x: x * 2)
# Maybe(10)
```

## bind()

Chain operations:

```python
Maybe.some(5).bind(lambda x: Maybe.some(x * 2))
# Maybe(10)
```
```

**✅ Prefer: Concept-first approach**

```markdown
## Transforming Values

When you have a Maybe value and want to transform its contents, use `map()`. This applies a function to the value inside the Maybe wrapper, preserving the optional nature of the result. If the Maybe is `Nothing`, the transformation is skipped and `Nothing` is returned.

```python
Maybe.some(5).map(lambda x: x * 2)
# Returns: Maybe(10)

Maybe.nothing().map(lambda x: x * 2)
# Returns: Nothing
```

## Chaining Optional Operations

Sometimes you need to chain operations that themselves return Maybe values. For example, looking up a user might return Maybe[User], and then fetching their profile might return Maybe[Profile]. In these cases, use `bind()` (also called `and_then`) to flatten the nested results.

```python
find_user(id).bind(lambda user: get_profile(user))
# Returns: Maybe[Profile]
```
```

**Why:** Users need mental models before they can understand code. Explain the concept first, then show the implementation.

---

### 3. Build Mental Models with Analogies

Analogies help users grasp abstract concepts. Use them consistently and explain them clearly.

**Example: The Box Analogy**

```markdown
## What is Maybe?

Think of Maybe as a box that might contain something or might be empty. When you have a regular Python value, it's like holding the object directly - it could be there, or it could be `None`, and you won't know until you try to use it.

Maybe puts the value inside a protective box. This box has two states:

- **Some**: The box contains a value
- **Nothing**: The box is empty

Every operation with Maybe acknowledges this uncertainty. You can't directly access what's inside without checking first, which forces you to handle both cases.

This is different from a simple `None` check because the type system knows the value is optional. Your code won't even compile (in typed Python) if you forget to handle the empty case.
```

**Guidelines for analogies:**
- Choose one primary analogy per concept and stick to it
- Explain the analogy clearly before using it
- Acknowledge when the analogy breaks down
- Real-world examples work best (boxes, gift wrapping, pipelines, etc.)

---

### 4. Use Narrative Structure

Organize content to tell a story: problem → solution → application.

**❌ Avoid: Random order**

```markdown
## Maybe API

### Creating
Maybe.some()
Maybe.nothing()

### Inspecting
is_some()
is_nothing()

### Extracting
unwrap()
unwrap_or()

### Transforming
map()
bind()
```

**✅ Prefer: Narrative flow**

```markdown
## Working with Maybe

Maybe follows a natural workflow: create a value, inspect it, transform it, and eventually extract the result.

### Creating Maybe Values

Start by wrapping your values...

[creation examples]

### Inspecting Maybe

Before doing anything with a Maybe value, you'll want to check...

[inspection examples]

### Transforming Values

Once you know a value exists, you can transform it...

[transformation examples]

### Extracting the Final Value

When you need to get the value out of the Maybe wrapper...

[extraction examples]
```

**Why:** Humans learn through stories. Guide users through a logical progression.

---

### 5. Show Real-World Context

**❌ Avoid: Abstract examples only**

```python
# Abstract
Maybe.some(42).map(lambda x: x * 2)
```

**✅ Prefer: Real-world scenarios**

```python
# Real: Finding a user's email
def get_user_email(user_id: int) -> Maybe[str]:
    return (
        find_user(user_id)
        .map(lambda user: user.email)
        .filter(lambda email: "@" in email)
    )

# This reads like English: "find user, get their email, keep it if valid"
```

**Guidelines:**
- Start with simple abstract examples to teach the concept
- Follow with realistic examples that show actual use cases
- Show problems users actually encounter (database queries, API calls, form validation)
- Use realistic variable names (`user`, `email`, `config`) not abstract ones (`x`, `y`, `foo`)

---

### 6. Comparison Sections

When users need to choose between options, use structured comparison sections.

```markdown
## map vs bind: When to Use Which

Both `map()` and `bind()` transform Maybe values, but they serve different purposes:

### Use map() when: Your function returns a regular value

```python
Maybe.some(5).map(lambda x: x * 2)
# Function returns int, so map is appropriate
```

### Use bind() when: Your function returns another Maybe

```python
Maybe.some(5).bind(lambda x: Maybe.some(x * 2))
# Function returns Maybe, so bind flattens the result
```

### Why the distinction matters

Using `map()` with a function that returns Maybe creates nested `Maybe[Maybe[int]]`, which is awkward to work with. The `bind()` method flattens this structure, keeping your code clean.

| Operation | Input Function | Result |
|-----------|---------------|---------|
| `map()` | `T → U` | `Maybe[T] → Maybe[U]` |
| `bind()` | `T → Maybe[U]` | `Maybe[T] → Maybe[U]` |
```

---

### 7. "Good to Know" Sections

Add practical notes that don't fit in the main flow but are important:

```markdown
## Extracting Values

[main explanation about unwrap() and unwrap_or()]

<Callout type="info" title="Good to know">

The `unwrap()` method will raise an exception if called on `Nothing`. Only use it when you're absolutely certain the value exists (for example, after checking `is_some()`). For safer extraction, prefer `unwrap_or()`.

</Callout>

<Callout type="warning" title="Warning">

Don't use `unwrap()` in library code - it forces your users to handle exceptions. Return the Maybe value instead and let them decide how to extract it safely.

</Callout>
```

---

### 8. Common Mistakes Section

Help users avoid pitfalls:

```markdown
## Common Mistakes

### Mistake 1: Unwrapping too early

```python
# DON'T
def get_user_name(user_id: int) -> str:
    user = find_user(user_id).unwrap()  # Crashes if user not found!
    return user.name

# DO
def get_user_name(user_id: int) -> Maybe[str]:
    return find_user(user_id).map(lambda user: user.name)
```

Unwrapping destroys the safety that Maybe provides. Keep values wrapped until you absolutely need them.

### Mistake 2: Ignoring the Nothing case

```python
# DON'T
maybe_value = get_config(key)
value = maybe_value.unwrap_or(default)
process(value)  # Always processes, even when value is default

# DO
maybe_value = get_config(key)
if maybe_value.is_some():
    process(maybe_value.unwrap())
```
```

---

### 9. Anti-Patterns Section

Be honest about when NOT to use your tool:

```markdown
## When NOT to Use Maybe

Maybe is a powerful tool, but it's not always the right choice:

### Simple if/else is clearer

```python
# Maybe is overkill here
value = Maybe.from_value(config.get("key"))
if value.is_some():
    use(value.unwrap())

# Just use if/else
if "key" in config:
    use(config["key"])
```

### Performance-critical code

Maybe adds a small overhead. In tight loops or performance-critical sections, direct null checks may be faster.

### Working with non-FP code

When interfacing with libraries that expect `None`, using Maybe requires constant conversion. Sometimes it's better to work with the library's conventions.

```

---

### 10. Progressive Complexity

Start simple, gradually add complexity:

```markdown
## Pattern Matching with Maybe

Python 3.10+ introduced structural pattern matching, which works beautifully with Maybe.

### Basic pattern matching

The simplest case is checking whether a value exists:

```python
match maybe_value:
    case Some(value):
        print(f"Got: {value}")
    case Nothing():
        print("No value")
```

### Pattern matching with conditions

You can add guards to filter values:

```python
match maybe_value:
    case Some(value) if value > 0:
        print(f"Positive: {value}")
    case Some(value):
        print(f"Non-positive: {value}")
    case Nothing():
        print("No value")
```

### Nested pattern matching

When working with nested Maybe values:

```python
match result:
    case Some(Some(inner_value)):
        print(f"Nested: {inner_value}")
    case Some(Nothing()):
        print("Outer exists, inner empty")
    case Nothing():
        print("Outer empty")
```
```

---

## Section Templates

### Concept Introduction Page

```markdown
# [Concept Name]

[One or two paragraphs explaining what the concept is and why it exists. Use simple language. Build a mental model.]

## When to Use [Concept]

[Bulleted list of appropriate use cases, but each bullet should be a complete thought, not just two words.]

<Callout type="success" title="Use [Concept] when:">

- [Use case 1: Explanation]
- [Use case 2: Explanation]
- [Use case 3: Explanation]

</Callout>

## How [Concept] Works

[Several paragraphs explaining the mechanics. Use analogies. Include diagrams if helpful.]

## Basic Usage

[Start with simple examples. Explain each step.]

## Common Patterns

[Show realistic usage patterns. Each pattern should have a heading explaining what problem it solves.]

### Pattern 1: [Descriptive Name]

[Paragraph explaining the pattern and why it's useful.]

```python
[code example]
```

## Common Mistakes

[Section showing mistakes users make and how to avoid them.]

## When NOT to Use [Concept]

[Be honest about limitations. This builds trust.]

## See Also

[Links to related concepts.]
```

### API Reference Page

```markdown
# [Class/Function Name]

[One paragraph explaining what this does and when you'd use it.]

## Signature

```python
[type signature]
```

## Parameters

[Table or paragraphs explaining each parameter.]

## Returns

[Explanation of return value and what it means.]

## Examples

### Basic example

[Simple example with explanation.]

### Real-world example

[Realistic use case with explanation.]

## Common Use Cases

[Several paragraphs explaining when this function is particularly useful.]

## Related

[Links to related APIs.]
```

---

## Voice and Tone

- **Conversational but professional**: Write like you're explaining to a colleague
- **Encouraging**: Acknowledge that functional programming can be challenging
- **Honest**: Admit limitations and trade-offs
- **Precise**: Use correct terminology, but explain it first
- **Active voice**: "Use `map()` to transform" not "`map()` can be used to transform"
- **Second person**: Address the reader directly ("you", "your")

---

## Formatting Guidelines

### Code Examples

- Always show imports
- Use realistic variable names
- Include comments explaining non-obvious parts
- Show the output when it's not immediately obvious
- Prefer complete, runnable examples over snippets

### Callouts/Alerts

Use Callout components strategically:

- **info**: Additional context, tips, clarification
- **success**: Best practices, recommended approaches
- **warning**: Potential pitfalls, breaking changes
- **error**: Common mistakes, dangerous patterns

Don't overuse them. If everything is highlighted, nothing is.

### Headings

- Use descriptive headings that tell a story
- Avoid generic headings like "Introduction" or "Overview"
- Prefer action-oriented headings: "Creating Values", "Transforming Data", "Handling Errors"

---

## Review Checklist

Before publishing documentation, ask:

- [ ] Does each section start with explanatory prose?
- [ ] Are code examples preceded by explanations?
- [ ] Do I explain WHY before showing HOW?
- [ ] Are analogies explained before being used?
- [ ] Do examples progress from simple to complex?
- [ ] Is there at least one real-world example?
- [ ] Did I include common mistakes?
- [ ] Did I honestly discuss when NOT to use this feature?
- [ ] Is the tone conversational and encouraging?
- [ ] Would a beginner understand this after reading once?

---

## Examples of Good Documentation

Study these examples for inspiration:

- [Next.js Documentation](https://nextjs.org/docs) - Excellent use of prose, examples, and progressive complexity
- [Rust Book](https://doc.rust-lang.org/book/) - Masterful use of analogies and narrative
- [React Documentation](https://react.dev/) - Clear explanations with interactive examples
- [Django Documentation](https://docs.djangoproject.com/) - Comprehensive yet approachable

Notice how they all:
- Start with concepts, not APIs
- Use paragraphs to explain, lists to enumerate
- Show real examples
- Build mental models progressively
- Are honest about trade-offs
```

---

## Summary

**Good documentation is taught, not listed.**

- Write in paragraphs, not bullet points
- Explain concepts before showing code
- Build mental models with analogies
- Tell a story with a clear narrative
- Show real-world examples
- Admit limitations and trade-offs
- Be a helpful human, not a robot

Your goal is to help users understand functional programming concepts, not just memorize APIs. When in doubt, ask yourself: "Would I explain this to a colleague over coffee?" Write that way.
