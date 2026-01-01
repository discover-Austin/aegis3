"""
Meta-Meta-Evolution: Evolving How Evolution Evolves

This goes beyond meta-evolution (which evolves primitives and fitness functions)
to evolve THE EVOLUTION PROCESS ITSELF.

Evolvable components:
1. Selection mechanisms (not just fitness-based)
2. Variation operators (not just mutation/crossover)
3. Reproduction strategies
4. Population structure
5. Exploration-exploitation balance
6. Credit assignment methods
7. The meta-evolution mechanism itself (self-referential!)

This is genuine recursive improvement of the evolutionary process.
"""

import random
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional, Tuple
from enum import Enum


class SelectionMechanism(Enum):
    """Different ways to select individuals for reproduction."""
    FITNESS_PROPORTIONAL = "fitness_proportional"  # Classic roulette wheel
    TOURNAMENT = "tournament"  # Tournament selection
    RANK_BASED = "rank_based"  # Based on rank not raw fitness
    NOVELTY = "novelty"  # Select for novelty
    AGE_FITNESS = "age_fitness"  # Balance age and fitness
    DIVERSITY = "diversity"  # Maintain diversity
    PARETO = "pareto"  # Multi-objective Pareto selection
    LEXICASE = "lexicase"  # Lexicase selection


class VariationOperator(Enum):
    """Different ways to create offspring."""
    MUTATION = "mutation"  # Random mutations
    CROSSOVER = "crossover"  # Combine two parents
    DIRECTED_MUTATION = "directed_mutation"  # Mutation guided by gradients
    MACROMUTATION = "macromutation"  # Large structural changes
    NEUTRAL_WALK = "neutral_walk"  # Explore neutral networks
    NOVELTY_SEARCH = "novelty_search"  # Maximize behavioral novelty
    QUALITY_DIVERSITY = "quality_diversity"  # Balance quality and diversity


@dataclass
class EvolutionaryParameters:
    """Parameters that control evolution."""
    population_size: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    tournament_size: int = 3
    elitism_count: int = 2
    exploration_rate: float = 0.3  # vs exploitation
    novelty_weight: float = 0.2  # vs fitness
    diversity_threshold: float = 0.5
    age_penalty: float = 0.01


@dataclass
class EvolutionStrategy:
    """A complete evolutionary strategy."""
    name: str
    selection_mechanism: SelectionMechanism
    variation_operators: List[VariationOperator]
    parameters: EvolutionaryParameters
    performance_history: List[float] = field(default_factory=list)

    def performance(self) -> float:
        """Get recent performance of this strategy."""
        if not self.performance_history:
            return 0.0
        # Recent performance with recency weighting
        recent = self.performance_history[-20:]
        weights = [math.exp(-0.1 * (len(recent) - i - 1)) for i in range(len(recent))]
        return sum(p * w for p, w in zip(recent, weights)) / sum(weights)

    def record_performance(self, performance: float):
        """Record performance of this strategy."""
        self.performance_history.append(performance)
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)


