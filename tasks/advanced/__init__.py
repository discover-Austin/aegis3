"""
Advanced Task Domains for Testing Open-Ended Evolution

These tasks test capabilities beyond basic problem-solving:
- Compositional Reasoning: Building complex solutions from primitives
- Meta-Learning: Learning to learn, adapting strategies
- Creative Generation: Producing novel, coherent outputs
- Abstraction: Discovering and using higher-level concepts
"""

from tasks.advanced.compositional import (
    CompositionalReasoningTask,
    FunctionCompositionTask,
    StructuralAbstractionTask
)

from tasks.advanced.meta_learning import (
    MetaLearningTask,
    FewShotLearningTask,
    StrategyAdaptationTask
)

from tasks.advanced.creative import (
    CreativeGenerationTask,
    NovelPatternTask,
    ConceptCombinationTask
)

__all__ = [
    'CompositionalReasoningTask',
    'FunctionCompositionTask',
    'StructuralAbstractionTask',
    'MetaLearningTask',
    'FewShotLearningTask',
    'StrategyAdaptationTask',
    'CreativeGenerationTask',
    'NovelPatternTask',
    'ConceptCombinationTask',
]
