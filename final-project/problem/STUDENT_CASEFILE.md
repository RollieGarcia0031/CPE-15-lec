# OPERATION: BLANK MAP — LUCBAN, QUEZON EDITION
### CPE15 Final Examination | Student Mission Dossier
**Southern Luzon State University | College of Engineering**  
**Course:** CPE15 Professional Elective 1: Programming for Data Science  
**Mode:** Individual investigative practical | **Time:** 180 minutes | **Technical defense:** Separately scheduled

> **CONFIDENTIAL CASE FILE CPE15-LUC-001**  
> Twelve named barangays of Lucban, Quezon. Five fictional assistance hubs. Three proposed deployments. One recommendation that must survive new evidence.

## Situation report

In the real municipality of **Lucban, Quezon**, a **fictional Municipal Digital Assistance Planning Unit** must choose which **three of twelve selected barangay-associated study catchments** should receive hypothetical mobile digital assistance units. Some simulated source records are incomplete, inconsistent, or duplicated. Facility locations and community boundaries have been supplied, but the analysis has not been verified.

You are an independent **Data Intelligence Officer**. Your task is to determine which three zones should receive priority, show the evidence behind your recommendations, and deliver a map that a nontechnical decision maker can explore. You will receive an operational update during the examination. Your final recommendation must account for it.

The **municipality and barangay names are real**, and the reference coordinates are approximate locations within Lucban. The circular 350 m study catchments are **not official barangay boundaries**. All service, household access, risk and demand statistics and assistance facilities are **fictional**. Do not present any of those simulated quantities as real government data.

## Your assignment

Produce a defensible response to these questions:

1. What source information is trustworthy, and what requires correction or qualification?
2. Which three zones rank highest under the supplied prioritization policy **before** the new operational update?
3. What factors explain those rankings?
4. Where are the zones in relation to currently operational service facilities?
5. Does the new evidence change the top three, and why?
6. What are the limitations of the proposed decision?

**You select the data science methods and organize your own code.** Your notebook must make it possible for an examiner to trace each major finding to the underlying evidence. Unjustified guesses, invented replacements, and screenshots without reproducible calculations are insufficient.

## Materials in your evidence folder

| File | Contents |
|---|---|
| `zones.geojson` | Twelve 350 m synthetic study catchments around approximate locations of real Lucban barangays; **not official boundaries** |
| `household_access.csv` | Household totals and digital access counts |
| `risk_index.csv` | Recorded community risk scores |
| `service_requests.sqlite` | Request records in SQLite |
| `facilities.csv` | Coordinates and status of **fictional** mobile-assistance service hubs near Lucban |
| `field_notes.txt` | **Simulated** verification evidence and interpretation rules |

See `data/GEOGRAPHIC_SOURCES.md` for geographic provenance and geographic uncertainty. For service demand, count only **distinct** request IDs with a status of `verified` or `open`. Evidence marked VERIFIED in the field notes may be used to repair affected records. Do not assume that missing data means zero.

## Prioritization policy

Apply this exact fictional policy after validating and joining the records. All four component scores are on a 0 to 100 scale.

| Indicator | Calculation | Weight |
|---|---|---:|
| Household service gap | `100 * (1 - households_with_access / total_households)` | 45% |
| Risk score | Validated `risk_score` in the risk file | 25% |
| Distance score | `100 * nearest_operational_facility_distance_km / maximum_zone_distance_km` | 20% |
| Request demand score | `100 * valid_requests / maximum_zone_valid_requests` | 10% |

**Priority = 0.45 × service gap + 0.25 × risk + 0.20 × distance + 0.10 × demand**

The denominator for each normalized indicator is taken from the corresponding **twelve-zone scenario being evaluated**. Recalculate the distance normalization for any change in facility availability. When a maximum denominator is zero, use a normalized score of zero. Break exact priority ties by ascending zone ID.

Distances are **straight-line distances from projected zone centroids to the nearest operational facility**, not travel distances. Use an appropriate projected coordinate reference system for any distance measurement.

These weights are supplied for comparable examination answers; they are **not** real government policy. You may discuss their limitations, but do not replace them with your own weights.

