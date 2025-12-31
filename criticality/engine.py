"""
AEGIS-2 Criticality Engine: Edge of Chaos Dynamics

Key insight from complex systems: Emergence happens at the "edge of chaos" -
the critical boundary between order and disorder where:
- Too ordered = frozen, no novelty
- Too chaotic = random, no structure
- Critical = maximum computational capacity, long-range correlations

This module implements:
- Order/chaos parameter tracking
- Self-organized criticality (SOC)
- Power law detection
- Avalanche dynamics
- Homeostatic regulation toward criticality
"""

import random
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from collections import deque
import statistics


@dataclass
class CriticalityMetrics:
    """Metrics for measuring proximity to critical point."""
    
    # Order parameter (0 = chaotic, 1 = frozen)
    order_parameter: float = 0.5
    
    # Correlation length (how far effects propagate)
    correlation_length: float = 1.0
    
    # Susceptibility (sensitivity to perturbation)
    susceptibility: float = 1.0
    
    # Branching ratio (avg number of events triggered by one event)
    branching_ratio: float = 1.0
    
    # Power law exponent (if present)
    power_law_exponent: float = 0.0
    power_law_fit: float = 0.0
    
    # Lyapunov exponent (chaos measure)
    lyapunov: float = 0.0
    
    # Entropy
    entropy: float = 0.0
    
    # Distance from critical point
    criticality_distance: float = 0.0
    
    def is_critical(self, tolerance: float = 0.1) -> bool:
        """Check if system is near critical point."""
        # At criticality: branching ratio ≈ 1, correlation length high
        br_critical = abs(self.branching_ratio - 1.0) < tolerance
        high_correlation = self.correlation_length > 2.0
        
        return br_critical and high_correlation
    
    def to_dict(self) -> Dict:
        return {
            'order_parameter': self.order_parameter,
            'correlation_length': self.correlation_length,
            'susceptibility': self.susceptibility,
            'branching_ratio': self.branching_ratio,
            'power_law_exponent': self.power_law_exponent,
            'lyapunov': self.lyapunov,
            'entropy': self.entropy,
            'criticality_distance': self.criticality_distance,
            'is_critical': self.is_critical()
        }


