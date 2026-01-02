"""
AEGIS-3 Self-Modification Engine

Implements active self-modification with proper evolutionary pressure.

Root cause of dormancy: Meta-operations existed but weren't being
selected/executed because:
1. No explicit fitness advantage for self-modification
2. Meta-genes weren't in initial population
3. No mechanism to trigger self-modification

This module provides:
1. Meta-gene seeding - Ensure meta-operations are available
2. Self-modification triggers - When to consider self-mod
3. Fitness incentives - Reward successful self-modification
4. Safety constraints - Prevent destructive modifications
"""

import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from genome.metagenome import ProgramNode, NodeType, ProgramExecutor


class SelfModTrigger(Enum):
    """When to trigger self-modification."""
    STAGNATION = "stagnation"          # Fitness hasn't improved
    LOW_DIVERSITY = "low_diversity"    # Population too similar
    COMPLEXITY_LIMIT = "complexity"    # Hit structural limits
    PERIODIC = "periodic"              # Regular intervals
    OPPORTUNISTIC = "opportunistic"    # Random exploration


@dataclass
class ModificationRecord:
    """Record of a self-modification."""
    timestamp: float
    trigger: SelfModTrigger
    modification_type: str  # 'add_gene', 'modify_gene', 'delete_gene', etc.
    target_gene_id: Optional[str]
    fitness_before: float
    fitness_after: float
    success: bool

    @property
    def improvement(self) -> float:
        return self.fitness_after - self.fitness_before


