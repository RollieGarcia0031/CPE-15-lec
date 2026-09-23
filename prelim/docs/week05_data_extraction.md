# Week 5: Native Python Data Extraction

**CPE15 - Programming for Data Science**

---

## Concepts Covered

| # | Concept | Module |
|---|---------|--------|
| 1 | Path handling with `pathlib` | pathlib |
| 2 | CSV reading and writing | csv |
| 3 | JSON reading and writing | json |
| 4 | Regular expressions for text parsing | re |
| 5 | Conversion error handling | builtins |
| 6 | Schema and range validation | builtins |
| 7 | Generators and `yield` | builtins |
| 8 | Audit reconciliation | concept |

---

## 1. Path Handling with `pathlib`

Use `pathlib.Path` for cross-platform paths. Avoid hardcoding `/` or `\`.

```python
from pathlib import Path

raw_dir = Path("artifacts") / "raw"
clean_dir = Path("artifacts") / "clean"
raw_dir.mkdir(exist_ok=True)

file_path = raw_dir / "sensor_log.txt"
print(file_path)        # artifacts/raw/sensor_log.txt
print(file_path.exists())  # False (until written)
```

**Key methods:**
- `Path("dir").mkdir(exist_ok=True)` - create directory without error if exists
- `path / "file.txt"` - join path components
- `path.read_text(encoding="utf-8")` - read file contents
- `path.write_text("content", encoding="utf-8")` - write file contents
- `path.resolve()` - get absolute path

---

## 2. CSV Extraction

### Reading CSV with `DictReader`

`csv.DictReader` uses the header row as dictionary keys. All values are text until converted.

```python
import csv
import io

csv_text = "device_id,zone,battery_v\nCEN-01,North,3.91\nCEN-02,South,3.44\n"

rows = list(csv.DictReader(io.StringIO(csv_text)))
print(rows)
# [{'device_id': 'CEN-01', 'zone': 'North', 'battery_v': '3.91'},
#  {'device_id': 'CEN-02', 'zone': 'South', 'battery_v': '3.44'}]

print(type(rows[0]["battery_v"]))  # <class 'str'>  -- still text!
```

### Writing CSV with `DictWriter`

```python
with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["device_id", "zone", "battery_v"])
    writer.writeheader()
    writer.writerows([
        {"device_id": "CEN-01", "zone": "North", "battery_v": "3.91"},
    ])
```

**Important:** Always use `newline=""` when opening CSV files for writing.

---

## 3. JSON Extraction

### Reading JSON

JSON objects become dicts, arrays become lists. Use `.get()` for optional keys.

```python
import json

data = {
    "stations": [
        {"id": "CEN-01", "active": True},
        {"id": "CEN-02", "active": False},
    ]
}

