"""
Compositional Reasoning Tasks

Test ability to:
- Compose simple functions into complex behaviors
- Discover and reuse abstract patterns
- Build hierarchical solutions
"""

import random
import math
from typing import List, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class CompositionExample:
    """Example of a compositional problem."""
    inputs: List[float]
    expected_output: float
    composition_depth: int  # How many primitive operations needed


class CompositionalReasoningTask(ABC):
    """
    Base class for compositional reasoning tasks.

    Tests whether agent can discover that complex functions
    are compositions of simpler primitives.
    """

    def __init__(self, difficulty: float = 0.5):
        self.difficulty = difficulty
        self.primitives = self._get_primitives()
        self.examples: List[CompositionExample] = []

    @abstractmethod
    def _get_primitives(self) -> Dict[str, Callable]:
        """Get available primitive operations."""
        pass

    @abstractmethod
    def generate_target_function(self) -> Callable:
        """Generate a target function to learn."""
        pass

    def evaluate_composition(self, proposed_fn: Callable, num_tests: int = 20) -> float:
        """
        Evaluate how well proposed function matches target.

        Returns score 0-1.
        """
        if not self.examples:
            self.examples = self._generate_examples(num_tests)

        correct = 0
        for example in self.examples:
            try:
                output = proposed_fn(example.inputs)
                if abs(output - example.expected_output) < 0.1:
                    correct += 1
            except:
                pass

        return correct / len(self.examples)

    def _generate_examples(self, num: int) -> List[CompositionExample]:
        """Generate training examples."""
        target_fn = self.generate_target_function()
        examples = []

        for _ in range(num):
            # Generate random inputs
            num_inputs = random.randint(1, 5)
            inputs = [random.uniform(-10, 10) for _ in range(num_inputs)]

            try:
                output = target_fn(inputs)
                examples.append(CompositionExample(
                    inputs=inputs,
                    expected_output=output,
                    composition_depth=self._estimate_depth()
                ))
            except:
                pass

        return examples

    def _estimate_depth(self) -> int:
        """Estimate composition depth based on difficulty."""
        return int(1 + self.difficulty * 5)


class FunctionCompositionTask(CompositionalReasoningTask):
    """
    Task: Learn function that is composition of primitives.

    Example: f(x) = sin(x² + 1) = compose(sin, add(square, const_1))

    Tests hierarchical composition ability.
    """

    def _get_primitives(self) -> Dict[str, Callable]:
        """Mathematical primitives."""
        return {
            'identity': lambda x: x[0] if x else 0,
            'square': lambda x: x[0] ** 2 if x else 0,
            'sqrt': lambda x: abs(x[0]) ** 0.5 if x else 0,
            'sin': lambda x: math.sin(x[0]) if x else 0,
            'cos': lambda x: math.cos(x[0]) if x else 0,
            'exp': lambda x: min(100, math.exp(min(10, x[0]))) if x else 0,
            'log': lambda x: math.log(max(0.01, abs(x[0]))) if x else 0,
            'add': lambda x: x[0] + x[1] if len(x) >= 2 else 0,
            'multiply': lambda x: x[0] * x[1] if len(x) >= 2 else 0,
            'negate': lambda x: -x[0] if x else 0,
        }

    def generate_target_function(self) -> Callable:
        """Generate target as composition of primitives."""
        depth = self._estimate_depth()

        # Build random composition tree
        def build_composition(current_depth: int) -> Callable:
            if current_depth == 0:
                # Leaf: identity or constant
                return lambda x: x[0] if x else random.random()

            # Pick random primitive
            prim_name = random.choice(list(self.primitives.keys()))
            prim = self.primitives[prim_name]

            # Unary or binary
            if prim_name in ['add', 'multiply']:
                # Binary: compose two sub-functions
                left = build_composition(current_depth - 1)
                right = build_composition(current_depth - 1)
                return lambda x: prim([left(x), right(x)])
            else:
                # Unary: compose one sub-function
                sub = build_composition(current_depth - 1)
                return lambda x: prim([sub(x)])

        return build_composition(depth)


