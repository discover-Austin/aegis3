#!/usr/bin/env python3
"""
AEGIS-3 Validation Experiment Suite

Tests the core claims:
1. Does evolution produce increasing fitness?
2. Does novelty continue to grow (not plateau)?
3. Does complexity increase over time?
4. Do emergent behaviors appear?
5. Does self-modification improve performance?

This provides empirical evidence for or against the system's claims.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from core.agent import AEGIS2


class ValidationExperiment:
    """Runs systematic validation experiments on AEGIS-3."""

    def __init__(self, experiment_name: str = "validation"):
        self.experiment_name = experiment_name
        self.results_dir = Path("validation_results")
        self.results_dir.mkdir(exist_ok=True)

        self.results = {
            'experiment': experiment_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

    def test_basic_evolution(self, cycles: int = 100) -> Dict[str, Any]:
        """
        Test 1: Basic Evolution
        Does the system evolve? Does fitness increase?
        """
        print(f"\n{'='*60}")
        print(f"TEST 1: Basic Evolution ({cycles} cycles)")
        print(f"{'='*60}\n")

        agent = AEGIS2(name="evolution_test")

        # Track metrics
        fitness_history = []
        genome_size_history = []
        pattern_count_history = []
        goal_count_history = []

        start_time = time.time()

        for cycle in range(cycles):
            # Step with simple input
            input_data = {'x': cycle / 100.0, 'signal': cycle}
            result = agent.step(input_data)

            # Record metrics
            fitness_history.append(agent.fitness)
            genome_stats = agent.genome.get_stats()
            genome_size_history.append(genome_stats['total_genes'])
            pattern_stats = agent.patterns.get_stats()
            pattern_count_history.append(pattern_stats['total_patterns'])
            goal_stats = agent.goals.get_stats()
            goal_count_history.append(goal_stats['total_goals'])

            # Progress update
            if (cycle + 1) % 20 == 0:
                print(f"  Cycle {cycle+1:3d}: Fitness={agent.fitness:.4f}, "
                      f"Genes={genome_stats['total_genes']}, "
                      f"Patterns={pattern_stats['total_patterns']}, "
                      f"Goals={goal_stats['total_goals']}")

        elapsed = time.time() - start_time

        # Analysis
        initial_fitness = fitness_history[0] if fitness_history else 0
        final_fitness = fitness_history[-1] if fitness_history else 0
        fitness_improvement = final_fitness - initial_fitness
        fitness_trend = "INCREASING" if fitness_improvement > 0.01 else "FLAT" if abs(fitness_improvement) < 0.01 else "DECREASING"

        avg_genome_size = sum(genome_size_history) / len(genome_size_history)
        genome_growth = genome_size_history[-1] - genome_size_history[0]

        results = {
            'cycles': cycles,
            'elapsed_time': elapsed,
            'cycles_per_second': cycles / elapsed,
            'fitness': {
                'initial': initial_fitness,
                'final': final_fitness,
                'improvement': fitness_improvement,
                'trend': fitness_trend,
                'history': fitness_history
            },
            'genome': {
                'initial_size': genome_size_history[0],
                'final_size': genome_size_history[-1],
                'growth': genome_growth,
                'avg_size': avg_genome_size,
                'history': genome_size_history
            },
            'patterns': {
                'initial': pattern_count_history[0],
                'final': pattern_count_history[-1],
                'growth': pattern_count_history[-1] - pattern_count_history[0],
                'history': pattern_count_history
            },
            'goals': {
                'initial': goal_count_history[0],
                'final': goal_count_history[-1],
                'history': goal_count_history
            }
        }

        # Verdict
        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  Time: {elapsed:.2f}s ({cycles/elapsed:.1f} cycles/sec)")
        print(f"  Fitness: {initial_fitness:.4f} → {final_fitness:.4f} ({fitness_trend})")
        print(f"  Genome: {genome_size_history[0]} → {genome_size_history[-1]} genes")
        print(f"  Patterns: {pattern_count_history[0]} → {pattern_count_history[-1]}")
        print(f"  Goals: {goal_count_history[0]} → {goal_count_history[-1]}")

        if fitness_improvement > 0.01:
            print(f"  ✅ PASS: Fitness improved by {fitness_improvement:.4f}")
        else:
            print(f"  ⚠️  WARNING: Little to no fitness improvement")

        return results

    def test_novelty_growth(self, cycles: int = 200) -> Dict[str, Any]:
        """
        Test 2: Novelty Growth
        Does novelty continue to increase or does it plateau?
        """
        print(f"\n{'='*60}")
        print(f"TEST 2: Novelty Growth ({cycles} cycles)")
        print(f"{'='*60}\n")

        agent = AEGIS2(name="novelty_test")

        novelty_scores = []
        archive_sizes = []
        diversity_scores = []

        for cycle in range(cycles):
            input_data = {'x': cycle / 100.0, 'y': (cycle * 1.5) % 10}
            result = agent.step(input_data)

            # Get novelty metrics
            novelty_stats = agent.novelty.get_stats()
            novelty_scores.append(novelty_stats.get('avg_novelty', 0))
            archive_sizes.append(novelty_stats.get('archive_size', 0))

            # Diversity from genome
            genome_stats = agent.genome.get_stats()
            diversity_scores.append(genome_stats.get('total_genes', 0))

            if (cycle + 1) % 40 == 0:
                print(f"  Cycle {cycle+1:3d}: Novelty={novelty_scores[-1]:.4f}, "
                      f"Archive={archive_sizes[-1]}, Diversity={diversity_scores[-1]}")

        # Analyze trend
        first_half_novelty = sum(novelty_scores[:len(novelty_scores)//2]) / (len(novelty_scores)//2) if novelty_scores else 0
        second_half_novelty = sum(novelty_scores[len(novelty_scores)//2:]) / (len(novelty_scores) - len(novelty_scores)//2) if novelty_scores else 0

        novelty_trend = "GROWING" if second_half_novelty > first_half_novelty * 1.1 else "PLATEAU" if second_half_novelty > first_half_novelty * 0.9 else "DECLINING"

        results = {
            'cycles': cycles,
            'novelty': {
                'first_half_avg': first_half_novelty,
                'second_half_avg': second_half_novelty,
                'trend': novelty_trend,
                'history': novelty_scores
            },
            'archive_growth': {
                'initial': archive_sizes[0] if archive_sizes else 0,
                'final': archive_sizes[-1] if archive_sizes else 0,
                'history': archive_sizes
            }
        }

        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  First half avg novelty: {first_half_novelty:.4f}")
        print(f"  Second half avg novelty: {second_half_novelty:.4f}")
        print(f"  Trend: {novelty_trend}")
        print(f"  Archive: {archive_sizes[0]} → {archive_sizes[-1]}")

        if novelty_trend == "GROWING":
            print(f"  ✅ PASS: Novelty continues to grow")
        elif novelty_trend == "PLATEAU":
            print(f"  ⚠️  WARNING: Novelty has plateaued")
        else:
            print(f"  ❌ FAIL: Novelty is declining")

        return results

    def test_complexity_growth(self, cycles: int = 200) -> Dict[str, Any]:
        """
        Test 3: Complexity Growth
        Do structures become more complex over time?
        """
        print(f"\n{'='*60}")
        print(f"TEST 3: Complexity Growth ({cycles} cycles)")
        print(f"{'='*60}\n")

        agent = AEGIS2(name="complexity_test")

        genome_depth_history = []
        pattern_complexity_history = []
        goal_depth_history = []

        for cycle in range(cycles):
            input_data = {'value': cycle * 0.01}
            result = agent.step(input_data)

            # Measure structural complexity
            genome_stats = agent.genome.get_stats()
            genome_depth_history.append(genome_stats.get('max_gene_depth', 1))

            pattern_stats = agent.patterns.get_stats()
            pattern_complexity_history.append(pattern_stats.get('abstraction_levels', 0))

            goal_stats = agent.goals.get_stats()
            goal_depth_history.append(goal_stats.get('max_goal_depth', 0))

            if (cycle + 1) % 40 == 0:
                print(f"  Cycle {cycle+1:3d}: GenomeDepth={genome_depth_history[-1]}, "
                      f"PatternLevels={pattern_complexity_history[-1]}, "
                      f"GoalDepth={goal_depth_history[-1]}")

        # Analysis
        initial_complexity = genome_depth_history[0] + pattern_complexity_history[0]
        final_complexity = genome_depth_history[-1] + pattern_complexity_history[-1]
        complexity_growth = final_complexity - initial_complexity

        results = {
            'cycles': cycles,
            'genome_depth': {
                'initial': genome_depth_history[0],
                'final': genome_depth_history[-1],
                'growth': genome_depth_history[-1] - genome_depth_history[0],
                'history': genome_depth_history
            },
            'pattern_levels': {
                'initial': pattern_complexity_history[0],
                'final': pattern_complexity_history[-1],
                'growth': pattern_complexity_history[-1] - pattern_complexity_history[0],
                'history': pattern_complexity_history
            },
            'total_complexity_growth': complexity_growth
        }

        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  Initial complexity: {initial_complexity}")
        print(f"  Final complexity: {final_complexity}")
        print(f"  Growth: {complexity_growth}")

        if complexity_growth > 0:
            print(f"  ✅ PASS: Complexity increased")
        else:
            print(f"  ❌ FAIL: No complexity growth")

        return results

    def test_emergence_detection(self, cycles: int = 300) -> Dict[str, Any]:
        """
        Test 4: Emergence Detection
        Does the system detect emergent phenomena?
        """
        print(f"\n{'='*60}")
        print(f"TEST 4: Emergence Detection ({cycles} cycles)")
        print(f"{'='*60}\n")

        agent = AEGIS2(name="emergence_test")

        emergence_events = []
        emergence_types = defaultdict(int)

        for cycle in range(cycles):
            input_data = {'t': cycle, 'signal': cycle % 10}
            result = agent.step(input_data)

            # Collect emergence events
            if 'emergence' in result and result['emergence']:
                for event in result['emergence']:
                    emergence_events.append({
                        'cycle': cycle,
                        'type': event.get('type', 'unknown'),
                        'description': event.get('description', '')
                    })
                    emergence_types[event.get('type', 'unknown')] += 1

            if emergence_events and len(emergence_events) % 10 == 0:
                print(f"  Cycle {cycle+1:3d}: {len(emergence_events)} emergence events so far")

        results = {
            'cycles': cycles,
            'total_emergence_events': len(emergence_events),
            'emergence_types': dict(emergence_types),
            'events': emergence_events[:50],  # First 50 events
            'emergence_rate': len(emergence_events) / cycles
        }

        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  Total emergence events: {len(emergence_events)}")
        print(f"  Emergence rate: {len(emergence_events)/cycles:.3f} per cycle")
        print(f"  Types detected: {dict(emergence_types)}")

        if len(emergence_events) > 0:
            print(f"  ✅ PASS: Emergence events detected")
            print(f"\n  Sample events:")
            for event in emergence_events[:5]:
                print(f"    - Cycle {event['cycle']}: {event['type']}")
        else:
            print(f"  ⚠️  WARNING: No emergence events detected")

        return results

    def test_self_modification(self, cycles: int = 100) -> Dict[str, Any]:
        """
        Test 5: Self-Modification
        Does the system modify itself? Does this improve performance?
        """
        print(f"\n{'='*60}")
        print(f"TEST 5: Self-Modification ({cycles} cycles)")
        print(f"{'='*60}\n")

        agent = AEGIS2(name="selfmod_test")

        modification_count = 0
        genome_changes = []
        fitness_before_mod = []
        fitness_after_mod = []

        for cycle in range(cycles):
            input_data = {'input': cycle}

            # Record fitness before
            fitness_before = agent.fitness
            genome_size_before = agent.genome.get_stats()['total_genes']

            result = agent.step(input_data)

            # Check if modification occurred
            genome_size_after = agent.genome.get_stats()['total_genes']
            fitness_after = agent.fitness

            if genome_size_after != genome_size_before:
                modification_count += 1
                genome_changes.append({
                    'cycle': cycle,
                    'size_change': genome_size_after - genome_size_before,
                    'fitness_before': fitness_before,
                    'fitness_after': fitness_after
                })
                fitness_before_mod.append(fitness_before)
                fitness_after_mod.append(fitness_after)

            if (cycle + 1) % 20 == 0:
                print(f"  Cycle {cycle+1:3d}: Modifications={modification_count}, "
                      f"Fitness={agent.fitness:.4f}")

        # Analysis
        if fitness_after_mod and fitness_before_mod:
            avg_fitness_before = sum(fitness_before_mod) / len(fitness_before_mod)
            avg_fitness_after = sum(fitness_after_mod) / len(fitness_after_mod)
            improvement = avg_fitness_after - avg_fitness_before
        else:
            avg_fitness_before = 0
            avg_fitness_after = 0
            improvement = 0

        results = {
            'cycles': cycles,
            'modification_count': modification_count,
            'modification_rate': modification_count / cycles,
            'genome_changes': genome_changes[:20],  # First 20 changes
            'fitness_impact': {
                'avg_before': avg_fitness_before,
                'avg_after': avg_fitness_after,
                'improvement': improvement
            }
        }

        print(f"\n{'─'*60}")
        print(f"RESULTS:")
        print(f"  Modifications: {modification_count} ({modification_count/cycles:.2%})")
        if modification_count > 0:
            print(f"  Avg fitness before mod: {avg_fitness_before:.4f}")
            print(f"  Avg fitness after mod: {avg_fitness_after:.4f}")
            print(f"  Improvement: {improvement:.4f}")

            if improvement > 0:
                print(f"  ✅ PASS: Self-modification improves fitness")
            else:
                print(f"  ⚠️  WARNING: Self-modification doesn't improve fitness")
        else:
            print(f"  ⚠️  WARNING: No self-modifications detected")

        return results

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all validation tests and generate comprehensive report."""
        print("\n" + "="*60)
        print("AEGIS-3 VALIDATION EXPERIMENT SUITE")
        print("="*60)
        print(f"Experiment: {self.experiment_name}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        # Run tests
        self.results['tests']['basic_evolution'] = self.test_basic_evolution(cycles=100)

        self.results['tests']['novelty_growth'] = self.test_novelty_growth(cycles=200)

        self.results['tests']['complexity_growth'] = self.test_complexity_growth(cycles=200)

        self.results['tests']['emergence_detection'] = self.test_emergence_detection(cycles=300)

        self.results['tests']['self_modification'] = self.test_self_modification(cycles=100)

        # Overall verdict
        print(f"\n{'='*60}")
        print("OVERALL VALIDATION RESULTS")
        print(f"{'='*60}\n")

        passes = 0
        warnings = 0
        fails = 0

        # Evaluate each test
        if self.results['tests']['basic_evolution']['fitness']['improvement'] > 0.01:
            print("✅ Evolution: PASS")
            passes += 1
        else:
            print("⚠️  Evolution: WARNING")
            warnings += 1

        if self.results['tests']['novelty_growth']['novelty']['trend'] == "GROWING":
            print("✅ Novelty: PASS")
            passes += 1
        elif self.results['tests']['novelty_growth']['novelty']['trend'] == "PLATEAU":
            print("⚠️  Novelty: WARNING (plateaued)")
            warnings += 1
        else:
            print("❌ Novelty: FAIL")
            fails += 1

        if self.results['tests']['complexity_growth']['total_complexity_growth'] > 0:
            print("✅ Complexity: PASS")
            passes += 1
        else:
            print("❌ Complexity: FAIL")
            fails += 1

        if self.results['tests']['emergence_detection']['total_emergence_events'] > 0:
            print("✅ Emergence: PASS")
            passes += 1
        else:
            print("⚠️  Emergence: WARNING")
            warnings += 1

        if self.results['tests']['self_modification']['modification_count'] > 0:
            print("✅ Self-Modification: PASS")
            passes += 1
        else:
            print("⚠️  Self-Modification: WARNING")
            warnings += 1

        print(f"\n{'─'*60}")
        print(f"SUMMARY: {passes} passed, {warnings} warnings, {fails} failed")
        print(f"{'─'*60}\n")

        # Save results
        results_file = self.results_dir / f"{self.experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"Results saved to: {results_file}")

        return self.results


def main():
    """Run validation experiments."""
    experiment = ValidationExperiment("aegis3_validation_v1")
    results = experiment.run_all_tests()

    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
