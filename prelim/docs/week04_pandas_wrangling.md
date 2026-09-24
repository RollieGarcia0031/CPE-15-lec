# Week 4: Pandas Data Wrangling

**CPE15 - Programming for Data Science**

---

## Concepts Covered

| # | Concept | Module |
|---|---------|--------|
| 1 | Series and DataFrame | pandas |
| 2 | Structural inspection | pandas |
| 3 | Datetime conversion | pandas |
| 4 | String cleaning with `.str` | pandas |
| 5 | Numeric conversion | pandas |
| 6 | Selection with `.loc` / `.iloc` | pandas |
| 7 | Boolean filtering | pandas |
| 8 | Derived columns, `drop`, index ops | pandas |
| 9 | Missing data handling | pandas |
| 10 | GroupBy: split-apply-combine | pandas |
| 11 | Merge and concatenate | pandas |

---

## 1. Series and DataFrame

### Series

A one-dimensional labeled array with an index and one dtype.

```python
import pandas as pd

s = pd.Series(
    [229.1, 231.0, 228.4],
    index=["CEN", "Lab", "Library"],
    name="voltage_v"
)
print(s)
# CEN        229.1
# Lab        231.0
# Library    228.4
# Name: voltage_v, dtype: float64

print(round(s.mean(), 2))  # 229.5
```

### DataFrame

A two-dimensional labeled table whose columns may have different dtypes.

```python
df = pd.DataFrame({
    "station": ["A", "B"],
    "temperature_c": [28.4, 29.1],
    "active": [True, False]
})
print(df)
#   station  temperature_c  active
# 0       A           28.4    True
# 1       B           29.1   False

print(df.dtypes)
# station          object
# temperature_c   float64
# active            bool
```

---

## 2. Structural Inspection

Always inspect a DataFrame before cleaning.

```python
energy = pd.DataFrame({
    "timestamp": ["2026-08-03 08:00", "2026-08-03 09:00", "2026-08-04 08:00"],
    "building": ["CEN", "CEN", "Library"],
    "voltage_v": [229.1, 231.0, 999.0],
    "current_a": [12.4, None, 9.3],
    "status": ["ok", "OK ", "check"],
})

print("Shape:", energy.shape)           # (3, 5)
print("Columns:", energy.columns.tolist())
print("Dtypes:\n", energy.dtypes, sep="")
print("Missing:\n", energy.isna().sum(), sep="")
print("Duplicates:", energy.duplicated().sum())
```

**Key inspection methods:**

| Method | Returns |
|--------|---------|
| `.shape` | `(rows, cols)` tuple |
| `.columns.tolist()` | list of column names |
| `.dtypes` | storage type per column |
| `.isna().sum()` | missing count per column |
| `.duplicated().sum()` | count of duplicate rows |
| `.head(n)` | first n rows |

---

## 3. Datetime Conversion

Convert text timestamps to datetime for time-aware operations.

```python
energy["timestamp"] = pd.to_datetime(energy["timestamp"])
energy["date"] = energy["timestamp"].dt.date
energy.dtypes
# timestamp    datetime64[ns]
# date                 object
```

### With explicit format

```python
time_text = pd.Series(["2026-08-03 08:00", "2026-08-03 09:30"])
times = pd.to_datetime(time_text, format="%Y-%m-%d %H:%M")

elapsed_min = (times.iloc[1] - times.iloc[0]).total_seconds() / 60
print(elapsed_min)  # 90.0
```

**Common `.dt` accessors:** `.dt.date`, `.dt.hour`, `.dt.day`, `.dt.month`

---

## 4. String Cleaning with `.str`

The `.str` accessor applies vectorized string methods to a Series.

```python
energy["status"] = energy["status"].str.strip().str.lower()
# "OK " becomes "ok", "Check" becomes "check"
```

### Common `.str` methods

| Method | Purpose |
|--------|---------|
| `.str.strip()` | remove leading/trailing whitespace |
| `.str.lower()` | lowercase all text |
| `.str.upper()` | uppercase all text |
| `.str.contains("text")` | Boolean: contains substring |
| `.str.replace("old", "new")` | pattern or text replacement |

### Side-by-side comparison

```python
raw = pd.Series([" OK ", "ok", "Check", None], name="status")
clean = raw.str.strip().str.lower()
print(pd.DataFrame({"raw": raw, "clean": clean}))
#    raw  clean
# 0   OK     ok
# 1   ok     ok
# 2  Check  check
# 3  None  None
```

