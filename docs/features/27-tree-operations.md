# Tree Operations - Hierarchical Data

Navigate and transform hierarchical data structures like XML, HTML, JSON.

## Overview

Tree operations enable:
- Navigate hierarchical data
- Query with selectors
- Transform subtrees
- Filter nodes
- Path-based access

## Basic Tree Structure

```python
from typing import Any, TypeVar, Generic, Callable
from dataclasses import dataclass
from typing import Protocol

T = TypeVar('T')

@dataclass
class TreeNode:
    """Generic tree node"""

    value: Any
    children: list['TreeNode']

    @classmethod
    def leaf(cls, value: Any) -> 'TreeNode':
        return cls(value, [])

    @classmethod
    def branch(cls, value: Any, *children: 'TreeNode') -> 'TreeNode':
        return cls(value, list(children))

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def depth(self) -> int:
        """Tree depth"""
        if self.is_leaf():
            return 1
        return 1 + max(child.depth() for child in self.children)

    def size(self) -> int:
        """Number of nodes"""
        return 1 + sum(child.size() for child in self.children)


# === Usage ===

tree = TreeNode.branch(
    "root",
    TreeNode.branch("a", TreeNode.leaf("a1"), TreeNode.leaf("a2")),
    TreeNode.branch("b", TreeNode.leaf("b1")),
    TreeNode.leaf("c")
)

print(tree.depth())  # 3
print(tree.size())   # 7
```

## Tree Traversal

```python
class Traverse:
    """Tree traversal strategies"""

    @staticmethod
    def preorder(node: TreeNode) -> list:
        """Root, left, right"""

        result = [node.value]
        for child in node.children:
            result.extend(Traverse.preorder(child))
        return result

    @staticmethod
    def postorder(node: TreeNode) -> list:
        """Left, right, root"""

        result = []
        for child in node.children:
            result.extend(Traverse.postorder(child))
        result.append(node.value)
        return result

    @staticmethod
    def breadth_first(node: TreeNode) -> list:
        """Level by level"""

        result = []
        queue = [node]

        while queue:
            current = queue.pop(0)
            result.append(current.value)
            queue.extend(current.children)

        return result


# === Usage ===

print(Traverse.preorder(tree))
# ['root', 'a', 'a1', 'a2', 'b', 'b1', 'c']

print(Traverse.postorder(tree))
# ['a1', 'a2', 'a', 'b1', 'b', 'c', 'root']

print(Traverse.breadth_first(tree))
# ['root', 'a', 'b', 'c', 'a1', 'a2', 'b1']
```

## Tree Query

```python
class TreeQuery:
    """Query tree nodes"""

    @staticmethod
    def find(node: TreeNode, predicate: Callable) -> TreeNode | None:
        """Find first matching node"""

        if predicate(node.value):
            return node

        for child in node.children:
            result = TreeQuery.find(child, predicate)
            if result:
                return result

        return None

    @staticmethod
    def find_all(node: TreeNode, predicate: Callable) -> list[TreeNode]:
        """Find all matching nodes"""

        results = []

        if predicate(node.value):
            results.append(node)

        for child in node.children:
            results.extend(TreeQuery.find_all(child, predicate))

        return results

    @staticmethod
    def path_to(node: TreeNode, predicate: Callable) -> list | None:
        """Find path to node"""

        if predicate(node.value):
            return [node.value]

        for child in node.children:
            path = TreeQuery.path_to(child, predicate)
            if path:
                return [node.value] + path

        return None


# === Usage ===

# Find node with value 'b1'
b1_node = TreeQuery.find(tree, lambda x: x == 'b1')
print(b1_node.value)  # 'b1'

# Find all leaf nodes
leaves = TreeQuery.find_all(tree, lambda node: node.is_leaf())
print([n.value for n in leaves])  # ['a1', 'a2', 'b1', 'c']

# Find path to 'b1'
path = TreeQuery.path_to(tree, lambda x: x == 'b1')
print(path)  # ['root', 'b', 'b1']
```

## Tree Transformation

```python
class TreeTransform:
    """Transform tree structures"""

    @staticmethod
    def map(node: TreeNode, func: Callable) -> TreeNode:
        """Apply function to all nodes"""

        new_value = func(node.value)
        new_children = [TreeTransform.map(child, func) for child in node.children]

        return TreeNode(new_value, new_children)

    @staticmethod
    def filter(node: TreeNode, predicate: Callable) -> TreeNode | None:
        """Filter nodes (remove subtrees that don't match)"""

        if not predicate(node.value):
            return None

        new_children = []
        for child in node.children:
            filtered = TreeTransform.filter(child, predicate)
            if filtered:
                new_children.append(filtered)

        return TreeNode(node.value, new_children)

    @staticmethod
    def prune(node: TreeNode, predicate: Callable) -> TreeNode:
        """Remove matching nodes"""

        new_children = []
        for child in node.children:
            if predicate(child.value):
                continue
            new_children.append(TreeTransform.prune(child, predicate))

        return TreeNode(node.value, new_children)


# === Usage ===

# Double all values
doubled = TreeTransform.map(tree, lambda x: f"{x}{x}")

# Keep only nodes starting with 'a'
filtered = TreeTransform.filter(tree, lambda x: x.startswith('a'))

# Remove leaf nodes
pruned = TreeTransform.prune(tree, lambda x: isinstance(x, str) and len(x) == 2)
```

## Path-Based Access

