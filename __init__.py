"""
AEGIS-2: Adaptive Emergent Generative Intelligence System

An open-ended evolving system designed for genuine emergence.

Core components:
- MetaGenome: Self-modifying genetic programs (genes that create genes)
- PatternAlgebra: Compositional patterns with unbounded complexity
- GoalAutomata: Self-spawning goals with intrinsic motivation
- NoveltyEngine: Curiosity-driven exploration and surprise detection
- TangledHierarchy: Strange loops and self-reference
- AutocatalyticNetwork: Self-sustaining reaction networks
- CriticalityEngine: Edge of chaos dynamics

Usage:
    from aegis2 import AEGIS2
    
    system = AEGIS2(name="my_agent")
    
    # Run the system
    for i in range(100):
        result = system.step({'input': i})
        if result['emergence']:
            print("Emergence detected!")
    
    # Check status
    print(system.status())
    
    # Save/load
    system.save()
    system.load()
"""

__version__ = "2.0.0"

from pathlib import Path
import sys

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

# Core
from core.agent import AEGIS2, EmergentEvent

# Genome
from genome.metagenome import MetaGenome, Gene, ProgramNode, NodeType

# Patterns
from patterns.compositional import (
    PatternAlgebra, ComposablePattern, AtomicPattern,
    CompoundPattern, MetaPattern, PatternOperator
)

# Goals
from goals.automata import GoalAutomata, Goal, GoalType, GoalState

# Novelty
from novelty.engine import NoveltyEngine, BehaviorCharacterization

# Strange Loops
from loops.strange_loop import TangledHierarchy, Level, StrangeLoop, SelfModel

# Autocatalysis
from autocatalysis.network import (
    AutocatalyticNetwork, AutocatalyticSet, 
    CatalyticEntity, Reaction
)

# Criticality
from criticality.engine import CriticalityEngine, CriticalityMetrics, Avalanche

# Population
from population.dynamics import Population, Environment

# Meta-evolution
from meta.evolution import MetaEvolutionEngine, Primitive, EvolutionParams

# Self-modification
from self_mod.engine import SelfModificationEngine, Modification

# Genesis (source code modification)
from genesis.engine import GenesisEngine

# Singularity (recursive self-improvement)
from singularity.engine import SingularityEngine, Constitution

# Integrated systems
from omega.system import AEGIS2Omega, OmegaConfig
from ultimate.system import AEGIS2Ultimate, UltimateConfig
from apex.system import AEGIS2Apex, ApexConfig

__all__ = [
    # Core
    'AEGIS2',
    'EmergentEvent',
    
    # Genome
    'MetaGenome',
    'Gene',
    'ProgramNode',
    'NodeType',
    
    # Patterns
    'PatternAlgebra',
    'ComposablePattern',
    'AtomicPattern',
    'CompoundPattern',
    'MetaPattern',
    'PatternOperator',
    
    # Goals
    'GoalAutomata',
    'Goal',
    'GoalType',
    'GoalState',
    
    # Novelty
    'NoveltyEngine',
    'BehaviorCharacterization',
    
    # Strange Loops
    'TangledHierarchy',
    'Level',
    'StrangeLoop',
    'SelfModel',
    
    # Autocatalysis
    'AutocatalyticNetwork',
    'AutocatalyticSet',
    'CatalyticEntity',
    'Reaction',
    
    # Criticality
    'CriticalityEngine',
    'CriticalityMetrics',
    'Avalanche',
    
    # Population
    'Population',
    'Environment',
    
    # Meta-evolution
    'MetaEvolutionEngine',
    'Primitive',
    'EvolutionParams',
    
    # Self-modification
    'SelfModificationEngine',
    'Modification',
    
    # Genesis
    'GenesisEngine',
    
    # Singularity
    'SingularityEngine',
    'Constitution',
    
    # Integration
    'AEGIS2Omega',
    'OmegaConfig',
    'AEGIS2Ultimate',
    'UltimateConfig',
    'AEGIS2Apex',
    'ApexConfig',
]
