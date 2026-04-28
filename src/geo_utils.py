"""Geographic utility functions and a small grid index."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

EARTH_RADIUS_M = 6_371_000.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two WGS84 points in meters."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lam = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def in_bbox(lon: float, lat: float, bbox: tuple[float, float, float, float]) -> bool:
    """Return True when a longitude/latitude point is inside a bounding box."""
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def assign_county(
    lon: float, lat: float, county_bboxes: dict[str, tuple[float, float, float, float]]
) -> str | None:
    """Assign a point to the first county bounding box that contains it."""
    for county, bbox in county_bboxes.items():
        if in_bbox(lon, lat, bbox):
            return county
    return None


class SpatialGrid:
    """Simple longitude/latitude grid index for nearest-neighbor lookups."""

    def __init__(self, cell_deg: float = 0.01) -> None:
        """Create an empty grid index with square cells measured in degrees."""
        self.cell_deg = cell_deg
        self._cells: dict[tuple[int, int], list[tuple[float, float, Any]]] = defaultdict(list)

    def add(self, lon: float, lat: float, payload: Any) -> None:
        """Add a point and its payload to the grid."""
        self._cells[self._cell(lon, lat)].append((lon, lat, payload))

    def nearest(self, lon: float, lat: float, search_cells: int = 6) -> tuple[float, Any]:
        """Return the nearest indexed payload as a ``(distance_m, payload)`` tuple."""
        best_distance = float("inf")
        best_payload: Any = None
        for cand_lon, cand_lat, payload in self.candidates(lon, lat, search_cells):
            distance = haversine_m(lat, lon, cand_lat, cand_lon)
            if distance < best_distance:
                best_distance = distance
                best_payload = payload
        return best_distance, best_payload

    def candidates(
        self, lon: float, lat: float, search_cells: int = 6
    ) -> list[tuple[float, float, Any]]:
        """Return candidate points from neighboring grid cells."""
        center_x, center_y = self._cell(lon, lat)
        candidates: list[tuple[float, float, Any]] = []
        for dx in range(-search_cells, search_cells + 1):
            for dy in range(-search_cells, search_cells + 1):
                candidates.extend(self._cells.get((center_x + dx, center_y + dy), []))
        return candidates

    def _cell(self, lon: float, lat: float) -> tuple[int, int]:
        return (math.floor(lon / self.cell_deg), math.floor(lat / self.cell_deg))
