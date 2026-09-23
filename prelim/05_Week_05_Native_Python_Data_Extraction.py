# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: CPE_15
#     language: python
#     name: python3
# ---

# %% [markdown] id="a0f88f44"
# # CPE15 - Week 5: Native Python Data Extraction
#
# **Programming for Data Science | Professional Elective 1 | AY 2026-2027**
#
# | Syllabus element | Alignment |
# |---|---|
# | Course outcome | CO3 |
# | Course objective | COBJ2 |
# | Assessment connection | Native Python data extraction performance output |
# | Sustainable Development Goals | 9, 16 |
#
# This notebook is designed for explanation, live coding, guided practice, and independent follow-through. Run it from top to bottom in a fresh kernel so that every result can be reproduced.
#

# %% [markdown] id="01f487b0" tags=["lecture-map", "legacy-inspired"]
# ## Lecture map
#
# 1. Extraction begins with explicit inputs
# 2. CSV extraction
# 3. JSON extraction
# 4. Parsing semi-structured text
# 5. Schema and range validation
# 6. Generator-based extraction
# 7. Write clean output and an audit summary
#
#  **Live-teaching rhythm:** define the idea → predict the result → run a focused example → inspect the saved output → explain the evidence → complete the practice task.

# %% [markdown] id="c68d1448"
# ## Learning outcomes
#
#  By the end of the session, students should be able to:
#
#  - read text, CSV, and JSON data using Python's standard library;
# - extract structured fields from semi-structured records;
# - validate types, required fields, ranges, and malformed input;
# - use generator-based pipelines for memory-conscious processing;
# - produce an auditable extraction summary and clean output file.
#
#
# ## Lecture route
# 1. Paths, encodings, and safe file handling
# 2. CSV and JSON extraction
# 3. Semi-structured log parsing
# 4. Validation and error reporting
# 5. A reproducible extraction pipeline
#

# %% id="fc14a635" outputId="7a936d42-226d-49b8-cab0-a93c386fe098" tags=["setup"]
from pathlib import Path
import platform
import random
import sys

random.seed(15)
ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)

print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {platform.system()}")
print(f"Artifacts folder: {ARTIFACTS.resolve()}")


# %% [markdown] id="bc92b873"
# > **Reproducibility habit:** a notebook is not finished merely because it ran once. It should run in order from a restarted kernel, use explicit inputs, avoid hidden state, and explain the meaning of its outputs.
#

# %% [markdown] id="ae01ead6"
# ## 1. Extraction begins with explicit inputs
#
# A reliable extraction process states the source path, format, encoding, schema expectations, and destination. Use `pathlib.Path` for readable cross-platform paths and `with` blocks so files are closed even when an exception occurs.
#
# This notebook creates small local source files to remain self-contained. In a real task, preserve the raw source as read-only and write transformed data elsewhere.
#

# %% id="ce69e32a"
import csv
import json
from pathlib import Path
import re

raw_dir = ARTIFACTS / "week05_raw"
clean_dir = ARTIFACTS / "week05_clean"
raw_dir.mkdir(exist_ok=True)
clean_dir.mkdir(exist_ok=True)


# %% [markdown] id="be49487b" tags=["concept-bridge", "case-explanation"]
# ### Create a controlled raw-text fixture
#
# The setup cell established raw and clean directories. This continuation writes a small source file containing two ordinary records, one malformed line, and one implausible temperature. Keeping these cases together creates a deterministic fixture for demonstrating the later distinction between parsing rejection and domain-validation rejection.

# %% id="29ce461b" outputId="2c99c119-2f84-48bb-ec3a-b654751b779a"
text_path = raw_dir / "sensor_log.txt"
text_path.write_text(
    chr(10).join(
        [
            "2026-08-10T08:00:00 | CEN-01 | temp=28.4 | status=OK",
            "2026-08-10T08:05:00 | CEN-02 | temp=29.1 | status=OK",
            "MALFORMED RECORD",
            "2026-08-10T08:10:00 | CEN-03 | temp=99.0 | status=CHECK",
        ]
    ),
    encoding="utf-8",
)

print(text_path.read_text(encoding="utf-8"))


# %% [markdown] id="67b587a1" tags=["concept-clinic", "case-explanation", "result-interpretation"]
# ### Discussion clinic — paths, encodings, and source ownership are part of the input contract
#
# Extraction begins before parsing. Record the source path, expected format, encoding, delimiter, schema version, and whether the source is immutable. `pathlib.Path` composes paths without hard-coding operating-system separators. Creating separate raw and clean directories prevents derived output from overwriting evidence. In production, include acquisition time and a checksum when provenance matters.
#
# **Interpretation standard.** A reproducible extractor can state exactly which source it read and where it wrote results. Directory creation is setup, not evidence that any record has been successfully extracted.

# %% [markdown] id="ab1fb970" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** A reproducible extractor can state exactly which source it read and where it wrote results.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="bd867bfd" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Write an extraction contract for a small sensor source that names its format, encoding, record unit, required fields, units, validation rules, and intended output artifact.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="381cace7" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — Extraction begins with explicit inputs
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

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

# %% [markdown] id="9f34efab"
# ## 2. CSV extraction
#
# Python's `csv.DictReader` uses the header row as dictionary keys. This preserves column meaning and makes validation more readable than position-only indexing.
#