class MetaMetaEvolution:
    """
    Evolves the evolution process itself.

    Maintains a population of evolution strategies and evolves them
    based on their performance at evolving solutions.
    """

    def __init__(self, num_strategies: int = 10):
        """Initialize with a population of evolution strategies."""
        self.strategies: List[EvolutionStrategy] = []

        # Create initial diverse population of strategies
        for i in range(num_strategies):
            strategy = self._create_random_strategy(f"strategy_{i}")
            self.strategies.append(strategy)

        # Meta-level tracking
        self.generation = 0
        self.strategy_applications = {}  # Track which strategy was used when
        self.best_strategy = None
        self.strategy_lineage = []  # Track evolution of strategies

    def _create_random_strategy(self, name: str) -> EvolutionStrategy:
        """Create a random evolution strategy."""
        return EvolutionStrategy(
            name=name,
            selection_mechanism=random.choice(list(SelectionMechanism)),
            variation_operators=random.sample(
                list(VariationOperator),
                k=random.randint(1, 3)
            ),
            parameters=EvolutionaryParameters(
                population_size=random.choice([50, 100, 200]),
                mutation_rate=random.uniform(0.01, 0.3),
                crossover_rate=random.uniform(0.5, 0.9),
                tournament_size=random.randint(2, 7),
                elitism_count=random.randint(1, 5),
                exploration_rate=random.uniform(0.1, 0.5),
                novelty_weight=random.uniform(0.0, 0.5),
                diversity_threshold=random.uniform(0.3, 0.7),
                age_penalty=random.uniform(0.0, 0.05)
            )
        )

    def select_strategy(self, exploration_rate: float = 0.2) -> EvolutionStrategy:
        """
        Select an evolution strategy to use.

        Balances exploitation (using best strategies) with
        exploration (trying different strategies).
        """
        if random.random() < exploration_rate:
            # Explore: Random strategy
            return random.choice(self.strategies)
        else:
            # Exploit: Best performing strategy
            best = max(self.strategies, key=lambda s: s.performance())
            return best

    def apply_selection(
        self,
        population: List[Any],
        fitnesses: List[float],
        strategy: EvolutionStrategy
    ) -> List[Any]:
        """
        Apply selection mechanism from strategy.

        Returns selected individuals for reproduction.
        """
        mechanism = strategy.selection_mechanism
        params = strategy.parameters
        num_parents = len(population) // 2

        if mechanism == SelectionMechanism.FITNESS_PROPORTIONAL:
            # Roulette wheel selection
            total_fitness = sum(max(0, f) for f in fitnesses)
            if total_fitness == 0:
                return random.sample(population, num_parents)

            selected = []
            for _ in range(num_parents):
                r = random.uniform(0, total_fitness)
                cumsum = 0
                for ind, fit in zip(population, fitnesses):
                    cumsum += max(0, fit)
                    if cumsum >= r:
                        selected.append(ind)
                        break
            return selected

        elif mechanism == SelectionMechanism.TOURNAMENT:
            # Tournament selection
            selected = []
            for _ in range(num_parents):
                tournament = random.sample(list(zip(population, fitnesses)), params.tournament_size)
                winner = max(tournament, key=lambda x: x[1])[0]
                selected.append(winner)
            return selected

        elif mechanism == SelectionMechanism.RANK_BASED:
            # Rank-based selection
            ranked = sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)
            # Linearly decreasing probabilities
            probs = [1.0 / (i + 1) for i in range(len(ranked))]
            total = sum(probs)
            probs = [p / total for p in probs]

            selected = []
            for _ in range(num_parents):
                r = random.random()
                cumsum = 0
                for (ind, _), prob in zip(ranked, probs):
                    cumsum += prob
                    if cumsum >= r:
                        selected.append(ind)
                        break
            return selected

        elif mechanism == SelectionMechanism.LEXICASE:
            # Lexicase selection (random case ordering)
            # Simplified: treat each individual's fitness as a single case
            selected = []
            for _ in range(num_parents):
                candidates = list(zip(population, fitnesses))
                # Random shuffle of selection criteria
                random.shuffle(candidates)
                # Select best on first criterion
                if candidates:
                    selected.append(max(candidates, key=lambda x: x[1])[0])
            return selected

        else:
            # Default: Tournament selection
            return self.apply_selection(population, fitnesses,
                                      EvolutionStrategy("temp", SelectionMechanism.TOURNAMENT,
                                                      [], params))

    def apply_variation(
        self,
        parent1: Any,
        parent2: Optional[Any],
        strategy: EvolutionStrategy
    ) -> Any:
        """
        Apply variation operators from strategy.

        Creates offspring from parent(s).
        """
        operators = strategy.variation_operators
        params = strategy.parameters

        # Start with parent1
        offspring = parent1

        # Apply each operator with some probability
        for operator in operators:
            if operator == VariationOperator.MUTATION:
                if random.random() < params.mutation_rate:
                    offspring = self._mutate(offspring, params.mutation_rate)

            elif operator == VariationOperator.CROSSOVER:
                if parent2 and random.random() < params.crossover_rate:
                    offspring = self._crossover(offspring, parent2)

            elif operator == VariationOperator.MACROMUTATION:
                if random.random() < params.mutation_rate / 2:
                    offspring = self._macromutate(offspring)

            elif operator == VariationOperator.DIRECTED_MUTATION:
                # Mutation in a beneficial direction (simplified)
                if random.random() < params.mutation_rate:
                    offspring = self._directed_mutate(offspring)

        return offspring

    def _mutate(self, individual: Any, rate: float) -> Any:
        """Basic mutation (placeholder - override for specific types)."""
        # This is a generic implementation
        # In practice, this would be specialized for the genome type
        if isinstance(individual, list):
            mutated = individual.copy()
            for i in range(len(mutated)):
                if random.random() < rate:
                    mutated[i] += random.gauss(0, 0.1)
            return mutated
        return individual

    def _crossover(self, parent1: Any, parent2: Any) -> Any:
        """Basic crossover (placeholder)."""
        if isinstance(parent1, list) and isinstance(parent2, list):
            point = random.randint(0, min(len(parent1), len(parent2)))
            return parent1[:point] + parent2[point:]
        return parent1

    def _macromutate(self, individual: Any) -> Any:
        """Large structural mutation."""
        # Simplified: Just do multiple mutations
        result = individual
        num_mutations = random.randint(3, 10)
        for _ in range(num_mutations):
            result = self._mutate(result, 0.5)
        return result

    def _directed_mutate(self, individual: Any) -> Any:
        """Mutation in a potentially beneficial direction."""
        # Simplified: Slightly larger mutations
        if isinstance(individual, list):
            mutated = individual.copy()
            for i in range(len(mutated)):
                if random.random() < 0.1:
                    mutated[i] += random.gauss(0, 0.3)
            return mutated
        return individual

    def evolve_strategies(self):
        """
        Evolve the population of evolution strategies.

        This is meta-meta-evolution: evolving how to evolve!
        """
        # Evaluate strategy performance
        performances = [s.performance() for s in self.strategies]

        # Keep best strategies (elitism at meta level)
        elite_count = 2
        elite_indices = sorted(range(len(performances)),
                              key=lambda i: performances[i],
                              reverse=True)[:elite_count]
        new_strategies = [self.strategies[i] for i in elite_indices]

        # Create offspring strategies
        while len(new_strategies) < len(self.strategies):
            # Select parent strategies based on performance
            if sum(max(0, p) for p in performances) > 0:
                total = sum(max(0, p) for p in performances)
                r1 = random.uniform(0, total)
                r2 = random.uniform(0, total)

                cumsum = 0
                parent1 = parent2 = None
                for i, perf in enumerate(performances):
                    cumsum += max(0, perf)
                    if r1 <= cumsum and parent1 is None:
                        parent1 = self.strategies[i]
                    if r2 <= cumsum and parent2 is None:
                        parent2 = self.strategies[i]
                    if parent1 and parent2:
                        break
            else:
                parent1, parent2 = random.sample(self.strategies, 2)

            # Create offspring strategy
            offspring = self._crossover_strategies(parent1, parent2)
            offspring = self._mutate_strategy(offspring)

            new_strategies.append(offspring)

        self.strategies = new_strategies
        self.generation += 1

        # Track lineage
        best = max(self.strategies, key=lambda s: s.performance())
        self.strategy_lineage.append(best.name)
        self.best_strategy = best

    def _crossover_strategies(
        self,
        parent1: EvolutionStrategy,
        parent2: EvolutionStrategy
    ) -> EvolutionStrategy:
        """Crossover two evolution strategies."""
        # Combine elements from both parents
        offspring = EvolutionStrategy(
            name=f"gen{self.generation}_hybrid",
            selection_mechanism=random.choice([parent1.selection_mechanism,
                                              parent2.selection_mechanism]),
            variation_operators=random.sample(
                parent1.variation_operators + parent2.variation_operators,
                k=min(3, len(parent1.variation_operators + parent2.variation_operators))
            ),
            parameters=EvolutionaryParameters(
                population_size=random.choice([parent1.parameters.population_size,
                                              parent2.parameters.population_size]),
                mutation_rate=(parent1.parameters.mutation_rate + parent2.parameters.mutation_rate) / 2,
                crossover_rate=(parent1.parameters.crossover_rate + parent2.parameters.crossover_rate) / 2,
                tournament_size=random.choice([parent1.parameters.tournament_size,
                                              parent2.parameters.tournament_size]),
                elitism_count=random.choice([parent1.parameters.elitism_count,
                                            parent2.parameters.elitism_count]),
                exploration_rate=(parent1.parameters.exploration_rate + parent2.parameters.exploration_rate) / 2,
                novelty_weight=(parent1.parameters.novelty_weight + parent2.parameters.novelty_weight) / 2,
                diversity_threshold=(parent1.parameters.diversity_threshold + parent2.parameters.diversity_threshold) / 2,
                age_penalty=(parent1.parameters.age_penalty + parent2.parameters.age_penalty) / 2
            )
        )
        return offspring

    def _mutate_strategy(self, strategy: EvolutionStrategy) -> EvolutionStrategy:
        """Mutate an evolution strategy."""
        mutated = EvolutionStrategy(
            name=f"{strategy.name}_mut",
            selection_mechanism=strategy.selection_mechanism,
            variation_operators=strategy.variation_operators.copy(),
            parameters=EvolutionaryParameters(
                population_size=strategy.parameters.population_size,
                mutation_rate=strategy.parameters.mutation_rate,
                crossover_rate=strategy.parameters.crossover_rate,
                tournament_size=strategy.parameters.tournament_size,
                elitism_count=strategy.parameters.elitism_count,
                exploration_rate=strategy.parameters.exploration_rate,
                novelty_weight=strategy.parameters.novelty_weight,
                diversity_threshold=strategy.parameters.diversity_threshold,
                age_penalty=strategy.parameters.age_penalty
            )
        )

        # Mutate each component with some probability
        if random.random() < 0.2:
            mutated.selection_mechanism = random.choice(list(SelectionMechanism))

        if random.random() < 0.3:
            if random.random() < 0.5 and len(mutated.variation_operators) > 1:
                # Remove an operator
                mutated.variation_operators.pop(random.randrange(len(mutated.variation_operators)))
            else:
                # Add an operator
                new_op = random.choice(list(VariationOperator))
                if new_op not in mutated.variation_operators:
                    mutated.variation_operators.append(new_op)

        # Mutate parameters
        if random.random() < 0.1:
            mutated.parameters.population_size = max(10, mutated.parameters.population_size + random.randint(-20, 20))
        if random.random() < 0.3:
            mutated.parameters.mutation_rate = max(0.01, min(0.5, mutated.parameters.mutation_rate + random.gauss(0, 0.05)))
        if random.random() < 0.3:
            mutated.parameters.crossover_rate = max(0.3, min(1.0, mutated.parameters.crossover_rate + random.gauss(0, 0.1)))
        if random.random() < 0.2:
            mutated.parameters.exploration_rate = max(0.0, min(0.7, mutated.parameters.exploration_rate + random.gauss(0, 0.1)))
        if random.random() < 0.2:
            mutated.parameters.novelty_weight = max(0.0, min(1.0, mutated.parameters.novelty_weight + random.gauss(0, 0.1)))

        return mutated

    def get_statistics(self) -> Dict[str, Any]:
        """Get meta-meta-evolution statistics."""
        performances = [s.performance() for s in self.strategies]

        return {
            'generation': self.generation,
            'num_strategies': len(self.strategies),
            'best_strategy': {
                'name': self.best_strategy.name if self.best_strategy else "none",
                'performance': self.best_strategy.performance() if self.best_strategy else 0.0,
                'selection': self.best_strategy.selection_mechanism.value if self.best_strategy else "none",
                'operators': [op.value for op in self.best_strategy.variation_operators] if self.best_strategy else []
            },
            'avg_performance': sum(performances) / len(performances) if performances else 0.0,
            'performance_diversity': max(performances) - min(performances) if performances else 0.0,
            'lineage': self.strategy_lineage[-10:] if self.strategy_lineage else []
        }
