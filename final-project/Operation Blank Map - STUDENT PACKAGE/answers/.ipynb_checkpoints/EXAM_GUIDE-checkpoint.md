# OPERATION: BLANK MAP — Exam Guide and Work Plan

This document explains, in plain language, what the CPE15 final examination is asking you to do and exactly how to produce the required deliverables. It is a study and execution guide for Case **CPE15-LUC-001**, based on `STUDENT_CASEFILE.md`, the rubrics, and the evidence files in `data/`.

---

## 1. What the exam actually wants

You are playing the role of a **Data Intelligence Officer** for a **fictional** Municipal Digital Assistance Planning Unit in the **real** municipality of Lucban, Quezon.

Your job is **not** just to draw a map. You must:

1. Inspect an imperfect evidence package and decide what is trustworthy.
2. Repair only what the field bulletin explicitly authorises, and keep a record of every correction.
3. Build one clean, validated table: one row per study zone.
4. Compute a supplied weighted priority score for all twelve zones.
5. Draw two charts that answer two different questions.
6. Measure straight-line distances from zones to the nearest **operational** facility.
7. Build an interactive Folium map a non-technical official could explore.
8. Recompute everything after a **sealed operational update** is released at 02:25.
9. Defend the original and revised recommendation in a short decision memo.

The central test is whether your conclusion **survives new evidence**. A correct answer that cannot be traced to executable code earns little credit.

### The six questions you must answer

| # | Question | Where it is answered |
|---|---|---|
| 1 | What source information is trustworthy, and what needs correction or qualification? | Source audit |
| 2 | Which three zones rank highest **before** the update? | Original ranking |
| 3 | What factors explain those rankings? | Component analysis and charts |
| 4 | Where are the zones relative to currently operational facilities? | Spatial analysis and map |
| 5 | Does the new evidence change the top three, and why? | Revised analysis |
| 6 | What are the limitations of the decision? | Memo and final section |

---

## 2. What is real and what is simulated

This distinction is graded and must appear in your map title, map footnote, and decision memo.

**Real:**
- The municipality of Lucban, Quezon.
- The twelve barangay names and their PSGC codes.
- The approximate locality reference points.

**Simulated / invented:**
- The 350 m circular catchments — they are **not official barangay boundaries**.
- All five assistance hubs, their coordinates, and their statuses.
- All household counts, digital access counts, risk scores, and service requests.
- The priority weights and the final recommendation.
- The distances and priority scores derived from them.

**Approximate and uncertain:**
- The reference coordinates are not field-surveyed and were not certified by NAMRIA or the LGU.

Never write that the results reflect real broadband access, hazard exposure, or LGU capacity. Say "simulated teaching data."

---

## 3. The evidence files

All files are in `data/`. Do not edit them. Read them with `dtype=str` where numeric parsing could destroy leading zeros or codes.

| File | What it contains | What to watch for |
|---|---|---|
| `zones.geojson` | 12 synthetic 350 m catchments with `zone_id`, `zone_name`, `psgc_code`, lat/lon | Geometry is EPSG:4326; not official boundaries |
| `household_access.csv` | `zone_code`, `total_households`, `households_with_access` | Duplicate row, blank value, impossible value, `A-03` alias |
| `risk_index.csv` | `zone_code`, `risk_score` | Conflicting duplicate for A09 |
| `service_requests.sqlite` | Table `requests`: `request_id`, `zone_code`, `request_type`, `status`, `requested_at` | Duplicate IDs, `A-03` alias, ineligible statuses |
| `facilities.csv` | 5 fictional hubs: `facility_id`, `facility_name`, longitude, latitude, `status` | All operational before the update |
| `field_notes.txt` | Simulated verification bulletin | Only `VERIFIED` statements authorise repairs |

### The defects you must find and handle

| ID | Defect | Authorised repair |
|---|---|---|
| D1 | `A-03` used instead of `A03` in household, risk, and request data | FN-01: normalise `A-03` to `A03` in all files |
| D2 | Exact duplicate household row for A07 | Count each household once; drop the duplicate |
| D3 | `households_with_access` blank for A06 | FN-02: set to 350; do **not** treat blank as zero |
| D4 | A11 access = 1220 against only 780 total households | FN-03: replace with 220 |
| D5 | A09 has both risk 72 and risk 96 | FN-04: keep 72; 96 is obsolete |
| D6 | Three duplicate `request_id` rows | Count `DISTINCT request_id` |
| D7 | `cancelled` and `invalid` requests exist | Keep only status `verified` or `open` |

