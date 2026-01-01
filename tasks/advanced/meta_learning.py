"""
Meta-Learning Tasks

Test ability to:
- Learn from few examples (few-shot learning)
- Adapt strategies across task distributions
- Transfer learning approaches
- Discover meta-level patterns
"""

import random
import math
from typing import List, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Task:
    """A single task in meta-learning."""
    name: str
    train_examples: List[Tuple[List[float], float]]
    test_examples: List[Tuple[List[float], float]]
    task_params: Dict[str, Any]


class MetaLearningTask:
    """
    Base class for meta-learning evaluation.

    Tests whether agent can learn a learning strategy that
    generalizes across a distribution of tasks.
    """

    def __init__(self, difficulty: float = 0.5):
        self.difficulty = difficulty
        self.task_distribution = self._create_task_distribution()

    def _create_task_distribution(self) -> Dict[str, Any]:
        """Define distribution of tasks to meta-learn over."""
        return {
            'type': 'regression',
            'input_dim': 1,
            'output_dim': 1,
            'task_family': 'polynomials'
        }

    def sample_task(self) -> Task:
        """Sample a new task from the distribution."""
        if self.task_distribution['task_family'] == 'polynomials':
            return self._sample_polynomial_task()
        elif self.task_distribution['task_family'] == 'sinusoids':
            return self._sample_sinusoid_task()
        elif self.task_distribution['task_family'] == 'step_functions':
            return self._sample_step_function_task()
        else:
            return self._sample_polynomial_task()

    def _sample_polynomial_task(self, num_train: int = 10, num_test: int = 10) -> Task:
        """Sample polynomial regression task."""
        # Random polynomial coefficients
        degree = random.randint(1, 3)
        coeffs = [random.uniform(-2, 2) for _ in range(degree + 1)]

        def target_fn(x):
            return sum(c * (x ** i) for i, c in enumerate(coeffs))

        # Generate examples
        train_examples = []
        for _ in range(num_train):
            x = random.uniform(-5, 5)
            y = target_fn(x)
            train_examples.append(([x], y))

        test_examples = []
        for _ in range(num_test):
            x = random.uniform(-5, 5)
            y = target_fn(x)
            test_examples.append(([x], y))

        return Task(
            name=f"polynomial_{degree}",
            train_examples=train_examples,
            test_examples=test_examples,
            task_params={'degree': degree, 'coefficients': coeffs}
        )

    def _sample_sinusoid_task(self, num_train: int = 10, num_test: int = 10) -> Task:
        """Sample sinusoidal regression task."""
        amplitude = random.uniform(0.5, 2.0)
        phase = random.uniform(0, 2 * math.pi)
        frequency = random.uniform(0.5, 2.0)

        def target_fn(x):
            return amplitude * math.sin(frequency * x + phase)

        train_examples = []
        for _ in range(num_train):
            x = random.uniform(-math.pi, math.pi)
            y = target_fn(x)
            train_examples.append(([x], y))

        test_examples = []
        for _ in range(num_test):
            x = random.uniform(-math.pi, math.pi)
            y = target_fn(x)
            test_examples.append(([x], y))

        return Task(
            name="sinusoid",
            train_examples=train_examples,
            test_examples=test_examples,
            task_params={'amplitude': amplitude, 'phase': phase, 'frequency': frequency}
        )

    def _sample_step_function_task(self, num_train: int = 10, num_test: int = 10) -> Task:
        """Sample step function task."""
        thresholds = sorted([random.uniform(-5, 5) for _ in range(random.randint(2, 5))])
        values = [random.uniform(-2, 2) for _ in range(len(thresholds) + 1)]

        def target_fn(x):
            for i, threshold in enumerate(thresholds):
                if x < threshold:
                    return values[i]
            return values[-1]

        train_examples = []
        for _ in range(num_train):
            x = random.uniform(-6, 6)
            y = target_fn(x)
            train_examples.append(([x], y))

        test_examples = []
        for _ in range(num_test):
            x = random.uniform(-6, 6)
            y = target_fn(x)
            test_examples.append(([x], y))

        return Task(
            name="step_function",
            train_examples=train_examples,
            test_examples=test_examples,
            task_params={'thresholds': thresholds, 'values': values}
        )

    def evaluate_meta_learner(
        self,
        meta_learner: Callable[[Task], Callable[[List[float]], float]],
        num_tasks: int = 20
    ) -> Dict[str, float]:
        """
        Evaluate meta-learning performance.

        meta_learner: function that takes a task and returns a learned predictor

        Returns metrics about generalization performance.
        """
        task_scores = []

        for _ in range(num_tasks):
            task = self.sample_task()

            try:
                # Meta-learner produces a predictor from training examples
                predictor = meta_learner(task)

                # Evaluate predictor on test examples
                test_errors = []
                for x, y_true in task.test_examples:
                    try:
                        y_pred = predictor(x)
                        error = abs(y_pred - y_true)
                        test_errors.append(error)
                    except:
                        test_errors.append(float('inf'))

                if test_errors:
                    avg_error = sum(min(e, 100) for e in test_errors) / len(test_errors)
                    score = max(0.0, 1.0 - avg_error / 10.0)
                    task_scores.append(score)

            except:
                task_scores.append(0.0)

        if not task_scores:
            return {'avg_score': 0.0, 'success_rate': 0.0}

        return {
            'avg_score': sum(task_scores) / len(task_scores),
            'success_rate': sum(1 for s in task_scores if s > 0.7) / len(task_scores),
            'min_score': min(task_scores),
            'max_score': max(task_scores)
        }


