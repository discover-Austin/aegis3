"""
Phase Transition Detection

Identifies critical points and bifurcations in evolution:
- Order parameters and susceptibility
- Critical slowing down
- Bifurcation points
- Self-organized criticality signatures
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass
class PhaseTransition:
    """Detected phase transition."""
    generation: int
    transition_type: str  # 'continuous', 'discontinuous', 'bifurcation'
    order_parameter_before: float
    order_parameter_after: float
    confidence: float


class PhaseTransitionDetector:
    """
    Detect phase transitions in evolving systems.

    Uses concepts from statistical physics:
    - Order parameters
    - Susceptibility
    - Correlation length
    - Critical slowing down
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.history: deque = deque(maxlen=window_size * 2)
        self.transitions: List[PhaseTransition] = []

    def update(self, state: Dict[str, float], generation: int) -> Optional[PhaseTransition]:
        """
        Update with new state.

        state: dictionary of observables (fitness, diversity, etc.)

        Returns PhaseTransition if detected.
        """
        self.history.append((generation, state))

        if len(self.history) < self.window_size:
            return None

        # Compute order parameter
        order_param = self._compute_order_parameter()

        # Detect transition
        transition = self._detect_transition(generation, order_param)

        if transition:
            self.transitions.append(transition)

        return transition

    def _compute_order_parameter(self) -> float:
        """
        Compute order parameter from recent history.

        Order parameter: measure of 'organization' in system.
        0 = disordered, 1 = ordered
        """
        if not self.history:
            return 0.0

        recent = list(self.history)[-self.window_size // 2:]

        # Multiple possible order parameters
        # Use fitness variance as proxy for order
        fitnesses = [state.get('fitness', 0.0) for _, state in recent]

        if not fitnesses:
            return 0.0

        mean_fitness = sum(fitnesses) / len(fitnesses)
        variance = sum((f - mean_fitness) ** 2 for f in fitnesses) / len(fitnesses)

        # Low variance = high order
        order = 1.0 / (1.0 + variance)

        return order

    def _detect_transition(self, generation: int, current_order: float) -> Optional[PhaseTransition]:
        """Detect if system is undergoing phase transition."""
        if len(self.history) < self.window_size:
            return None

        # Split history
        earlier = list(self.history)[:self.window_size // 2]
        later = list(self.history)[self.window_size // 2:]

        # Compute order parameters for each period
        earlier_fitnesses = [state.get('fitness', 0.0) for _, state in earlier]
        later_fitnesses = [state.get('fitness', 0.0) for _, state in later]

        if not earlier_fitnesses or not later_fitnesses:
            return None

        def compute_order(fitnesses):
            mean = sum(fitnesses) / len(fitnesses)
            var = sum((f - mean) ** 2 for f in fitnesses) / len(fitnesses)
            return 1.0 / (1.0 + var)

        order_before = compute_order(earlier_fitnesses)
        order_after = compute_order(later_fitnesses)

        # Check for significant change
        order_change = abs(order_after - order_before)

        # Threshold for transition
        if order_change > 0.2:
            # Determine type
            if order_change > 0.5:
                transition_type = 'discontinuous'
                confidence = min(1.0, order_change / 0.5)
            else:
                transition_type = 'continuous'
                confidence = order_change / 0.2

            return PhaseTransition(
                generation=generation,
                transition_type=transition_type,
                order_parameter_before=order_before,
                order_parameter_after=order_after,
                confidence=confidence
            )

        return None


class CriticalityAnalyzer:
    """
    Analyze if system is at critical point.

    Signs of criticality:
    - Power law distributions
    - Scale invariance
    - Long-range correlations
    """

    def __init__(self):
        self.avalanche_sizes: List[int] = []
        self.event_history: deque = deque(maxlen=1000)

    def record_event(self, magnitude: float):
        """Record event (e.g., fitness change, mutation effect)."""
        self.event_history.append(magnitude)

        # Detect avalanche (cascade of events)
        if magnitude > 0.1:  # Threshold for significant event
            self.avalanche_sizes.append(1)
        elif self.avalanche_sizes:
            self.avalanche_sizes[-1] += 1

    def compute_criticality_metrics(self) -> Dict[str, float]:
        """
        Compute metrics indicating criticality.

        Returns:
        - power_law_exponent: α in P(s) ~ s^-α
        - scale_invariance: how self-similar across scales
        - correlation_length: how far events propagate
        """
        if len(self.avalanche_sizes) < 20:
            return {
                'power_law_exponent': 0.0,
                'scale_invariance': 0.0,
                'correlation_length': 0.0,
                'at_criticality': False
            }

        # Fit power law to avalanche sizes
        exponent = self._fit_power_law(self.avalanche_sizes)

        # Scale invariance: check if distribution similar at different scales
        scale_inv = self._compute_scale_invariance()

        # Correlation length from autocorrelation
        corr_length = self._compute_correlation_length()

        # At criticality: exponent ~ 1.5-2.5, high scale invariance
        at_criticality = (1.5 < exponent < 2.5) and scale_inv > 0.6

        return {
            'power_law_exponent': exponent,
            'scale_invariance': scale_inv,
            'correlation_length': corr_length,
            'at_criticality': at_criticality
        }

    def _fit_power_law(self, sizes: List[int]) -> float:
        """
        Fit power law to size distribution.

        P(s) ~ s^-α

        Returns exponent α.
        """
        if not sizes:
            return 0.0

        # Log-log regression
        from collections import Counter
        counts = Counter(sizes)

        if len(counts) < 3:
            return 0.0

        log_sizes = []
        log_probs = []

        total = len(sizes)

        for size, count in counts.items():
            if size > 0 and count > 0:
                log_sizes.append(math.log(size))
                log_probs.append(math.log(count / total))

        if len(log_sizes) < 2:
            return 0.0

        # Linear regression in log-log space
        n = len(log_sizes)
        mean_x = sum(log_sizes) / n
        mean_y = sum(log_probs) / n

        numerator = sum((log_sizes[i] - mean_x) * (log_probs[i] - mean_y) for i in range(n))
        denominator = sum((log_sizes[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Negative slope is the exponent
        return abs(slope)

    def _compute_scale_invariance(self) -> float:
        """
        Measure scale invariance.

        If system is scale-invariant, zooming in/out shows similar patterns.
        """
        if len(self.event_history) < 100:
            return 0.0

        events = list(self.event_history)

        # Compare distribution at different scales
        def distribution_similarity(data1, data2):
            # Bin and compare
            bins = 10
            hist1 = [0] * bins
            hist2 = [0] * bins

            for val in data1:
                bin_idx = min(bins - 1, int(val * bins))
                hist1[bin_idx] += 1

            for val in data2:
                bin_idx = min(bins - 1, int(val * bins))
                hist2[bin_idx] += 1

            # Normalize
            if sum(hist1) > 0:
                hist1 = [h / sum(hist1) for h in hist1]
            if sum(hist2) > 0:
                hist2 = [h / sum(hist2) for h in hist2]

            # Compare
            diff = sum(abs(h1 - h2) for h1, h2 in zip(hist1, hist2))
            return 1.0 - diff / 2.0  # Similarity

        # Compare first half vs second half
        mid = len(events) // 2
        first_half = events[:mid]
        second_half = events[mid:]

        similarity = distribution_similarity(first_half, second_half)

        return similarity

    def _compute_correlation_length(self) -> float:
        """
        Compute correlation length.

        How far do perturbations propagate?
        """
        if len(self.event_history) < 50:
            return 0.0

        events = list(self.event_history)

        # Autocorrelation
        max_lag = min(20, len(events) // 3)
        autocorr = []

        mean = sum(events) / len(events)
        var = sum((e - mean) ** 2 for e in events) / len(events)

        if var == 0:
            return 0.0

        for lag in range(1, max_lag):
            corr_sum = 0.0
            count = 0

            for i in range(len(events) - lag):
                corr_sum += (events[i] - mean) * (events[i + lag] - mean)
                count += 1

            if count > 0:
                corr = (corr_sum / count) / var
                autocorr.append(corr)

        if not autocorr:
            return 0.0

        # Correlation length: lag where correlation drops below threshold
        threshold = 0.2
        for i, corr in enumerate(autocorr):
            if corr < threshold:
                return float(i + 1)

        return float(len(autocorr))


class BifurcationDetector:
    """
    Detect bifurcation points.

    Bifurcation: parameter change causes qualitative change in behavior.
    System splits into distinct behavioral regimes.
    """

    def __init__(self):
        self.behavior_history: List[Any] = []
        self.bifurcations: List[Dict[str, Any]] = []

    def update(self, behavior: Any, parameter: float, generation: int):
        """
        Update with behavior at given parameter value.

        behavior: behavioral descriptor
        parameter: control parameter
        generation: current generation
        """
        self.behavior_history.append({
            'behavior': behavior,
            'parameter': parameter,
            'generation': generation
        })

        # Detect bifurcation
        bifurcation = self._detect_bifurcation()

        if bifurcation:
            self.bifurcations.append(bifurcation)

    def _detect_bifurcation(self) -> Optional[Dict[str, Any]]:
        """Detect if system has undergone bifurcation."""
        if len(self.behavior_history) < 50:
            return None

        recent = self.behavior_history[-50:]

        # Cluster behaviors
        clusters = self._cluster_behaviors([r['behavior'] for r in recent])

        # Bifurcation: sudden increase in number of distinct clusters
        if len(clusters) >= 2:
            # Check if this is new (wasn't multiple clusters before)
            earlier = self.behavior_history[-100:-50] if len(self.behavior_history) >= 100 else []

            if earlier:
                earlier_clusters = self._cluster_behaviors([r['behavior'] for r in earlier])

                if len(clusters) > len(earlier_clusters):
                    # Bifurcation detected
                    return {
                        'generation': recent[-1]['generation'],
                        'num_branches': len(clusters),
                        'parameter': recent[-1]['parameter'],
                        'type': 'branching'
                    }

        return None

    def _cluster_behaviors(self, behaviors: List[Any]) -> List[List[Any]]:
        """Simple clustering of behaviors."""
        if not behaviors:
            return []

        # Simple threshold-based clustering
        clusters = []

        for behavior in behaviors:
            # Try to add to existing cluster
            added = False

            for cluster in clusters:
                # Check if similar to cluster representative
                if self._behavior_distance(behavior, cluster[0]) < 0.3:
                    cluster.append(behavior)
                    added = True
                    break

            if not added:
                # Create new cluster
                clusters.append([behavior])

        return clusters

    def _behavior_distance(self, b1: Any, b2: Any) -> float:
        """Distance between behaviors."""
        if b1 == b2:
            return 0.0

        if isinstance(b1, (int, float)) and isinstance(b2, (int, float)):
            return abs(b1 - b2)

        if isinstance(b1, (list, tuple)) and isinstance(b2, (list, tuple)):
            if len(b1) != len(b2):
                return 1.0
            return sum(abs(a - b) for a, b in zip(b1, b2)) / max(len(b1), 1)

        return 1.0
