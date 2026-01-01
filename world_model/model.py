"""
World Model: Predictive Model of Environment Dynamics

Enables planning, imagination, and counterfactual reasoning.
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from collections import deque


@dataclass
class Transition:
    """A state transition experience."""
    state: List[float]
    action: Any
    next_state: List[float]
    reward: float
    done: bool = False


class TransitionModel:
    """Predicts next state given current state and action."""

    def __init__(self, state_dim: int = 10, action_dim: int = 4):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.transitions: List[Transition] = []
        self.model: Dict[Tuple, List[float]] = {}  # Simple lookup table

    def predict(self, state: List[float], action: Any) -> List[float]:
        """Predict next state."""
        # Simple nearest-neighbor prediction
        if not self.transitions:
            return state  # No prediction possible

        # Find similar transitions
        state_key = tuple(round(s, 1) for s in state)
        if state_key in self.model:
            return self.model[state_key]

        # Find nearest
        best_transition = min(
            self.transitions,
            key=lambda t: sum((s1 - s2) ** 2 for s1, s2 in zip(t.state, state))
        )

        return best_transition.next_state

    def update(self, transition: Transition):
        """Update model with new transition."""
        self.transitions.append(transition)
        state_key = tuple(round(s, 1) for s in transition.state)
        self.model[state_key] = transition.next_state

    def uncertainty(self, state: List[float]) -> float:
        """Estimate uncertainty of prediction."""
        if not self.transitions:
            return 1.0  # Maximum uncertainty

        # Count similar states seen before
        state_key = tuple(round(s, 1) for s in state)
        count = sum(1 for t in self.transitions
                    if tuple(round(s, 1) for s in t.state) == state_key)

        # More observations = less uncertainty
        return 1.0 / (1.0 + count)


class RewardModel:
    """Predicts reward for state-action pairs."""

    def __init__(self):
        self.rewards: Dict[Tuple, float] = {}
        self.observations: List[Tuple[List[float], Any, float]] = []

    def predict(self, state: List[float], action: Any) -> float:
        """Predict reward."""
        state_key = tuple(round(s, 1) for s in state)
        action_key = str(action)
        key = (state_key, action_key)

        if key in self.rewards:
            return self.rewards[key]

        # Find similar state-action pair
        if self.observations:
            best_match = min(
                self.observations,
                key=lambda obs: sum((s1 - s2) ** 2 for s1, s2 in zip(obs[0], state))
            )
            return best_match[2]

        return 0.0

    def update(self, state: List[float], action: Any, reward: float):
        """Update reward model."""
        state_key = tuple(round(s, 1) for s in state)
        action_key = str(action)
        key = (state_key, action_key)

        self.rewards[key] = reward
        self.observations.append((state, action, reward))


class WorldModel:
    """
    Complete world model combining transition and reward prediction.

    Enables:
    - Planning (simulate action sequences)
    - Imagination (generate hypothetical scenarios)
    - Counterfactual reasoning (what if?)
    """

    def __init__(self, state_dim: int = 10, action_dim: int = 4):
        self.transition_model = TransitionModel(state_dim, action_dim)
        self.reward_model = RewardModel()
        self.experience_buffer: deque = deque(maxlen=10000)

    def observe(self, transition: Transition):
        """Add observation to world model."""
        self.transition_model.update(transition)
        self.reward_model.update(transition.state, transition.action, transition.reward)
        self.experience_buffer.append(transition)

    def plan(
        self,
        start_state: List[float],
        actions: List[Any],
        horizon: int = 5
    ) -> Tuple[List[List[float]], float]:
        """
        Plan action sequence by simulating forward.

        Returns:
            (predicted_states, total_predicted_reward)
        """
        states = [start_state]
        total_reward = 0.0

        current_state = start_state

        for i in range(min(horizon, len(actions))):
            action = actions[i]

            # Predict next state
            next_state = self.transition_model.predict(current_state, action)

            # Predict reward
            reward = self.reward_model.predict(current_state, action)

            states.append(next_state)
            total_reward += reward

            current_state = next_state

        return states, total_reward

    def imagine(self, start_state: List[float], num_scenarios: int = 10) -> List[Dict]:
        """
        Generate imagined scenarios from start state.

        Returns list of possible futures.
        """
        scenarios = []

        for _ in range(num_scenarios):
            scenario = {
                'states': [start_state],
                'actions': [],
                'rewards': [],
                'total_reward': 0.0
            }

            current_state = start_state

            for step in range(5):  # 5-step lookahead
                # Random action
                action = random.randint(0, 3)

                # Predict
                next_state = self.transition_model.predict(current_state, action)
                reward = self.reward_model.predict(current_state, action)

                scenario['states'].append(next_state)
                scenario['actions'].append(action)
                scenario['rewards'].append(reward)
                scenario['total_reward'] += reward

                current_state = next_state

            scenarios.append(scenario)

        return scenarios

    def counterfactual(
        self,
        actual_state: List[float],
        actual_action: Any,
        alternative_action: Any
    ) -> Dict[str, Any]:
        """
        Counterfactual reasoning: What if we had taken a different action?

        Returns comparison of actual vs counterfactual outcomes.
        """
        # Actual outcome
        actual_next_state = self.transition_model.predict(actual_state, actual_action)
        actual_reward = self.reward_model.predict(actual_state, actual_action)

        # Counterfactual outcome
        cf_next_state = self.transition_model.predict(actual_state, alternative_action)
        cf_reward = self.reward_model.predict(actual_state, alternative_action)

        return {
            'actual': {
                'action': actual_action,
                'next_state': actual_next_state,
                'reward': actual_reward
            },
            'counterfactual': {
                'action': alternative_action,
                'next_state': cf_next_state,
                'reward': cf_reward
            },
            'reward_difference': cf_reward - actual_reward,
            'better_choice': alternative_action if cf_reward > actual_reward else actual_action
        }

    def get_uncertainty_map(self, states: List[List[float]]) -> List[float]:
        """Get uncertainty estimates for list of states."""
        return [self.transition_model.uncertainty(s) for s in states]

    def get_statistics(self) -> Dict[str, Any]:
        """Get world model statistics."""
        return {
            'total_transitions': len(self.transition_model.transitions),
            'unique_states': len(self.transition_model.model),
            'unique_rewards': len(self.reward_model.rewards),
            'buffer_size': len(self.experience_buffer)
        }
