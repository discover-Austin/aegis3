"""
MAP-Elites: Illuminating the Search Space

Jean-Baptiste Mouret and Jeff Clune, 2015

Quality-Diversity algorithm that:
- Maintains archive of diverse, high-performing solutions
- Uses behavior descriptors to define diversity
- Illuminates the space of possible behaviors
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Callable
import copy


@dataclass
class Elite:
    """Elite individual in MAP-Elites archive."""
    genotype: Any  # Genome representation
    fitness: float
    behavior: Tuple[float, ...]  # Behavior descriptor
    age: int = 0

    def copy(self) -> 'Elite':
        """Create a deep copy."""
        return Elite(
            genotype=copy.deepcopy(self.genotype),
            fitness=self.fitness,
            behavior=self.behavior,
            age=self.age
        )


class MAPElites:
    """
    MAP-Elites: Multi-dimensional Archive of Phenotypic Elites

    Maintains an archive organized by behavior descriptors.
    Each cell contains the highest-performing solution with that behavior.

    Key insight: Search for both quality AND diversity.
    """

    def __init__(
        self,
        behavior_dimensions: int = 2,
        behavior_ranges: Optional[List[Tuple[float, float]]] = None,
        bins_per_dimension: int = 10,
        mutation_rate: float = 0.1,
        mutation_strength: float = 0.2
    ):
        """
        Initialize MAP-Elites.

        Args:
            behavior_dimensions: Number of behavior descriptor dimensions
            behavior_ranges: Min/max for each dimension (defaults to [0,1] for each)
            bins_per_dimension: Resolution of discretization
            mutation_rate: Probability of mutating each gene
            mutation_strength: Strength of mutations
        """
        self.behavior_dimensions = behavior_dimensions
        self.bins_per_dimension = bins_per_dimension
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

        if behavior_ranges is None:
            self.behavior_ranges = [(0.0, 1.0)] * behavior_dimensions
        else:
            self.behavior_ranges = behavior_ranges

        # Archive: maps bin indices to elites
        self.archive: Dict[Tuple[int, ...], Elite] = {}

        self.generation = 0
        self.total_evaluations = 0

    def _discretize_behavior(self, behavior: Tuple[float, ...]) -> Tuple[int, ...]:
        """
        Convert continuous behavior to discrete bin indices.

        Example: behavior=(0.37, 0.82) with 10 bins -> (3, 8)
        """
        indices = []
        for i, value in enumerate(behavior):
            min_val, max_val = self.behavior_ranges[i]

            # Clamp to range
            value = max(min_val, min(max_val, value))

            # Convert to bin index
            if max_val > min_val:
                normalized = (value - min_val) / (max_val - min_val)
            else:
                normalized = 0.5

            bin_idx = int(normalized * self.bins_per_dimension)
            bin_idx = min(bin_idx, self.bins_per_dimension - 1)

            indices.append(bin_idx)

        return tuple(indices)

    def add_to_archive(self, genotype: Any, fitness: float, behavior: Tuple[float, ...]) -> bool:
        """
        Add individual to archive if it's the best in its niche.

        Returns True if added (niche was empty or fitness improved).
        """
        bin_idx = self._discretize_behavior(behavior)

        # Check if niche is empty or this is better
        if bin_idx not in self.archive or fitness > self.archive[bin_idx].fitness:
            self.archive[bin_idx] = Elite(
                genotype=copy.deepcopy(genotype),
                fitness=fitness,
                behavior=behavior,
                age=0
            )
            return True

        return False

    def evolve(
        self,
        initial_population: List[Any],
        fitness_fn: Callable[[Any], float],
        behavior_fn: Callable[[Any], Tuple[float, ...]],
        iterations: int = 10000,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Run MAP-Elites algorithm.

        Args:
            initial_population: Starting genotypes
            fitness_fn: Function mapping genotype -> fitness
            behavior_fn: Function mapping genotype -> behavior descriptor
            iterations: Number of evolutionary iterations
            batch_size: Evaluations per iteration

        Returns:
            Dictionary with statistics and final archive
        """
        # Initialize archive with random solutions
        for genotype in initial_population:
            fitness = fitness_fn(genotype)
            behavior = behavior_fn(genotype)
            self.add_to_archive(genotype, fitness, behavior)
            self.total_evaluations += 1

        history = {
            'coverage': [],
            'max_fitness': [],
            'mean_fitness': [],
            'qd_score': []
        }

        # Main loop
        for iteration in range(iterations):
            # Generate batch of new solutions
            for _ in range(batch_size):
                # Select random elite from archive
                if not self.archive:
                    continue

                parent_elite = random.choice(list(self.archive.values()))

                # Mutate
                child_genotype = self._mutate(parent_elite.genotype)

                # Evaluate
                child_fitness = fitness_fn(child_genotype)
                child_behavior = behavior_fn(child_genotype)

                # Add to archive
                self.add_to_archive(child_genotype, child_fitness, child_behavior)
                self.total_evaluations += 1

            # Age all elites
            for elite in self.archive.values():
                elite.age += 1

            # Track statistics
            stats = self.get_stats()
            history['coverage'].append(stats['coverage'])
            history['max_fitness'].append(stats['max_fitness'])
            history['mean_fitness'].append(stats['mean_fitness'])
            history['qd_score'].append(stats['qd_score'])

            self.generation += 1

        return {
            'archive': self.archive,
            'history': history,
            'final_stats': self.get_stats()
        }

    def _mutate(self, genotype: Any) -> Any:
        """
        Mutate genotype.

        Assumes genotype is a list/dict of floats. Override for custom types.
        """
        child = copy.deepcopy(genotype)

        if isinstance(child, list):
            for i in range(len(child)):
                if random.random() < self.mutation_rate:
                    child[i] += random.gauss(0, self.mutation_strength)

        elif isinstance(child, dict):
            for key in child:
                if isinstance(child[key], (int, float)):
                    if random.random() < self.mutation_rate:
                        child[key] += random.gauss(0, self.mutation_strength)

        return child

    def get_stats(self) -> Dict[str, Any]:
        """Get current archive statistics."""
        if not self.archive:
            return {
                'coverage': 0.0,
                'max_fitness': 0.0,
                'mean_fitness': 0.0,
                'qd_score': 0.0,
                'num_elites': 0
            }

        # Coverage: percentage of bins filled
        total_bins = self.bins_per_dimension ** self.behavior_dimensions
        coverage = len(self.archive) / total_bins

        # Fitness statistics
        fitnesses = [elite.fitness for elite in self.archive.values()]
        max_fitness = max(fitnesses)
        mean_fitness = sum(fitnesses) / len(fitnesses)

        # QD-score: sum of all fitnesses (measures both quality and diversity)
        qd_score = sum(fitnesses)

        return {
            'coverage': coverage,
            'max_fitness': max_fitness,
            'mean_fitness': mean_fitness,
            'qd_score': qd_score,
            'num_elites': len(self.archive),
            'total_evaluations': self.total_evaluations
        }

    def get_best(self) -> Optional[Elite]:
        """Get highest-fitness elite from archive."""
        if not self.archive:
            return None
        return max(self.archive.values(), key=lambda e: e.fitness)

    def get_archive_grid(self) -> Dict[Tuple[int, ...], float]:
        """
        Get archive as grid of fitnesses.

        Returns dict mapping bin indices to fitness values.
        """
        grid = {}
        for bin_idx, elite in self.archive.items():
            grid[bin_idx] = elite.fitness
        return grid

    def visualize_2d(self) -> str:
        """
        Create ASCII visualization for 2D behavior space.

        Only works when behavior_dimensions == 2.
        """
        if self.behavior_dimensions != 2:
            return "Visualization only available for 2D behavior spaces"

        grid = [[' ' for _ in range(self.bins_per_dimension)]
                for _ in range(self.bins_per_dimension)]

        # Get fitness range for normalization
        if not self.archive:
            return "Empty archive"

        fitnesses = [e.fitness for e in self.archive.values()]
        min_fit = min(fitnesses)
        max_fit = max(fitnesses)
        fit_range = max_fit - min_fit if max_fit > min_fit else 1.0

        # Fill grid
        for (i, j), elite in self.archive.items():
            # Normalize fitness to 0-9 scale
            normalized = (elite.fitness - min_fit) / fit_range
            char_idx = int(normalized * 9)
            chars = ' .:-=+*#%@'
            grid[j][i] = chars[char_idx]

        # Build string
        result = []
        result.append("MAP-Elites Archive (2D)")
        result.append("=" * (self.bins_per_dimension + 2))

        for row in reversed(grid):
            result.append('|' + ''.join(row) + '|')

        result.append("=" * (self.bins_per_dimension + 2))
        result.append(f"Coverage: {self.get_stats()['coverage']:.1%}")
        result.append(f"Max fitness: {max_fit:.3f}")

        return '\n'.join(result)


