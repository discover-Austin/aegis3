"""
AEGIS-2 Representation Evolution

True open-endedness: Evolve THE representation itself.
- Invent new node types
- Discover new operators
- Create new abstraction levels
"""

from .evolution import (
    RepresentationEvolution, TypeInventor, OperatorDiscovery,
    AbstractionLevelCreator
)

__all__ = [
    'RepresentationEvolution', 'TypeInventor', 'OperatorDiscovery',
    'AbstractionLevelCreator'
]
