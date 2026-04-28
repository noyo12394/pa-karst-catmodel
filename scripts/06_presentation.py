"""Run Step 6: build the final PowerPoint presentation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import OUT_PRESENTATION
from src.presentation import build_presentation


def main() -> None:
    """Build the final project presentation."""
    build_presentation(OUT_PRESENTATION / "PA_Karst_Final_Presentation.pptx")


if __name__ == "__main__":
    main()
