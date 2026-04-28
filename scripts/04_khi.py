"""Run Step 4: compute KHI, sensitivity, and loss proxy."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATA_PROCESSED
from src.khi import compute_khi, loss_proxy, sensitivity_analysis


def main() -> None:
    """Compute KHI outputs from processed CSVs."""
    karst = pd.read_csv(DATA_PROCESSED / "karst_study_area.csv")
    facilities = pd.read_csv(DATA_PROCESSED / "facilities_with_exposure.csv")
    munis = compute_khi(karst, facilities)
    sensitivity_analysis(munis)
    loss_proxy(facilities)


if __name__ == "__main__":
    main()
