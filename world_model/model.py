"""
World Model: Predictive Model of Environment Dynamics

Enables planning, imagination, and counterfactual reasoning.
"""

import random
import math
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from collections import deque

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.neural import OnlineNeuralNetwork, create_world_model_network


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


class NeuralTransitionModel:
    """
    Neural network-based transition model with learned predictions.

    Uses online learning to continuously improve predictions as new data arrives.
    """

    def __init__(self, state_dim: int = 10, action_dim: int = 4, learning_rate: float = 0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim

        # Combined state-action input
        input_dim = state_dim + action_dim

        # Create neural network
        self.network = create_world_model_network(
            state_action_dim=input_dim,
            state_dim=state_dim,
            learning_rate=learning_rate
        )

        # Keep track of prediction errors for uncertainty estimation
        self.prediction_errors: List[float] = []
        self.max_errors = 1000  # Rolling window

        # Fallback to nearest-neighbor for cold start
        self.transitions: List[Transition] = []
        self.min_samples_for_nn = 10  # Use NN only after this many samples

    def _encode_action(self, action: Any) -> List[float]:
        """Encode action as one-hot vector."""
        if isinstance(action, (int, float)):
            # One-hot encoding
            action_idx = int(action) % self.action_dim
            encoding = [0.0] * self.action_dim
            encoding[action_idx] = 1.0
            return encoding
        elif isinstance(action, list):
            # Already encoded
            return action[:self.action_dim]
        else:
            # Hash to index
            action_idx = hash(str(action)) % self.action_dim
            encoding = [0.0] * self.action_dim
            encoding[action_idx] = 1.0
            return encoding

    def predict(self, state: List[float], action: Any) -> List[float]:
        """Predict next state using neural network."""
        # Ensure state has correct dimensions
        if len(state) != self.state_dim:
            state = state[:self.state_dim] + [0.0] * (self.state_dim - len(state))

        # Not enough data yet - use simple nearest neighbor
        if len(self.transitions) < self.min_samples_for_nn:
            if not self.transitions:
                return state  # No data, return same state

            best_transition = min(
                self.transitions,
                key=lambda t: sum((s1 - s2) ** 2 for s1, s2 in zip(t.state[:self.state_dim], state))
            )
            return best_transition.next_state[:self.state_dim]

        # Encode action
        action_encoding = self._encode_action(action)

        # Combine state and action
        input_vector = state[:self.state_dim] + action_encoding

        # Neural network prediction
        prediction = self.network.predict(input_vector)

        return prediction

    def update(self, transition: Transition):
        """Update model with new transition and train network."""
        self.transitions.append(transition)

        # Ensure correct dimensions
        state = transition.state[:self.state_dim] + [0.0] * (self.state_dim - len(transition.state))
        next_state = transition.next_state[:self.state_dim] + [0.0] * (self.state_dim - len(transition.next_state))

        # Only train NN if we have enough samples
        if len(self.transitions) >= self.min_samples_for_nn:
            # Encode action
            action_encoding = self._encode_action(transition.action)

            # Create training example
            input_vector = state + action_encoding
            target = next_state

            # Add to experience buffer and train
            self.network.add_experience(input_vector, target)

            # Train with experience replay
            if len(self.network.experience_buffer) >= 10:
                loss = self.network.train_with_replay(replay_batch_size=min(32, len(self.network.experience_buffer)))

                if loss is not None:
                    # Track prediction error for uncertainty
                    self.prediction_errors.append(math.sqrt(loss))  # RMSE
                    if len(self.prediction_errors) > self.max_errors:
                        self.prediction_errors.pop(0)

    def uncertainty(self, state: List[float]) -> float:
        """
        Estimate prediction uncertainty.

        Returns higher uncertainty for less-explored regions.
        """
        # If using nearest-neighbor fallback
        if len(self.transitions) < self.min_samples_for_nn:
            state_key = tuple(round(s, 1) for s in state[:self.state_dim])
            count = sum(1 for t in self.transitions
                       if tuple(round(s, 1) for s in t.state[:self.state_dim]) == state_key)
            return 1.0 / (1.0 + count)

        # Use average prediction error as uncertainty estimate
        if self.prediction_errors:
            base_uncertainty = sum(self.prediction_errors) / len(self.prediction_errors)
        else:
            base_uncertainty = 0.5

        # Adjust based on how many similar states we've seen
        state_similarities = [
            sum((s1 - s2) ** 2 for s1, s2 in zip(t.state[:self.state_dim], state[:self.state_dim]))
            for t in self.transitions[-100:]  # Check recent transitions
        ]

        if state_similarities:
            min_distance = min(state_similarities)
            # Higher uncertainty for states far from training data
            distance_uncertainty = min(1.0, min_distance / 10.0)
        else:
            distance_uncertainty = 1.0

        # Combine uncertainties
        return min(1.0, (base_uncertainty + distance_uncertainty) / 2.0)


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


class NeuralWorldModel(WorldModel):
    """
    Enhanced world model using neural networks for learned predictions.

    Advantages over table-based WorldModel:
    - Generalizes to unseen states
    - Learns complex transition dynamics
    - Continuous online improvement
    - Better uncertainty quantification
    """

    def __init__(self, state_dim: int = 10, action_dim: int = 4, learning_rate: float = 0.001):
        """Initialize neural world model."""
        # Don't call super().__init__ to avoid creating table-based model
        self.transition_model = NeuralTransitionModel(state_dim, action_dim, learning_rate)
        self.reward_model = RewardModel()  # Keep simple reward model for now
        self.experience_buffer: deque = deque(maxlen=10000)

        self.state_dim = state_dim
        self.action_dim = action_dim

    def get_statistics(self) -> Dict[str, Any]:
        """Get neural world model statistics."""
        stats = {
            'total_transitions': len(self.transition_model.transitions),
            'buffer_size': len(self.experience_buffer),
            'unique_rewards': len(self.reward_model.rewards),
            'neural_network': {
                'using_nn': len(self.transition_model.transitions) >= self.transition_model.min_samples_for_nn,
                'experience_buffer': len(self.transition_model.network.experience_buffer),
                'training_steps': self.transition_model.network.training_steps
            }
        }

        # Add prediction error statistics if available
        if self.transition_model.prediction_errors:
            stats['neural_network']['avg_prediction_error'] = (
                sum(self.transition_model.prediction_errors) / len(self.transition_model.prediction_errors)
            )
            stats['neural_network']['recent_prediction_error'] = (
                sum(self.transition_model.prediction_errors[-10:]) / min(10, len(self.transition_model.prediction_errors))
            )

        return stats

    def train_on_batch(self, batch_size: int = 32) -> Optional[float]:
        """
        Explicitly train on a batch from experience buffer.

        Returns:
            Average loss if training occurred, None otherwise
        """
        if len(self.experience_buffer) < batch_size:
            return None

        # Sample batch from experience
        batch_transitions = random.sample(list(self.experience_buffer), batch_size)

        total_loss = 0.0
        for transition in batch_transitions:
            # Ensure correct dimensions
            state = transition.state[:self.state_dim] + [0.0] * (self.state_dim - len(transition.state))
            next_state = transition.next_state[:self.state_dim] + [0.0] * (self.state_dim - len(transition.next_state))

            # Encode action
            action_encoding = self.transition_model._encode_action(transition.action)

            # Create training example
            input_vector = state + action_encoding
            target = next_state

            # Train network
            loss = self.transition_model.network.train(input_vector, target)
            total_loss += loss

        return total_loss / batch_size