If you apply any fix not authorised by the bulletin, you must justify it. Do not invent replacements for missing values.

---

## 4. The scoring formula (use it exactly)

For every zone:

```
service_gap      = 100 * (1 - households_with_access / total_households)
risk_component   = validated risk_score
distance_score   = 100 * nearest_operational_facility_distance_km
                         / maximum_zone_distance_km
demand_score     = 100 * distinct_valid_requests
                         / maximum_zone_valid_requests

priority = 0.45 * service_gap
         + 0.25 * risk_component
         + 0.20 * distance_score
         + 0.10 * demand_score
```

Rules that are easy to lose points on:

- **Denominators are from the twelve-zone scenario being evaluated.** When facility availability changes, recompute the distance maximum. Otherwise your revised scores are wrong.
- **If a denominator is zero, the component score is zero.** Do not divide by zero.
- **Only `verified` and `open` statuses count.** Use `COUNT(DISTINCT request_id)`.
- **Tie-break by ascending zone ID.** A07 before A08 if scores are exactly equal.
- **Distances are straight-line, not road distance.** Reproject first; never measure degrees.
- **Use the supplied weights.** You may critique them but must not replace them.

---

## 5. Recommended method, step by step

### Step 1 — Inspect before cleaning (about 10 minutes)

- Load every file as text.
- Print shapes, unique zone codes, duplicate rows, missing values, status counts, and the date range.
- Write down each defect and its evidence. This becomes your audit section.

### Step 2 — Parse the field notes with Python (about 15 minutes)

- Read `field_notes.txt` line by line.
- Use `re` to select lines matching `^FN-\d+\s+VERIFIED:`.
- Extract the zone code and the numeric values from each statement into a structured list or DataFrame.
- Keep non-`VERIFIED` notes as interpretation rules, not repairs.
- This demonstrates native Python text handling, which is explicitly scored.

### Step 3 — Apply repairs to copies (about 15 minutes)

- Never mutate the originals.
- Normalise `A-03` in all three affected tables.
- Drop the duplicate household row before using the values.
- Apply A06 = 350, A11 = 220, A09 = 72.
- Build a correction log with columns: source file, zone, field, old value, new value, authority (FN number), rationale.
- Assert post-repair integrity:
  - one row per zone,
  - no missing values,
  - access never exceeds total,
  - all gaps between 0 and 100,
  - all nine-digit PSGC codes present.

### Step 4 — Extract demand with SQL (about 15 minutes)

Write SQL that normalises the alias inside the query, filters status, and counts distinct IDs:

```sql
SELECT CASE WHEN zone_code = 'A-03' THEN 'A03' ELSE zone_code END AS zone_code,
       COUNT(DISTINCT request_id) AS valid_requests
FROM requests
WHERE status IN ('verified', 'open')
GROUP BY 1
ORDER BY 1;
```

Also run an audit query showing all rows, distinct IDs, and eligible rows so the effect of the filter is visible.

### Step 5 — Build one analysis table (about 15 minutes)

- Use the GeoJSON zones as the authoritative spine (12 rows).
- Left-join household, risk, and SQL demand on `zone_code`.
- Validate that the result is exactly 12 unique zones.
- Fill request counts with zero only where the zone genuinely has no eligible record.
- Compute `service_gap` here.

### Step 6 — Make two charts (about 20 minutes)

Chart 1 should answer **who ranks highest**:
- horizontal bars of priority, sorted highest to lowest,
- top three highlighted,
- values labelled,
- axis title with units.

Chart 2 must answer a **different** question. Good options:
- stacked weighted contributions (gap, risk, distance, demand) per zone,
- service gap versus risk scatter sized by demand,
- distance-to-facility versus priority.

Every figure needs a title, labelled axes with units, and a short interpretation in your own words.

### Step 7 — Compute geography and the original ranking (about 30 minutes)

