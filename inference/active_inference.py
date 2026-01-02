"""
Active Inference and Free Energy Minimization for AEGIS-3

Based on Karl Friston's Free Energy Principle, this module implements:
- Variational free energy minimization
- Active inference for action selection
- Precision-weighted prediction errors
- Epistemic and pragmatic value
- Expected free energy for planning

Core insight: Intelligent agents minimize surprise (free energy) by:
1. Updating beliefs to better predict observations (perception)
2. Acting to make observations more predictable (action)
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable
from collections import deque
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.neural import NeuralNetwork, create_mlp


@dataclass
class Belief:
    """Probabilistic belief state (posterior)."""
    mean: List[float]
    precision: List[float]  # Inverse variance (confidence)

    def entropy(self) -> float:
        """Calculate entropy of belief (uncertainty)."""
        # H = 0.5 * log(2πe / precision)
        total_entropy = 0.0
        for prec in self.precision:
            if prec > 0:
                total_entropy += 0.5 * math.log(2 * math.pi * math.e / prec)
        return total_entropy

    def kl_divergence(self, other: 'Belief') -> float:
        """KL divergence from this belief to another."""
        if len(self.mean) != len(other.mean):
            raise ValueError("Beliefs must have same dimensionality")

        kl = 0.0
        for i in range(len(self.mean)):
            # KL = 0.5 * (log(p2/p1) + p1/p2 - 1 + (m1-m2)^2 * p2)
            if self.precision[i] > 0 and other.precision[i] > 0:
                variance_ratio = self.precision[i] / other.precision[i]
                mean_diff_sq = (self.mean[i] - other.mean[i]) ** 2

                kl += 0.5 * (
                    math.log(other.precision[i] / self.precision[i]) +
                    variance_ratio - 1.0 +
                    mean_diff_sq * other.precision[i]
                )

        return max(0.0, kl)  # KL is non-negative


@dataclass
class GenerativeModel:
    """
    Generative model P(observation | state, action).

    Represents the agent's model of how the world works.
    """
    state_dim: int
    observation_dim: int
    action_dim: int

    # Likelihood model: P(observation | state)
    likelihood_network: Optional[NeuralNetwork] = None

    # Transition model: P(state' | state, action)
    transition_network: Optional[NeuralNetwork] = None

    # Prior preferences (desired observations)
    preferred_observations: List[float] = field(default_factory=list)

    def __post_init__(self):
        """Initialize neural networks for the generative model."""
        if self.likelihood_network is None:
            # State -> Observation
            self.likelihood_network = create_mlp(
                self.state_dim,
                self.observation_dim,
                [32, 32],
                learning_rate=0.001
            )

        if self.transition_network is None:
            # State + Action -> Next State
            self.transition_network = create_mlp(
                self.state_dim + self.action_dim,
                self.state_dim,
                [64, 32],
                learning_rate=0.001
            )

        if not self.preferred_observations:
            self.preferred_observations = [0.0] * self.observation_dim

    def predict_observation(self, state: List[float]) -> List[float]:
        """Predict observation from state."""
        return self.likelihood_network.predict(state)

    def predict_next_state(self, state: List[float], action: List[float]) -> List[float]:
        """Predict next state given current state and action."""
        state_action = state + action
        return self.transition_network.predict(state_action)

    def update_likelihood(self, state: List[float], observation: List[float]):
        """Update likelihood model with new observation."""
        self.likelihood_network.train(state, observation)

    def update_transition(self, state: List[float], action: List[float], next_state: List[float]):
        """Update transition model with new transition."""
        state_action = state + action
        self.transition_network.train(state_action, next_state)


class ActiveInferenceAgent:
    """
    Agent that minimizes free energy through active inference.

    Combines perception (belief updating) and action (free energy minimization).
    """

    def __init__(
        self,
        state_dim: int = 10,
        observation_dim: int = 10,
        action_dim: int = 4,
        planning_horizon: int = 3
    ):
        """
        Initialize active inference agent.

        Args:
            state_dim: Dimension of hidden state
            observation_dim: Dimension of observations
            action_dim: Dimension of actions
            planning_horizon: How far ahead to plan
        """
        self.state_dim = state_dim
        self.observation_dim = observation_dim
        self.action_dim = action_dim
        self.planning_horizon = planning_horizon

        # Current belief about state
        self.belief = Belief(
            mean=[0.0] * state_dim,
            precision=[1.0] * state_dim  # Start with moderate confidence
        )

        # Generative model of the world
        self.generative_model = GenerativeModel(
            state_dim=state_dim,
            observation_dim=observation_dim,
            action_dim=action_dim
        )

        # History
        self.observation_history: deque = deque(maxlen=1000)
        self.action_history: deque = deque(maxlen=1000)
        self.free_energy_history: deque = deque(maxlen=1000)

        # Precision (inverse temperature) for action selection
        self.action_precision = 1.0

    def perception(self, observation: List[float], learning_rate: float = 0.1):
        """
        Perceptual inference: Update beliefs to minimize prediction error.

        This is gradient descent on free energy w.r.t. beliefs.
        """
        # Predict observation from current belief
        predicted_obs = self.generative_model.predict_observation(self.belief.mean)

        # Prediction error
        prediction_error = [
            observation[i] - predicted_obs[i]
            for i in range(self.observation_dim)
        ]

        # Precision-weighted prediction error
        weighted_error = [
            prediction_error[i] * self.belief.precision[i % len(self.belief.precision)]
            for i in range(len(prediction_error))
        ]

        # Update belief (gradient descent on free energy)
        # Simplified: move belief to reduce prediction error
        for i in range(min(len(self.belief.mean), len(weighted_error))):
            self.belief.mean[i] += learning_rate * weighted_error[i]

        # Update generative model (learning)
        self.generative_model.update_likelihood(self.belief.mean, observation)

        # Store observation
        self.observation_history.append(observation)

    def calculate_free_energy(self, observation: List[float], belief: Optional[Belief] = None) -> float:
        """
        Calculate variational free energy.

        F = -log P(observation | belief) + KL[Q(state) || P(state)]

        Where:
        - First term: Prediction error (accuracy)
        - Second term: Divergence from prior (complexity)
        """
        if belief is None:
            belief = self.belief

        # Predict observation from belief
        predicted_obs = self.generative_model.predict_observation(belief.mean)

        # Prediction error (negative log-likelihood)
        prediction_error = sum(
            (observation[i] - predicted_obs[i]) ** 2
            for i in range(self.observation_dim)
        )

        # Complexity term (KL divergence from prior)
        # Simplified: assume standard normal prior
        prior_belief = Belief(
            mean=[0.0] * len(belief.mean),
            precision=[1.0] * len(belief.precision)
        )
        complexity = belief.kl_divergence(prior_belief)

        # Total free energy
        free_energy = 0.5 * prediction_error + complexity

        return free_energy

    def expected_free_energy(
        self,
        action: List[float],
        horizon: Optional[int] = None
    ) -> Tuple[float, float]:
        """
        Calculate expected free energy for an action sequence.

        G = E[ambiguity] - E[information gain] - E[value]

        Where:
        - Ambiguity: Expected prediction error
        - Information gain: Expected reduction in uncertainty (epistemic value)
        - Value: Expected reward/preference satisfaction (pragmatic value)

        Returns:
            (epistemic_value, pragmatic_value)
        """
        if horizon is None:
            horizon = 1

        # Simulate forward
        current_state = self.belief.mean.copy()
        total_epistemic = 0.0
        total_pragmatic = 0.0

        for step in range(horizon):
            # Predict next state
            next_state = self.generative_model.predict_next_state(current_state, action)

            # Predict observation at next state
            predicted_obs = self.generative_model.predict_observation(next_state)

            # Epistemic value: Information gain (reduction in uncertainty)
            # Measured as entropy reduction
            current_entropy = self.belief.entropy()
            # Simplified: assume observation reduces uncertainty
            expected_entropy_reduction = 0.1 * current_entropy
            total_epistemic += expected_entropy_reduction

            # Pragmatic value: How well does predicted observation match preferences?
            preference_error = sum(
                (predicted_obs[i] - self.generative_model.preferred_observations[i]) ** 2
                for i in range(min(len(predicted_obs), len(self.generative_model.preferred_observations)))
            )
            pragmatic_value = -preference_error  # Negative error is positive value
            total_pragmatic += pragmatic_value

            # Update for next step
            current_state = next_state

        return total_epistemic, total_pragmatic

    def action_selection(
        self,
        num_samples: int = 20,
        epistemic_weight: float = 0.5,
        pragmatic_weight: float = 0.5
    ) -> List[float]:
        """
        Select action by minimizing expected free energy.

        Balances:
        - Epistemic value: Seeking information (exploration)
        - Pragmatic value: Achieving preferences (exploitation)
        """
        best_action = None
        best_score = float('-inf')
        best_values = None

        # Sample possible actions
        for _ in range(num_samples):
            # Random action
            action = [random.random() for _ in range(self.action_dim)]

            # Calculate expected free energy
            epistemic, pragmatic = self.expected_free_energy(action, horizon=self.planning_horizon)

            # Combined score (higher is better)
            score = epistemic_weight * epistemic + pragmatic_weight * pragmatic

            if score > best_score:
                best_score = score
                best_action = action
                best_values = (epistemic, pragmatic)

        self.action_history.append(best_action)
        return best_action

    def step(
        self,
        observation: List[float],
        epistemic_weight: float = 0.5,
        pragmatic_weight: float = 0.5
    ) -> Tuple[List[float], Dict[str, Any]]:
        """
        Perform one step of active inference.

        1. Update beliefs (perception)
        2. Calculate free energy
        3. Select action to minimize expected free energy

        Returns:
            (action, info_dict)
        """
        # Perception: Update beliefs
        self.perception(observation)

        # Calculate current free energy
        free_energy = self.calculate_free_energy(observation)
        self.free_energy_history.append(free_energy)

        # Action selection
        action = self.action_selection(
            epistemic_weight=epistemic_weight,
            pragmatic_weight=pragmatic_weight
        )

        # Prepare info
        info = {
            'belief_mean': self.belief.mean.copy(),
            'belief_entropy': self.belief.entropy(),
            'free_energy': free_energy,
            'avg_free_energy': sum(self.free_energy_history) / len(self.free_energy_history) if self.free_energy_history else 0.0
        }

        return action, info

    def set_preferences(self, preferred_observations: List[float]):
        """Set preferred observations (what the agent wants to perceive)."""
        self.generative_model.preferred_observations = preferred_observations

    def learn_transition(self, state: List[float], action: List[float], next_state: List[float]):
        """Update transition model with observed transition."""
        self.generative_model.update_transition(state, action, next_state)

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'belief_entropy': self.belief.entropy(),
            'recent_free_energy': list(self.free_energy_history)[-10:] if self.free_energy_history else [],
            'avg_free_energy': sum(self.free_energy_history) / len(self.free_energy_history) if self.free_energy_history else 0.0,
            'num_observations': len(self.observation_history),
            'num_actions': len(self.action_history)
        }


class HierarchicalActiveInference:
    """
    Hierarchical active inference with multiple timescales.

    Higher levels set preferences/goals for lower levels.
    Lower levels minimize free energy to achieve those preferences.
    """

    def __init__(
        self,
        levels: int = 3,
        state_dims: Optional[List[int]] = None,
        observation_dim: int = 10,
        action_dim: int = 4
    ):
        """
        Initialize hierarchical active inference.

        Args:
            levels: Number of hierarchical levels
            state_dims: State dimensions for each level (higher levels have smaller state spaces)
            observation_dim: Observation dimension
            action_dim: Action dimension
        """
        self.levels = levels

        # Default state dimensions: Higher levels are more abstract (smaller)
        if state_dims is None:
            state_dims = [observation_dim // (2 ** i) for i in range(levels)]
            state_dims = [max(4, dim) for dim in state_dims]  # Minimum of 4

        # Create agent for each level
        self.agents = []
        for level in range(levels):
            agent = ActiveInferenceAgent(
                state_dim=state_dims[level],
                observation_dim=observation_dim if level == 0 else state_dims[level - 1],
                action_dim=action_dim if level == 0 else state_dims[level],
                planning_horizon=level + 1  # Higher levels plan further
            )
            self.agents.append(agent)

    def step(self, observation: List[float]) -> Tuple[List[float], Dict[str, Any]]:
        """
        Hierarchical inference step.

        Bottom-up: Propagate observations up the hierarchy
        Top-down: Higher levels set preferences for lower levels
        """
        # Bottom-up pass
        current_observation = observation
        for level in range(self.levels):
            agent = self.agents[level]

            # Update beliefs at this level
            agent.perception(current_observation)

            # Observation for next level is the belief of current level
            if level < self.levels - 1:
                current_observation = agent.belief.mean

        # Top-down pass: Set preferences
        for level in range(self.levels - 1, 0, -1):
            higher_agent = self.agents[level]
            lower_agent = self.agents[level - 1]

            # Higher level's belief becomes lower level's preference
            lower_agent.set_preferences(higher_agent.belief.mean)

        # Action from lowest level
        action, info = self.agents[0].step(observation, epistemic_weight=0.3, pragmatic_weight=0.7)

        # Aggregate info from all levels
        info['levels'] = [
            {
                'entropy': agent.belief.entropy(),
                'free_energy': agent.free_energy_history[-1] if agent.free_energy_history else 0.0
            }
            for agent in self.agents
        ]

        return action, info
