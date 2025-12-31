"""
Attention/Salience Mechanism

Determines what to focus on in high-dimensional sensory input.
Learns what features are important.
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class SalienceMap:
    """Map of attention weights over input dimensions."""
    weights: List[float] = field(default_factory=list)
    dim: int = 0

    def __post_init__(self):
        if not self.weights and self.dim > 0:
            # Uniform attention initially
            self.weights = [1.0 / self.dim] * self.dim

    def attend(self, input_vector: List[float]) -> List[float]:
        """Apply attention to input."""
        if len(input_vector) != len(self.weights):
            return input_vector  # Dimension mismatch

        return [inp * weight for inp, weight in zip(input_vector, self.weights)]

    def normalize(self):
        """Normalize weights to sum to 1."""
        total = sum(self.weights)
        if total > 0:
            self.weights = [w / total for w in self.weights]

    def top_k(self, k: int) -> List[int]:
        """Get indices of top-k attended dimensions."""
        indexed = [(i, w) for i, w in enumerate(self.weights)]
        indexed.sort(key=lambda x: x[1], reverse=True)
        return [i for i, _ in indexed[:k]]


class AttentionMechanism:
    """
    Learnable attention mechanism.

    Features:
    - Bottom-up salience (data-driven)
    - Top-down attention (goal-driven)
    - Adaptive learning
    """

    def __init__(self, input_dim: int, context_dim: int = 10):
        self.input_dim = input_dim
        self.context_dim = context_dim

        # Bottom-up salience (based on input statistics)
        self.bottom_up = SalienceMap(dim=input_dim)

        # Top-down attention (based on task/goal)
        self.top_down = SalienceMap(dim=input_dim)

        # Combined attention
        self.combined = SalienceMap(dim=input_dim)

        # Learning history
        self.attention_history: List[List[float]] = []

    def attend(
        self,
        input_vector: List[float],
        context: Optional[List[float]] = None
    ) -> List[float]:
        """
        Apply attention to input.

        Args:
            input_vector: Input to attend to
            context: Task/goal context (optional)

        Returns:
            Attended input
        """
        # Update bottom-up salience based on input
        self._update_bottom_up(input_vector)

        # Update top-down attention based on context
        if context:
            self._update_top_down(context)

        # Combine bottom-up and top-down
        self._combine_attention()

        # Apply attention
        attended = self.combined.attend(input_vector)

        # Record
        self.attention_history.append(self.combined.weights.copy())

        return attended

    def _update_bottom_up(self, input_vector: List[float]):
        """Update bottom-up salience based on input statistics."""
        # Salience based on magnitude and variance
        for i, val in enumerate(input_vector):
            if i < len(self.bottom_up.weights):
                # Exponential moving average
                alpha = 0.1
                magnitude_salience = abs(val)
                self.bottom_up.weights[i] = (
                    alpha * magnitude_salience +
                    (1 - alpha) * self.bottom_up.weights[i]
                )

        self.bottom_up.normalize()

    def _update_top_down(self, context: List[float]):
        """Update top-down attention based on context."""
        # Context influences which dimensions to attend to
        # Simple approach: use context to modulate attention

        for i in range(min(len(context), len(self.top_down.weights))):
            # Context values influence corresponding attention weights
            self.top_down.weights[i] = abs(context[i])

        self.top_down.normalize()

    def _combine_attention(self, bottom_up_weight: float = 0.5):
        """Combine bottom-up and top-down attention."""
        top_down_weight = 1.0 - bottom_up_weight

        for i in range(self.input_dim):
            self.combined.weights[i] = (
                bottom_up_weight * self.bottom_up.weights[i] +
                top_down_weight * self.top_down.weights[i]
            )

        self.combined.normalize()

    def learn_attention(self, reward_signal: float):
        """
        Learn attention weights based on reward.

        Reinforcement learning: increase attention to features that led to reward.
        """
        if not self.attention_history:
            return

        # Credit assignment: recent attention patterns get more credit
        learning_rate = 0.01

        for i in range(self.input_dim):
            # Increase weight if reward was positive
            if reward_signal > 0:
                self.top_down.weights[i] += learning_rate * reward_signal
            else:
                # Decrease weight if reward was negative
                self.top_down.weights[i] = max(
                    0.0,
                    self.top_down.weights[i] + learning_rate * reward_signal
                )

        self.top_down.normalize()

    def get_focused_dimensions(self, threshold: float = 0.1) -> List[int]:
        """Get dimensions with attention above threshold."""
        return [
            i for i, w in enumerate(self.combined.weights)
            if w > threshold
        ]

    def get_attention_entropy(self) -> float:
        """Calculate entropy of attention distribution."""
        entropy = 0.0
        for w in self.combined.weights:
            if w > 0:
                entropy -= w * math.log2(w)
        return entropy

    def get_statistics(self) -> Dict[str, Any]:
        """Get attention statistics."""
        return {
            'attention_entropy': self.get_attention_entropy(),
            'focused_dims': len(self.get_focused_dimensions()),
            'top_5_dims': self.combined.top_k(5),
            'history_length': len(self.attention_history)
        }
