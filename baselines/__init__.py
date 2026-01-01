"""
Baseline Algorithms for Comparison

Implementations of state-of-the-art open-ended evolution algorithms:
- NEAT: NeuroEvolution of Augmenting Topologies
- MAP-Elites: Quality-Diversity Algorithm
- POET: Paired Open-Ended Trailblazer

These serve as rigorous baselines for benchmarking AEGIS-3.
"""

from baselines.neat import NEAT, NEATGenome, NEATNode, NEATConnection
from baselines.map_elites import MAPElites, Elite
from baselines.poet import POET, POETEnvironment, POETPair

__all__ = [
    'NEAT',
    'NEATGenome',
    'NEATNode',
    'NEATConnection',
    'MAPElites',
    'Elite',
    'POET',
    'POETEnvironment',
    'POETPair',
]
