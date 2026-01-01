"""
AEGIS-3: Adaptive Emergent Generative Intelligence System

An open-ended evolving system designed for genuine emergence.

Core components:
- MetaGenome: Self-modifying genetic programs (genes that create genes)
- PatternAlgebra: Compositional patterns with unbounded complexity
- GoalAutomata: Self-spawning goals with intrinsic motivation
- NoveltyEngine: Curiosity-driven exploration and surprise detection
- TangledHierarchy: Strange loops and self-reference
- AutocatalyticNetwork: Self-sustaining reaction networks
- CriticalityEngine: Edge of chaos dynamics

AEGIS-3 New Features:
- TaskEnvironment: Real fitness evaluation on actual tasks
- Persistence: Save/load complete state across sessions
- RichPrimitives: 100+ advanced GP primitives
- MultiModal: Image, text, audio, graph I/O
- RepresentationEvolution: Evolve the representation itself
- WorldModel: Predictive models for planning
- Attention: Salience mechanisms
- TemporalHierarchy: Multi-timescale actions
- EmergentLanguage: Communication protocol evolution
- CausalReasoning: Interventions and counterfactuals
- Benchmarks: Standardized open-endedness tests
- Infrastructure: Distributed, visualization, tracking

Usage:
    from aegis3 import AEGIS2

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

__version__ = "3.0.0"

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

# AEGIS-3 New Modules
# Tasks (real fitness evaluation)
from tasks.environment import TaskEnvironment, Task, TaskType

# Persistence
from persistence.checkpoint import PersistentGenome, CheckpointManager

# Rich Primitives
from genome.rich_primitives import ExtendedNodeType, ExtendedPrimitiveExecutor

# Multi-Modal I/O
from multimodal.modalities import (
    ImageModality, TextModality, AudioModality,
    TimeSeriesModality, GraphModality, MultiModalInput
)

# Representation Evolution
from representation.evolution import (
    RepresentationEvolution, TypeInventor, OperatorDiscovery
)

# World Model
from world_model.model import WorldModel, TransitionModel

# Attention
from attention.mechanism import AttentionMechanism, SalienceMap

# Temporal Hierarchy
from hierarchy.temporal import TemporalHierarchy, Skill, Option

# Communication
from communication.protocol import EmergentLanguage, CommunicationProtocol

# Causal Reasoning
from causal.reasoning import CausalModel, CausalGraph

# Grounded Symbols
from grounded.emergence import GroundedGoalFormation, SymbolGrounding

# Benchmarks
from benchmarks.suite import AEGISBenchmarks, BenchmarkResult

# Infrastructure
from experiments.runner import ExperimentRunner, LongRunConfig
from distributed.island import DistributedAEGIS
from visualization.dashboard import AEGISDashboard
from tracking.tracker import ExperimentTracker
from bootstrap.minimal import MinimalBootstrap

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

    # AEGIS-3: New Systems
    'TaskEnvironment',
    'Task',
    'TaskType',
    'PersistentGenome',
    'CheckpointManager',
    'ExtendedNodeType',
    'ExtendedPrimitiveExecutor',
    'ImageModality',
    'TextModality',
    'AudioModality',
    'TimeSeriesModality',
    'GraphModality',
    'MultiModalInput',
    'RepresentationEvolution',
    'TypeInventor',
    'OperatorDiscovery',
    'WorldModel',
    'TransitionModel',
    'AttentionMechanism',
    'SalienceMap',
    'TemporalHierarchy',
    'Skill',
    'Option',
    'EmergentLanguage',
    'CommunicationProtocol',
    'CausalModel',
    'CausalGraph',
    'GroundedGoalFormation',
    'SymbolGrounding',
    'AEGISBenchmarks',
    'BenchmarkResult',
    'ExperimentRunner',
    'LongRunConfig',
    'DistributedAEGIS',
    'AEGISDashboard',
    'ExperimentTracker',
    'MinimalBootstrap',
]

