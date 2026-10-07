# Data Cleaning Checklist (Revised): Lucban Establishment Field Data (BSCPE 3GF)

To whoever reads this, wag tamarin magbasa alam kong mahab 'to so please, tyaga lang pre.

Target submission: **Oct 11, 2026**.

---

## 0. Decisions (record answers in the decision log first)
- [ ] **NEW** D1: Dedup strategy confirmed (name + proximity, then reassign unique IDs)
- [ ] **NEW** D2: Barangay authority when ID and `barangay` disagree (ID or coordinates)
- [ ] **NEW** D3: Spelling of `Sari Sari Store` (spec form is unhyphenated; 107 rows use it vs. 22 hyphenated)
- [ ] **NEW** D4: Definition of `Closed` (about 105 rows)
- [ ] **NEW** D5: Handling of rows with no recoverable name
- [ ] **NEW** D6: Phone number policy (publicly posted only)
- [ ] **NEW** D7: `verified` policy for rows failing QA
- [ ] **NEW** D8: Barangay 7 status (out of scope vs. unsurveyed)
- [ ] **NEW** D9: Accuracy threshold and action for points over 10 m
- [ ] **NEW** D10: Street field rule (primary street only; house numbers and intersections go to `location_description`)
- [ ] **NEW** Confirm file naming (`3GF` vs. `groupXX`) with the instructor

---

## 1. Loading & Schema Setup
- [ ] **REVISED** Read all CSVs with `dtype=str` (prevents float phone numbers and lost leading zeros)
- [ ] **NEW** Keep SW Maps GPS columns (`Time`, `Horizontal Accuracy`, `HDOP`, `Satellites in Use`, `Fix ID`, `Averaged Count`) for QA instead of dropping them at load
- [ ] **NEW** Add a `source_file` column to the merged raw data for traceability
- [ ] **NEW** Merge the stray capitalized `Remarks` column (1 value) into `remarks`; handle `Image` / `establishment_pic` columns (files 9 and 10)
- [ ] Rename `Latitude` / `Longitude` to lowercase `latitude` / `longitude`
- [ ] **REVISED** Output column order matches the spec (`... contact_info`, `date_collected`, `collector`, `remarks`, `verified`); the notebook currently has `collector` before `date_collected`
- [ ] Verify all 16 required columns are present:
  - [ ] `feature_id` (Text)
  - [ ] `name` (Text)
  - [ ] `category` (Text)
  - [ ] `subcategory` (Text)
  - [ ] `street` (Text)
  - [ ] `barangay` (Text)
  - [ ] `latitude` (Decimal)
  - [ ] `longitude` (Decimal)
  - [ ] `location_description` (Text)
  - [ ] `operating_status` (Text)
  - [ ] `opening_hours` (Text)
  - [ ] `contact_info` (Text)
  - [ ] `date_collected` (Date YYYY-MM-DD)
  - [ ] `collector` (Text)
  - [ ] `remarks` (Text)
  - [ ] `verified` (Text)

---

## 2. Identifier Standardization (`feature_id`)
- [ ] **REVISED** Repair IDs with regex or rules, not a hard-coded dict (all 8 malformed IDs; the notebook currently fixes only 3):
  - [ ] Replace letter `O` with digit `0` (`LUC_BO5_001`, `_006`, `_011`, `_014`)
  - [ ] Replace hyphens with underscores (`LUC-B08_036`)
  - [ ] Remove spaces (`LUC _B04_008`)
  - [ ] Fix prefix typos (`LIC_B04_014`)
  - [ ] Zero-pad sequence numbers to 3 digits (`LUC_B04_20`)
- [ ] Enforce pattern `^LUC_B\d{2}_\d{3}$`
- [ ] **NEW** After deduplication, reassign unique `feature_id`s and save an `old_id -> new_id` mapping file

---

