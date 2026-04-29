# Project Audit

| File / artifact | Purpose | Status | Gap / note |
| --- | --- | --- | --- |
| `src/config.py` | Paths, constants, study-area metadata, model weights | current | Includes real-data path constants and four KHI schemes |
| `src/io_utils.py` | Pure-Python DBF and CSV helpers | current | Supports DBF numeric/string fields and deleted records |
| `src/shapefile_utils.py` | Pure-Python point/polygon shapefile reader | current | Supports point and polygon geometry used by this project |
| `src/boundaries.py` | County and municipality polygon loading/assignment | current | Falls back to bbox rectangles only if boundary archives are absent |
| `src/load_karst.py` | DCNR karst parse/filter and summary JSON | current / real | Produces 144,245 statewide and 30,623 study-area records with polygon assignment |
| `src/facilities.py` | Real DOH/USGS facility loader plus synthetic fallback | current / real | Real path produces 42 hospitals + 1,675 structures; fallback is labeled screening-grade |
| `src/exposure.py` | Nearest-karst distance, buffers, density, facility risk tables | current / real | Uses 100 m, 250 m, 500 m, 1 km, and outside classes |
| `src/khi.py` | Municipality KHI, sensitivity, and loss proxy | current / real | Uses 287 real municipality polygons when available |
| `src/figures.py` | Eight 220-dpi matplotlib outputs | current | Regenerated from processed tables |
| `src/presentation.py` | Final PPTX generator | current | Builds 15 slides with speaker notes |
| `scripts/*.py` | Individual and full pipeline entry points | current | `scripts/run_all.py` completes end to end locally |
| `tests/*.py` | Unit tests | current | 6 tests pass, including geospatial, KHI, and exposure buffer tests |
| `dashboard/index.html` | Static project hub shell | current | Adds OG metadata, data inventory, new tabs, downloads |
| `dashboard/app.js` | Dashboard state, charts, animation | current | Synced to regenerated table values |
| `dashboard/styles.css` | Dashboard layout and visual system | current | Responsive checks completed via headless render |
| `dashboard/assets/*` | GIS evidence images | current / evidence | Image requests return 200 locally |
| `dashboard/downloads/*` | Served copies of final PPTX, CSVs, and brief | current | Built into Vercel `dist/` |
| `docs/final-results-brief.md` | Polished technical brief | current | Uses regenerated real-data values |
| `README.md` | Project overview, quickstart, methods, citations | current | Updated with live site and real-data methodology |
| `data/raw/*` | Raw GIS/source files | local / gitignored | Required for real reruns; clean clone can add same sources |
| `data/processed/*` | Generated intermediate CSVs/JSON | generated / gitignored | Recreated by pipeline |
| `outputs/tables/*` | Generated CSV result tables | generated / gitignored | Recreated by pipeline; copies served from dashboard downloads |
| `outputs/figures/*` | Generated PNG figures | generated / gitignored | Recreated by pipeline |
| `outputs/presentation/PA_Karst_Final_Presentation.pptx` | Generated final deck | generated / gitignored | Committed served copy lives in `dashboard/downloads/` |
| `project-assets/gis/*.pdf` | Source GIS layout evidence | current / evidence | Committed as project assets |

## Synthetic vs Real Status

- Real now: karst counts, county assignment, hospital points, USGS essential structures, county summaries, municipality KHI, sensitivity correlations, figures, PPTX, dashboard tables.
- Synthetic only as fallback: facility generator in `src/facilities.py` if DOH/USGS source files are absent.
- Still screening-grade by design: buffer exposure, relative loss proxy, and KHI weights because no temporal probability, fragility curves, or site-specific geotechnical covariates are included.
