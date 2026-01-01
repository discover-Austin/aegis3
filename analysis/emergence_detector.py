"""
Emergence Detection System

Detects and characterizes emergent phenomena:
- Sudden capability jumps (discontinuous emergence)
- Gradual phase transitions (continuous emergence)
- Novel behavior patterns
- Synergistic effects (whole > sum of parts)
- Downward causation (high-level influencing low-level)
"""

import random
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Tuple
from collections import deque, defaultdict


class EmergenceType(Enum):
    """Types of emergent phenomena."""
    CAPABILITY_JUMP = "capability_jump"  # Sudden new ability
    PHASE_TRANSITION = "phase_transition"  # System-wide reorganization
    NOVEL_PATTERN = "novel_pattern"  # New behavioral pattern
    SYNERGY = "synergy"  # Combined effect > individual effects
    DOWNWARD_CAUSATION = "downward_causation"  # High-level affects low-level
    BIFURCATION = "bifurcation"  # System splits into distinct regimes
    CRITICALITY = "criticality"  # System reaches critical point
    ABSTRACTION = "abstraction"  # New conceptual level emerges


@dataclass
class EmergenceEvent:
    """Detected emergence event."""
    event_type: EmergenceType
    timestamp: int
    magnitude: float  # 0-1, strength of emergence
    description: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5  # How confident we are this is real emergence


