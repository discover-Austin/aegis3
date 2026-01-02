"""
Minimal Bootstrap

Start with the absolute minimum and let everything else emerge:
- Basic computation (Turing complete)
- Selection pressure (survive/reproduce)
- Variation (random mutation)
- Time

Everything else should emerge from these basics.
"""

import random
from typing import Any, List, Callable, Dict


class MinimalBootstrap:
    """
    Minimal starting point for open-ended evolution.

    Provides only:
    1. Turing-complete computation (lambda calculus-like)
    2. Selection (fitness-based survival)
    3. Variation (mutation)
    4. Time (iteration)

    Everything else emerges.
    """

    def __init__(self, population_size: int = 100):
        self.population_size = population_size

        # Minimal instruction set (Turing complete)
        self.instructions = ['LAMBDA', 'APPLY', 'IF', 'CONST', 'VAR']

        # Population of programs
        self.population: List[List[str]] = []

        # Initialize with random programs
        for _ in range(population_size):
            program = self._random_program(length=10)
            self.population.append(program)

    def _random_program(self, length: int = 10) -> List[str]:
        """Generate random program."""
        return [random.choice(self.instructions) for _ in range(length)]

    def _execute(self, program: List[str], input_val: Any = 0) -> Any:
        """Execute a program (simplified)."""
        # Minimal interpreter
        try:
            # This is highly simplified
            return len(program)  # Placeholder
        except Exception:
            # Catch any exception during program execution
            return 0

    def _fitness(self, program: List[str]) -> float:
        """Evaluate fitness of program."""
        # Fitness = ability to compute something useful
        # Start with simple: reward longer programs that don't crash

        try:
            output = self._execute(program)
            return float(output) if output is not None else 0.0
        except (ValueError, TypeError, Exception):
            # ValueError: if output cannot be converted to float
            # TypeError: if output is wrong type
            # Exception: catch any error from _execute
            return 0.0

    def _mutate(self, program: List[str]) -> List[str]:
        """Mutate program."""
        mutated = program.copy()

        # Point mutation
        if random.random() < 0.1 and mutated:
            idx = random.randint(0, len(mutated) - 1)
            mutated[idx] = random.choice(self.instructions)

        # Insertion
        if random.random() < 0.05:
            idx = random.randint(0, len(mutated))
            mutated.insert(idx, random.choice(self.instructions))

        # Deletion
        if random.random() < 0.05 and len(mutated) > 1:
            idx = random.randint(0, len(mutated) - 1)
            del mutated[idx]

        return mutated

    def step(self) -> Dict[str, Any]:
        """Single evolution step."""
        # Evaluate fitness
        fitnesses = [self._fitness(prog) for prog in self.population]

        # Selection
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            # Random selection
            selected = random.choices(self.population, k=self.population_size)
        else:
            # Fitness-proportional selection
            selected = random.choices(
                self.population,
                weights=fitnesses,
                k=self.population_size
            )

        # Variation (mutation)
        new_population = [self._mutate(prog) for prog in selected]

        self.population = new_population

        # Stats
        avg_fitness = sum(fitnesses) / len(fitnesses) if fitnesses else 0
        max_fitness = max(fitnesses) if fitnesses else 0

        return {
            'avg_fitness': avg_fitness,
            'max_fitness': max_fitness,
            'avg_length': sum(len(p) for p in self.population) / len(self.population)
        }

    def run(self, generations: int = 1000) -> Dict[str, Any]:
        """Run bootstrap evolution."""
        history = []

        for gen in range(generations):
            stats = self.step()
            stats['generation'] = gen
            history.append(stats)

            if gen % 100 == 0:
                print(f"Gen {gen}: max_fitness={stats['max_fitness']:.2f}, avg_length={stats['avg_length']:.1f}")

        return {
            'history': history,
            'final_population': self.population
        }
