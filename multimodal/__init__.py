"""
AEGIS-2 Multi-Modal I/O

Support for diverse input/output modalities beyond Dict[str, float]:
- Images
- Text/Language
- Audio
- Time series
- Structured data (graphs, trees)
"""

from .modalities import (
    Modality, ModalityType,
    ImageModality, TextModality, AudioModality,
    TimeSeriesModality, GraphModality, MultiModalInput,
    ModalityEncoder, ModalityDecoder
)

__all__ = [
    'Modality', 'ModalityType',
    'ImageModality', 'TextModality', 'AudioModality',
    'TimeSeriesModality', 'GraphModality', 'MultiModalInput',
    'ModalityEncoder', 'ModalityDecoder'
]
