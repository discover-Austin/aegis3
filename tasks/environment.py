"""
Real Task Environments for Genuine Fitness Evaluation

No more synthetic fitness - agents must solve actual problems:
- Predict sequences
- Classify patterns
- Navigate mazes
- Solve symbolic regression
- Complete logic puzzles
- Control dynamic systems
"""

import random
import math
import hashlib
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod


class TaskType(Enum):
    """Types of tasks agents can solve."""
    SEQUENCE_PREDICTION = "sequence_prediction"
    PATTERN_CLASSIFICATION = "pattern_classification"
    MAZE_NAVIGATION = "maze_navigation"
    SYMBOLIC_REGRESSION = "symbolic_regression"
    LOGIC_PUZZLE = "logic_puzzle"
    CONTROL_TASK = "control_task"


@dataclass
class TaskResult:
    """Result of attempting a task."""
    success: bool = False
    score: float = 0.0  # 0-1
    steps_taken: int = 0
    time_taken: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'score': self.score,
            'steps_taken': self.steps_taken,
            'time_taken': self.time_taken,
            'error': self.error,
            'details': self.details
        }


class Task(ABC):
    """Abstract base class for tasks."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        self.task_id = task_id
        self.difficulty = difficulty  # 0-1
        self.attempts = 0
        self.successes = 0

    @abstractmethod
    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate agent's solution."""
        pass

    @abstractmethod
    def get_input(self) -> Any:
        """Get task input for agent."""
        pass

    @abstractmethod
    def reset(self):
        """Reset task to initial state."""
        pass

    def get_success_rate(self) -> float:
        """Get historical success rate."""
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts


