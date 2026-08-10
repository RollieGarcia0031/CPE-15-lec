# CPE15 — ANSWERS: Week 4 and Week 5 Notebook Activities

Solutions, code, and short interpretations for every **Practice task**, **Exit ticket**, and **Independent challenge** in:

1. `04_Week_04_Pandas_Data_Wrangling.ipynb`
2. `05_Week_05_Native_Python_Data_Extraction.ipynb`

Solutions assume the notebook cells above each task have already been run (variables such as `energy`, `clean_energy`, `log_pattern`, `text_path`, `raw_dir`, `clean_dir` are in scope).

---

# Week 4 — pandas Data Organization and Wrangling

## Practice task 1 — Labeled data structures

**Task.** Create a labeled Series and a mixed-type DataFrame for three campus stations, then inspect labels, shape, dtypes, missingness, and duplicate rows before cleaning.

```python
import numpy as np
import pandas as pd

# Labeled Series: one variable, labeled index, unit-bearing name
stations_series = pd.Series(
    [229.1, 231.0, 228.4],
    index=["CEN", "Library", "Gym"],
    name="voltage_v",
)
print(stations_series)

# Mixed-type DataFrame: one row = one campus station observation
campus = pd.DataFrame(
    {
        "station": ["CEN", "Library", "Gym"],
        "voltage_v": [229.1, 231.0, None],
        "current_a": [12.4, 8.7, 9.3],
        "active": [True, True, False],
    }
)

# Structural inspection BEFORE cleaning
print("index:", campus.index.tolist())
print("shape:", campus.shape)
print("dtypes:\n", campus.dtypes, sep="")
print("missing:\n", campus.isna().sum(), sep="")
print("duplicate_rows:", int(campus.duplicated().sum()))
```

**Interpretation.** The Series is one labeled variable (voltage_v in volts); the DataFrame is a 3×4 mixed-type table (object, float64, float64, bool). One `voltage_v` value is missing (NaN), no rows are exact duplicates. One row = one campus station, so `voltage_v` is a measurement in V and `current_a` in A. Assumption: `None` genuinely means "not measured", not zero.

---

## Practice task 2 — Cleaning types and text

**Task.** Clean a column containing padded numeric text and one invalid token using string methods and `pd.to_numeric(errors='coerce')`; count and preserve conversion failures.

```python
raw_values = pd.Series([" 3.91 ", "not_available", "3.44"], name="battery_v")

cleaned = raw_values.str.strip()                 # trim padding
numeric = pd.to_numeric(cleaned, errors="coerce")  # invalid token -> NaN

print(pd.DataFrame({"raw": raw_values, "clean": cleaned, "numeric": numeric}))
print("conversion failures:", int(numeric.isna().sum()))
```

**Interpretation.** Two padded strings become floats (3.91, 3.44) and the invalid token `not_available` becomes NaN (1 conversion failure). The failure is counted and preserved as missing rather than silently dropped, so the data-quality decision remains auditable. Assumption: `errors="coerce"` (retain-and-audit) is preferred over `errors="raise"` in exploratory work.

---

## Practice task 3 — Selection and filtering

**Task.** Select the same DataFrame subset once with `.loc`, once with `.iloc`, and once with a Boolean mask; explain whether labels, positions, or conditions define each result.

```python
# .loc — LABEL/CONDITION based rule: keep CEN building rows, 2 columns
sel_loc = energy.loc[energy["building"].eq("CEN"), ["timestamp", "voltage_v"]]

# .iloc — POSITION based slice: first 2 rows, first 3 columns
sel_iloc = energy.iloc[:2, :3]

# Boolean mask — CONDITION based rule: voltage within plausible 180-260 V
mask = energy["voltage_v"].between(180, 260)
sel_mask = energy.loc[mask, ["timestamp", "voltage_v"]]

print(".loc (CEN rows, 2 cols):\n", sel_loc, sep="")
print(".iloc (first 2x3 block):\n", sel_iloc, sep="")
print("mask retained/rejected:", int(mask.sum()), int((~mask).sum()))
```

**Interpretation.** `.loc` is defined by labels/conditions (`building == 'CEN'`), so it survives sorting. `.iloc` is defined by integer positions (first 2 rows × first 3 columns), so it is order-dependent. The Boolean mask states a real data rule (voltage in 180–260 V); it retains 5 of 6 rows and rejects the implausible 999 V row. Assumption: 180–260 V is an illustrative plausible range for the teaching data.

