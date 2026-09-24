# Week 1: Python Basics for Data Science

**CPE15 - Programming for Data Science**

---

## Concepts Covered

| # | Concept | Module |
|---|---------|--------|
| 1 | Values, variables, and types | builtins |
| 2 | Type conversion | builtins |
| 3 | Collections: list, tuple, dict, set | builtins |
| 4 | Comparisons and logical operators | builtins |
| 5 | Decisions: if / elif / else | builtins |
| 6 | Loops: for, while | builtins |
| 7 | Comprehensions | builtins |
| 8 | Functions and methods | builtins |
| 9 | Lambda, map, filter | builtins |
| 10 | Integrated case study: sensor-quality report | builtins |

---

## 1. Values, Variables, and Types

A **value** is a piece of data. A **type** tells Python what the value represents and which operations are valid. A **variable** is a name bound to a value with `=`.

| Type | Example | Meaning in a data-science task | Typical operation |
|---|---|---|---|
| `str` | `"CEN-01"` | identifier or category label | `.strip()`, `.lower()` |
| `int` | `120` | whole-number count | addition, comparison |
| `float` | `3.28` | measured or calculated quantity | arithmetic, rounding |
| `bool` | `True` | logical state | `and`, `or`, `not` |
| `NoneType` | `None` | value is absent or not yet known | `is None` check |

The expression on the **right** of `=` is evaluated first, then assigned to the name on the **left**. Use names that preserve meaning and units, such as `voltage_v` instead of `x`.

```python
device_id = "SLSU-CPE-015"   # str: a label, not a quantity
sample_count = 120           # int: a whole-number count
voltage_v = 3.28             # float: a measured quantity
is_calibrated = True         # bool: a two-state condition
last_error = None            # None: no recorded value

[(value, type(value).__name__) for value in [device_id, sample_count, voltage_v, is_calibrated, last_error]]
```

Note: `True` is a Boolean, not the string `"True"`, and `None` is different from `0`, `False`, and an empty string.

### Type conversion

CSV files, forms, and serial messages often supply numeric-looking data as text. Use explicit conversion functions.

```python
raw_temperature = "29.6"
temperature_c = float(raw_temperature)
temperature_f = temperature_c * 9 / 5 + 32

print("Original type:", type(raw_temperature).__name__)   # str
print("Converted type:", type(temperature_c).__name__)     # float
print(f"{temperature_c:.1f} deg C = {temperature_f:.1f} deg F")  # 29.6 -> 85.3
```

**Syntax notes:**
- `float("29.6")` returns the floating-point value `29.6`.
- Type conversions used: `float(...)`, `int(...)`, `bool(...)`.
- `f"{value:.1f}"` formats the number with one digit after the decimal.

In real extraction code, conversion belongs inside validation because text like `"missing"` cannot be converted with `float()`.

---

## 2. Collections

The four built-in collection types express different structural rules.

| Question | List | Tuple | Dictionary | Set |
|---|---|---|---|---|
| Written with | `[...]` | `(...)` | `{key: value}` | `{value, ...}` |
| Ordered | Yes | Yes | Yes, by insertion | Do not depend on display order |
| Mutable | Yes | No | Yes | Yes |
| Allows duplicates | Yes | Yes | Keys: no; values: yes | No |
| Main access | integer index | integer index / unpacking | key | membership test |
| Best mental model | editable sequence | fixed record | labeled record | unique-value collection |

### 2.1 List — an ordered sequence that can change

A list is appropriate when order matters and items may be added, removed, or replaced. Positions start at index `0`.

```python
readings = [28.4, 28.9, 29.1, 28.7]

print(readings[0])        # 28.4  (first item)
print(readings[1:3])      # [28.9, 29.1]  (stop excluded)
print(len(readings))      # 4

readings.append(29.0)     # mutates the list, adds at the end
print(readings)           # 5 values now
```

**Syntax:** index with `[0]`, slice with `[start:stop]`, add with `.append()`.

**When not to use a list:** when the number and meaning of positions must remain fixed, or when each field needs a descriptive label.

### 2.2 Tuple — an ordered fixed record

A tuple is useful for a value whose positions have an agreed meaning and should not change accidentally (e.g., `(latitude, longitude)`).

```python
station_coordinate = (14.1135, 121.5569)
latitude, longitude = station_coordinate      # unpacking
print(station_coordinate[0])                  # 14.1135 by index
print(latitude)                                # 14.1135 by unpacking
print(len(station_coordinate))                 # 2
```

