# Final Results Brief: PA Karst Hazard CATModel

## Project Position

This project treats mapped karst features as a regional susceptibility proxy and asks where that susceptibility intersects essential facilities in southeastern Pennsylvania. It does not predict the timing or probability of a sinkhole at a parcel. It provides a transparent screening workflow for prioritization: which counties, municipalities, and essential facilities deserve more detailed geotechnical review, asset verification, or emergency-planning attention.

The final workflow links mapped karst, public facility inventories, county and municipality boundaries, exposure buffers, and a Karst Hazard Index sensitivity test into one reproducible package. The project is intentionally lightweight: no GeoPandas dependency, raw DBF parsing, pure-Python shapefile readers, and deterministic fallback logic when optional facility files are missing.

## Final Data Inventory

| File / layer | Purpose | Status | Gap / note |
| --- | --- | --- | --- |
| `DCNR_PAKarst.dbf` | Statewide mapped karst points | current / real | 144,245 records parsed directly from DBF |
| `PaCounty2026_01.zip` | County polygons and area | current / real | Web Mercator polygons converted to lon/lat |
| `PaMunicipalities2026_01.zip` | Municipality polygons | current / real | 287 study-area polygons used for KHI |
| `DOH_Hospitals202511.zip` | Hospital points | current / real | 42 study-area hospital records |
| `Struct_Point.shp/dbf` | USGS structures | current / real | 1,675 school, fire/EMS, police, and correctional records |
| Synthetic facility generator | Backup facility inventory | fallback only | Used only if real facility files are absent |
| GIS layout PDFs / screenshot | Workflow evidence | current / evidence | Used in dashboard and presentation |
| Dashboard / PPTX / brief | Communication artifacts | current | Synced to regenerated tables |

## Top-Line Results

| Metric | Value |
| --- | ---: |
| Statewide mapped karst records | 144,245 |
| Study-area mapped karst records | 30,623 |
| Study counties | 5 |
| Municipality polygons | 287 |
| Total facilities | 1,717 |
| Hospitals | 42 |
| USGS structures | 1,675 |
| Facilities within 500 m | 352 |
| Facilities within 1 km | 455 |

The study-area karst inventory is dominated by surface depressions: 28,798 of 30,623 features. The remaining features are 951 surface mines, 871 sinkholes, and 3 caves. This is why the model uses susceptibility language rather than treating every point as an observed damaging sinkhole.

County-level density is highly uneven. Lehigh has the highest mapped-feature density at 11.24 features/km², followed by Berks at 7.27 features/km². Chester is 1.30 features/km², Bucks is 0.62, and Montgomery is 0.51. This spatial imbalance drives the screening results: the greatest concern is not simply where the most people live, but where dense essential facilities overlap mapped karst evidence.

## Exposure Results

The regenerated exposure screen identifies 455 essential facilities within 1 km of mapped karst. The proximity bands are interpreted as planning screens:

| Buffer band | Fire/EMS | Hospital | Police | School | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0-100 m | 15 | 2 | 5 | 72 | 94 |
| 100-250 m | 30 | 3 | 11 | 84 | 128 |
| 250-500 m | 42 | 5 | 17 | 66 | 130 |
| 500-1000 m | 34 | 2 | 18 | 49 | 103 |
| Outside 1 km | 314 | 30 | 153 | 765 | 1,262 |

County summaries show the concentration clearly:

| County | Facilities | Within 500 m | Within 1 km | % within 1 km |
| --- | ---: | ---: | ---: | ---: |
| Lehigh | 215 | 159 | 176 | 81.9% |
| Berks | 301 | 114 | 158 | 52.5% |
| Chester | 331 | 47 | 63 | 19.0% |
| Montgomery | 499 | 23 | 47 | 9.4% |
| Bucks | 371 | 9 | 11 | 3.0% |

Lehigh and Berks account for 334 of the 455 facilities within 1 km. Lehigh is especially important because its total facility count is smaller than Montgomery or Bucks, but its exposure share is far higher.

## Critical Hospital Findings

Twelve hospitals fall within 1 km of a mapped karst feature. The nearest hospital points are:

| Rank | Hospital | County | City | Nearest karst |
| ---: | --- | --- | --- | ---: |
| 1 | Lehigh Valley Hospital | Lehigh | Allentown | 57 m |
| 2 | Tower Behavioral Health | Berks | Reading | 72 m |
| 3 | Surgical Institute of Reading | Berks | Wyomissing | 111 m |
| 4 | Good Shepherd Specialty Hospital | Lehigh | Bethlehem | 130 m |
| 5 | St. Luke's Hospital Bethlehem | Lehigh | Bethlehem | 181 m |
| 6 | Wernersville State Hospital | Berks | Wernersville | 273 m |
| 7 | Saint John Vianney Hospital | Chester | Downingtown | 303 m |
| 8 | Penn State Health St. Joseph | Berks | Reading | 333 m |
| 9 | Good Shepherd Rehabilitation Hospital | Lehigh | Allentown | 434 m |
| 10 | Veterans Affairs Medical Center Coatesville | Chester | Coatesville | 442 m |

