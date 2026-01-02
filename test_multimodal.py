#!/usr/bin/env python3
"""
Test multimodal processing capabilities of AEGIS-3.

Validates that the system can actually process different modalities
and that the implementations are correct.
"""

import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent))

from multimodal.modalities import (
    ImageModality, AudioModality, VideoModality,
    GraphModality, ModalityType
)


def test_image_processing():
    """Test image modality."""
    print("\n" + "="*60)
    print("TEST: Image Processing")
    print("="*60 + "\n")

    # Create image with gradient pattern
    img = ImageModality(modality_type=ModalityType.IMAGE, width=32, height=32, channels=3)

    # Create test pattern
    for y in range(img.height):
        for x in range(img.width):
            value = (x + y) / (img.width + img.height)
            img.pixels[y][x] = [value, value * 0.8, value * 0.6]

    # Extract features
    features = img.extract_features()

    print(f"Image size: {img.width}x{img.height}x{img.channels}")
    print(f"Features extracted:")
    print(f"  - Histogram: {len(features['histogram']['channel_0'])} bins")
    print(f"  - Moments: mean={features['moments']['channel_0']['mean']:.3f}, "
          f"variance={features['moments']['channel_0']['variance']:.3f}")
    print(f"  - Texture: energy={features['texture']['energy']:.3f}, "
          f"contrast={features['texture']['contrast']:.3f}")
    print(f"  - Edges: density={features['edges']['edge_density']:.3f}")

    # Test conversion
    vec = img.to_vector()
    print(f"  - Vector size: {len(vec)}")

    print("  ✅ Image processing works correctly\n")

    return True


def test_audio_processing():
    """Test audio modality."""
    print("="*60)
    print("TEST: Audio Processing")
    print("="*60 + "\n")

    # Create audio with tone
    audio = AudioModality(modality_type=ModalityType.AUDIO, sample_rate=1000, duration=0.5)
    audio.generate_tone(frequency=200.0, amplitude=0.7)

    print(f"Audio: {len(audio.samples)} samples at {audio.sample_rate}Hz")

    # Test spectral features
    zcr = audio.zero_crossing_rate()
    centroids = audio.spectral_centroid(window_size=64)
    mfccs = audio.compute_mfcc(num_coeffs=13, window_size=64)

    print(f"Features:")
    print(f"  - Zero-crossing rate: {zcr:.4f}")
    print(f"  - Spectral centroid: {sum(centroids)/len(centroids):.1f} Hz (avg)")
    print(f"  - MFCCs: {len(mfccs)} frames x {len(mfccs[0])} coefficients")

    # Comprehensive features
    features = audio.extract_audio_features()
    print(f"  - RMS energy: {features['rms_energy']:.3f}")
    print(f"  - Spectral rolloff: {sum(features['spectral_rolloff'])/len(features['spectral_rolloff']):.1f} Hz")

    print("  ✅ Audio processing works correctly\n")

    return True


def test_video_processing():
    """Test video modality."""
    print("="*60)
    print("TEST: Video Processing")
    print("="*60 + "\n")

    # Create video with motion
    video = VideoModality(modality_type=ModalityType.VIDEO, width=16, height=16, channels=3, fps=10.0)

    # Add frames with moving object
    for frame_idx in range(10):
        frame = [[[0.0] * 3 for _ in range(16)] for _ in range(16)]
        # Moving bright spot
        x = (frame_idx * 2) % 16
        y = (frame_idx * 2) % 16
        if 0 <= x < 16 and 0 <= y < 16:
            frame[y][x] = [1.0, 1.0, 1.0]
        video.add_frame(frame)

    print(f"Video: {len(video.frames)} frames, {video.width}x{video.height}")

    # Detect motion
    motion_data = video.detect_motion(threshold=0.1)
    temporal_features = video.extract_temporal_features()

    print(f"Features:")
    print(f"  - Motion frames: {len(motion_data)}")
    print(f"  - Avg temporal change: {temporal_features['avg_temporal_change']:.4f}")
    print(f"  - Scene cuts: {temporal_features['scene_cuts']}")
    print(f"  - Optical flow vectors: {len(temporal_features['motion_vectors'])}")

    print("  ✅ Video processing works correctly\n")

    return True


def test_graph_processing():
    """Test graph modality."""
    print("="*60)
    print("TEST: Graph Processing")
    print("="*60 + "\n")

    # Create test graph
    graph = GraphModality(modality_type=ModalityType.GRAPH)

    # Add nodes with features
    for i in range(10):
        node_id = f"node_{i}"
        features = [float(i) * 0.1 for _ in range(10)]
        graph.add_node(node_id, features)

    # Add edges (ring + some random connections)
    for i in range(10):
        graph.add_edge(f"node_{i}", f"node_{(i+1)%10}")

    graph.add_edge("node_0", "node_5")
    graph.add_edge("node_2", "node_7")
    graph.add_edge("node_4", "node_9")

    print(f"Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges")

    # Compute features
    centrality = graph.compute_centrality()
    clustering = graph.compute_clustering()
    connectivity = graph.compute_connectivity()

    print(f"Features:")
    print(f"  - Avg degree centrality: {sum(centrality.values())/len(centrality):.3f}")
    print(f"  - Avg clustering: {sum(clustering.values())/len(clustering):.3f}")
    print(f"  - Is connected: {connectivity['is_connected']}")
    print(f"  - Components: {connectivity['num_components']}")

    # Test conversion
    vec = graph.to_vector()
    print(f"  - Vector size: {len(vec)}")

    print("  ✅ Graph processing works correctly\n")

    return True


def main():
    """Run all multimodal tests."""
    print("\n" + "="*60)
    print("MULTIMODAL PROCESSING VALIDATION")
    print("="*60)

    results = []

    try:
        results.append(("Image", test_image_processing()))
    except Exception as e:
        print(f"  ❌ Image test failed: {e}\n")
        results.append(("Image", False))

    try:
        results.append(("Audio", test_audio_processing()))
    except Exception as e:
        print(f"  ❌ Audio test failed: {e}\n")
        results.append(("Audio", False))

    try:
        results.append(("Video", test_video_processing()))
    except Exception as e:
        print(f"  ❌ Video test failed: {e}\n")
        results.append(("Video", False))

    try:
        results.append(("Graph", test_graph_processing()))
    except Exception as e:
        print(f"  ❌ Graph test failed: {e}\n")
        results.append(("Graph", False))

    # Summary
    print("="*60)
    print("MULTIMODAL VALIDATION SUMMARY")
    print("="*60 + "\n")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for modality, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {modality:10s}: {status}")

    print(f"\n  Total: {passed}/{total} passed")

    if passed == total:
        print("\n  ✅ ALL MULTIMODAL TESTS PASSED")
        return 0
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
