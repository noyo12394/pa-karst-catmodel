"""Tests for KHI constants and scoring range."""

import pandas as pd

from src.config import KHI_SCHEMES
from src.khi import _add_khi_scores


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


def test_computed_khi_columns_stay_bounded() -> None:
    """Computed KHI scores should stay within [0, 100] for normalized inputs."""
    muni_df = pd.DataFrame(
        {
            "hazard": [0.0, 3.0, 9.0],
            "exposed_count": [0.0, 2.0, 6.0],
            "criticality_weighted_exposure": [0.0, 1.0, 4.0],
        }
    )
    _add_khi_scores(muni_df, hazard_column="hazard")
    for scheme in KHI_SCHEMES:
        assert muni_df[f"KHI_{scheme}"].between(0, 100).all()
