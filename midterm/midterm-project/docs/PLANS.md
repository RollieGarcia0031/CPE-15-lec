# Data Cleaning & Validation Plan (Revised): Lucban Establishment Field Data (BSCPE 3GF)

To whoever reads this, wag tamarin magbasa alam kong mahab 'to so please, tyaga lang pre.

Revised plan for the **CPE15 Midterm Project: Field Data Collection and Cleaning**. This version keeps the original plan and adds the gaps, corrections, and open decisions found in a full review of `docs/`, `lucban_data_cleaning_3GF.ipynb`, and all 10 raw CSVs (767 rows).

> Target submission date (per notebook header): **Oct 11, 2026** *lapit na tangina VHWAHAHAHA*.

---

## 1. Executive Summary & Deliverables

The group must process 10 raw field datasets (`raw_dataset_1.csv` to `raw_dataset_10.csv`, 767 rows) into a clean, verified, documented base dataset. The spec rewards completeness, traceability, consistency, and field verification over record count.

| # | Deliverable (spec  10) | Planned file | Status |
|---|---|---|---|
| 1 | Original SW Maps export (unmodified) | `RAW/` (keep raw CSVs and any original SW Maps project file) | Confirm original export is preserved |
| 2 | Raw CSV | `lucban_establishments_3GF_raw.csv` (merged, with `source_file` column) | Not yet exported |
| 3 | Clean CSV | `lucban_establishments_3GF_clean.csv` | Not yet exported |
| 4 | Cleaning notebook | `lucban_data_cleaning_3GF.ipynb` | In progress (stops at date audit) |
| 5 | Data dictionary | `DOCUMENTATION/data_dictionary.md` | Not started |
| 6 | Field and cleaning report | `DOCUMENTATION/field_and_cleaning_report.md` | Not started |

Submission structure (spec  13): `CPE15_MIDTERM_GROUPXX/` with `RAW/`, `CLEAN/`, `NOTEBOOK/`, `DOCUMENTATION/`. Confirm with the instructor whether `3GF` satisfies the `groupXX` naming convention.

---

## 2. Audit Findings (verified against the raw data)

### A. Identifier & Schema
- **8 malformed feature IDs**: letter `O` for `0` (`LUC_BO5_001`, `_006`, `_011`, `_014`), hyphen (`LUC-B08_036`), space (`LUC _B04_008`), prefix typo (`LIC_B04_014`), unpadded (`LUC_B04_20`). The notebook currently hard-codes only 3 of these.
- **Header case**: SW Maps exports `Latitude` / `Longitude`; the schema requires lowercase.
- **Extra columns**: files 9 and 10 have `Image` / `establishment_pic` columns (the latter is entirely empty). Every file also carries SW Maps GPS-quality columns (`Time`, `Horizontal Accuracy`, `HDOP`, `Satellites in Use`, `Fix ID`, `Averaged Count`) that the notebook currently drops via `usecols`.
- **Column order**: the notebook lists `collector` before `date_collected`; the schema order is `date_collected`, then `collector`.

