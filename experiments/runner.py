"""
Long-Run Experiments Infrastructure

Support for multi-million cycle evolution experiments.
"""

import time
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class LongRunConfig:
    """Configuration for long-run experiment."""
    max_generations: int = 1000000
    checkpoint_interval: int = 1000
    log_interval: int = 100
    early_stop_patience: int = 10000


class ExperimentRunner:
    """Runner for long-duration experiments."""

    def __init__(self, config: LongRunConfig, output_dir: str = "./experiments"):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_log: list = []
        self.best_fitness = float('-inf')
        self.generations_without_improvement = 0

    def run(self, agent, experiment_name: str) -> Dict[str, Any]:
        """Run long experiment."""
        print(f"Starting experiment: {experiment_name}")
        print(f"Max generations: {self.config.max_generations}")

        start_time = time.time()

        for gen in range(self.config.max_generations):
            # Evolution step
            result = agent.step({})

            # Log
            if gen % self.config.log_interval == 0:
                fitness = result.get('fitness', 0)
                self.metrics_log.append({'generation': gen, 'fitness': fitness})

                elapsed = time.time() - start_time
                print(f"Gen {gen}: fitness={fitness:.4f}, time={elapsed:.1f}s")

                # Track improvement
                if fitness > self.best_fitness:
                    self.best_fitness = fitness
                    self.generations_without_improvement = 0
                else:
                    self.generations_without_improvement += 1

            # Checkpoint
            if gen % self.config.checkpoint_interval == 0:
                self._save_checkpoint(agent, gen)

            # Early stopping
            if self.generations_without_improvement > self.config.early_stop_patience:
                print(f"Early stopping at generation {gen}")
                break

        total_time = time.time() - start_time

        # Final report
        return {
            'experiment_name': experiment_name,
            'generations': gen + 1,
            'best_fitness': self.best_fitness,
            'total_time': total_time,
            'avg_time_per_gen': total_time / (gen + 1)
        }

    def _save_checkpoint(self, agent, generation: int):
        """Save checkpoint."""
        checkpoint_file = self.output_dir / f"checkpoint_gen{generation}.json"

        data = {
            'generation': generation,
            'best_fitness': self.best_fitness,
            'metrics': self.metrics_log[-100:]  # Last 100 entries
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