## 3. Category & Subcategory Normalization
- [ ] Fix `Professional Sevices` -> `Professional Services` (done in notebook)
- [ ] Fix `Financial Services` -> `Financial` (**missing** from the notebook's `category_fixes`)
- [ ] Verify every category is in the approved list (`Food and Dining`, `Retail`, `Accommodation`, `Financial`, `Health`, `Personal Services`, `Automotive`, `Professional Services`, `Government`, `Tourism`, `Other`)
- [ ] **REVISED** Normalize `Sari Sari Store` / `Sari-sari Store` / `Sari-Sari Store` to the form chosen in D3
- [ ] **NEW** Build a category -> subcategory lookup table (also feeds the data dictionary)
- [ ] **NEW** Merge near-duplicate subcategories: Grocery / Grocery Store, Laundry / Laundry Shop, Dental Clinic / Dentist
- [ ] **NEW** Fix category/subcategory mismatches, for example:
  - [ ] Lote Fitness Gym tagged Restaurant
  - [ ] Ester Sari-Sari Store tagged Clothing
  - [ ] Professional Services with Lodge, Restaurant, Laundry, Dental Clinic
  - [ ] Personal Services with Clothing, Electronics, Souvenir
  - [ ] Financial with Entrepreneurship
  - [ ] Food and Dining with Sari Sari Store
  - [ ] Retail with Eatery, Restaurant, Bakery
- [ ] **NEW** Recode `Other` categories and subcategories where a standard home exists (about 100 rows; use `remarks` hints such as "Meat shop", "Water Refilling Station")
- [ ] **NEW** Assert every (`category`, `subcategory`) pair exists in the lookup table

---

## 4. Names
- [ ] **NEW** Trim whitespace and fix inline newlines (2 names)
- [ ] **NEW** Standardize casing (ALL CAPS vs. Title Case variants such as `SLDC MART 3` / `SLDC Mart 3`)
- [ ] **NEW** Recover missing names (23 rows, 21 in file 6) from their twin records during dedup
- [ ] **NEW** Apply D5 to rows still unnamed (including the seller-refused-name remark)

---

## 5. Operating Status & Schedule Cleaning
- [ ] Standardize open statuses (`open`, `OPEN`, `Oepn` -> `Open`) (done in notebook)
- [ ] Standardize closed statuses (`closed`, `close`, `Close`, `CLOSED`, `closel` -> `Closed`) (done in notebook)
- [ ] Move non-status notes (`closed on Saturday`, `8AM - 2AM`) into `opening_hours` and set status
- [ ] **NEW** Decide values for the 5 blank `operating_status` rows (D4 rule)
- [ ] **NEW** Repair the six `opening_hours` values that read `24-Jul` -> `24/7`
- [ ] **NEW** Normalize `opening_hours` to one format (e.g. `8:00 AM to 8:00 PM`); fix `6;30 am`, bare `9:00 am`, `24hrs` / `24/7` variants

---

## 6. Contact Info & Privacy
- [ ] **NEW** Keep `contact_info` as text; restore leading zeros; strip `.0` suffixes
- [ ] **NEW** Normalize phone formats (`9XXXXXXXXX`, `09XXXXXXXXX`, `0947-893-1163`, `(042) 540-6177`) to one style
- [ ] **NEW** Audit mobile numbers against spec  8 (public business numbers only) and apply D6
- [ ] **NEW** Review `remarks` for personal or sensitive notes (owner or seller comments) and neutralize them
- [ ] **NEW** Check  4.2 exclusions: temporary or non-establishment records (for example the "lamayan" / wake remark) and records outside the study area

---

## 7. Street Name Standardization
- [ ] **REVISED** Build one canonical street list and map **all** raw variants (about 85 raw values) to it, then assert every value is in the list
- [ ] **A. Racelis Avenue**: `A. Racelis`, `Racelis`, `Racelis Street`, `Armando Racelis Avenue`, `A. Racelis Avenue`
- [ ] **La Purisima Concepcion**: `La Purisma Concepcion`, `La Purisima Conception`, `la Purisima Conception`, `Conception`, `Conception Street`
- [ ] **Gomburza Street**: `Gomburza`, `Gomburza St.`, `Gomburza Street`
- [ ] **General Lukban Street**: `Gen. Lukban`, `Gen. Lucban`, `Gen Lukban`, `General Lukban`, `General Lukban St.`
- [ ] **Don V. Cadeliña**: `Don V. Cadelina`, `Don V . Cadelina`, `Don V. Cadeliña Streeg`, `G.Cadeliña`, `G. Cadeliña` (**verify** `G. Cadeliña` is the same street)
- [ ] **Quezon Avenue**: `Quezon avenue`
- [ ] **NEW Fidel Rada**: `Fidel Rada`, `Fidel Rada St.`, `Fidel rada St`, `Fidel Rada Stm`, `Fidel Rada Street`, and check `Gil Rada`
- [ ] **NEW Marcos Tigla**: `Marcos Tigla St.`, `Marcos Tigla Street`, `Marcos Tigla street`, `Marcos Tigla`, `Marcus Tigla St`
- [ ] **NEW Balintawak**: `Balintawak`, `Balintawak St.`, `Balintawak st.`, `Balintawak Street`
- [ ] **NEW Emilio Jacinto**: `Emilio Jacinto`, `Emilio Jacinto St.`, `EMILIO JACINTO ST.`
- [ ] **NEW Bonifacio**: `Bonifacio`, `A. Bonifacio`, `Bonifacio Street`, `A. Bonifacio Street`
- [ ] **NEW Mabini**: `Mabini`, `Apolinario Mabini`, `A. Mabini Street`, `A. Mabini St.`
- [ ] **NEW** Other casing and typo fixes: `katipunan`, `plaridel`, `Lopez jaena`, `D. Agular`, `Rizal Ave.`, `G. Del Pilar Street`, `H. Dator` / `Hobart Dator Street`, `A. Regidor` / `Regidor`
- [ ] **NEW** Move house numbers (`129 Cadavez St.`, `15 Hobart Dator St.`) and intersections (`San Luis Cor. G. Cadeliña`) out of `street` (D10)
- [ ] Fill the 9 missing `street` values from nearby points or landmark notes

---

## 8. Collector & Date Formatting
- [ ] **Collector names**
  - [ ] Trim trailing commas and whitespace; remove inline newlines
  - [ ] **REVISED** Build a manual alias map (70 distinct strings, many being the same person; nicknames like `HUTAMARES, CHEZKA` vs `HUTAMARES, Franchezka, M.` cannot be fixed by regex)
  - [ ] Normalize to `LASTNAME, Firstname M.`; convert First-Last entries (`Mark Gabriel E. Susim`)
  - [ ] Fill or resolve the 2 blank collectors
- [ ] **Dates (`date_collected`)**
  - [ ] **REVISED** Parse explicitly per format, not with `dayfirst=True` on mixed strings
  - [ ] Convert `DD/MM/YYYY`, `YYYY_MM-DD`, `2026-10_01` to `YYYY-MM-DD`
  - [ ] **NEW** Fix `10/03/2026` (month-first; would be misread as 10 March)
  - [ ] **NEW** Fix `30/10/2026` (outside the collection window)
  - [ ] Correct `03/10/2206` and `2026-20-03` to `2026-10-03`
  - [ ] **REVISED** Impute the 14 missing dates from the SW Maps `Time` column (present on all 767 rows) instead of collector batch dates
  - [ ] **NEW** Assert all dates fall inside the collection window (Sep 28 to Oct 5, 2026)

---

## 9. Deduplication & ID Collisions
- [ ] **REVISED** Do **not** drop duplicates by `feature_id` alone. In files 6 and 8 the shared IDs are mostly different establishments (two collectors each numbered B04 from 001)
- [ ] **NEW** Create a normalized-name helper column
- [ ] **NEW** Match records by name similarity + distance; confirm the distance threshold using the files 6 vs 8 pairs (about 40 to 190 m apart)
- [ ] Merge matched records, keeping the most complete values and filling blanks from the twin
- [ ] **NEW** Resolve ID reuse inside single files (12 IDs, for example 5 in file 3, 2 in file 1)
- [ ] **NEW** Remove the exact duplicate row `LUC_B10_031`
- [ ] **NEW** Review cross-file repeats manually: Palawan Pawnshop, Pectos Bakery, Raquel Pawnshop, Abcede's Resto, Cebuana Lhuillier, Potato Corner (duplicate vs. genuine branch)
- [ ] Check records sharing identical coordinates (19 rows); **keep** legitimate multi-tenant buildings
- [ ] **NEW** Reassign unique `feature_id`s and export the `old_id -> new_id` mapping
- [ ] **NEW** Log counts at each step (767 raw -> after dedup -> after exclusions -> final)

---

## 10. Cross-Field & Geospatial Validation
- [ ] **REVISED** Barangay vs. ID code: resolve the 17 mismatches using the rule from D2 (many are defaulted to "Barangay 1")
- [ ] Validate latitude within about 14.1100 to 14.1200 and longitude within about 121.5500 to 121.5650 (currently all pass; this catches only gross errors)
- [ ] **NEW** Flag `Horizontal Accuracy` over 10 m (54 points; 29 of 37 in file 5) and over 30 m (Alfamart, Oodles ni Utol, MV Store, ZUREA Hotel); apply D9
- [ ] **NEW** Check `Fix ID` = 0 rows (27, all in file 9)
- [ ] **NEW** Plot all points (colored by barangay) and inspect misplaced points
- [ ] **NEW** Check coordinate outliers against same-street neighbors
- [ ] **REVISED** Set `verified` according to D7; the raw data has "Yes" on all 767 rows, so confirm explicit `Yes` / `No` values after QA
- [ ] **NEW** Enforce dtypes: text for IDs and contact, float for coordinates, date for `date_collected`, categorical for category fields

---

## 11. Coverage Review
- [ ] **NEW** Confirm and document Barangay 7 (zero records) per D8
- [ ] **NEW** Document thin coverage: Barangay 3 (30 records), Barangay 1 (17 by ID code)
- [ ] **NEW** Document ID sequence gaps (`B02_024`, `B08_045`, `B08_164`, five in B09, two in B10)
- [ ] Document any areas not surveyed and the reasons (spec  3)

---

## 12. Final Output Generation & Verification
- [ ] Export `lucban_establishments_3GF_raw.csv` (merged 767 raw records, with `source_file`)
- [ ] Export `lucban_establishments_3GF_clean.csv` (cleaned and deduplicated)
- [ ] Confirm 0 missing values in required attributes
- [ ] Confirm 0 duplicate feature IDs and no duplicate establishments
- [ ] **NEW** Add `assert` checks in the notebook for the acceptance gate (categories, pairs, streets, dates, dtypes, column order)
- [ ] **NEW** Export a change log (row, field, old value, new value, reason)
- [ ] Run the full notebook with Restart and Run All; clean output
- [ ] **NEW** Tidy the notebook (remove the duplicate `category.value_counts()` cell and the empty last cell)

---

## 13. Documentation & Submission (spec  10 and  13)
- [ ] **NEW** Data dictionary: definition, type, allowed values, coding rules, and missing-value rule for every field
- [ ] **NEW** Field and cleaning report:
  - [ ] Coverage by barangay and gaps
  - [ ] Collection dates and method
  - [ ] Record counts at each step
  - [ ] Problems encountered and corrections
  - [ ] Completed decision log (D1 to D10)
  - [ ] Geolocation accuracy summary
  - [ ] Ethics and privacy handling
  - [ ] Limitations
  - [ ] Group contributions (records per collector, from the cleaned collector column)
- [ ] **NEW** Preserve the original SW Maps export unmodified in `RAW/`
- [ ] **NEW** Build the submission folder `CPE15_MIDTERM_GROUPXX/` with `RAW/`, `CLEAN/`, `NOTEBOOK/`, `DOCUMENTATION/`
- [ ] **NEW** Check that file names follow the prescribed convention; no screenshots in place of datasets or notebooks