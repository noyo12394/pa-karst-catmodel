"""Minimal pure-Python shapefile readers used by the CATModel pipeline."""

from __future__ import annotations

import math
import struct
import tempfile
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.io_utils import read_dbf

WEB_MERCATOR_RADIUS_M = 6_378_137.0


@dataclass
class PointRecord:
    """A point geometry paired with DBF attributes."""

    lon: float
    lat: float
    attributes: dict[str, Any]


@dataclass
class PolygonRecord:
    """A polygon or multipolygon geometry paired with DBF attributes."""

    rings: list[list[tuple[float, float]]]
    attributes: dict[str, Any]
    bbox: tuple[float, float, float, float]


def web_mercator_to_lonlat(x: float, y: float) -> tuple[float, float]:
    """Convert EPSG:3857/Web Mercator coordinates to longitude/latitude."""
    lon = math.degrees(x / WEB_MERCATOR_RADIUS_M)
    lat = math.degrees(2.0 * math.atan(math.exp(y / WEB_MERCATOR_RADIUS_M)) - math.pi / 2.0)
    return lon, lat


def read_point_records(shp_path: Path, dbf_path: Path) -> list[PointRecord]:
    """Read point shapefile records and pair each point with its DBF row."""
    _, dbf_records = read_dbf(dbf_path)
    points = _read_point_geometries(shp_path)
    return [
        PointRecord(lon=lon, lat=lat, attributes=attributes)
        for (lon, lat), attributes in zip(points, dbf_records)
        if lon is not None and lat is not None
    ]


def read_zipped_polygon_records(zip_path: Path) -> list[PolygonRecord]:
    """Read polygon records from a zipped shapefile archive."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        shp_path, dbf_path = _extract_shapefile_pair(zip_path, Path(tmp_dir))
        return read_polygon_records(shp_path, dbf_path)


def read_polygon_records(shp_path: Path, dbf_path: Path) -> list[PolygonRecord]:
    """Read polygon shapefile records and pair each geometry with its DBF row."""
    _, dbf_records = read_dbf(dbf_path)
    polygons = _read_polygon_geometries(shp_path, transform=_auto_lonlat)
    return [
        PolygonRecord(rings=rings, attributes=attributes, bbox=polygon_bbox(rings))
        for rings, attributes in zip(polygons, dbf_records)
        if rings
    ]


def point_in_polygon(lon: float, lat: float, rings: list[list[tuple[float, float]]]) -> bool:
    """Return True when a point is inside a shapefile polygon using parity fill."""
    inside = False
    for ring in rings:
        if bbox_contains(lon, lat, ring_bbox(ring)) and _point_in_ring(lon, lat, ring):
            inside = not inside
    return inside


def bbox_contains(lon: float, lat: float, bbox: tuple[float, float, float, float]) -> bool:
    """Return True when a point falls within a longitude/latitude bounding box."""
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def ring_bbox(ring: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    """Return the bounding box for a single polygon ring."""
    lons = [point[0] for point in ring]
    lats = [point[1] for point in ring]
    return min(lons), min(lats), max(lons), max(lats)


def polygon_bbox(rings: list[list[tuple[float, float]]]) -> tuple[float, float, float, float]:
    """Return the bounding box for all rings in a polygon record."""
    lons = [point[0] for ring in rings for point in ring]
    lats = [point[1] for ring in rings for point in ring]
    return min(lons), min(lats), max(lons), max(lats)


def _read_point_geometries(shp_path: Path) -> list[tuple[float | None, float | None]]:
    points: list[tuple[float | None, float | None]] = []
    with shp_path.open("rb") as handle:
        handle.read(100)
        while True:
            record_header = handle.read(8)
            if len(record_header) < 8:
                break
            _, content_words = struct.unpack(">2i", record_header)
            content = handle.read(content_words * 2)
            if len(content) < 4:
                continue
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type in {1, 11, 21} and len(content) >= 20:
                points.append(struct.unpack("<2d", content[4:20]))
            else:
                points.append((None, None))
    return points


def _read_polygon_geometries(
    shp_path: Path, transform: Callable[[float, float], tuple[float, float]]
) -> list[list[list[tuple[float, float]]]]:
    polygons: list[list[list[tuple[float, float]]]] = []
    with shp_path.open("rb") as handle:
        handle.read(100)
        while True:
            record_header = handle.read(8)
            if len(record_header) < 8:
                break
            _, content_words = struct.unpack(">2i", record_header)
            content = handle.read(content_words * 2)
            if len(content) < 44:
                polygons.append([])
                continue
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type not in {5, 15, 25}:
                polygons.append([])
                continue
            num_parts, num_points = struct.unpack("<2i", content[36:44])
            part_offset = 44
            point_offset = part_offset + 4 * num_parts
            parts = list(struct.unpack(f"<{num_parts}i", content[part_offset:point_offset]))
            points = [
                transform(*struct.unpack("<2d", content[point_offset + i * 16 : point_offset + i * 16 + 16]))
                for i in range(num_points)
            ]
            rings: list[list[tuple[float, float]]] = []
            for index, start in enumerate(parts):
                end = parts[index + 1] if index + 1 < len(parts) else num_points
                ring = points[start:end]
                if len(ring) >= 3:
                    rings.append(ring)
            polygons.append(rings)
    return polygons


def _auto_lonlat(x: float, y: float) -> tuple[float, float]:
    if abs(x) <= 180.0 and abs(y) <= 90.0:
        return x, y
    return web_mercator_to_lonlat(x, y)


def _point_in_ring(lon: float, lat: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    prev_lon, prev_lat = ring[-1]
    for curr_lon, curr_lat in ring:
        if (curr_lat > lat) != (prev_lat > lat):
            intersect_lon = (prev_lon - curr_lon) * (lat - curr_lat) / (
                prev_lat - curr_lat + 1e-30
            ) + curr_lon
            if lon < intersect_lon:
                inside = not inside
        prev_lon, prev_lat = curr_lon, curr_lat
    return inside


def _extract_shapefile_pair(zip_path: Path, out_dir: Path) -> tuple[Path, Path]:
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        shp_name = _first_suffix(names, ".shp")
        dbf_name = _first_suffix(names, ".dbf")
        archive.extract(shp_name, out_dir)
        archive.extract(dbf_name, out_dir)
    return out_dir / shp_name, out_dir / dbf_name


def _first_suffix(names: list[str], suffix: str) -> str:
    for name in names:
        if name.lower().endswith(suffix):
            return name
    raise FileNotFoundError(f"Archive is missing a {suffix} member")