---

## Practice task 4 — Derived columns, drop, set index, and reset index

**Task.** Create a unit-bearing derived column, remove one temporary field with `drop`, set a timestamp index, and reset it while checking that the row count stays unchanged.

```python
# 1) Derived, unit-bearing column (apparent power in VA, V * A)
energy["apparent_power_va"] = energy["voltage_v"] * energy["current_a"]

# 2) Temporary field added then removed with drop
tmp = energy.assign(teaching_note="demo")
without_tmp = tmp.drop(columns=["teaching_note"])
print("temporary column removed:", "teaching_note" not in without_tmp.columns)

# 3) Set timestamp index, then reset it back to a column
indexed = energy.set_index("timestamp")
restored = indexed.reset_index()

print("index name:", indexed.index.name)
print("index unique:", indexed.index.is_unique)
print("restored first column:", restored.columns[0])
print("row count unchanged:", len(restored) == len(energy))
```

**Interpretation.** The derived column `apparent_power_va` = voltage × current (V·A) keeps units in the name; the missing current stays missing (NaN propagates, not silently 0). `drop` removes only the temporary teaching field. `set_index("timestamp")` makes timestamp the row label (not unique — timestamps repeat across buildings), and `reset_index()` restores it as the first column with no change to the 6-row count.

---

## Practice task 5 — Missing data

**Task.** Compare dropping incomplete rows with group-median imputation on the same table; flag imputed values and explain how each choice changes the evidence base.

```python
# Choice A: drop incomplete rows
dropped = energy.dropna(subset=["current_a"])
print(f"dropna: retained {len(dropped)} of {len(energy)} rows")

# Choice B: group-median imputation, flagged
imputed = energy[["building", "current_a"]].copy()
imputed["was_imputed"] = imputed["current_a"].isna()
imputed["current_a"] = imputed.groupby("building")["current_a"].transform(
    lambda v: v.fillna(v.median())
)
print(imputed)
print("imputed values:", int(imputed["was_imputed"].sum()))
```

**Interpretation.** Dropping removes 1 of 6 rows: the evidence base shrinks to complete-current observations only (may bias summaries if missingness is systematic). Imputation keeps all 6 rows but replaces the missing CEN current with the median of observed CEN currents (12.75 A), and the `was_imputed` flag prevents the estimate from being mistaken for an observation. Both choices change what the data represents; dropping reduces the sample, imputation substitutes an estimate.

---

## Practice task 6 — GroupBy: split, apply, combine

**Task.** Group energy observations by building and use `agg` for one-row-per-building summaries and `transform` for row-aligned deviations; state the granularity of both outputs.

```python
# agg -> one row PER GROUP (granularity changes to group-level)
summary = clean_energy.groupby("building", as_index=False).agg(
    n=("building", "size"),
    mean_voltage_v=("voltage_v", "mean"),
)
print("agg (one row per building):\n", summary, sep="")

# transform -> row-ALIGNED result (same number of rows as input)
dev = clean_energy[["building", "voltage_v"]].copy()
dev["building_mean_v"] = dev.groupby("building")["voltage_v"].transform("mean")
dev["deviation_v"] = dev["voltage_v"] - dev["building_mean_v"]
print("transform (row-aligned):\n", dev, sep="")
```

**Interpretation.** `.agg` returns 2 rows (one per building) — group-level granularity, good for summary tables. `.transform` returns the same 5 rows as `clean_energy`, with the building mean repeated beside each observation so a per-row deviation (voltage − building mean) can be computed. Granularity: agg = 1 row/group; transform = 1 row per original observation.

---

## Practice task 7 — Merge and concatenate

**Task.** Perform a left merge with an indicator column and a row-wise concatenation of compatible batches; reconcile matched, left-only, and total result counts.

```python
# Left merge with indicator
left = pd.DataFrame({"station": ["A", "B", "C"], "value": [10, 20, 30]})
right = pd.DataFrame({"station": ["A", "B"], "region": ["North", "South"]})
merged = left.merge(right, on="station", how="left", indicator=True)

print(merged)
print("merge counts:", merged["_merge"].value_counts().to_dict())

# Row-wise concatenation of compatible batches
batch_1 = pd.DataFrame({"station": ["A"], "value": [10]})
batch_2 = pd.DataFrame({"station": ["B"], "value": [20]})
stacked = pd.concat([batch_1, batch_2], ignore_index=True)
print("concat:\n", stacked, sep="")

# Reconciliation: matched + left_only == total result rows
n_both = int((merged["_merge"] == "both").sum())
n_left = int((merged["_merge"] == "left_only").sum())
print("reconciles:", n_both, "+", n_left, "==", len(merged), "->", n_both + n_left == len(merged))
```

