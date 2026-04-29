"""Load and filter Pennsylvania karst features for the study area."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.boundaries import BoundaryFeature, assign_boundary, load_county_boundaries
from src.config import COUNTY_AREA_KM2, COUNTY_POP, DATA_PROCESSED
from src.io_utils import read_dbf


def load_and_filter_karst(dbf_path: Path) -> pd.DataFrame:
    """Parse the DCNR karst DBF and save study-area karst records."""
    _, records = read_dbf(dbf_path)
    county_boundaries = load_county_boundaries()
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
            _assign_county(float(row.lon), float(row.lat), county_boundaries)
            for row in karst_df.itertuples(index=False)
        ]
        karst_df = karst_df.dropna(subset=["county"]).reset_index(drop=True)
        karst_df["karst_type"] = karst_df["karst_type"].fillna("unknown").astype(str).str.lower()

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    karst_df.to_csv(DATA_PROCESSED / "karst_study_area.csv", index=False)
    _write_summary(raw_total=len(records), karst_df=karst_df, counties=county_boundaries)
    return karst_df


def _assign_county(
    lon: float, lat: float, county_boundaries: list[BoundaryFeature]
) -> str | None:
    boundary = assign_boundary(lon, lat, county_boundaries)
    return boundary.county if boundary is not None else None


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


def _write_summary(
    raw_total: int, karst_df: pd.DataFrame, counties: list[BoundaryFeature]
) -> None:
    area_lookup = {
        county.county: county.area_km2
        for county in counties
        if county.area_km2 > 0
    } or COUNTY_AREA_KM2
    by_county_counts = karst_df["county"].value_counts().to_dict()
    by_county = {
        county: {
            "karst_count": int(by_county_counts.get(county, 0)),
            "area_km2": float(area_lookup.get(county, 0.0)),
            "karst_density_km2": round(
                int(by_county_counts.get(county, 0)) / float(area_lookup.get(county, 1.0)),
                3,
            )
            if float(area_lookup.get(county, 0.0)) > 0
            else 0.0,
            "population": int(COUNTY_POP.get(county, 0)),
        }
        for county in COUNTY_POP
    }
    summary: dict[str, Any] = {
        "total_statewide": raw_total,
        "total_study_area": int(len(karst_df)),
        "type_distribution": karst_df["karst_type"].value_counts().to_dict(),
        "by_county": by_county,
        "county_area_km2": area_lookup,
        "county_population": COUNTY_POP,
        "assignment_method": "county polygon" if any(c.area_km2 > 0 for c in counties) else "bbox",
    }
    with (DATA_PROCESSED / "karst_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