- Keep geometries in `EPSG:4326` for the map.
- Reproject to **`EPSG:32651` (UTM zone 51N)** for all distance work. This is the correct metric zone for Luzon.
- Compute the **polygon centroid** in the projected CRS, not in degrees.
- For each zone, find the minimum distance to a facility whose status is `operational`.
- Record the nearest facility ID and name too.
- Compute the four indicators, the weighted priority, and the rank.
- Save this as your **original** ranking before applying the update.

### Step 8 — Build the Folium map (about 35 minutes)

Required elements:

- Study catchment polygons coloured by priority score.
- Real barangay names visible in tooltips.
- Operational facility markers with popups.
- A separate layer for any facility affected by the update.
- Useful popups showing the numbers behind the colour.
- A working `LayerControl`.
- A legend explaining colours and symbols.
- A visible disclaimer that catchments and statistics are simulated and not official boundaries.
- A useful map extent and readable contrast.

Export the map to `CPE15_FINAL_MAP.html`. Opening it must not depend on the notebook running.

### Step 9 — Apply the sealed update (about 25 minutes)

At 02:25 the examiner releases a notice. It may, for example, close a hub, open a new one, or add verified requests.

Do this:

1. Record the time and exact substance of the notice.
2. Encode it as a status override (and/or extra requests) in code. Do not edit the original files.
3. Re-run the same scoring function. The function must recompute the nearest operational facility and the distance denominator.
4. Produce a before/after comparison table and a comparison chart.
5. Rebuild the map with the affected facility clearly flagged and the revised priorities.
6. State whether the top three changed and explain the mechanism — including zones that move only because the normalisation denominator changed.

### Step 10 — Write the decision memo (about 10 minutes)

Maximum **350 words** in the memo body. Cover:

- Original top three.
- Revised top three.
- The evidence behind the change.
- Limitations.
- Confidence level.
- The simulated-data disclaimer.

Export as PDF.

### Step 11 — Package and validate (about 10 minutes)

Produce:

| Upload | Filename | Contents |
|---|---|---|
| 1 | `CPE15_ID_ANALYSIS.ipynb` | Executed notebook with all code, outputs, charts, map, and interpretations |
| 2 | `CPE15_ID_DECISION.pdf` | Decision memo, max 350 words |
| 3 | `CPE15_ID_SUPPORTING.zip` | `CPE15_ID_FINAL_MAP.html` and `CPE15_ID_PROCESSED.csv`, plus any local map assets |

- Do not include the six original evidence files in the ZIP.
- The processed CSV must contain all twelve zones with final scores, ranks, and spatial metrics.
- Replace `ID` with your Student ID.
- Open the exported HTML from the ZIP to confirm it works.
- Re-run the notebook from a fresh kernel to confirm reproducibility.

---

## 6. How the exam is marked

There are two separate 100-point assessments.

### A. Final Long Examination (100)

| Area | Points | What earns credit |
|---|---:|---|
| Source audit and reconciliation | 15 | Six defects detected, repairs justified and applied, correction log kept |
| Native Python and SQL extraction | 20 | Field notes parsed with native Python, distinct eligible requests counted, results integrated |
| Tabular integration and reasoning | 20 | One row per zone, valid joins, correct indicators and weights, validated initial ranking |
| Charts and interpretation | 15 | Priority chart plus a distinct second chart, titles, units, interpretation |
| Spatial reasoning and CRS | 15 | Correct geometry and projected CRS, centroid-to-nearest-active distance, limitations explained |
| Revised decision and explanation | 15 | Sound recomputation, rank comparison, explanation, limitations, confidence |

### B. Interactive Mapping Performance (100)

| Area | Points | What earns credit |
|---|---:|---|
| GeoPandas processing | 25 | CRS, geometries, projected distances, active nearest facility, joined attributes |
| Folium implementation | 25 | Thematic zones, facility markers and status, popups and tooltips, layer controls and legend |
| Data encoded on map | 15 | Accurate revised priorities, understandable encoding, displayed values |
| Operational update | 10 | Visible change in availability, recalculated scores and facility information |
| Reproducibility and code quality | 10 | Fresh-kernel execution, understandable reusable code, correct exports |
| Cartographic readability and disclosure | 5 | Extent, contrast, explanatory legend, explicit simulated-data disclaimer |
| Individual technical defense | 10 | Explain provenance and algorithm, GIS calculations or changes, minor code modification |

---

