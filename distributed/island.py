"""
Distributed AEGIS using Island Model

Scale evolution across multiple machines/processes.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class Island:
    """An island in the island model."""
    island_id: str
    population: List[Any] = field(default_factory=list)
    best_fitness: float = 0.0


class DistributedAEGIS:
    """Distributed evolution using island model."""

    def __init__(self, num_islands: int = 4, migration_rate: float = 0.1):
        self.num_islands = num_islands
        self.migration_rate = migration_rate

        self.islands: Dict[str, Island] = {}
        for i in range(num_islands):
            self.islands[f"island_{i}"] = Island(island_id=f"island_{i}")

    def spawn_island(self, config: Dict[str, Any]) -> Island:
        """Spawn a new island."""
        island_id = f"island_{len(self.islands)}"
        island = Island(island_id=island_id)
        self.islands[island_id] = island
        return island

    def migrate(self, agent: Any, from_island: str, to_island: str):
        """Migrate agent between islands."""
        if from_island in self.islands and to_island in self.islands:
            # Remove from source
            if agent in self.islands[from_island].population:
                self.islands[from_island].population.remove(agent)

            # Add to destination
            self.islands[to_island].population.append(agent)

    def migration_step(self):
        """Perform migration between islands."""
        island_ids = list(self.islands.keys())

        for island_id in island_ids:
            island = self.islands[island_id]

            # Select migrants
            num_migrants = int(len(island.population) * self.migration_rate)

            for _ in range(num_migrants):
                if island.population:
                    # Select random agent
                    agent = random.choice(island.population)

                    # Select random destination
                    dest_id = random.choice([iid for iid in island_ids if iid != island_id])

                    # Migrate
                    self.migrate(agent, island_id, dest_id)

    def aggregate_discoveries(self) -> Dict[str, Any]:
        """Aggregate best solutions from all islands."""
        best_agents = []

        for island in self.islands.values():
            if island.population:
                # Get best from island
                best = max(island.population, key=lambda a: getattr(a, 'fitness', 0))
                best_agents.append({
                    'island': island.island_id,
                    'agent': best,
                    'fitness': getattr(best, 'fitness', 0)
                })

        return {
            'num_islands': len(self.islands),
            'best_agents': sorted(best_agents, key=lambda x: x['fitness'], reverse=True)
        }
