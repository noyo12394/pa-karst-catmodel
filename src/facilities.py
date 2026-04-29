"""Essential-facility inventory loading and synthetic fallback generation."""

from __future__ import annotations

import math
import random
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd

from src.boundaries import assign_boundary, load_county_boundaries
from src.config import (
    COUNTY_BBOX,
    DATA_PROCESSED,
    DOH_HOSPITALS_ZIP,
    FACILITY_COUNTS,
    POP_CENTERS,
    RANDOM_SEED,
    STRUCT_POINT_DBF,
    STRUCT_POINT_SHP,
)
from src.geo_utils import assign_county, in_bbox
from src.io_utils import read_dbf
from src.shapefile_utils import read_point_records

SIGMA_KM: dict[str, float] = {
    "hospital": 3.0,
    "police": 4.0,
    "fire_ems": 5.0,
    "school": 6.0,
}

STRUCT_FCODE_TO_TYPE: dict[str, str] = {
    "73002": "school",
    "73003": "school",
    "73004": "school",
    "73005": "school",
    "73006": "school",
    "73007": "school",
    "74001": "fire_ems",
    "74026": "fire_ems",
    "74034": "police",
    "74036": "police",
}


def load_or_generate_facilities(seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Load real facility files when available, otherwise create synthetic points."""
    real_facilities = load_real_facilities()
    if not real_facilities.empty:
        return real_facilities
    return generate_facilities(seed=seed)


def load_real_facilities() -> pd.DataFrame:
    """Load DOH hospitals and USGS structures for the five-county study area."""
    rows: list[dict[str, float | int | str]] = []
    county_boundaries = load_county_boundaries()

    rows.extend(_hospital_rows(county_boundaries))
    rows.extend(_structure_rows(county_boundaries))

    facilities_df = pd.DataFrame(rows)
    if facilities_df.empty:
        return pd.DataFrame(columns=["fid", "name", "type", "county", "lon", "lat"])

    facilities_df = facilities_df.sort_values(["county", "type", "name"]).reset_index(drop=True)
    facilities_df["fid"] = range(1, len(facilities_df) + 1)
    columns = ["fid", "name", "type", "county", "lon", "lat", "source", "source_id", "city"]
    facilities_df = facilities_df.loc[:, columns]

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    facilities_df.to_csv(DATA_PROCESSED / "facilities.csv", index=False)
    return facilities_df


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
                        "source": "screening-grade synthetic fallback",
                        "source_id": f"SYN-{fid}",
                        "city": center_name,
                    }
                )
                fid += 1

    facilities_df = pd.DataFrame(rows)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    facilities_df.to_csv(DATA_PROCESSED / "facilities.csv", index=False)
    return facilities_df


def _hospital_rows(
    county_boundaries: list[Any],
) -> list[dict[str, float | int | str]]:
    if not DOH_HOSPITALS_ZIP.exists():
        return []

    rows: list[dict[str, float | int | str]] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        dbf_path = _extract_first_dbf(DOH_HOSPITALS_ZIP, Path(tmp_dir))
        _, records = read_dbf(dbf_path)

    for index, record in enumerate(records, start=1):
        lon = _float(record.get("LONGITUDE"))
        lat = _float(record.get("LATITUDE"))
        if lon is None or lat is None:
            continue
        county = _clean_county(record.get("COUNTY")) or _assign_county(lon, lat, county_boundaries)
        if county not in COUNTY_BBOX:
            continue
        rows.append(
            {
                "fid": 0,
                "name": _text(record.get("NAME")) or f"Hospital {index}",
                "type": "hospital",
                "county": county,
                "lon": lon,
                "lat": lat,
                "source": "PA DOH Hospitals 2025",
                "source_id": _text(record.get("FACILITYID")) or f"DOH-{index}",
                "city": _text(record.get("CITY")),
            }
        )
    return rows


def _structure_rows(
    county_boundaries: list[Any],
) -> list[dict[str, float | int | str]]:
    if not STRUCT_POINT_SHP.exists() or not STRUCT_POINT_DBF.exists():
        return []

    rows: list[dict[str, float | int | str]] = []
    for index, point in enumerate(read_point_records(STRUCT_POINT_SHP, STRUCT_POINT_DBF), start=1):
        record = point.attributes
        ftype = STRUCT_FCODE_TO_TYPE.get(str(record.get("fcode")))
        if ftype is None:
            continue
        county = _assign_county(point.lon, point.lat, county_boundaries)
        if county not in COUNTY_BBOX:
            continue
        rows.append(
            {
                "fid": 0,
                "name": _text(record.get("name")) or f"USGS Structure {index}",
                "type": ftype,
                "county": county,
                "lon": float(point.lon),
                "lat": float(point.lat),
                "source": "USGS Structures",
                "source_id": str(record.get("permanent_") or record.get("objectid") or index),
                "city": _text(record.get("city")),
            }
        )
    return rows


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


def _assign_county(lon: float, lat: float, county_boundaries: list[Any]) -> str | None:
    boundary = assign_boundary(lon, lat, county_boundaries)
    if boundary is not None:
        return boundary.county
    if not county_boundaries or not any(getattr(item, "area_km2", 0.0) > 0 for item in county_boundaries):
        return assign_county(lon, lat, COUNTY_BBOX)
    return None


def _extract_first_dbf(zip_path: Path, out_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        dbf_name = next(name for name in archive.namelist() if name.lower().endswith(".dbf"))
        archive.extract(dbf_name, out_dir)
    return out_dir / dbf_name


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_county(value: Any) -> str:
    county = _text(value).replace(" County", "").title()
    return county if county in COUNTY_BBOX else ""


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()