# %% id="ca2f7dcc" outputId="5765b472-be5d-460e-a3ef-b9df31dbc712"
csv_path = raw_dir / "devices.csv"
with csv_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["device_id", "zone", "battery_v"],
    )
    writer.writeheader()
    writer.writerows(
        [
            {"device_id": "CEN-01", "zone": "North", "battery_v": "3.91"},
            {"device_id": "CEN-02", "zone": "South", "battery_v": "3.44"},
            {"device_id": "CEN-03", "zone": "North", "battery_v": "not_available"},
        ]
    )

with csv_path.open(newline="", encoding="utf-8-sig") as file:
    device_rows = list(csv.DictReader(file))

device_rows


# %% [markdown] id="359bf6ed" tags=["concept-bridge", "case-explanation"]
# ### Convert CSV text without discarding the original row
#
# `DictReader` returned every field as text, including battery voltage. The helper attempts `float()` and returns `None` for missing or invalid text. Applying it row by row makes numerical values usable while preserving the affected record for a later audit. In production, also retain the original raw value and an error message.

# %% id="80a8f887" outputId="4787b95a-edda-4701-8045-ada026f4c518"
def parse_optional_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None

for row in device_rows:
    row["battery_v"] = parse_optional_float(row["battery_v"])

device_rows


# %% [markdown] id="786fefb4" tags=["concept-clinic", "case-explanation", "result-interpretation"]
# ### Discussion clinic — CSV rows are text until conversion and validation say otherwise
#
# `csv.DictReader` uses the header row as dictionary keys, but every field value is still text. `newline=''` lets the CSV module handle newline conventions, and `utf-8-sig` tolerates an optional byte-order mark. Header names, duplicate identifiers, row length, and numeric conversion all require checks. Preserve the raw value when recording a conversion error so the rejection can be explained.
#
# **Interpretation standard.** The extracted dictionaries prove that parsing succeeded, not that battery voltage is numerical or valid. The value `'not_available'` remains text and must be handled explicitly downstream.

# %% [markdown] id="c51717ff" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 2.1 Individual topic — `csv.DictReader`
#
# **What it is and how it works.** `DictReader` uses header fields as dictionary keys and returns every CSV field as text unless converted later.
#
# **Core syntax**
#
# ```python
# `csv.DictReader(file)`
# ```
#
# **When to use it.** Use it for modest CSV sources when staying within the standard library and row dictionaries are convenient.
#
# **When to use another approach.** Avoid assuming numerical-looking fields are numbers or that headers and row lengths are valid.

# %% id="205f092a" outputId="fcbf923c-9904-4a01-c8f7-f7667c85fa51" tags=["individual-topic-example", "individual-topic"]
# Demonstration — `csv.DictReader`
topic_csv_preview = [{key: (value, type(value).__name__) for key, value in row.items()} for row in device_rows[:1]]
topic_csv_preview

# %% [markdown] id="fcdd337d" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The first row's device, zone, and battery fields are all strings immediately after CSV extraction.
#
# **Science-communication statement.** Separate 'parsed as a CSV row' from 'converted and validated'; parsing alone does not establish field meaning.

# %% [markdown] id="2f9b96dd" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 2.2 Individual topic — Conversion error handling
#
# **What it is and how it works.** A conversion wrapper catches expected `TypeError` or `ValueError` and returns or records an explicit failure representation.
#
# **Core syntax**
#
# ```python
# `try: value=float(text); except (TypeError, ValueError): ...`
# ```
#
# **When to use it.** Use it at external-data boundaries where malformed fields should be audited without terminating the whole batch.
#
# **When to use another approach.** Avoid a bare `except` or silent default that hides the raw value and reason.

# %% id="2848a689" outputId="7683c668-614a-46a4-a6c7-f5249e487cd6" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Conversion error handling
topic_conversion_cases = ["3.91", "not_available", None]
topic_conversion_results = [(raw, parse_optional_float(raw)) for raw in topic_conversion_cases]
print(topic_conversion_results)

# %% [markdown] id="54685d70" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** Valid numeric text converts to 3.91; invalid text and `None` become `None` under the helper's policy.
#
# **Science-communication statement.** Report two conversion failures out of three cases and preserve their raw representations; do not equate both failure causes automatically.

# %% [markdown] id="f8c83a69" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** The extracted dictionaries prove that parsing succeeded, not that battery voltage is numerical or valid.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="741764cc" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Parse a CSV string with `csv.DictReader`, convert numeric fields safely, and preserve the line number and reason for every rejected record.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="26af62c1" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — CSV extraction
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

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




# %% [markdown] id="6e8d80f3"
# ## 3. JSON extraction
#
# JSON can represent nested objects and arrays. Inspect the structure before assuming every record contains the same fields. Use `.get()` for optional fields and direct indexing when a missing required field should be treated as an error.
#

# %% id="d74b123e" outputId="f99aa493-a13b-44ec-8779-2cfa6f0303bf"
json_path = raw_dir / "stations.json"
source_object = {
    "generated_at": "2026-08-10T09:00:00",
    "stations": [
        {"id": "CEN-01", "coordinates": [121.5569, 14.1135], "active": True},
        {"id": "CEN-02", "coordinates": [121.5580, 14.1142], "active": True},
        {"id": "CEN-03", "coordinates": None, "active": False},
    ],
}
json_path.write_text(json.dumps(source_object, indent=2), encoding="utf-8")

