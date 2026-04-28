# PA Karst Hazard CATModel

One-line description: a reproducible Python CATModel pipeline that estimates essential-facility exposure to mapped karst features in Lehigh, Berks, Bucks, Montgomery, and Chester Counties, Pennsylvania.

## Quickstart

```bash
git clone <repo-url>
cd pa-karst-catmodel
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the PASDA/DCNR karst shapefile files in `data/raw/`, including `DCNR_PAKarst.dbf`, then run:

```bash
python scripts/run_all.py
```

The pipeline writes processed CSVs to `data/processed/`, result tables to `outputs/tables/`, figures to `outputs/figures/`, and the final slide deck to `outputs/presentation/PA_Karst_Final_Presentation.pptx`.

## Dashboard and Vercel

This repository includes a static project hub in `dashboard/` for web presentation of the final PDF/PPT results, literature context, methodology, interactive exposure/KHI views, scenario testing, and project outputs. Build it locally with:

```bash
npm run build
```

The Vercel deployment uses `vercel.json` to run the dashboard build and serve the generated `dist/` directory. Deploy directly to production with:

```bash
vercel --prod --yes
```

## Directory Structure

```text
pa-karst-catmodel/
├── data/
│   ├── raw/          # input shapefiles, gitignored
│   └── processed/    # cleaned intermediate CSVs, gitignored
├── outputs/
│   ├── figures/      # PNG charts and maps
│   ├── tables/       # CSV result tables
│   └── presentation/ # final PPTX
├── scripts/          # runnable pipeline steps
├── dashboard/        # static web dashboard for Vercel
├── src/              # model source code
└── tests/            # pytest unit tests
```

## Methodology Summary

This project reframes mapped karst as a susceptibility proxy rather than a deterministic sinkhole forecast. The final result set uses 30,623 mapped karst features from the PASDA/DCNR Pennsylvania Karst Inventory clipped to Lehigh, Berks, Bucks, Montgomery, and Chester Counties. Those features are summarized by county, feature type, and local density to show where mapped carbonate-related ground-failure susceptibility is spatially concentrated.

Essential-facility exposure is calculated from 42 PA Department of Health hospital points and 1,675 USGS National Map essential-structure points. Each facility is scored by nearest mapped karst distance, buffer class, local karst density within 1 km, and facility criticality. The 100 m, 250 m, 500 m, and 1 km screening bands are used as planning-level proximity classes rather than direct damage states.

The Karst Hazard Index (KHI) aggregates hazard, exposure, and criticality across 287 PennDOT municipality polygons. Three weighting schemes test whether rankings are stable when the model is hazard-led, exposure-led, or balanced. The result is a transparent CATModel-style screening tool that identifies where more detailed engineering or site-specific geotechnical review would be most valuable.

For a concise final-result narrative, see [`docs/final-results-brief.md`](docs/final-results-brief.md).

## Data Sources

- PASDA/DCNR Pennsylvania Karst Features: https://www.pasda.psu.edu/
- Pennsylvania Department of Health facility and public health context: https://www.health.pa.gov/
- National Center for Education Statistics school data context: https://nces.ed.gov/
- U.S. Census Bureau county population context: https://www.census.gov/
- Pennsylvania Geological Survey karst references: https://www.dcnr.pa.gov/Geology/

## Limitations

- The hazard layer is treated as a binary susceptibility proxy; it is not a time-dependent sinkhole probability model.
- Facility coordinates and classifications depend on the completeness of public DOH and USGS source inventories.
- The model does not include fragility curves, structural vulnerability, repair duration, redundancy, or service-area disruption.
- Exposure buffers are screening distances, not geotechnical proof of sinkhole initiation, propagation, or facility damage.
- Loss proxy values are relative scenario indicators, not dollar-denominated loss estimates.

## Citations

- IPCC. 2014. Climate Change 2014: Impacts, Adaptation, and Vulnerability. Cambridge University Press.
- Wood, N., Jones, J., Peters, J., and Richards, K. U.S. Geological Survey risk and vulnerability framing for natural hazards.
- Reese, S. O., and Kochanov, W. E. Pennsylvania Geological Survey karst and sinkhole hazard references.

## License

MIT
