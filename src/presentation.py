"""PowerPoint slide deck generation for the PA karst CATModel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from src.config import OUT_FIGURES, OUT_PRESENTATION, OUT_TABLES
from src.figures import DARK, SAGE, SAND, TERRACOTTA

WIDE_WIDTH = 13.333
WIDE_HEIGHT = 7.5
COURSE_FOOTER = "Lehigh University CAT402/CEE332 - PA Karst Hazard CATModel"


def add_rect(
    slide: Any,
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    line: str | None = None,
) -> Any:
    """Add a rectangle to a slide using inch coordinates and hex colors."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(fill)
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = _rgb(line)
    return shape


def add_text(
    slide: Any,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    size: int = 18,
    bold: bool = False,
    color: str = DARK,
    align: str = "left",
    anchor: str = "top",
    font: str = "Aptos",
    italic: bool = False,
) -> Any:
    """Add a single styled text box to a slide."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    text_frame = box.text_frame
    text_frame.clear()
    text_frame.word_wrap = True
    text_frame.vertical_anchor = _anchor(anchor)
    paragraph = text_frame.paragraphs[0]
    paragraph.alignment = _align(align)
    run = paragraph.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = _rgb(color)
    return box


def add_multi_text(
    slide: Any,
    x: float,
    y: float,
    w: float,
    h: float,
    lines: list[tuple[str, int, bool, str, bool, int]],
    align: str = "left",
    anchor: str = "top",
    font: str = "Aptos",
) -> Any:
    """Add a multi-paragraph styled text box to a slide."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    text_frame = box.text_frame
    text_frame.clear()
    text_frame.word_wrap = True
    text_frame.vertical_anchor = _anchor(anchor)

    for idx, (text, size, bold, color, italic, space_after) in enumerate(lines):
        paragraph = text_frame.paragraphs[0] if idx == 0 else text_frame.add_paragraph()
        paragraph.alignment = _align(align)
        paragraph.space_after = Pt(space_after)
        run = paragraph.add_run()
        run.text = text
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = _rgb(color)
    return box


def build_presentation(out_path: Path) -> Path:
    """Build and save the 10-slide final project presentation."""
    prs = Presentation()
    prs.slide_width = Inches(WIDE_WIDTH)
    prs.slide_height = Inches(WIDE_HEIGHT)
    blank = prs.slide_layouts[6]

    _slide_cover(prs, blank)
    _slide_intro(prs, blank, 2)
    _slide_method1(prs, blank, 3)
    _slide_method2(prs, blank, 4)
    _slide_workflow(prs, blank, 5)
    _slide_result1(prs, blank, 6)
    _slide_result2(prs, blank, 7)
    _slide_result3(prs, blank, 8)
    _slide_result4(prs, blank, 9)
    _slide_conclusion(prs, blank, 10)

    out_path = OUT_PRESENTATION / "PA_Karst_Final_Presentation.pptx" if out_path is None else out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_path)
    return out_path


def _slide_cover(prs: Presentation, blank: Any) -> None:
    slide = prs.slides.add_slide(blank)
    add_rect(slide, 0, 0, WIDE_WIDTH, WIDE_HEIGHT, DARK)
    add_rect(slide, 0, 6.9, WIDE_WIDTH, 0.6, TERRACOTTA)
    add_multi_text(
        slide,
        0.8,
        1.05,
        9.6,
        2.5,
        [
            ("PA Karst", 38, True, SAND, False, 2),
            ("Hazard", 38, True, SAND, False, 2),
            ("CATModel", 38, True, SAND, False, 8),
        ],
        align="left",
    )
    add_text(slide, 0.85, 4.25, 5.8, 0.35, "Essential-facility exposure in southeastern Pennsylvania", 18, False, SAND)
    add_text(slide, 0.85, 5.0, 5.8, 0.35, "Lehigh University CAT402/CEE332 Final Project", 15, False, SAGE)
    add_text(slide, 0.85, 5.43, 5.8, 0.35, "Prepared by: N. Chatterjee", 15, False, SAGE)


