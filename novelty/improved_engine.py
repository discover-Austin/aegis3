"""
AEGIS-3 Improved Novelty Engine

Fixes the critical issue where novelty scores were always 0.0.

Root cause: Behavioral characterizations had empty or improperly constructed
vectors, so all behaviors appeared identical (distance = 0).

This implementation:
1. Properly extracts behavioral features from agent state
2. Ensures non-empty characterization vectors
3. Tracks multiple behavioral dimensions
4. Validates vectors before computing novelty
5. Provides debugging information
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from novelty.engine import BehaviorCharacterization, NoveltyArchive


class ImprovedBehaviorCharacterization:
    """
    Enhanced behavioral characterization with proper vector construction.
    """

    @staticmethod
    def characterize_agent_state(
        agent_state: Dict[str, Any],
        input_data: Optional[Dict] = None
    ) -> BehaviorCharacterization:
        """
        Create a behavior characterization from agent state.

        Extracts multiple behavioral dimensions:
        - Fitness trajectory
        - Structural properties (genome size, pattern count, etc.)
        - Activity levels (goals active, patterns used)
        - Output characteristics
        - Diversity metrics
        """
        vector = []

        # 1. Fitness and performance
        fitness = agent_state.get('fitness', 0.0)
        vector.append(fitness)

        # 2. Structural dimensions
        genome_stats = agent_state.get('genome_stats', {})
        vector.append(genome_stats.get('total_genes', 0) / 100.0)  # Normalize
        vector.append(genome_stats.get('max_gene_depth', 1) / 10.0)
        vector.append(genome_stats.get('avg_generation', 0) / 50.0)

        # 3. Pattern space
        pattern_stats = agent_state.get('pattern_stats', {})
        vector.append(pattern_stats.get('total_patterns', 0) / 1000.0)  # Normalize
        vector.append(pattern_stats.get('abstraction_levels', 0) / 5.0)
        vector.append(pattern_stats.get('compositions', 0) / 100.0)

        # 4. Goal dynamics
        goal_stats = agent_state.get('goal_stats', {})
        vector.append(goal_stats.get('total_goals', 0) / 200.0)
        active_goals = goal_stats.get('by_state', {}).get('active', 0)
        vector.append(active_goals / 50.0)

        # 5. Novelty and diversity
        novelty_stats = agent_state.get('novelty_stats', {})
        vector.append(novelty_stats.get('archive_size', 0) / 100.0)

        # 6. Activity patterns (if input provided)
        if input_data:
            # Characterize response to input
            for key in sorted(input_data.keys())[:3]:  # First 3 inputs
                val = input_data[key]
                if isinstance(val, (int, float)):
                    vector.append(float(val) % 1.0)  # Normalize to [0,1]

        # 7. Temporal dynamics
        vector.append(agent_state.get('cycle', 0) / 1000.0)  # Normalize

        # 8. Emergence indicators
        emergence_count = len(agent_state.get('recent_emergence', []))
        vector.append(emergence_count / 10.0)

        # Ensure vector is non-empty and has consistent length
        if len(vector) < 10:
            # Pad with zeros if needed
            vector.extend([0.0] * (10 - len(vector)))

        # Clip to reasonable range
        vector = [max(0.0, min(1.0, v)) for v in vector[:15]]  # Keep first 15 dims

        behavior = BehaviorCharacterization(
            vector=vector,
            source_type='agent',
            source_id=agent_state.get('agent_id', 'unknown'),
            context={
                'cycle': agent_state.get('cycle', 0),
                'fitness': fitness,
                'vector_length': len(vector)
            }
        )

        return behavior

    @staticmethod
    def characterize_genome(genome_stats: Dict[str, Any]) -> BehaviorCharacterization:
        """Characterize genome structure and evolution."""
        vector = []

        vector.append(genome_stats.get('total_genes', 0) / 100.0)
        vector.append(genome_stats.get('max_gene_depth', 1) / 10.0)
        vector.append(genome_stats.get('avg_generation', 0) / 50.0)
        vector.append(genome_stats.get('regulatory_connections', 0) / 50.0)
        vector.append(genome_stats.get('total_fitness', 0.0))

        # Pad to consistent length
        while len(vector) < 10:
            vector.append(0.0)

        return BehaviorCharacterization(
            vector=vector[:10],
            source_type='genome',
            context=genome_stats
        )

    @staticmethod
    def characterize_pattern_space(pattern_stats: Dict[str, Any]) -> BehaviorCharacterization:
        """Characterize pattern space exploration."""
        vector = []

        vector.append(pattern_stats.get('total_patterns', 0) / 1000.0)
        vector.append(pattern_stats.get('abstraction_levels', 0) / 5.0)
        vector.append(pattern_stats.get('compositions', 0) / 100.0)
        vector.append(pattern_stats.get('abstractions', 0) / 50.0)

        while len(vector) < 10:
            vector.append(0.0)

        return BehaviorCharacterization(
            vector=vector[:10],
            source_type='patterns',
            context=pattern_stats
        )


class NoveltyEngine:
    """
    Improved novelty engine with proper behavioral characterization.

    Fixes the bug where novelty was always 0.0.
    """

    def __init__(
        self,
        archive_size: int = 500,
        k_nearest: int = 15,
        characterization_method: str = 'agent_state'
    ):
        """
        Initialize novelty engine.

        Args:
            archive_size: Maximum size of novelty archive
            k_nearest: Number of neighbors for novelty computation
            characterization_method: How to characterize behaviors
        """
        self.archive = NoveltyArchive(max_size=archive_size, k_nearest=k_nearest)
        self.characterization_method = characterization_method

        # Characterizers (functions that extract behavior vectors)
        self.characterizers: Dict[str, Callable] = {
            'agent_state': ImprovedBehaviorCharacterization.characterize_agent_state,
            'genome': ImprovedBehaviorCharacterization.characterize_genome,
            'patterns': ImprovedBehaviorCharacterization.characterize_pattern_space
        }

        # Statistics
        self.total_characterizations = 0
        self.empty_vectors_detected = 0
        self.novelty_scores_history: List[float] = []

    def register_characterizer(
        self,
        name: str,
        func: Callable[[Any], BehaviorCharacterization]
    ):
        """Register a custom characterization function."""
        self.characterizers[name] = func

    def characterize_and_add(
        self,
        entity: Any,
        entity_type: str = 'agent_state',
        min_novelty: float = 0.0,
        input_data: Optional[Dict] = None
    ) -> float:
        """
        Characterize an entity and add to novelty archive.

        Returns novelty score (0.0 to 1.0).
        """
        self.total_characterizations += 1

        # Get appropriate characterizer
        if entity_type in self.characterizers:
            if entity_type == 'agent_state' and input_data:
                behavior = self.characterizers[entity_type](entity, input_data)
            else:
                behavior = self.characterizers[entity_type](entity)
        else:
            # Fallback: try to extract vector directly
            if isinstance(entity, dict):
                behavior = ImprovedBehaviorCharacterization.characterize_agent_state(entity, input_data)
            else:
                # Can't characterize
                return 0.0

        # Validate vector
        if not behavior.vector or all(v == 0.0 for v in behavior.vector):
            self.empty_vectors_detected += 1
            # Still add with small random perturbation to avoid identical vectors
            behavior.vector = [random.random() * 0.01 for _ in range(10)]

        # Compute novelty
        novelty = self.archive.compute_novelty(behavior)
        behavior.novelty_score = novelty

        # Add to archive
        self.archive.add(behavior, min_novelty=min_novelty)

        # Track scores
        self.novelty_scores_history.append(novelty)
        if len(self.novelty_scores_history) > 1000:
            self.novelty_scores_history.pop(0)

        return novelty

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive novelty engine statistics."""
        archive_stats = self.archive.get_stats()

        recent_avg_novelty = (
            sum(self.novelty_scores_history[-100:]) / len(self.novelty_scores_history[-100:])
            if self.novelty_scores_history else 0.0
        )

        return {
            **archive_stats,
            'total_characterizations': self.total_characterizations,
            'empty_vectors_detected': self.empty_vectors_detected,
            'recent_avg_novelty': recent_avg_novelty,
            'novelty_scores_count': len(self.novelty_scores_history),
            'characterization_methods': list(self.characterizers.keys())
        }

    def get_diversity_metrics(self) -> Dict[str, float]:
        """Get diversity metrics from novelty archive."""
        if len(self.archive.archive) < 2:
            return {
                'coverage': 0.0,
                'spread': 0.0,
                'uniformity': 0.0
            }

        behaviors = list(self.archive.archive.values())

        # Coverage: Number of unique grid cells occupied
        grid_cells = set()
        for b in behaviors:
            cell = self.archive._get_grid_cell(b.vector)
            grid_cells.add(cell)

        coverage = len(grid_cells) / (len(behaviors) + 1)

        # Spread: Average distance to centroid
        if behaviors:
            centroid = [
                sum(b.vector[i] for b in behaviors if i < len(b.vector)) / len(behaviors)
                for i in range(max(len(b.vector) for b in behaviors))
            ]

            spread = sum(
                math.sqrt(sum((b.vector[i] - centroid[i]) ** 2 for i in range(min(len(b.vector), len(centroid)))))
                for b in behaviors
            ) / len(behaviors)
        else:
            spread = 0.0

        # Uniformity: Variance of nearest neighbor distances
        nn_distances = []
        for b in behaviors:
            neighbors = self.archive.get_nearest(b, k=3)
            if neighbors:
                avg_dist = sum(d for _, d in neighbors) / len(neighbors)
                nn_distances.append(avg_dist)

        if nn_distances:
            mean_nn = sum(nn_distances) / len(nn_distances)
            variance = sum((d - mean_nn) ** 2 for d in nn_distances) / len(nn_distances)
            uniformity = 1.0 / (1.0 + variance)  # Higher is more uniform
        else:
            uniformity = 0.0

        return {
            'coverage': coverage,
            'spread': spread,
            'uniformity': uniformity
        }


# Utility function for debugging
def validate_behavior_vector(vector: List[float]) -> Dict[str, Any]:
    """Validate a behavior vector and report issues."""
    issues = []
    stats = {}

    if not vector:
        issues.append("Empty vector")
        return {'valid': False, 'issues': issues}

    if all(v == 0.0 for v in vector):
        issues.append("All zeros - no behavioral information")

    if len(vector) < 5:
        issues.append(f"Vector too short ({len(vector)} dims) - may not capture enough diversity")

    stats['length'] = len(vector)
    stats['mean'] = sum(vector) / len(vector)
    stats['variance'] = sum((v - stats['mean']) ** 2 for v in vector) / len(vector)
    stats['min'] = min(vector)
    stats['max'] = max(vector)
    stats['non_zero_dims'] = sum(1 for v in vector if v != 0.0)

    if stats['variance'] < 0.01:
        issues.append("Very low variance - behaviors may appear too similar")

    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'stats': stats
    }
