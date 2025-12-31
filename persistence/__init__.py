"""
AEGIS-2 Persistence: Save and Load System State

Enable long-term evolution by persisting state across sessions.
"""

from .checkpoint import (
    PersistentGenome, CheckpointManager, Checkpoint,
    save_agent, load_agent, auto_checkpoint
)

__all__ = [
    'PersistentGenome', 'CheckpointManager', 'Checkpoint',
    'save_agent', 'load_agent', 'auto_checkpoint'
]
