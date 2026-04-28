"""Tests for geographic helpers."""

from src.geo_utils import haversine_m, in_bbox


def test_haversine_known_distance() -> None:
    """Allentown to Bethlehem should be on the order of 8 to 12 km."""
    d = haversine_m(40.602, -75.490, 40.601, -75.371)
    assert 8000 < d < 12000


def test_bbox() -> None:
    """Bounding-box checks should include nearby points and exclude far points."""
    assert in_bbox(-75.5, 40.6, (-75.84, 40.40, -75.35, 40.79))
    assert not in_bbox(-80, 40.6, (-75.84, 40.40, -75.35, 40.79))
