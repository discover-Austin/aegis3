"""
Persistent State Management for AEGIS-2

Save and restore complete agent state:
- Genome structure and content
- Pattern algebra
- Goal states
- Novelty archive
- Autocatalytic networks
- Meta-evolution parameters
- Training history
"""

import json
import pickle
import gzip
import hashlib
import shutil
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Checkpoint:
    """A saved checkpoint of system state."""
    checkpoint_id: str
    timestamp: float
    generation: int
    fitness: float

    # Metadata
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # Metrics at checkpoint time
    metrics: Dict[str, Any] = field(default_factory=dict)

    # File paths
    genome_path: str = ""
    patterns_path: str = ""
    goals_path: str = ""
    novelty_path: str = ""
    autocatalysis_path: str = ""
    meta_path: str = ""
    history_path: str = ""

    # Size info
    total_size_bytes: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class PersistentGenome:
    """
    Wrapper for genome with save/load capabilities.

    Handles serialization of complex evolutionary structures.
    """

    def __init__(self, genome_data: Dict[str, Any]):
        self.data = genome_data
        self.version = "3.0"  # AEGIS-3 format

    def save(self, path: Path) -> int:
        """Save genome to compressed file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        save_data = {
            'version': self.version,
            'timestamp': datetime.now().timestamp(),
            'genome': self.data
        }

        # Compress and save
        with gzip.open(path, 'wb') as f:
            pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        return path.stat().st_size

    @classmethod
    def load(cls, path: Path):
        """Load genome from file."""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Genome file not found: {path}")

        with gzip.open(path, 'rb') as f:
            save_data = pickle.load(f)

        # Version compatibility check
        version = save_data.get('version', '1.0')
        if version != cls(None).version:
            print(f"Warning: Loading genome from version {version}, current version is 3.0")

        return cls(save_data['genome'])

    def get_hash(self) -> str:
        """Get content hash for versioning."""
        content = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class CheckpointManager:
    """
    Manages checkpoints for long-running evolution.

    Features:
    - Auto-checkpointing based on generation/time
    - Checkpoint branching
    - Checkpoint cleanup (keep best N)
    - Restore from checkpoint
    """

    def __init__(self, base_dir: str = "./checkpoints", auto_save_interval: int = 100):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.auto_save_interval = auto_save_interval
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.current_generation = 0

        # Load existing checkpoints
        self._load_checkpoint_index()

    def _load_checkpoint_index(self):
        """Load checkpoint index from disk."""
        index_path = self.base_dir / "checkpoint_index.json"

        if index_path.exists():
            with open(index_path, 'r') as f:
                data = json.load(f)
                self.checkpoints = {
                    k: Checkpoint.from_dict(v)
                    for k, v in data.items()
                }
                print(f"Loaded {len(self.checkpoints)} existing checkpoints")

    def _save_checkpoint_index(self):
        """Save checkpoint index to disk."""
        index_path = self.base_dir / "checkpoint_index.json"

        with open(index_path, 'w') as f:
            json.dump(
                {k: v.to_dict() for k, v in self.checkpoints.items()},
                f,
                indent=2
            )

    def save(
        self,
        agent,
        generation: int,
        fitness: float,
        name: str = "",
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> Checkpoint:
        """
        Save agent state to checkpoint.

        Args:
            agent: AEGIS2 agent instance
            generation: Current generation number
            fitness: Current fitness value
            name: Optional checkpoint name
            description: Optional description
            tags: Optional tags for categorization

        Returns:
            Checkpoint object
        """
        # Generate checkpoint ID
        timestamp = datetime.now().timestamp()
        checkpoint_id = f"gen{generation:06d}_{int(timestamp)}"

        # Create checkpoint directory
        checkpoint_dir = self.base_dir / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save each component
        genome_path = checkpoint_dir / "genome.pkl.gz"
        patterns_path = checkpoint_dir / "patterns.pkl.gz"
        goals_path = checkpoint_dir / "goals.pkl.gz"
        novelty_path = checkpoint_dir / "novelty.pkl.gz"
        autocatalysis_path = checkpoint_dir / "autocatalysis.pkl.gz"
        meta_path = checkpoint_dir / "meta.pkl.gz"
        history_path = checkpoint_dir / "history.json"

        # Save genome
        if hasattr(agent, 'genome'):
            genome_data = self._extract_genome_data(agent.genome)
            pg = PersistentGenome(genome_data)
            pg.save(genome_path)

        # Save patterns
        if hasattr(agent, 'pattern_algebra'):
            self._save_component(agent.pattern_algebra, patterns_path)

        # Save goals
        if hasattr(agent, 'goal_automata'):
            self._save_component(agent.goal_automata, goals_path)

        # Save novelty
        if hasattr(agent, 'novelty_engine'):
            self._save_component(agent.novelty_engine, novelty_path)

        # Save autocatalysis
        if hasattr(agent, 'autocatalytic_net'):
            self._save_component(agent.autocatalytic_net, autocatalysis_path)

        # Save meta-evolution
        if hasattr(agent, 'meta_evolution'):
            self._save_component(agent.meta_evolution, meta_path)

        # Save history
        if hasattr(agent, 'history'):
            with open(history_path, 'w') as f:
                json.dump(agent.history, f, indent=2, default=str)

        # Calculate total size
        total_size = sum(
            p.stat().st_size
            for p in checkpoint_dir.glob("*")
            if p.is_file()
        )

        # Get metrics
        metrics = {}
        if hasattr(agent, 'get_metrics'):
            metrics = agent.get_metrics()

        # Create checkpoint record
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=timestamp,
            generation=generation,
            fitness=fitness,
            name=name or f"Generation {generation}",
            description=description,
            tags=tags or [],
            metrics=metrics,
            genome_path=str(genome_path),
            patterns_path=str(patterns_path),
            goals_path=str(goals_path),
            novelty_path=str(novelty_path),
            autocatalysis_path=str(autocatalysis_path),
            meta_path=str(meta_path),
            history_path=str(history_path),
            total_size_bytes=total_size
        )

        # Register checkpoint
        self.checkpoints[checkpoint_id] = checkpoint
        self._save_checkpoint_index()

        self.current_generation = generation

        print(f"Checkpoint saved: {checkpoint_id} ({total_size / 1024 / 1024:.2f} MB)")

        return checkpoint

    def load(self, checkpoint_id: str, agent_class):
        """
        Load agent from checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to load
            agent_class: Agent class to instantiate

        Returns:
            Restored agent instance
        """
        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        checkpoint = self.checkpoints[checkpoint_id]

        # Load genome
        genome_data = None
        if Path(checkpoint.genome_path).exists():
            pg = PersistentGenome.load(Path(checkpoint.genome_path))
            genome_data = pg.data

        # Create agent (simplified - actual implementation depends on agent constructor)
        # This is a placeholder
        agent = agent_class(name=checkpoint.name)

        # Restore components
        if genome_data and hasattr(agent, 'genome'):
            self._restore_genome_data(agent.genome, genome_data)

        if Path(checkpoint.patterns_path).exists() and hasattr(agent, 'pattern_algebra'):
            agent.pattern_algebra = self._load_component(Path(checkpoint.patterns_path))

        if Path(checkpoint.goals_path).exists() and hasattr(agent, 'goal_automata'):
            agent.goal_automata = self._load_component(Path(checkpoint.goals_path))

        if Path(checkpoint.novelty_path).exists() and hasattr(agent, 'novelty_engine'):
            agent.novelty_engine = self._load_component(Path(checkpoint.novelty_path))

        if Path(checkpoint.autocatalysis_path).exists() and hasattr(agent, 'autocatalytic_net'):
            agent.autocatalytic_net = self._load_component(Path(checkpoint.autocatalysis_path))

        if Path(checkpoint.meta_path).exists() and hasattr(agent, 'meta_evolution'):
            agent.meta_evolution = self._load_component(Path(checkpoint.meta_path))

        if Path(checkpoint.history_path).exists() and hasattr(agent, 'history'):
            with open(checkpoint.history_path, 'r') as f:
                agent.history = json.load(f)

        print(f"Checkpoint loaded: {checkpoint_id} (generation {checkpoint.generation})")

        return agent

    def _extract_genome_data(self, genome) -> Dict[str, Any]:
        """Extract serializable data from genome."""
        # This is simplified - actual implementation depends on genome structure
        data = {}

        if hasattr(genome, 'to_dict'):
            data = genome.to_dict()
        elif hasattr(genome, '__dict__'):
            data = {
                k: v for k, v in genome.__dict__.items()
                if not k.startswith('_') and self._is_serializable(v)
            }

        return data

    def _restore_genome_data(self, genome, data: Dict[str, Any]):
        """Restore genome from serialized data."""
        if hasattr(genome, 'from_dict'):
            genome.from_dict(data)
        else:
            for k, v in data.items():
                if hasattr(genome, k):
                    setattr(genome, k, v)

    def _is_serializable(self, obj) -> bool:
        """Check if object is easily serializable."""
        return isinstance(obj, (int, float, str, bool, list, dict, tuple, type(None)))

    def _save_component(self, component, path: Path):
        """Save a component using pickle."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, 'wb') as f:
            pickle.dump(component, f, protocol=pickle.HIGHEST_PROTOCOL)

    def _load_component(self, path: Path):
        """Load a component using pickle."""
        with gzip.open(path, 'rb') as f:
            return pickle.load(f)

    def auto_checkpoint(self, agent, generation: int, fitness: float) -> Optional[Checkpoint]:
        """
        Automatically checkpoint if interval reached.

        Returns checkpoint if created, None otherwise.
        """
        if generation % self.auto_save_interval == 0:
            return self.save(
                agent,
                generation,
                fitness,
                name=f"Auto-checkpoint gen {generation}",
                tags=['auto']
            )
        return None

    def cleanup(self, keep_best: int = 10, keep_recent: int = 5):
        """
        Clean up old checkpoints, keeping best and most recent.

        Args:
            keep_best: Number of best (by fitness) checkpoints to keep
            keep_recent: Number of recent checkpoints to keep
        """
        if len(self.checkpoints) <= keep_best + keep_recent:
            return

        # Sort by fitness
        by_fitness = sorted(
            self.checkpoints.values(),
            key=lambda c: c.fitness,
            reverse=True
        )

        # Sort by timestamp
        by_time = sorted(
            self.checkpoints.values(),
            key=lambda c: c.timestamp,
            reverse=True
        )

        # Keep these
        keep_ids = set()
        keep_ids.update(c.checkpoint_id for c in by_fitness[:keep_best])
        keep_ids.update(c.checkpoint_id for c in by_time[:keep_recent])

        # Delete others
        for checkpoint_id, checkpoint in list(self.checkpoints.items()):
            if checkpoint_id not in keep_ids:
                checkpoint_dir = self.base_dir / checkpoint_id
                if checkpoint_dir.exists():
                    shutil.rmtree(checkpoint_dir)
                del self.checkpoints[checkpoint_id]
                print(f"Cleaned up checkpoint: {checkpoint_id}")

        self._save_checkpoint_index()

    def list_checkpoints(
        self,
        tags: Optional[List[str]] = None,
        min_fitness: Optional[float] = None
    ) -> List[Checkpoint]:
        """
        List checkpoints with optional filtering.

        Args:
            tags: Filter by tags
            min_fitness: Minimum fitness threshold

        Returns:
            List of matching checkpoints
        """
        checkpoints = list(self.checkpoints.values())

        if tags:
            checkpoints = [
                c for c in checkpoints
                if any(tag in c.tags for tag in tags)
            ]

        if min_fitness is not None:
            checkpoints = [
                c for c in checkpoints
                if c.fitness >= min_fitness
            ]

        return sorted(checkpoints, key=lambda c: c.timestamp, reverse=True)

    def get_best(self, n: int = 1) -> List[Checkpoint]:
        """Get N best checkpoints by fitness."""
        return sorted(
            self.checkpoints.values(),
            key=lambda c: c.fitness,
            reverse=True
        )[:n]

    def get_latest(self, n: int = 1) -> List[Checkpoint]:
        """Get N most recent checkpoints."""
        return sorted(
            self.checkpoints.values(),
            key=lambda c: c.timestamp,
            reverse=True
        )[:n]


# Convenience functions

def save_agent(
    agent,
    path: str,
    generation: int = 0,
    fitness: float = 0.0,
    **kwargs
) -> Checkpoint:
    """
    Save agent to checkpoint.

    Convenience wrapper around CheckpointManager.
    """
    manager = CheckpointManager(base_dir=str(Path(path).parent))
    return manager.save(agent, generation, fitness, **kwargs)


def load_agent(checkpoint_id: str, base_dir: str, agent_class):
    """
    Load agent from checkpoint.

    Convenience wrapper around CheckpointManager.
    """
    manager = CheckpointManager(base_dir=base_dir)
    return manager.load(checkpoint_id, agent_class)


def auto_checkpoint(
    manager: CheckpointManager,
    agent,
    generation: int,
    fitness: float
) -> Optional[Checkpoint]:
    """
    Auto-checkpoint wrapper.

    Usage in training loop:
    ```
    manager = CheckpointManager()
    for gen in range(10000):
        agent.step()
        auto_checkpoint(manager, agent, gen, agent.fitness)
    ```
    """
    return manager.auto_checkpoint(agent, generation, fitness)
