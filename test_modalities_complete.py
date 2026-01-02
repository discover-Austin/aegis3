#!/usr/bin/env python3
"""
Test script to verify all placeholder implementations are complete and functional.
"""

import sys
import math
from multimodal.modalities import (
    ImageModality, VideoModality, AudioModality, GraphModality,
    ModalityType
)


def test_image_features():
    """Test image feature extraction (histogram, moments, texture, edges)."""
    print("Testing ImageModality feature extraction...")

    # Create a test image with some pattern
    img = ImageModality(width=16, height=16, channels=3)

    # Create a simple gradient pattern
    for i in range(img.height):
        for j in range(img.width):
            value = (i + j) / (img.height + img.width)
            img.pixels[i][j] = [value, value * 0.8, value * 0.6]

    # Test histogram
    histogram = img.compute_histogram(bins=8)
    assert 'channel_0' in histogram, "Histogram missing channel_0"
    assert len(histogram['channel_0']) == 8, "Histogram wrong size"
    assert sum(histogram['channel_0']) == img.height * img.width, "Histogram count incorrect"
    print("  ✓ Histogram computation works")

    # Test moments
    moments = img.compute_moments()
    assert 'channel_0' in moments, "Moments missing channel_0"
    assert 'mean' in moments['channel_0'], "Moments missing mean"
    assert 'variance' in moments['channel_0'], "Moments missing variance"
    assert 'skewness' in moments['channel_0'], "Moments missing skewness"
    assert 'kurtosis' in moments['channel_0'], "Moments missing kurtosis"
    print(f"  ✓ Moments computation works (mean={moments['channel_0']['mean']:.3f})")

    # Test texture features
    texture = img.extract_texture_features()
    assert 'energy' in texture, "Texture missing energy"
    assert 'contrast' in texture, "Texture missing contrast"
    assert 'homogeneity' in texture, "Texture missing homogeneity"
    assert 'entropy' in texture, "Texture missing entropy"
    print(f"  ✓ Texture features work (energy={texture['energy']:.3f}, entropy={texture['entropy']:.3f})")

    # Test edge features
    edges = img.extract_edge_features()
    assert 'edge_density' in edges, "Edge features missing edge_density"
    assert 'avg_gradient_magnitude' in edges, "Edge features missing avg_gradient_magnitude"
    assert 'dominant_direction' in edges, "Edge features missing dominant_direction"
    print(f"  ✓ Edge features work (density={edges['edge_density']:.3f})")

    # Test comprehensive feature extraction
    features = img.extract_features()
    assert 'histogram' in features, "Features missing histogram"
    assert 'moments' in features, "Features missing moments"
    assert 'texture' in features, "Features missing texture"
    assert 'edges' in features, "Features missing edges"
    print("  ✓ Comprehensive feature extraction works")

    print("✓ All ImageModality features implemented correctly!\n")


def test_video_processing():
    """Test video processing (temporal features, motion detection)."""
    print("Testing VideoModality processing...")

    # Create a test video with motion
    video = VideoModality(width=8, height=8, channels=3, fps=10.0)

    # Add frames with simulated motion
    for frame_idx in range(5):
        frame = [[[0.0] * 3 for _ in range(8)] for _ in range(8)]
        # Create a moving bright spot
        x = frame_idx + 2
        y = frame_idx + 2
        if x < 8 and y < 8:
            frame[y][x] = [1.0, 1.0, 1.0]
        video.add_frame(frame)

    # Test basic properties
    assert len(video.frames) == 6, "Frame count incorrect"  # 1 initial + 5 added
    assert video.get_shape() == (6, 8, 8, 3), "Video shape incorrect"
    print(f"  ✓ Video has {len(video.frames)} frames")

    # Test frame difference
    diff = video.compute_frame_difference(0, 1)
    assert len(diff) == 8, "Frame difference height incorrect"
    assert len(diff[0]) == 8, "Frame difference width incorrect"
    print("  ✓ Frame difference computation works")

    # Test motion detection
    motion_data = video.detect_motion(threshold=0.05)
    assert len(motion_data) > 0, "Motion detection returned no data"
    assert 'motion_density' in motion_data[0], "Motion data missing motion_density"
    assert 'center_of_motion' in motion_data[0], "Motion data missing center_of_motion"
    print(f"  ✓ Motion detection works ({len(motion_data)} motion frames)")

    # Test temporal features
    temporal = video.extract_temporal_features()
    assert 'num_frames' in temporal, "Temporal features missing num_frames"
    assert 'duration' in temporal, "Temporal features missing duration"
    assert 'avg_temporal_change' in temporal, "Temporal features missing avg_temporal_change"
    assert 'temporal_variance' in temporal, "Temporal features missing temporal_variance"
    assert 'scene_cuts' in temporal, "Temporal features missing scene_cuts"
    assert 'motion_vectors' in temporal, "Temporal features missing motion_vectors"
    print(f"  ✓ Temporal features work (avg_change={temporal['avg_temporal_change']:.4f})")

    # Test optical flow
    assert len(temporal['motion_vectors']) > 0, "Optical flow returned no data"
    assert 'vectors' in temporal['motion_vectors'][0], "Optical flow missing vectors"
    print(f"  ✓ Optical flow estimation works ({len(temporal['motion_vectors'])} flow frames)")

    # Test vector conversion
    vec = video.to_vector()
    assert len(vec) > 0, "Video to_vector returned empty"
    video2 = VideoModality(width=8, height=8, channels=3)
    video2.from_vector(vec)
    assert len(video2.frames) > 0, "Video from_vector failed"
    print("  ✓ Vector conversion (to/from) works")

    print("✓ All VideoModality features implemented correctly!\n")