loaded_json = json.loads(json_path.read_text(encoding="utf-8"))
active_ids = [row["id"] for row in loaded_json["stations"] if row.get("active")]
active_ids


# %% [markdown] id="9ebc8425" tags=["concept-clinic", "case-explanation"]
# ### Additional worked case — JSON preserves nested structure but optional fields still need guards
#
# JSON objects become dictionaries, arrays become lists, and `true`, `false`, and `null` become `True`, `False`, and `None`. Direct indexing is appropriate for required keys; `.get()` is useful for optional keys but can hide misspellings if used indiscriminately. Validate coordinate length and order because GeoJSON convention is longitude then latitude, while many mapping APIs expect latitude then longitude.

# %% id="a1e0cec5" outputId="c8027829-06d3-4e59-b7b5-1aae85216037" tags=["additional-example", "concept-clinic"]
clinic_station_checks = []
for clinic_station in loaded_json["stations"]:
    clinic_coordinates = clinic_station.get("coordinates")
    clinic_station_checks.append(
        {
            "id": clinic_station.get("id"),
            "has_two_coordinates": isinstance(clinic_coordinates, list) and len(clinic_coordinates) == 2,
            "active": clinic_station.get("active", False),
        }
    )
clinic_station_checks

# %% [markdown] id="714a349b" tags=["concept-clinic", "result-interpretation"]
# **Result and interpretation.** The inactive station lacks coordinates, so its structural check is false. The example separates key presence from domain validity; a two-item coordinate could still be outside plausible bounds.

# %% [markdown] id="a6babffb" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 3.1 Individual topic — JSON object and array structure
#
# **What it is and how it works.** JSON objects load as dictionaries and arrays as lists, preserving nested relationships and primitive values.
#
# **Core syntax**
#
# ```python
# `object = json.loads(text)`; `object['stations'][0]`
# ```
#
# **When to use it.** Use JSON for structured hierarchical exchange with explicit keys and arrays.
#
# **When to use another approach.** Avoid assuming key presence, schema version, coordinate order, or numerical ranges from valid JSON syntax.

# %% id="c09bf8b6" outputId="5ae236e0-82c9-475e-a514-1f2ab2c74362" tags=["individual-topic-example", "individual-topic"]
# Demonstration — JSON object and array structure
topic_first_station = loaded_json["stations"][0]
print("top-level keys:", list(loaded_json))
print("station count:", len(loaded_json["stations"]))
print("first station:", topic_first_station)

# %% [markdown] id="b9a40c8a" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The top-level object contains metadata and a three-record stations list; the first station is a dictionary.
#
# **Science-communication statement.** Describe hierarchy and record count, then state which schema assumptions require validation.

# %% [markdown] id="4c8d93fe" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 3.2 Individual topic — Optional JSON fields with `.get`
#
# **What it is and how it works.** Dictionary `.get(key, default)` retrieves an optional value without raising `KeyError`; direct indexing is clearer for required keys.
#
# **Core syntax**
#
# ```python
# `record.get('coordinates')`; `record['id']`
# ```
#
# **When to use it.** Use `.get` for genuinely optional fields with an explicit downstream policy.
#
# **When to use another approach.** Avoid using `.get` everywhere because misspelled required keys can be silently treated as missing.

# %% id="fdff3020" outputId="af1cac2f-7a7e-4d5d-d783-627c1360a73d" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Optional JSON fields with `.get`
for topic_station in loaded_json["stations"]:
    print(topic_station["id"], "coordinates:", topic_station.get("coordinates", "absent"))

# %% [markdown] id="3722b963" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** Two stations return coordinate lists and one returns `None`, which differs from an absent key default.
#
# **Science-communication statement.** Distinguish absent, explicitly null, and invalid values; they may represent different data-quality conditions.

# %% [markdown] id="758193f3" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** The inactive station lacks coordinates, so its structural check is false.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="fd067d8b" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Load nested JSON containing one optional field, distinguish a missing key from an explicit `null`, and normalize valid records into a consistent schema.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="83308b55" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — JSON extraction
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

import pandas as pd

# load json file from previous cell
loaded_json = json.loads(json_path.read_text(encoding="utf-8"))

# create a normalized list
stations = loaded_json["stations"]
normalized_json = []

for station in stations:
    coordinates = station.get("coordinates", None)
    active = station.get("active", None)
    id = station.get("id", None)

    valid_coordinates = type(coordinates) is list

    if type(id) is not None:
        normalized_station = {
            "id": id,
            "coordinates": coordinates if valid_coordinates else None,
            "active": active
        }

        normalized_json.append(normalized_station)

df = pd.DataFrame(normalized_json)
print(f"Missing records:\n{df.isna().sum()}")
print(f"\nNormalized stations:")
for station in normalized_json: print(station)

# %% [markdown] id="1d16295c"
# ## 4. Parsing semi-structured text
#
# A regular expression is suitable when records follow a stable pattern. Name capture groups so the pattern documents its fields. Never assume that every line matches; preserve the line number and raw content of rejected records.
#

# %% id="3e4931cc" outputId="7ddb0d63-87ea-4d23-a96d-4e258feb85c8"
log_pattern = re.compile(
    r"^(?P<timestamp>[^|]+)\s*\|\s*"
    r"(?P<device>CEN-\d+)\s*\|\s*"
    r"temp=(?P<temperature>-?\d+(?:\.\d+)?)\s*\|\s*"
    r"status=(?P<status>[A-Za-z]+)$"
)

