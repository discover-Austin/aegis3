"""
Multi-Modal Input/Output for AEGIS-2

Handle diverse data types beyond simple numeric vectors:
- Images (2D/3D arrays)
- Text (sequences of tokens)
- Audio (waveforms, spectrograms)
- Time series (temporal sequences)
- Graphs (nodes, edges, attributes)
"""

import random
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod


class ModalityType(Enum):
    """Types of modalities."""
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    TIME_SERIES = "time_series"
    GRAPH = "graph"
    STRUCTURED = "structured"
    MULTIMODAL = "multimodal"


@dataclass
class Modality(ABC):
    """Abstract base class for modalities."""
    modality_type: ModalityType
    metadata: Dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def to_vector(self) -> List[float]:
        """Convert to flat vector representation."""
        pass

    @abstractmethod
    def from_vector(self, vector: List[float]):
        """Reconstruct from vector representation."""
        pass

    @abstractmethod
    def get_shape(self) -> Tuple[int, ...]:
        """Get dimensionality."""
        pass


@dataclass
class ImageModality(Modality):
    """Image modality (2D or 3D arrays)."""
    width: int = 32
    height: int = 32
    channels: int = 3  # RGB
    pixels: List[List[List[float]]] = field(default_factory=list)

    def __post_init__(self):
        if not self.pixels:
            # Initialize with zeros
            self.pixels = [
                [[0.0 for _ in range(self.channels)] for _ in range(self.width)]
                for _ in range(self.height)
            ]
        self.modality_type = ModalityType.IMAGE

    def to_vector(self) -> List[float]:
        """Flatten image to vector."""
        vector = []
        for row in self.pixels:
            for pixel in row:
                vector.extend(pixel)
        return vector

    def from_vector(self, vector: List[float]):
        """Reshape vector to image."""
        expected_size = self.height * self.width * self.channels
        if len(vector) < expected_size:
            vector = vector + [0.0] * (expected_size - len(vector))

        idx = 0
        for i in range(self.height):
            for j in range(self.width):
                for c in range(self.channels):
                    if idx < len(vector):
                        self.pixels[i][j][c] = vector[idx]
                        idx += 1

    def get_shape(self) -> Tuple[int, ...]:
        """Get image shape."""
        return (self.height, self.width, self.channels)

    def get_pixel(self, x: int, y: int) -> List[float]:
        """Get pixel at coordinates."""
        x = x % self.width
        y = y % self.height
        return self.pixels[y][x]

    def set_pixel(self, x: int, y: int, value: List[float]):
        """Set pixel at coordinates."""
        x = x % self.width
        y = y % self.height
        self.pixels[y][x] = value[:self.channels]

    def apply_filter(self, filter_type: str) -> 'ImageModality':
        """Apply simple image filter."""
        result = ImageModality(self.width, self.height, self.channels)

        if filter_type == "blur":
            # Simple box blur
            for i in range(self.height):
                for j in range(self.width):
                    avg = [0.0] * self.channels
                    count = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            ni, nj = (i + di) % self.height, (j + dj) % self.width
                            for c in range(self.channels):
                                avg[c] += self.pixels[ni][nj][c]
                            count += 1
                    result.pixels[i][j] = [a / count for a in avg]

        elif filter_type == "edge":
            # Simple edge detection (Sobel-like)
            for i in range(self.height):
                for j in range(self.width):
                    gx = [0.0] * self.channels
                    gy = [0.0] * self.channels
                    for c in range(self.channels):
                        # Horizontal gradient
                        gx[c] = (
                            self.pixels[(i-1) % self.height][(j+1) % self.width][c] +
                            2 * self.pixels[i][(j+1) % self.width][c] +
                            self.pixels[(i+1) % self.height][(j+1) % self.width][c] -
                            self.pixels[(i-1) % self.height][(j-1) % self.width][c] -
                            2 * self.pixels[i][(j-1) % self.width][c] -
                            self.pixels[(i+1) % self.height][(j-1) % self.width][c]
                        )
                        # Vertical gradient
                        gy[c] = (
                            self.pixels[(i+1) % self.height][(j-1) % self.width][c] +
                            2 * self.pixels[(i+1) % self.height][j][c] +
                            self.pixels[(i+1) % self.height][(j+1) % self.width][c] -
                            self.pixels[(i-1) % self.height][(j-1) % self.width][c] -
                            2 * self.pixels[(i-1) % self.height][j][c] -
                            self.pixels[(i-1) % self.height][(j+1) % self.width][c]
                        )
                    result.pixels[i][j] = [math.sqrt(gx[c]**2 + gy[c]**2) for c in range(self.channels)]

        return result


