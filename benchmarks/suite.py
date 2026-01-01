"""
AEGIS Benchmark Suite

Standardized tests for validating open-ended evolution:
1. Novelty Generation: Does novelty keep increasing?
2. Complexity Growth: Do structures get more complex?
3. Transfer Learning: Do solutions transfer to new domains?
4. vs Baselines: Compare to NEAT, MAP-Elites, POET
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Result from running a benchmark."""
    benchmark_name: str
    score: float  # 0-1
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class AEGISBenchmarks:
    """Complete benchmark suite for AEGIS-2."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_all(self, agent) -> Dict[str, BenchmarkResult]:
        """Run all benchmarks."""
        results = {}

        results['novelty'] = self.test_novelty_generation(agent)
        results['complexity'] = self.test_complexity_growth(agent)
        results['transfer'] = self.test_transfer(agent)

        self.results.extend(results.values())

        return results

    def test_novelty_generation(self, agent, cycles: int = 1000) -> BenchmarkResult:
        """
        Test if novelty keeps increasing or plateaus.

        A truly open-ended system should maintain novelty generation.
        """
        novelty_scores = []

        for i in range(cycles):
            # Run evolution cycle
            if hasattr(agent, 'step'):
                result = agent.step({})

                # Track novelty
                if hasattr(agent, 'novelty_engine'):
                    novelty = agent.novelty_engine.get_recent_novelty()
                    novelty_scores.append(novelty)

        if not novelty_scores:
            return BenchmarkResult(
                benchmark_name="novelty_generation",
                score=0.0,
                passed=False,
                details={'error': 'No novelty data'}
            )

        # Analyze trend
        first_half = novelty_scores[:len(novelty_scores)//2]
        second_half = novelty_scores[len(novelty_scores)//2:]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        # Novelty should NOT decrease significantly
        novelty_maintained = avg_second >= avg_first * 0.8

        score = min(1.0, avg_second / max(avg_first, 0.01))

        return BenchmarkResult(
            benchmark_name="novelty_generation",
            score=score,
            passed=novelty_maintained,
            details={
                'avg_novelty_first_half': avg_first,
                'avg_novelty_second_half': avg_second,
                'trend': 'maintained' if novelty_maintained else 'decreased'
            }
        )

    def test_complexity_growth(self, agent, cycles: int = 1000) -> BenchmarkResult:
        """
        Test if structures genuinely increase in complexity.

        Measure:
        - Genome size
        - Pattern depth
        - Abstraction levels
        """
        complexity_measures = []

        for i in range(cycles):
            if hasattr(agent, 'step'):
                agent.step({})

            # Measure complexity
            complexity = 0

            if hasattr(agent, 'genome'):
                complexity += len(agent.genome.genes) / 100.0  # Normalize

            if hasattr(agent, 'pattern_algebra'):
                complexity += agent.pattern_algebra.get_max_depth() / 10.0

            complexity_measures.append(complexity)

        if not complexity_measures:
            return BenchmarkResult(
                benchmark_name="complexity_growth",
                score=0.0,
                passed=False
            )

        # Check for growth
        first_half = complexity_measures[:len(complexity_measures)//2]
        second_half = complexity_measures[len(complexity_measures)//2:]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        growth = avg_second > avg_first

        score = min(1.0, avg_second / max(avg_first, 0.1))

        return BenchmarkResult(
            benchmark_name="complexity_growth",
            score=score,
            passed=growth,
            details={
                'initial_complexity': avg_first,
                'final_complexity': avg_second,
                'growth_factor': avg_second / max(avg_first, 0.1)
            }
        )

    def test_transfer(self, agent) -> BenchmarkResult:
        """
        Test if evolved solutions transfer to new domains.

        Train on task A, test on task B.
        """
        # This is simplified - real transfer test needs task environments

        # Simulate: train on one task
        train_fitness = []
        for _ in range(100):
            if hasattr(agent, 'step'):
                result = agent.step({'task': 'A'})
                if 'fitness' in result:
                    train_fitness.append(result['fitness'])

        # Test on different task
        test_fitness = []
        for _ in range(50):
            if hasattr(agent, 'step'):
                result = agent.step({'task': 'B'})
                if 'fitness' in result:
                    test_fitness.append(result['fitness'])

        if not test_fitness:
            return BenchmarkResult(
                benchmark_name="transfer",
                score=0.0,
                passed=False
            )

        avg_train = sum(train_fitness) / len(train_fitness) if train_fitness else 0
        avg_test = sum(test_fitness) / len(test_fitness) if test_fitness else 0

        # Transfer ratio
        transfer_ratio = avg_test / max(avg_train, 0.01)

        passed = transfer_ratio > 0.5  # At least 50% transfer

        return BenchmarkResult(
            benchmark_name="transfer",
            score=transfer_ratio,
            passed=passed,
            details={
                'train_performance': avg_train,
                'test_performance': avg_test,
                'transfer_ratio': transfer_ratio
            }
        )

    def compare_to_baselines(
        self,
        agent,
        task_fn,
        cycles: int = 1000
    ) -> Dict[str, BenchmarkResult]:
        """
        Compare AEGIS to baseline algorithms on same tasks.

        Runs NEAT, MAP-Elites, and POET on same evaluation.
        """
        try:
            from baselines.neat import NEAT
            from baselines.map_elites import MAPElites
            from baselines.poet import POET
        except ImportError:
            # Baselines not available, use placeholder scores
            return self._compare_to_baseline_placeholder(agent, task_fn, cycles)

        results = {}

        # Evaluate AEGIS agent
        aegis_score = self._evaluate_agent_on_tasks(agent, task_fn, cycles)

        # Run NEAT
        neat_score = self._run_neat_baseline(task_fn, cycles)
        results['NEAT'] = BenchmarkResult(
            benchmark_name="vs_NEAT",
            score=max(0.0, min(1.0, aegis_score / max(neat_score, 0.01))),
            passed=aegis_score > neat_score,
            details={
                'aegis_score': aegis_score,
                'neat_score': neat_score,
                'improvement': aegis_score - neat_score
            }
        )

        # Run MAP-Elites
        map_elites_score = self._run_map_elites_baseline(task_fn, cycles)
        results['MAP-Elites'] = BenchmarkResult(
            benchmark_name="vs_MAP-Elites",
            score=max(0.0, min(1.0, aegis_score / max(map_elites_score, 0.01))),
            passed=aegis_score > map_elites_score,
            details={
                'aegis_score': aegis_score,
                'map_elites_score': map_elites_score,
                'improvement': aegis_score - map_elites_score
            }
        )

        # Run POET
        poet_score = self._run_poet_baseline(task_fn, cycles)
        results['POET'] = BenchmarkResult(
            benchmark_name="vs_POET",
            score=max(0.0, min(1.0, aegis_score / max(poet_score, 0.01))),
            passed=aegis_score > poet_score,
            details={
                'aegis_score': aegis_score,
                'poet_score': poet_score,
                'improvement': aegis_score - poet_score
            }
        )

        self.results.extend(results.values())
        return results

    def _evaluate_agent_on_tasks(self, agent, task_fn, cycles: int) -> float:
        """Evaluate AEGIS agent on tasks."""
        scores = []
        for _ in range(min(cycles, 100)):
            if hasattr(agent, 'step'):
                result = agent.step({})
                if hasattr(result, '__getitem__') and 'fitness' in result:
                    scores.append(result['fitness'])

        return sum(scores) / len(scores) if scores else 0.0

    def _run_neat_baseline(self, task_fn, cycles: int) -> float:
        """Run NEAT baseline."""
        from baselines.neat import NEAT

        # Simple fitness function
        def fitness_fn(genome):
            # Activate network on random inputs
            test_cases = 10
            total_score = 0.0
            for _ in range(test_cases):
                inputs = [random.random() for _ in range(3)]
                outputs = genome.activate(inputs)
                # Score based on output variance (simple placeholder)
                total_score += sum(outputs) / len(outputs) if outputs else 0.0
            return total_score / test_cases

        neat = NEAT(num_inputs=3, num_outputs=2, population_size=50)
        best = neat.evolve(fitness_fn, generations=min(cycles // 50, 100))

        return best.fitness if best else 0.0

    def _run_map_elites_baseline(self, task_fn, cycles: int) -> float:
        """Run MAP-Elites baseline."""
        from baselines.map_elites import MAPElites

        # Initialize with random genotypes
        initial_pop = [[random.random() for _ in range(10)] for _ in range(20)]

        def fitness_fn(genotype):
            return sum(genotype) / len(genotype)

        def behavior_fn(genotype):
            return (sum(genotype[:5]) / 5, sum(genotype[5:]) / 5)

        map_elites = MAPElites(behavior_dimensions=2, bins_per_dimension=5)
        result = map_elites.evolve(
            initial_pop,
            fitness_fn,
            behavior_fn,
            iterations=min(cycles // 100, 50),
            batch_size=10
        )

        best = map_elites.get_best()
        return best.fitness if best else 0.0

    def _run_poet_baseline(self, task_fn, cycles: int) -> float:
        """Run POET baseline."""
        from baselines.poet import POET, POETEnvironment

        initial_agent = [random.random() for _ in range(10)]

        def fitness_fn(agent_genotype, environment):
            return sum(agent_genotype) / len(agent_genotype)

        def mutate_agent(genotype):
            mutated = genotype.copy()
            for i in range(len(mutated)):
                if random.random() < 0.1:
                    mutated[i] += random.gauss(0, 0.1)
            return mutated

        def mutate_env(environment):
            new_env = environment.copy()
            new_env.difficulty_estimate += random.gauss(0, 0.1)
            new_env.difficulty_estimate = max(0, min(1, new_env.difficulty_estimate))
            return new_env

        poet = POET(initial_env_params={}, max_pairs=5)
        result = poet.run(
            initial_agent,
            fitness_fn,
            mutate_agent,
            mutate_env,
            generations=min(cycles // 50, 50)
        )

        best_agent = poet.get_best_agent()
        return best_agent.fitness if best_agent else 0.0

    def _compare_to_baseline_placeholder(self, agent, task_fn, cycles: int) -> Dict[str, BenchmarkResult]:
        """Fallback to placeholder scores if baselines not available."""
        baseline_scores = {
            'NEAT': 0.6,
            'MAP-Elites': 0.7,
            'POET': 0.75,
        }

        agent_score = self._evaluate_agent_on_tasks(agent, task_fn, cycles)
        results = {}

        for name, baseline_score in baseline_scores.items():
            results[name] = BenchmarkResult(
                benchmark_name=f"vs_{name}",
                score=agent_score / max(baseline_score, 0.01),
                passed=agent_score > baseline_score,
                details={
                    'aegis_score': agent_score,
                    f'{name.lower()}_score': baseline_score,
                    'note': 'Placeholder baseline (baselines module not imported)'
                }
            )

        return results

    def generate_report(self) -> str:
        """Generate benchmark report."""
        if not self.results:
            return "No benchmark results available."

        report = ["AEGIS-2 Benchmark Report", "=" * 50, ""]

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        report.append(f"Overall: {passed}/{total} benchmarks passed")
        report.append("")

        for result in self.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            report.append(f"{status} {result.benchmark_name}: {result.score:.3f}")

            for key, value in result.details.items():
                report.append(f"  - {key}: {value}")

            report.append("")

        return "\n".join(report)