parsed_records = []
rejected_records = []

for line_number, raw_line in enumerate(
    text_path.read_text(encoding="utf-8").splitlines(), start=1
):
    match = log_pattern.match(raw_line)
    if match is None:
        rejected_records.append({"line": line_number, "raw": raw_line})
        continue
    record = match.groupdict()
    record["temperature_c"] = float(record.pop("temperature"))
    record["status"] = record["status"].lower()
    parsed_records.append(record)

print("Parsed:", parsed_records)
print("Rejected:", rejected_records)


# %% [markdown] id="bf61e095" tags=["concept-clinic", "case-explanation"]
# ### Additional worked case — a regular expression is a schema for one line, not general understanding
#
# Named groups such as `(?P<device>...)` make extracted fields readable. Anchors `^` and `$` require the whole line to match, and `\s*` permits surrounding whitespace. A successful match validates only the encoded pattern; conversion and domain rules remain separate. Keep rejected raw lines and line numbers so the parser can be improved without losing evidence.

# %% id="c93ca138" outputId="f8a29874-7a1d-4fd4-d92b-61dac661df5e" tags=["additional-example", "concept-clinic"]
clinic_lines = [
    "2026-08-10T09:05:00 | CEN-08 | temp=30.5 | status=OK",
    "bad timestamp and missing fields",
]
for clinic_line in clinic_lines:
    clinic_match = log_pattern.match(clinic_line)
    print("MATCH" if clinic_match else "REJECT", clinic_match.groupdict() if clinic_match else clinic_line)

# %% [markdown] id="3dd93100" tags=["concept-clinic", "result-interpretation"]
# **Result and interpretation.** The structured line yields named text fields; the malformed line is rejected as a whole. The temperature is still text at this stage and must be converted before numerical validation.

# %% [markdown] id="388de6f6" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 4.1 Individual topic — Regular-expression pattern
#
# **What it is and how it works.** A compiled regular expression encodes allowed text structure. Anchors require a full-line match and groups capture fields.
#
# **Core syntax**
#
# ```python
# `pattern = re.compile(r'^...$')`; `match = pattern.match(text)`
# ```
#
# **When to use it.** Use it for stable, documented semi-structured formats with manageable variability.
#
# **When to use another approach.** Avoid treating regex as a general parser for deeply nested or frequently changing formats.

# %% id="11a6f1f8" outputId="4f0371ea-3806-4665-8deb-90189a53bf98" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Regular-expression pattern
topic_good_line = "2026-08-10T09:05:00 | CEN-08 | temp=30.5 | status=OK"
topic_bad_line = "CEN-08 temperature 30.5"
print("good matches:", log_pattern.match(topic_good_line) is not None)
print("bad matches:", log_pattern.match(topic_bad_line) is not None)

# %% [markdown] id="29e93efc" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The fully structured line matches and the underspecified line is rejected.
#
# **Science-communication statement.** State that the second line failed the encoded format, not that its possible underlying observation was false.

# %% [markdown] id="29c5187b" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 4.2 Individual topic — Named capture groups
#
# **What it is and how it works.** `(?P<name>...)` assigns a readable name to a captured substring, and `groupdict()` returns all named captures as text.
#
# **Core syntax**
#
# ```python
# `match.groupdict()`; `match.group('device')`
# ```
#
# **When to use it.** Use named groups when extracted fields have stable meanings and downstream conversion needs readable keys.
#
# **When to use another approach.** Avoid leaving numeric captures as text when range checks or arithmetic follow.

# %% id="424edce9" outputId="57ab15ac-ebe8-45ac-9e1f-fcd3cea0ffdf" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Named capture groups
topic_match = log_pattern.match(topic_good_line)
topic_fields = topic_match.groupdict()
print(topic_fields)
print("temperature capture type:", type(topic_fields["temperature"]).__name__)

# %% [markdown] id="1e542c6f" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The line becomes a dictionary of named text fields; temperature remains a string until explicitly converted.
#
# **Science-communication statement.** Separate extraction from conversion and validation when explaining the pipeline.

# %% [markdown] id="4227cc10" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** The structured line yields named text fields; the malformed line is rejected as a whole.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="ca4c6269" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Use a regular expression with named groups to parse three log lines, including one malformed line, and report matched and unmatched counts.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="c9d63fd1" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — Parsing semi-structured text
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

# create raw data
lines = [
    "2026-08-10T09:05:00 | CEN-08 | temp=30.5 | status=OK",
    "bad timestamp and missing fields",               # malformed
    "2026-08-10T09:10:00 | CEN-09 | temp=31.0 | status=OK",
]

# seprate raw data to unmatched/matched category
matched, unmatched = [], []
for line_no, line in enumerate(lines, start=1):
    m = log_pattern.match(line)   # log_pattern defined ni sir earlier in notebook

    if m is None:
        unmatched.append({"line": line_no, "raw": line})
        continue

    record = m.groupdict()                        # named capture groups

    record["temperature_c"] = float(record.pop("temperature"))
    record["status"] = record["status"].lower()
    matched.append(record)

# create a report
report = {
    "matched" :{
        "count" :len(matched),
        "records": matched,
    },
    "unmatched": {
        "count": len(unmatched),
        "unmatched records": unmatched
    }
}

report


# %% [markdown] id="e41f0396"
# ## 5. Schema and range validation
#
# Parsing answers "can the text be converted?" Validation answers "does the converted record satisfy the stated contract?" Keep these stages separate so errors are easier to diagnose.
#

