# Data Cleaning & Validation Plan: Lucban Establishment Field Data (BSCPE 3GF)

This document details the data cleaning plan, quality audit findings, and reproducible notebook workflow for the **CPE15 Midterm Project: Field Data Collection and Cleaning**.

---

## 1. Executive Summary & Deliverable Requirements

Per the midterm project specification (`CPE15_Midterm_Project_Field_Data_Collection_and_Cleaning.docx`), the BSCPE 3GF group must process 10 raw field datasets (`raw_dataset_1.csv` through `raw_dataset_10.csv`, total 767 entries) into a clean, verified base dataset.

### Required Deliverables:
1. **Original SW Maps Export**: Unmodified field collection project exports.
2. **Raw CSV (`lucban_establishments_3GF_raw.csv`)**: Merged raw dataset containing all field collection records.
3. **Clean CSV (`lucban_establishments_3GF_clean.csv`)**: Fully standardized, deduplicated, and validated dataset with 16 required columns.
4. **Cleaning Notebook (`lucban_data_cleaning_3GF.ipynb`)**: Executable Jupyter Notebook demonstrating audit, cleaning, validation, and export steps.
5. **Data Dictionary**: Field specifications, data types, allowed values, and missing value rules.
6. **Field and Cleaning Report**: Method documentation, coverage details, record counts, and limitation notes.

---

## 2. Summary of Identified Data Quality Issues

An empirical audit of all 767 records across the 10 raw CSV files revealed the following issues:

### A. Identifier & Schema Formatting Anomalies
- **Feature ID Syntax Errors**:
  - Letter `O` instead of digit `0`: `LUC_BO5_001` $\rightarrow$ `LUC_B05_001`
  - Hyphens instead of underscores: `LUC-B08_036` $\rightarrow$ `LUC_B08_036`
  - Spaces: `LUC _B04_008` $\rightarrow$ `LUC_B04_008`
  - Prefix typos: `LIC_B04_014` $\rightarrow$ `LUC_B04_014`
  - Unpadded sequence numbers: `LUC_B04_20` $\rightarrow$ `LUC_B04_020`
- **Header Case Sensitivity**: SW Maps exports capitalize `Latitude` and `Longitude`. Schema requires lowercase `latitude` and `longitude`.

### B. Duplication & Missing Data
- **Duplicate Feature IDs (118 occurrences)**:
  - Overlap between `raw_dataset_6.csv` and `raw_dataset_8.csv` in Barangay 4. `raw_dataset_6` contains unnamed entries while `raw_dataset_8` contains complete named entries for the same feature IDs.
  - Duplicate rows within individual files (e.g. `raw_dataset_7.csv` and `raw_dataset_9.csv`).
- **Missing Required Attributes**:
  - `name`: 23 missing establishment names.
  - `street`: 9 missing street values.
  - `operating_status`: 5 missing status values.
  - `date_collected`: 14 missing/corrupted values.
  - `collector`: 2 missing values.

### C. Text & Categorical Standardization
- **Category Labels**:
  - `Professional Sevices` $\rightarrow$ `Professional Services`
  - `Financial Services` $\rightarrow$ `Financial`
- **Subcategory Labels**:
  - `Sari Sari Store` / `Sari-sari Store` $\rightarrow$ `Sari-Sari Store`
- **Operating Status**:
  - `open`, `OPEN`, `Oepn` $\rightarrow$ `Open`
  - `closed`, `close`, `Close`, `CLOSED`, `closel` $\rightarrow$ `Closed`
  - Non-standard notes (`closed on Saturday`, `8AM - 2AM`) relocated to `opening_hours`.
- **Street Names (30+ variations)**:
  - `A. Racelis` / `Racelis` / `Armando Racelis Avenue` / `A. Racelis Avenue` $\rightarrow$ `A. Racelis Avenue`
  - `La Purisma Concepcion` / `La Purisima Conception` $\rightarrow$ `La Purisima Concepcion`
  - `Gomburza` $\rightarrow$ `Gomburza Street`
  - `Gen. Lukban` / `General Lukban` $\rightarrow$ `General Lukban Street`
  - `Don V. Cadelina` / `G.Cadeliña` $\rightarrow$ `Don V. Cadeliña`
- **Collector Names**:
  - 71 raw formatting variations cleaned of newlines (`ARELLANO, Arvin\n L.`), trailing commas, whitespace, and mixed capitalization.
- **Dates**:
  - Mixed date string formats (`DD/MM/YYYY`, `YYYY_MM-DD`) and invalid dates (e.g. year `2206`, month `20`).

### D. Geospatial Integrity
- Mismatches between `feature_id` barangay codes (e.g. `LUC_B05_xxx`) and the `barangay` column (e.g. `Barangay 1`).
- Verification of coordinates within the Poblacion, Lucban bounding box (~Lat 14.110°N - 14.120°N, Lon 121.550°E - 121.565°E).

---

## 3. Data Cleaning Pipeline Architecture

The Jupyter Notebook `lucban_data_cleaning_3GF.ipynb` is structured into 7 sequential steps:

```
Step 1: Import Raw CSV Files & Setup DataFrames
  │
Step 2: Perform Data Audits (Structure, Nulls, Duplicates)
  │
Step 3: Standardize Schema Headers & Feature ID Regex
  │
Step 4: Standardize Categories, Subcategories, Streets, & Collectors
  │
Step 5: Deduplicate Records (Prioritizing Complete Information)
  │
Step 6: Validate Spatial Bounds & Cross-Field Consistency
  │
Step 7: Export Raw CSV, Clean CSV, and Data Dictionary
```

---

## 4. Verification & Quality Acceptance Criteria

To pass the midterm acceptance gate (Section 11 of project guide):
1. Zero duplicate `feature_id` values in `lucban_establishments_3GF_clean.csv`.
2. Zero missing values in required Section 5 fields (`feature_id`, `name`, `category`, `subcategory`, `street`, `barangay`, `latitude`, `longitude`, `operating_status`, `date_collected`, `collector`, `verified`).
3. 100% adherence to standard major category classifications.
4. Clean date format (`YYYY-MM-DD`) for all records.
5. Exact column header matching with Section 5 schema.