class FewShotLearningTask:
    """
    Few-shot learning: Learn from very few examples.

    Classic meta-learning challenge.
    N-way K-shot: classify into N categories with K examples each.
    """

    def __init__(self, n_way: int = 5, k_shot: int = 1, difficulty: float = 0.5):
        self.n_way = n_way
        self.k_shot = k_shot
        self.difficulty = difficulty

    def sample_episode(self) -> Dict[str, Any]:
        """
        Sample a few-shot learning episode.

        Returns support set (training) and query set (test).
        """
        # Generate N classes
        classes = []
        for i in range(self.n_way):
            # Each class is defined by a prototype + noise
            prototype = [random.uniform(-1, 1) for _ in range(10)]
            classes.append(prototype)

        # Support set: K examples per class
        support_set = []
        for class_id, prototype in enumerate(classes):
            for _ in range(self.k_shot):
                # Add noise to prototype
                example = [p + random.gauss(0, 0.2) for p in prototype]
                support_set.append((example, class_id))

        # Query set: examples to classify
        query_set = []
        for class_id, prototype in enumerate(classes):
            for _ in range(5):  # 5 query examples per class
                example = [p + random.gauss(0, 0.2) for p in prototype]
                query_set.append((example, class_id))

        return {
            'support': support_set,
            'query': query_set,
            'n_way': self.n_way,
            'k_shot': self.k_shot
        }

    def evaluate_few_shot(
        self,
        classifier: Callable[[List[Tuple], List[float]], int],
        num_episodes: int = 20
    ) -> Dict[str, float]:
        """
        Evaluate few-shot learning.

        classifier: function(support_set, query_example) -> predicted_class

        Returns accuracy metrics.
        """
        accuracies = []

        for _ in range(num_episodes):
            episode = self.sample_episode()

            correct = 0
            total = 0

            for example, true_class in episode['query']:
                try:
                    predicted_class = classifier(episode['support'], example)
                    if predicted_class == true_class:
                        correct += 1
                    total += 1
                except:
                    total += 1

            if total > 0:
                accuracy = correct / total
                accuracies.append(accuracy)

        if not accuracies:
            return {'accuracy': 0.0, 'success_rate': 0.0}

        return {
            'accuracy': sum(accuracies) / len(accuracies),
            'success_rate': sum(1 for a in accuracies if a > 0.6) / len(accuracies)
        }


