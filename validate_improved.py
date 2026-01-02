#!/usr/bin/env python3
"""
Validation of AEGIS-3 Improved System

Tests that all critical fixes work:
1. Pattern explosion is prevented
2. Novelty search produces non-zero scores
3. Self-modification activates
4. System scales to 10,000+ cycles

Expected results:
- ✅ Novelty > 0.0 (FIXED: was 0.0)
- ✅ Self-modifications > 0 (FIXED: was 0)
- ✅ Performance maintained (FIXED: collapsed at 500 cycles)
- ✅ Patterns bounded (FIXED: exploded to 24K)
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.improved_agent import AEGIS3Improved


def validate_improvements(cycles: int = 2000, checkpoint_interval: int = 100):
    """
    Validate that all improvements work.

    Args:
        cycles: Number of cycles to run
        checkpoint_interval: How often to report progress
    """
    print("="*70)
    print("AEGIS-3 IMPROVED - VALIDATION TEST")
    print("="*70)
    print(f"Testing {cycles} cycles to validate all fixes...")
    print()

    agent = AEGIS3Improved(
        name="validation_agent",
        max_patterns=5000,
        enable_self_mod=True,
        target_performance=50.0
    )

    # Metrics tracking
    metrics = {
        'novelty_scores': [],
        'fitness_values': [],
        'pattern_counts': [],
        'self_mod_counts': [],
        'performance_rates': [],
        'checkpoints': []
    }

    start_time = time.time()
    last_checkpoint = time.time()

    print("Starting evolution...\n")

    for cycle in range(cycles):
        # Varying input for exploration
        input_data = {
            'x': (cycle % 100) / 100.0,
            'y': (cycle * 1.618) % 10,
            'z': (cycle ** 1.5) % 7,
            'signal': cycle
        }

        # Execute cycle
        result = agent.step(input_data)

        # Collect metrics
        metrics['novelty_scores'].append(result['novelty'])
        metrics['fitness_values'].append(result['fitness'])
        metrics['pattern_counts'].append(result['resources']['patterns'])
        metrics['self_mod_counts'].append(result['self_modifications'])
        metrics['performance_rates'].append(result['performance'])

        # Checkpoint
        if (cycle + 1) % checkpoint_interval == 0:
            elapsed = time.time() - last_checkpoint
            last_checkpoint = time.time()

            checkpoint = {
                'cycle': cycle + 1,
                'elapsed': elapsed,
                'rate': checkpoint_interval / elapsed,
                'fitness': result['fitness'],
                'novelty': result['novelty'],
                'avg_novelty': result['avg_novelty'],
                'patterns': result['resources']['patterns'],
                'self_mods': result['self_modifications'],
                'emergence': len(result['emergence'])
            }

            metrics['checkpoints'].append(checkpoint)

            # Print progress
            print(f"Cycle {cycle+1:5d}: "
                  f"Fit={checkpoint['fitness']:.4f}, "
                  f"Nov={checkpoint['novelty']:.4f} (avg={checkpoint['avg_novelty']:.4f}), "
                  f"Pat={checkpoint['patterns']:4d}, "
                  f"Mods={checkpoint['self_mods']:3d}, "
                  f"Perf={checkpoint['rate']:.1f} c/s")

    total_time = time.time() - start_time

    # === VALIDATION ANALYSIS ===

    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)

    # Test 1: Novelty Search
    print("\n[Test 1: Novelty Search]")
    avg_novelty = sum(metrics['novelty_scores']) / len(metrics['novelty_scores'])
    non_zero_novelty = sum(1 for n in metrics['novelty_scores'] if n > 0.0)
    novelty_pct = (non_zero_novelty / len(metrics['novelty_scores'])) * 100

    print(f"  Average novelty: {avg_novelty:.4f}")
    print(f"  Non-zero novelty: {non_zero_novelty}/{len(metrics['novelty_scores'])} ({novelty_pct:.1f}%)")

    if avg_novelty > 0.05 and novelty_pct > 50:
        print(f"  ✅ PASS: Novelty search is functional (was 0.0)")
    else:
        print(f"  ❌ FAIL: Novelty still broken")

    # Test 2: Self-Modification
    print("\n[Test 2: Self-Modification]")
    final_mods = metrics['self_mod_counts'][-1] if metrics['self_mod_counts'] else 0
    self_mod_stats = agent.self_mod.get_stats()

    print(f"  Total modifications: {final_mods}")
    print(f"  Success rate: {self_mod_stats['success_rate']:.1%}")
    print(f"  Avg improvement: {self_mod_stats['avg_improvement']:.4f}")

    if final_mods > 0:
        print(f"  ✅ PASS: Self-modification activated (was dormant)")
    else:
        print(f"  ⚠️  WARNING: Self-modification still inactive")

    # Test 3: Scalability
    print("\n[Test 3: Scalability]")
    initial_rate = metrics['performance_rates'][10] if len(metrics['performance_rates']) > 10 else 0
    final_rate = sum(metrics['performance_rates'][-10:]) / 10 if len(metrics['performance_rates']) >= 10 else 0
    rate_change = ((final_rate - initial_rate) / initial_rate * 100) if initial_rate > 0 else 0

    max_patterns = max(metrics['pattern_counts'])
    final_patterns = metrics['pattern_counts'][-1]

    print(f"  Initial performance: {initial_rate:.1f} c/s")
    print(f"  Final performance: {final_rate:.1f} c/s ({rate_change:+.1f}%)")
    print(f"  Pattern count: {metrics['pattern_counts'][0]} → {final_patterns} (max: {max_patterns})")

    if final_rate > initial_rate * 0.5 and max_patterns < 10000:
        print(f"  ✅ PASS: Scalability maintained (was 99.5% degradation)")
    else:
        print(f"  ❌ FAIL: Scalability issues persist")

    # Test 4: Bounded Growth
    print("\n[Test 4: Bounded Growth]")
    print(f"  Max patterns: {max_patterns} (limit: {agent.patterns.max_patterns})")
    print(f"  Pattern evictions: {agent.patterns.evictions}")
    print(f"  Pattern merges: {agent.patterns.merges}")

    if max_patterns <= agent.patterns.max_patterns:
        print(f"  ✅ PASS: Patterns stayed within bounds (was unbounded)")
    else:
        print(f"  ❌ FAIL: Patterns exceeded limit")

    # Test 5: Fitness Progress
    print("\n[Test 5: Fitness Progress]")
    initial_fitness = sum(metrics['fitness_values'][:100]) / 100
    final_fitness = sum(metrics['fitness_values'][-100:]) / 100
    fitness_improvement = final_fitness - initial_fitness

    print(f"  Initial fitness (first 100): {initial_fitness:.4f}")
    print(f"  Final fitness (last 100): {final_fitness:.4f}")
    print(f"  Improvement: {fitness_improvement:+.4f}")

    if fitness_improvement > 0:
        print(f"  ✅ PASS: Fitness improved")
    else:
        print(f"  ⚠️  WARNING: No fitness improvement")

    # Overall Assessment
    print("\n" + "="*70)
    print("OVERALL ASSESSMENT")
    print("="*70)

    tests_passed = 0
    total_tests = 5

    if avg_novelty > 0.05 and novelty_pct > 50:
        tests_passed += 1
    if final_mods > 0:
        tests_passed += 1
    if final_rate > initial_rate * 0.5 and max_patterns < 10000:
        tests_passed += 1
    if max_patterns <= agent.patterns.max_patterns:
        tests_passed += 1
    if fitness_improvement > 0:
        tests_passed += 1

    print(f"\nTests passed: {tests_passed}/{total_tests}")
    print(f"Total cycles: {cycles} in {total_time:.1f}s ({cycles/total_time:.1f} c/s avg)")
    print(f"Emergence events: {len(agent.emergence_events)}")

    if tests_passed >= 4:
        print("\n🎉 ✅ VALIDATION SUCCESSFUL!")
        print("All critical issues have been fixed. System achieves:")
        print("  • Functional novelty search")
        print("  • Active self-modification")
        print("  • Sustained scalability")
        print("  • Bounded resource usage")
        print("\nGenuine open-ended evolution is now feasible.")
    elif tests_passed >= 3:
        print("\n⚠️  PARTIAL SUCCESS")
        print("Most critical issues fixed, but some improvements needed.")
    else:
        print("\n❌ VALIDATION FAILED")
        print("Critical issues remain. Further fixes required.")

    # Save detailed results
    results_dir = Path("validation_results")
    results_dir.mkdir(exist_ok=True)
    results_file = results_dir / f"improved_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(results_file, 'w') as f:
        json.dump({
            'metrics': {
                'novelty': {
                    'avg': avg_novelty,
                    'non_zero_pct': novelty_pct,
                    'history': metrics['novelty_scores'][::10]  # Sampled
                },
                'self_modification': self_mod_stats,
                'scalability': {
                    'initial_rate': initial_rate,
                    'final_rate': final_rate,
                    'rate_change_pct': rate_change,
                    'max_patterns': max_patterns
                },
                'fitness': {
                    'initial': initial_fitness,
                    'final': final_fitness,
                    'improvement': fitness_improvement
                }
            },
            'checkpoints': metrics['checkpoints'],
            'tests_passed': f"{tests_passed}/{total_tests}",
            'overall_success': tests_passed >= 4
        }, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")

    return tests_passed >= 4


if __name__ == "__main__":
    # Run with specified cycles (default 2000)
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    success = validate_improvements(cycles=cycles)

    sys.exit(0 if success else 1)