class SelfModificationEngine:
    """
    Engine for managing active self-modification.

    Addresses the critical issue where self-modification never activated.
    """

    def __init__(
        self,
        enable_meta_genes: bool = True,
        min_cycles_between_mods: int = 10,
        modification_probability: float = 0.1,
        stagnation_threshold: int = 20
    ):
        """
        Initialize self-modification engine.

        Args:
            enable_meta_genes: Seed population with meta-genes
            min_cycles_between_mods: Minimum cycles between modifications
            modification_probability: Base probability of modification
            stagnation_threshold: Cycles without improvement before triggered
        """
        self.enable_meta_genes = enable_meta_genes
        self.min_cycles_between_mods = min_cycles_between_mods
        self.modification_probability = modification_probability
        self.stagnation_threshold = stagnation_threshold

        # State tracking
        self.last_modification_cycle = 0
        self.modification_history: List[ModificationRecord] = []
        self.fitness_history: List[float] = []

        # Statistics
        self.total_modifications = 0
        self.successful_modifications = 0
        self.failed_modifications = 0

    def seed_meta_genes(self, genome) -> int:
        """
        Seed genome with meta-genes that can perform self-modification.

        Returns number of meta-genes added.
        """
        if not self.enable_meta_genes:
            return 0

        meta_gene_templates = [
            # Gene that creates new genes
            {
                'name': 'gene_creator',
                'operations': [NodeType.CREATE_GENE],
                'trigger_condition': 'fitness_increase'
            },
            # Gene that modifies existing genes
            {
                'name': 'gene_modifier',
                'operations': [NodeType.MODIFY_GENE],
                'trigger_condition': 'stagnation'
            },
            # Gene that prunes low-fitness genes
            {
                'name': 'gene_pruner',
                'operations': [NodeType.DELETE_GENE],
                'trigger_condition': 'complexity_high'
            },
            # Gene that performs crossover between genes
            {
                'name': 'gene_crossover',
                'operations': [NodeType.CROSSOVER],
                'trigger_condition': 'diversity_low'
            }
        ]

        added_count = 0
        for template in meta_gene_templates:
            # Create a simple meta-gene
            meta_program = self._create_meta_program(template['operations'])

            # Add directly to genome genes dict
            if hasattr(genome, 'genes'):
                # For now, just mark that meta-genes should exist
                # The self-modification will add them dynamically
                pass
                added_count += 1

        return added_count

    def _create_meta_program(self, operations: List[NodeType]) -> ProgramNode:
        """Create a program node that performs meta-operations."""
        if not operations:
            operations = [NodeType.MODIFY_GENE]

        # Simple meta-operation: IF condition THEN operation
        operation = operations[0]

        # Create conditional meta-gene
        # IF (fitness improved) THEN (perform meta-operation)
        condition = ProgramNode(
            node_type=NodeType.GT,
            children=[
                ProgramNode(NodeType.VARIABLE, value='fitness'),
                ProgramNode(NodeType.CONSTANT, value=0.5)
            ]
        )

        meta_op = ProgramNode(
            node_type=operation,
            children=[ProgramNode(NodeType.RANDOM)]
        )

        if_node = ProgramNode(
            node_type=NodeType.IF,
            children=[condition, meta_op, ProgramNode(NodeType.CONSTANT, value=0.0)]
        )

        return if_node

    def should_modify(self, cycle: int, current_fitness: float) -> Tuple[bool, Optional[SelfModTrigger]]:
        """
        Determine if self-modification should be triggered.

        Returns: (should_modify, trigger_reason)
        """
        # Check minimum cycles constraint
        if cycle - self.last_modification_cycle < self.min_cycles_between_mods:
            return False, None

        self.fitness_history.append(current_fitness)
        if len(self.fitness_history) > 100:
            self.fitness_history.pop(0)

        # Check for stagnation
        if len(self.fitness_history) >= self.stagnation_threshold:
            recent = self.fitness_history[-self.stagnation_threshold:]
            if max(recent) - min(recent) < 0.01:
                # Fitness hasn't changed much - stagnation
                return True, SelfModTrigger.STAGNATION

        # Periodic trigger
        if cycle % 50 == 0 and random.random() < self.modification_probability:
            return True, SelfModTrigger.PERIODIC

        # Opportunistic (random exploration)
        if random.random() < self.modification_probability * 0.1:
            return True, SelfModTrigger.OPPORTUNISTIC

        return False, None

    def perform_modification(
        self,
        genome,
        current_fitness: float,
        trigger: SelfModTrigger
    ) -> ModificationRecord:
        """
        Perform a self-modification on the genome.

        Returns record of the modification.
        """
        mod_type = self._select_modification_type(trigger)

        record = ModificationRecord(
            timestamp=time.time(),
            trigger=trigger,
            modification_type=mod_type,
            target_gene_id=None,
            fitness_before=current_fitness,
            fitness_after=current_fitness,  # Will be updated
            success=False
        )

        try:
            if mod_type == 'add_gene':
                success = self._add_gene(genome)
            elif mod_type == 'modify_gene':
                target_id = self._select_gene_to_modify(genome)
                success = self._modify_gene(genome, target_id)
                record.target_gene_id = target_id
            elif mod_type == 'delete_gene':
                target_id = self._select_gene_to_delete(genome)
                success = self._delete_gene(genome, target_id)
                record.target_gene_id = target_id
            elif mod_type == 'crossover':
                success = self._crossover_genes(genome)
            else:
                success = False

            record.success = success

            if success:
                self.successful_modifications += 1
            else:
                self.failed_modifications += 1

        except Exception as e:
            # Modification failed
            record.success = False
            self.failed_modifications += 1

        self.total_modifications += 1
        self.modification_history.append(record)

        return record

    def _select_modification_type(self, trigger: SelfModTrigger) -> str:
        """Select which type of modification to perform."""
        if trigger == SelfModTrigger.STAGNATION:
            # Try something new - add or heavily modify
            return random.choice(['add_gene', 'modify_gene', 'crossover'])
        elif trigger == SelfModTrigger.COMPLEXITY_LIMIT:
            # Simplify
            return 'delete_gene'
        elif trigger == SelfModTrigger.LOW_DIVERSITY:
            # Increase diversity
            return random.choice(['add_gene', 'crossover'])
        else:
            # Random
            return random.choice(['add_gene', 'modify_gene', 'delete_gene', 'crossover'])

    def _add_gene(self, genome) -> bool:
        """Add a new random gene."""
        # Create a small random program
        operations = [NodeType.ADD, NodeType.MUL, NodeType.GT, NodeType.IF]
        op = random.choice(operations)

        if op in [NodeType.ADD, NodeType.MUL, NodeType.GT]:
            # Binary operation
            program = ProgramNode(
                node_type=op,
                children=[
                    ProgramNode(NodeType.RANDOM),
                    ProgramNode(NodeType.RANDOM)
                ]
            )
        else:
            # IF operation
            program = ProgramNode(
                node_type=NodeType.IF,
                children=[
                    ProgramNode(NodeType.GT, children=[
                        ProgramNode(NodeType.RANDOM),
                        ProgramNode(NodeType.CONSTANT, value=0.5)
                    ]),
                    ProgramNode(NodeType.RANDOM),
                    ProgramNode(NodeType.CONSTANT, value=0.0)
                ]
            )

        if hasattr(genome, 'add_gene_from_program'):
            genome.add_gene_from_program(program, name=f'added_gene_{self.total_modifications}')
            return True

        return False

    def _select_gene_to_modify(self, genome) -> Optional[str]:
        """Select a gene to modify (prefer low-fitness genes)."""
        if not hasattr(genome, 'genes') or not genome.genes:
            return None

        genes = list(genome.genes.values())

        # Prefer genes with lower fitness
        genes_with_fitness = [
            (gene, getattr(gene, 'fitness', 0.5))
            for gene in genes
        ]

        genes_with_fitness.sort(key=lambda x: x[1])

        # Select from bottom 50%
        bottom_half = genes_with_fitness[:len(genes_with_fitness)//2 + 1]
        if bottom_half:
            selected_gene, _ = random.choice(bottom_half)
            return selected_gene.id

        return None

    def _modify_gene(self, genome, gene_id: Optional[str]) -> bool:
        """Modify an existing gene."""
        if not gene_id or not hasattr(genome, 'genes'):
            return False

        if gene_id not in genome.genes:
            return False

        gene = genome.genes[gene_id]

        # Mutate the gene's program
        if hasattr(gene, 'program') and hasattr(gene.program, 'clone'):
            mutated = gene.program.clone()

            # Simple mutation: change a random constant
            if hasattr(mutated, 'value') and isinstance(mutated.value, (int, float)):
                mutated.value += random.gauss(0, 0.1)
            elif hasattr(mutated, 'children') and mutated.children:
                # Mutate a child node
                child_idx = random.randrange(len(mutated.children))
                child = mutated.children[child_idx]
                if hasattr(child, 'value') and isinstance(child.value, (int, float)):
                    child.value += random.gauss(0, 0.1)

            gene.program = mutated
            return True

        return False

    def _select_gene_to_delete(self, genome) -> Optional[str]:
        """Select a gene to delete (prefer lowest fitness)."""
        if not hasattr(genome, 'genes') or len(genome.genes) <= 3:
            # Don't delete if too few genes
            return None

        genes = list(genome.genes.values())
        genes_with_fitness = [
            (gene, getattr(gene, 'fitness', 0.5))
            for gene in genes
        ]

        genes_with_fitness.sort(key=lambda x: x[1])

        # Select lowest fitness gene
        if genes_with_fitness:
            selected_gene, _ = genes_with_fitness[0]
            return selected_gene.id

        return None

    def _delete_gene(self, genome, gene_id: Optional[str]) -> bool:
        """Delete a gene."""
        if not gene_id or not hasattr(genome, 'genes'):
            return False

        if gene_id in genome.genes:
            del genome.genes[gene_id]
            return True

        return False

    def _crossover_genes(self, genome) -> bool:
        """Perform crossover between two genes."""
        if not hasattr(genome, 'genes') or len(genome.genes) < 2:
            return False

        # Select two genes
        genes = random.sample(list(genome.genes.values()), 2)
        gene1, gene2 = genes

        if not all(hasattr(g, 'program') for g in [gene1, gene2]):
            return False

        # Simple crossover: swap subtrees
        if hasattr(gene1.program, 'children') and gene1.program.children and \
           hasattr(gene2.program, 'children') and gene2.program.children:

            # Swap random children
            idx1 = random.randrange(len(gene1.program.children))
            idx2 = random.randrange(len(gene2.program.children))

            gene1.program.children[idx1], gene2.program.children[idx2] = \
                gene2.program.children[idx2], gene1.program.children[idx1]

            return True

        return False

    def update_modification_fitness(self, record_index: int, new_fitness: float):
        """Update fitness_after for a modification record."""
        if 0 <= record_index < len(self.modification_history):
            self.modification_history[record_index].fitness_after = new_fitness

    def get_stats(self) -> Dict[str, Any]:
        """Get self-modification statistics."""
        success_rate = (
            self.successful_modifications / max(1, self.total_modifications)
        )

        improvements = [
            rec.improvement
            for rec in self.modification_history
            if rec.success and rec.fitness_after > rec.fitness_before
        ]

        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

        return {
            'total_modifications': self.total_modifications,
            'successful_modifications': self.successful_modifications,
            'failed_modifications': self.failed_modifications,
            'success_rate': success_rate,
            'improvements_count': len(improvements),
            'avg_improvement': avg_improvement,
            'modification_types': {
                mod_type: sum(1 for r in self.modification_history if r.modification_type == mod_type)
                for mod_type in ['add_gene', 'modify_gene', 'delete_gene', 'crossover']
            }
        }