---

## 5. Numeric Conversion

Convert text columns to numbers. `errors='coerce'` turns failures into `NaN`.

```python
clinic_raw = pd.Series([" 3.91 ", "not_available", "3.44"], name="battery_v")
clinic_numeric = pd.to_numeric(clinic_raw.str.strip(), errors="coerce")

print(pd.DataFrame({"raw": clinic_raw, "numeric": clinic_numeric}))
#              raw  numeric
# 0         3.91      3.91
# 1  not_available      NaN
# 2          3.44      3.44

print("Conversion failures:", int(clinic_numeric.isna().sum()))  # 1
```

**When to use:**
- `errors='coerce'` -- retain rows, audit failures as missing
- `errors='raise'` -- stop at the first failure (production/graded)

---

## 6. Selection with `.loc` / `.iloc`

### `.loc` -- label-based

```python
# Select specific columns
selected = energy.loc[:, ["timestamp", "building", "voltage_v"]]

# Filter rows by condition
cen_rows = energy.loc[energy["building"].eq("CEN")]

# Combined: filter + select
result = energy.loc[energy["building"].eq("CEN"), ["timestamp", "voltage_v"]]
print(result)
```

### `.iloc` -- position-based

```python
# First 3 rows, first 4 columns (stop is exclusive)
first_three = energy.iloc[:3, :4]
print(first_three)
print("shape:", first_three.shape)  # (3, 4)
```

**Key difference:** `.loc` uses labels/conditions, `.iloc` uses integer positions. `.iloc` slices exclude the stop index like regular Python.

---

## 7. Boolean Filtering

Use `.between()`, `.eq()`, `.isin()`, `.isna()` for readable rules.

```python
# Range filter
valid_voltage = energy["voltage_v"].between(180, 260)

# Allow missing current or valid range
valid_current = energy["current_a"].between(0, 100) | energy["current_a"].isna()

# Combine masks
energy["quality_ok"] = valid_voltage & valid_current

print(energy[["building", "voltage_v", "current_a", "quality_ok"]])
#   building  voltage_v  current_a  quality_ok
# 0      CEN      229.1       12.4        True
# 1      CEN      231.0        NaN        True
# 2   Library      228.4        8.7        True
# 3      CEN      230.2        NaN       False   (current missing, not ok)
# 4   Library      999.0        9.3       False   (voltage out of range)
# 5   Library      229.5        9.0        True
```

**Operators:** `&` (and), `|` (or), `~` (not). Always use parentheses around each condition.

---

## 8. Derived Columns, Drop, and Index Operations

### Derived column

```python
energy["apparent_power_va"] = energy["voltage_v"] * energy["current_a"]
# Missing current propagates -- result is NaN, not zero
```

### `.assign()` (non-mutating)

```python
clinic_energy = energy.assign(
    power_kw=lambda frame: frame["voltage_v"] * frame["current_a"] / 1000,
    hour=lambda frame: frame["timestamp"].dt.hour,
)
# energy itself is unchanged
```

### Drop columns

```python
compact = energy.drop(columns=["timestamp"])
print(compact.columns.tolist())
```

### Set and reset index

```python
indexed = energy.set_index("timestamp").sort_index()
# timestamp becomes the row labels

restored = indexed.reset_index()
# timestamp returns to a regular column
```

**Rule:** Include units in derived column names (`_va`, `_kwh`, `_c`). Avoid dropping source fields before audit is complete.

---

## 9. Missing Data

### Detecting missing values

```python
missing_report = energy.isna().sum().rename("missing_count").to_frame()
missing_report["missing_pct"] = (
    missing_report["missing_count"] / len(energy) * 100
).round(1)
print(missing_report)
```

### Missing by group

```python
missing_by_building = (
    energy.groupby("building")["current_a"]
    .apply(lambda values: int(values.isna().sum()))
)
print(missing_by_building)
# building
# CEN        1
# Library    0
```

### Dropping missing rows

```python
complete = energy.dropna(subset=["current_a"])
print(f"Received: {len(energy)}, Retained: {len(complete)}")
# Received: 6, Retained: 5
```

### Imputation (group median)

