"""
Emergence Analysis and Detection Tools

Tools for identifying, characterizing, and analyzing emergent phenomena:
- Emergence detectors for different types of emergence
- Statistical tests for phase transitions
- Complexity metrics and tracking
- Novelty quantification beyond simple distance metrics
"""

from analysis.emergence_detector import (
    EmergenceDetector,
    EmergenceType,
    EmergenceEvent,
    MultiScaleDetector
)

from analysis.complexity_metrics import (
    ComplexityAnalyzer,
    LempelZivComplexity,
    KolmogorovComplexity,
    LogicalDepth
)

from analysis.phase_transitions import (
    PhaseTransitionDetector,
    CriticalityAnalyzer,
    BifurcationDetector
)

__all__ = [
    'EmergenceDetector',
    'EmergenceType',
    'EmergenceEvent',
    'MultiScaleDetector',
    'ComplexityAnalyzer',
    'LempelZivComplexity',
    'KolmogorovComplexity',
    'LogicalDepth',
    'PhaseTransitionDetector',
    'CriticalityAnalyzer',
    'BifurcationDetector',
]