**Interpretation.** The left merge keeps all 3 left rows: stations A and B match (`both`), station C has no region (`left_only`, region NaN). Reconciliation confirms 2 + 1 = 3 total rows, so nothing was silently lost or duplicated. `concat` stacks two one-row batches into a single 2-row table because they share schema and granularity.

---

## Exit ticket (Week 4)

1. **When should `.loc` be preferred over `.iloc`?**
   `.loc` when selection is driven by row/column **labels or conditions** (e.g., `building == "CEN"`), because the rule survives sorting and inserted rows. `.iloc` only when integer **position** is intentionally meaningful (previews, partitions).

2. **Why should a merge specify the expected key relationship?**
   So pandas' `validate=` can catch unexpected cardinality (e.g., duplicate keys multiplying rows). Stating `one_to_one`/`many_to_one` turns silent, plausible-but-wrong joins into immediate errors.

3. **What information must accompany an imputation decision?**
   The method (e.g., group median), the group and count of values imputed, the justification/assumption, and a flag so imputed values are not presented as observed measurements.

---

## Independent challenge (Week 4)

**Task.** Create a DataFrame with ≥12 observations from two or more devices. Include one invalid value, one missing value, and a metadata table. Clean and validate, create two derived columns, produce a GroupBy summary, merge metadata with validation enabled, and report retained/excluded rows.

```python
import numpy as np
import pandas as pd

# 12 observations, 2 devices: one invalid (99.9), one missing (None)
sensor = pd.DataFrame(
    {
        "device": ["D1"] * 6 + ["D2"] * 6,
        "reading": [10.1, 10.3, 10.2, 99.9, 10.4, None,
                    20.1, 20.2, 20.3, 20.4, 20.1, 20.5],
        "current_a": [1.1, 1.2, 1.3, 1.4, 1.5, 1.6,
                      2.1, 2.2, 2.3, 2.4, 2.5, 2.6],
    }
)
metadata = pd.DataFrame(
    {"device": ["D1", "D2"], "location": ["North", "South"], "zone": ["A", "B"]}
)

# Validate: keep only plausible, non-missing readings (0-50)
valid = sensor["reading"].between(0, 50) & sensor["reading"].notna()
clean = sensor.loc[valid].copy()

# Two derived columns (unit-bearing)
clean["power_w"] = clean["reading"] * clean["current_a"]
clean["reading_deviation"] = clean["reading"] - clean.groupby("device")["reading"].transform("mean")

# GroupBy summary
summary = clean.groupby("device", as_index=False).agg(
    n=("device", "size"),
    mean_reading=("reading", "mean"),
    mean_power_w=("power_w", "mean"),
)

# Merge metadata with validation
enriched = summary.merge(metadata, on="device", validate="one_to_one")

print(f"input rows: {len(sensor)} | retained: {len(clean)} | excluded: {len(sensor) - len(clean)}")
print(enriched)
```

**Interpretation.** 12 input rows; the 99.9 reading fails the 0–50 plausible range and the `None` is missing, so 10 rows are retained and 2 excluded. Two derived columns (`power_w`, `reading_deviation`) were added; the GroupBy summary gives one row per device; the metadata merge is validated one-to-one. Every row is accounted for: 12 = 10 retained + 2 excluded.

---

# Week 5 — Native Python Data Extraction

## Practice task 1 — Extraction begins with explicit inputs

**Task.** Write an extraction contract for a small sensor source that names its format, encoding, record unit, required fields, units, validation rules, and intended output artifact.

```python
contract = {
    "source": "artifacts/week05_raw/sensor_log.txt",
    "format": "pipe-delimited text: timestamp | device | temp=X | status=Y",
    "encoding": "utf-8",
    "record_unit": "one sensor sample per line",
    "required_fields": ["timestamp", "device", "temperature_c", "status"],
    "units": {"temperature_c": "degrees Celsius"},
    "validation_rules": {
        "device": "must match CEN-\\d+",
        "temperature_c": "-10 <= value <= 60 (plausible range)",
        "status": "must be one of {ok, check, offline}",
    },
    "destination": "artifacts/week05_clean/valid_sensor_records.json",
}
contract
```