## Mission schedule

| Clock | Mission | Evidence expected |
|---|---|---|
| 00:00–00:10 | Case briefing | Read rules; inspect files |
| 00:10–00:35 | Evidence recovery | Auditable corrections and unresolved issues |
| 00:35–01:00 | Data reconstruction | One validated analytical table, including SQL results |
| 01:00–01:20 | Intelligence board | Two justified analytical visualizations |
| 01:20–01:50 | Geographic investigation | Spatial calculations and original ranking |
| 01:50–02:25 | Interactive intelligence map | Functioning Folium map |
| **02:25** | **Sealed operational update released** | Apply new evidence to calculations and map |
| 02:25–02:50 | Evidence reversal | Revised ranking, map, and comparison |
| 02:50–03:00 | Final report and submission | Files saved and submitted |

The time windows are guidance for pacing. You may revisit earlier code throughout the examination. **No clue or file will be withheld because your answer to a checkpoint was incorrect.**

## Required submissions: official Google Form (3 uploads)

Submit **exactly three files** through the official CPE15 Google Form during the scheduled examination. Replace `ID` with your Student ID, exactly as issued:

| Google Form upload | Filename | Required contents |
|---|---|---|
| 1. Notebook | `CPE15_ID_ANALYSIS.ipynb` | Executable source audit, SQL and Python extraction, computations, visualizations, before/after interpretations |
| 2. Decision report | `CPE15_ID_DECISION.pdf` | Up to 350 words in the memo body: original and revised top three, explanations, evidence limitations and confidence |
| 3. Supporting files | `CPE15_ID_SUPPORTING.zip` | Includes `CPE15_ID_FINAL_MAP.html` and `CPE15_ID_PROCESSED.csv`, plus any local map assets needed to open the HTML |

Do **not** include the six original evidence files in the supporting ZIP. Preserve any local map asset paths if needed. The processed CSV must contain all twelve zones and their validated final scores, rankings, and spatial metrics. **A screenshot is not a substitute for an executable notebook, an inspectable HTML map, or a processable CSV.**

If your files were already prepared in the previous four-file format, consult the instructor before uploading; the correction engine can inspect that layout, but **the official Google Form requires the three uploads above.**

The final map must include **synthetic study catchments**, labelled with the real barangay names, coded by priority score, operational facility locations, useful popups and tooltips, meaningful layer controls, a legend, and an indication of any facility affected by the new evidence. A readable exported map is required; merely displaying a map within the notebook is insufficient.

The two charts must each communicate a different relevant question. At least one should compare zone priorities. Label values and units appropriately.

## Professional standards

- Demonstrate Python, pandas/NumPy, SQL, Matplotlib or seaborn, GeoPandas, and Folium where they materially support the investigation.
- Keep original evidence unchanged. Record any correction and its source.
- Write code that can be executed from a fresh notebook kernel using only the supplied files and authorized locally available libraries.
- Explicitly distinguish observed evidence from assumptions and recommendations.
- Do not claim that proximity equals road travel time or that synthetic scores are definitive evidence of actual community need.
- Your final output will be evaluated on technical accuracy, completeness, appropriate interpretation, and reproducibility, not speed or theatrical participation.

## Authorized resources and integrity

Individual work only. Instructor-provided notes, documentation, and locally installed libraries may be consulted if authorized during the briefing. Do **not** use generative AI, AI coding assistants, another person's solutions, or unapproved external services to complete graded tasks. Do not share examination answers.

The separately scheduled individual defense may require you to explain your code or perform a small modification in front of the examiner.

**MISSION DIRECTIVE:** Your objective is not simply to draw a map. It is to present a conclusion that remains defensible after the evidence changes.

## Location context and academic honesty

The geographic context is **Lucban, Quezon, Philippines**. The names and identifiers of the 12 selected barangays are factual. The reference points are approximations and the buffer shapes are invented teaching areas rather than legal barangay boundaries. The scenario is not an assessment of actual broadband availability, hazard exposure, household access, or municipal facility capacity. Any map title, footnote and decision memo must disclose this distinction.