```python
clean_energy = energy.loc[energy["status"].str.strip().str.lower().eq("ok")].copy()

clean_energy["current_a"] = clean_energy.groupby("building")["current_a"].transform(
    lambda values: values.fillna(values.median())
)

clean_energy["apparent_power_va"] = (
    clean_energy["voltage_v"] * clean_energy["current_a"]
)
print(f"Retained {len(clean_energy)} of {len(energy)} rows")
```

**Never** replace missing values with zero unless zero is a justified observation. Always flag imputed values.

---

## 10. GroupBy: Split, Apply, Combine

### `.agg()` -- one row per group

```python
building_summary = (
    clean_energy.groupby("building", as_index=False)
    .agg(
        observations=("building", "size"),
        mean_voltage_v=("voltage_v", "mean"),
        max_current_a=("current_a", "max"),
        mean_apparent_power_va=("apparent_power_va", "mean"),
    )
    .round(2)
)
print(building_summary)
#   building  observations  mean_voltage_v  max_current_a  mean_apparent_power_va
# 0      CEN             2          230.05           13.1                 2867.16
# 1   Library             3          229.13            9.3                 2064.36
```

### `.transform()` -- row-aligned results

```python
transformed = clean_energy[["building", "voltage_v"]].copy()
transformed["group_mean_v"] = transformed.groupby("building")["voltage_v"].transform("mean")
transformed["deviation_v"] = transformed["voltage_v"] - transformed["group_mean_v"]
print(transformed)
#   building  voltage_v  group_mean_v  deviation_v
# 0      CEN      229.1        230.05        -0.95
# 1      CEN      231.0        230.05         0.95
# 2   Library      228.4        229.13        -0.73
# ...
```

| Method | Output rows | Use case |
|--------|-------------|----------|
| `.agg()` | 1 per group | summary tables |
| `.transform()` | same as input | per-row deviations, imputation |

---

## 11. Merge and Concatenate

### Merge (relational join)

```python
building_info = pd.DataFrame({
    "building": ["CEN", "Library"],
    "floor_area_m2": [2400, 1800],
    "manager": ["Engineering", "Library Services"],
})

enriched = building_summary.merge(
    building_info,
    on="building",
    how="left",
    validate="one_to_one",
)
enriched["va_per_m2"] = enriched["mean_apparent_power_va"] / enriched["floor_area_m2"]
print(enriched.round(3))
```

### Merge with indicator

```python
left = pd.DataFrame({"station": ["A", "B", "C"], "value": [10, 20, 30]})
right = pd.DataFrame({"station": ["A", "B"], "region": ["North", "South"]})

merged = left.merge(right, on="station", how="left", validate="many_to_one", indicator=True)
print(merged)
#   station  value   region      _merge
# 0       A     10    North       both
# 1       B     20    South       both
# 2       C     30      NaN  left_only
```

**Join types (`how=`):** `left`, `right`, `inner`, `outer`

### Concatenate (stack compatible objects)

```python
morning = clean_energy.iloc[:2].copy()
later = clean_energy.iloc[2:].copy()
recombined = pd.concat([morning, later], ignore_index=True)

assert len(recombined) == len(clean_energy)
assert set(recombined.columns) == set(clean_energy.columns)
```

| Operation | Purpose |
|-----------|---------|
| `merge` | combine columns by key (like SQL join) |
| `concat` | stack rows or align columns (no key matching) |

---

## Data Quality Report

```python
quality_report = {
    "input_rows": len(energy),
    "retained_rows": len(clean_energy),
    "excluded_rows": len(energy) - len(clean_energy),
    "remaining_missing": int(clean_energy.isna().sum().sum()),
    "duplicate_rows": int(clean_energy.duplicated().sum()),
}
assert quality_report["remaining_missing"] == 0
print(quality_report)
```

---

## Key Takeaways

1. **Inspect first** -- always check `.shape`, `.dtypes`, `.isna().sum()` before transforming
2. **Clean text** -- `.str.strip().str.lower()` standardizes category labels
3. **Convert types explicitly** -- `pd.to_numeric(errors='coerce')` retains failures as `NaN`
4. **`.loc` for labels, `.iloc` for positions** -- avoid chained indexing
5. **Separate `agg` from `transform`** -- summary vs. row-aligned
6. **`merge` joins by key, `concat` stacks** -- different questions, different tools
7. **Flag imputed values** -- never describe estimates as observations