Attempting `station_coordinate[0] = 14.2` raises `TypeError` because **tuples are immutable**. Immutability protects the record from accidental replacement; it does not validate correctness.

### 2.3 Dictionary — a labeled record

A dictionary maps a unique **key** to a **value**.

```python
station = {
    "id": "CEN-01",
    "location": "Lucban",
    "readings_c": [28.4, 28.9, 29.1, 28.7],
}

print(station["id"])                             # CEN-01  (raises KeyError if absent)
print(station.get("operator", "not assigned"))    # safe default
station["mean_c"] = 28.775                        # add or replace a key
```

**Syntax:**
- `station[key]` — direct lookup, raises `KeyError` if absent.
- `station.get(key, default)` — returns a safe default.
- `station[key] = value` — adds a new pair or replaces an existing one.

Dictionary keys are unique; assigning an existing key updates it. Values may be lists, tuples, dictionaries, or sets.

### 2.4 Set — unique values and membership operations

A set removes duplicates and is optimized for membership questions.

```python
observed_statuses = {"online", "maintenance", "online"}   # "online" kept once
print(len(observed_statuses))                              # 2
print("offline" in observed_statuses)                      # False  (membership)
print(observed_statuses & critical_statuses)               # intersection
print(allowed_statuses - observed_statuses)                # difference
```

**Syntax:**
- `in` — membership test.
- `|` — union, `&` — intersection, `-` — difference.
- Use `set()` for an empty set; `{}` creates an empty **dictionary**.

Set display order must not be used to communicate rank or sequence. Use `sorted()` only to make output deterministic.

### 2.5 Choosing and combining collections

| Need | Use |
|------|-----|
| Editable time-ordered series | **list** |
| Fixed `(latitude, longitude)` pair | **tuple** |
| Named fields for one station | **dictionary** |
| Unique categories / fast membership | **set** |

Collections can be nested: a dictionary may hold a tuple, list, set, or another dict. Note a set needs conversion to a list before standard JSON serialization.

---

## 3. Comparisons, Logical Operators, and Decisions

A comparison asks one question and produces `True` or `False`.

| Operator | Question | Example |
|---|---|---|
| `==` | equal? | `status == "online"` |
| `!=` | different? | `status != "offline"` |
| `<`, `<=` | smaller? | `battery_v < 3.2` |
| `>`, `>=` | larger? | `temp_c >= 38` |
| `in` | present? | `status in allowed_statuses` |

**Do not confuse assignment `=` with equality comparison `==`.**

```python
temperature_c = 38.2
print(temperature_c >= 38)   # True
print(status == "online")    # comparison
```

### Combining Boolean conditions

- `A and B` — true only when both are true.
- `A or B` — true when at least one is true.
- `not A` — reverses a Boolean result.

```python
hot = temperature_c >= 38
humid = humidity_pct >= 75
low_battery = battery_v < 3.2

heat_alert = hot and humid
service_needed = heat_alert or low_battery
sensor_invalid = not (0 <= humidity_pct <= 100)
```

Parentheses make policy easier to read.

### Decision branches with `if` / `elif` / `else`

Python tests branches top to bottom; the first true condition runs and the rest are skipped. **Put invalid-data checks before ordinary classifications**.

```python
if not (0 <= humidity_pct <= 100):
    status = "invalid sensor value"
elif temperature_c >= 38 and humidity_pct >= 75:
    status = "heat alert"
elif temperature_c >= 35:
    status = "high temperature"
else:
    status = "normal"
```

### Boundary cases

```python
def alert_level(temp_c):
    if temp_c >= 38:
        return "alert"
    if temp_c >= 35:
        return "watch"
    return "normal"

[(v, alert_level(v)) for v in [34.9, 35.0, 37.9, 38.0, 38.1]]
# normal, watch, watch, alert, alert
```

Test values just below, exactly at, and just above every boundary to prove the boundary operator (`>=`, `<=`) matches the stated policy.

---

## 4. Loops and Comprehensions

| Construct | Best use | Stop condition |
|---|---|---|
| `for` loop | visit each item in a collection | collection is exhausted |
| `while` loop | repeat while a state remains true | Boolean condition turns false or `break` runs |
| comprehension | one readable transformation or filter | source collection is exhausted |

### 4.1 `for` loop — explicit multi-step processing

```python
raw_adc = [510, 515, 498, 1023, 505]
volts = []

for count in raw_adc:
    voltage = count / 1023 * 5.0
    volts.append(round(voltage, 3))

print(volts)
```

A regular loop is useful when intermediate values are named and each conversion is printed for inspection.

### 4.2 Comprehensions — compact transformation and filtering

