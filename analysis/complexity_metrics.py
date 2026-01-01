"""
Complexity Metrics for Evolved Systems

Multiple measures of complexity:
- Lempel-Ziv complexity (compressibility)
- Kolmogorov complexity (approximations)
- Logical depth (computation time)
- Effective complexity (non-random information)
"""

import random
import math
from typing import List, Any, Dict
from collections import defaultdict, Counter


class ComplexityAnalyzer:
    """
    Comprehensive complexity analysis.

    Combines multiple complexity measures to understand
    sophistication of evolved solutions.
    """

    def __init__(self):
        self.lz = LempelZivComplexity()
        self.kc = KolmogorovComplexity()
        self.ld = LogicalDepth()

    def analyze(self, data: Any) -> Dict[str, float]:
        """
        Compute multiple complexity metrics.

        Args:
            data: Object to analyze (convert to sequence)

        Returns:
            Dictionary of complexity scores
        """
        # Convert data to binary sequence for analysis
        sequence = self._to_sequence(data)

        if not sequence:
            return {
                'lempel_ziv': 0.0,
                'kolmogorov_approx': 0.0,
                'logical_depth': 0.0,
                'effective_complexity': 0.0,
                'overall_complexity': 0.0
            }

        lz_complexity = self.lz.compute(sequence)
        kc_complexity = self.kc.approximate(sequence)
        depth = self.ld.compute(sequence)

        # Effective complexity: complexity of regularities (not random noise)
        effective = self._effective_complexity(sequence)

        # Overall score
        overall = (lz_complexity + kc_complexity + depth + effective) / 4

        return {
            'lempel_ziv': lz_complexity,
            'kolmogorov_approx': kc_complexity,
            'logical_depth': depth,
            'effective_complexity': effective,
            'overall_complexity': overall
        }

    def _to_sequence(self, data: Any) -> List[int]:
        """Convert arbitrary data to binary sequence."""
        if isinstance(data, (list, tuple)):
            # Flatten and binarize
            result = []
            for item in data:
                if isinstance(item, bool):
                    result.append(1 if item else 0)
                elif isinstance(item, int):
                    # Use bits
                    result.extend([int(b) for b in bin(abs(item))[2:]])
                elif isinstance(item, float):
                    # Discretize
                    result.append(1 if item > 0.5 else 0)
                elif isinstance(item, (list, tuple)):
                    result.extend(self._to_sequence(item))
            return result

        elif isinstance(data, str):
            # String to ASCII bits
            result = []
            for char in data:
                bits = bin(ord(char))[2:].zfill(8)
                result.extend([int(b) for b in bits])
            return result

        elif isinstance(data, (int, float)):
            return [1 if data > 0 else 0]

        else:
            # Convert to string representation
            return self._to_sequence(str(data))

    def _effective_complexity(self, sequence: List[int]) -> float:
        """
        Effective complexity: information in regularities.

        Complexity of the 'structure', not random noise.
        """
        if not sequence:
            return 0.0

        # Find repeated patterns
        pattern_counts = self._find_patterns(sequence, max_length=5)

        # Entropy of pattern distribution
        total = sum(pattern_counts.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in pattern_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize to 0-1
        max_entropy = math.log2(len(pattern_counts)) if len(pattern_counts) > 1 else 1.0

        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _find_patterns(self, sequence: List[int], max_length: int = 5) -> Dict[tuple, int]:
        """Find all repeated patterns up to max_length."""
        patterns = defaultdict(int)

        for length in range(1, min(max_length + 1, len(sequence) + 1)):
            for i in range(len(sequence) - length + 1):
                pattern = tuple(sequence[i:i + length])
                patterns[pattern] += 1

        # Keep only patterns that repeat
        return {p: c for p, c in patterns.items() if c > 1}


class LempelZivComplexity:
    """
    Lempel-Ziv complexity.

    Measures how compressible a sequence is.
    Higher = less compressible = more complex.
    """

    def compute(self, sequence: List[int]) -> float:
        """
        Compute normalized LZ complexity.

        Returns value 0-1.
        """
        if not sequence:
            return 0.0

        n = len(sequence)
        if n == 0:
            return 0.0

        # LZ76 algorithm
        complexity = 0
        i = 0
        history = set()

        while i < n:
            # Find longest prefix in history
            for length in range(min(n - i, 20), 0, -1):
                substring = tuple(sequence[i:i + length])
                if substring in history or length == 1:
                    history.add(substring)
                    i += length
                    complexity += 1
                    break

        # Normalize by maximum possible complexity
        # Upper bound is approximately n / log2(n)
        max_complexity = n / max(1, math.log2(n))

        return min(1.0, complexity / max_complexity) if max_complexity > 0 else 0.0


class KolmogorovComplexity:
    """
    Kolmogorov complexity approximation.

    True KC is uncomputable, but we can approximate via:
    - Compression ratio
    - Minimal description length
    """

    def approximate(self, sequence: List[int]) -> float:
        """
        Approximate KC via compression.

        Returns normalized complexity 0-1.
        """
        if not sequence:
            return 0.0

        # Simple run-length encoding
        compressed_length = self._compress_rle(sequence)

        # Compression ratio as proxy for KC
        ratio = compressed_length / max(1, len(sequence))

        # Higher ratio = less compressible = more complex
        return min(1.0, ratio)

    def _compress_rle(self, sequence: List[int]) -> int:
        """Run-length encoding."""
        if not sequence:
            return 0

        compressed = []
        current = sequence[0]
        count = 1

        for i in range(1, len(sequence)):
            if sequence[i] == current:
                count += 1
            else:
                compressed.append((current, count))
                current = sequence[i]
                count = 1

        compressed.append((current, count))

        # Estimate size of compressed representation
        # Each run is (symbol, count)
        return len(compressed) * 2


class LogicalDepth:
    """
    Logical depth (Bennett).

    Complexity measured by computational effort needed to generate.
    A random string has low depth (easy to generate randomly).
    A structured string has high depth (took computation to create).
    """

    def compute(self, sequence: List[int]) -> float:
        """
        Approximate logical depth.

        Measures how 'meaningful' the complexity is.

        Returns normalized depth 0-1.
        """
        if not sequence:
            return 0.0

        # Depth approximation: entropy * structure_score
        entropy = self._compute_entropy(sequence)
        structure = self._compute_structure(sequence)

        # High depth = high entropy + high structure
        depth = entropy * structure

        return min(1.0, depth)

    def _compute_entropy(self, sequence: List[int]) -> float:
        """Shannon entropy of sequence."""
        if not sequence:
            return 0.0

        counts = Counter(sequence)
        total = len(sequence)

        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize to 0-1
        max_entropy = math.log2(len(set(sequence))) if len(set(sequence)) > 1 else 1.0

        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _compute_structure(self, sequence: List[int]) -> float:
        """
        Measure of structure (vs randomness).

        High structure = patterns, regularities
        Low structure = random
        """
        if len(sequence) < 4:
            return 0.0

        # Autocorrelation as structure measure
        autocorr = 0.0
        lags_tested = 0

        for lag in range(1, min(10, len(sequence) // 2)):
            corr = 0.0
            count = 0

            for i in range(len(sequence) - lag):
                if sequence[i] == sequence[i + lag]:
                    corr += 1
                count += 1

            if count > 0:
                autocorr += corr / count
                lags_tested += 1

        if lags_tested > 0:
            autocorr /= lags_tested

        return autocorr


class EffectiveComplexity:
    """
    Effective complexity (Gell-Mann, Lloyd).

    Complexity of the 'regularities' in data.
    Random noise doesn't count as complexity.
    """

    def compute(self, sequence: List[int]) -> float:
        """
        Compute effective complexity.

        Returns 0-1 score.
        """
        if not sequence:
            return 0.0

        # Model: find simplest description of regularities
        model_complexity = self._minimal_model_complexity(sequence)

        # Random component
        randomness = self._estimate_randomness(sequence)

        # Effective complexity = model complexity, not randomness
        effective = model_complexity * (1 - randomness)

        return min(1.0, effective)

    def _minimal_model_complexity(self, sequence: List[int]) -> float:
        """Complexity of minimal model explaining sequence."""
        if not sequence:
            return 0.0

        # Try simple models
        models = [
            self._constant_model,
            self._linear_model,
            self._periodic_model,
            self._random_model
        ]

        best_fit = 0.0
        best_complexity = 1.0

        for model_fn in models:
            complexity, fit = model_fn(sequence)
            if fit > best_fit or (fit == best_fit and complexity < best_complexity):
                best_fit = fit
                best_complexity = complexity

        return best_complexity

    def _constant_model(self, sequence: List[int]) -> tuple:
        """Constant model: all same value."""
        if not sequence:
            return 1.0, 0.0

        most_common = Counter(sequence).most_common(1)[0][0]
        fit = sum(1 for x in sequence if x == most_common) / len(sequence)
        complexity = 0.1  # Very simple model

        return complexity, fit

    def _linear_model(self, sequence: List[int]) -> tuple:
        """Linear trend model."""
        if len(sequence) < 2:
            return 1.0, 0.0

        # Simple linear regression
        n = len(sequence)
        x = list(range(n))
        y = sequence

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

        if denominator == 0:
            return 1.0, 0.0

        slope = numerator / denominator
        intercept = mean_y - slope * mean_x

        # Compute fit
        predictions = [slope * i + intercept for i in range(n)]
        errors = [abs(y[i] - predictions[i]) for i in range(n)]
        fit = 1.0 - (sum(errors) / (n * max(abs(max(y) - min(y)), 1)))

        complexity = 0.3  # Moderate complexity

        return complexity, max(0.0, fit)

    def _periodic_model(self, sequence: List[int]) -> tuple:
        """Periodic model."""
        if len(sequence) < 4:
            return 1.0, 0.0

        best_period_fit = 0.0

        # Try periods 2-10
        for period in range(2, min(11, len(sequence) // 2)):
            matches = 0
            comparisons = 0

            for i in range(len(sequence) - period):
                if sequence[i] == sequence[i + period]:
                    matches += 1
                comparisons += 1

            if comparisons > 0:
                fit = matches / comparisons
                best_period_fit = max(best_period_fit, fit)

        complexity = 0.5  # Moderate complexity

        return complexity, best_period_fit

    def _random_model(self, sequence: List[int]) -> tuple:
        """Random model: no pattern."""
        complexity = 1.0  # Maximum complexity (no compression)
        fit = 0.0  # Doesn't predict anything

        return complexity, fit

    def _estimate_randomness(self, sequence: List[int]) -> float:
        """Estimate how random sequence is."""
        if not sequence:
            return 1.0

        # Use entropy as randomness proxy
        counts = Counter(sequence)
        total = len(sequence)

        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Normalize
        max_entropy = math.log2(len(set(sequence))) if len(set(sequence)) > 1 else 1.0

        return entropy / max_entropy if max_entropy > 0 else 0.0
