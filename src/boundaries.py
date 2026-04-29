"""County and municipality boundary helpers for real-data assignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config import COUNTY_BBOX, COUNTY_ZIP, MUNICIPALITY_ZIP
from src.shapefile_utils import (
    bbox_contains,
    point_in_polygon,
    read_zipped_polygon_records,
)

SQMI_TO_KM2 = 2.58999
STUDY_COUNTIES = set(COUNTY_BBOX)


@dataclass
class BoundaryFeature:
    """A named polygon feature used for point-in-polygon assignment."""

    name: str
    county: str
    area_km2: float
    rings: list[list[tuple[float, float]]]
    bbox: tuple[float, float, float, float]


def load_county_boundaries() -> list[BoundaryFeature]:
    """Load study-county polygon boundaries, falling back to configured bboxes."""
    if COUNTY_ZIP.exists():
        features: list[BoundaryFeature] = []
        for record in read_zipped_polygon_records(COUNTY_ZIP):
            county = _county_name(record.attributes.get("COUNTY_NAM"))
            if county in STUDY_COUNTIES:
                features.append(
                    BoundaryFeature(
                        name=county,
                        county=county,
                        area_km2=_area_km2(record.attributes),
                        rings=record.rings,
                        bbox=record.bbox,
                    )
                )
        if features:
            return features

    return [_bbox_feature(county, bbox) for county, bbox in COUNTY_BBOX.items()]


def load_municipal_boundaries() -> list[BoundaryFeature]:
    """Load municipality polygon boundaries for the five-county study area."""
    if not MUNICIPALITY_ZIP.exists():
        return []

    features: list[BoundaryFeature] = []
    for record in read_zipped_polygon_records(MUNICIPALITY_ZIP):
        county = _county_name(record.attributes.get("COUNTY_NAM"))
        if county not in STUDY_COUNTIES:
            continue
        name = _text(record.attributes.get("MUNICIPAL1")) or _text(
            record.attributes.get("MUNICIPAL")
        )
        if not name:
            continue
        features.append(
            BoundaryFeature(
                name=name.title(),
                county=county,
                area_km2=_area_km2(record.attributes),
                rings=record.rings,
                bbox=record.bbox,
            )
        )
    return features


def assign_boundary(
    lon: float, lat: float, boundaries: list[BoundaryFeature]
) -> BoundaryFeature | None:
    """Return the first polygon boundary containing a point."""
    for boundary in boundaries:
        if bbox_contains(lon, lat, boundary.bbox) and point_in_polygon(
            lon, lat, boundary.rings
        ):
            return boundary
    return None


def _bbox_feature(
    county: str, bbox: tuple[float, float, float, float]
) -> BoundaryFeature:
    min_lon, min_lat, max_lon, max_lat = bbox
    ring = [
        (min_lon, min_lat),
        (max_lon, min_lat),
        (max_lon, max_lat),
        (min_lon, max_lat),
        (min_lon, min_lat),
    ]
    return BoundaryFeature(
        name=county,
        county=county,
        area_km2=0.0,
        rings=[ring],
        bbox=bbox,
    )


def _area_km2(attributes: dict[str, Any]) -> float:
    for key in ("AREA_SQ_MI", "FIPS_SQ_MI"):
        value = attributes.get(key)
        if value not in (None, ""):
            try:
                return round(float(value) * SQMI_TO_KM2, 3)
            except (TypeError, ValueError):
                continue
    return 0.0


def _county_name(value: Any) -> str:
    county = _text(value).replace(" County", "")
    return county.title()


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()
