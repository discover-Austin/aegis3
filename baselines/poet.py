"""
POET: Paired Open-Ended Trailblazer

Wang et al., 2019

Co-evolution of agents and environments:
- Environments evolve to be challenging but solvable
- Agents transfer between environments
- Unbounded generation of novel challenges
"""

import random
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum


class EnvironmentDifficulty(Enum):
    """Difficulty level of environment."""
    TRIVIAL = "trivial"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNSOLVABLE = "unsolvable"


@dataclass
class POETEnvironment:
    """Environment in POET."""
    env_id: int
    parameters: Dict[str, Any]
    difficulty_estimate: float = 0.5  # 0-1
    age: int = 0
    solved: bool = False
    best_agent_fitness: float = 0.0

    def copy(self) -> 'POETEnvironment':
        """Create a copy of this environment."""
        return POETEnvironment(
            env_id=self.env_id,
            parameters=copy.deepcopy(self.parameters),
            difficulty_estimate=self.difficulty_estimate,
            age=self.age,
            solved=self.solved,
            best_agent_fitness=self.best_agent_fitness
        )


@dataclass
class POETAgent:
    """Agent in POET."""
    agent_id: int
    genotype: Any  # Agent representation
    fitness: float = 0.0
    environment_id: Optional[int] = None

    def copy(self) -> 'POETAgent':
        """Create a copy of this agent."""
        return POETAgent(
            agent_id=self.agent_id,
            genotype=copy.deepcopy(self.genotype),
            fitness=self.fitness,
            environment_id=self.environment_id
        )


@dataclass
class POETPair:
    """Agent-Environment pair in POET."""
    environment: POETEnvironment
    agent: POETAgent

    def copy(self) -> 'POETPair':
        """Create a copy of this pair."""
        return POETPair(
            environment=self.environment.copy(),
            agent=self.agent.copy()
        )