```python
from typing import Any

class TreePath:
    """Access tree nodes by path"""

    @staticmethod
    def get(node: TreeNode, path: str, separator: str = ".") -> Any:
        """Get value by path"""

        parts = path.split(separator)
        current = node

        for part in parts:
            # Find child by value or index
            if part.isdigit():
                # By index
                index = int(part)
                if index < len(current.children):
                    current = current.children[index]
                else:
                    return None
            else:
                # By value
                found = False
                for child in current.children:
                    if child.value == part:
                        current = child
                        found = True
                        break
                if not found:
                    return None

        return current.value

    @staticmethod
    def set(node: TreeNode, path: str, value: Any, separator: str = ".") -> TreeNode:
        """Set value by path (returns new tree)"""

        parts = path.split(separator)

        def update(n: TreeNode, depth: int = 0) -> TreeNode:

            if depth >= len(parts):
                return TreeNode(value, n.children)

            part = parts[depth]

            if part.isdigit():
                # Update by index
                index = int(part)
                if index < len(n.children):
                    new_children = n.children.copy()
                    new_children[index] = update(new_children[index], depth + 1)
                    return TreeNode(n.value, new_children)
                return n

            else:
                # Update by value
                new_children = []
                for child in n.children:
                    if child.value == part:
                        new_children.append(update(child, depth + 1))
                    else:
                        new_children.append(child)
                return TreeNode(n.value, new_children)

        return update(node)


# === Usage ===

# Get by path
value = TreePath.get(tree, "a.a1")
print(value)  # 'a1'

# Set by path
new_tree = TreePath.set(tree, "a.a1", "UPDATED")
print(TreePath.get(new_tree, "a.a1"))  # 'UPDATED'
```

## Tree Selection

```python
from typing import Any

class TreeSelector:
    """Select nodes with CSS-like selectors"""

    @staticmethod
    def select(node: TreeNode, selector: str) -> list[TreeNode]:
        """Select nodes by selector"""

        # Simple selector: tag, #id, .class
        results = []

        def matches(n: TreeNode) -> bool:
            value = n.value

            if selector == value:
                return True
            if selector.startswith(".") and isinstance(value, dict):
                return value.get("class") == selector[1:]
            if selector.startswith("#") and isinstance(value, dict):
                return value.get("id") == selector[1:]

            return False

        def traverse(n: TreeNode):
            if matches(n):
                results.append(n)
            for child in n.children:
                traverse(child)

        traverse(node)
        return results

    @staticmethod
    def select_all(node: TreeNode, *selectors: str) -> list[TreeNode]:
        """Select nodes matching any selector"""

        all_results = []

        for selector in selectors:
            results = TreeSelector.select(node, selector)
            all_results.extend(results)

        # Remove duplicates
        seen = set()
        unique = []
        for node in all_results:
            if id(node) not in seen:
                seen.add(id(node))
                unique.append(node)

        return unique


# === Usage ===

html_tree = TreeNode.branch(
    "div",
    TreeNode.branch(
        "p",
        TreeNode.leaf({"tag": "span", "class": "highlight", "text": "Hello"})
    ),
    TreeNode.leaf({"tag": "p", "id": "intro", "text": "World"})
)

# Select by tag
paragraphs = TreeSelector.select(html_tree, "p")

# Select by class
highlighted = TreeSelector.select(html_tree, ".highlight")

# Select by id
intro = TreeSelector.select(html_tree, "#intro")
```

## Tree Reduction

```python
class TreeReduce:
    """Reduce tree to single value"""

    @staticmethod
    def reduce(node: TreeNode, func: Callable, initial: Any) -> Any:
        """Reduce tree with function"""

        accumulator = initial

        def reduce_node(n: TreeNode):
            nonlocal accumulator
            accumulator = func(accumulator, n.value)
            for child in n.children:
                reduce_node(child)

        reduce_node(node)
        return accumulator

    @staticmethod
    def count(node: TreeNode, predicate: Callable) -> int:
        """Count matching nodes"""

        count = 0

        def traverse(n: TreeNode):
            nonlocal count
            if predicate(n.value):
                count += 1
            for child in n.children:
                traverse(child)

        traverse(node)
        return count

    @staticmethod
    def max_depth(node: TreeNode) -> int:
        """Calculate maximum depth"""

        if node.is_leaf():
            return 1

        return 1 + max(TreeReduce.max_depth(child) for child in node.children)

    @staticmethod
    def collect(node: TreeNode) -> list:
        """Collect all values"""

        return TreeReduce.reduce(node, lambda acc, x: acc + [x], [])


# === Usage ===

# Sum all numeric values
total = TreeReduce.reduce(tree, lambda acc, x: acc + (x if isinstance(x, (int, float)) else 0), 0)

# Count matching nodes
count = TreeReduce.count(tree, lambda x: x.startswith('a'))

# Collect all values
all_values = TreeReduce.collect(tree)
```

## DX Benefits

✅ **Flexible**: Works with any tree structure
✅ **Queryable**: Selector-based queries
✅ **Transformable**: Map, filter, prune
✅ **Path-based**: Easy navigation
✅ **Composable**: Chain operations

## Best Practices

```python
# ✅ Good: Specific queries
TreeQuery.find(tree, lambda x: x == 'target')

# ✅ Good: Path-based access
TreePath.get(tree, "users.admin.email")

# ✅ Good: Immutable transforms
new_tree = TreeTransform.map(old_tree, func)

# ❌ Bad: Mutating tree
# Don't modify tree in place
```
