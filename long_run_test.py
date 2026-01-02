#!/usr/bin/env python3
"""
Long-run validation test for AEGIS-3.

Tests whether the system maintains novelty and achieves genuine open-endedness
over extended periods (1000+ cycles).
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.agent import AEGIS2


def run_long_test(cycles: int = 1000, checkpoint_interval: int = 100):
    """Run extended evolution test."""
    print(f"{'='*60}")
    print(f"LONG-RUN VALIDATION TEST ({cycles} cycles)")
    print(f"{'='*60}\n")

    agent = AEGIS2(name="long_run_test")

    # Tracking
    metrics = {
        'fitness': [],
        'genome_size': [],
        'patterns': [],
        'goals': [],
        'emergence_counts': [],
        'novelty': [],
        'checkpoints': []
    }

    start_time = time.time()
    last_checkpoint = time.time()

    for cycle in range(cycles):
        # Varying input to encourage exploration
        input_data = {
            'x': (cycle % 100) / 100.0,
            'y': (cycle * 1.618) % 10,  # Golden ratio for variation
            'signal': cycle,
            'noise': (cycle * 7) % 13
        }

        result = agent.step(input_data)

        # Collect metrics
        metrics['fitness'].append(agent.fitness)
        genome_stats = agent.genome.get_stats()
        metrics['genome_size'].append(genome_stats['total_genes'])
        pattern_stats = agent.patterns.get_stats()
        metrics['patterns'].append(pattern_stats['total_patterns'])
        goal_stats = agent.goals.get_stats()
        metrics['goals'].append(goal_stats['total_goals'])
        emergence_count = len(result.get('emergence', []))
        metrics['emergence_counts'].append(emergence_count)
        novelty_stats = agent.novelty.get_stats()
        metrics['novelty'].append(novelty_stats.get('avg_novelty', 0))

        # Checkpoint progress
        if (cycle + 1) % checkpoint_interval == 0:
            elapsed = time.time() - last_checkpoint
            last_checkpoint = time.time()

            checkpoint = {
                'cycle': cycle + 1,
                'elapsed': elapsed,
                'rate': checkpoint_interval / elapsed,
                'fitness': agent.fitness,
                'genome_size': genome_stats['total_genes'],
                'patterns': pattern_stats['total_patterns'],
                'goals': goal_stats['total_goals'],
                'recent_emergence': sum(metrics['emergence_counts'][-checkpoint_interval:])
            }
            metrics['checkpoints'].append(checkpoint)

            print(f"Cycle {cycle+1:4d}: "
                  f"Fit={agent.fitness:.4f}, "
                  f"Genes={genome_stats['total_genes']:3d}, "
                  f"Patterns={pattern_stats['total_patterns']:4d}, "
                  f"Goals={goal_stats['total_goals']:3d}, "
                  f"Emergence={checkpoint['recent_emergence']:3d}, "
                  f"({checkpoint['rate']:.1f} c/s)")

    total_time = time.time() - start_time

    # Final analysis
    print(f"\n{'='*60}")
    print(f"LONG-RUN RESULTS")
    print(f"{'='*60}\n")

    # Fitness trend
    first_100 = sum(metrics['fitness'][:100]) / 100
    last_100 = sum(metrics['fitness'][-100:]) / 100
    fitness_change = last_100 - first_100

    print(f"Total time: {total_time:.1f}s ({cycles/total_time:.1f} cycles/sec)")
    print(f"\nFitness:")
    print(f"  First 100 avg: {first_100:.4f}")
    print(f"  Last 100 avg: {last_100:.4f}")
    print(f"  Change: {fitness_change:+.4f}")

    # Novelty trend
    first_100_novelty = sum(metrics['novelty'][:100]) / 100
    last_100_novelty = sum(metrics['novelty'][-100:]) / 100

    print(f"\nNovelty:")
    print(f"  First 100 avg: {first_100_novelty:.4f}")
    print(f"  Last 100 avg: {last_100_novelty:.4f}")

    # Emergence totals
    total_emergence = sum(metrics['emergence_counts'])
    print(f"\nEmergence:")
    print(f"  Total events: {total_emergence}")
    print(f"  Rate: {total_emergence/cycles:.3f} per cycle")

    # Complexity
    print(f"\nComplexity:")
    print(f"  Genome: {metrics['genome_size'][0]} → {metrics['genome_size'][-1]}")
    print(f"  Patterns: {metrics['patterns'][0]} → {metrics['patterns'][-1]}")
    print(f"  Goals: {metrics['goals'][0]} → {metrics['goals'][-1]}")

    # Verdict
    print(f"\n{'─'*60}")
    print(f"VERDICT:")

    verdicts = []

    if fitness_change > 0.01:
        print(f"  ✅ Fitness improved over long run")
        verdicts.append("PASS")
    else:
        print(f"  ⚠️  Fitness did not improve significantly")
        verdicts.append("WARN")

    if last_100_novelty > first_100_novelty * 0.5:
        print(f"  ✅ Novelty maintained")
        verdicts.append("PASS")
    else:
        print(f"  ❌ Novelty collapsed")
        verdicts.append("FAIL")

    if total_emergence > cycles * 0.1:
        print(f"  ✅ Consistent emergence detected")
        verdicts.append("PASS")
    else:
        print(f"  ⚠️  Low emergence rate")
        verdicts.append("WARN")

    if metrics['patterns'][-1] > metrics['patterns'][0] * 2:
        print(f"  ✅ Significant structural growth")
        verdicts.append("PASS")
    else:
        print(f"  ⚠️  Limited structural growth")
        verdicts.append("WARN")

    # Overall
    passes = verdicts.count("PASS")
    fails = verdicts.count("FAIL")
    warnings = verdicts.count("WARN")

    print(f"\n  Overall: {passes}/4 passed, {warnings} warnings, {fails} failures")

    # Save results
    results_dir = Path("validation_results")
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"long_run_{cycles}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    return metrics


if __name__ == "__main__":
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    run_long_test(cycles=cycles)