These distances are screening evidence only. The appropriate follow-up is source-coordinate QA, site geotechnical record review, stormwater and drainage checks, and facility-owner coordination where appropriate.

## KHI Method and Sensitivity

The Karst Hazard Index follows the risk framing that risk emerges from the interaction of hazard, exposure, and vulnerability or criticality:

```text
KHI = 100 * (wH * H + wE * E + wC * C)
```

`H` is min-max normalized municipal karst density, `E` is min-max normalized exposed-facility count within 500 m, and `C` is min-max normalized criticality-weighted exposure. Four schemes were tested:

| Scheme | Hazard | Exposure | Criticality |
| --- | ---: | ---: | ---: |
| Base | 0.40 | 0.40 | 0.20 |
| Hazard-led | 0.60 | 0.25 | 0.15 |
| Exposure-led | 0.25 | 0.60 | 0.15 |
| Critical-facility | 0.30 | 0.35 | 0.35 |

Top Base KHI municipalities:

| Base rank | Municipality | County | Karst count | Exposed facilities | Base KHI |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | Allentown | Lehigh | 349 | 51 | 64.36 |
| 2 | Lower Macungie | Lehigh | 2,016 | 10 | 46.41 |
| 3 | Hanover | Lehigh | 787 | 5 | 46.32 |
| 4 | South Whitehall | Lehigh | 1,248 | 16 | 38.84 |
| 5 | Upper Macungie | Lehigh | 2,990 | 7 | 37.54 |
| 6 | Maxatawny | Berks | 3,407 | 6 | 36.52 |

Spearman rank correlations over the top 50 Base municipalities are strong but not identical:

| Scheme pair | Spearman rho |
| --- | ---: |
| Base vs Hazard-led | 0.957 |
| Base vs Exposure-led | 0.944 |
| Base vs Critical-facility | 0.969 |
| Hazard-led vs Exposure-led | 0.832 |

The interpretation is that the highest priorities are fairly stable, but the reason for high priority changes. Allentown is exposure- and criticality-driven. Hanover and Lower Macungie are more sensitive to hazard density. That distinction is useful for explaining what kind of follow-up each place needs.

## What This Means

The main technical finding is spatial concentration. Lehigh and Berks carry most of the modeled exposure burden, while Allentown, Lower Macungie, Hanover, South Whitehall, Upper Macungie, and Maxatawny emerge as high-priority municipal screening targets under the Base scheme. These results do not prove damage, but they do identify where deeper review is easiest to justify.

For screening and prioritization, the recommended next step is a short-list workflow: verify the highest-ranked hospital and facility coordinates, review known local geotechnical reports where available, check stormwater and drainage conditions, and decide whether site-level investigation is warranted. The model is strongest as a defensible triage tool. It is not a replacement for geotechnical engineering, but it gives that engineering work a more transparent starting point.

## Recommended Next Work

1. Verify the nearest-karst hospital list against original facility coordinates and local geotechnical records.
2. Add carbonate geology, depth-to-bedrock, soil, slope, hydrology, stormwater, and land-use covariates.
3. Replace buffer-only loss logic with facility-type fragility curves or expert-elicited damage states.
4. Add service-area and redundancy metrics for hospitals, EMS, schools, and police.
5. Convert the relative loss proxy into a dollar and downtime model using replacement value, repair duration, and functionality curves.
6. Extend sensitivity analysis from deterministic weight sweeps to probabilistic uncertainty.

## Core Citations

- IPCC. 2014. *Climate Change 2014: Impacts, Adaptation, and Vulnerability*.
- Wood, N. J., Doctor, D. H., Alder, J. R., and Jones, J. M. 2023. "Current and future sinkhole susceptibility in karst and pseudokarst areas of the conterminous United States." *Frontiers in Earth Science*. <https://doi.org/10.3389/feart.2023.1207689>
- Reese, S. O., and Kochanov, W. E. Pennsylvania Geological Survey karst and sinkhole hazard references.
- Maleki, M. et al. 2023. "GIS-based sinkhole susceptibility mapping using the best worst method." *Spatial Information Research*. <https://doi.org/10.1007/s41324-023-00520-6>
- Qiu, X., Wu, S.-S., and Chen, Y. 2020. "Sinkhole susceptibility assessment based on morphological, imagery, and contextual attributes derived from GIS and imagery data." *Journal of Cave and Karst Studies*. <https://doi.org/10.4311/2018ES0118>
- Taheri, K. et al. 2015. "Sinkhole susceptibility mapping using the analytical hierarchy process and magnitude-frequency relationships." *Geomorphology*. <https://doi.org/10.1016/j.geomorph.2015.01.005>