class StructuralAbstractionTask:
    """
    Task: Discover abstract patterns in data structures.

    Example: Given trees, discover "depth" or "balance" as concepts.

    Tests ability to form abstractions.
    """

    def __init__(self, difficulty: float = 0.5):
        self.difficulty = difficulty
        self.structures: List[Dict[str, Any]] = []
        self.target_property = self._select_target_property()

    def _select_target_property(self) -> str:
        """Select which structural property to learn."""
        properties = [
            'depth',           # Tree depth
            'branching_factor', # Average children per node
            'symmetry',        # Structural symmetry
            'density',         # Ratio of edges to nodes
            'diameter',        # Longest path
        ]
        return random.choice(properties)

    def generate_structure(self) -> Dict[str, Any]:
        """Generate random tree structure."""
        num_nodes = random.randint(3, 15)

        # Build tree as adjacency list
        tree = {
            'nodes': list(range(num_nodes)),
            'edges': [],
            'root': 0
        }

        # Add edges (parent -> children)
        for node in range(1, num_nodes):
            parent = random.randint(0, node - 1)
            tree['edges'].append((parent, node))

        return tree

    def compute_property(self, structure: Dict[str, Any]) -> float:
        """Compute target property value."""
        if self.target_property == 'depth':
            return self._compute_depth(structure)
        elif self.target_property == 'branching_factor':
            return self._compute_branching_factor(structure)
        elif self.target_property == 'symmetry':
            return self._compute_symmetry(structure)
        elif self.target_property == 'density':
            return self._compute_density(structure)
        elif self.target_property == 'diameter':
            return self._compute_diameter(structure)
        else:
            return 0.0

    def _compute_depth(self, structure: Dict[str, Any]) -> float:
        """Compute tree depth."""
        if not structure['edges']:
            return 1.0

        # Build adjacency list
        children = {}
        for parent, child in structure['edges']:
            if parent not in children:
                children[parent] = []
            children[parent].append(child)

        def depth(node):
            if node not in children:
                return 1
            return 1 + max(depth(c) for c in children[node])

        return float(depth(structure['root']))

    def _compute_branching_factor(self, structure: Dict[str, Any]) -> float:
        """Average number of children per node."""
        if not structure['nodes']:
            return 0.0

        children_count = {}
        for parent, _ in structure['edges']:
            children_count[parent] = children_count.get(parent, 0) + 1

        if not children_count:
            return 0.0

        return sum(children_count.values()) / len(structure['nodes'])

    def _compute_symmetry(self, structure: Dict[str, Any]) -> float:
        """Measure structural symmetry (0-1)."""
        # Simple heuristic: ratio of balanced to total nodes
        children = {}
        for parent, child in structure['edges']:
            if parent not in children:
                children[parent] = []
            children[parent].append(child)

        def is_balanced(node):
            if node not in children:
                return True
            child_list = children[node]
            if len(child_list) <= 1:
                return True
            # Check if children have similar subtree sizes
            sizes = [subtree_size(c) for c in child_list]
            if not sizes:
                return True
            avg = sum(sizes) / len(sizes)
            variance = sum((s - avg) ** 2 for s in sizes) / len(sizes)
            return variance < 2.0

        def subtree_size(node):
            if node not in children:
                return 1
            return 1 + sum(subtree_size(c) for c in children[node])

        balanced_count = sum(1 for n in structure['nodes'] if is_balanced(n))
        return balanced_count / len(structure['nodes'])

    def _compute_density(self, structure: Dict[str, Any]) -> float:
        """Edge to node ratio."""
        if not structure['nodes']:
            return 0.0
        return len(structure['edges']) / len(structure['nodes'])

    def _compute_diameter(self, structure: Dict[str, Any]) -> float:
        """Longest path in tree."""
        if not structure['edges']:
            return 1.0

        # Build adjacency (undirected for diameter)
        adj = {}
        for u, v in structure['edges']:
            if u not in adj:
                adj[u] = []
            if v not in adj:
                adj[v] = []
            adj[u].append(v)
            adj[v].append(u)

        def farthest(start):
            visited = {start}
            queue = [(start, 0)]
            max_dist = 0
            farthest_node = start

            while queue:
                node, dist = queue.pop(0)
                if dist > max_dist:
                    max_dist = dist
                    farthest_node = node

                if node in adj:
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, dist + 1))

            return farthest_node, max_dist

        # Find diameter: farthest from any node, then farthest from that
        node1, _ = farthest(structure['root'])
        _, diameter = farthest(node1)

        return float(diameter)

    def evaluate_abstraction(
        self,
        abstraction_fn: Callable[[Dict[str, Any]], float],
        num_tests: int = 20
    ) -> float:
        """
        Evaluate how well abstraction function captures target property.

        Returns score 0-1.
        """
        errors = []

        for _ in range(num_tests):
            structure = self.generate_structure()
            true_value = self.compute_property(structure)

            try:
                predicted_value = abstraction_fn(structure)
                error = abs(predicted_value - true_value)
                errors.append(error)
            except:
                errors.append(float('inf'))

        if not errors:
            return 0.0

        # Score based on average error
        avg_error = sum(min(e, 10) for e in errors) / len(errors)
        score = max(0.0, 1.0 - avg_error / 10.0)

        return score


class RecursiveDecompositionTask:
    """
    Task: Decompose problem recursively into subproblems.

    Example: Compute fibonacci by recognizing recursive structure.

    Tests ability to discover recursive patterns.
    """

    def __init__(self, difficulty: float = 0.5):
        self.difficulty = difficulty
        self.problem_type = self._select_problem_type()

    def _select_problem_type(self) -> str:
        """Select type of recursive problem."""
        types = [
            'fibonacci',
            'factorial',
            'ackermann',
            'tower_of_hanoi',
            'catalan'
        ]
        return random.choice(types)

    def get_target_function(self) -> Callable[[int], int]:
        """Get the target recursive function."""
        if self.problem_type == 'fibonacci':
            def fib(n):
                if n <= 1:
                    return n
                return fib(n - 1) + fib(n - 2)
            return fib

        elif self.problem_type == 'factorial':
            def fact(n):
                if n <= 1:
                    return 1
                return n * fact(n - 1)
            return fact

        elif self.problem_type == 'ackermann':
            def ack(m, n=2):
                if m == 0:
                    return n + 1
                if n == 0:
                    return ack(m - 1, 1)
                return ack(m - 1, ack(m, n - 1))
            return lambda x: ack(min(x, 3), 2)

        elif self.problem_type == 'tower_of_hanoi':
            def hanoi(n):
                if n == 1:
                    return 1
                return 2 * hanoi(n - 1) + 1
            return hanoi

        elif self.problem_type == 'catalan':
            def catalan(n):
                if n <= 1:
                    return 1
                result = 0
                for i in range(n):
                    result += catalan(i) * catalan(n - 1 - i)
                return result
            return catalan

        else:
            return lambda n: n

    def evaluate_recursion(
        self,
        proposed_fn: Callable[[int], int],
        num_tests: int = 10
    ) -> float:
        """
        Evaluate if proposed function matches recursive pattern.

        Returns score 0-1.
        """
        target_fn = self.get_target_function()
        correct = 0

        for n in range(num_tests):
            try:
                expected = target_fn(n)
                actual = proposed_fn(n)

                if abs(expected - actual) < 0.001:
                    correct += 1
            except:
                pass

        return correct / num_tests