**Interpretation.** The contract makes every input expectation explicit before any parsing: what to read, in what format/encoding, what one record means, which fields are required, their units, the validation rules, and where the clean output will be written. Assumption: the source is treated as read-only (raw vs clean directories kept separate).

---

## Practice task 2 — CSV extraction

**Task.** Parse a CSV string with `csv.DictReader`, convert numeric fields safely, and preserve the line number and reason for every rejected record.

```python
import csv
import io

csv_text = (
    "device_id,zone,battery_v\n"
    "CEN-01,North,3.91\n"
    "CEN-02,South,not_available\n"
    "CEN-03,North,3.44\n"
)

parsed, rejected = [], []
for line_no, row in enumerate(csv.DictReader(io.StringIO(csv_text)), start=2):  # header = line 1
    try:
        battery = float(row["battery_v"])
    except ValueError:
        rejected.append(
            {
                "line": line_no,
                "device_id": row["device_id"],
                "reason": f"battery_v={row['battery_v']!r} is not numeric",
            }
        )
        battery = None
    row["battery_v"] = battery
    parsed.append(row)

print("parsed:", parsed)
print("rejected:", rejected)
```

**Interpretation.** Two rows parse cleanly with numeric `battery_v` (3.91, 3.44). The `not_available` value cannot convert to float, so the record is rejected **with its line number (3) and the reason** kept for audit instead of being silently dropped. Parsing succeeded for the file, but the invalid field is preserved as evidence.

---

## Practice task 3 — JSON extraction

**Task.** Load nested JSON containing one optional field, distinguish a missing key from an explicit `null`, and normalize valid records into a consistent schema.

```python
# Reuse the notebook's stations.json (CEN-03 has explicit null coordinates)
loaded = json.loads(json_path.read_text(encoding="utf-8"))

normalized = []
for station in loaded["stations"]:
    coords = station.get("coordinates")
    normalized.append(
        {
            "id": station["id"],                    # required key -> direct indexing
            "active": station.get("active", False),
            "coordinates": coords if isinstance(coords, list) else None,
            "coordinates_present": coords is not None,
        }
    )
print(normalized)
```

**Interpretation.** CEN-01 and CEN-02 return coordinate lists; CEN-03 has an **explicit `null`** (`None`), which is different from an **absent key**. Using `station["id"]` (direct indexing) treats a missing id as an error, while `.get("active", False)` handles the optional field with a documented default. All records are normalized to the same schema (id, active, coordinates, coordinates_present).

---

## Practice task 4 — Parsing semi-structured text

**Task.** Use a regular expression with named groups to parse three log lines, including one malformed line, and report matched and unmatched counts.

```python
lines = [
    "2026-08-10T09:05:00 | CEN-08 | temp=30.5 | status=OK",
    "bad timestamp and missing fields",               # malformed
    "2026-08-10T09:10:00 | CEN-09 | temp=31.0 | status=OK",
]

matched, unmatched = [], []
for line_no, line in enumerate(lines, start=1):
    m = log_pattern.match(line)   # log_pattern defined earlier in notebook
    if m is None:
        unmatched.append({"line": line_no, "raw": line})
        continue
    record = m.groupdict()                        # named capture groups
    record["temperature_c"] = float(record.pop("temperature"))
    record["status"] = record["status"].lower()
    matched.append(record)

print("matched:", len(matched), "| unmatched:", len(unmatched))
print("matched records:", matched)
print("unmatched records:", unmatched)
```

**Interpretation.** 2 lines match the compiled pattern and become named-field dictionaries (temperature converted to float, status lowercased); the malformed line is rejected as a whole and preserved with its line number (2) and raw content. A regex is a schema for one line — matching proves structure, not that the measurement is plausible.

---

## Practice task 5 — Schema and range validation

**Task.** Validate a record against required-field, type, and plausible-range rules; return all detected problems instead of stopping after the first failure.

