"""
AEGIS-3 Pattern Resource Management

Implements bounded pattern storage with intelligent pruning to enable
long-term open-ended evolution without performance collapse.

Key mechanisms:
1. LRU eviction - Remove least recently used patterns
2. Utility-based pruning - Keep high-value patterns
3. Similarity merging - Consolidate similar patterns
4. Diversity preservation - Maintain variety in pattern space
5. Hard capacity limits - Prevent unbounded growth

This solves the critical scalability issue discovered in validation testing.
"""

import time
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import OrderedDict
import random
import math


@dataclass
class PatternStats:
    """Statistics for a pattern."""
    creation_time: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0
    success_count: int = 0
    composition_count: int = 0  # How many times used in compositions
    abstraction_level: int = 0
    complexity: int = 1

    @property
    def success_rate(self) -> float:
        """Success rate of matching."""
        return self.success_count / max(1, self.use_count)

    @property
    def age(self) -> float:
        """Age in seconds."""
        return time.time() - self.creation_time

    @property
    def recency(self) -> float:
        """Time since last use."""
        return time.time() - self.last_used

    def utility(self, recency_weight: float = 0.3,
                success_weight: float = 0.4,
                composition_weight: float = 0.3) -> float:
        """
        Calculate utility score for this pattern.

        Higher utility = more valuable to keep.
        """
        # Recency component (normalized to [0,1], recent = higher)
        max_recency = 3600  # 1 hour max age consideration
        recency_score = max(0, 1 - (self.recency / max_recency))

        # Success component
        success_score = self.success_rate

        # Composition component (normalized)
        composition_score = min(1.0, self.composition_count / 10.0)

        # Combined utility
        utility = (recency_weight * recency_score +
                  success_weight * success_score +
                  composition_weight * composition_score)

        return utility