# %% id="1d535c39" outputId="19d1117e-7697-4edd-ce0a-c23ec794528f"
def validate_sensor_record(record):
    errors = []
    if not record.get("device"):
        errors.append("missing device")
    if not (-10 <= record["temperature_c"] <= 60):
        errors.append("temperature outside plausible range")
    if record.get("status") not in {"ok", "check", "offline"}:
        errors.append("unknown status")
    return errors

valid_records = []
invalid_records = []
for record in parsed_records:
    errors = validate_sensor_record(record)
    if errors:
        invalid_records.append({"record": record, "errors": errors})
    else:
        valid_records.append(record)

print("Valid:", valid_records)
print("Invalid:", invalid_records)


# %% [markdown] id="27fb6feb" tags=["concept-clinic", "case-explanation"]
# ### Additional worked case — schema, type, range, and cross-field rules are separate cases
#
# A robust validator distinguishes missing required fields, wrong types, implausible ranges, unknown categories, and inconsistent field combinations. Returning a list of errors is more informative than returning only `True` or `False`. Test an ordinary valid record, each boundary, one value just beyond each boundary, and records with missing keys. Do not let one exception prevent the rest of the batch from being audited.

# %% id="fafc50c4" outputId="febc19d9-5070-4ee5-94c8-843fcb34bc56" tags=["additional-example", "concept-clinic"]
clinic_validation_cases = [
    {"device": "CEN-20", "temperature_c": -10, "status": "ok"},
    {"device": "CEN-21", "temperature_c": 60.1, "status": "ok"},
    {"device": "CEN-22", "temperature_c": 25, "status": "unknown"},
]
[(case["device"], validate_sensor_record(case)) for case in clinic_validation_cases]

# %% [markdown] id="201364e9" tags=["concept-clinic", "result-interpretation"]
# **Result and interpretation.** The exact lower boundary passes, while 60.1 and the unknown status produce distinct error messages. These cases document the validator's policy and catch incorrect comparison operators.

# %% [markdown] id="6fc3257b" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 5.1 Individual topic — Schema validation
#
# **What it is and how it works.** Schema validation checks required fields, types, and permitted structures before domain calculations rely on them.
#
# **Core syntax**
#
# ```python
# `required <= record.keys()`; explicit type checks
# ```
#
# **When to use it.** Use it at data boundaries and before range or cross-field rules that assume keys and types exist.
#
# **When to use another approach.** Avoid allowing missing-key exceptions to terminate a batch without an auditable rejection.

# %% id="76a379ce" outputId="6c6c5c15-b8ea-41ef-f3de-921a01239824" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Schema validation
topic_schema_cases = [
    {"device": "CEN-1", "temperature_c": 28.4, "status": "ok"},
    {"temperature_c": 28.4, "status": "ok"},
]
topic_required = {"device", "temperature_c", "status"}
print([(topic_required <= case.keys()) for case in topic_schema_cases])

# %% [markdown] id="f7148c34" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The complete record passes required-key presence and the record without device fails.
#
# **Science-communication statement.** Report which required field is missing; a schema failure is different from a scientifically implausible measured value.

# %% [markdown] id="2212292d" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 5.2 Individual topic — Range and category validation
#
# **What it is and how it works.** Domain validation tests numerical intervals and controlled categories after structure and types are known.
#
# **Core syntax**
#
# ```python
# `low <= value <= high`; `label in allowed_labels`
# ```
#
# **When to use it.** Use limits supported by instrument specifications, science, policy, or an explicitly labeled teaching assumption.
#
# **When to use another approach.** Avoid presenting arbitrary thresholds as universal scientific facts.

# %% id="cfd330c6" outputId="9da94dc3-2479-46ac-c874-ad3665643c63" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Range and category validation
topic_domain_cases = [
    {"device": "A", "temperature_c": -10, "status": "ok"},
    {"device": "B", "temperature_c": 60.1, "status": "ok"},
]
print([(case["device"], validate_sensor_record(case)) for case in topic_domain_cases])

# %% [markdown] id="38ef544e" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The exact lower boundary passes while 60.1 °C fails the stated plausible interval.
#
# **Science-communication statement.** Name the interval, inclusivity, source of the rule, and failure count; call it illustrative if no authoritative source is supplied.

# %% [markdown] id="7c137105" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** The exact lower boundary passes, while 60.1 and the unknown status produce distinct error messages.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="3141dd76" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Validate a record against required-field, type, and plausible-range rules; return all detected problems instead of stopping after the first failure.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="aa7ac788" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — Schema and range validation
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

required_fields = {"device", "temperature_c", "status"}
allowed_status = {"offline", "ok"}
def validate_record(case: dict) -> list:
    errors = []

    missing_fields = required_fields - case.keys();
    has_missing_fields = len(missing_fields) > 0

    if has_missing_fields:
        errors.append(f"missing fields: {", ".join(missing_fields)}")

    temp = case.get("temperature_c", None)
    if type(temp) is None:
        errors.append("Temperature not recorded")
    elif isinstance(temp, (int, float)):
        valid_range = 10 <= temp <= 40
        if not valid_range:
            errors.append("temperature out ouf bound")
    else:
        errors.append("temperature record has mistype")

    status = str(case.get("status", "")).lower().strip()
    valid_status = status in allowed_status
    if not valid_status:
        errors.append(f"invalid status {status}")


    return errors

