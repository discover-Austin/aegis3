"""
Causal Reasoning

Understand cause-effect relationships beyond correlation.
Support interventions and counterfactuals.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple


@dataclass
class Intervention:
    """An intervention on a variable."""
    variable: str
    value: float


@dataclass
class CausalEdge:
    """A causal edge from cause to effect."""
    cause: str
    effect: str
    strength: float = 1.0  # Causal strength
    discovered_at: int = 0


class CausalGraph:
    """
    Directed acyclic graph representing causal relationships.
    """

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: List[CausalEdge] = []

        # Adjacency list
        self.children: Dict[str, List[str]] = {}
        self.parents: Dict[str, List[str]] = {}

    def add_node(self, node: str):
        """Add a node (variable)."""
        if node not in self.nodes:
            self.nodes.add(node)
            self.children[node] = []
            self.parents[node] = []

    def add_edge(self, cause: str, effect: str, strength: float = 1.0, generation: int = 0):
        """Add causal edge."""
        self.add_node(cause)
        self.add_node(effect)

        # Check for cycles
        if self._would_create_cycle(cause, effect):
            return False

        edge = CausalEdge(cause, effect, strength, generation)
        self.edges.append(edge)

        self.children[cause].append(effect)
        self.parents[effect].append(cause)

        return True

    def _would_create_cycle(self, cause: str, effect: str) -> bool:
        """Check if adding edge would create a cycle."""
        # BFS from effect to see if we can reach cause
        visited = set()
        queue = [effect]

        while queue:
            node = queue.pop(0)
            if node == cause:
                return True

            if node in visited:
                continue

            visited.add(node)

            for child in self.children.get(node, []):
                if child not in visited:
                    queue.append(child)

        return False

    def get_ancestors(self, node: str) -> Set[str]:
        """Get all ancestors (causes) of a node."""
        ancestors = set()
        queue = [node]

        while queue:
            current = queue.pop(0)
            for parent in self.parents.get(current, []):
                if parent not in ancestors:
                    ancestors.add(parent)
                    queue.append(parent)

        return ancestors

    def get_descendants(self, node: str) -> Set[str]:
        """Get all descendants (effects) of a node."""
        descendants = set()
        queue = [node]

        while queue:
            current = queue.pop(0)
            for child in self.children.get(current, []):
                if child not in descendants:
                    descendants.add(child)
                    queue.append(child)

        return descendants

    def d_separated(self, x: str, y: str, z: Set[str]) -> bool:
        """
        Check if X and Y are d-separated given Z.

        (Simplified implementation - full d-separation is complex)
        """
        # Simple check: if all paths from X to Y go through Z, they're d-separated
        # This is a simplification
        ancestors_x = self.get_ancestors(x)
        ancestors_y = self.get_ancestors(y)

        common_ancestors = ancestors_x & ancestors_y

        return len(common_ancestors & z) > 0


class CausalModel:
    """
    Causal model for reasoning about interventions and counterfactuals.
    """

    def __init__(self):
        self.graph = CausalGraph()
        self.observations: List[Dict[str, float]] = []
        self.generation = 0

    def observe(self, observation: Dict[str, float]):
        """Add observation."""
        self.observations.append(observation)

        # Add nodes for any new variables
        for var in observation.keys():
            self.graph.add_node(var)

    def discover_structure(self):
        """
        Discover causal structure from observations.

        (Simplified - real causal discovery is complex)
        """
        if len(self.observations) < 10:
            return  # Need more data

        # For each pair of variables, test for causal relationship
        variables = list(self.graph.nodes)

        for i, var1 in enumerate(variables):
            for var2 in variables[i + 1:]:
                # Test if var1 causes var2
                correlation = self._compute_correlation(var1, var2)

                if abs(correlation) > 0.5:
                    # Significant correlation - could be causal
                    # Try to determine direction using temporal precedence
                    # (simplified - assumes earlier variables cause later ones)

                    if variables.index(var1) < variables.index(var2):
                        self.graph.add_edge(var1, var2, abs(correlation), self.generation)
                    else:
                        self.graph.add_edge(var2, var1, abs(correlation), self.generation)

    def _compute_correlation(self, var1: str, var2: str) -> float:
        """Compute correlation between two variables."""
        values1 = [obs.get(var1, 0) for obs in self.observations]
        values2 = [obs.get(var2, 0) for obs in self.observations]

        if not values1 or not values2:
            return 0.0

        # Pearson correlation (simplified)
        mean1 = sum(values1) / len(values1)
        mean2 = sum(values2) / len(values2)

        numerator = sum((v1 - mean1) * (v2 - mean2)
                        for v1, v2 in zip(values1, values2))
        denominator1 = sum((v1 - mean1) ** 2 for v1 in values1) ** 0.5
        denominator2 = sum((v2 - mean2) ** 2 for v2 in values2) ** 0.5

        if denominator1 == 0 or denominator2 == 0:
            return 0.0

        return numerator / (denominator1 * denominator2)

    def intervene(self, intervention: Intervention) -> Dict[str, float]:
        """
        Perform intervention (do-operator).

        Returns predicted outcomes under intervention.
        """
        # Intervention removes incoming edges to intervened variable
        # Predict outcomes using causal graph

        result = {intervention.variable: intervention.value}

        # Propagate effects to descendants
        descendants = self.graph.get_descendants(intervention.variable)

        for desc in descendants:
            # Simple linear causal effect (simplified)
            value = 0.0
            for edge in self.graph.edges:
                if edge.effect == desc:
                    cause_value = result.get(edge.cause, 0)
                    value += edge.strength * cause_value

            result[desc] = value

        return result

    def counterfactual(
        self,
        observation: Dict[str, float],
        intervention: Intervention
    ) -> Dict[str, float]:
        """
        Counterfactual reasoning: What if X had been Y instead?

        Returns counterfactual outcomes.
        """
        # Step 1: Abduction - infer latent variables from observation
        # Step 2: Action - apply intervention
        # Step 3: Prediction - predict under intervention

        # Simplified implementation
        cf_world = observation.copy()
        cf_world[intervention.variable] = intervention.value

        # Propagate changes
        descendants = self.graph.get_descendants(intervention.variable)

        for desc in descendants:
            # Recompute value based on new parent values
            value = 0.0
            for edge in self.graph.edges:
                if edge.effect == desc:
                    cause_value = cf_world.get(edge.cause, observation.get(edge.cause, 0))
                    value += edge.strength * cause_value

            cf_world[desc] = value

        return cf_world

    def find_confounders(self, treatment: str, outcome: str) -> Set[str]:
        """Find confounding variables for treatment-outcome relationship."""
        # Confounders are common causes of treatment and outcome
        treatment_ancestors = self.graph.get_ancestors(treatment)
        outcome_ancestors = self.graph.get_ancestors(outcome)

        confounders = treatment_ancestors & outcome_ancestors

        return confounders

    def get_statistics(self) -> Dict[str, Any]:
        """Get causal model statistics."""
        return {
            'num_variables': len(self.graph.nodes),
            'num_causal_edges': len(self.graph.edges),
            'num_observations': len(self.observations),
            'generation': self.generation
        }
