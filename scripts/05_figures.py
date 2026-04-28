"""Run Step 5: generate all figures."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import make_all_figures


def main() -> None:
    """Generate all project figures from processed outputs."""
    make_all_figures()


if __name__ == "__main__":
    main()