class SequencePrediction(Task):
    """Predict next element in sequence."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.sequence_generators = [
            self._arithmetic,
            self._geometric,
            self._fibonacci,
            self._polynomial,
            self._periodic
        ]
        self.current_sequence = []
        self.current_answer = 0
        self.reset()

    def _arithmetic(self, n: int, diff: float) -> List[float]:
        """Arithmetic sequence."""
        start = random.uniform(-10, 10)
        return [start + i * diff for i in range(n)]

    def _geometric(self, n: int, ratio: float) -> List[float]:
        """Geometric sequence."""
        start = random.uniform(1, 5)
        return [start * (ratio ** i) for i in range(n)]

    def _fibonacci(self, n: int, _) -> List[float]:
        """Fibonacci-like sequence."""
        a, b = random.randint(1, 5), random.randint(1, 5)
        seq = [a, b]
        for _ in range(n - 2):
            seq.append(seq[-1] + seq[-2])
        return seq[:n]

    def _polynomial(self, n: int, degree: float) -> List[float]:
        """Polynomial sequence."""
        coeffs = [random.uniform(-2, 2) for _ in range(int(degree) + 1)]
        return [sum(c * (i ** p) for p, c in enumerate(coeffs)) for i in range(n)]

    def _periodic(self, n: int, period: float) -> List[float]:
        """Periodic sequence."""
        amplitude = random.uniform(1, 5)
        offset = random.uniform(-5, 5)
        return [amplitude * math.sin(2 * math.pi * i / period) + offset for i in range(n)]

    def reset(self):
        """Generate new sequence."""
        gen = random.choice(self.sequence_generators)
        length = int(5 + self.difficulty * 10)
        param = 1 + self.difficulty * 3
        full_seq = gen(length + 1, param)
        self.current_sequence = full_seq[:-1]
        self.current_answer = full_seq[-1]

    def get_input(self) -> List[float]:
        """Get sequence to predict."""
        return self.current_sequence.copy()

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate prediction."""
        self.attempts += 1

        try:
            prediction = float(agent_output)
            error = abs(prediction - self.current_answer)
            relative_error = error / (abs(self.current_answer) + 1e-6)

            # Score based on relative error
            score = max(0.0, 1.0 - relative_error)
            success = score > 0.8

            if success:
                self.successes += 1

            return TaskResult(
                success=success,
                score=score,
                details={
                    'prediction': prediction,
                    'correct': self.current_answer,
                    'error': error,
                    'relative_error': relative_error
                }
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class PatternClassification(Task):
    """Classify patterns into categories."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.num_classes = int(2 + difficulty * 4)  # 2-6 classes
        self.pattern_dim = int(4 + difficulty * 8)  # 4-12 dimensions
        self.centroids = []
        self.current_pattern = []
        self.current_class = 0
        self.reset()

    def reset(self):
        """Generate new classification problem."""
        # Create class centroids
        self.centroids = []
        for _ in range(self.num_classes):
            centroid = [random.gauss(0, 5) for _ in range(self.pattern_dim)]
            self.centroids.append(centroid)

        # Generate pattern from random class
        self.current_class = random.randint(0, self.num_classes - 1)
        noise_level = 0.5 + self.difficulty * 1.5
        self.current_pattern = [
            c + random.gauss(0, noise_level)
            for c in self.centroids[self.current_class]
        ]

    def get_input(self) -> List[float]:
        """Get pattern to classify."""
        return self.current_pattern.copy()

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate classification."""
        self.attempts += 1

        try:
            predicted_class = int(agent_output) % self.num_classes
            correct = predicted_class == self.current_class

            if correct:
                self.successes += 1

            return TaskResult(
                success=correct,
                score=1.0 if correct else 0.0,
                details={
                    'predicted': predicted_class,
                    'correct': self.current_class,
                    'num_classes': self.num_classes
                }
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class MazeNavigation(Task):
    """Navigate through a maze to reach goal."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.size = int(5 + difficulty * 10)  # 5x5 to 15x15
        self.maze = []
        self.start_pos = (0, 0)
        self.goal_pos = (0, 0)
        self.current_pos = (0, 0)
        self.visited = set()
        self.steps = 0
        self.max_steps = self.size * self.size
        self.reset()

    def reset(self):
        """Generate new maze."""
        # Simple maze generation (can be improved with proper algorithms)
        self.maze = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # Add walls (1 = wall, 0 = path)
        for i in range(self.size):
            for j in range(self.size):
                if random.random() < 0.2 * self.difficulty:
                    self.maze[i][j] = 1

        # Ensure start and goal are clear
        self.start_pos = (0, 0)
        self.goal_pos = (self.size - 1, self.size - 1)
        self.maze[0][0] = 0
        self.maze[self.size - 1][self.size - 1] = 0

        self.current_pos = self.start_pos
        self.visited = {self.start_pos}
        self.steps = 0

    def get_input(self) -> Dict[str, Any]:
        """Get current maze state."""
        x, y = self.current_pos
        gx, gy = self.goal_pos

        # Local view (3x3 around agent)
        local_view = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    local_view.append(self.maze[nx][ny])
                else:
                    local_view.append(1)  # Wall

        return {
            'position': [x, y],
            'goal': [gx, gy],
            'local_view': local_view,
            'distance_to_goal': abs(x - gx) + abs(y - gy),
            'steps': self.steps
        }

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate navigation action."""
        self.attempts += 1

        try:
            # Action: 0=up, 1=right, 2=down, 3=left
            action = int(agent_output) % 4
            x, y = self.current_pos

            # Move
            moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            dx, dy = moves[action]
            nx, ny = x + dx, y + dy

            # Check validity
            if 0 <= nx < self.size and 0 <= ny < self.size and self.maze[nx][ny] == 0:
                self.current_pos = (nx, ny)
                self.visited.add(self.current_pos)

            self.steps += 1

            # Check goal
            success = self.current_pos == self.goal_pos
            if success:
                self.successes += 1

            # Timeout
            if self.steps >= self.max_steps:
                return TaskResult(success=False, score=0.0, error="Timeout")

            # Score based on efficiency
            if success:
                optimal_steps = abs(self.goal_pos[0] - self.start_pos[0]) + abs(self.goal_pos[1] - self.start_pos[1])
                efficiency = optimal_steps / max(self.steps, 1)
                score = min(1.0, efficiency)
            else:
                # Partial credit for getting closer
                initial_dist = abs(self.goal_pos[0] - self.start_pos[0]) + abs(self.goal_pos[1] - self.start_pos[1])
                current_dist = abs(self.goal_pos[0] - self.current_pos[0]) + abs(self.goal_pos[1] - self.current_pos[1])
                score = max(0.0, 1.0 - current_dist / max(initial_dist, 1))

            return TaskResult(
                success=success,
                score=score,
                steps_taken=self.steps,
                details={
                    'position': self.current_pos,
                    'goal': self.goal_pos,
                    'visited': len(self.visited),
                    'action': action
                }
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class SymbolicRegression(Task):
    """Find symbolic expression that fits data."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.target_function = None
        self.data_points = []
        self.reset()

    def reset(self):
        """Generate new regression problem."""
        # Random target function
        functions = [
            lambda x: x ** 2,
            lambda x: 2 * x + 1,
            lambda x: math.sin(x),
            lambda x: math.exp(-x ** 2),
            lambda x: x ** 3 - 2 * x,
            lambda x: 1 / (1 + math.exp(-x))
        ]
        self.target_function = random.choice(functions)

        # Generate data points
        num_points = int(10 + self.difficulty * 20)
        self.data_points = []
        for _ in range(num_points):
            x = random.uniform(-3, 3)
            y = self.target_function(x)
            noise = random.gauss(0, 0.1 * self.difficulty)
            self.data_points.append((x, y + noise))

    def get_input(self) -> List[Tuple[float, float]]:
        """Get data points."""
        return self.data_points.copy()

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate fitted function."""
        self.attempts += 1

        try:
            # Agent should provide predictions for each x
            if not isinstance(agent_output, (list, tuple)):
                return TaskResult(success=False, score=0.0, error="Expected list of predictions")

            if len(agent_output) != len(self.data_points):
                return TaskResult(success=False, score=0.0, error="Wrong number of predictions")

            # Calculate MSE
            mse = 0.0
            for (x, y_true), y_pred in zip(self.data_points, agent_output):
                mse += (y_true - y_pred) ** 2
            mse /= len(self.data_points)

            # Score based on MSE
            score = max(0.0, 1.0 - mse)
            success = score > 0.8

            if success:
                self.successes += 1

            return TaskResult(
                success=success,
                score=score,
                details={'mse': mse, 'num_points': len(self.data_points)}
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class LogicPuzzle(Task):
    """Solve logic puzzles."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.variables = []
        self.constraints = []
        self.solution = {}
        self.reset()

    def reset(self):
        """Generate new logic puzzle."""
        num_vars = int(2 + self.difficulty * 4)  # 2-6 variables
        self.variables = [f"v{i}" for i in range(num_vars)]

        # Simple SAT-like problem: assign True/False to satisfy constraints
        # Generate solution first
        self.solution = {v: random.choice([True, False]) for v in self.variables}

        # Generate constraints satisfied by solution
        self.constraints = []
        num_constraints = int(3 + self.difficulty * 5)
        for _ in range(num_constraints):
            # Random clause
            clause_size = random.randint(1, min(3, num_vars))
            clause = random.sample(self.variables, clause_size)
            # Add negations
            clause = [(v, random.choice([True, False])) for v in clause]
            # Ensure constraint is satisfied
            if not any(self.solution[v] == val for v, val in clause):
                # Flip one to make it satisfied
                v, val = random.choice(clause)
                clause = [(v2, val2) if v2 != v else (v, self.solution[v]) for v2, val2 in clause]
            self.constraints.append(clause)

    def get_input(self) -> Dict[str, Any]:
        """Get puzzle specification."""
        return {
            'variables': self.variables,
            'constraints': self.constraints
        }

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate solution."""
        self.attempts += 1

        try:
            # Agent provides variable assignment
            if not isinstance(agent_output, dict):
                return TaskResult(success=False, score=0.0, error="Expected dict of assignments")

            # Check constraints
            satisfied = 0
            for clause in self.constraints:
                if any(agent_output.get(v, False) == val for v, val in clause):
                    satisfied += 1

            score = satisfied / len(self.constraints) if self.constraints else 0.0
            success = score == 1.0

            if success:
                self.successes += 1

            return TaskResult(
                success=success,
                score=score,
                details={
                    'satisfied': satisfied,
                    'total': len(self.constraints),
                    'assignment': agent_output
                }
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class ControlTask(Task):
    """Control a dynamic system to reach target state."""

    def __init__(self, task_id: str, difficulty: float = 0.5):
        super().__init__(task_id, difficulty)
        self.state = []
        self.target = []
        self.steps = 0
        self.max_steps = 100
        self.reset()

    def reset(self):
        """Initialize control problem."""
        # Simple 2D point control
        self.state = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.target = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.steps = 0

    def get_input(self) -> Dict[str, Any]:
        """Get current state."""
        distance = math.sqrt(sum((s - t) ** 2 for s, t in zip(self.state, self.target)))
        return {
            'state': self.state.copy(),
            'target': self.target.copy(),
            'distance': distance,
            'steps': self.steps
        }

    def evaluate(self, agent_output: Any) -> TaskResult:
        """Evaluate control action."""
        self.attempts += 1

        try:
            # Action is velocity command
            if not isinstance(agent_output, (list, tuple)) or len(agent_output) != 2:
                return TaskResult(success=False, score=0.0, error="Expected [vx, vy]")

            vx, vy = float(agent_output[0]), float(agent_output[1])

            # Limit action magnitude
            max_vel = 1.0
            mag = math.sqrt(vx ** 2 + vy ** 2)
            if mag > max_vel:
                vx = vx / mag * max_vel
                vy = vy / mag * max_vel

            # Update state
            self.state[0] += vx * 0.1
            self.state[1] += vy * 0.1

            self.steps += 1

            # Check goal
            distance = math.sqrt(sum((s - t) ** 2 for s, t in zip(self.state, self.target)))
            success = distance < 0.1

            if success:
                self.successes += 1

            # Score based on distance
            initial_dist = 10.0  # Approximate
            score = max(0.0, 1.0 - distance / initial_dist)

            if self.steps >= self.max_steps:
                return TaskResult(success=False, score=score, error="Timeout")

            return TaskResult(
                success=success,
                score=score,
                steps_taken=self.steps,
                details={
                    'state': self.state.copy(),
                    'target': self.target.copy(),
                    'distance': distance,
                    'action': [vx, vy]
                }
            )
        except Exception as e:
            return TaskResult(success=False, score=0.0, error=str(e))


class TaskEnvironment:
    """
    Environment containing multiple tasks for agent evaluation.

    This replaces synthetic fitness with actual problem-solving performance.
    """

    def __init__(self, curriculum: bool = True):
        self.curriculum = curriculum
        self.tasks: Dict[str, Task] = {}
        self.task_history: List[Dict] = []
        self.current_difficulty = 0.1

        # Initialize task suite
        self._initialize_tasks()

    def _initialize_tasks(self):
        """Create initial task set."""
        task_types = [
            (SequencePrediction, "seq"),
            (PatternClassification, "pattern"),
            (MazeNavigation, "maze"),
            (SymbolicRegression, "regression"),
            (LogicPuzzle, "logic"),
            (ControlTask, "control")
        ]

        for TaskClass, prefix in task_types:
            for i in range(3):  # 3 tasks of each type
                task_id = f"{prefix}_{i}"
                difficulty = self.current_difficulty if self.curriculum else random.random()
                self.tasks[task_id] = TaskClass(task_id, difficulty)

    def evaluate_agent(self, agent, num_tasks: int = 5) -> Dict[str, Any]:
        """
        Evaluate agent on multiple tasks.

        Returns comprehensive fitness metrics based on actual performance.
        """
        # Sample tasks
        task_ids = random.sample(list(self.tasks.keys()), min(num_tasks, len(self.tasks)))

        results = []
        total_score = 0.0
        successes = 0

        for task_id in task_ids:
            task = self.tasks[task_id]
            task.reset()

            # Get agent's response
            task_input = task.get_input()

            # Agent needs to produce output (this is a simplified interface)
            # Real implementation would call agent's inference method
            agent_output = self._agent_solve(agent, task_input, task)

            # Evaluate
            result = task.evaluate(agent_output)
            results.append({
                'task_id': task_id,
                'task_type': type(task).__name__,
                'result': result.to_dict()
            })

            total_score += result.score
            if result.success:
                successes += 1

        # Aggregate metrics
        avg_score = total_score / len(results) if results else 0.0
        success_rate = successes / len(results) if results else 0.0

        # Update curriculum
        if self.curriculum:
            if success_rate > 0.8:
                self.current_difficulty = min(1.0, self.current_difficulty + 0.05)
            elif success_rate < 0.3:
                self.current_difficulty = max(0.1, self.current_difficulty - 0.05)

        eval_result = {
            'avg_score': avg_score,
            'success_rate': success_rate,
            'total_successes': successes,
            'total_tasks': len(results),
            'difficulty': self.current_difficulty,
            'task_results': results
        }

        self.task_history.append(eval_result)

        return eval_result

    def _agent_solve(self, agent, task_input: Any, task: Task) -> Any:
        """
        Interface between agent and task.

        This is a placeholder - actual implementation depends on agent architecture.
        """
        # For maze navigation, might need multiple steps
        if isinstance(task, MazeNavigation):
            # Return single action
            return random.randint(0, 3)

        # For control tasks
        elif isinstance(task, ControlTask):
            # Return velocity command
            state = task_input['state']
            target = task_input['target']
            # Simple proportional control
            return [(target[0] - state[0]) * 0.5, (target[1] - state[1]) * 0.5]

        # For sequence prediction
        elif isinstance(task, SequencePrediction):
            # Return next value (simple prediction)
            if len(task_input) >= 2:
                return task_input[-1] + (task_input[-1] - task_input[-2])
            return 0.0

        # For pattern classification
        elif isinstance(task, PatternClassification):
            # Return class prediction
            return random.randint(0, task.num_classes - 1)

        # For symbolic regression
        elif isinstance(task, SymbolicRegression):
            # Return predictions for each point
            return [y for x, y in task_input]

        # For logic puzzles
        elif isinstance(task, LogicPuzzle):
            # Return assignment
            return {v: random.choice([True, False]) for v in task_input['variables']}

        return None

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get specific task."""
        return self.tasks.get(task_id)

    def add_task(self, task: Task):
        """Add new task to environment."""
        self.tasks[task.task_id] = task

    def get_statistics(self) -> Dict[str, Any]:
        """Get environment statistics."""
        if not self.task_history:
            return {}

        recent = self.task_history[-10:]

        return {
            'total_evaluations': len(self.task_history),
            'current_difficulty': self.current_difficulty,
            'recent_avg_score': sum(e['avg_score'] for e in recent) / len(recent),
            'recent_success_rate': sum(e['success_rate'] for e in recent) / len(recent),
            'task_count': len(self.tasks),
            'task_types': list(set(type(t).__name__ for t in self.tasks.values()))
        }
