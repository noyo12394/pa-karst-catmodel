"""Project constants, paths, study-area metadata, and model weights."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
DATA_RAW: Path = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED: Path = PROJECT_ROOT / "data" / "processed"
OUT_FIGURES: Path = PROJECT_ROOT / "outputs" / "figures"
OUT_TABLES: Path = PROJECT_ROOT / "outputs" / "tables"
OUT_PRESENTATION: Path = PROJECT_ROOT / "outputs" / "presentation"

KARST_DBF_CANDIDATES: tuple[Path, ...] = (
    DATA_RAW / "DCNR_PAKarst.dbf",
    DATA_RAW / "DCNR_PAKarst" / "DCNR_PAKarst.dbf",
)
COUNTY_ZIP: Path = DATA_RAW / "PaCounty2026_01.zip"
MUNICIPALITY_ZIP: Path = DATA_RAW / "PaMunicipalities2026_01.zip"
DOH_HOSPITALS_ZIP: Path = DATA_RAW / "DOH_Hospitals202511.zip"
STRUCT_POINT_SHP: Path = (
    DATA_RAW / "STRUCT_Pennsylvania_State_Shape" / "Shape" / "Struct_Point.shp"
)
STRUCT_POINT_DBF: Path = (
    DATA_RAW / "STRUCT_Pennsylvania_State_Shape" / "Shape" / "Struct_Point.dbf"
)

COUNTY_BBOX: dict[str, tuple[float, float, float, float]] = {
    "Lehigh": (-75.840, 40.402, -75.354, 40.789),
    "Berks": (-76.246, 40.197, -75.604, 40.581),
    "Bucks": (-75.477, 40.118, -74.694, 40.609),
    "Montgomery": (-75.694, 40.080, -75.090, 40.451),
    "Chester": (-76.058, 39.720, -75.420, 40.262),
}

COUNTY_AREA_KM2: dict[str, int] = {
    "Lehigh": 906,
    "Berks": 2261,
    "Bucks": 1597,
    "Montgomery": 1265,
    "Chester": 1944,
}

COUNTY_POP: dict[str, int] = {
    "Lehigh": 374557,
    "Berks": 428849,
    "Bucks": 646538,
    "Montgomery": 856553,
    "Chester": 545823,
}

POP_CENTERS: dict[str, list[tuple[float, float, str, float]]] = {
    "Lehigh": [
        (-75.490, 40.602, "Allentown", 0.55),
        (-75.371, 40.601, "Bethlehem", 0.20),
        (-75.620, 40.640, "Schnecksville", 0.10),
        (-75.490, 40.430, "Emmaus", 0.15),
    ],
    "Berks": [
        (-75.926, 40.336, "Reading", 0.50),
        (-75.778, 40.474, "Leesport", 0.10),
        (-75.803, 40.560, "Hamburg", 0.10),
        (-76.004, 40.211, "Wernersville", 0.10),
        (-75.717, 40.330, "Boyertown", 0.20),
    ],
    "Bucks": [
        (-75.130, 40.310, "Doylestown", 0.30),
        (-74.990, 40.150, "Bristol", 0.20),
        (-75.183, 40.224, "Warrington", 0.15),
        (-75.343, 40.443, "Quakertown", 0.20),
        (-75.080, 40.176, "Levittown", 0.15),
    ],
    "Montgomery": [
        (-75.340, 40.115, "Norristown", 0.30),
        (-75.290, 40.142, "King of Prussia", 0.20),
        (-75.122, 40.121, "Abington", 0.15),
        (-75.246, 40.245, "Lansdale", 0.15),
        (-75.648, 40.243, "Pottstown", 0.20),
    ],
    "Chester": [
        (-75.605, 39.961, "West Chester", 0.30),
        (-75.520, 40.137, "Phoenixville", 0.20),
        (-75.802, 39.971, "Coatesville", 0.20),
        (-75.678, 39.870, "Kennett Square", 0.15),
        (-75.826, 40.146, "Downingtown", 0.15),
    ],
}

FACILITY_COUNTS: dict[str, dict[str, int]] = {
    "Lehigh": {"hospital": 6, "school": 75, "fire_ems": 38, "police": 14},
    "Berks": {"hospital": 4, "school": 97, "fire_ems": 72, "police": 28},
    "Bucks": {"hospital": 7, "school": 110, "fire_ems": 65, "police": 35},
    "Montgomery": {"hospital": 9, "school": 160, "fire_ems": 88, "police": 42},
    "Chester": {"hospital": 5, "school": 92, "fire_ems": 70, "police": 30},
}

CRITICALITY: dict[str, float] = {
    "hospital": 1.00,
    "fire_ems": 0.90,
    "police": 0.85,
    "school": 0.70,
}

BUFFER_ZONES: list[tuple[float, str, float]] = [
    (100, "100m", 1.0),
    (250, "250m", 0.7),
    (500, "500m", 0.4),
    (1000, "1000m", 0.2),
    (float("inf"), "outside", 0.1),
]

KHI_SCHEMES: dict[str, tuple[float, float, float]] = {
    "Base": (0.40, 0.40, 0.20),
    "Hazard-led": (0.60, 0.25, 0.15),
    "Exposure-led": (0.25, 0.60, 0.15),
    "Critical-facility": (0.30, 0.35, 0.35),
}

DAMAGE_RATIO: dict[str, float] = {
    "100m": 0.30,
    "250m": 0.15,
    "500m": 0.05,
    "1000m": 0.01,
    "outside": 0.0,
}

REPL_VAL: dict[str, float] = {
    "hospital": 1.00,
    "fire_ems": 0.70,
    "police": 0.65,
    "school": 0.60,
}

RANDOM_SEED: int = 42
