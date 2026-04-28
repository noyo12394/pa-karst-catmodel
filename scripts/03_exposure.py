"""Run Step 3: compute facility exposure and summary tables."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATA_PROCESSED
from src.exposure import compute_exposure, summary_tables


def main() -> None:
    """Compute exposure from processed karst and facility CSVs."""
    karst = pd.read_csv(DATA_PROCESSED / "karst_study_area.csv")
    facilities = pd.read_csv(DATA_PROCESSED / "facilities.csv")
    exposed = compute_exposure(karst, facilities)
    summary_tables(exposed)


if __name__ == "__main__":
    main()
