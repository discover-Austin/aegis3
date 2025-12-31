"""
Communication Protocol Evolution

Agents develop shared communication through coordination pressure.
Language emerges from interaction, not pre-definition.
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class Signal:
    """A communication signal."""
    signal_id: str
    content: List[float]  # Signal representation
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class Meaning:
    """A semantic meaning."""
    meaning_id: str
    representation: List[float]  # Semantic representation
    associated_signals: List[str] = field(default_factory=list)


class CommunicationProtocol:
    """Mapping between signals and meanings."""

    def __init__(self, signal_dim: int = 10, meaning_dim: int = 10):
        self.signal_dim = signal_dim
        self.meaning_dim = meaning_dim

        # Signal -> Meaning mapping
        self.signal_to_meaning: Dict[str, str] = {}

        # Meaning -> Signal mapping
        self.meaning_to_signal: Dict[str, str] = {}

        # All signals and meanings
        self.signals: Dict[str, Signal] = {}
        self.meanings: Dict[str, Meaning] = {}

    def create_signal(self, content: Optional[List[float]] = None) -> Signal:
        """Create a new signal."""
        if content is None:
            content = [random.gauss(0, 1) for _ in range(self.signal_dim)]

        signal_id = hashlib.md5(str(content).encode()).hexdigest()[:12]

        signal = Signal(signal_id=signal_id, content=content)
        self.signals[signal_id] = signal

        return signal

    def create_meaning(self, representation: Optional[List[float]] = None) -> Meaning:
        """Create a new meaning."""
        if representation is None:
            representation = [random.gauss(0, 1) for _ in range(self.meaning_dim)]

        meaning_id = hashlib.md5(str(representation).encode()).hexdigest()[:12]

        meaning = Meaning(meaning_id=meaning_id, representation=representation)
        self.meanings[meaning_id] = meaning

        return meaning

    def associate(self, signal_id: str, meaning_id: str):
        """Associate a signal with a meaning."""
        self.signal_to_meaning[signal_id] = meaning_id
        self.meaning_to_signal[meaning_id] = signal_id

        if meaning_id in self.meanings:
            if signal_id not in self.meanings[meaning_id].associated_signals:
                self.meanings[meaning_id].associated_signals.append(signal_id)

    def interpret(self, signal_id: str) -> Optional[str]:
        """Interpret a signal to get its meaning."""
        return self.signal_to_meaning.get(signal_id)

    def express(self, meaning_id: str) -> Optional[str]:
        """Express a meaning as a signal."""
        return self.meaning_to_signal.get(meaning_id)


class EmergentLanguage:
    """
    System for evolving communication between agents.

    Language emerges through:
    1. Signaling game (sender-receiver)
    2. Coordination success reinforces signal-meaning pairs
    3. Population-wide conventions emerge
    """

    def __init__(
        self,
        num_agents: int = 10,
        signal_dim: int = 10,
        meaning_dim: int = 10
    ):
        self.num_agents = num_agents
        self.signal_dim = signal_dim
        self.meaning_dim = meaning_dim

        # Each agent has its own protocol
        self.protocols: Dict[str, CommunicationProtocol] = {}
        for i in range(num_agents):
            agent_id = f"agent_{i}"
            self.protocols[agent_id] = CommunicationProtocol(signal_dim, meaning_dim)

        # Shared signal space (population-level)
        self.shared_signals: Dict[str, Signal] = {}
        self.shared_meanings: Dict[str, Meaning] = {}

        # Communication history
        self.interactions: List[Dict[str, Any]] = []

    def communicate(
        self,
        sender_id: str,
        receiver_id: str,
        meaning_id: str
    ) -> bool:
        """
        Communication episode between sender and receiver.

        Returns True if communication was successful.
        """
        sender = self.protocols.get(sender_id)
        receiver = self.protocols.get(receiver_id)

        if not sender or not receiver:
            return False

        # Sender expresses meaning
        signal_id = sender.express(meaning_id)

        if not signal_id:
            # Sender doesn't know how to express this meaning
            # Create new signal
            signal = sender.create_signal()
            sender.associate(signal.signal_id, meaning_id)
            signal_id = signal.signal_id

            # Add to shared space
            self.shared_signals[signal_id] = signal

        # Receiver interprets signal
        interpreted_meaning = receiver.interpret(signal_id)

        success = (interpreted_meaning == meaning_id)

        # Record interaction
        self.interactions.append({
            'sender': sender_id,
            'receiver': receiver_id,
            'intended_meaning': meaning_id,
            'signal': signal_id,
            'interpreted_meaning': interpreted_meaning,
            'success': success
        })

        # Update protocols based on success
        if success:
            # Reinforce this association
            if signal_id in sender.signals:
                sender.signals[signal_id].usage_count += 1
                sender.signals[signal_id].success_rate = (
                    0.9 * sender.signals[signal_id].success_rate + 0.1 * 1.0
                )
        else:
            # Failed communication - receiver learns
            if signal_id not in receiver.signal_to_meaning:
                receiver.associate(signal_id, meaning_id)

        return success

    def evolve_language(self, num_interactions: int = 100):
        """
        Run communication episodes to evolve language.

        Returns success rate over episodes.
        """
        successes = 0

        for _ in range(num_interactions):
            # Random sender and receiver
            sender_id = f"agent_{random.randint(0, self.num_agents - 1)}"
            receiver_id = f"agent_{random.randint(0, self.num_agents - 1)}"

            if sender_id == receiver_id:
                continue  # Skip self-communication

            # Random meaning to communicate
            meaning_id = f"meaning_{random.randint(0, 9)}"

            # Ensure meaning exists
            if meaning_id not in self.shared_meanings:
                meaning = Meaning(
                    meaning_id=meaning_id,
                    representation=[random.gauss(0, 1) for _ in range(self.meaning_dim)]
                )
                self.shared_meanings[meaning_id] = meaning

            # Communicate
            success = self.communicate(sender_id, receiver_id, meaning_id)

            if success:
                successes += 1

        return successes / num_interactions if num_interactions > 0 else 0.0

    def get_convergence(self) -> float:
        """
        Measure convergence of population to shared language.

        Returns fraction of signal-meaning pairs that are shared.
        """
        if not self.protocols:
            return 0.0

        # Count how many agents share each signal-meaning association
        association_counts: Dict[Tuple[str, str], int] = {}

        for protocol in self.protocols.values():
            for signal_id, meaning_id in protocol.signal_to_meaning.items():
                key = (signal_id, meaning_id)
                association_counts[key] = association_counts.get(key, 0) + 1

        # Associations shared by majority (>50% of agents)
        majority_threshold = self.num_agents / 2
        shared_associations = sum(
            1 for count in association_counts.values()
            if count > majority_threshold
        )

        total_associations = len(association_counts)

        return shared_associations / total_associations if total_associations > 0 else 0.0

    def get_statistics(self) -> Dict[str, Any]:
        """Get language evolution statistics."""
        if not self.interactions:
            return {}

        recent = self.interactions[-100:]
        recent_success = sum(1 for i in recent if i['success']) / len(recent)

        return {
            'total_interactions': len(self.interactions),
            'recent_success_rate': recent_success,
            'convergence': self.get_convergence(),
            'shared_signals': len(self.shared_signals),
            'shared_meanings': len(self.shared_meanings),
            'num_agents': self.num_agents
        }
