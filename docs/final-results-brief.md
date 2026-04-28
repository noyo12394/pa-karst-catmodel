# Final Results Brief: PA Karst Hazard CATModel

## Project Position

This project treats mapped karst features as a regional susceptibility proxy and asks where that susceptibility intersects essential facilities in southeastern Pennsylvania. The model does not claim to predict the timing or probability of a sinkhole at a parcel. It instead provides a transparent screening workflow that supports prioritization: which counties, municipalities, and essential facilities deserve more detailed geotechnical review, asset verification, or emergency-planning attention.

The study area covers Lehigh, Berks, Bucks, Montgomery, and Chester Counties. These counties combine mapped carbonate-karst terrain, dense public infrastructure, and high population exposure. The final workflow links mapped karst, public facility inventories, municipality boundaries, and a Karst Hazard Index (KHI) sensitivity test into one reproducible project package.

## Final Data Inventory

| Layer | Source | Geometry | Statewide Records | Study-Area Records | Role |
| --- | --- | --- | ---: | ---: | --- |
| Pennsylvania Karst Inventory | PA DCNR / PASDA | Point | 144,245 | 30,623 | Hazard / susceptibility proxy |
| Hospitals | PA Department of Health, 2025-11 | Point | 226 | 42 | Essential-facility exposure |
| Essential Structures | USGS National Map | Point | 24,217 | 1,675 | Essential-facility exposure |
| County boundaries | PennDOT, 2026-01 | Polygon | 67 | 5 | Study-area clipping and county summary |
| Municipality boundaries | PennDOT, 2026-01 | Polygon | 2,567 | 287 | KHI aggregation unit |

The dashboard uses the reconciled final-deck facility count: 42 hospitals plus 1,675 USGS essential structures, for 1,717 total facilities. Earlier draft artifacts contained a minor alternate essential-structure count, but the final PDF/PPT county totals reconcile to 1,717 facilities.

## Hazard Pattern

The mapped karst inventory is dominated by surface depressions, which represent about 94.0 percent of study-area features. Sinkholes contribute about 2.8 percent, surface mines about 3.1 percent, and caves less than 0.1 percent. This composition is why the project uses "mapped karst susceptibility" language rather than treating every point as an observed damaging sinkhole.

County-level hazard density is highly uneven. Lehigh has the highest mapped-feature density at 11.24 features/km2, followed by Berks at 7.27 features/km2. Chester drops to 1.29 features/km2, while Bucks and Montgomery are below 0.40 features/km2. This spatial imbalance is the backbone of the county exposure story: the highest concern is not simply where the most people live, but where dense essential facilities overlap dense mapped karst.

## Exposure Results

The final exposure screen identifies 380 essential facilities within 1 km of a mapped karst feature. The proximity bands are interpreted as planning screens:

| Buffer band | Hospital | Fire/EMS | Police | School | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0-100 m | 2 | 13 | 1 | 56 | 72 |
| 100-250 m | 2 | 23 | 7 | 62 | 94 |
| 250-500 m | 5 | 36 | 12 | 54 | 107 |
| 500-1000 m | 2 | 34 | 23 | 48 | 107 |
| Cumulative 1 km | 11 | 106 | 43 | 220 | 380 |

Berks and Lehigh dominate the exposure totals. Berks has 158 exposed facilities within 1 km, and Lehigh has 116. Together they account for 274 of 380 exposed facilities, or about 72 percent of the 1 km exposure set. Chester has 63, Montgomery has 40, and Bucks has only 3.

## Critical Hospital Findings

The most exposed hospital points are concentrated in Lehigh and Berks, with additional flagged facilities in Chester and Montgomery. The nearest-karst hospital list begins:

1. Lehigh Valley Hospital, Lehigh County, Allentown: 57 m
2. Tower Behavioral Health, Berks County, Reading: 72 m
3. Surgical Institute of Reading, Berks County, Wyomissing: 111 m
4. Good Shepherd Specialty Hospital, Lehigh County, Bethlehem: 130 m
5. Wernersville State Hospital, Berks County, Wernersville: 273 m