class CVTMAPElites(MAPElites):
    """
    CVT-MAP-Elites: Using Centroidal Voronoi Tessellation

    More efficient for high-dimensional behavior spaces.
    Uses clustering instead of regular grid.
    """

    def __init__(
        self,
        behavior_dimensions: int = 2,
        num_niches: int = 100,
        mutation_rate: float = 0.1,
        mutation_strength: float = 0.2
    ):
        """
        Initialize CVT-MAP-Elites.

        Args:
            behavior_dimensions: Number of behavior descriptor dimensions
            num_niches: Number of niches (centroids)
            mutation_rate: Probability of mutating each gene
            mutation_strength: Strength of mutations
        """
        super().__init__(
            behavior_dimensions=behavior_dimensions,
            bins_per_dimension=0,  # Not used in CVT
            mutation_rate=mutation_rate,
            mutation_strength=mutation_strength
        )

        self.num_niches = num_niches

        # Generate random centroids in behavior space
        self.centroids: List[Tuple[float, ...]] = []
        for _ in range(num_niches):
            centroid = tuple(random.random() for _ in range(behavior_dimensions))
            self.centroids.append(centroid)

        # Archive maps centroid index to elite
        self.archive: Dict[int, Elite] = {}

    def _discretize_behavior(self, behavior: Tuple[float, ...]) -> int:
        """
        Find nearest centroid for behavior.

        Returns centroid index instead of bin tuple.
        """
        if not self.centroids:
            return 0

        # Find nearest centroid (Euclidean distance)
        min_dist = float('inf')
        nearest_idx = 0

        for i, centroid in enumerate(self.centroids):
            dist = sum((b - c) ** 2 for b, c in zip(behavior, centroid)) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def add_to_archive(self, genotype: Any, fitness: float, behavior: Tuple[float, ...]) -> bool:
        """Add individual to archive using CVT."""
        niche_idx = self._discretize_behavior(behavior)

        if niche_idx not in self.archive or fitness > self.archive[niche_idx].fitness:
            self.archive[niche_idx] = Elite(
                genotype=copy.deepcopy(genotype),
                fitness=fitness,
                behavior=behavior,
                age=0
            )
            return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get current archive statistics."""
        if not self.archive:
            return {
                'coverage': 0.0,
                'max_fitness': 0.0,
                'mean_fitness': 0.0,
                'qd_score': 0.0,
                'num_elites': 0
            }

        coverage = len(self.archive) / self.num_niches

        fitnesses = [elite.fitness for elite in self.archive.values()]
        max_fitness = max(fitnesses)
        mean_fitness = sum(fitnesses) / len(fitnesses)
        qd_score = sum(fitnesses)

        return {
            'coverage': coverage,
            'max_fitness': max_fitness,
            'mean_fitness': mean_fitness,
            'qd_score': qd_score,
            'num_elites': len(self.archive),
            'total_evaluations': self.total_evaluations
        }