@dataclass
class TextModality(Modality):
    """Text modality (token sequences)."""
    tokens: List[str] = field(default_factory=list)
    vocab_size: int = 256  # ASCII-like
    max_length: int = 128

    def __post_init__(self):
        self.modality_type = ModalityType.TEXT

    def to_vector(self) -> List[float]:
        """Convert tokens to one-hot encoding."""
        vector = []
        for token in self.tokens[:self.max_length]:
            # Simple hash-based encoding
            token_id = hash(token) % self.vocab_size
            one_hot = [0.0] * self.vocab_size
            one_hot[token_id] = 1.0
            vector.extend(one_hot)

        # Pad to max length
        while len(vector) < self.max_length * self.vocab_size:
            vector.extend([0.0] * self.vocab_size)

        return vector

    def from_vector(self, vector: List[float]):
        """Reconstruct tokens from vector (approximate)."""
        self.tokens = []
        for i in range(0, len(vector), self.vocab_size):
            chunk = vector[i:i + self.vocab_size]
            if sum(chunk) > 0:
                token_id = chunk.index(max(chunk))
                self.tokens.append(f"token_{token_id}")

    def get_shape(self) -> Tuple[int, ...]:
        """Get text shape."""
        return (self.max_length, self.vocab_size)

    def get_text(self) -> str:
        """Get text as string."""
        return " ".join(self.tokens)

    def set_text(self, text: str):
        """Set text from string."""
        self.tokens = text.split()[:self.max_length]