cases = [
    {"device": "CEN-01", "temperature_c": 28.4, "status": "ok"},
    {"temperature_c": 99.0, "status": "offline"},              # missing device + range
    {"device": "CEN-02", "temperature_c": "hot", "status": "fine"},
]
for case in cases:
    print(case, "->", validate_record(case))


# %% [markdown] id="a38b6875"
# ## 6. Generator-based extraction
#
# A generator yields one item at a time. This can reduce memory use when processing large files and makes pipeline stages composable. The source file still needs careful error handling and an explicit encoding.
#

# %% id="de4cbddd" outputId="f6dc4858-b745-416f-f690-73f235b05d50"
def nonempty_lines(path):
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if stripped:
                yield line_number, stripped

preview = list(nonempty_lines(text_path))
preview


# %% [markdown] id="4e4ac8bd" tags=["concept-clinic", "case-explanation"]
# ### Additional worked case — a generator is lazy and can stream large sources
#
# A generator function contains `yield` and produces one item at a time. Calling it returns an iterator without reading all records immediately. This limits memory use and supports pipelines, but a consumed iterator cannot simply be restarted unless the generator is called again. `list(generator)` is convenient for a small preview but removes the memory advantage for a large source.

# %% id="1beb7a6f" outputId="6758b4c9-db69-426e-fd6f-e5ecbc7fc240" tags=["additional-example", "concept-clinic"]
clinic_stream = nonempty_lines(text_path)
clinic_first = next(clinic_stream)
clinic_second = next(clinic_stream)

print("First yielded line:", clinic_first)
print("Second yielded line:", clinic_second)
print("Remaining lines:", sum(1 for _ in clinic_stream))

# %% [markdown] id="d31065c9" tags=["concept-clinic", "result-interpretation"]
# **Result and interpretation.** `next()` advances the iterator one record at a time, and the final count sees only the unconsumed remainder. Call `nonempty_lines(text_path)` again to begin a fresh pass.

# %% [markdown] id="bd72d5b2" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 6.1 Individual topic — Generator and `yield`
#
# **What it is and how it works.** A generator function pauses at `yield`, returns one item on demand, and resumes from its saved state on the next request.
#
# **Core syntax**
#
# ```python
# `def generator(...): yield item`; `next(iterator)`
# ```
#
# **When to use it.** Use it to stream large or indefinite inputs without materializing every record in memory.
#
# **When to use another approach.** Avoid reusing a consumed generator as if it automatically restarts; call the generator function again.

# %% id="2d189973" outputId="f999117b-69ac-48b9-a8c8-c0e1fdab9518" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Generator and `yield`
topic_line_iterator = nonempty_lines(text_path)
print("iterator type:", type(topic_line_iterator).__name__)
print("first yield:", next(topic_line_iterator))
print("second yield:", next(topic_line_iterator))


# %% [markdown] id="58611c62" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The generator object yields one numbered nonempty line per `next` call and retains its position between calls.
#
# **Science-communication statement.** Explain that only requested lines have been consumed; a preview is not a complete-file summary.

# %% [markdown] id="e988a05c" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** `next()` advances the iterator one record at a time, and the final count sees only the unconsumed remainder.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="5a4060a0" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Write a generator that yields valid records one at a time from a mixed-quality source and demonstrate that iteration does not require storing every parsed record simultaneously.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="aba4c885" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — Generator-based extraction
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

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


# %% [markdown] id="fd8cd6c6"
# ## 7. Write clean output and an audit summary
#
# A performance output should include a clean machine-readable result and a human-readable summary of what happened to every input record.
#

# %% id="9a7db48d" outputId="bb4ce535-6867-44d7-9d9a-7d514839f0bb" tags=["solution"]
clean_path = clean_dir / "valid_sensor_records.json"
clean_path.write_text(json.dumps(valid_records, indent=2), encoding="utf-8")

audit = {
    "source": str(text_path),
    "total_lines": len(preview),
    "parse_rejected": len(rejected_records),
    "validation_rejected": len(invalid_records),
    "written_records": len(valid_records),
    "destination": str(clean_path),
}

assert audit["total_lines"] == (
    audit["parse_rejected"]
    + audit["validation_rejected"]
    + audit["written_records"]
)
audit


# %% [markdown] id="89f2f796" tags=["concept-clinic", "case-explanation"]
# ### Additional worked case — round-trip validation checks what was actually written
#
# A successful `write_text` call proves only that bytes were written. Reopen the destination, parse it, compare record counts and identifiers, and record file size or checksum when appropriate. Reconciliation should account for every input: written plus parse-rejected plus validation-rejected equals received. Keep the audit alongside the clean output so downstream users know what was excluded.

# %% id="3f6934b4" outputId="2414059d-d1f6-4e64-eddc-f46930d1e11c" tags=["additional-example", "concept-clinic"]
clinic_reloaded_clean = json.loads(clean_path.read_text(encoding="utf-8"))
clinic_written_ids = {row["device"] for row in clinic_reloaded_clean}
clinic_expected_ids = {row["device"] for row in valid_records}

print("Reloaded records:", len(clinic_reloaded_clean))
print("Identifiers match:", clinic_written_ids == clinic_expected_ids)
print("Output bytes:", clean_path.stat().st_size)
assert clinic_written_ids == clinic_expected_ids

