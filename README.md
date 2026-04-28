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

This repository includes a static dashboard in `dashboard/` for web presentation of the model baseline. Build it locally with:

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

This project reframes mapped karst as a susceptibility proxy rather than a deterministic sinkhole forecast. The PASDA/DCNR DBF is parsed with a pure-Python reader, converted into latitude/longitude records, assigned to one of five study-area counties by bounding box, and summarized by county and feature type. This avoids heavyweight geospatial dependencies while keeping the workflow reproducible on a standard Python environment.

Essential facilities are represented with a synthetic but fixed-seed exposure inventory. Hospitals, schools, fire/EMS stations, and police facilities are generated around county population centers using type-specific spatial jitter, then scored by nearest mapped karst distance, local karst density within 1 km, and facility criticality. Buffer zones at 100 m, 250 m, and 500 m translate proximity into a simple exposure score.

The Karst Hazard Index (KHI) aggregates the hazard, exposure, and criticality dimensions to coarse municipality-like grid cells. Three weighting schemes test whether rankings are stable when the model is hazard-led, exposure-led, or balanced. The result is a transparent CATModel-style screening tool that identifies where more detailed engineering or site-specific geotechnical review would be most valuable.

## Data Sources

- PASDA/DCNR Pennsylvania Karst Features: https://www.pasda.psu.edu/
- Pennsylvania Department of Health facility and public health context: https://www.health.pa.gov/
- National Center for Education Statistics school data context: https://nces.ed.gov/
- U.S. Census Bureau county population context: https://www.census.gov/
- Pennsylvania Geological Survey karst references: https://www.dcnr.pa.gov/Geology/

## Limitations

- The hazard layer is treated as a binary susceptibility proxy; it is not a time-dependent sinkhole probability model.
- Facility locations are synthesized from population centers and facility counts, so they support classroom-scale exposure screening but not parcel-level decisions.
- The model does not include fragility curves, structural vulnerability, repair duration, redundancy, or service-area disruption.
- County bounding boxes are used for assignment instead of polygon overlays to keep the project install-light and reproducible without GeoPandas.
- Loss proxy values are relative scenario indicators, not dollar-denominated loss estimates.

## Citations

- IPCC. 2014. Climate Change 2014: Impacts, Adaptation, and Vulnerability. Cambridge University Press.
- Wood, N., Jones, J., Peters, J., and Richards, K. U.S. Geological Survey risk and vulnerability framing for natural hazards.
- Reese, S. O., and Kochanov, W. E. Pennsylvania Geological Survey karst and sinkhole hazard references.

## License

MIT
