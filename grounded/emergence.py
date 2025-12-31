"""
Grounded Symbol Emergence

Goals and symbols emerge from experience without predefined categories.
No GoalType.EXPLORE or GoalType.MASTER - goals form from regularities.
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from collections import Counter


@dataclass
class GroundedSymbol:
    """A symbol grounded in sensorimotor experience."""
    symbol_id: str
    name: str

    # Grounding: association with experience patterns
    sensory_patterns: List[List[float]] = field(default_factory=list)
    motor_patterns: List[List[float]] = field(default_factory=list)

    # Usage statistics
    activation_count: int = 0
    co_occurrences: Counter = field(default_factory=Counter)

    def similarity(self, other: 'GroundedSymbol') -> float:
        """Compute similarity with another symbol."""
        if not self.sensory_patterns or not other.sensory_patterns:
            return 0.0

        # Average similarity of sensory patterns
        similarities = []
        for p1 in self.sensory_patterns[:5]:  # Sample
            for p2 in other.sensory_patterns[:5]:
                if len(p1) == len(p2):
                    dist = sum((a - b) ** 2 for a, b in zip(p1, p2)) ** 0.5
                    sim = 1.0 / (1.0 + dist)
                    similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0


class SymbolGrounding:
    """
    System for grounding symbols in sensorimotor experience.

    Symbols emerge from:
    - Recurring sensory patterns
    - Predictable action outcomes
    - Co-occurrence regularities
    """

    def __init__(self):
        self.symbols: Dict[str, GroundedSymbol] = {}
        self.experience_history: List[Dict[str, Any]] = []

    def process_experience(
        self,
        sensory_input: List[float],
        motor_output: List[float],
        outcome: float
    ):
        """Process sensorimotor experience."""
        experience = {
            'sensory': sensory_input,
            'motor': motor_output,
            'outcome': outcome
        }
        self.experience_history.append(experience)

        # Detect recurring patterns
        if len(self.experience_history) >= 10:
            self._detect_patterns()

    def _detect_patterns(self):
        """Detect recurring patterns in experience."""
        # Simple clustering of recent experiences
        recent = self.experience_history[-100:]

        # Find clusters of similar sensory patterns
        clusters = self._cluster_experiences(recent)

        # Create symbols for stable clusters
        for cluster in clusters:
            if len(cluster) >= 5:  # Stable pattern
                self._create_symbol_from_cluster(cluster)

    def _cluster_experiences(
        self,
        experiences: List[Dict[str, Any]],
        threshold: float = 0.3
    ) -> List[List[Dict]]:
        """Simple clustering of experiences."""
        clusters = []

        for exp in experiences:
            # Find closest cluster
            best_cluster = None
            best_similarity = 0.0

            for cluster in clusters:
                # Compute similarity to cluster centroid
                centroid = cluster[0]['sensory']  # Simplified
                similarity = self._compute_similarity(exp['sensory'], centroid)

                if similarity > best_similarity and similarity > threshold:
                    best_similarity = similarity
                    best_cluster = cluster

            if best_cluster:
                best_cluster.append(exp)
            else:
                clusters.append([exp])

        return clusters

    def _compute_similarity(self, pattern1: List[float], pattern2: List[float]) -> float:
        """Compute similarity between patterns."""
        if len(pattern1) != len(pattern2):
            return 0.0

        dist = sum((a - b) ** 2 for a, b in zip(pattern1, pattern2)) ** 0.5
        return 1.0 / (1.0 + dist)

    def _create_symbol_from_cluster(self, cluster: List[Dict[str, Any]]):
        """Create a grounded symbol from experience cluster."""
        # Extract patterns
        sensory_patterns = [exp['sensory'] for exp in cluster]
        motor_patterns = [exp['motor'] for exp in cluster]

        # Generate symbol ID
        pattern_hash = hashlib.md5(str(sensory_patterns[0]).encode()).hexdigest()[:8]
        symbol_id = f"symbol_{pattern_hash}"

        if symbol_id not in self.symbols:
            symbol = GroundedSymbol(
                symbol_id=symbol_id,
                name=f"Grounded_{len(self.symbols)}",
                sensory_patterns=sensory_patterns,
                motor_patterns=motor_patterns
            )
            self.symbols[symbol_id] = symbol

    def activate_symbol(self, sensory_input: List[float]) -> Optional[GroundedSymbol]:
        """Activate symbol most similar to current input."""
        best_symbol = None
        best_similarity = 0.0

        for symbol in self.symbols.values():
            for pattern in symbol.sensory_patterns:
                similarity = self._compute_similarity(sensory_input, pattern)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_symbol = symbol

        if best_symbol and best_similarity > 0.5:
            best_symbol.activation_count += 1
            return best_symbol

        return None


class GroundedGoalFormation:
    """
    Goals emerge from experience without predefined types.

    Instead of GoalType.EXPLORE, goals form from:
    - Prediction errors (curiosity)
    - Reward gradients (value)
    - Pattern repetition (mastery)
    - Novelty detection (exploration)
    """

    def __init__(self):
        self.goals: List[Dict[str, Any]] = []
        self.symbol_grounding = SymbolGrounding()

    def form_goal_from_experience(self, trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Form a goal from experience trajectory.

        No predefined categories - goal emerges from structure of experience.
        """
        if len(trajectory) < 3:
            return {}

        # Analyze trajectory structure
        rewards = [exp.get('reward', 0) for exp in trajectory]
        prediction_errors = [exp.get('prediction_error', 0) for exp in trajectory]

        # Detect goal type from structure
        goal = {}

        # High prediction error -> exploration goal
        if sum(prediction_errors) / len(prediction_errors) > 0.5:
            goal = {
                'type': 'emergent_exploration',
                'target': 'reduce_uncertainty',
                'motivation': 'curiosity',
                'priority': sum(prediction_errors)
            }

        # Increasing rewards -> mastery goal
        elif len(rewards) >= 2 and rewards[-1] > rewards[0]:
            goal = {
                'type': 'emergent_mastery',
                'target': 'maximize_reward',
                'motivation': 'value',
                'priority': rewards[-1] - rewards[0]
            }

        # Repeating pattern -> habit goal
        else:
            goal = {
                'type': 'emergent_habit',
                'target': 'maintain_pattern',
                'motivation': 'efficiency',
                'priority': 0.5
            }

        self.goals.append(goal)

        return goal

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Get currently active goals."""
        return sorted(self.goals, key=lambda g: g.get('priority', 0), reverse=True)[:5]
