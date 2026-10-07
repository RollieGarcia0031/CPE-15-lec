# Data Cleaning Checklist: Lucban Establishment Field Data (BSCPE 3GF)

Use this checklist to track the data cleaning, standardization, deduplication, and validation tasks for the CPE15 Midterm Project.

---

## 1. Schema & Attribute Setup
- [ ] Rename SW Maps coordinate columns from capitalized `Latitude` and `Longitude` to lowercase `latitude` and `longitude`.
- [ ] Verify all 16 required columns are present in the dataset in standard order:
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
- [ ] Replace letter `O` with digit `0` (e.g., `LUC_BO5_001` $\rightarrow$ `LUC_B05_001`).
- [ ] Replace hyphens with underscores (e.g., `LUC-B08_036` $\rightarrow$ `LUC_B08_036`).
- [ ] Remove leading/internal spaces (e.g., `LUC _B04_008` $\rightarrow$ `LUC_B04_008`).
- [ ] Fix prefix typos (e.g., `LIC_B04_014` $\rightarrow$ `LUC_B04_014`).
- [ ] Zero-pad sequence numbers to 3 digits (e.g., `LUC_B04_20` $\rightarrow$ `LUC_B04_020`).
- [ ] Enforce standard pattern matching `^LUC_B\d{2}_\d{3}$`.

---

## 3. Category & Subcategory Normalization
- [ ] **Major Categories**:
  - [ ] Fix `Professional Sevices` $\rightarrow$ `Professional Services`.
  - [ ] Fix `Financial Services` $\rightarrow$ `Financial`.
  - [ ] Verify all category values belong to standard list (`Food and Dining`, `Retail`, `Accommodation`, `Financial`, `Health`, `Personal Services`, `Automotive`, `Professional Services`, `Government`, `Tourism`, `Other`).
- [ ] **Subcategories**:
  - [ ] Normalize `Sari Sari Store` and `Sari-sari Store` $\rightarrow$ `Sari-Sari Store`.
  - [ ] Standardize spelling and title casing across all subcategories (e.g., `Bakery`, `Eatery`, `Pharmacy`, `Barbershop`).

---

## 4. Operating Status & Schedule Cleaning
- [ ] Standardize open statuses (`open`, `OPEN`, `Oepn` $\rightarrow$ `Open`).
- [ ] Standardize closed statuses (`closed`, `close`, `Close`, `CLOSED`, `closel` $\rightarrow$ `Closed`).
- [ ] Relocate non-standard status notes (`closed on Saturday`, `8AM - 2AM`) into `opening_hours` and set `operating_status` to `Open` or `Closed`.

---

## 5. Street Name Standardization
- [ ] **A. Racelis Avenue**: Normalize `A. Racelis`, `Racelis`, `Armando Racelis Avenue`, `A. Racelis Avenue` $\rightarrow$ `A. Racelis Avenue`.
- [ ] **La Purisima Concepcion**: Normalize `La Purisma Concepcion`, `La Purisima Conception` $\rightarrow$ `La Purisima Concepcion`.
- [ ] **Gomburza Street**: Normalize `Gomburza`, `Gomburza Street` $\rightarrow$ `Gomburza Street`.
- [ ] **General Lukban Street**: Normalize `Gen. Lukban`, `General Lukban` $\rightarrow$ `General Lukban Street`.
- [ ] **Don V. Cadeliña**: Normalize `Don V. Cadelina`, `G.Cadeliña`, `G. Cadeliña` $\rightarrow$ `Don V. Cadeliña`.
- [ ] **Quezon Avenue**: Normalize `Quezon avenue` $\rightarrow$ `Quezon Avenue`.
- [ ] Fill in missing street values using spatial location or landmark notes where available.

---

## 6. Collector & Date Formatting
- [ ] **Collector Names**:
  - [ ] Trim trailing commas (e.g., `GONZALES, Louis,` $\rightarrow$ `Gonzales, Louis`).
  - [ ] Remove inline newlines (e.g., `ARELLANO, Arvin\n L.` $\rightarrow$ `ARELLANO, Arvin L.`).
  - [ ] Normalize format to `LASTNAME, Firstname M.` with consistent title casing.
- [ ] **Dates (`date_collected`)**:
  - [ ] Convert mixed date formats (`DD/MM/YYYY`, `YYYY_MM-DD`) to `YYYY-MM-DD`.
  - [ ] Correct invalid years/months (e.g., year `2206` $\rightarrow$ `2026-10-03`, month `20` $\rightarrow$ `2026-10-03`).
  - [ ] Impute missing date values based on collector batch dates.

---

## 7. Deduplication & Data Merging
- [ ] **Overlapping Records**:
  - [ ] Resolve duplicate entries between `raw_dataset_6.csv` and `raw_dataset_8.csv` for Barangay 4.
  - [ ] Prioritize records with complete `name`, `operating_status`, and `opening_hours` over incomplete/blank rows.
- [ ] **Duplicate Feature IDs**: Drop duplicate rows keeping the most complete record.
- [ ] **Duplicate Coordinates**: Check entries sharing identical latitude/longitude coordinates.

---

## 8. Cross-Field & Geospatial Validation
- [ ] Validate `feature_id` barangay code matches encoded `barangay` (e.g. `LUC_B05_xxx` must correspond to `Barangay 5`).
- [ ] Validate latitude values fall within ~14.1100°N to 14.1200°N.
- [ ] Validate longitude values fall within ~121.5500°E to 121.5650°E.
- [ ] Verify `verified` column is explicitly set to `Yes` or `No` for all rows.

---

## 9. Final Output Generation & Verification
- [ ] Export `lucban_establishments_3GF_raw.csv` (merged 767 raw records).
- [ ] Export `lucban_establishments_3GF_clean.csv` (fully cleaned and deduplicated dataset).
- [ ] Run full notebook test execution (`lucban_data_cleaning_3GF.ipynb`) with clean run output.
- [ ] Confirm 0 missing values in required attributes.
- [ ] Confirm 0 duplicate feature IDs in cleaned output.
