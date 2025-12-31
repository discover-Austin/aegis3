"""
AEGIS-2 Task Environments: Real Fitness Evaluation

Instead of synthetic fitness from internal metrics, agents must solve actual problems.
"""

from .environment import (
    TaskEnvironment, Task, TaskType, TaskResult,
    SequencePrediction, PatternClassification, MazeNavigation,
    SymbolicRegression, LogicPuzzle, ControlTask
)

__all__ = [
    'TaskEnvironment', 'Task', 'TaskType', 'TaskResult',
    'SequencePrediction', 'PatternClassification', 'MazeNavigation',
    'SymbolicRegression', 'LogicPuzzle', 'ControlTask'
]