# Write to file
Path("stations.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

# Read back
loaded = json.loads(Path("stations.json").read_text(encoding="utf-8"))
print(loaded["stations"][0]["id"])  # CEN-01
```

### Accessing fields safely

```python
station = loaded["stations"][0]

# Required field - use direct indexing (raises KeyError if missing)
print(station["id"])

# Optional field - use .get() (returns None or default if missing)
print(station.get("coordinates", "absent"))  # absent
```

**Tip:** Use `.get()` only for genuinely optional fields. Using it everywhere hides typos in required key names.

---

## 4. Regular Expressions for Text Parsing

### Compiled pattern with named groups

Use `re.compile()` for patterns used repeatedly. Named groups `(?P<name>...)` make captures readable.

```python
import re

pattern = re.compile(
    r"^(?P<timestamp>[^|]+)\s*\|\s*"
    r"(?P<device>CEN-\d+)\s*\|\s*"
    r"temp=(?P<temperature>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"status=(?P<status>[A-Za-z]+)$"
)

line = "2026-08-10T08:00:00 | CEN-01 | temp=28.4 | status=OK"
match = pattern.match(line)

if match:
    fields = match.groupdict()
    print(fields)
    # {'timestamp': '2026-08-10T08:00:00', 'device': 'CEN-01',
    #  'temperature': '28.4', 'status': 'OK'}
    print(type(fields["temperature"]))  # <class 'str'> -- still text!
```

### Parsing with rejection tracking

```python
parsed, rejected = [], []

lines = [
    "2026-08-10T08:00:00 | CEN-01 | temp=28.4 | status=OK",
    "MALFORMED RECORD",
]

for line_no, line in enumerate(lines, start=1):
    match = pattern.match(line)
    if match is None:
        rejected.append({"line": line_no, "raw": line})
        continue
    record = match.groupdict()
    record["temperature_c"] = float(record.pop("temperature"))
    record["status"] = record["status"].lower()
    parsed.append(record)

print("Parsed:", len(parsed))    # 1
print("Rejected:", len(rejected))  # 1
```

**Key regex elements:**
- `^` and `$` - anchors for full-line match
- `(?P<name>...)` - named capture group
- `\d+` - one or more digits
- `(?:...)` - non-capturing group
- `[^|]+` - one or more characters that are not `|`
- `\s*` - zero or more whitespace

---

## 5. Conversion Error Handling

Use `try/except` to convert fields safely without terminating the batch.

```python
def parse_optional_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None

cases = ["3.91", "not_available", None]
results = [(raw, parse_optional_float(raw)) for raw in cases]
print(results)
# [('3.91', 3.91), ('not_available', None), (None, None)]
```

**Rule:** Avoid bare `except` or silent defaults that hide the raw value and reason.

---

## 6. Schema and Range Validation

### Schema validation (required fields + types)

```python
def validate_record(record):
    errors = []
    required = {"device", "temperature_c", "status"}

    # Check required fields
    missing = required - record.keys()
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")

    # Check type and range
    temp = record.get("temperature_c")
    if not isinstance(temp, (int, float)):
        errors.append("temperature not numeric")
    elif not (-10 <= temp <= 60):
        errors.append("temperature outside plausible range")

    # Check category
    if record.get("status") not in {"ok", "check", "offline"}:
        errors.append("unknown status")

    return errors
```

### Applying validation

```python
records = [
    {"device": "CEN-01", "temperature_c": 28.4, "status": "ok"},
    {"device": "CEN-02", "temperature_c": 99.0, "status": "ok"},
]

valid, invalid = [], []
for rec in records:
    errors = validate_record(rec)
    if errors:
        invalid.append({"record": rec, "errors": errors})
    else:
        valid.append(rec)

print("Valid:", len(valid))    # 1
print("Invalid:", len(invalid))  # 1
```

**Separate parsing from validation.** Parsing asks "can the text be structured?" Validation asks "does the record satisfy the contract?"

---

## 7. Generators and `yield`

A generator yields one item at a time, reducing memory use for large files.

```python
def nonempty_lines(path):
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if stripped:
                yield line_number, stripped

# Generator is lazy -- nothing is read until iterated
stream = nonempty_lines(Path("sensor_log.txt"))

# Read one item at a time
first = next(stream)
second = next(stream)
print(first)   # (1, '2026-08-10T08:00:00 | CEN-01 | temp=28.4 | status=OK')
print(second)  # (2, '2026-08-10T08:05:00 | CEN-02 | temp=29.1 | status=OK')

# Count remaining without storing them all
remaining = sum(1 for _ in stream)
```

**Key points:**
- A generator pauses at `yield` and resumes on the next request
- A consumed iterator cannot restart -- call the generator function again
- `list(generator)` is convenient for preview but removes the memory advantage

---

## 8. Audit Reconciliation

Account for every input record across all outcomes.

```python
audit = {
    "total_lines": 4,
    "parse_rejected": 1,
    "validation_rejected": 1,
    "written_records": 2,
}

# Every input must be accounted for
assert audit["total_lines"] == (
    audit["parse_rejected"]
    + audit["validation_rejected"]
    + audit["written_records"]
)
```

### Round-trip validation

Write clean output, then read it back to confirm the artifact is parseable.

```python
import json

clean_path = Path("clean/valid.json")
clean_path.write_text(json.dumps(valid_records, indent=2), encoding="utf-8")

reloaded = json.loads(clean_path.read_text(encoding="utf-8"))
print(len(reloaded) == len(valid_records))  # True
```

---

## Complete Pipeline Example

```python
import csv
import json
import re
from pathlib import Path

# 1. Explicit inputs
RAW = Path("artifacts") / "sensor_log.txt"
CLEAN = Path("artifacts") / "clean" / "valid.json"
CLEAN.parent.mkdir(exist_ok=True)

# 2. Regex pattern
pattern = re.compile(
    r"^(?P<device>CEN-\d+)\s*\|\s*"
    r"temp=(?P<temperature>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"status=(?P<status>[A-Za-z]+)$"
)

# 3. Parse
parsed, rejected = [], []
for line_no, line in enumerate(RAW.read_text(encoding="utf-8").splitlines(), 1):
    m = pattern.match(line.strip())
    if m is None:
        rejected.append({"line": line_no, "raw": line})
        continue
    rec = m.groupdict()
    rec["temperature_c"] = float(rec.pop("temperature"))
    rec["status"] = rec["status"].lower()
    parsed.append(rec)

# 4. Validate
valid, invalid = [], []
for rec in parsed:
    errors = []
    if not (-10 <= rec["temperature_c"] <= 60):
        errors.append("temp out of range")
    if rec["status"] not in {"ok", "check", "offline"}:
        errors.append("unknown status")
    if errors:
        invalid.append({"record": rec, "errors": errors})
    else:
        valid.append(rec)

# 5. Write + read-back
CLEAN.write_text(json.dumps(valid, indent=2), encoding="utf-8")
reloaded = json.loads(CLEAN.read_text(encoding="utf-8"))

# 6. Audit
audit = {
    "total": len(list(RAW.read_text(encoding="utf-8").splitlines())),
    "parse_rejected": len(rejected),
    "validation_rejected": len(invalid),
    "written": len(valid),
    "round_trip": len(reloaded),
}
assert audit["total"] == audit["parse_rejected"] + audit["validation_rejected"] + audit["written"]
assert audit["written"] == audit["round_trip"]
print(audit)
```

---

## Key Takeaways

1. **Explicit inputs** -- state source, format, encoding, and destination upfront
2. **Separate parsing from validation** -- they fail for different reasons
3. **Preserve rejected records** -- keep line numbers and raw content for diagnosis
4. **Use `pathlib.Path`** -- readable, cross-platform path handling
5. **Generators for large files** -- process one record at a time
6. **Audit reconciliation** -- `total = parse_rejected + validation_rejected + written`
7. **Round-trip checks** -- read back output to verify the artifact is correct