class StrategyAdaptationTask:
    """
    Test ability to adapt strategies based on task characteristics.

    Agent should recognize task type and apply appropriate strategy.
    """

    def __init__(self, difficulty: float = 0.5):
        self.difficulty = difficulty
        self.strategy_types = [
            'greedy',
            'explore_first',
            'cautious',
            'random',
            'adaptive'
        ]

    def sample_environment(self) -> Dict[str, Any]:
        """
        Sample environment that favors different strategies.
        """
        env_type = random.choice(['sparse_reward', 'dense_reward', 'deceptive', 'dynamic'])

        if env_type == 'sparse_reward':
            # Greedy fails, exploration needed
            return {
                'type': 'sparse_reward',
                'reward_fn': lambda action, state: 1.0 if action == state['goal'] else 0.0,
                'optimal_strategy': 'explore_first',
                'states': 20
            }

        elif env_type == 'dense_reward':
            # Greedy works well
            return {
                'type': 'dense_reward',
                'reward_fn': lambda action, state: max(0, 1.0 - abs(action - state['goal']) / 10),
                'optimal_strategy': 'greedy',
                'states': 20
            }

        elif env_type == 'deceptive':
            # Local optima, need to be cautious
            return {
                'type': 'deceptive',
                'reward_fn': self._deceptive_reward,
                'optimal_strategy': 'cautious',
                'states': 20
            }

        elif env_type == 'dynamic':
            # Environment changes, need adaptation
            return {
                'type': 'dynamic',
                'reward_fn': self._dynamic_reward,
                'optimal_strategy': 'adaptive',
                'states': 20
            }

        return {}

    def _deceptive_reward(self, action: int, state: Dict) -> float:
        """Deceptive reward with local optima."""
        goal = state.get('goal', 10)
        # Reward decreases toward goal initially, then spikes
        dist = abs(action - goal)
        if dist == 0:
            return 1.0
        elif dist < 3:
            return 0.2  # Low reward near goal
        else:
            return 0.5 - dist / 20  # Higher reward far from goal

    def _dynamic_reward(self, action: int, state: Dict) -> float:
        """Reward that changes over time."""
        goal = state.get('goal', 10)
        time = state.get('time', 0)
        # Goal shifts over time
        shifted_goal = (goal + time // 5) % 20
        return max(0, 1.0 - abs(action - shifted_goal) / 10)

    def evaluate_strategy_adaptation(
        self,
        agent: Callable[[Dict[str, Any]], str],
        num_environments: int = 10
    ) -> Dict[str, float]:
        """
        Evaluate if agent adapts strategy to environment.

        agent: function(environment) -> strategy_name

        Returns score based on choosing appropriate strategy.
        """
        correct_adaptations = 0
        total = 0

        for _ in range(num_environments):
            env = self.sample_environment()

            try:
                chosen_strategy = agent(env)
                if chosen_strategy == env['optimal_strategy']:
                    correct_adaptations += 1
                total += 1
            except:
                total += 1

        if total == 0:
            return {'accuracy': 0.0}

        return {
            'accuracy': correct_adaptations / total,
            'score': correct_adaptations / total
        }


class LearningCurveAnalysisTask:
    """
    Test if agent can predict its own learning dynamics.

    Meta-cognition: understanding own learning process.
    """

    def __init__(self):
        self.learning_curves = []

    def generate_learning_curve(self, curve_type: str = 'power_law') -> List[float]:
        """Generate synthetic learning curve."""
        steps = 100

        if curve_type == 'power_law':
            # Performance improves as power law
            alpha = random.uniform(0.3, 0.7)
            return [min(1.0, (t + 1) ** alpha / (steps ** alpha)) for t in range(steps)]

        elif curve_type == 'sigmoid':
            # S-curve learning
            midpoint = random.uniform(30, 70)
            steepness = random.uniform(0.05, 0.15)
            return [1.0 / (1.0 + math.exp(-steepness * (t - midpoint))) for t in range(steps)]

        elif curve_type == 'plateau':
            # Quick learning then plateau
            plateau_point = random.randint(20, 50)
            plateau_value = random.uniform(0.6, 0.9)
            return [min(plateau_value, t / plateau_point) for t in range(steps)]

        else:
            return [t / steps for t in range(steps)]

    def evaluate_curve_prediction(
        self,
        predictor: Callable[[List[float], int], List[float]],
        num_curves: int = 20
    ) -> Dict[str, float]:
        """
        Evaluate ability to predict learning curve continuation.

        predictor: function(partial_curve, steps_ahead) -> prediction

        Given first 20% of curve, predict next 80%.
        """
        errors = []

        for _ in range(num_curves):
            curve_type = random.choice(['power_law', 'sigmoid', 'plateau'])
            full_curve = self.generate_learning_curve(curve_type)

            # Give first 20% as context
            context_length = len(full_curve) // 5
            context = full_curve[:context_length]
            true_continuation = full_curve[context_length:]

            try:
                predicted = predictor(context, len(true_continuation))

                # Compute error
                error = sum(abs(p - t) for p, t in zip(predicted, true_continuation))
                error /= len(true_continuation)
                errors.append(error)

            except:
                errors.append(1.0)

        if not errors:
            return {'avg_error': 1.0, 'score': 0.0}

        avg_error = sum(errors) / len(errors)
        score = max(0.0, 1.0 - avg_error)

        return {
            'avg_error': avg_error,
            'score': score
        }