def _slide_intro(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Introduction & Study Area", page)
    stats = [
        ("5", "counties"),
        ("30,623", "karst features"),
        ("1,717", "essential facilities"),
        ("287", "municipalities"),
    ]
    for idx, (value, label) in enumerate(stats):
        x = 0.8 + idx * 3.05
        add_rect(slide, x, 1.25, 2.55, 1.2, SAND, TERRACOTTA)
        add_text(slide, x + 0.18, 1.42, 2.2, 0.4, value, 28, True, TERRACOTTA, "center")
        add_text(slide, x + 0.18, 1.9, 2.2, 0.3, label, 13, False, DARK, "center")
    add_multi_text(
        slide,
        0.9,
        3.0,
        11.3,
        2.7,
        [
            ("Karst terrain creates localized ground-failure susceptibility that can matter disproportionately for hospitals, schools, emergency services, and police facilities.", 20, False, DARK, False, 12),
            ("This project builds a transparent CATModel-style screening workflow using mapped DCNR karst features, PA DOH hospitals, USGS essential structures, proximity buffers, and municipality-scale KHI rankings.", 18, False, DARK, False, 0),
        ],
    )


def _slide_method1(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Methodology I", page)
    add_text(slide, 0.85, 1.15, 5.6, 0.45, "Hazard reframed as susceptibility proxy", 24, True, TERRACOTTA)
    add_multi_text(
        slide,
        0.95,
        1.9,
        5.4,
        4.25,
        [
            ("Mapped karst features are treated as evidence of susceptibility, not as deterministic sinkhole events.", 18, False, DARK, False, 12),
            ("The model avoids polygon overlay dependencies by assigning records to counties with fixed bounding boxes and performing point-based nearest-neighbor searches.", 18, False, DARK, False, 12),
            ("This keeps the pipeline reproducible for classroom use while preserving the exposure logic needed for CATModel framing.", 18, False, DARK, False, 0),
        ],
    )
    add_rect(slide, 7.0, 1.35, 4.8, 4.4, SAND, TERRACOTTA)
    add_text(slide, 7.35, 1.75, 4.1, 0.55, "Susceptibility layer", 23, True, DARK, "center")
    add_text(slide, 7.35, 2.55, 4.1, 1.75, "DCNR mapped karst points\n+\nfacility proximity buffers", 24, True, TERRACOTTA, "center", "middle")
    add_text(slide, 7.35, 4.85, 4.1, 0.55, "screening, not prediction", 16, False, DARK, "center")


def _slide_method2(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Methodology II", page)
    add_text(slide, 0.85, 1.2, 5.9, 0.5, "Karst Hazard Index", 25, True, TERRACOTTA)
    add_text(slide, 0.95, 2.0, 5.7, 0.9, "KHI = 100 * (wH * H + wE * E + wC * C)", 24, True, DARK, "center")
    add_multi_text(
        slide,
        0.95,
        3.25,
        5.7,
        2.2,
        [
            ("H: normalized mapped-karst count", 17, False, DARK, False, 8),
            ("E: normalized exposed-facility count", 17, False, DARK, False, 8),
            ("C: normalized criticality-weighted exposure", 17, False, DARK, False, 0),
        ],
    )
    add_rect(slide, 7.25, 1.35, 4.8, 4.4, SAND, TERRACOTTA)
    add_multi_text(
        slide,
        7.6,
        1.8,
        4.1,
        3.5,
        [
            ("Weighting schemes", 21, True, DARK, False, 16),
            ("Base: 0.40 / 0.40 / 0.20", 16, False, DARK, False, 8),
            ("Hazard-led: 0.60 / 0.25 / 0.15", 16, False, DARK, False, 8),
            ("Exposure-led: 0.25 / 0.60 / 0.15", 16, False, DARK, False, 18),
            ("Framing follows IPCC 2014, Wood et al. USGS, and Reese & Kochanov PAGS.", 13, False, DARK, True, 0),
        ],
    )


def _slide_workflow(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Workflow", page)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig7_flowchart.png", 0.85, 1.35, 11.6, 4.8)


def _slide_result1(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Result I: Karst Density", page)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig1_karst_density.png", 0.65, 1.15, 7.3, 5.6)
    add_multi_text(
        slide,
        8.25,
        1.35,
        4.1,
        4.9,
        [
            ("Key findings", 22, True, TERRACOTTA, False, 14),
            ("Karst features cluster unevenly across the study area.", 17, False, DARK, False, 10),
            ("The density surface is a screening layer for exposure, not a probability surface.", 17, False, DARK, False, 10),
            ("County bounding boxes provide a simple reproducible geography for the final project.", 17, False, DARK, False, 0),
        ],
    )


def _slide_result2(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Result II: Facility Exposure", page)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig2_facility_exposure.png", 0.65, 1.1, 7.5, 5.65)
    summary = _read_table(OUT_TABLES / "table3_county_summary.csv")
    text = _county_summary_text(summary)
    add_multi_text(
        slide,
        8.45,
        1.35,
        3.85,
        4.8,
        [
            ("Exposure summary", 22, True, TERRACOTTA, False, 14),
            (text, 16, False, DARK, False, 0),
        ],
    )


def _slide_result3(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Result III: Facility Risk", page)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig5_top10_facilities.png", 0.55, 1.15, 6.25, 5.25)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig4_county_summary.png", 6.95, 1.15, 5.8, 5.25)


def _slide_result4(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Result IV: KHI Sensitivity", page)
    _add_picture_or_placeholder(slide, OUT_FIGURES / "fig6_sensitivity.png", 0.55, 1.15, 7.4, 4.9)
    top5 = _top5_munis()
    add_multi_text(
        slide,
        8.25,
        1.25,
        4.25,
        5.35,
        [
            ("Top 5 Base KHI", 21, True, TERRACOTTA, False, 10),
            (top5, 14, False, DARK, False, 14),
            ("Uncertainty", 18, True, TERRACOTTA, False, 8),
            ("Rank sensitivity indicates whether priority cells are robust to alternative hazard-led or exposure-led assumptions.", 14, False, DARK, False, 0),
        ],
    )


def _slide_conclusion(prs: Presentation, blank: Any, page: int) -> None:
    slide = _content_slide(prs, blank, "Conclusion", page)
    columns = [
        ("CATModel takeaways", "A lightweight hazard, exposure, and criticality workflow can identify where karst screening deserves closer engineering attention."),
        ("Limitations", "Mapped karst is a susceptibility proxy, public facility coordinates require QA, and no fragility curves or service disruption model are included."),
        ("Future work", "Add facility QA, service-area geometry, geotechnical covariates, and calibrated event likelihood or damage functions."),
    ]
    for idx, (title, body) in enumerate(columns):
        x = 0.75 + idx * 4.18
        add_rect(slide, x, 1.35, 3.55, 4.85, SAND, TERRACOTTA)
        add_text(slide, x + 0.25, 1.75, 3.05, 0.55, title, 19, True, TERRACOTTA, "center")
        add_text(slide, x + 0.35, 2.65, 2.85, 2.8, body, 15, False, DARK, "center", "middle")


def _content_slide(prs: Presentation, blank: Any, title: str, page: int) -> Any:
    slide = prs.slides.add_slide(blank)
    add_rect(slide, 0, 0, WIDE_WIDTH, WIDE_HEIGHT, "FFFFFF")
    add_rect(slide, 0, 0, WIDE_WIDTH, 0.22, TERRACOTTA)
    add_text(slide, 0.65, 0.42, 9.5, 0.45, title, 24, True, DARK)
    _footer(slide, page)
    return slide


def _footer(slide: Any, page: int) -> None:
    add_rect(slide, 0, 7.12, WIDE_WIDTH, 0.38, SAND)
    add_text(slide, 0.55, 7.18, 9.5, 0.2, COURSE_FOOTER, 8, False, DARK)
    add_text(slide, 12.2, 7.18, 0.6, 0.2, str(page), 8, False, DARK, "right")


def _add_picture_or_placeholder(
    slide: Any, path: Path, x: float, y: float, w: float, h: float
) -> None:
    if path.exists():
        slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
    else:
        add_rect(slide, x, y, w, h, SAND, TERRACOTTA)
        add_text(slide, x + 0.25, y + h / 2 - 0.2, w - 0.5, 0.4, path.name, 15, True, DARK, "center")


def _read_table(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _county_summary_text(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "Run the pipeline to populate county exposure summaries."
    parts = []
    for row in summary.itertuples(index=False):
        parts.append(f"{row.county}: {int(row.exposed_within_500m)} of {int(row.total)} within 500 m")
    return "\n".join(parts)


def _top5_munis() -> str:
    table = _read_table(OUT_TABLES / "table4_top15_munis_KHI.csv")
    if table.empty:
        return "Run the pipeline to populate KHI rankings."
    lines = []
    for idx, row in enumerate(table.head(5).itertuples(index=False), start=1):
        lines.append(f"{idx}. {row.label}: {row.KHI_Base:.1f}")
    return "\n".join(lines)


def _align(value: str) -> PP_ALIGN:
    return {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }.get(value, PP_ALIGN.LEFT)


def _anchor(value: str) -> MSO_ANCHOR:
    return {
        "top": MSO_ANCHOR.TOP,
        "middle": MSO_ANCHOR.MIDDLE,
        "bottom": MSO_ANCHOR.BOTTOM,
    }.get(value, MSO_ANCHOR.TOP)


def _rgb(hex_color: str) -> RGBColor:
    color = hex_color.lstrip("#")
    return RGBColor(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
