"""Run the full PA karst CATModel pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATA_RAW, OUT_PRESENTATION
from src.exposure import compute_exposure, summary_tables
from src.facilities import generate_facilities
from src.figures import make_all_figures
from src.khi import compute_khi, loss_proxy, sensitivity_analysis
from src.load_karst import load_and_filter_karst
from src.presentation import build_presentation


def main() -> None:
    """Execute all six pipeline steps in order."""
    dbf_path = _resolve_dbf()
    print(f"Step 1/6: loading karst DBF from {dbf_path}")
    karst = load_and_filter_karst(dbf_path)

    print("Step 2/6: generating synthetic essential facilities")
    facilities = generate_facilities()

    print("Step 3/6: computing facility exposure")
    facilities = compute_exposure(karst, facilities)
    summary_tables(facilities)

    print("Step 4/6: computing KHI, sensitivity, and loss proxy")
    munis = compute_khi(karst, facilities)
    sensitivity_analysis(munis)
    loss_proxy(facilities)

    print("Step 5/6: generating figures")
    make_all_figures()

    print("Step 6/6: building presentation")
    out_path = OUT_PRESENTATION / "PA_Karst_Final_Presentation.pptx"
    build_presentation(out_path)
    print(f"Done: {out_path}")


def _resolve_dbf() -> Path:
    preferred = DATA_RAW / "DCNR_PAKarst.dbf"
    if preferred.exists():
        return preferred
    matches = sorted(DATA_RAW.glob("*.dbf"))
    if matches:
        return matches[0]
    raise FileNotFoundError(
        f"No DBF found. Place DCNR_PAKarst.dbf in {DATA_RAW} before running the pipeline."
    )


if __name__ == "__main__":
    main()
