"""Run Step 2: load real essential facilities or generate a fallback inventory."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.facilities import load_or_generate_facilities


def main() -> None:
    """Prepare essential facilities for the exposure model."""
    load_or_generate_facilities()


if __name__ == "__main__":
    main()