# %% [markdown] id="1a4d2887" tags=["concept-clinic", "result-interpretation"]
# **Result and interpretation.** The round trip confirms that the destination can be parsed and contains the expected valid identifiers. It still does not prove that the original validation policy was appropriate; that belongs in the audit documentation.

# %% [markdown] id="a8cd4240" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 7.1 Individual topic — Write and read-back validation
#
# **What it is and how it works.** Writing creates an artifact; reading it back verifies that the destination is parseable and structurally matches expectations.
#
# **Core syntax**
#
# ```python
# `path.write_text(...)`; `json.loads(path.read_text(...))`
# ```
#
# **When to use it.** Use round-trip checks for exported data that downstream tools or people will consume.
#
# **When to use another approach.** Avoid treating file existence or byte size alone as proof of correct records.

# %% id="fee4bffc" outputId="1fd42db0-3352-48f3-bb4d-e368a224c160" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Write and read-back validation
topic_roundtrip = json.loads(clean_path.read_text(encoding="utf-8"))
print("written records:", len(valid_records))
print("reloaded records:", len(topic_roundtrip))
print("same records:", topic_roundtrip == valid_records)

# %% [markdown] id="18e1bc0d" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** Written and reloaded record counts agree, and the parsed content equals the in-memory valid list.
#
# **Science-communication statement.** Report the round-trip check and destination; it validates serialization, not the scientific validity of the records.

# %% [markdown] id="84fff6e2" tags=["individual-topic", "topic-explanation", "when-to-use"]
# ### 7.2 Individual topic — Audit reconciliation
#
# **What it is and how it works.** Reconciliation accounts for every received unit across mutually exclusive outcomes such as parsed, rejected, and written.
#
# **Core syntax**
#
# ```python
# `received == parse_rejected + validation_rejected + written`
# ```
#
# **When to use it.** Use it whenever filters or validation can remove evidence from downstream output.
#
# **When to use another approach.** Avoid double-counting one record in multiple terminal categories or omitting early failures.

# %% id="ec40d785" outputId="cb30fe4c-40ea-48c3-e79d-a3095d74b7f5" tags=["individual-topic-example", "individual-topic"]
# Demonstration — Audit reconciliation
topic_reconciles = audit["total_lines"] == audit["parse_rejected"] + audit["validation_rejected"] + audit["written_records"]
print("audit:", audit)
print("reconciles:", topic_reconciles)

# %% [markdown] id="44311a0d" tags=["individual-topic", "topic-output-interpretation", "topic-science-communication"]
# **Expected output pattern and interpretation.** The total line count equals the sum of parse rejection, validation rejection, and written records.
#
# **Science-communication statement.** Lead with received and written counts, then explain every exclusion category so the clean output does not hide data loss.

# %% [markdown] id="fc320c48" tags=["science-communication", "claim-evidence-reasoning"]
# ### Science communication lens
#
# - **Audience:** A downstream analyst who must judge whether extracted records are traceable and fit for use.
# - **Lead with the meaning:** The round trip confirms that the destination can be parsed and contains the expected valid identifiers.
# - **Show the evidence:** Name the source, format, encoding, parsing rule, validation rule, received/parsed/rejected/written counts, and destination artifact.
# - **State the boundary:** Successful parsing establishes structural conformity, not truth, accuracy, completeness, or permission to use the data.
#
# An effective explanation follows **claim → evidence → reasoning → limitation**. Define technical terms when first used, retain units and denominators, distinguish observed output from interpretation, and use wording proportional to the strength of the evidence.

# %% [markdown] id="a6a92fb9" tags=["student-practice", "legacy-inspired", "practice-prompt"]
# ### Practice task — your turn
#
# **Task.** Write cleaned records to an artifact, read them back, and reconcile source, parsed, rejected, written, and round-trip row counts in an audit summary.
#
# **Before running your solution.** Predict the most relevant result property: value, type, shape, retained row count, numerical range, visual pattern, map behavior, or artifact destination.
#
# **After running your solution.** Compare the output with your prediction. Report the evidence with applicable units and counts, explain the reasoning, and state one assumption or limitation.

# %% id="b0b8915f" tags=["student-practice", "legacy-inspired", "practice-scaffold"]
# YOUR TURN — Write clean output and an audit summary
# Complete the specific task in the Markdown cell above.
# Keep input values, intermediate results, and final evidence easy to inspect.

# Write your solution below.

import csv
from pathlib import Path

ARTIFACTS = Path("artifacts")
DATA_DIR = ARTIFACTS / "data-1.csv"

# convert string to number
def to_number(string: str):
    try:
        return float(string)
    except ValueError:
        return None;

# return data row with error
def find_error(data: dict)->dict:
    new_row = data.copy()
    errors = data.get("errors", [])

    temp = to_number(data.get("temperature_c", None))
    valid_type = isinstance(temp, (int, float))

    if not valid_type:
        errors.append("temperature not found")

    if isinstance(temp, (int, float)) and 10 >= temp >= 40:
        errors.append("temperature out of bound")

    new_row["errors"] = errors
    new_row["temperature_c"] = temp

    return new_row

# create a new csv file
def write_csv(data: list):
    with DATA_DIR.open('w', newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["room_id", "temperature_c", "available"]
        )

        writer.writeheader()
        writer.writerows(data)

# open csv file
def read_csv(path: Path) -> list:
    with path.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))

