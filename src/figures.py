"""Matplotlib figure generation for the PA karst CATModel."""

from __future__ import annotations

import os
from pathlib import Path

from src.config import BUFFER_ZONES, COUNTY_BBOX, DATA_PROCESSED, OUT_FIGURES, OUT_TABLES

_MPL_CONFIG_DIR = DATA_PROCESSED / ".matplotlib"
_MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CONFIG_DIR))
_FONT_CACHE_DIR = DATA_PROCESSED / ".cache"
_FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(_FONT_CACHE_DIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from scipy.ndimage import gaussian_filter

TERRACOTTA = "#B85042"
SAGE = "#A7BEAE"
SAND = "#E7E8D1"
DARK = "#3A2520"


def make_fig1(karst_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a smoothed karst point-density map."""
    out_path = out_path or OUT_FIGURES / "fig1_karst_density.png"
    fig, ax = plt.subplots(figsize=(10, 7))
    _plot_density(ax, karst_df, alpha=0.95)
    _overlay_counties(ax)
    ax.set_title("Mapped Karst Feature Density", color=DARK, fontsize=16, weight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    _save(fig, out_path)
    return out_path


def make_fig2(
    karst_df: pd.DataFrame, facilities_df: pd.DataFrame, out_path: Path | None = None
) -> Path:
    """Create a facility exposure map over a karst density background."""
    out_path = out_path or OUT_FIGURES / "fig2_facility_exposure.png"
    fig, ax = plt.subplots(figsize=(10, 7))
    _plot_density(ax, karst_df, alpha=0.45)
    _overlay_counties(ax)

    marker_map = {"hospital": "P", "school": "o", "fire_ems": "^", "police": "s"}
    color_map = {
        "100m": TERRACOTTA,
        "250m": "#D98C5F",
        "500m": SAGE,
        "1000m": "#78909C",
        "outside": "#B0BEC5",
    }
    for ftype, marker in marker_map.items():
        subset = facilities_df[facilities_df["type"] == ftype]
        if subset.empty:
            continue
        ax.scatter(
            subset["lon"],
            subset["lat"],
            c=subset["buffer_zone"].map(color_map),
            marker=marker,
            s=32,
            edgecolor=DARK,
            linewidth=0.35,
            label=ftype.replace("_", "/"),
            alpha=0.88,
        )

    ax.set_title("Essential Facilities by Karst Buffer Zone", color=DARK, fontsize=16, weight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left", frameon=True, fontsize=8)
    _save(fig, out_path)
    return out_path


def make_fig3(facilities_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a stacked bar chart of facility exposure by buffer and type."""
    out_path = out_path or OUT_FIGURES / "fig3_exposure_bars.png"
    pivot = (
        facilities_df.pivot_table(
            index="buffer_zone", columns="type", values="fid", aggfunc="count", fill_value=0
        )
        .reindex([zone[1] for zone in BUFFER_ZONES])
        .fillna(0)
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    pivot.plot(kind="bar", stacked=True, ax=ax, color=[TERRACOTTA, SAGE, "#78909C", "#D98C5F"])
    ax.set_title("Facilities by Karst Proximity Buffer", color=DARK, fontsize=15, weight="bold")
    ax.set_xlabel("Nearest mapped karst buffer")
    ax.set_ylabel("Facility count")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Facility type", fontsize=8)
    _save(fig, out_path)
    return out_path


def make_fig4(facilities_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a county summary bar chart for total and exposed facilities."""
    out_path = out_path or OUT_FIGURES / "fig4_county_summary.png"
    summary = facilities_df.groupby("county", sort=False).agg(total=("fid", "count")).reset_index()
    exposed = (
        facilities_df[facilities_df["nearest_karst_m"] <= 500.0]
        .groupby("county")
        .size()
        .rename("exposed")
    )
    summary = summary.merge(exposed, on="county", how="left").fillna({"exposed": 0})
    x = np.arange(len(summary))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(x - width / 2, summary["total"], width=width, color=SAGE, label="Total facilities")
    ax.bar(x + width / 2, summary["exposed"], width=width, color=TERRACOTTA, label="Within 500 m")
    ax.set_xticks(x)
    ax.set_xticklabels(summary["county"], rotation=25, ha="right")
    ax.set_title("County Facility Exposure Summary", color=DARK, fontsize=15, weight="bold")
    ax.set_ylabel("Facility count")
    ax.legend()
    _save(fig, out_path)
    return out_path


def make_fig5(facilities_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a horizontal bar chart for the top 10 facility risk scores."""
    out_path = out_path or OUT_FIGURES / "fig5_top10_facilities.png"
    top10 = facilities_df.sort_values("facility_risk_score", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top10["name"], top10["facility_risk_score"], color=TERRACOTTA)
    ax.invert_yaxis()
    ax.set_title("Top 10 Facility Risk Scores", color=DARK, fontsize=15, weight="bold")
    ax.set_xlabel("Risk score")
    ax.tick_params(axis="y", labelsize=8)
    _save(fig, out_path)
    return out_path


def make_fig6(sensitivity_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a grouped bar chart comparing ranks across KHI schemes."""
    out_path = out_path or OUT_FIGURES / "fig6_sensitivity.png"
    top10 = sensitivity_df.head(10).copy()
    labels = top10["label"].astype(str).str.replace(" cell", "", regex=False)
    x = np.arange(len(top10))
    rank_columns = [column for column in top10.columns if column.startswith("rank_")]
    width = min(0.18, 0.72 / max(len(rank_columns), 1))
    colors = [TERRACOTTA, SAGE, "#78909C", "#C99B3F", "#6D4C41"]

    fig, ax = plt.subplots(figsize=(11, 6))
    start = -0.5 * width * (len(rank_columns) - 1)
    for idx, column in enumerate(rank_columns):
        scheme = column.replace("rank_", "")
        ax.bar(
            x + start + idx * width,
            top10[column],
            width=width,
            color=colors[idx % len(colors)],
            label=scheme,
        )
    ax.invert_yaxis()
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Rank")
    ax.set_title("KHI Rank Sensitivity", color=DARK, fontsize=15, weight="bold")
    ax.legend()
    _save(fig, out_path)
    return out_path


def make_fig7(out_path: Path | None = None) -> Path:
    """Create a methodology flowchart figure."""
    out_path = out_path or OUT_FIGURES / "fig7_flowchart.png"
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.axis("off")
    steps = [
        ("1", "Parse DCNR DBF\nand filter counties"),
        ("2", "Prepare essential\nfacility inventory"),
        ("3", "Nearest karst,\nbuffers, density"),
        ("4", "Aggregate KHI\nand sensitivity"),
        ("5", "Tables, figures,\nfinal PPTX"),
    ]
    x_positions = np.linspace(0.06, 0.82, len(steps))
    for idx, (num, text) in enumerate(steps):
        x = x_positions[idx]
        box = FancyBboxPatch(
            (x, 0.36),
            0.16,
            0.28,
            boxstyle="round,pad=0.02,rounding_size=0.025",
            facecolor=SAND,
            edgecolor=TERRACOTTA,
            linewidth=1.6,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x + 0.02, 0.56, num, color=TERRACOTTA, weight="bold", fontsize=16, transform=ax.transAxes)
        ax.text(x + 0.08, 0.49, text, color=DARK, ha="center", va="center", fontsize=10, transform=ax.transAxes)
        if idx < len(steps) - 1:
            arrow = FancyArrowPatch(
                (x + 0.165, 0.50),
                (x_positions[idx + 1] - 0.01, 0.50),
                arrowstyle="-|>",
                mutation_scale=16,
                color=DARK,
                linewidth=1.2,
                transform=ax.transAxes,
            )
            ax.add_patch(arrow)
    ax.set_title("Reproducible Karst Exposure CATModel Workflow", color=DARK, fontsize=16, weight="bold")
    _save(fig, out_path)
    return out_path


def make_fig8(loss_df: pd.DataFrame, out_path: Path | None = None) -> Path:
    """Create a county scenario loss proxy bar chart."""
    out_path = out_path or OUT_FIGURES / "fig8_loss_proxy.png"
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.bar(loss_df["county"], loss_df["loss_proxy"], color=TERRACOTTA)
    ax.set_title("Relative Scenario Loss Proxy by County", color=DARK, fontsize=15, weight="bold")
    ax.set_ylabel("Relative loss proxy")
    ax.tick_params(axis="x", rotation=25)
    _save(fig, out_path)
    return out_path


def make_all_figures() -> list[Path]:
    """Load processed outputs and generate all eight project figures."""
    OUT_FIGURES.mkdir(parents=True, exist_ok=True)
    karst_df = pd.read_csv(DATA_PROCESSED / "karst_study_area.csv")
    facilities_df = pd.read_csv(DATA_PROCESSED / "facilities_with_exposure.csv")
    sensitivity_df = pd.read_csv(OUT_TABLES / "table5_sensitivity.csv")
    loss_df = pd.read_csv(OUT_TABLES / "table6_loss_proxy.csv")

    return [
        make_fig1(karst_df),
        make_fig2(karst_df, facilities_df),
        make_fig3(facilities_df),
        make_fig4(facilities_df),
        make_fig5(facilities_df),
        make_fig6(sensitivity_df),
        make_fig7(),
        make_fig8(loss_df),
    ]


def _plot_density(ax: plt.Axes, karst_df: pd.DataFrame, alpha: float) -> None:
    min_lon, min_lat, max_lon, max_lat = _study_extent()
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    if karst_df.empty:
        ax.text(0.5, 0.5, "No karst records", transform=ax.transAxes, ha="center", va="center")
        return

    hist, xedges, yedges = np.histogram2d(
        karst_df["lon"],
        karst_df["lat"],
        bins=180,
        range=[[min_lon, max_lon], [min_lat, max_lat]],
    )
    smooth = gaussian_filter(hist.T, sigma=2.0)
    cmap = LinearSegmentedColormap.from_list("warm_karst", [SAND, TERRACOTTA, DARK])
    ax.imshow(
        smooth,
        extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
        origin="lower",
        cmap=cmap,
        alpha=alpha,
        aspect="auto",
    )


def _overlay_counties(ax: plt.Axes) -> None:
    for county, (min_lon, min_lat, max_lon, max_lat) in COUNTY_BBOX.items():
        ax.add_patch(
            Rectangle(
                (min_lon, min_lat),
                max_lon - min_lon,
                max_lat - min_lat,
                fill=False,
                edgecolor=DARK,
                linewidth=1.0,
                alpha=0.8,
            )
        )
        ax.text(min_lon + 0.01, max_lat - 0.02, county, color=DARK, fontsize=8, weight="bold")


def _study_extent() -> tuple[float, float, float, float]:
    boxes = list(COUNTY_BBOX.values())
    min_lon = min(box[0] for box in boxes) - 0.04
    min_lat = min(box[1] for box in boxes) - 0.04
    max_lon = max(box[2] for box in boxes) + 0.04
    max_lat = max(box[3] for box in boxes) + 0.04
    return min_lon, min_lat, max_lon, max_lat


def _save(fig: plt.Figure, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