Read `[expression for item in source]` as "produce this expression for every item." Adding `if condition` retains only matching items.

```python
rounded_volts = [round(count / 1023 * 5.0, 3) for count in raw_adc]   # transform
plausible_volts = [value for value in rounded_volts if value < 4.9]    # filter
rejected = len(rounded_volts) - len(plausible_volts)
```

Transformation keeps the length; filtering reduces it. Reconcile received vs retained counts.

### 4.3 `while` loop — condition-controlled repetition

A `while` loop must update the state used by its condition, or it may never terminate. `break` exits immediately.

```python
attempts_remaining = 3
simulated_results = [False, False, True]
attempt_index = 0

while attempts_remaining > 0:
    passed = simulated_results[attempt_index]
    if passed:
        break
    attempts_remaining -= 1
    attempt_index += 1
```

---

## 5. Functions, Methods, Lambda, map, and filter

These five terms all involve behavior but solve different problems.

| Construct | What it is | How it is called | Best use |
|---|---|---|---|
| function | named reusable operation | `function(argument)` | logic deserving a name, tests, and documentation |
| method | operation supplied by an object's type | `object.method(argument)` | behavior associated with the object |
| lambda | anonymous one-expression function | created with `lambda`, then called/passed | a short local key or predicate |
| `map` | applies a function to every item | `map(function, iterable)` | an existing function transforms every element |
| `filter` | keeps items accepted by a predicate | `filter(predicate, iterable)` | an existing predicate selects elements |

### 5.1 Function — a named input-to-output rule

```python
def celsius_to_fahrenheit(temp_c: float) -> float:
    return temp_c * 9 / 5 + 32

room_temperature_f = celsius_to_fahrenheit(29.0)   # 84.2
```

- `def` starts the definition; the name follows.
- `temp_c` is a **parameter** (local name receiving input); `29.0` is the **argument** supplied.
- `: float` and `-> float` are type hints for readers/tools; Python does not enforce them.
- `return` sends the value back and ends the call.

**Prefer returning a value** so another calculation, plot, table, or test can reuse it. Do not create a function merely to hide an unexplained formula.

### 5.2 Method — behavior attached to an object

Dot syntax: `object.method(arguments)`. Understand the difference between **returning a new value** and **mutating in place**.

```python
clean = raw_station_name.strip().upper()    # strip returns new string; upper on the result
samples.append(29.1)                         # mutates the list, returns None
operator_name = record.get("operator", "unassigned")   # returns value or default
```

**Critical:** `samples = samples.append(29.1)` would replace the list with `None` because `.append()` returns `None`. `.get()` does not modify the dictionary; `.strip()`/`.upper()` return new strings without changing the original.

### 5.3 Lambda — a temporary one-expression function

Pattern: `lambda parameters: returned_expression`. No statement block, no explicit `return`.

```python
devices = [("D-03", 88.4), ("D-01", 97.2), ("D-02", 91.0)]
ranked = sorted(devices, key=lambda item: item[1], reverse=True)
# [('D-01', 97.2), ('D-02', 91.0), ('D-03', 88.4)]
```

**When to use lambda:** a short, obvious rule used at one location (e.g., `key=` in `sorted`, or a simple predicate).
**When not to use lambda:** if the rule needs a name, type hints, a docstring, validation, reuse, or tests — use `def`. Plain-language communication should rank by the stated field, not overclaim "best device."

### 5.4 `map` — apply one transformation to every item

`map(function, iterable)` sends each item to the function and yields each returned value.

```python
temperatures_c = [27.5, 29.0, 31.2]
iterator = map(celsius_to_fahrenheit, temperatures_c)
temperatures_f = list(iterator)     # materialize the lazy iterator
# [81.5, 84.2, 88.16]
```

**Behavior notes:**
- In Python 3, `map` returns a **lazy iterator** — wrap in `list(...)` to inspect.
- Once consumed, iterating the same iterator again produces nothing; call `map(...)` again for a fresh one.
- `map` transforms (keeps length) rather than filters.

A comprehension `[f(x) for x in xs]` is often clearer for a short in-place transformation.

### 5.5 `filter` — retain items that satisfy a predicate

`filter(predicate, iterable)` sends each item to a predicate (a function returning `True`/`False`); items returning `True` are retained.

```python
def is_at_least_30(temp_c: float) -> bool:
    return temp_c >= 30

temperatures_c = [27.5, 29.0, 31.2]
retained = list(filter(is_at_least_30, temperatures_c))   # [31.2]
rejected = len(temperatures_c) - len(retained)            # 2
```

