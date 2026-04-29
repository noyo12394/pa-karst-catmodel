"""Karst Hazard Index aggregation, sensitivity, and loss proxy."""

from __future__ import annotations

from itertools import combinations
from typing import Any

import pandas as pd
from scipy.stats import spearmanr

from src.boundaries import BoundaryFeature, assign_boundary, load_municipal_boundaries
from src.config import (
    CRITICALITY,
    DATA_PROCESSED,
    DAMAGE_RATIO,
    KHI_SCHEMES,
    OUT_TABLES,
    POP_CENTERS,
    REPL_VAL,
)
from src.geo_utils import haversine_m


def compute_khi(karst_df: pd.DataFrame, facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Compute municipality-cell Karst Hazard Index scores under all schemes."""
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    municipal_boundaries = load_municipal_boundaries()
    if municipal_boundaries:
        return _compute_boundary_khi(karst_df, facilities_df, municipal_boundaries)

    return _compute_grid_khi(karst_df, facilities_df)


def _compute_boundary_khi(
    karst_df: pd.DataFrame,
    facilities_df: pd.DataFrame,
    municipal_boundaries: list[BoundaryFeature],
) -> pd.DataFrame:
    by_county = _boundaries_by_county(municipal_boundaries)

    karst_rows: list[dict[str, Any]] = []
    for row in karst_df.itertuples(index=False):
        county = _row_value(row, "county")
        boundary = _boundary_for_point(float(row.lon), float(row.lat), county, by_county)
        if boundary is None:
            continue
        karst_rows.append(
            {
                "county": boundary.county,
                "label": boundary.name,
                "area_km2": boundary.area_km2,
            }
        )

    facilities = facilities_df.copy()
    assigned_rows: list[dict[str, Any]] = []
    for row in facilities.itertuples(index=False):
        county = _row_value(row, "county")
        boundary = _boundary_for_point(float(row.lon), float(row.lat), county, by_county)
        if boundary is None:
            continue
        row_dict = row._asdict()
        row_dict["county"] = boundary.county
        row_dict["label"] = boundary.name
        row_dict["area_km2"] = boundary.area_km2
        assigned_rows.append(row_dict)

    assigned = pd.DataFrame(assigned_rows)
    if assigned.empty:
        return _compute_grid_khi(karst_df, facilities_df)

    karst_counts = (
        pd.DataFrame(karst_rows)
        .groupby(["county", "label", "area_km2"])
        .size()
        .rename("karst_count")
        .reset_index()
        if karst_rows
        else pd.DataFrame(columns=["county", "label", "area_km2", "karst_count"])
    )

    assigned["is_exposed"] = assigned["nearest_karst_m"] <= 500.0
    assigned["is_exposed_1km"] = assigned["nearest_karst_m"] <= 1000.0
    assigned["criticality_weighted_exposure"] = (
        assigned["type"].map(CRITICALITY) * assigned["proximity_score"]
    )
    facility_counts = (
        assigned.groupby(["county", "label", "area_km2"])
        .agg(
            facility_count=("fid", "count"),
            exposed_count=("is_exposed", "sum"),
            exposed_1km=("is_exposed_1km", "sum"),
            criticality_weighted_exposure=("criticality_weighted_exposure", "sum"),
        )
        .reset_index()
    )

    muni_df = facility_counts.merge(
        karst_counts,
        on=["county", "label", "area_km2"],
        how="left",
    )
    muni_df["karst_count"] = muni_df["karst_count"].fillna(0).astype(int)
    muni_df["karst_density_km2"] = (
        muni_df["karst_count"] / muni_df["area_km2"].replace(0, pd.NA)
    ).fillna(0.0)
    muni_df["assignment_method"] = "municipality polygon"

    _add_khi_scores(muni_df, hazard_column="karst_density_km2")
    muni_df.to_csv(DATA_PROCESSED / "municipality_khi.csv", index=False)

    table4 = (
        muni_df.sort_values("KHI_Base", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )
    table4.to_csv(OUT_TABLES / "table4_top15_munis_KHI.csv", index=False)
    return muni_df


def _compute_grid_khi(karst_df: pd.DataFrame, facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Compute KHI with the original coarse grid fallback."""
    karst = karst_df.copy()
    facilities = facilities_df.copy()

    if karst.empty:
        karst["cell_lon"] = pd.Series(dtype=float)
        karst["cell_lat"] = pd.Series(dtype=float)
    else:
        karst[["cell_lon", "cell_lat"]] = karst.apply(
            lambda row: pd.Series(muni_cell(float(row["lon"]), float(row["lat"]))), axis=1
        )

    if facilities.empty:
        facilities["cell_lon"] = pd.Series(dtype=float)
        facilities["cell_lat"] = pd.Series(dtype=float)
    else:
        facilities[["cell_lon", "cell_lat"]] = facilities.apply(
            lambda row: pd.Series(muni_cell(float(row["lon"]), float(row["lat"]))), axis=1
        )

    karst_counts = (
        karst.groupby(["cell_lon", "cell_lat"]).size().rename("karst_count").reset_index()
        if not karst.empty
        else pd.DataFrame(columns=["cell_lon", "cell_lat", "karst_count"])
    )

    facilities["is_exposed"] = facilities["nearest_karst_m"] <= 500.0
    facilities["criticality_weighted_exposure"] = (
        facilities["type"].map(CRITICALITY) * facilities["proximity_score"]
    )
    facility_counts = (
        facilities.groupby(["cell_lon", "cell_lat", "county"])
        .agg(
            facility_count=("fid", "count"),
            exposed_count=("is_exposed", "sum"),
            criticality_weighted_exposure=("criticality_weighted_exposure", "sum"),
        )
        .reset_index()
    )

    muni_df = facility_counts.merge(karst_counts, on=["cell_lon", "cell_lat"], how="left")
    muni_df["karst_count"] = muni_df["karst_count"].fillna(0).astype(int)

    muni_df["karst_density_km2"] = muni_df["karst_count"].astype(float)
    muni_df["assignment_method"] = "coarse grid fallback"
    _add_khi_scores(muni_df, hazard_column="karst_count")

    muni_df["label"] = [
        _nearest_pop_center(str(row.county), float(row.cell_lon), float(row.cell_lat))
        for row in muni_df.itertuples(index=False)
    ]

    table4 = (
        muni_df.sort_values("KHI_Base", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )
    table4.to_csv(OUT_TABLES / "table4_top15_munis_KHI.csv", index=False)
    return muni_df


def muni_cell(lon: float, lat: float) -> tuple[float, float]:
    """Map a longitude/latitude point to a coarse municipality-like grid cell."""
    return (round(lon / 0.06) * 0.06, round(lat / 0.05) * 0.05)


def sensitivity_analysis(muni_df: pd.DataFrame) -> dict[str, Any]:
    """Compute rank changes and Spearman correlations among KHI schemes."""
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    ranked = muni_df.copy()
    for scheme in KHI_SCHEMES:
        ranked[f"rank_{scheme}"] = ranked[f"KHI_{scheme}"].rank(
            ascending=False, method="min"
        ).astype(int)

    top50 = ranked.nsmallest(min(50, len(ranked)), "rank_Base")
    correlations: dict[str, float] = {}
    for left, right in combinations(KHI_SCHEMES.keys(), 2):
        if len(top50) < 2:
            corr = float("nan")
        else:
            corr = float(spearmanr(top50[f"rank_{left}"], top50[f"rank_{right}"]).correlation)
        correlations[f"{left} vs {right}"] = corr

    correlation_table = pd.DataFrame(
        [
            {"scheme_pair": pair, "spearman_top50": round(value, 3)}
            for pair, value in correlations.items()
        ]
    )
    correlation_table.to_csv(OUT_TABLES / "table5_sensitivity_correlations.csv", index=False)

    rank_columns = [f"rank_{scheme}" for scheme in KHI_SCHEMES]
    table_columns = ["label", "county", "KHI_Base", *rank_columns]
    table5 = ranked.sort_values("KHI_Base", ascending=False).head(15).loc[:, table_columns].copy()
    for scheme in KHI_SCHEMES:
        if scheme != "Base":
            table5[f"delta_{scheme}"] = table5[f"rank_{scheme}"] - table5["rank_Base"]
    table5.to_csv(OUT_TABLES / "table5_sensitivity.csv", index=False)

    return {"correlations": correlations, "rank_table": table5}


def loss_proxy(facilities_df: pd.DataFrame) -> pd.DataFrame:
    """Compute a relative scenario loss proxy by county."""
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    loss_df = facilities_df.copy()
    loss_df["loss_proxy"] = loss_df.apply(
        lambda row: REPL_VAL[str(row["type"])] * DAMAGE_RATIO[str(row["buffer_zone"])],
        axis=1,
    )
    table6 = (
        loss_df.groupby("county", sort=False)["loss_proxy"]
        .sum()
        .round(3)
        .reset_index()
        .sort_values("loss_proxy", ascending=False)
    )
    table6.to_csv(OUT_TABLES / "table6_loss_proxy.csv", index=False)
    return table6


def _normalize(series: pd.Series) -> pd.Series:
    max_value = float(series.max()) if len(series) else 0.0
    if max_value <= 0.0:
        return pd.Series([0.0] * len(series), index=series.index)
    return series.astype(float) / max_value


def _add_khi_scores(muni_df: pd.DataFrame, hazard_column: str) -> None:
    muni_df["H_norm"] = _normalize(muni_df[hazard_column])
    muni_df["E_norm"] = _normalize(muni_df["exposed_count"])
    muni_df["C_norm"] = _normalize(muni_df["criticality_weighted_exposure"])

    for scheme, (h_weight, e_weight, c_weight) in KHI_SCHEMES.items():
        muni_df[f"KHI_{scheme}"] = 100.0 * (
            h_weight * muni_df["H_norm"]
            + e_weight * muni_df["E_norm"]
            + c_weight * muni_df["C_norm"]
        )
        muni_df[f"KHI_{scheme}"] = muni_df[f"KHI_{scheme}"].round(2)


def _boundaries_by_county(
    boundaries: list[BoundaryFeature],
) -> dict[str, list[BoundaryFeature]]:
    grouped: dict[str, list[BoundaryFeature]] = {}
    for boundary in boundaries:
        grouped.setdefault(boundary.county, []).append(boundary)
    return grouped


def _boundary_for_point(
    lon: float,
    lat: float,
    county: str,
    by_county: dict[str, list[BoundaryFeature]],
) -> BoundaryFeature | None:
    if county in by_county:
        boundary = assign_boundary(lon, lat, by_county[county])
        if boundary is not None:
            return boundary
    for candidates in by_county.values():
        boundary = assign_boundary(lon, lat, candidates)
        if boundary is not None:
            return boundary
    return None


def _row_value(row: Any, field: str) -> str:
    value = getattr(row, field, "")
    if pd.isna(value):
        return ""
    return str(value)


def _nearest_pop_center(county: str, lon: float, lat: float) -> str:
    centers = POP_CENTERS.get(county, [])
    if not centers:
        return f"Cell {lon:.2f}, {lat:.2f}"
    best_name = min(
        centers,
        key=lambda center: haversine_m(lat, lon, center[1], center[0]),
    )[2]
    return f"{best_name} cell ({lon:.2f}, {lat:.2f})"