class EmergenceDetector:
    """
    Detects emergent phenomena in evolving systems.

    Uses multiple signals:
    - Discontinuities in performance
    - Changes in behavioral repertoire
    - Organizational transitions
    - Complexity measures
    """

    def __init__(self, window_size: int = 50, sensitivity: float = 0.5):
        self.window_size = window_size
        self.sensitivity = sensitivity

        # History
        self.fitness_history: deque = deque(maxlen=window_size * 2)
        self.complexity_history: deque = deque(maxlen=window_size * 2)
        self.behavior_history: List[Any] = []

        # Detected events
        self.emergence_events: List[EmergenceEvent] = []

        # Statistics for detection
        self.baseline_stats = {}

    def update(
        self,
        fitness: float,
        complexity: float,
        behavior: Any,
        generation: int
    ) -> List[EmergenceEvent]:
        """
        Update detector with new data.

        Returns any newly detected emergence events.
        """
        self.fitness_history.append(fitness)
        self.complexity_history.append(complexity)
        self.behavior_history.append(behavior)

        new_events = []

        # Only detect after enough history
        if len(self.fitness_history) < self.window_size:
            return new_events

        # Detect different types of emergence
        capability_jump = self._detect_capability_jump(generation)
        if capability_jump:
            new_events.append(capability_jump)

        phase_transition = self._detect_phase_transition(generation)
        if phase_transition:
            new_events.append(phase_transition)

        novel_pattern = self._detect_novel_pattern(generation)
        if novel_pattern:
            new_events.append(novel_pattern)

        synergy = self._detect_synergy(generation)
        if synergy:
            new_events.append(synergy)

        # Add to history
        self.emergence_events.extend(new_events)

        return new_events

    def _detect_capability_jump(self, generation: int) -> Optional[EmergenceEvent]:
        """
        Detect sudden discontinuous improvement.

        Looks for:
        - Sharp increase in fitness
        - Statistically significant deviation from trend
        """
        if len(self.fitness_history) < self.window_size:
            return None

        recent = list(self.fitness_history)

        # Split into before and after
        before = recent[:self.window_size]
        after = recent[self.window_size:]

        if not before or not after:
            return None

        # Compare means
        mean_before = sum(before) / len(before)
        mean_after = sum(after) / len(after)

        # Check for significant jump
        std_before = (sum((x - mean_before) ** 2 for x in before) / len(before)) ** 0.5

        if std_before < 0.001:  # Avoid division by zero
            return None

        # Z-score of improvement
        improvement = mean_after - mean_before
        z_score = improvement / (std_before + 0.001)

        # Threshold based on sensitivity
        threshold = 2.0 / (self.sensitivity + 0.1)

        if z_score > threshold:
            magnitude = min(1.0, z_score / 5.0)

            return EmergenceEvent(
                event_type=EmergenceType.CAPABILITY_JUMP,
                timestamp=generation,
                magnitude=magnitude,
                description=f"Fitness jumped from {mean_before:.3f} to {mean_after:.3f}",
                evidence={
                    'mean_before': mean_before,
                    'mean_after': mean_after,
                    'z_score': z_score,
                    'improvement': improvement
                },
                confidence=min(1.0, z_score / threshold / 2.0)
            )

        return None

    def _detect_phase_transition(self, generation: int) -> Optional[EmergenceEvent]:
        """
        Detect system-wide reorganization.

        Looks for:
        - Simultaneous changes in multiple metrics
        - Variance spike (system exploring new regime)
        - Correlation changes
        """
        if len(self.fitness_history) < self.window_size or len(self.complexity_history) < self.window_size:
            return None

        recent_fitness = list(self.fitness_history)
        recent_complexity = list(self.complexity_history)

        # Compute variance in recent window
        recent_window = recent_fitness[-self.window_size // 2:]
        older_window = recent_fitness[-self.window_size:-self.window_size // 2]

        if not recent_window or not older_window:
            return None

        def variance(data):
            if not data:
                return 0.0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)

        var_recent = variance(recent_window)
        var_older = variance(older_window)

        # Phase transitions often show variance spike
        if var_older < 0.001:
            return None

        variance_ratio = var_recent / var_older

        # Also check complexity change
        comp_recent = recent_complexity[-self.window_size // 2:]
        comp_older = recent_complexity[-self.window_size:-self.window_size // 2]

        if comp_recent and comp_older:
            comp_change = (sum(comp_recent) / len(comp_recent)) - (sum(comp_older) / len(comp_older))
        else:
            comp_change = 0.0

        # Phase transition: high variance + complexity change
        threshold = 2.0
        if variance_ratio > threshold and abs(comp_change) > 0.1:
            magnitude = min(1.0, (variance_ratio / threshold) * abs(comp_change))

            return EmergenceEvent(
                event_type=EmergenceType.PHASE_TRANSITION,
                timestamp=generation,
                magnitude=magnitude,
                description=f"System reorganization: variance increased {variance_ratio:.2f}x",
                evidence={
                    'variance_ratio': variance_ratio,
                    'complexity_change': comp_change
                },
                confidence=min(1.0, variance_ratio / threshold / 3.0)
            )

        return None

    def _detect_novel_pattern(self, generation: int) -> Optional[EmergenceEvent]:
        """
        Detect emergence of novel behavioral pattern.

        Looks for:
        - Behavior significantly different from history
        - Sustained over multiple steps
        """
        if len(self.behavior_history) < self.window_size:
            return None

        # Compare recent behavior to historical archive
        recent_behaviors = self.behavior_history[-10:]  # Last 10 behaviors
        historical_behaviors = self.behavior_history[:-10]

        if not historical_behaviors:
            return None

        # Compute novelty
        novelties = []
        for recent in recent_behaviors:
            # Find min distance to historical behaviors
            min_dist = float('inf')
            for hist in historical_behaviors[-50:]:  # Compare to last 50
                dist = self._behavior_distance(recent, hist)
                min_dist = min(min_dist, dist)
            novelties.append(min_dist)

        avg_novelty = sum(novelties) / len(novelties) if novelties else 0.0

        # Threshold for novel pattern
        threshold = 0.5
        if avg_novelty > threshold:
            magnitude = min(1.0, avg_novelty)

            return EmergenceEvent(
                event_type=EmergenceType.NOVEL_PATTERN,
                timestamp=generation,
                magnitude=magnitude,
                description=f"Novel behavior pattern emerged (novelty: {avg_novelty:.3f})",
                evidence={
                    'avg_novelty': avg_novelty,
                    'num_behaviors': len(recent_behaviors)
                },
                confidence=min(1.0, avg_novelty / threshold)
            )

        return None

    def _behavior_distance(self, behavior1: Any, behavior2: Any) -> float:
        """Compute distance between two behaviors."""
        # Generic distance based on type
        if behavior1 == behavior2:
            return 0.0

        if isinstance(behavior1, (int, float)) and isinstance(behavior2, (int, float)):
            return abs(behavior1 - behavior2)

        if isinstance(behavior1, (list, tuple)) and isinstance(behavior2, (list, tuple)):
            if len(behavior1) != len(behavior2):
                return 1.0
            return sum(abs(a - b) for a, b in zip(behavior1, behavior2)) / len(behavior1)

        # Default: different = distance 1
        return 1.0

    def _detect_synergy(self, generation: int) -> Optional[EmergenceEvent]:
        """
        Detect synergistic emergence.

        Whole > sum of parts:
        - Combined fitness exceeds additive expectation
        - Interactions create new capabilities
        """
        # This requires tracking component contributions
        # Simplified version: detect superlinear growth

        if len(self.fitness_history) < self.window_size:
            return None

        recent = list(self.fitness_history)[-self.window_size:]

        if len(recent) < 20:
            return None

        # Fit growth rate
        # If superlinear, might indicate synergy
        first_quarter = recent[:len(recent) // 4]
        last_quarter = recent[-len(recent) // 4:]

        if not first_quarter or not last_quarter:
            return None

        early_growth = sum(last_quarter) / len(last_quarter) - sum(first_quarter) / len(first_quarter)

        # Check if growth is accelerating
        mid_early = recent[len(recent) // 4:len(recent) // 2]
        mid_late = recent[len(recent) // 2:3 * len(recent) // 4]

        if mid_early and mid_late:
            mid_growth = sum(mid_late) / len(mid_late) - sum(mid_early) / len(mid_early)

            if early_growth > 0.01 and mid_growth > early_growth * 1.5:
                # Accelerating growth suggests synergy
                magnitude = min(1.0, mid_growth / (early_growth + 0.001))

                return EmergenceEvent(
                    event_type=EmergenceType.SYNERGY,
                    timestamp=generation,
                    magnitude=magnitude,
                    description="Synergistic effects detected: accelerating growth",
                    evidence={
                        'early_growth': early_growth,
                        'mid_growth': mid_growth,
                        'acceleration': mid_growth / (early_growth + 0.001)
                    },
                    confidence=0.6
                )

        return None

    def get_emergence_summary(self) -> Dict[str, Any]:
        """Get summary of all detected emergence."""
        if not self.emergence_events:
            return {
                'total_events': 0,
                'by_type': {},
                'avg_magnitude': 0.0
            }

        by_type = defaultdict(int)
        for event in self.emergence_events:
            by_type[event.event_type.value] += 1

        magnitudes = [e.magnitude for e in self.emergence_events]

        return {
            'total_events': len(self.emergence_events),
            'by_type': dict(by_type),
            'avg_magnitude': sum(magnitudes) / len(magnitudes),
            'max_magnitude': max(magnitudes),
            'recent_events': self.emergence_events[-5:]
        }


class MultiScaleDetector:
    """
    Detect emergence across multiple timescales.

    Some emergence is immediate, some takes thousands of generations.
    """

    def __init__(self):
        # Detectors at different timescales
        self.detectors = {
            'micro': EmergenceDetector(window_size=10, sensitivity=0.7),   # Immediate
            'meso': EmergenceDetector(window_size=50, sensitivity=0.5),    # Medium-term
            'macro': EmergenceDetector(window_size=200, sensitivity=0.3),  # Long-term
        }

        self.all_events: List[Tuple[str, EmergenceEvent]] = []

    def update(
        self,
        fitness: float,
        complexity: float,
        behavior: Any,
        generation: int
    ) -> Dict[str, List[EmergenceEvent]]:
        """
        Update all detectors.

        Returns events by timescale.
        """
        events_by_scale = {}

        for scale_name, detector in self.detectors.items():
            events = detector.update(fitness, complexity, behavior, generation)
            events_by_scale[scale_name] = events

            # Record all events with scale
            for event in events:
                self.all_events.append((scale_name, event))

        return events_by_scale

    def get_multi_scale_summary(self) -> Dict[str, Any]:
        """Get summary across all scales."""
        summary = {
            'by_scale': {},
            'total_events': len(self.all_events)
        }

        for scale_name, detector in self.detectors.items():
            summary['by_scale'][scale_name] = detector.get_emergence_summary()

        # Cross-scale emergence: same event detected at multiple scales
        event_types_by_gen = defaultdict(set)
        for scale, event in self.all_events:
            event_types_by_gen[event.timestamp].add(event.event_type)

        cross_scale_events = [
            gen for gen, types in event_types_by_gen.items()
            if len(types) > 1
        ]

        summary['cross_scale_events'] = len(cross_scale_events)

        return summary
