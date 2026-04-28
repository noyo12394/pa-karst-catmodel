"""Facility exposure scoring against mapped karst points."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.config import BUFFER_ZONES, CRITICALITY, DATA_PROCESSED, OUT_TABLES
from src.geo_utils import SpatialGrid, haversine_m


def compute_exposure(karst_df: pd.DataFrame, facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Add nearest-distance, buffer-zone, density, and risk scores to facilities."""
    grid = SpatialGrid(cell_deg=0.01)
    for row in karst_df.itertuples(index=False):
        grid.add(float(row.lon), float(row.lat), getattr(row, "karst_type", "karst"))

    augmented: list[dict[str, Any]] = []
    density_counts: list[int] = []
    for facility in facilities_df.to_dict(orient="records"):
        lon = float(facility["lon"])
        lat = float(facility["lat"])
        nearest_distance, nearest_type = grid.nearest(lon, lat, search_cells=12)
        buffer_zone, proximity_score = _buffer_for_distance(nearest_distance)
        density_count = _count_within(grid, lon, lat, radius_m=1000.0, search_cells=12)
        density_counts.append(density_count)

        facility.update(
            {
                "nearest_karst_m": nearest_distance,
                "nearest_karst_type": nearest_type,
                "buffer_zone": buffer_zone,
                "proximity_score": proximity_score,
                "karst_points_1km": density_count,
                "criticality": CRITICALITY[str(facility["type"])],
            }
        )
        augmented.append(facility)

    out_df = pd.DataFrame(augmented)
    max_density = max(density_counts) if density_counts else 0
    if max_density > 0:
        out_df["density_score"] = out_df["karst_points_1km"] / max_density
    else:
        out_df["density_score"] = 0.0

    out_df["facility_risk_score"] = 100.0 * (
        0.50 * out_df["density_score"]
        + 0.30 * out_df["proximity_score"]
        + 0.20 * out_df["criticality"]
    )
    out_df["nearest_karst_m"] = out_df["nearest_karst_m"].round(2)
    out_df["facility_risk_score"] = out_df["facility_risk_score"].round(2)

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(DATA_PROCESSED / "facilities_with_exposure.csv", index=False)
    return out_df


def summary_tables(facilities_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create and save the three facility exposure summary tables."""
    OUT_TABLES.mkdir(parents=True, exist_ok=True)

    table1 = (
        facilities_df.pivot_table(
            index="buffer_zone", columns="type", values="fid", aggfunc="count", fill_value=0
        )
        .reindex([zone[1] for zone in BUFFER_ZONES])
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    table1["total"] = table1.drop(columns=["buffer_zone"]).sum(axis=1)
    table1.to_csv(OUT_TABLES / "table1_exposure_by_buffer.csv", index=False)

    table2 = (
        facilities_df.sort_values("facility_risk_score", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    table2.to_csv(OUT_TABLES / "table2_top10_facilities.csv", index=False)

    grouped = facilities_df.groupby("county", sort=False)
    table3 = grouped.agg(total=("fid", "count")).reset_index()
    exposed = (
        facilities_df[facilities_df["nearest_karst_m"] <= 500.0]
        .groupby("county")
        .size()
        .rename("exposed_within_500m")
    )
    weighted = (
        facilities_df.assign(
            weighted_exposure=facilities_df["criticality"] * facilities_df["proximity_score"]
        )
        .groupby("county")["weighted_exposure"]
        .sum()
    )
    table3 = table3.merge(exposed, on="county", how="left").merge(weighted, on="county", how="left")
    table3["exposed_within_500m"] = table3["exposed_within_500m"].fillna(0).astype(int)
    table3["weighted_exposure"] = table3["weighted_exposure"].fillna(0.0).round(3)
    table3["pct"] = (100.0 * table3["exposed_within_500m"] / table3["total"]).round(1)
    table3.to_csv(OUT_TABLES / "table3_county_summary.csv", index=False)

    return {
        "exposure_by_buffer": table1,
        "top10_facilities": table2,
        "county_summary": table3,
    }


def _buffer_for_distance(distance_m: float) -> tuple[str, float]:
    for max_meters, label, proximity_score in BUFFER_ZONES:
        if distance_m <= max_meters:
            return label, proximity_score
    return "outside", 0.1


def _count_within(
    grid: SpatialGrid, lon: float, lat: float, radius_m: float, search_cells: int
) -> int:
    count = 0
    for cand_lon, cand_lat, _ in grid.candidates(lon, lat, search_cells):
        if haversine_m(lat, lon, cand_lat, cand_lon) <= radius_m:
            count += 1
    return count