These distances should be read as screening evidence, not evidence of structural distress. The appropriate follow-up would be source-data QA, site geotechnical record review, drainage and stormwater checks, and coordination with facility owners where appropriate.

## KHI Method

The Karst Hazard Index uses the IPCC-style risk framing that risk emerges from the interaction of hazard, exposure, and vulnerability or criticality. The project operationalizes that framing as:

```text
KHI = 100 x (wH H + wE E + wC C)
```

where `H` is normalized mapped-karst count, `E` is normalized exposed-facility count, and `C` is normalized criticality-weighted exposure. Three schemes are used:

| Scheme | Hazard weight | Exposure weight | Criticality weight |
| --- | ---: | ---: | ---: |
| Base | 0.40 | 0.40 | 0.20 |
| Hazard-led | 0.60 | 0.25 | 0.15 |
| Exposure-led | 0.25 | 0.60 | 0.15 |

## Highest-Priority Municipalities

The base KHI ranking identifies Allentown as the strongest combined priority because it has both high exposed-facility count and meaningful mapped-karst presence. Hanover Township and Maxatawny Township follow, but for different reasons: Hanover is sensitive to hazard weighting, while Maxatawny has very high mapped-karst count.

| Base rank | Municipality | County | Karst count | Exposed facilities | Base KHI |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | Allentown | Lehigh | 349 | 45 | 64.4 |
| 2 | Hanover | Lehigh | 787 | 5 | 48.0 |
| 3 | Maxatawny | Berks | 3,407 | 6 | 38.3 |
| 4 | Lyons | Berks | 58 | 2 | 36.6 |
| 5 | Whitehall | Lehigh | 346 | 18 | 34.8 |

The sensitivity test evaluates 900 weight combinations across the hazard-exposure-criticality simplex. Base and hazard-led ranks are strongly correlated with Spearman rho = 0.942, and base and exposure-led ranks remain strongly correlated with rho = 0.906. Allentown remains ranked first across roughly 80 percent of valid weight space, making it the most stable top-priority municipality in the analysis.

## Interpretation

The main technical finding is spatial concentration. Karst susceptibility is not evenly distributed across the five counties, and neither is essential-facility exposure. Berks and Lehigh carry most of the modeled exposure burden, while Allentown, Hanover, and Maxatawny emerge as high-priority KHI municipalities for different combinations of hazard count, exposed assets, and criticality.

The model is strongest as a defensible screening tool. It is transparent, reproducible, and sensitive to weight assumptions, but it does not contain a subsurface failure model, event frequency, fragility curve, downtime estimate, or service-area disruption model. Those additions would be required before moving from classroom CATModel screening to operational risk management.

## Recommended Next Work

1. Verify the nearest-karst hospital list against original facility coordinates and local geotechnical records.
2. Add carbonate geology, depth-to-bedrock, soil, slope, hydrology, stormwater, and land-use covariates.
3. Replace buffer-only damage logic with facility-type fragility curves or expert-elicited damage states.
4. Add service-area and redundancy metrics for hospitals, EMS, schools, and police.
5. Convert the loss proxy into a dollar and downtime model using replacement value, occupancy, repair duration, and functionality curves.
6. Extend the sensitivity analysis to probabilistic uncertainty rather than deterministic weight sweeps alone.

## Core Citations

- IPCC. 2014. Climate Change 2014: Impacts, Adaptation, and Vulnerability.
- Wood, N., Jones, J., Peters, J., and Richards, K. U.S. Geological Survey risk and vulnerability framing for natural hazards.
- Reese, S. O., and Kochanov, W. E. Pennsylvania Geological Survey karst and sinkhole hazard references.
- PA DCNR / PASDA. Pennsylvania Karst Inventory.
- PA Department of Health. Hospital facility inventory.
- USGS National Map. Essential structures.