**Filtering changes the denominator.** Report received, retained, and rejected counts, and state the exclusion rule. A comprehension `[x for x in xs if rule(x)]` reads well when transforming and filtering together.

### 5.6 Decision guide

| If you need to... | Prefer | Why |
|---|---|---|
| name and test a reusable rule | `def` | the contract stays visible |
| use behavior of a value's type | method | the object supplies it |
| provide one tiny local key | lambda | avoids a distant one-use definition |
| apply an existing function to every item | `map` | separates iteration from transformation |
| retain items accepted by a predicate | `filter` | separates iteration from selection |
| transform/filter with a short visible expression | comprehension | reads most directly |

### Integrated callable pipeline

```python
raw_readings = [" 28.4 ", "missing", "31.2", " 29.7"]

def parse_temperature(text):
    cleaned = text.strip()
    if cleaned.lower() == "missing":
        return None
    return float(cleaned)

def is_observed(value):
    return value is not None

parsed = list(map(parse_temperature, raw_readings))     # parse each string
observed = list(filter(is_observed, parsed))            # drop None
ranked = sorted(observed, key=lambda value: value, reverse=True)

report = {
    "received": len(raw_readings),
    "parsed_values": parsed,
    "observed_count": len(observed),
    "missing_count": len(raw_readings) - len(observed),
    "ranked_observed_c": ranked,
}
```

Transparency: "Four text records were processed; three were numerical and one was missing. The three observed values were ranked; the missing record was counted but excluded from ranking."

---

## 6. Integrated Case Study: Sensor-Quality Report

This combines: a **list of dictionaries** as input, a **function** with ordered validation branches, a **loop** adding classifications, a **comprehension** selecting usable temperatures, and a **summary dictionary** preserving counts.

```python
sensor_rows = [
    {"station": "CEN-A", "temperature_c": 29.4, "battery_v": 3.91},
    {"station": "CEN-B", "temperature_c": 31.7, "battery_v": 3.42},
    {"station": "CEN-C", "temperature_c": 99.0, "battery_v": 3.88},
    {"station": "CEN-D", "temperature_c": 30.1, "battery_v": 2.95},
]

def classify_record(row):
    if not (-10 <= row["temperature_c"] <= 60):
        return "invalid temperature"
    if row["battery_v"] < 3.2:
        return "low battery"
    return "usable"

for row in sensor_rows:
    row["quality_status"] = classify_record(row)

usable_temps = [
    row["temperature_c"]
    for row in sensor_rows
    if row["quality_status"] == "usable"
]

records_received = len(sensor_rows)
records_usable = len(usable_temps)
records_rejected = records_received - records_usable

report = {
    "records_received": records_received,
    "records_usable": records_usable,
    "records_rejected": records_rejected,
    "mean_usable_temperature_c": round(sum(usable_temps) / records_usable, 2),
}

assert records_received == records_usable + records_rejected
```

**Key checks:**
- Temperature validity is checked **before** the low-battery warning, so an impossible temperature is not reported usable.
- The identity `records received = records usable + records rejected` must hold.
- The mean is computed only from accepted records (CEN-A and CEN-B), never from all received.

---

## Common Mistakes and Debugging Habits

| Mistake | Why it fails | Better check |
|---|---|---|
| using `=` inside a comparison | `=` performs assignment | use `==` to compare |
| assuming index 1 is first item | indexing starts at zero | inspect `items[0]` and `len(items)` |
| assigning the result of `.append()` | `.append()` returns `None` | call it on its own line |
| changing a tuple item | tuples are immutable | create a new tuple |
| treating set display order as meaningful | sets model uniqueness, not rank | use a list or sort only for display |
| letting a `while` condition stay unchanged | loop may never terminate | trace the state update |
| printing inside every function | printed text is hard to reuse | return a value, then print at the boundary |

**Debugging flow:** read the final traceback line first → locate the failing line → inspect relevant types and values → reduce to the smallest reproducible example.

### Boundary-checked helper

```python
def safe_mean(values):
    if not values:
        return None
    return sum(values) / len(values)

assert safe_mean([]) is None
assert safe_mean([2, 4, 6]) == 4
```

---

## Key Takeaways

1. **Types determine valid operations and should preserve data meaning.**
2. **Lists, tuples, dictionaries, and sets express different structural rules.**
3. **Control flow translates stated policies into traceable decisions.**
4. **Small functions make analysis reusable, testable, and readable.**
5. **Integration should occur only after each construct can be explained independently.**
6. **Return values instead of only printing them; reconcile received/retained/rejected counts.**