class POET:
    """
    POET: Paired Open-Ended Trailblazer

    Key ideas:
    1. Co-evolve agents AND environments
    2. Environments should be challenging but solvable
    3. Agents can transfer between environments
    4. Create unbounded curriculum
    """

    def __init__(
        self,
        initial_env_params: Dict[str, Any],
        agent_mutation_rate: float = 0.1,
        env_mutation_rate: float = 0.2,
        transfer_interval: int = 10,
        mc_lower: float = 0.05,  # Minimal criterion lower bound
        mc_upper: float = 0.95,  # Minimal criterion upper bound
        max_pairs: int = 20
    ):
        """
        Initialize POET.

        Args:
            initial_env_params: Parameters for initial environment
            agent_mutation_rate: Rate of agent mutation
            env_mutation_rate: Rate of environment mutation
            transfer_interval: Generations between transfer attempts
            mc_lower: Lower bound for minimal criterion (too easy)
            mc_upper: Upper bound for minimal criterion (too hard)
            max_pairs: Maximum number of environment-agent pairs
        """
        self.agent_mutation_rate = agent_mutation_rate
        self.env_mutation_rate = env_mutation_rate
        self.transfer_interval = transfer_interval
        self.mc_lower = mc_lower
        self.mc_upper = mc_upper
        self.max_pairs = max_pairs

        # Active pairs
        self.pairs: List[POETPair] = []

        # Archive of all environments ever created
        self.environment_archive: List[POETEnvironment] = []

        self.generation = 0
        self.next_env_id = 0
        self.next_agent_id = 0

    def run(
        self,
        initial_agent: Any,
        fitness_fn: Callable[[Any, POETEnvironment], float],
        mutate_agent_fn: Callable[[Any], Any],
        mutate_env_fn: Callable[[POETEnvironment], POETEnvironment],
        generations: int = 100
    ) -> Dict[str, Any]:
        """
        Run POET algorithm.

        Args:
            initial_agent: Starting agent genotype
            fitness_fn: Function (agent, env) -> fitness
            mutate_agent_fn: Function to mutate agent genotype
            mutate_env_fn: Function to mutate environment
            generations: Number of generations to run

        Returns:
            Dictionary with results and statistics
        """
        # Initialize with first environment-agent pair
        if not self.pairs:
            env = POETEnvironment(env_id=self.next_env_id, parameters={})
            self.next_env_id += 1

            agent = POETAgent(
                agent_id=self.next_agent_id,
                genotype=copy.deepcopy(initial_agent),
                environment_id=env.env_id
            )
            self.next_agent_id += 1

            # Evaluate initial pair
            agent.fitness = fitness_fn(agent.genotype, env)
            env.best_agent_fitness = agent.fitness

            self.pairs.append(POETPair(environment=env, agent=agent))
            self.environment_archive.append(env.copy())

        history = {
            'num_pairs': [],
            'max_fitness': [],
            'avg_fitness': [],
            'num_environments_created': []
        }

        # Main loop
        for gen in range(generations):
            # 1. Evolve agents within their environments
            self._evolve_agents(fitness_fn, mutate_agent_fn)

            # 2. Reproduce environments
            if gen % 5 == 0:  # Every 5 generations
                self._reproduce_environments(fitness_fn, mutate_env_fn)

            # 3. Transfer agents between environments
            if gen % self.transfer_interval == 0:
                self._transfer_agents(fitness_fn)

            # 4. Prune pairs
            self._prune_pairs()

            # Age all pairs
            for pair in self.pairs:
                pair.environment.age += 1

            # Track statistics
            stats = self.get_stats()
            history['num_pairs'].append(stats['num_pairs'])
            history['max_fitness'].append(stats['max_fitness'])
            history['avg_fitness'].append(stats['avg_fitness'])
            history['num_environments_created'].append(len(self.environment_archive))

            self.generation += 1

        return {
            'pairs': self.pairs,
            'environment_archive': self.environment_archive,
            'history': history,
            'final_stats': self.get_stats()
        }

    def _evolve_agents(
        self,
        fitness_fn: Callable[[Any, POETEnvironment], float],
        mutate_agent_fn: Callable[[Any], Any]
    ):
        """Evolve agents within their paired environments."""
        for pair in self.pairs:
            # Create offspring
            child_genotype = mutate_agent_fn(pair.agent.genotype)

            # Evaluate
            child_fitness = fitness_fn(child_genotype, pair.environment)

            # Replace if better
            if child_fitness > pair.agent.fitness:
                pair.agent.genotype = child_genotype
                pair.agent.fitness = child_fitness
                pair.environment.best_agent_fitness = max(
                    pair.environment.best_agent_fitness,
                    child_fitness
                )

    def _reproduce_environments(
        self,
        fitness_fn: Callable[[Any, POETEnvironment], float],
        mutate_env_fn: Callable[[POETEnvironment], POETEnvironment]
    ):
        """
        Create new environments through mutation.

        New environments are admitted if they pass the minimal criterion:
        - Not too easy (mc_lower)
        - Not too hard (mc_upper)
        - Sufficiently novel
        """
        if len(self.pairs) >= self.max_pairs:
            return

        new_environments = []

        # Try to create new environments from existing ones
        for pair in self.pairs:
            # Mutate environment
            new_env = mutate_env_fn(pair.environment)
            new_env.env_id = self.next_env_id
            self.next_env_id += 1
            new_env.age = 0

            # Test with current agent
            test_fitness = fitness_fn(pair.agent.genotype, new_env)

            # Minimal criterion: should be challenging but solvable
            if self.mc_lower <= test_fitness <= self.mc_upper:
                # Check novelty against existing environments
                if self._is_novel_environment(new_env):
                    # Create new agent for this environment
                    new_agent = POETAgent(
                        agent_id=self.next_agent_id,
                        genotype=copy.deepcopy(pair.agent.genotype),
                        fitness=test_fitness,
                        environment_id=new_env.env_id
                    )
                    self.next_agent_id += 1

                    new_env.best_agent_fitness = test_fitness

                    new_pair = POETPair(environment=new_env, agent=new_agent)
                    new_environments.append(new_pair)

                    self.environment_archive.append(new_env.copy())

        # Add new environments
        for new_pair in new_environments:
            if len(self.pairs) < self.max_pairs:
                self.pairs.append(new_pair)

    def _transfer_agents(
        self,
        fitness_fn: Callable[[Any, POETEnvironment], float]
    ):
        """
        Attempt to transfer agents between environments.

        Agents can move to environments where they perform better.
        """
        if len(self.pairs) < 2:
            return

        # Try each agent in other environments
        for i, pair in enumerate(self.pairs):
            best_fitness = pair.agent.fitness
            best_env_idx = i

            # Test in other environments
            for j, other_pair in enumerate(self.pairs):
                if i == j:
                    continue

                # Evaluate agent in other environment
                fitness = fitness_fn(pair.agent.genotype, other_pair.environment)

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_env_idx = j

            # Transfer if found better environment
            if best_env_idx != i:
                # Create copy of agent for new environment
                transferred_agent = pair.agent.copy()
                transferred_agent.fitness = best_fitness
                transferred_agent.environment_id = self.pairs[best_env_idx].environment.env_id

                # Replace if better than current agent in target environment
                if best_fitness > self.pairs[best_env_idx].agent.fitness:
                    self.pairs[best_env_idx].agent = transferred_agent
                    self.pairs[best_env_idx].environment.best_agent_fitness = best_fitness

    def _is_novel_environment(self, env: POETEnvironment, threshold: float = 0.1) -> bool:
        """
        Check if environment is sufficiently novel.

        Compares parameters to existing environments.
        """
        if not self.pairs:
            return True

        for pair in self.pairs:
            # Calculate parameter distance
            distance = self._environment_distance(env, pair.environment)
            if distance < threshold:
                return False

        return True

    def _environment_distance(self, env1: POETEnvironment, env2: POETEnvironment) -> float:
        """Calculate distance between two environments."""
        # Simple parameter difference
        # Override this for custom environment types
        if env1.parameters == env2.parameters:
            return 0.0

        # Hash-based distance as fallback
        return 1.0 if env1.parameters != env2.parameters else 0.0

    def _prune_pairs(self):
        """
        Remove pairs that are:
        - Too old without improvement
        - Solved (too easy)
        - Stagnant
        """
        if len(self.pairs) <= 2:
            return

        pairs_to_keep = []

        for pair in self.pairs:
            keep = True

            # Remove if solved (fitness too high, environment too easy)
            if pair.agent.fitness > self.mc_upper:
                pair.environment.solved = True
                keep = False

            # Keep if relatively young
            if pair.environment.age < 20:
                keep = True

            if keep:
                pairs_to_keep.append(pair)

        # Ensure we keep at least 2 pairs
        if len(pairs_to_keep) < 2 and self.pairs:
            pairs_to_keep = sorted(self.pairs, key=lambda p: p.agent.fitness, reverse=True)[:2]

        self.pairs = pairs_to_keep

    def get_stats(self) -> Dict[str, Any]:
        """Get current POET statistics."""
        if not self.pairs:
            return {
                'num_pairs': 0,
                'max_fitness': 0.0,
                'avg_fitness': 0.0,
                'num_environments_total': len(self.environment_archive)
            }

        fitnesses = [pair.agent.fitness for pair in self.pairs]

        return {
            'generation': self.generation,
            'num_pairs': len(self.pairs),
            'max_fitness': max(fitnesses),
            'avg_fitness': sum(fitnesses) / len(fitnesses),
            'min_fitness': min(fitnesses),
            'num_environments_total': len(self.environment_archive),
            'avg_env_age': sum(p.environment.age for p in self.pairs) / len(self.pairs)
        }

    def get_best_agent(self) -> Optional[POETAgent]:
        """Get highest-performing agent."""
        if not self.pairs:
            return None
        best_pair = max(self.pairs, key=lambda p: p.agent.fitness)
        return best_pair.agent.copy()

    def get_environment_archive(self) -> List[POETEnvironment]:
        """Get all environments ever created."""
        return [env.copy() for env in self.environment_archive]