def test_audio_processing():
    """Test audio processing (DFT, MFCCs, spectral features, zero-crossing)."""
    print("Testing AudioModality processing...")

    # Create audio with a simple tone
    audio = AudioModality(sample_rate=1000, duration=0.1)  # 100ms
    audio.generate_tone(frequency=100.0, amplitude=0.5)

    assert len(audio.samples) == 100, "Audio sample count incorrect"
    print(f"  ✓ Audio has {len(audio.samples)} samples")

    # Test zero-crossing rate
    zcr = audio.zero_crossing_rate()
    assert isinstance(zcr, float), "ZCR not a float"
    assert 0.0 <= zcr <= 1.0, "ZCR out of range"
    print(f"  ✓ Zero-crossing rate: {zcr:.4f}")

    # Test spectrogram with proper DFT
    spectrogram = audio.get_spectrogram(window_size=32)
    assert len(spectrogram) > 0, "Spectrogram empty"
    assert len(spectrogram[0]) == 16, "Spectrogram frequency bins incorrect"  # window_size/2
    print(f"  ✓ Spectrogram works ({len(spectrogram)} frames, {len(spectrogram[0])} freq bins)")

    # Test spectral centroid
    centroids = audio.spectral_centroid(window_size=32)
    assert len(centroids) > 0, "Spectral centroid empty"
    assert all(isinstance(c, (int, float)) for c in centroids), "Centroid values invalid"
    print(f"  ✓ Spectral centroid works (mean={sum(centroids)/len(centroids):.2f} Hz)")

    # Test spectral rolloff
    rolloffs = audio.spectral_rolloff(window_size=32)
    assert len(rolloffs) > 0, "Spectral rolloff empty"
    assert all(isinstance(r, (int, float)) for r in rolloffs), "Rolloff values invalid"
    print(f"  ✓ Spectral rolloff works (mean={sum(rolloffs)/len(rolloffs):.2f} Hz)")

    # Test spectral flux
    flux = audio.spectral_flux(window_size=32)
    assert len(flux) > 0, "Spectral flux empty"
    assert all(isinstance(f, (int, float)) for f in flux), "Flux values invalid"
    print(f"  ✓ Spectral flux works ({len(flux)} values)")

    # Test MFCCs
    mfccs = audio.compute_mfcc(num_coeffs=13, window_size=32, num_filters=20)
    assert len(mfccs) > 0, "MFCCs empty"
    assert len(mfccs[0]) == 13, "MFCC coefficient count incorrect"
    assert all(isinstance(m, (int, float)) for m in mfccs[0]), "MFCC values invalid"
    print(f"  ✓ MFCCs work ({len(mfccs)} frames, {len(mfccs[0])} coefficients)")

    # Test comprehensive audio features
    features = audio.extract_audio_features()
    assert 'zero_crossing_rate' in features, "Features missing zero_crossing_rate"
    assert 'rms_energy' in features, "Features missing rms_energy"
    assert 'spectral_centroid' in features, "Features missing spectral_centroid"
    assert 'spectral_rolloff' in features, "Features missing spectral_rolloff"
    assert 'spectral_flux' in features, "Features missing spectral_flux"
    assert 'mfcc' in features, "Features missing mfcc"
    print(f"  ✓ Comprehensive audio features work (RMS={features['rms_energy']:.3f})")

    print("✓ All AudioModality features implemented correctly!\n")


def test_graph_reconstruction():
    """Test graph reconstruction from vector."""
    print("Testing GraphModality reconstruction...")

    # Create a test graph
    graph = GraphModality()
    graph.add_node("A", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    graph.add_node("B", [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0])
    graph.add_node("C", [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0])
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("A", "C")

    print(f"  ✓ Created graph with {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Convert to vector
    vec = graph.to_vector()
    assert len(vec) > 0, "Graph to_vector returned empty"
    print(f"  ✓ Graph to vector: {len(vec)} elements")

    # Reconstruct from vector
    graph2 = GraphModality()
    graph2.nodes = ["A", "B", "C"]  # Need to know node names
    graph2.from_vector(vec)

    # Verify reconstruction
    assert len(graph2.edges) > 0, "Graph reconstruction failed - no edges"
    assert len(graph2.node_features) > 0, "Graph reconstruction failed - no node features"
    print(f"  ✓ Graph reconstructed: {len(graph2.edges)} edges, {len(graph2.node_features)} node features")

    # Verify node features were reconstructed
    for node in ["A", "B", "C"]:
        assert node in graph2.node_features, f"Node {node} features not reconstructed"
        assert len(graph2.node_features[node]) == 10, f"Node {node} features wrong size"
    print("  ✓ All node features reconstructed correctly")

    # Verify edges were reconstructed
    assert len(graph2.edges) == 3, f"Expected 3 edges, got {len(graph2.edges)}"
    print("  ✓ All edges reconstructed correctly")

    print("✓ GraphModality reconstruction implemented correctly!\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Complete Modality Implementations")
    print("=" * 60 + "\n")

    try:
        test_image_features()
        test_video_processing()
        test_audio_processing()
        test_graph_reconstruction()

        print("=" * 60)
        print("✓ ALL TESTS PASSED - All implementations are complete!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
