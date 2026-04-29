# PA Karst Hazard CATModel

A reproducible Python and Vercel project that screens essential-facility exposure to mapped karst susceptibility in Lehigh, Berks, Bucks, Montgomery, and Chester Counties, Pennsylvania.

Live site: <https://pa-karst-catmodel.vercel.app>

## Quickstart

```bash
git clone https://github.com/noyo12394/pa-karst-catmodel.git
cd pa-karst-catmodel
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Place the raw source files in `data/raw/`:

- `DCNR_PAKarst/DCNR_PAKarst.dbf`
- `DOH_Hospitals202511.zip`
- `STRUCT_Pennsylvania_State_Shape/Shape/Struct_Point.shp`
- `STRUCT_Pennsylvania_State_Shape/Shape/Struct_Point.dbf`
- `PaCounty2026_01.zip`
- `PaMunicipalities2026_01.zip`

Then run:

```bash
python scripts/run_all.py
```

The pipeline writes processed CSVs to `data/processed/`, result tables to `outputs/tables/`, figures to `outputs/figures/`, and the final deck to `outputs/presentation/PA_Karst_Final_Presentation.pptx`.

## Dashboard

The static project hub in `dashboard/` contains the final project narrative, literature context, real-data inventory, exposure lab, KHI lab, scenario controls, cinematic animation, USGS photo gallery, GIS evidence, and download links. Build it locally with:

```bash
npm run build
```

Vercel serves the generated `dist/` directory using `vercel.json`.

## Directory Structure

```text
pa-karst-catmodel/
├── data/
│   ├── raw/              # input GIS files, gitignored
│   └── processed/        # cleaned intermediate CSVs, gitignored
├── outputs/
│   ├── figures/          # generated PNG charts and maps, gitignored
│   ├── tables/           # generated CSV tables, gitignored
│   └── presentation/     # generated PPTX, gitignored
├── dashboard/            # static Vercel dashboard and downloadable copies
├── docs/                 # final technical brief
├── project-assets/gis/   # committed GIS evidence PDFs
├── scripts/              # pipeline entry points
├── src/                  # type-hinted model source code
└── tests/                # pytest unit tests
```

## Methodology Summary

The project treats mapped karst as a susceptibility proxy, not a deterministic sinkhole forecast. The DCNR/PASDA karst DBF contains 144,245 statewide records; 30,623 fall inside the five study-county polygons. Surface depressions dominate the study inventory, so the language stays deliberately conservative: the model screens where mapped karst evidence is dense, not where a failure will occur.

Essential-facility exposure is computed from real public inventories: 42 PA Department of Health hospital points and 1,675 USGS structure points classified as schools, fire/EMS, police, or correctional facilities. Each facility receives nearest-karst distance, proximity class at 100 m, 250 m, 500 m, 1 km, local karst count within 1 km, and type criticality. The regenerated results identify 455 facilities within 1 km of mapped karst.

The Karst Hazard Index is computed over 287 PennDOT municipality polygons using `KHI = 100 * (wH*H + wE*E + wC*C)`. `H` is min-max normalized municipal karst density, `E` is min-max normalized exposed-facility count within 500 m, and `C` is min-max normalized criticality-weighted exposure. The Base, Hazard-led, Exposure-led, and Critical-facility schemes support sensitivity testing with Spearman rank correlations.

## Data Sources

- PASDA / PA DCNR Pennsylvania Karst Features: <https://www.pasda.psu.edu/>
- PA Department of Health hospital facility data: <https://www.health.pa.gov/>
- USGS National Map structures data: <https://www.usgs.gov/programs/national-geospatial-program/national-map>
- PennDOT / PA geospatial county and municipality boundaries via PASDA: <https://www.pasda.psu.edu/>
- U.S. Census Bureau county population context: <https://www.census.gov/>
- PA DCNR sinkhole and karst guidance: <https://www.pa.gov/agencies/dcnr/conservation/geology/geologic-hazards/sinkholes>

## Limitations

- Mapped karst is a binary susceptibility proxy, not a temporal sinkhole probability.
- Public facility coordinates and source classifications still need facility-by-facility QA before operational use.
- The model does not include fragility curves, foundation type, repair costs, service-area disruption, redundancy, or downtime.
- Exposure buffers are screening distances, not direct evidence of distress or damage at a facility.
- No rainfall, groundwater, construction, or climate trigger probability is modeled.

## Citations

- IPCC. 2014. *Climate Change 2014: Impacts, Adaptation, and Vulnerability*. Cambridge University Press.
- Wood, N. J., Doctor, D. H., Alder, J. R., and Jones, J. M. 2023. "Current and future sinkhole susceptibility in karst and pseudokarst areas of the conterminous United States." *Frontiers in Earth Science*. <https://doi.org/10.3389/feart.2023.1207689>
- Reese, S. O., and Kochanov, W. E. Pennsylvania Geological Survey sinkhole and karst hazard references.
- Maleki, M. et al. 2023. "GIS-based sinkhole susceptibility mapping using the best worst method." *Spatial Information Research*. <https://doi.org/10.1007/s41324-023-00520-6>
- Qiu, X., Wu, S.-S., and Chen, Y. 2020. "Sinkhole susceptibility assessment based on morphological, imagery, and contextual attributes derived from GIS and imagery data." *Journal of Cave and Karst Studies*. <https://doi.org/10.4311/2018ES0118>
- Taheri, K. et al. 2015. "Sinkhole susceptibility mapping using the analytical hierarchy process and magnitude-frequency relationships." *Geomorphology*. <https://doi.org/10.1016/j.geomorph.2015.01.005>

## License

MIT