### B. Duplicates and ID collisions (corrects the earlier plan)
- 62 surplus rows across 50 repeated IDs (112 rows involved). The earlier plan said 118; recheck that figure.
- **Files 6 and 8 share 37 IDs, but mostly for *different* establishments.** Example: `LUC_B04_005` is Irene's Sewing Shop in file 6 and San Luis Development Cooperative in file 8. Two collectors numbered Barangay 4 from 001 independently.
- The same real place can appear under different IDs (SLDC Mart 3 is `B04_026` in file 6 and `B04_003` in file 8; Camilon Dental Clinic is `B04_016` and `B04_007`; Campville's Bakery is `B04_015` and `B04_006`).
- 12 IDs are reused for different places inside a single file (5 in file 3, 2 in file 1, and others). One exact duplicate row exists (`LUC_B10_031`).
- Cross-file repeats to review (duplicate vs. genuine branch): Palawan Pawnshop, Pectos Bakery, Raquel Pawnshop, Abcede's Resto.
- 19 rows share coordinates with another row. Many are legitimate multi-tenant buildings (for example, four clinics at one point); do not drop these automatically.

### C. Missing values
`name` 23 (21 are in file 6), `street` 9, `operating_status` 5, `date_collected` 14, `collector` 2.

### D. Categorical standardization
- Category typos: `Professional Sevices` (9 rows), `Financial Services` (1 row).
- **Category/subcategory mismatches** (not covered before): Lote Fitness Gym tagged Restaurant; Ester Sari-Sari Store tagged Clothing; Professional Services with Lodge, Restaurant, Laundry, Dental Clinic; Financial with Entrepreneurship; Food and Dining with Sari Sari Store.
- About 100 rows use `Other` as the subcategory, many with a clear standard home (Boarding House, Laundry, Parts Shop, Printing Shop, Grocery). Some `remarks` already state the answer ("Meat shop", "Water Refilling Station").
- Near-duplicate subcategories: Grocery / Grocery Store, Laundry / Laundry Shop, Dental Clinic / Dentist, Sari Sari Store / Sari-Sari Store / Sari-sari Store.
- **Spec conflict**: the spec's vocabulary writes **"Sari Sari Store"** (unhyphenated). 107 rows already use it vs. 22 hyphenated. Decide before normalizing.
- `operating_status`: `Open`/`open`/`OPEN`/`Oepn`; `Closed`/`closed`/`CLOSED`/`close`/`Close`/`closel`; two non-status values (`closed on Saturday`, `8AM - 2AM`); 5 blank. About 105 rows are Closed.

### E. Streets (about 85 raw values, not the 30 originally estimated)
Beyond the 6 streets in the original checklist: Fidel Rada (5+ spellings), Marcos Tigla (including "Marcus"), Balintawak, Emilio Jacinto (some ALL CAPS), Bonifacio / A. Bonifacio, Mabini, G. Del Pilar, Hobart Dator / H. Dator, Lopez Jaena casing, `katipunan`, `plaridel`, "Conception", "Gil Rada", "D. Agular", "Streeg", "Stm", "Gen. Lucban"; house numbers inside the field ("129 Cadavez St."); an intersection ("San Luis Cor. G. Cadeliña"). Also verify that `G. Cadeliña` and `Don V. Cadeliña` are the same street.

### F. Dates
Raw formats: `DD/MM/YYYY` (majority), `YYYY_MM-DD`, `YYYY-MM-DD`, plus corrupt values:
- `10/03/2026` is month-first; `dayfirst=True` would silently turn it into 10 March 2026.
- `30/10/2026` is later than the collection window (Sep 28 to Oct 5, 2026).
- `03/10/2206`, `2026-20-03`, `2026-10_01`, and 14 blanks.
- SW Maps `Time` exists for all 767 rows and is the best source for validating and imputing dates.

### G. Excel / text damage
- `opening_hours`: six values read `24-Jul` (Excel converted "24/7" to a date). 103 distinct strings overall, including `6;30 am` and bare `9:00 am`.
- `contact_info`: read as floats (`425403261.0`), leading zeros lost, four phone formats mixed.

### H. Geolocation quality (new)
- 54 points have horizontal accuracy over 10 m (spec target is about 10 m or better); 29 of 37 points in file 5. Four are over 30 m: Alfamart 48 m, Oodles ni Utol 46 m, MV Store 46 m, ZUREA Hotel 33 m.
- 27 rows, all in file 9, have `Fix ID` = 0. Accuracy is good (1.5 to 2.5 m), so this is probably a receiver quirk, but verify.
- All 767 points fall inside the bounding box (Lat 14.1123 to 14.1188, Lon 121.5500 to 121.5586), so the box only catches gross errors.
- 17 rows have a barangay code in the ID that disagrees with the `barangay` column (many default to "Barangay 1").

### I. Coverage and ethics
- **Barangay 7 has zero records.** Barangay 3 has only 30 and Barangay 1 only 17 by ID code.
- ID sequence gaps: `B02_024`, `B08_045`, `B08_164`, five in B09, two in B10.
- `verified` is "Yes" on all 767 rows, which is hard to defend given the issues above.
- Spec  8: most `contact_info` values are 09XX mobile numbers; confirm they were publicly posted.
- Remarks to review: a wake ("lamayan", temporary, excluded by  4.2), and a remark about a seller's reaction when refusing to give a name.
- `remarks` is sometimes used as a subcategory note; a stray capitalized `Remarks` column (SW Maps) holds one value.

### J. Collector names
70 distinct strings, with variants such as `ARELLANO, Arvin L.`, `ARELLANO, Arvin, L.`, `ARELLANO, Arvin\n L.`; nickname variants (`HUTAMARES, CHEZKA` vs `HUTAMARES, Franchezka, M.`); at least one First-Last entry (`Mark Gabriel E. Susim`); 2 blanks.

---

## 3. Decisions Needed (record outcomes in the decision log)

| # | Decision | Options | Decision / rationale |
|---|---|---|---|
| D1 | Dedup strategy | Name + distance matching, then reassign unique IDs | _TBD_ |
| D2 | Barangay authority when ID and `barangay` disagree | Trust ID, or trust coordinates | _TBD_ |
| D3 | Spelling of Sari Sari Store | Spec form (unhyphenated) or hyphenated | _TBD_ |
| D4 | Meaning of `Closed` | Observed closed at visit time (recommended) vs. permanently closed | _TBD_ |
| D5 | Rows with no recoverable name | Drop and document, or keep with placeholder and `verified=No` | _TBD_ |
| D6 | Phone numbers | Keep only publicly posted numbers; blank the rest | _TBD_ |
| D7 | `verified` policy | Set `No` (or add `qa_flag`) for rows failing QA | _TBD_ |
| D8 | Barangay 7 | Out of scope vs. unsurveyed (document either way) | _TBD_ |
| D9 | Accuracy threshold | Flag over 10 m; decide whether to re-check, keep with flag, or exclude | _TBD_ |
| D10 | Street field rule | Primary street only; intersections and house numbers go to `location_description` | _TBD_ |

---

## 4. Revised Pipeline Architecture

```
Step 1: Load raw CSVs as strings (dtype=str), keep SW Maps GPS columns,
        add source_file column, export merged raw CSV
  │
Step 2: Audit (structure, nulls, duplicates, accuracy, barangay mismatches)
  │
Step 3: Schema + ID repair (regex, not hard-coded), lowercase lat/lon, merge Remarks/remarks
  │
Step 4: Standardize text: names, category/subcategory (lookup table), streets
        (canonical table), status, opening_hours, contact_info, collector (alias map)
  │
Step 5: Dates: parse explicitly, validate against collection window and SW Maps Time
  │
Step 6: Deduplicate by normalized name + proximity, resolve collisions,
        reassign unique feature_ids, write mapping table
  │
Step 7: Validate: barangay vs ID, accuracy flags, spatial plot, category/subcategory
        pairs, street list, dtypes, required-field completeness
  │
Step 8: Privacy / inclusion audit, set verified / qa_flag
  │
Step 9: Assertions (acceptance gate), export clean CSV, change log, data dictionary
```

### Dedup and ID strategy (Step 6 detail)
1. Normalize names (lowercase, strip punctuation and extra spaces) into a helper column.
2. Compute pairwise distance for records with similar names; treat as the same establishment if name similarity is high and distance is under a threshold (suggest 50 to 150 m, tune using the files 6 vs 8 pairs, which sit about 40 to 190 m apart).
3. Keep the most complete record, filling blanks from its twin (this also recovers many of the 21 unnamed rows in file 6).
4. Review same-name pairs across barangays manually (branch vs. duplicate).
5. After dedup, **reassign unique `feature_id`s** and keep an `old_id -> new_id` mapping file in `DOCUMENTATION/`.
6. Never "drop duplicate IDs" blindly.

### Geolocation QA (Step 7 detail)
- Flag `Horizontal Accuracy` over 10 m and over 30 m; flag `Fix ID` = 0.
- Plot all points colored by barangay to spot misplaced points (spec  9).
- Check same-street neighbors for coordinate outliers.

---

## 5. Documentation Plan

### Data dictionary (one row per field)
Definition, type, allowed values, coding rules, missing-value rule. Allowed values for `category`/`subcategory` come from the lookup table in Step 4. Include any added QA columns (`qa_flag`, accuracy, `source_file`) if they are in the clean CSV.

### Field and cleaning report outline
1. Study area and coverage by barangay (including Barangay 7 and any gaps, ID sequence gaps)
2. Collection dates (Sep 28 to Oct 5, 2026) and method (SW Maps, GPS stabilization practice)
3. Record counts at every step (767 raw -> after dedup -> after exclusions -> final)
4. Problems encountered and corrections (summarize sections 2A to 2J)
5. Decision log (section 3 table, completed)
6. Geolocation accuracy summary
7. Ethics and privacy handling
8. Limitations
9. Group contributions (records per collector, using the cleaned collector column)

---

## 6. Verification & Acceptance Criteria (spec  11)

1. Zero duplicate `feature_id` values in the clean CSV, and no duplicate establishments.
2. Zero missing values in required fields (`feature_id`, `name`, `category`, `subcategory`, `street`, `barangay`, `latitude`, `longitude`, `operating_status`, `date_collected`, `collector`, `verified`).
3. 100% of `category` values in the approved list; every (`category`, `subcategory`) pair in the lookup table.
4. All `date_collected` values in `YYYY-MM-DD` and inside the collection window.
5. Exact column names and order matching the spec schema.
6. Correct dtypes: text for IDs and contact, float for coordinates, date for `date_collected`.
7. Notebook runs top to bottom (Restart and Run All) with clean output.

---

## 7. Suggested Timeline

| Day | Focus |
|---|---|
| Oct 8 | Decisions D1 to D10; load as strings; ID repair; dates from SW Maps `Time` |
| Oct 9 | Category/subcategory lookup, street table, status/hours/phone, collector alias map |
| Oct 10 | Dedup and ID reassignment, geolocation QA and map, privacy audit, exports |
| Oct 11 | Data dictionary, report, folder structure, final run and assertions, submit |

---

## 8. Changes from the Previous Plan

- Dedup by `feature_id` replaced with name + proximity matching and ID reassignment.
- Duplicate-ID count corrected (62 surplus rows across 50 IDs, not 118).
- Added geolocation QA, category/subcategory validation, name cleanup, Excel-damage repair, privacy and inclusion audit, coverage documentation, `verified` policy, and decision log.
- Street variation count raised from 30+ to about 85 raw values.
- Dates: use SW Maps `Time` for validation and imputation instead of collector batch dates.