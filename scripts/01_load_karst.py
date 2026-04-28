"""Run Step 1: load and filter karst records."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_all import _resolve_dbf
from src.load_karst import load_and_filter_karst


def main() -> None:
    """Load karst records for the study area."""
    load_and_filter_karst(_resolve_dbf())


if __name__ == "__main__":
    main()