@dataclass
class AudioModality(Modality):
    """Audio modality (waveforms)."""
    sample_rate: int = 16000
    samples: List[float] = field(default_factory=list)
    duration: float = 1.0  # seconds

    def __post_init__(self):
        if not self.samples:
            # Initialize with silence
            num_samples = int(self.sample_rate * self.duration)
            self.samples = [0.0] * num_samples
        self.modality_type = ModalityType.AUDIO

    def to_vector(self) -> List[float]:
        """Audio is already a vector."""
        return self.samples.copy()

    def from_vector(self, vector: List[float]):
        """Set samples from vector."""
        self.samples = vector.copy()

    def get_shape(self) -> Tuple[int, ...]:
        """Get audio shape."""
        return (len(self.samples),)

    def generate_tone(self, frequency: float, amplitude: float = 0.5):
        """Generate a pure tone."""
        num_samples = int(self.sample_rate * self.duration)
        self.samples = [
            amplitude * math.sin(2 * math.pi * frequency * t / self.sample_rate)
            for t in range(num_samples)
        ]

    def get_spectrogram(self, window_size: int = 256) -> List[List[float]]:
        """Compute simple spectrogram (simplified FFT)."""
        # This is a placeholder - real FFT would be more complex
        spectrogram = []
        for i in range(0, len(self.samples) - window_size, window_size // 2):
            window = self.samples[i:i + window_size]
            # Simplified frequency content
            spectrum = [
                sum(window[j] * math.cos(2 * math.pi * k * j / window_size)
                    for j in range(len(window)))
                for k in range(window_size // 2)
            ]
            spectrogram.append(spectrum)
        return spectrogram


@dataclass
class TimeSeriesModality(Modality):
    """Time series modality."""
    series: List[List[float]] = field(default_factory=list)  # [time_steps, features]
    num_features: int = 1
    num_timesteps: int = 100

    def __post_init__(self):
        if not self.series:
            self.series = [[0.0] * self.num_features for _ in range(self.num_timesteps)]
        self.modality_type = ModalityType.TIME_SERIES

    def to_vector(self) -> List[float]:
        """Flatten time series."""
        vector = []
        for timestep in self.series:
            vector.extend(timestep)
        return vector

    def from_vector(self, vector: List[float]):
        """Reshape to time series."""
        self.series = []
        for i in range(0, len(vector), self.num_features):
            self.series.append(vector[i:i + self.num_features])

    def get_shape(self) -> Tuple[int, ...]:
        """Get time series shape."""
        return (self.num_timesteps, self.num_features)

    def get_statistics(self) -> Dict[str, List[float]]:
        """Compute basic statistics per feature."""
        if not self.series:
            return {}

        stats = {}
        for feat in range(self.num_features):
            values = [ts[feat] for ts in self.series if feat < len(ts)]
            if values:
                stats[f"feature_{feat}"] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'std': math.sqrt(sum((v - sum(values) / len(values)) ** 2 for v in values) / len(values))
                }
        return stats


@dataclass
class GraphModality(Modality):
    """Graph modality (nodes and edges)."""
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    node_features: Dict[str, List[float]] = field(default_factory=dict)
    edge_features: Dict[Tuple[str, str], List[float]] = field(default_factory=dict)

    def __post_init__(self):
        self.modality_type = ModalityType.GRAPH

    def to_vector(self) -> List[float]:
        """Convert graph to vector (adjacency + features)."""
        # Create adjacency matrix
        n = len(self.nodes)
        adj_matrix = [[0.0] * n for _ in range(n)]

        node_to_idx = {node: i for i, node in enumerate(self.nodes)}

        for src, dst in self.edges:
            if src in node_to_idx and dst in node_to_idx:
                adj_matrix[node_to_idx[src]][node_to_idx[dst]] = 1.0

        # Flatten
        vector = []
        for row in adj_matrix:
            vector.extend(row)

        # Add node features
        for node in self.nodes:
            if node in self.node_features:
                vector.extend(self.node_features[node])
            else:
                vector.extend([0.0] * 10)  # Default feature size

        return vector

    def from_vector(self, vector: List[float]):
        """Reconstruct graph from vector (approximate)."""
        # This is simplified - real reconstruction is complex
        pass

    def get_shape(self) -> Tuple[int, ...]:
        """Get graph shape."""
        return (len(self.nodes), len(self.edges))

    def add_node(self, node: str, features: Optional[List[float]] = None):
        """Add node to graph."""
        if node not in self.nodes:
            self.nodes.append(node)
            if features:
                self.node_features[node] = features

    def add_edge(self, src: str, dst: str, features: Optional[List[float]] = None):
        """Add edge to graph."""
        if (src, dst) not in self.edges:
            self.edges.append((src, dst))
            if features:
                self.edge_features[(src, dst)] = features

    def get_neighbors(self, node: str) -> List[str]:
        """Get neighbors of node."""
        return [dst for src, dst in self.edges if src == node]

    def get_degree(self, node: str) -> int:
        """Get degree of node."""
        in_degree = sum(1 for _, dst in self.edges if dst == node)
        out_degree = sum(1 for src, _ in self.edges if src == node)
        return in_degree + out_degree


@dataclass
class MultiModalInput:
    """
    Container for multi-modal inputs.

    Allows agents to process heterogeneous data simultaneously.
    """
    modalities: Dict[str, Modality] = field(default_factory=dict)

    def add_modality(self, name: str, modality: Modality):
        """Add a modality."""
        self.modalities[name] = modality

    def get_modality(self, name: str) -> Optional[Modality]:
        """Get modality by name."""
        return self.modalities.get(name)

    def to_vector(self) -> List[float]:
        """Convert all modalities to single vector."""
        vector = []
        for name, modality in sorted(self.modalities.items()):
            vector.extend(modality.to_vector())
        return vector

    def get_modality_types(self) -> Dict[str, ModalityType]:
        """Get types of all modalities."""
        return {name: mod.modality_type for name, mod in self.modalities.items()}

    def get_total_dimensions(self) -> int:
        """Get total dimensionality."""
        return len(self.to_vector())


class ModalityEncoder:
    """
    Encode modalities to unified representation.

    Provides compression and normalization.
    """

    def __init__(self, target_dim: int = 128):
        self.target_dim = target_dim

    def encode(self, modality: Modality) -> List[float]:
        """Encode modality to fixed-size vector."""
        vector = modality.to_vector()

        # Simple compression via sampling/averaging
        if len(vector) > self.target_dim:
            # Downsample
            step = len(vector) / self.target_dim
            encoded = []
            for i in range(self.target_dim):
                start = int(i * step)
                end = int((i + 1) * step)
                encoded.append(sum(vector[start:end]) / max(end - start, 1))
            return encoded
        else:
            # Pad
            return vector + [0.0] * (self.target_dim - len(vector))

    def encode_multi(self, multi_modal: MultiModalInput) -> List[float]:
        """Encode multi-modal input."""
        encoded = []
        for name, modality in sorted(multi_modal.modalities.items()):
            encoded.extend(self.encode(modality))
        return encoded


class ModalityDecoder:
    """
    Decode unified representation back to modalities.

    Provides decompression and denormalization.
    """

    def __init__(self):
        pass

    def decode(self, vector: List[float], modality_type: ModalityType, **kwargs) -> Modality:
        """Decode vector to modality."""
        if modality_type == ModalityType.IMAGE:
            modality = ImageModality(
                width=kwargs.get('width', 32),
                height=kwargs.get('height', 32),
                channels=kwargs.get('channels', 3)
            )
            modality.from_vector(vector)
            return modality

        elif modality_type == ModalityType.TEXT:
            modality = TextModality(
                vocab_size=kwargs.get('vocab_size', 256),
                max_length=kwargs.get('max_length', 128)
            )
            modality.from_vector(vector)
            return modality

        elif modality_type == ModalityType.AUDIO:
            modality = AudioModality(
                sample_rate=kwargs.get('sample_rate', 16000),
                duration=kwargs.get('duration', 1.0)
            )
            modality.from_vector(vector)
            return modality

        elif modality_type == ModalityType.TIME_SERIES:
            modality = TimeSeriesModality(
                num_features=kwargs.get('num_features', 1),
                num_timesteps=kwargs.get('num_timesteps', 100)
            )
            modality.from_vector(vector)
            return modality

        elif modality_type == ModalityType.GRAPH:
            modality = GraphModality()
            modality.from_vector(vector)
            return modality

        return None
