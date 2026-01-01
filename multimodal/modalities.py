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

    def compute_histogram(self, bins: int = 256) -> Dict[str, List[int]]:
        """
        Compute color histogram for each channel.

        Returns a dictionary with histogram for each channel.
        """
        histograms = {f'channel_{c}': [0] * bins for c in range(self.channels)}

        for i in range(self.height):
            for j in range(self.width):
                for c in range(self.channels):
                    # Normalize pixel value to [0, bins-1]
                    value = self.pixels[i][j][c]
                    # Clamp value to [0, 1] range then scale to bins
                    value = max(0.0, min(1.0, value))
                    bin_idx = int(value * (bins - 1))
                    histograms[f'channel_{c}'][bin_idx] += 1

        return histograms

    def compute_moments(self) -> Dict[str, Dict[str, float]]:
        """
        Compute statistical moments for each channel.

        Returns mean, variance, skewness, and kurtosis for each channel.
        """
        moments = {}

        for c in range(self.channels):
            # Collect all values for this channel
            values = []
            for i in range(self.height):
                for j in range(self.width):
                    values.append(self.pixels[i][j][c])

            n = len(values)
            if n == 0:
                continue

            # Mean (first moment)
            mean = sum(values) / n

            # Variance (second central moment)
            variance = sum((v - mean) ** 2 for v in values) / n
            std_dev = math.sqrt(variance) if variance > 0 else 0.0

            # Skewness (third standardized moment)
            if std_dev > 0:
                skewness = sum((v - mean) ** 3 for v in values) / (n * std_dev ** 3)
            else:
                skewness = 0.0

            # Kurtosis (fourth standardized moment)
            if std_dev > 0:
                kurtosis = sum((v - mean) ** 4 for v in values) / (n * std_dev ** 4) - 3.0
            else:
                kurtosis = 0.0

            moments[f'channel_{c}'] = {
                'mean': mean,
                'variance': variance,
                'std_dev': std_dev,
                'skewness': skewness,
                'kurtosis': kurtosis
            }

        return moments

    def extract_texture_features(self) -> Dict[str, float]:
        """
        Extract texture features using Gray-Level Co-occurrence Matrix (GLCO) approach.

        Computes energy, contrast, homogeneity, and entropy.
        """
        # Convert to grayscale first
        grayscale = [[0.0] * self.width for _ in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                # Simple average across channels
                grayscale[i][j] = sum(self.pixels[i][j]) / self.channels

        # Quantize to reduce computational complexity
        levels = 8
        quantized = [[0] * self.width for _ in range(self.height)]
        for i in range(self.height):
            for j in range(self.width):
                quantized[i][j] = int(grayscale[i][j] * (levels - 1))

        # Build co-occurrence matrix (horizontal adjacency)
        glcm = [[0] * levels for _ in range(levels)]
        for i in range(self.height):
            for j in range(self.width - 1):
                current = quantized[i][j]
                next_pixel = quantized[i][j + 1]
                glcm[current][next_pixel] += 1

        # Normalize GLCM
        total = sum(sum(row) for row in glcm)
        if total > 0:
            glcm = [[val / total for val in row] for row in glcm]

        # Compute texture features
        energy = sum(glcm[i][j] ** 2 for i in range(levels) for j in range(levels))

        contrast = sum((i - j) ** 2 * glcm[i][j]
                      for i in range(levels) for j in range(levels))

        homogeneity = sum(glcm[i][j] / (1 + abs(i - j))
                         for i in range(levels) for j in range(levels))

        entropy = -sum(glcm[i][j] * math.log(glcm[i][j] + 1e-10)
                      for i in range(levels) for j in range(levels))

        return {
            'energy': energy,
            'contrast': contrast,
            'homogeneity': homogeneity,
            'entropy': entropy
        }

    def extract_edge_features(self) -> Dict[str, float]:
        """
        Extract edge-based features using gradient analysis.

        Returns edge density, average gradient magnitude, and gradient direction histogram.
        """
        edge_map = [[0.0] * self.width for _ in range(self.height)]
        gradient_directions = []

        for i in range(self.height):
            for j in range(self.width):
                # Compute gradients across all channels
                gx_total = 0.0
                gy_total = 0.0

                for c in range(self.channels):
                    # Sobel operator
                    gx = (
                        self.pixels[(i-1) % self.height][(j+1) % self.width][c] +
                        2 * self.pixels[i][(j+1) % self.width][c] +
                        self.pixels[(i+1) % self.height][(j+1) % self.width][c] -
                        self.pixels[(i-1) % self.height][(j-1) % self.width][c] -
                        2 * self.pixels[i][(j-1) % self.width][c] -
                        self.pixels[(i+1) % self.height][(j-1) % self.width][c]
                    )
                    gy = (
                        self.pixels[(i+1) % self.height][(j-1) % self.width][c] +
                        2 * self.pixels[(i+1) % self.height][j][c] +
                        self.pixels[(i+1) % self.height][(j+1) % self.width][c] -
                        self.pixels[(i-1) % self.height][(j-1) % self.width][c] -
                        2 * self.pixels[(i-1) % self.height][j][c] -
                        self.pixels[(i-1) % self.height][(j+1) % self.width][c]
                    )
                    gx_total += gx
                    gy_total += gy

                # Average gradient magnitude
                magnitude = math.sqrt(gx_total ** 2 + gy_total ** 2) / self.channels
                edge_map[i][j] = magnitude

                # Gradient direction
                if magnitude > 0.1:  # Threshold for significant edges
                    direction = math.atan2(gy_total, gx_total)
                    gradient_directions.append(direction)

        # Compute edge density
        total_pixels = self.height * self.width
        edge_pixels = sum(1 for i in range(self.height)
                         for j in range(self.width) if edge_map[i][j] > 0.1)
        edge_density = edge_pixels / total_pixels if total_pixels > 0 else 0.0

        # Average gradient magnitude
        avg_magnitude = sum(sum(row) for row in edge_map) / total_pixels if total_pixels > 0 else 0.0

        # Dominant gradient direction
        dominant_direction = sum(gradient_directions) / len(gradient_directions) if gradient_directions else 0.0

        return {
            'edge_density': edge_density,
            'avg_gradient_magnitude': avg_magnitude,
            'dominant_direction': dominant_direction,
            'num_edge_pixels': edge_pixels
        }

    def extract_features(self) -> Dict[str, Any]:
        """
        Extract comprehensive image features.

        Combines histogram, moments, texture, and edge features into a single dictionary.
        """
        features = {
            'histogram': self.compute_histogram(),
            'moments': self.compute_moments(),
            'texture': self.extract_texture_features(),
            'edges': self.extract_edge_features()
        }
        return features


@dataclass
class VideoModality(Modality):
    """Video modality (sequence of images/frames)."""
    width: int = 32
    height: int = 32
    channels: int = 3
    fps: float = 30.0
    frames: List[List[List[List[float]]]] = field(default_factory=list)  # [frame][y][x][c]

    def __post_init__(self):
        if not self.frames:
            # Initialize with a single black frame
            self.frames = [[
                [[0.0 for _ in range(self.channels)] for _ in range(self.width)]
                for _ in range(self.height)
            ]]
        self.modality_type = ModalityType.IMAGE  # Video is sequence of images

    def to_vector(self) -> List[float]:
        """Flatten video to vector."""
        vector = []
        for frame in self.frames:
            for row in frame:
                for pixel in row:
                    vector.extend(pixel)
        return vector

    def from_vector(self, vector: List[float]):
        """Reconstruct video from vector."""
        frame_size = self.height * self.width * self.channels
        num_frames = len(vector) // frame_size if frame_size > 0 else 1

        self.frames = []
        idx = 0
        for _ in range(num_frames):
            frame = [
                [[0.0 for _ in range(self.channels)] for _ in range(self.width)]
                for _ in range(self.height)
            ]
            for i in range(self.height):
                for j in range(self.width):
                    for c in range(self.channels):
                        if idx < len(vector):
                            frame[i][j][c] = vector[idx]
                            idx += 1
            self.frames.append(frame)

    def get_shape(self) -> Tuple[int, ...]:
        """Get video shape."""
        return (len(self.frames), self.height, self.width, self.channels)

    def add_frame(self, frame: List[List[List[float]]]):
        """Add a frame to the video."""
        if len(frame) == self.height and len(frame[0]) == self.width:
            self.frames.append(frame)

    def get_frame(self, idx: int) -> List[List[List[float]]]:
        """Get frame at index."""
        if 0 <= idx < len(self.frames):
            return self.frames[idx]
        return [[
            [0.0 for _ in range(self.channels)] for _ in range(self.width)
        ] for _ in range(self.height)]

    def compute_frame_difference(self, frame1_idx: int, frame2_idx: int) -> List[List[List[float]]]:
        """
        Compute pixel-wise difference between two frames.

        Used for motion detection.
        """
        if frame1_idx >= len(self.frames) or frame2_idx >= len(self.frames):
            return [[
                [0.0 for _ in range(self.channels)] for _ in range(self.width)
            ] for _ in range(self.height)]

        frame1 = self.frames[frame1_idx]
        frame2 = self.frames[frame2_idx]

        diff = [[
            [0.0 for _ in range(self.channels)] for _ in range(self.width)
        ] for _ in range(self.height)]

        for i in range(self.height):
            for j in range(self.width):
                for c in range(self.channels):
                    diff[i][j][c] = abs(frame2[i][j][c] - frame1[i][j][c])

        return diff

    def detect_motion(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Detect motion between consecutive frames.

        Returns a list of motion descriptors for each frame transition.
        """
        if len(self.frames) < 2:
            return []

        motion_data = []

        for i in range(len(self.frames) - 1):
            diff = self.compute_frame_difference(i, i + 1)

            # Compute motion metrics
            total_motion = 0.0
            motion_pixels = 0
            motion_map = [[False] * self.width for _ in range(self.height)]

            for y in range(self.height):
                for x in range(self.width):
                    pixel_change = sum(diff[y][x]) / self.channels
                    total_motion += pixel_change
                    if pixel_change > threshold:
                        motion_pixels += 1
                        motion_map[y][x] = True

            total_pixels = self.height * self.width
            motion_density = motion_pixels / total_pixels if total_pixels > 0 else 0.0
            avg_motion = total_motion / total_pixels if total_pixels > 0 else 0.0

            # Compute center of motion
            if motion_pixels > 0:
                center_x = sum(x for y in range(self.height) for x in range(self.width)
                             if motion_map[y][x]) / motion_pixels
                center_y = sum(y for y in range(self.height) for x in range(self.width)
                             if motion_map[y][x]) / motion_pixels
            else:
                center_x = self.width / 2
                center_y = self.height / 2

            motion_data.append({
                'frame_index': i,
                'motion_density': motion_density,
                'avg_motion': avg_motion,
                'motion_pixels': motion_pixels,
                'center_of_motion': (center_x, center_y)
            })

        return motion_data

    def extract_temporal_features(self) -> Dict[str, Any]:
        """
        Extract temporal features across frames.

        Computes frame-to-frame changes, motion patterns, and temporal statistics.
        """
        if len(self.frames) < 2:
            return {
                'num_frames': len(self.frames),
                'duration': len(self.frames) / self.fps,
                'avg_temporal_change': 0.0,
                'max_temporal_change': 0.0,
                'temporal_variance': 0.0
            }

        # Compute temporal changes
        temporal_changes = []
        for i in range(len(self.frames) - 1):
            diff = self.compute_frame_difference(i, i + 1)
            # Average change across all pixels
            total_change = sum(
                sum(sum(pixel) for pixel in row)
                for row in diff
            )
            avg_change = total_change / (self.height * self.width * self.channels)
            temporal_changes.append(avg_change)

        # Compute statistics
        avg_temporal_change = sum(temporal_changes) / len(temporal_changes)
        max_temporal_change = max(temporal_changes) if temporal_changes else 0.0
        min_temporal_change = min(temporal_changes) if temporal_changes else 0.0

        # Temporal variance
        temporal_variance = sum(
            (tc - avg_temporal_change) ** 2 for tc in temporal_changes
        ) / len(temporal_changes) if temporal_changes else 0.0

        # Scene cut detection (large temporal changes)
        scene_cut_threshold = avg_temporal_change * 3.0
        scene_cuts = [i for i, tc in enumerate(temporal_changes) if tc > scene_cut_threshold]

        # Optical flow estimation (simplified)
        motion_vectors = self._estimate_optical_flow()

        return {
            'num_frames': len(self.frames),
            'duration': len(self.frames) / self.fps,
            'avg_temporal_change': avg_temporal_change,
            'max_temporal_change': max_temporal_change,
            'min_temporal_change': min_temporal_change,
            'temporal_variance': temporal_variance,
            'scene_cuts': scene_cuts,
            'num_scene_cuts': len(scene_cuts),
            'motion_vectors': motion_vectors
        }

    def _estimate_optical_flow(self, block_size: int = 4) -> List[Dict[str, Any]]:
        """
        Estimate optical flow using block matching (simplified Lucas-Kanade approach).

        Divides frames into blocks and estimates motion vectors.
        """
        if len(self.frames) < 2:
            return []

        flow_data = []

        # Process consecutive frame pairs
        for frame_idx in range(len(self.frames) - 1):
            frame1 = self.frames[frame_idx]
            frame2 = self.frames[frame_idx + 1]

            vectors = []

            # Divide into blocks
            for y in range(0, self.height - block_size, block_size):
                for x in range(0, self.width - block_size, block_size):
                    # Extract block from frame1
                    block1 = [
                        [frame1[y + dy][x + dx] for dx in range(block_size)]
                        for dy in range(block_size)
                    ]

                    # Search for best match in frame2 (within search window)
                    search_range = block_size
                    best_match = (0, 0)
                    best_score = float('inf')

                    for dy in range(-search_range, search_range + 1):
                        for dx in range(-search_range, search_range + 1):
                            ny = y + dy
                            nx = x + dx

                            if 0 <= ny < self.height - block_size and 0 <= nx < self.width - block_size:
                                # Compute SSD (Sum of Squared Differences)
                                ssd = 0.0
                                for by in range(block_size):
                                    for bx in range(block_size):
                                        for c in range(self.channels):
                                            diff = block1[by][bx][c] - frame2[ny + by][nx + bx][c]
                                            ssd += diff ** 2

                                if ssd < best_score:
                                    best_score = ssd
                                    best_match = (dx, dy)

                    vectors.append({
                        'position': (x, y),
                        'motion': best_match,
                        'magnitude': math.sqrt(best_match[0]**2 + best_match[1]**2)
                    })

            # Compute average motion
            avg_magnitude = sum(v['magnitude'] for v in vectors) / len(vectors) if vectors else 0.0

            flow_data.append({
                'frame_index': frame_idx,
                'vectors': vectors,
                'avg_motion_magnitude': avg_magnitude
            })

        return flow_data


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

    def _apply_window(self, samples: List[float], window_type: str = 'hamming') -> List[float]:
        """
        Apply window function to samples.

        Supports Hamming, Hanning, and Blackman windows.
        """
        n = len(samples)
        if window_type == 'hamming':
            window = [0.54 - 0.46 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
        elif window_type == 'hanning':
            window = [0.5 * (1 - math.cos(2 * math.pi * i / (n - 1))) for i in range(n)]
        elif window_type == 'blackman':
            window = [
                0.42 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) +
                0.08 * math.cos(4 * math.pi * i / (n - 1))
                for i in range(n)
            ]
        else:  # rectangular
            window = [1.0] * n

        return [samples[i] * window[i] for i in range(n)]

    def _dft(self, samples: List[float]) -> List[complex]:
        """
        Compute Discrete Fourier Transform using direct method.

        Returns complex frequency components.
        """
        n = len(samples)
        spectrum = []

        for k in range(n // 2):  # Only compute positive frequencies
            real = sum(samples[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
            imag = -sum(samples[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
            spectrum.append(complex(real, imag))

        return spectrum

    def _magnitude_spectrum(self, spectrum: List[complex]) -> List[float]:
        """Compute magnitude from complex spectrum."""
        return [abs(s) for s in spectrum]

    def _power_spectrum(self, spectrum: List[complex]) -> List[float]:
        """Compute power spectrum from complex spectrum."""
        return [abs(s) ** 2 for s in spectrum]

    def get_spectrogram(self, window_size: int = 256, hop_size: Optional[int] = None) -> List[List[float]]:
        """
        Compute spectrogram using proper DFT.

        Returns time-frequency representation of the audio signal.
        """
        if hop_size is None:
            hop_size = window_size // 2

        spectrogram = []
        for i in range(0, len(self.samples) - window_size, hop_size):
            window = self.samples[i:i + window_size]
            # Apply Hamming window
            windowed = self._apply_window(window, 'hamming')
            # Compute DFT
            spectrum = self._dft(windowed)
            # Get magnitude
            magnitude = self._magnitude_spectrum(spectrum)
            spectrogram.append(magnitude)

        return spectrogram

    def zero_crossing_rate(self) -> float:
        """
        Compute zero-crossing rate.

        Measures how often the signal changes sign.
        Useful for distinguishing voiced/unvoiced speech and percussion.
        """
        if len(self.samples) < 2:
            return 0.0

        crossings = sum(
            1 for i in range(len(self.samples) - 1)
            if self.samples[i] * self.samples[i + 1] < 0
        )

        return crossings / (len(self.samples) - 1)

    def spectral_centroid(self, window_size: int = 256) -> List[float]:
        """
        Compute spectral centroid over time.

        Indicates where the "center of mass" of the spectrum is located.
        """
        spectrogram = self.get_spectrogram(window_size)
        centroids = []

        for spectrum in spectrogram:
            # Compute weighted average of frequencies
            total_magnitude = sum(spectrum)
            if total_magnitude > 0:
                centroid = sum(k * spectrum[k] for k in range(len(spectrum))) / total_magnitude
                # Convert to Hz
                centroid_hz = centroid * self.sample_rate / window_size
                centroids.append(centroid_hz)
            else:
                centroids.append(0.0)

        return centroids

    def spectral_rolloff(self, window_size: int = 256, rolloff_percent: float = 0.85) -> List[float]:
        """
        Compute spectral rolloff over time.

        Frequency below which rolloff_percent of spectral energy is contained.
        """
        spectrogram = self.get_spectrogram(window_size)
        rolloffs = []

        for spectrum in spectrogram:
            total_energy = sum(spectrum)
            if total_energy > 0:
                threshold = rolloff_percent * total_energy
                cumulative = 0.0
                rolloff_idx = 0

                for k in range(len(spectrum)):
                    cumulative += spectrum[k]
                    if cumulative >= threshold:
                        rolloff_idx = k
                        break

                # Convert to Hz
                rolloff_hz = rolloff_idx * self.sample_rate / window_size
                rolloffs.append(rolloff_hz)
            else:
                rolloffs.append(0.0)

        return rolloffs

    def spectral_flux(self, window_size: int = 256) -> List[float]:
        """
        Compute spectral flux over time.

        Measures the rate of change in the power spectrum.
        """
        spectrogram = self.get_spectrogram(window_size)
        flux = []

        for i in range(len(spectrogram) - 1):
            # Compute difference between consecutive frames
            diff = sum(
                (spectrogram[i + 1][k] - spectrogram[i][k]) ** 2
                for k in range(len(spectrogram[i]))
            )
            flux.append(math.sqrt(diff))

        return flux

    def _mel_filterbank(self, num_filters: int = 26, fft_size: int = 256) -> List[List[float]]:
        """
        Create Mel filterbank.

        Returns triangular filters in the Mel scale.
        """
        # Convert Hz to Mel scale
        def hz_to_mel(hz):
            return 2595 * math.log10(1 + hz / 700.0)

        def mel_to_hz(mel):
            return 700 * (10 ** (mel / 2595.0) - 1)

        # Create equally spaced points in Mel scale
        min_mel = hz_to_mel(0)
        max_mel = hz_to_mel(self.sample_rate / 2)

        mel_points = [min_mel + i * (max_mel - min_mel) / (num_filters + 1)
                     for i in range(num_filters + 2)]
        hz_points = [mel_to_hz(m) for m in mel_points]

        # Convert to FFT bin numbers
        bin_points = [int((fft_size + 1) * hz / self.sample_rate) for hz in hz_points]

        # Create triangular filters
        filterbank = []
        for i in range(1, num_filters + 1):
            filt = [0.0] * (fft_size // 2)

            # Rising slope
            for k in range(bin_points[i - 1], bin_points[i]):
                if bin_points[i] != bin_points[i - 1]:
                    filt[k] = (k - bin_points[i - 1]) / (bin_points[i] - bin_points[i - 1])

            # Falling slope
            for k in range(bin_points[i], bin_points[i + 1]):
                if bin_points[i + 1] != bin_points[i]:
                    filt[k] = (bin_points[i + 1] - k) / (bin_points[i + 1] - bin_points[i])

            filterbank.append(filt)

        return filterbank

    def _dct(self, values: List[float], num_coeffs: int = 13) -> List[float]:
        """
        Compute Discrete Cosine Transform.

        Used to decorrelate Mel filterbank energies.
        """
        n = len(values)
        coeffs = []

        for k in range(num_coeffs):
            coeff = sum(
                values[i] * math.cos(math.pi * k * (i + 0.5) / n)
                for i in range(n)
            )
            coeffs.append(coeff)

        return coeffs

    def compute_mfcc(self, num_coeffs: int = 13, window_size: int = 256,
                     num_filters: int = 26) -> List[List[float]]:
        """
        Compute Mel-Frequency Cepstral Coefficients.

        MFCCs are widely used features in speech and audio processing.

        Returns a list of MFCC vectors, one per frame.
        """
        # Get spectrogram
        spectrogram = self.get_spectrogram(window_size)

        # Get Mel filterbank
        filterbank = self._mel_filterbank(num_filters, window_size)

        mfccs = []

        for spectrum in spectrogram:
            # Apply Mel filters
            mel_energies = []
            for filt in filterbank:
                # Multiply spectrum by filter and sum
                energy = sum(spectrum[k] * filt[k] for k in range(len(spectrum)) if k < len(filt))
                # Take log (add small value to avoid log(0))
                mel_energies.append(math.log(energy + 1e-10))

            # Apply DCT to decorrelate
            mfcc = self._dct(mel_energies, num_coeffs)
            mfccs.append(mfcc)

        return mfccs

    def extract_audio_features(self) -> Dict[str, Any]:
        """
        Extract comprehensive audio features.

        Combines time-domain and frequency-domain features.
        """
        # Time-domain features
        zcr = self.zero_crossing_rate()
        rms_energy = math.sqrt(sum(s ** 2 for s in self.samples) / len(self.samples)) if self.samples else 0.0

        # Frequency-domain features
        centroids = self.spectral_centroid()
        rolloffs = self.spectral_rolloff()
        flux = self.spectral_flux()
        mfccs = self.compute_mfcc()

        # Compute statistics
        def compute_stats(values):
            if not values:
                return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            return {
                'mean': mean,
                'std': math.sqrt(variance),
                'min': min(values),
                'max': max(values)
            }

        return {
            'zero_crossing_rate': zcr,
            'rms_energy': rms_energy,
            'spectral_centroid': compute_stats(centroids),
            'spectral_rolloff': compute_stats(rolloffs),
            'spectral_flux': compute_stats(flux),
            'mfcc': {
                'num_frames': len(mfccs),
                'num_coeffs': len(mfccs[0]) if mfccs else 0,
                'mean_mfcc': [
                    sum(mfccs[i][j] for i in range(len(mfccs))) / len(mfccs)
                    for j in range(len(mfccs[0]))
                ] if mfccs else []
            }
        }


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
        """
        Reconstruct graph from vector.

        Uses adjacency matrix and node features to rebuild graph structure.
        """
        if not vector or not self.nodes:
            return

        n = len(self.nodes)
        feature_dim = 10  # Default feature dimension

        # Calculate expected sizes
        adj_size = n * n
        features_size = n * feature_dim

        if len(vector) < adj_size:
            return

        # Extract adjacency matrix
        adj_matrix = []
        idx = 0
        for i in range(n):
            row = vector[idx:idx + n]
            adj_matrix.append(row)
            idx += n

        # Reconstruct edges from adjacency matrix
        self.edges = []
        edge_threshold = 0.5  # Threshold for edge existence

        for i in range(n):
            for j in range(n):
                if adj_matrix[i][j] > edge_threshold:
                    src = self.nodes[i]
                    dst = self.nodes[j]
                    if (src, dst) not in self.edges:
                        self.edges.append((src, dst))

        # Extract node features if available
        if len(vector) >= adj_size + features_size:
            self.node_features = {}
            for i, node in enumerate(self.nodes):
                feature_start = adj_size + i * feature_dim
                feature_end = feature_start + feature_dim
                if feature_end <= len(vector):
                    features = vector[feature_start:feature_end]
                    self.node_features[node] = features

        # Reconstruct edge features if available
        remaining_size = len(vector) - adj_size - features_size
        edge_feature_dim = remaining_size // len(self.edges) if self.edges else 0

        if edge_feature_dim > 0 and self.edges:
            self.edge_features = {}
            edge_idx = adj_size + features_size

            for edge in self.edges:
                if edge_idx + edge_feature_dim <= len(vector):
                    edge_feat = vector[edge_idx:edge_idx + edge_feature_dim]
                    self.edge_features[edge] = edge_feat
                    edge_idx += edge_feature_dim

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