```python
REQUIRED = {"device", "temperature_c", "status"}
ALLOWED_STATUS = {"ok", "check", "offline"}

def validate_record(record):
    errors = []
    missing = REQUIRED - set(record.keys())
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    if "temperature_c" in record:
        value = record["temperature_c"]
        if not isinstance(value, (int, float)):
            errors.append("temperature_c is not numeric")
        elif not (-10 <= value <= 60):
            errors.append("temperature outside plausible range")
    if record.get("status") not in ALLOWED_STATUS:
        errors.append("unknown status")
    return errors

cases = [
    {"device": "CEN-01", "temperature_c": 28.4, "status": "ok"},
    {"temperature_c": 99.0, "status": "offline"},              # missing device + range
    {"device": "CEN-02", "temperature_c": "hot", "status": "fine"},
]
for case in cases:
    print(case, "->", validate_record(case))
```

**Interpretation.** The validator returns a **list of every** problem per record rather than stopping at the first: the second record reports both `missing fields` and `temperature outside plausible range`; the third reports a wrong type and an unknown status. Collecting all errors (instead of True/False) makes the rejection reasons auditable and keeps one bad record from terminating the whole batch.

---

## Practice task 6 — Generator-based extraction

**Task.** Write a generator that yields valid records one at a time from a mixed-quality source and demonstrate that iteration does not require storing every parsed record simultaneously.

```python
def parse_valid_records(path, pattern=log_pattern):
    with path.open(encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            m = pattern.match(line.strip())
            if m is None:
                continue  # skip malformed lines, no storage
            record = m.groupdict()
            record["temperature_c"] = float(record.pop("temperature"))
            record["status"] = record["status"].lower()
            yield record

stream = parse_valid_records(text_path)
print("first yield:", next(stream))
print("second yield:", next(stream))
print("remaining after two yields:", sum(1 for _ in stream))
```

**Interpretation.** The generator pauses at each `yield`, so records are produced one at a time and only requested items are consumed (memory advantage for large files). After two `next()` calls, the remaining count sees only the unconsumed records. A consumed iterator does not restart — call `parse_valid_records(text_path)` again for a fresh pass.

---

## Practice task 7 — Write clean output and an audit summary

**Task.** Write cleaned records to an artifact, read them back, and reconcile source, parsed, rejected, written, and round-trip row counts in an audit summary.

```python
# Write the valid records to a clean artifact
clean_path.write_text(json.dumps(valid_records, indent=2), encoding="utf-8")

# Read back (round-trip check)
reloaded = json.loads(clean_path.read_text(encoding="utf-8"))

audit = {
    "source": str(text_path),
    "total_lines": 4,                    # 4 lines in sensor_log.txt
    "parse_rejected": len(rejected_records),        # 1 (MALFORMED RECORD)
    "validation_rejected": len(invalid_records),    # 1 (temp = 99.0)
    "written_records": len(valid_records),          # 2
    "round_trip_records": len(reloaded),            # 2
    "destination": str(clean_path),
}

# Reconciliation: every received line is accounted for
assert audit["total_lines"] == (
    audit["parse_rejected"] + audit["validation_rejected"] + audit["written_records"]
)
# Round-trip: what was written is what is read back
assert audit["written_records"] == audit["round_trip_records"]
audit
```

**Interpretation.** The audit proves reconciliation: 4 total lines = 1 parse-rejected + 1 validation-rejected + 2 written, and the round-trip check confirms the JSON file reloads to the same 2 records. Writing bytes is not proof of correctness; the read-back and reconciliation assertion show nothing was silently lost or duplicated.

---

## Exit ticket (Week 5)

1. **Why should raw files remain unchanged?**
   Raw files are the original evidence. Keeping them read-only (and writing transformed data to separate clean directories) preserves provenance so any parsing/validation change can be re-run and re-audited without losing source truth.

2. **What is the difference between parsing and validation?**
   **Parsing** asks "can the text be converted into the expected structure?" (format/type). **Validation** asks "does the converted record satisfy the stated contract?" (required fields, plausible ranges, allowed categories). They are separate stages with separate failure modes — e.g., `temp=99.0` parses fine but fails range validation.

3. **How does a reconciliation assertion improve trust in an extraction process?**
   It proves that every received record is accounted for exactly once (received = parse-rejected + validation-rejected + written), so downstream consumers know nothing was silently dropped, duplicated, or left unclassified.

---

## Independent challenge (Week 5)

**Task.** Create a self-contained extraction pipeline for a small source containing at least ten records and two intentional problems. Use only the standard library, parse, validate, write clean JSON/CSV, preserve rejected records, and prove through an assertion that every input record is accounted for.