@dataclass
class Avalanche:
    """An avalanche event - cascade of activity."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(random.random()).encode()).hexdigest()[:10])
    
    # Size (number of events in cascade)
    size: int = 0
    
    # Duration (time steps)
    duration: int = 0
    
    # Events in the avalanche
    events: List[Dict] = field(default_factory=list)
    
    # Start/end times
    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    end_time: Optional[float] = None
    
    # Peak activity
    peak_activity: float = 0.0
    
    # Branching factor for this avalanche
    branching: float = 1.0
    
    def add_event(self, event: Dict):
        """Add an event to the avalanche."""
        self.events.append(event)
        self.size += 1
        self.peak_activity = max(self.peak_activity, event.get('activity', 1.0))
    
    def close(self):
        """Close the avalanche."""
        self.end_time = datetime.now().timestamp()
        self.duration = len(self.events)
        
        # Compute branching
        if self.size > 1:
            # Average number of children per event
            children_counts = [e.get('children', 0) for e in self.events]
            self.branching = sum(children_counts) / len(children_counts) if children_counts else 1.0


class SandpileModel:
    """
    Abelian sandpile model for self-organized criticality.
    
    This is the canonical model for SOC - the system naturally
    evolves toward criticality without parameter tuning.
    """
    
    def __init__(self, size: int = 50):
        self.size = size
        self.threshold = 4  # Topple when >= threshold
        
        # Grid of sand heights
        self.grid: List[List[int]] = [[0] * size for _ in range(size)]
        
        # Total grains
        self.total_grains: int = 0
        
        # Avalanche history
        self.avalanche_sizes: List[int] = []
        self.current_avalanche: Optional[Avalanche] = None
        
        # Statistics
        self.total_drops: int = 0
        self.total_topples: int = 0
    
    def drop_grain(self, x: Optional[int] = None, y: Optional[int] = None) -> Avalanche:
        """Drop a grain and trigger avalanche if needed."""
        if x is None:
            x = random.randint(0, self.size - 1)
        if y is None:
            y = random.randint(0, self.size - 1)
        
        self.grid[y][x] += 1
        self.total_grains += 1
        self.total_drops += 1
        
        # Check for avalanche
        avalanche = Avalanche()
        self._topple(x, y, avalanche)
        avalanche.close()
        
        if avalanche.size > 0:
            self.avalanche_sizes.append(avalanche.size)
        
        return avalanche
    
    def _topple(self, x: int, y: int, avalanche: Avalanche):
        """Recursive toppling."""
        if self.grid[y][x] < self.threshold:
            return
        
        self.grid[y][x] -= 4
        self.total_topples += 1
        self.total_grains -= 4  # Some fall off edges
        
        children = 0
        
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        for nx, ny in neighbors:
            if 0 <= nx < self.size and 0 <= ny < self.size:
                self.grid[ny][nx] += 1
                self.total_grains += 1
                children += 1
                
                if self.grid[ny][nx] >= self.threshold:
                    avalanche.add_event({'x': nx, 'y': ny, 'children': 0})
                    self._topple(nx, ny, avalanche)
        
        avalanche.add_event({'x': x, 'y': y, 'children': children})
    
    def get_power_law_exponent(self) -> Tuple[float, float]:
        """Fit power law to avalanche size distribution."""
        if len(self.avalanche_sizes) < 20:
            return 0.0, 0.0
        
        # Bin the sizes
        sizes = [s for s in self.avalanche_sizes if s > 0]
        if not sizes:
            return 0.0, 0.0
        
        # Log-log fit
        log_sizes = [math.log(s) for s in sizes if s > 0]
        
        if len(log_sizes) < 10:
            return 0.0, 0.0
        
        # Simple linear regression on log-log
        n = len(log_sizes)
        
        # Create rank (proxy for probability)
        ranks = list(range(1, n + 1))
        log_ranks = [math.log(r) for r in ranks]
        
        # Sort by size descending
        sorted_pairs = sorted(zip(log_sizes, log_ranks), reverse=True)
        log_sizes_sorted = [p[0] for p in sorted_pairs]
        log_ranks_sorted = [math.log(i + 1) for i in range(len(sorted_pairs))]
        
        # Linear regression
        mean_x = sum(log_sizes_sorted) / n
        mean_y = sum(log_ranks_sorted) / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_sizes_sorted, log_ranks_sorted))
        denominator = sum((x - mean_x) ** 2 for x in log_sizes_sorted)
        
        if denominator == 0:
            return 0.0, 0.0
        
        slope = numerator / denominator
        
        # R-squared
        ss_res = sum((y - (slope * x + (mean_y - slope * mean_x))) ** 2 
                     for x, y in zip(log_sizes_sorted, log_ranks_sorted))
        ss_tot = sum((y - mean_y) ** 2 for y in log_ranks_sorted)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        return -slope, r_squared  # Exponent is negative of slope


class CriticalityEngine:
    """
    Engine for maintaining system at edge of chaos.
    
    Core functions:
    1. Measure current criticality state
    2. Detect phase transitions
    3. Apply homeostatic regulation toward criticality
    4. Track avalanches and power laws
    """
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        
        # Current metrics
        self.metrics = CriticalityMetrics()
        
        # History
        self.activity_history: deque = deque(maxlen=window_size)
        self.order_history: deque = deque(maxlen=window_size)
        self.avalanche_history: List[Avalanche] = []
        
        # Sandpile for SOC dynamics
        self.sandpile = SandpileModel(size=30)
        
        # Control parameters
        self.temperature: float = 1.0  # Noise/randomness level
        self.coupling: float = 0.5     # Interaction strength
        
        # Homeostatic targets
        self.target_order: float = 0.5  # Edge of chaos
        self.target_branching: float = 1.0  # Critical branching
        
        # Regulation strength
        self.regulation_strength: float = 0.1
        
        # State
        self.total_events: int = 0
        self.total_avalanches: int = 0
    
    def record_activity(self, activity: float, event_data: Optional[Dict] = None):
        """Record an activity event."""
        self.activity_history.append(activity)
        self.total_events += 1
        
        # Update order parameter
        if len(self.activity_history) >= 2:
            recent = list(self.activity_history)[-10:]
            variance = statistics.variance(recent) if len(recent) > 1 else 0
            # High variance = chaos, low variance = order
            self.metrics.order_parameter = 1.0 / (1.0 + variance)
        
        self.order_history.append(self.metrics.order_parameter)
        
        # Drop grain in sandpile
        avalanche = self.sandpile.drop_grain()
        if avalanche.size > 0:
            self.avalanche_history.append(avalanche)
            self.total_avalanches += 1
        
        # Update metrics
        self._update_metrics()
    
    def record_cascade(self, trigger: Dict, propagation: List[Dict]):
        """Record a cascade/avalanche of events."""
        avalanche = Avalanche()
        avalanche.add_event(trigger)
        
        for event in propagation:
            avalanche.add_event(event)
        
        avalanche.close()
        self.avalanche_history.append(avalanche)
        self.total_avalanches += 1
        
        # Update branching ratio
        if avalanche.size > 0:
            alpha = 0.1
            self.metrics.branching_ratio = (
                (1 - alpha) * self.metrics.branching_ratio +
                alpha * avalanche.branching
            )
    
    def _update_metrics(self):
        """Update criticality metrics."""
        # Correlation length from activity history
        if len(self.activity_history) >= 20:
            self.metrics.correlation_length = self._compute_correlation_length()
        
        # Susceptibility
        if len(self.order_history) >= 10:
            order_values = list(self.order_history)[-20:]
            self.metrics.susceptibility = statistics.variance(order_values) * 10 if len(order_values) > 1 else 1.0
        
        # Power law from avalanche distribution
        exp, fit = self.sandpile.get_power_law_exponent()
        self.metrics.power_law_exponent = exp
        self.metrics.power_law_fit = fit
        
        # Lyapunov exponent estimate
        self.metrics.lyapunov = self._estimate_lyapunov()
        
        # Entropy
        self.metrics.entropy = self._compute_entropy()
        
        # Distance from criticality
        self._compute_criticality_distance()
    
    def _compute_correlation_length(self) -> float:
        """Compute correlation length from activity time series."""
        data = list(self.activity_history)
        n = len(data)
        
        if n < 10:
            return 1.0
        
        mean = sum(data) / n
        
        # Autocorrelation
        max_lag = min(20, n // 2)
        correlations = []
        
        var = sum((x - mean) ** 2 for x in data) / n
        if var == 0:
            return 1.0
        
        for lag in range(1, max_lag):
            cov = sum((data[i] - mean) * (data[i + lag] - mean) for i in range(n - lag)) / (n - lag)
            correlations.append(cov / var)
        
        # Find where correlation drops below 1/e
        threshold = 1.0 / math.e
        for i, corr in enumerate(correlations):
            if corr < threshold:
                return float(i + 1)
        
        return float(max_lag)
    
    def _estimate_lyapunov(self) -> float:
        """Estimate Lyapunov exponent (chaos measure)."""
        data = list(self.activity_history)
        if len(data) < 20:
            return 0.0
        
        # Simplified: look at divergence of nearby points
        divergences = []
        
        for i in range(len(data) - 2):
            for j in range(i + 1, min(i + 5, len(data) - 1)):
                d0 = abs(data[i] - data[j])
                d1 = abs(data[i + 1] - data[j + 1])
                
                if d0 > 0.01 and d1 > 0.01:
                    divergences.append(math.log(d1 / d0))
        
        if divergences:
            return sum(divergences) / len(divergences)
        return 0.0
    
    def _compute_entropy(self) -> float:
        """Compute entropy of activity distribution."""
        data = list(self.activity_history)
        if len(data) < 10:
            return 0.0
        
        # Bin the data
        n_bins = 10
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return 0.0
        
        bin_width = (max_val - min_val) / n_bins
        bins = [0] * n_bins
        
        for x in data:
            bin_idx = min(n_bins - 1, int((x - min_val) / bin_width))
            bins[bin_idx] += 1
        
        # Compute entropy
        total = sum(bins)
        entropy = 0.0
        for count in bins:
            if count > 0:
                p = count / total
                entropy -= p * math.log(p)
        
        return entropy
    
    def _compute_criticality_distance(self):
        """Compute distance from critical point."""
        # Critical point characterized by:
        # - Branching ratio = 1
        # - Order parameter = 0.5
        # - High correlation length
        # - Power law fit
        
        br_dist = abs(self.metrics.branching_ratio - 1.0)
        order_dist = abs(self.metrics.order_parameter - 0.5) * 2
        
        # Normalize correlation length contribution
        corr_score = 1.0 - (1.0 / (1.0 + self.metrics.correlation_length / 5.0))
        
        power_law_score = self.metrics.power_law_fit if self.metrics.power_law_exponent > 0 else 0.0
        
        # Combined distance (lower = closer to criticality)
        self.metrics.criticality_distance = (
            0.3 * br_dist +
            0.3 * order_dist +
            0.2 * (1 - corr_score) +
            0.2 * (1 - power_law_score)
        )
    
    def regulate(self) -> Dict[str, float]:
        """
        Apply homeostatic regulation toward criticality.
        Returns adjustment recommendations.
        """
        adjustments = {}
        
        # If too ordered (frozen), increase temperature
        if self.metrics.order_parameter > self.target_order + 0.1:
            adjustment = self.regulation_strength * (self.metrics.order_parameter - self.target_order)
            adjustments['temperature'] = adjustment
            self.temperature += adjustment
        
        # If too chaotic, decrease temperature
        elif self.metrics.order_parameter < self.target_order - 0.1:
            adjustment = self.regulation_strength * (self.target_order - self.metrics.order_parameter)
            adjustments['temperature'] = -adjustment
            self.temperature -= adjustment
        
        # Regulate coupling based on branching ratio
        if self.metrics.branching_ratio > self.target_branching + 0.1:
            adjustment = self.regulation_strength * (self.metrics.branching_ratio - self.target_branching)
            adjustments['coupling'] = -adjustment
            self.coupling -= adjustment * 0.5
        elif self.metrics.branching_ratio < self.target_branching - 0.1:
            adjustment = self.regulation_strength * (self.target_branching - self.metrics.branching_ratio)
            adjustments['coupling'] = adjustment
            self.coupling += adjustment * 0.5
        
        # Clamp values
        self.temperature = max(0.1, min(2.0, self.temperature))
        self.coupling = max(0.1, min(1.0, self.coupling))
        
        return adjustments
    
    def get_noise(self) -> float:
        """Get noise value based on current temperature."""
        return random.gauss(0, self.temperature * 0.1)
    
    def should_propagate(self, strength: float) -> bool:
        """Determine if an event should propagate based on coupling and criticality."""
        # Higher coupling = more propagation
        # Near criticality = critical branching
        
        threshold = 1.0 - self.coupling
        
        # Adjust threshold based on current branching ratio
        if self.metrics.branching_ratio > 1.1:
            threshold += 0.1  # Reduce propagation
        elif self.metrics.branching_ratio < 0.9:
            threshold -= 0.1  # Increase propagation
        
        return (strength + self.get_noise()) > threshold
    
    def get_stats(self) -> Dict:
        return {
            'metrics': self.metrics.to_dict(),
            'temperature': self.temperature,
            'coupling': self.coupling,
            'total_events': self.total_events,
            'total_avalanches': self.total_avalanches,
            'sandpile_grains': self.sandpile.total_grains,
            'is_critical': self.metrics.is_critical()
        }
    
    def to_dict(self) -> Dict:
        return {
            'metrics': self.metrics.to_dict(),
            'temperature': self.temperature,
            'coupling': self.coupling,
            'target_order': self.target_order,
            'target_branching': self.target_branching,
            'total_events': self.total_events,
            'total_avalanches': self.total_avalanches
        }
