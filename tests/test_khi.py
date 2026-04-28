"""Tests for KHI constants and scoring range."""

from src.config import KHI_SCHEMES


def test_khi_weights_sum_to_one() -> None:
    """Every KHI weight scheme should sum to exactly one."""
    for scheme, (h, e, c) in KHI_SCHEMES.items():
        assert abs(h + e + c - 1.0) < 1e-9, scheme


def test_khi_range() -> None:
    """KHI must be in [0, 100] given normalized inputs."""
    normalized_values = [
        (0.0, 0.0, 0.0),
        (0.3, 0.7, 0.5),
        (1.0, 1.0, 1.0),
    ]
    for h_norm, e_norm, c_norm in normalized_values:
        for h_w, e_w, c_w in KHI_SCHEMES.values():
            score = 100.0 * (h_w * h_norm + e_w * e_norm + c_w * c_norm)
            assert 0.0 <= score <= 100.0
