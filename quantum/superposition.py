"""
Quantum-Inspired Superposition for Parallel Hypothesis Testing

Inspired by quantum superposition and Many-Worlds Interpretation, this module
allows the system to maintain and evolve MULTIPLE HYPOTHESES IN PARALLEL.

Key concepts:
- Superposition: Multiple hypotheses exist simultaneously
- Amplitude: "Probability weight" of each hypothesis
- Interference: Hypotheses can reinforce or cancel
- Measurement: Collapsing to a single hypothesis when needed
- Entanglement: Correlations between hypotheses

This enables exponentially more efficient exploration by testing many
possibilities at once, then focusing on the most promising branches.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Callable
from collections import defaultdict


@dataclass
class Hypothesis:
    """A single hypothesis in superposition."""
    id: str
    state: Any  # The actual hypothesis content
    amplitude: complex  # Complex amplitude (real + imaginary)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def probability(self) -> float:
        """Probability of this hypothesis (|amplitude|²)."""
        return abs(self.amplitude) ** 2

    @property
    def phase(self) -> float:
        """Phase of the complex amplitude."""
        return math.atan2(self.amplitude.imag, self.amplitude.real)


class QuantumSuperposition:
    """
    Maintains a superposition of multiple hypotheses.

    Hypotheses interfere quantum-mechanically, allowing for:
    - Parallel exploration
    - Constructive/destructive interference
    - Amplitude amplification of good hypotheses
    - Decoherence and measurement
    """

    def __init__(self, initial_hypotheses: Optional[List[Any]] = None):
        """
        Initialize superposition.

        Args:
            initial_hypotheses: Initial hypotheses (equal superposition)
        """
        self.hypotheses: List[Hypothesis] = []
        self.next_id = 0
        self.measurement_history: List[Tuple[str, Any]] = []

        if initial_hypotheses:
            # Create equal superposition
            n = len(initial_hypotheses)
            amplitude = complex(1.0 / math.sqrt(n), 0)
            for state in initial_hypotheses:
                self.add_hypothesis(state, amplitude)
        else:
            # Single hypothesis in |0⟩ state
            self.add_hypothesis(None, complex(1.0, 0))

    def add_hypothesis(
        self,
        state: Any,
        amplitude: Optional[complex] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Add a hypothesis to the superposition."""
        if amplitude is None:
            # Default: small amplitude
            amplitude = complex(0.1, 0)

        hyp = Hypothesis(
            id=f"hyp_{self.next_id}",
            state=state,
            amplitude=amplitude,
            metadata=metadata or {}
        )
        self.hypotheses.append(hyp)
        self.next_id += 1

        # Renormalize
        self.normalize()

        return hyp.id

    def normalize(self):
        """Normalize amplitudes so probabilities sum to 1."""
        total_prob = sum(h.probability for h in self.hypotheses)
        if total_prob > 0:
            factor = 1.0 / math.sqrt(total_prob)
            for h in self.hypotheses:
                h.amplitude *= factor

    def apply_unitary(self, transformation: Callable[[Any], Tuple[Any, complex]]):
        """
        Apply a unitary transformation to all hypotheses.

        Args:
            transformation: Function that maps (state) -> (new_state, amplitude_factor)
        """
        new_hypotheses = []
        for h in self.hypotheses:
            new_state, amp_factor = transformation(h.state)
            new_hyp = Hypothesis(
                id=f"{h.id}_transformed",
                state=new_state,
                amplitude=h.amplitude * amp_factor,
                metadata=h.metadata.copy()
            )
            new_hypotheses.append(new_hyp)

        self.hypotheses = new_hypotheses
        self.normalize()

    def amplitude_amplification(
        self,
        fitness_fn: Callable[[Any], float],
        iterations: int = 1
    ):
        """
        Grover-style amplitude amplification.

        Amplifies amplitudes of "good" hypotheses (high fitness).
        """
        for _ in range(iterations):
            # Evaluate fitness
            fitnesses = [fitness_fn(h.state) for h in self.hypotheses]
            if not fitnesses:
                continue

            # Normalize fitnesses to [0, 1]
            min_fit = min(fitnesses)
            max_fit = max(fitnesses)
            if max_fit > min_fit:
                normalized_fitnesses = [
                    (f - min_fit) / (max_fit - min_fit)
                    for f in fitnesses
                ]
            else:
                normalized_fitnesses = [0.5] * len(fitnesses)

            # Oracle: Mark good states with phase flip
            for h, fit in zip(self.hypotheses, normalized_fitnesses):
                if fit > 0.7:  # Good hypothesis
                    h.amplitude *= -1  # Phase flip

            # Inversion about average
            avg_amplitude = sum(h.amplitude for h in self.hypotheses) / len(self.hypotheses)
            for h in self.hypotheses:
                h.amplitude = 2 * avg_amplitude - h.amplitude

            self.normalize()

    def interference(self, other: 'QuantumSuperposition', coupling: float = 0.5):
        """
        Interfere with another superposition.

        Creates entanglement and correlation between hypotheses.
        """
        # Create product state (simplified)
        new_hypotheses = []

        for h1 in self.hypotheses:
            for h2 in other.hypotheses:
                # Combine states (simplified: just concatenate)
                if isinstance(h1.state, list) and isinstance(h2.state, list):
                    combined_state = h1.state + h2.state
                else:
                    combined_state = (h1.state, h2.state)

                # Amplitude is product (with coupling factor)
                combined_amplitude = coupling * h1.amplitude * h2.amplitude

                new_hyp = Hypothesis(
                    id=f"{h1.id}_{h2.id}",
                    state=combined_state,
                    amplitude=combined_amplitude,
                    metadata={'parent1': h1.id, 'parent2': h2.id}
                )
                new_hypotheses.append(new_hyp)

        self.hypotheses = new_hypotheses
        self.normalize()

    def measure(
        self,
        collapse: bool = True,
        top_k: Optional[int] = None
    ) -> Tuple[Any, float]:
        """
        Measure the superposition, collapsing to a single hypothesis.

        Args:
            collapse: If True, collapse to measured state
            top_k: If set, only consider top k most probable hypotheses

        Returns:
            (measured_state, probability)
        """
        if not self.hypotheses:
            return None, 0.0

        # Filter to top k if specified
        if top_k:
            sorted_hyps = sorted(self.hypotheses, key=lambda h: h.probability, reverse=True)
            candidates = sorted_hyps[:top_k]
        else:
            candidates = self.hypotheses

        # Probabilistic measurement
        probs = [h.probability for h in candidates]
        total = sum(probs)
        if total == 0:
            return None, 0.0

        probs = [p / total for p in probs]

        # Sample based on probability
        r = random.random()
        cumsum = 0
        measured_hyp = None
        for h, p in zip(candidates, probs):
            cumsum += p
            if r <= cumsum:
                measured_hyp = h
                break

        if measured_hyp is None:
            measured_hyp = candidates[-1]

        # Record measurement
        self.measurement_history.append((measured_hyp.id, measured_hyp.state))

        # Collapse if requested
        if collapse:
            self.hypotheses = [Hypothesis(
                id=f"{measured_hyp.id}_collapsed",
                state=measured_hyp.state,
                amplitude=complex(1.0, 0),
                metadata=measured_hyp.metadata
            )]

        return measured_hyp.state, measured_hyp.probability

    def decohere(self, decoherence_rate: float = 0.1):
        """
        Apply decoherence - phases randomize, superposition → classical mixture.

        Simulates environmental interaction that destroys quantum coherence.
        """
        for h in self.hypotheses:
            # Add random phase noise
            phase_noise = random.gauss(0, decoherence_rate)
            magnitude = abs(h.amplitude)
            phase = h.phase + phase_noise

            h.amplitude = magnitude * complex(math.cos(phase), math.sin(phase))

    def branch(self, branching_fn: Callable[[Any], List[Any]]) -> 'QuantumSuperposition':
        """
        Branch hypotheses (Many-Worlds style).

        Each hypothesis spawns multiple children.
        """
        new_superposition = QuantumSuperposition()
        new_superposition.hypotheses = []

        for h in self.hypotheses:
            branches = branching_fn(h.state)
            if not branches:
                continue

            # Divide amplitude among branches
            branch_amplitude = h.amplitude / math.sqrt(len(branches))

            for branch_state in branches:
                new_hyp = Hypothesis(
                    id=f"{h.id}_branch_{len(new_superposition.hypotheses)}",
                    state=branch_state,
                    amplitude=branch_amplitude,
                    metadata={'parent': h.id}
                )
                new_superposition.hypotheses.append(new_hyp)

        new_superposition.normalize()
        return new_superposition

    def prune(self, min_probability: float = 0.01):
        """Remove low-probability hypotheses."""
        self.hypotheses = [
            h for h in self.hypotheses
            if h.probability >= min_probability
        ]
        self.normalize()

    def get_entropy(self) -> float:
        """Calculate Shannon entropy of the probability distribution."""
        entropy = 0.0
        for h in self.hypotheses:
            p = h.probability
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the superposition."""
        if not self.hypotheses:
            return {
                'num_hypotheses': 0,
                'entropy': 0.0,
                'max_probability': 0.0,
                'measurements': len(self.measurement_history)
            }

        probs = [h.probability for h in self.hypotheses]
        phases = [h.phase for h in self.hypotheses]

        return {
            'num_hypotheses': len(self.hypotheses),
            'entropy': self.get_entropy(),
            'max_probability': max(probs),
            'avg_probability': sum(probs) / len(probs),
            'phase_variance': sum((p - sum(phases)/len(phases))**2 for p in phases) / len(phases),
            'measurements': len(self.measurement_history),
            'most_probable': max(self.hypotheses, key=lambda h: h.probability).id
        }


class MultiHypothesisTracker:
    """
    Manages multiple superpositions for different aspects of a problem.

    Allows parallel exploration of:
    - Multiple solution approaches
    - Different parameter settings
    - Alternative world models
    - Competing goals
    """

    def __init__(self):
        """Initialize multi-hypothesis tracker."""
        self.superpositions: Dict[str, QuantumSuperposition] = {}
        self.correlations: Dict[Tuple[str, str], float] = {}

    def create_superposition(
        self,
        name: str,
        initial_hypotheses: List[Any]
    ) -> QuantumSuperposition:
        """Create a named superposition."""
        sp = QuantumSuperposition(initial_hypotheses)
        self.superpositions[name] = sp
        return sp

    def measure_all(self, collapse: bool = False) -> Dict[str, Tuple[Any, float]]:
        """Measure all superpositions."""
        results = {}
        for name, sp in self.superpositions.items():
            state, prob = sp.measure(collapse=collapse)
            results[name] = (state, prob)
        return results

    def correlate(self, name1: str, name2: str, strength: float = 0.5):
        """Create correlation between two superpositions."""
        if name1 in self.superpositions and name2 in self.superpositions:
            self.correlations[(name1, name2)] = strength
            self.correlations[(name2, name1)] = strength

            # Apply interference based on correlation
            sp1 = self.superpositions[name1]
            sp2 = self.superpositions[name2]
            sp1.interference(sp2, coupling=strength)

    def get_best_hypothesis_set(self) -> Dict[str, Any]:
        """Get the most probable hypothesis from each superposition."""
        best = {}
        for name, sp in self.superpositions.items():
            if sp.hypotheses:
                best_hyp = max(sp.hypotheses, key=lambda h: h.probability)
                best[name] = best_hyp.state
        return best

    def global_statistics(self) -> Dict[str, Any]:
        """Get global statistics across all superpositions."""
        return {
            'num_superpositions': len(self.superpositions),
            'total_hypotheses': sum(len(sp.hypotheses) for sp in self.superpositions.values()),
            'avg_entropy': sum(sp.get_entropy() for sp in self.superpositions.values()) / len(self.superpositions) if self.superpositions else 0.0,
            'correlations': len(self.correlations),
            'superpositions': {
                name: sp.get_statistics()
                for name, sp in self.superpositions.items()
            }
        }


# Utility functions

def create_branching_search(
    initial_state: Any,
    branching_fn: Callable[[Any], List[Any]],
    fitness_fn: Callable[[Any], float],
    max_depth: int = 5,
    prune_threshold: float = 0.01
) -> Any:
    """
    Perform branching search using quantum superposition.

    Explores all branches in parallel, uses amplitude amplification
    to focus on promising branches.

    Returns:
        Best state found
    """
    sp = QuantumSuperposition([initial_state])

    for depth in range(max_depth):
        # Branch
        sp = sp.branch(branching_fn)

        # Amplify good branches
        sp.amplitude_amplification(fitness_fn, iterations=1)

        # Prune unlikely branches
        sp.prune(min_probability=prune_threshold)

        # Decohere slightly (prevents exponential growth)
        sp.decohere(decoherence_rate=0.05)

        if len(sp.hypotheses) == 0:
            break

    # Measure to get best
    best_state, prob = sp.measure(collapse=False, top_k=1)
    return best_state