raw_data = [
    {"room_id": "r-101", "temperature_c":"34.1", "available":False},
    {"room_id": "r-104", "temperature_c":"x", "available":True},
    {"room_id": "r-206", "temperature_c":"53.8", "available":True},
    {"room_id": "r-305", "temperature_c":"23.01", "available":False},
    {"room_id": "r-302", "temperature_c":"9.9", "available":True},
]

evaluated_data = []

for data in raw_data:
    new_row = find_error(data)
    evaluated_data.append(new_row)


filtered_data = []

for data in evaluated_data:
    if len(data["errors"]) == 0:
        filtered_data.append({
            "room_id": data["room_id"],
            "temperature_c": data["temperature_c"],
            "available": data["available"]
        })

write_csv(filtered_data)
data_read = read_csv(DATA_DIR)

report = {
    "raw_records": len(raw_data),
    "rejected": len(raw_data) - len(data_read),
    "accepted" : len(data_read)
}

report

# %% [markdown] id="48819f84"
# ## Common mistakes and professional risks
#
# - Using a computer-specific absolute path that fails on another machine.
# - Ignoring file encoding or newline handling.
# - Silently catching every exception and losing evidence of bad records.
# - Treating successful type conversion as proof that a value is plausible.
# - Overwriting raw source files or mixing raw and transformed data.
# - Extracting personal information that is unnecessary for the stated purpose.
#

# %% [markdown] id="1aafedde" tags=["student-task"]
# ## Independent challenge
#
# Create a self-contained extraction pipeline for a small source containing at least ten records and two intentional problems. Use only Python's standard library, parse the source, validate required fields and plausible ranges, write clean JSON or CSV output, preserve rejected-record details, and prove through an assertion that every input record is accounted for.
#
# **Submission expectation:** include readable code, meaningful variable names, a short interpretation, and evidence that the notebook was restarted and run from top to bottom.
#

# %%
from pathlib import Path
import re
import json

# declare directory paths
ARTIFACTS = Path('artifacts')
ARTIFACTS.mkdir(exist_ok=True)

RAW_FILE = ARTIFACTS / "raw_data-1.txt"
clean_dir = ARTIFACTS / "week05_clean"

# create raw data
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

# create audit data
parsed, parse_rejected, validation_rejected, valid = [], [], [], []

# write raw data into txt file
raw_text = "\n".join(raw_lines)
RAW_FILE.write_text(raw_text, encoding="utf-8")

# create regex for later matching
pattern = re.compile(
    r"^(?P<timestamp>[^|]+)\s*\|\s*(?P<device>CEN-\d+)\s*\|\s*"
    r"temp=(?P<temperature>-?\d+(?:\.\d+)?)\s*\|\s*status=(?P<status>[A-Za-z]+)$"
)

# appends errors to a row of record
def validate(record):
    errors = []
    if not (-10 <= record["temperature_c"] <= 60):
        errors.append("temperature outside plausible range")
    if record["status"] not in {"ok", "check", "offline"}:
        errors.append("unknown status")
    return errors

# add row to the rejected list
def add_rejected_line(line_no: int, line: str):
    parse_rejected.append({"line": line_no, "raw": line})


# validate each row of record
read_lines = RAW_FILE.read_text(encoding="utf-8").splitlines()
for line_no, line in enumerate(read_lines, start=1):
    m = pattern.match(line)

    unable_to_read = m is None
    if unable_to_read:
        add_rejected_line(line_no, line)
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

# write clean output (JSON) and round-trip it
out = clean_dir / "valid_sensor_records.json"
out.write_text(json.dumps(valid, indent=2), encoding="utf-8")
reloaded = json.loads(out.read_text(encoding="utf-8"))

# Audit + reconciliation assertions
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
print("reconciliation holds:", audit["total_lines"]
      == audit["parse_rejected"] + audit["validation_rejected"] + audit["written_records"])

audit

# %% [markdown]
# Interpretation. 12 source lines: 1 is malformed (parse-rejected), 1 has temp 99.0 °C (validation-rejected), and 10 valid records are written to JSON and reloaded successfully. The reconciliation assertion accounts for every input line (12 = 1 + 1 + 10) and the round-trip check confirms the artifact is readable and matches the in-memory records. The pipeline separates explicit inputs, parsing, validation, output, and audit so all rejections remain traceable.

# %% [markdown] id="408cf8ce"
# ## Key takeaways
#
#             - Extraction should make source, encoding, schema, and destination explicit.
# - Parsing and validation are separate stages with separate failure modes.
# - Rejected records must be counted and preserved for diagnosis.
# - A clean output is strongest when accompanied by a reconciliation audit.
#
#             ## Exit ticket
#
#             1. Why should raw files remain unchanged?
# 2. What is the difference between parsing and validation?
# 3. How does a reconciliation assertion improve trust in an extraction process?
#

# %% [markdown] id="184dd070" tags=["instructor-note"]
# ## References and further reading
#
#             - Python Software Foundation. `csv`, `json`, `re`, and `pathlib` documentation.
# - Pehcevski, J. (Ed.). (2023). Data Analysis and Information Processing.
# - CPE15 syllabus, Week 5 course learning plan.
#
#             <details>
#             <summary><strong>Instructor facilitation note</strong></summary>
#
#             Ask students to predict outputs before execution, compare at least two valid approaches, and explain results in plain language. During live coding, deliberately trigger one common error and model a calm debugging process.
#
#             </details>
#
