"""Tests for facility exposure buffer assignment."""

from src.exposure import buffer_for_distance


def test_buffer_for_distance_edges() -> None:
    """Distances should map to the configured proximity classes."""
    assert buffer_for_distance(99.9)[0] == "100m"
    assert buffer_for_distance(100.0)[0] == "100m"
    assert buffer_for_distance(250.0)[0] == "250m"
    assert buffer_for_distance(500.0)[0] == "500m"
    assert buffer_for_distance(1000.0)[0] == "1000m"
    assert buffer_for_distance(1000.1)[0] == "outside"