```python
import csv, json, re
from pathlib import Path

# --- Explicit inputs: raw + clean dirs, source fixture (12 lines, 2 problems) ---
raw_dir = Path("artifacts/challenge_raw"); raw_dir.mkdir(parents=True, exist_ok=True)
clean_dir = Path("artifacts/challenge_clean"); clean_dir.mkdir(parents=True, exist_ok=True)

raw_lines = [
    "2026-08-10T08:00:00 | CEN-01 | temp=28.4 | status=OK",
    "2026-08-10T08:01:00 | CEN-02 | temp=29.1 | status=OK",
    "2026-08-10T08:02:00 | CEN-03 | temp=30.0 | status=CHECK",
    "2026-08-10T08:03:00 | CEN-04 | temp=27.8 | status=OK",
    "MALFORMED RECORD",                                      # problem 1
    "2026-08-10T08:04:00 | CEN-05 | temp=31.2 | status=OK",
    "2026-08-10T08:05:00 | CEN-06 | temp=99.0 | status=OK",  # problem 2 (range)
    "2026-08-10T08:06:00 | CEN-07 | temp=28.9 | status=OK",
    "2026-08-10T08:07:00 | CEN-08 | temp=29.5 | status=OK",
    "2026-08-10T08:08:00 | CEN-09 | temp=30.3 | status=OK",
    "2026-08-10T08:09:00 | CEN-10 | temp=28.1 | status=OK",
    "2026-08-10T08:10:00 | CEN-11 | temp=32.4 | status=OFFLINE",
]
src = raw_dir / "sensor_log.txt"
src.write_text("\n".join(raw_lines), encoding="utf-8")

# --- Parse stage: regex with named groups, keep rejected lines ---
pattern = re.compile(
    r"^(?P<timestamp>[^|]+)\s*\|\s*(?P<device>CEN-\d+)\s*\|\s*"
    r"temp=(?P<temperature>-?\d+(?:\.\d+)?)\s*\|\s*status=(?P<status>[A-Za-z]+)$"
)

# --- Validation stage: required/range/category, all errors returned ---
def validate(record):
    errors = []
    if not (-10 <= record["temperature_c"] <= 60):
        errors.append("temperature outside plausible range")
    if record["status"] not in {"ok", "check", "offline"}:
        errors.append("unknown status")
    return errors

parsed, parse_rejected, validation_rejected, valid = [], [], [], []
for line_no, line in enumerate(src.read_text(encoding="utf-8").splitlines(), start=1):
    m = pattern.match(line)
    if m is None:
        parse_rejected.append({"line": line_no, "raw": line})
        continue
    rec = m.groupdict()
    rec["temperature_c"] = float(rec.pop("temperature"))
    rec["status"] = rec["status"].lower()
    parsed.append(rec)
    problems = validate(rec)
    if problems:
        validation_rejected.append({"record": rec, "errors": problems})
    else:
        valid.append(rec)

# --- Write clean output (JSON) and round-trip it ---
out = clean_dir / "valid_sensor_records.json"
out.write_text(json.dumps(valid, indent=2), encoding="utf-8")
reloaded = json.loads(out.read_text(encoding="utf-8"))

# --- Audit + reconciliation assertions ---
audit = {
    "total_lines": len(raw_lines),
    "parse_rejected": len(parse_rejected),
    "validation_rejected": len(validation_rejected),
    "written_records": len(valid),
    "round_trip_records": len(reloaded),
    "destination": str(out),
}
assert audit["total_lines"] == (
    audit["parse_rejected"] + audit["validation_rejected"] + audit["written_records"]
)
assert audit["written_records"] == audit["round_trip_records"]

print("parsed:", len(parsed), "| rejected details preserved")
print(audit)
print("reconciliation holds:", audit["total_lines"]
      == audit["parse_rejected"] + audit["validation_rejected"] + audit["written_records"])
```

**Interpretation.** 12 source lines: 1 is malformed (parse-rejected), 1 has temp 99.0 °C (validation-rejected), and 10 valid records are written to JSON and reloaded successfully. The reconciliation assertion accounts for every input line (12 = 1 + 1 + 10) and the round-trip check confirms the artifact is readable and matches the in-memory records. The pipeline separates explicit inputs, parsing, validation, output, and audit so all rejections remain traceable.