class POETWithArchive(POET):
    """
    Enhanced POET with agent archive.

    Maintains archive of best agents ever found.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_archive: List[POETAgent] = []

    def _evolve_agents(
        self,
        fitness_fn: Callable[[Any, POETEnvironment], float],
        mutate_agent_fn: Callable[[Any], Any]
    ):
        """Evolve agents and archive best."""
        super()._evolve_agents(fitness_fn, mutate_agent_fn)

        # Archive best agents
        for pair in self.pairs:
            # Check if this agent should be archived
            if not self.agent_archive or pair.agent.fitness > min(a.fitness for a in self.agent_archive):
                self.agent_archive.append(pair.agent.copy())

                # Keep only top agents
                self.agent_archive.sort(key=lambda a: a.fitness, reverse=True)
                self.agent_archive = self.agent_archive[:50]

    def _transfer_agents(
        self,
        fitness_fn: Callable[[Any, POETEnvironment], float]
    ):
        """Transfer with access to archived agents."""
        # Try current agents
        super()._transfer_agents(fitness_fn)

        # Also try archived agents in new environments
        for pair in self.pairs:
            for archived_agent in self.agent_archive[:10]:  # Try top 10
                fitness = fitness_fn(archived_agent.genotype, pair.environment)

                if fitness > pair.agent.fitness:
                    # Transfer archived agent
                    transferred = archived_agent.copy()
                    transferred.fitness = fitness
                    transferred.environment_id = pair.environment.env_id
                    pair.agent = transferred
                    pair.environment.best_agent_fitness = fitness

    def get_agent_archive(self) -> List[POETAgent]:
        """Get archive of best agents."""
        return [agent.copy() for agent in self.agent_archive]
