"""Load and filter Pennsylvania karst features for the study area."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import COUNTY_AREA_KM2, COUNTY_BBOX, COUNTY_POP, DATA_PROCESSED
from src.geo_utils import assign_county
from src.io_utils import read_dbf


def load_and_filter_karst(dbf_path: Path) -> pd.DataFrame:
    """Parse the DCNR karst DBF and save study-area karst records."""
    _, records = read_dbf(dbf_path)
    raw_df = pd.DataFrame(records)
    if raw_df.empty:
        karst_df = pd.DataFrame(columns=["lat", "lon", "karst_type", "county"])
    else:
        lat_col = _find_column(raw_df, ["lat", "latitude", "y", "ycoord", "y_coord", "point_y"])
        lon_col = _find_column(
            raw_df, ["lon", "long", "longitude", "x", "xcoord", "x_coord", "point_x"]
        )
        type_col = _find_column(
            raw_df,
            [
                "karst_type",
                "karsttype",
                "type",
                "feature",
                "feature_ty",
                "feat_type",
                "class",
                "label",
                "symbol",
            ],
            required=False,
        )

        raw_df["lat"] = pd.to_numeric(raw_df[lat_col], errors="coerce")
        raw_df["lon"] = pd.to_numeric(raw_df[lon_col], errors="coerce")
        if type_col is None:
            raw_df["karst_type"] = "mapped karst"
        else:
            raw_df["karst_type"] = raw_df[type_col].fillna("unknown").astype(str).str.lower()

        karst_df = raw_df[["lat", "lon", "karst_type"]].dropna(subset=["lat", "lon"]).copy()
        karst_df["county"] = [
            assign_county(float(row.lon), float(row.lat), COUNTY_BBOX)
            for row in karst_df.itertuples(index=False)
        ]
        karst_df = karst_df.dropna(subset=["county"]).reset_index(drop=True)
        karst_df["karst_type"] = karst_df["karst_type"].fillna("unknown").astype(str).str.lower()

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    karst_df.to_csv(DATA_PROCESSED / "karst_study_area.csv", index=False)
    _write_summary(raw_total=len(records), karst_df=karst_df)
    return karst_df


def _find_column(
    df: pd.DataFrame, candidates: list[str], required: bool = True
) -> str | None:
    normalized = {str(col).lower().replace(" ", "_"): str(col) for col in df.columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for key, original in normalized.items():
        if any(candidate in key for candidate in candidates):
            return original
    if required:
        raise ValueError(
            "Could not identify required DBF column. "
            f"Available columns: {', '.join(map(str, df.columns))}"
        )
    return None


def _write_summary(raw_total: int, karst_df: pd.DataFrame) -> None:
    summary: dict[str, Any] = {
        "total_statewide": raw_total,
        "total_study_area": int(len(karst_df)),
        "type_distribution": karst_df["karst_type"].value_counts().to_dict(),
        "by_county": karst_df["county"].value_counts().to_dict(),
        "county_area_km2": COUNTY_AREA_KM2,
        "county_population": COUNTY_POP,
    }
    with (DATA_PROCESSED / "karst_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
