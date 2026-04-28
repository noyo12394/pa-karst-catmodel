"""Synthetic essential-facility inventory generation."""

from __future__ import annotations

import math
import random

import pandas as pd

from src.config import (
    COUNTY_BBOX,
    DATA_PROCESSED,
    FACILITY_COUNTS,
    POP_CENTERS,
    RANDOM_SEED,
)
from src.geo_utils import in_bbox

SIGMA_KM: dict[str, float] = {
    "hospital": 3.0,
    "police": 4.0,
    "fire_ems": 5.0,
    "school": 6.0,
}


def generate_facilities(seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Generate fixed-seed synthetic essential-facility points."""
    random.seed(seed)
    rows: list[dict[str, float | int | str]] = []
    fid = 1

    for county, facility_counts in FACILITY_COUNTS.items():
        centers = POP_CENTERS[county]
        weights = [center[3] for center in centers]
        for ftype, count in facility_counts.items():
            sigma_km = SIGMA_KM[ftype]
            for i in range(count):
                center_lon, center_lat, center_name, _ = random.choices(
                    centers, weights=weights, k=1
                )[0]
                lon, lat = _jitter_within_county(center_lon, center_lat, sigma_km, county)
                rows.append(
                    {
                        "fid": fid,
                        "name": f"{center_name} {ftype.replace('_', '/')} #{i + 1}",
                        "type": ftype,
                        "county": county,
                        "lon": lon,
                        "lat": lat,
                    }
                )
                fid += 1

    facilities_df = pd.DataFrame(rows)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    facilities_df.to_csv(DATA_PROCESSED / "facilities.csv", index=False)
    return facilities_df


def _jitter_within_county(
    center_lon: float, center_lat: float, sigma_km: float, county: str
) -> tuple[float, float]:
    bbox = COUNTY_BBOX[county]
    for _ in range(100):
        dlat = random.gauss(0.0, sigma_km / 111.0)
        cos_lat = max(math.cos(math.radians(center_lat)), 0.1)
        dlon = random.gauss(0.0, sigma_km / (111.0 * cos_lat))
        lon = center_lon + dlon
        lat = center_lat + dlat
        if in_bbox(lon, lat, bbox):
            return lon, lat

    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        min(max(center_lon, min_lon), max_lon),
        min(max(center_lat, min_lat), max_lat),
    )