## 7. What is already prepared for you

The file `answers/CPE15_ANALYSIS.ipynb` is a complete, executed notebook that follows the workflow above. It contains:

- All imports and environment checks.
- Programmatic detection of defects D1–D7.
- Native Python parsing of the field bulletin.
- A correction log and integrity assertions.
- The SQL demand extraction with an audit query.
- One validated row per zone.
- The two required charts.
- GeoPandas distance work in EPSG:32651.
- The original ranking.
- A full Folium map with layers, legend, popups, and disclaimer.
- A parameterised sealed-update section.
- CSV and HTML export with validation.

`answers/CPE15_PROCESSED.csv` and `answers/CPE15_FINAL_MAP.html` are already generated.

### What remains for you

1. **Paste the sealed operational update** into the update cell (variables `UPDATE_SOURCE`, `UPDATE_FACILITY_STATUS`, `UPDATE_EXTRA_REQUESTS`, `UPDATE_NOTES`).
2. Re-run the update cell and the comparison, map, and export cells.
3. Write the 350-word decision memo in `answers/ANSWERS.md` and export it to PDF.
4. Rename files with your Student ID.
5. Zip the HTML and CSV (not the original evidence).
6. Verify the notebook runs from a fresh kernel.

### Current pre-update numbers (for your reference)

| Rank | Zone | Barangay | Priority |
|---:|---|---|---:|
| 1 | A08 | Malupak | 70.99 |
| 2 | A02 | Aliliw | 68.36 |
| 3 | A07 | Kulapi | 64.18 |
| 4 | A03 | Atulinao | 63.43 |

A03 is only about 0.75 points behind A07, so a facility closure or new demand can plausibly change the top three. Explain any such change mechanically.

---

## 8. Common mistakes that lose points

- Treating `A-03` as a different zone from `A03`.
- Treating the blank A06 value as zero.
- Accepting A11's access count of 1220 even though it exceeds total households.
- Keeping both A09 risk values or averaging them.
- Using `COUNT(*)` instead of `COUNT(DISTINCT request_id)`.
- Counting `cancelled` or `invalid` requests.
- Measuring distance in degrees, or using the GeoJSON anchor point instead of the projected polygon centroid.
- Forgetting to recompute the distance denominator after a facility changes status.
- Ranking a zone using a distance to a hub that is no longer operational.
- Producing two charts that answer the same question.
- Omitting the simulated-data disclaimer from the map or memo.
- Exporting a map that only displays inside the notebook.
- Including the original evidence files in the supporting ZIP.
- Submitting a screenshot instead of the notebook, HTML map, and CSV.
- Using generative AI, another person's solution, or unapproved external services. The exam forbids it, and there is a separate oral defense.

---

## 9. Final checklist before submission

- [ ] All six original evidence files unchanged.
- [ ] Every correction traceable to an FN number or an explicit rationale.
- [ ] One row per zone; twelve rows in the validated table.
- [ ] SQL counts distinct eligible request IDs.
- [ ] All four indicators and the weighted priority recomputed correctly.
- [ ] Original ranking saved before the update.
- [ ] Two distinct, labelled, interpreted charts.
- [ ] Distances computed in EPSG:32651 from projected centroids to operational facilities.
- [ ] Folium map has thematic zones, facilities, popups, tooltips, layer control, legend, and disclaimer.
- [ ] Sealed update applied to calculations and to the map.
- [ ] Revised top three and comparison presented.
- [ ] Affected facility visibly marked on the map.
- [ ] `CPE15_ID_PROCESSED.csv` has all twelve zones and final metrics.
- [ ] `CPE15_ID_FINAL_MAP.html` opens independently.
- [ ] Decision memo is at most 350 words and covers original, revised, evidence, limitations, confidence.
- [ ] ZIP contains only the HTML, CSV, and required assets.
- [ ] Notebook runs from a fresh kernel.
- [ ] Files renamed with your Student ID and uploaded through the official form.

---

## 10. A note on honesty and scope

The barangay names and municipality are real. Everything that drives the score is invented for teaching. Your report should be defensible as a **data-science exercise**, not as an assessment of actual community need. If the update is ambiguous, record your interpretation and its effect rather than silently guessing. A transparent, reproducible analysis with stated uncertainty is the intended answer.