class BoundedPatternAlgebra:
    """
    Pattern algebra with bounded resource usage.

    Prevents the pattern explosion that caused catastrophic performance
    degradation in validation testing.
    """

    def __init__(
        self,
        max_patterns: int = 5000,
        eviction_threshold: float = 0.9,
        min_utility: float = 0.1,
        similarity_threshold: float = 0.85,
        enable_merging: bool = True
    ):
        """
        Initialize bounded pattern algebra.

        Args:
            max_patterns: Hard limit on pattern count
            eviction_threshold: Trigger eviction when usage hits this fraction
            min_utility: Minimum utility to keep a pattern
            similarity_threshold: Merge patterns above this similarity
            enable_merging: Whether to merge similar patterns
        """
        self.max_patterns = max_patterns
        self.eviction_threshold = eviction_threshold
        self.min_utility = min_utility
        self.similarity_threshold = similarity_threshold
        self.enable_merging = enable_merging

        # Pattern storage
        self.patterns: OrderedDict = OrderedDict()  # LRU ordering
        self.pattern_stats: Dict[str, PatternStats] = {}

        # Abstraction hierarchy
        self.abstraction_hierarchy: Dict[int, Set[str]] = {}

        # Statistics
        self.compositions = 0
        self.abstractions = 0
        self.specializations = 0
        self.evictions = 0
        self.merges = 0

        # Performance tracking
        self.last_prune_time = time.time()
        self.prune_count = 0

    def register(self, pattern, track_usage: bool = True) -> str:
        """
        Register a pattern with bounded storage.

        Automatically prunes when capacity is reached.
        """
        pattern_id = pattern.id

        # Check if we need to make space
        if len(self.patterns) >= self.max_patterns * self.eviction_threshold:
            self._prune_patterns()

        # Check for similar patterns (merge if enabled)
        if self.enable_merging and len(self.patterns) > 0:
            similar_id = self._find_similar_pattern(pattern)
            if similar_id:
                # Merge into existing pattern instead of adding new
                self._merge_patterns(similar_id, pattern_id)
                return similar_id

        # Add pattern
        self.patterns[pattern_id] = pattern
        self.patterns.move_to_end(pattern_id)  # Mark as most recently used

        # Initialize stats
        if pattern_id not in self.pattern_stats:
            self.pattern_stats[pattern_id] = PatternStats(
                complexity=pattern.complexity() if hasattr(pattern, 'complexity') else 1,
                abstraction_level=getattr(pattern, 'abstraction_level', 0)
            )

        # Update abstraction hierarchy
        if hasattr(pattern, 'abstraction_level'):
            level = pattern.abstraction_level
            if level not in self.abstraction_hierarchy:
                self.abstraction_hierarchy[level] = set()
            self.abstraction_hierarchy[level].add(pattern_id)

        return pattern_id

    def touch(self, pattern_id: str, success: bool = False):
        """
        Mark a pattern as used (updates LRU).

        Args:
            pattern_id: ID of pattern being used
            success: Whether the use was successful (e.g., pattern matched)
        """
        if pattern_id in self.patterns:
            # Update LRU ordering
            self.patterns.move_to_end(pattern_id)

            # Update stats
            if pattern_id in self.pattern_stats:
                stats = self.pattern_stats[pattern_id]
                stats.last_used = time.time()
                stats.use_count += 1
                if success:
                    stats.success_count += 1

    def _prune_patterns(self):
        """
        Prune low-utility patterns to maintain bounded size.

        Strategy:
        1. Calculate utility for all patterns
        2. Remove patterns below minimum utility threshold
        3. If still over capacity, remove lowest utility patterns
        4. Always preserve some diversity across abstraction levels
        """
        self.prune_count += 1
        initial_count = len(self.patterns)

        # Calculate utilities
        utilities = {}
        for pattern_id, stats in self.pattern_stats.items():
            if pattern_id in self.patterns:
                utilities[pattern_id] = stats.utility()

        # Identify patterns to remove
        to_remove = []

        # Phase 1: Remove patterns below minimum utility
        for pattern_id, utility in utilities.items():
            if utility < self.min_utility:
                to_remove.append(pattern_id)

        # Phase 2: If still over capacity, remove lowest utility
        target_size = int(self.max_patterns * 0.8)  # Prune to 80% capacity
        if len(self.patterns) - len(to_remove) > target_size:
            # Sort by utility
            sorted_patterns = sorted(utilities.items(), key=lambda x: x[1])

            # Remove lowest utility patterns, but preserve diversity
            removed_by_level = {}
            for pattern_id, utility in sorted_patterns:
                if len(self.patterns) - len(to_remove) <= target_size:
                    break

                if pattern_id in to_remove:
                    continue

                # Check diversity preservation
                stats = self.pattern_stats.get(pattern_id)
                if stats:
                    level = stats.abstraction_level
                    removed_at_level = removed_by_level.get(level, 0)
                    total_at_level = len(self.abstraction_hierarchy.get(level, set()))

                    # Don't remove if it would eliminate all patterns at this level
                    if total_at_level - removed_at_level > 1:
                        to_remove.append(pattern_id)
                        removed_by_level[level] = removed_at_level + 1

        # Execute removal
        for pattern_id in to_remove:
            if pattern_id in self.patterns:
                del self.patterns[pattern_id]
                self.evictions += 1

            # Clean up hierarchy
            if pattern_id in self.pattern_stats:
                level = self.pattern_stats[pattern_id].abstraction_level
                if level in self.abstraction_hierarchy:
                    self.abstraction_hierarchy[level].discard(pattern_id)

        self.last_prune_time = time.time()

        removed_count = initial_count - len(self.patterns)
        return removed_count

    def _find_similar_pattern(self, pattern) -> Optional[str]:
        """
        Find a pattern similar to the given one.

        Returns pattern_id of similar pattern, or None.
        """
        pattern_dict = pattern.to_dict() if hasattr(pattern, 'to_dict') else {}
        pattern_complexity = pattern.complexity() if hasattr(pattern, 'complexity') else 1

        # Sample a subset for efficiency
        sample_size = min(100, len(self.patterns))
        sample_ids = random.sample(list(self.patterns.keys()), sample_size)

        best_similarity = 0.0
        best_id = None

        for candidate_id in sample_ids:
            candidate = self.patterns[candidate_id]
            similarity = self._compute_similarity(pattern, candidate)

            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_id = candidate_id

        return best_id

    def _compute_similarity(self, pattern1, pattern2) -> float:
        """
        Compute structural similarity between two patterns.

        Returns value in [0, 1] where 1 = identical.
        """
        # Get dictionaries
        dict1 = pattern1.to_dict() if hasattr(pattern1, 'to_dict') else {'type': type(pattern1).__name__}
        dict2 = pattern2.to_dict() if hasattr(pattern2, 'to_dict') else {'type': type(pattern2).__name__}

        similarity = 0.0

        # Type similarity
        if dict1.get('type') == dict2.get('type'):
            similarity += 0.4

        # Complexity similarity
        comp1 = pattern1.complexity() if hasattr(pattern1, 'complexity') else 1
        comp2 = pattern2.complexity() if hasattr(pattern2, 'complexity') else 1
        if comp1 > 0 and comp2 > 0:
            comp_sim = 1.0 - abs(comp1 - comp2) / max(comp1, comp2)
            similarity += 0.3 * comp_sim

        # Structural similarity (simplified)
        # In a full implementation, would do deep structural comparison
        if hasattr(pattern1, 'name') and hasattr(pattern2, 'name'):
            if pattern1.name == pattern2.name:
                similarity += 0.3

        return min(1.0, similarity)

    def _merge_patterns(self, keep_id: str, merge_id: str):
        """
        Merge two similar patterns, keeping statistics from both.
        """
        if keep_id in self.pattern_stats and merge_id in self.pattern_stats:
            keep_stats = self.pattern_stats[keep_id]
            merge_stats = self.pattern_stats[merge_id]

            # Combine statistics
            keep_stats.use_count += merge_stats.use_count
            keep_stats.success_count += merge_stats.success_count
            keep_stats.composition_count += merge_stats.composition_count

            # Update last used to more recent
            keep_stats.last_used = max(keep_stats.last_used, merge_stats.last_used)

            self.merges += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the pattern algebra."""
        total_utility = sum(
            stats.utility()
            for pattern_id, stats in self.pattern_stats.items()
            if pattern_id in self.patterns
        )

        avg_utility = total_utility / len(self.patterns) if self.patterns else 0

        return {
            'total_patterns': len(self.patterns),
            'max_patterns': self.max_patterns,
            'capacity_used': len(self.patterns) / self.max_patterns,
            'compositions': self.compositions,
            'abstractions': self.abstractions,
            'specializations': self.specializations,
            'evictions': self.evictions,
            'merges': self.merges,
            'prune_count': self.prune_count,
            'avg_utility': avg_utility,
            'abstraction_levels': len(self.abstraction_hierarchy),
            'patterns_by_level': {
                level: len(patterns)
                for level, patterns in self.abstraction_hierarchy.items()
            }
        }


class AdaptiveResourceManager:
    """
    Adaptive resource management for entire AEGIS system.

    Monitors resource usage and adjusts limits dynamically based on
    available resources and performance targets.
    """

    def __init__(
        self,
        target_cycles_per_second: float = 50.0,
        measurement_window: int = 100
    ):
        self.target_cycles_per_second = target_cycles_per_second
        self.measurement_window = measurement_window

        # Performance tracking
        self.cycle_times: List[float] = []
        self.last_cycle_time = time.time()

        # Resource limits (will be adapted)
        self.max_patterns = 5000
        self.max_goals = 200
        self.max_genes = 100

    def record_cycle(self):
        """Record completion of one cycle."""
        now = time.time()
        cycle_time = now - self.last_cycle_time
        self.cycle_times.append(cycle_time)

        # Keep only recent measurements
        if len(self.cycle_times) > self.measurement_window:
            self.cycle_times.pop(0)

        self.last_cycle_time = now

    def get_current_rate(self) -> float:
        """Get current cycles per second."""
        if not self.cycle_times:
            return 0.0

        avg_cycle_time = sum(self.cycle_times) / len(self.cycle_times)
        return 1.0 / avg_cycle_time if avg_cycle_time > 0 else 0.0

    def adapt_limits(self) -> Dict[str, int]:
        """
        Adapt resource limits based on performance.

        If running too slow, reduce limits.
        If running fast enough, can increase limits.
        """
        current_rate = self.get_current_rate()

        if current_rate < self.target_cycles_per_second * 0.5:
            # Running much too slow - reduce limits aggressively
            self.max_patterns = int(self.max_patterns * 0.7)
            self.max_goals = int(self.max_goals * 0.8)
            self.max_genes = int(self.max_genes * 0.9)
        elif current_rate < self.target_cycles_per_second:
            # Running slow - reduce limits moderately
            self.max_patterns = int(self.max_patterns * 0.9)
        elif current_rate > self.target_cycles_per_second * 1.5:
            # Running fast - can increase limits
            self.max_patterns = int(self.max_patterns * 1.1)
            self.max_goals = min(300, int(self.max_goals * 1.05))

        # Apply bounds
        self.max_patterns = max(1000, min(10000, self.max_patterns))
        self.max_goals = max(50, min(300, self.max_goals))
        self.max_genes = max(20, min(150, self.max_genes))

        return {
            'max_patterns': self.max_patterns,
            'max_goals': self.max_goals,
            'max_genes': self.max_genes,
            'current_rate': current_rate,
            'target_rate': self.target_cycles_per_second
        }
