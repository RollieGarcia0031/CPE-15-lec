# Week 2: NumPy Arrays and Vectorized Computation

**CPE15 - Programming for Data Science**

---

## Concepts Covered

| # | Concept | Module |
|---|---------|--------|
| 1 | Array creation and dtype | numpy |
| 2 | Shape, ndim, and size | numpy |
| 3 | Constructors: zeros, ones, arange, linspace, eye | numpy |
| 4 | Integer indexing and slicing | numpy |
| 5 | Views vs copies | numpy |
| 6 | Boolean masks and combining masks | numpy |
| 7 | np.where | numpy |
| 8 | reshape and inferred dimension (-1) | numpy |
| 9 | Axis reductions (mean, sum) | numpy |
| 10 | Broadcasting | numpy |
| 11 | Vectorization vs loops | numpy |
| 12 | Case study: power and quality calculations | numpy |

---

## 1. Why NumPy arrays?

A NumPy array stores elements in a regular, typed structure that supports concise operations over entire vectors/matrices. A Python list is flexible and may hold mixed objects, but an array is deliberately regular — which enables speed, predictable shape behavior, and a large scientific-computing ecosystem.

**Key contrast:** array operators are elementwise/numerical; list operators are structural.

```python
import numpy as np

python_values = [1, 2, 3]
numpy_values = np.array([1, 2, 3])

print("List * 2:", python_values * 2)    # [1, 2, 3, 1, 2, 3]  (repetition)
print("Array * 2:", numpy_values * 2)     # [2 4 6]              (elementwise)
print("List addition:", [1, 2, 3] + [10, 20, 30])   # concatenation
print("Array addition:", np.array([1, 2, 3]) + np.array([10, 20, 30]))  # [11 22 33]
```

| Operation | List | Array |
|-----------|------|-------|
| `* 2` | repeats the sequence | elementwise multiplication |
| `+` | concatenates | adds aligned elements |

Before using an operator, state whether the intended operation is **structural** or **numerical**.

---

## 2. Creating Arrays and Inspecting Their Structure

Always inspect `shape`, `ndim`, `size`, and `dtype` before serious computation.

### Core attributes

```python
readings = np.array(
    [
        [3.28, 0.41, 28.5],
        [3.31, 0.39, 28.7],
        [3.26, 0.44, 29.0],
        [3.30, 0.40, 28.8],
    ],
    dtype=float,
)

print("shape:", readings.shape)  # (4, 3)  length of each axis
print("ndim:", readings.ndim)     # 2        number of axes
print("size:", readings.size)     # 12       total elements
print("dtype:", readings.dtype)   # float64
```

**Interpretation standard:** State what one row and each column represent, the shape, and the dtype — not just "it is a matrix." A `(4, 3)` array might mean four observations and three sensor channels, but NumPy only knows the shape.

### Constructors for different starting conditions

| Function | Purpose | Example |
|----------|---------|---------|
| `np.array([...], dtype=float)` | from a list, with explicit dtype | `np.array([1, 2, 3], dtype=float)` |
| `np.zeros((rows, cols))` | all-zero placeholders | `np.zeros((2, 3))` |
| `np.ones(shape, dtype=int)` | all-one placeholders | `np.ones(4, dtype=int)` |
| `np.arange(start, stop, step)` | start-stop-step rule (stop excluded) | `np.arange(0, 12, 2)` |
| `np.linspace(start, stop, num)` | exact number of evenly spaced values | `np.linspace(0, 1, 5)` |
| `np.eye(n)` | identity matrix (ones on diagonal) | `np.eye(3)` |

```python
zeros = np.zeros((2, 3))
ones = np.ones((2, 3))
sequence = np.arange(0, 12, 2)
grid = np.linspace(0, 1, 5)
identity = np.eye(3)
```

**Selection rule:** use `arange` when the step is central; use `linspace` when the required number of evenly spaced samples (including endpoints) is central. With floating-point steps, `linspace` is safer at the endpoint.

**dtype promotion:** mixing integers with decimals usually promotes to float; mixing numbers with text can promote the entire array to strings, blocking numerical summaries.

**Notes:**
- `zeros`/`ones` produce *placeholders*, not observed data — don't use zeros as substitutes for missing observations unless zero is a valid measured value.
- `np.eye` is an identity matrix, not an all-ones matrix.

---

## 3. Indexing, Slicing, and Views

Indexing retrieves individual elements; slicing uses `start:stop:step` (stop excluded); slices are often **views** sharing memory with the source.

```python
readings = np.array(
    [
        [3.28, 0.41, 28.5],
        [3.31, 0.39, 28.7],
        [3.26, 0.44, 29.0],
        [3.30, 0.40, 28.8],
    ],
    dtype=float,
)

voltage = readings[:, 0]            # column 0 (all rows)
current = readings[:, 1]            # column 1
first_two_rows = readings[:2, :]    # rows 0-1
temperature_copy = readings[:, 2].copy()  # independent copy
```

### Integer indexing

```python
grid = np.arange(12).reshape(3, 4)
print(grid[1, 2])   # 6  second row, third column (0-based)
print(grid[-1])     # last row (negative indices count from the end)
```

### Slicing

```python
grid = np.arange(20).reshape(4, 5)
block = grid[1:3, 2:5]   # rows 1-2, columns 2-4  -> shape (2, 3)
```

**Important:** the stop value is **excluded**, so `1:3` keeps rows 1 and 2 only.

### Views vs copies

```python
demo = np.arange(6)
view = demo[1:4]
view[0] = 99
print(view)   # [99  2  3]
print(demo)   # [ 0 99  2  3  4  5]   <- source changed!
```

```python
source = np.array([10, 20, 30, 40])
independent = source[1:3].copy()
independent[0] = 999
print(independent)   # [999  30]
print(source)        # [10 20 30 40]  <- preserved
```

| | View | Copy |
|---|------|------|
| Memory | shares the original | independent storage |
| Mutating it changes the source | yes | no |
| Check | `np.shares_memory(a, b)` | returns False |
| Created by | basic slicing | `.copy()` |

**Rule:** make a deliberate `.copy()` before destructive cleaning when the original measurement array must remain for audit. Treat indexing ("which element?"), slicing ("which rectangular region?"), and copying ("should later mutation remain isolated?") as three separate design decisions.

---

## 4. Boolean Selection

A Boolean mask has the same relevant shape as the data being filtered.

```python
valid_voltage_mask = (voltage >= 3.25) & (voltage <= 3.35)
high_current_mask = current > 0.42

print("Valid voltage rows:\n", readings[valid_voltage_mask])
print("High-current row indices:", np.where(high_current_mask)[0])
```

### Combining masks

- Use **`&`** (AND), **`|`** (OR), and **`~`** (NOT) for elementwise array logic.
- **Parenthesize each comparison** — Python's `and`/`or` are scalar and do not work elementwise on arrays.

```python
combined = valid_voltage_mask & (readings[:, 2] < 28.9)
print("Retained:", readings[combined])
print("Retained / rejected:", int(combined.sum()), int((~combined).sum()))
assert int(combined.sum() + (~combined).sum()) == len(readings)
```

Counting `mask.sum()` and `(~mask).sum()` gives a reconciliation check: retained + rejected must equal the source row count.

### np.where

With one argument it returns matching indices; with three arguments it selects a value when true and another when false.

```python
current = np.array([0.20, 0.55, 0.90])
high = current >= 0.50

print("matching indices:", np.where(high)[0])          # [1 2]
print("labels:", np.where(high, "review", "normal"))   # ['normal' 'review' 'review']
```

**Syntax:**
- `np.where(mask)[0]` — locate matches
- `np.where(mask, value_if_true, value_if_false)` — two-way labeling

Avoid deeply nested `where` for multi-class logic; prefer explicit functions for readability.

---

## 5. Reshaping and Axis Meaning

Reshaping changes how elements are organized, not their order or total count. The product of dimensions must equal `size`.

```python
one_day = np.arange(24)
six_blocks = one_day.reshape(6, 4)   # six 4-hour blocks
restored = six_blocks.reshape(-1)    # flatten back to 1-D
assert np.array_equal(restored, one_day)
```

### Inferred dimension with `-1`

Exactly one reshape dimension may be `-1`; NumPy infers its length from total size and the other dimensions.

```python
stream = np.arange(24)
columns = stream.reshape(-1, 6)
print(columns.shape)   # (4, 6)  -- NumPy infers 4 rows
```

Do not use more than one `-1`, and verify the inferred shape matches the intended grouping.

### Axis reductions

For a `(rows, columns)` table:

- `axis=0` collapses rows → one result **per column**
- `axis=1` collapses columns → one result **per row**

```python
grid = np.arange(12).reshape(3, 4)
print(grid.mean(axis=0))   # four column means
print(grid.mean(axis=1))   # three row means
print(grid.reshape(-1))    # flatten: 12 positions
```

| Reduction | Collapse | Result count |
|-----------|----------|--------------|
| `mean(axis=0)` | rows | one per column |
| `mean(axis=1)` | columns | one per row |

**Rule:** translate axis operations into words before coding — "mean across observations for each channel" is clearer than memorizing a number. Name the new axes and verify the result length matches the intended choice.

---

## 6. Broadcasting and Vectorized Computation

Broadcasting lets arrays with compatible shapes interact without explicitly copying repeated values. Compare shapes from the **trailing** dimension: compatible when equal or one of them is 1.

```python
raw = np.array(
    [
        [510, 205, 720],
        [515, 198, 730],
        [505, 210, 710],
        [520, 202, 725],
    ],
    dtype=float,
)
scales = np.array([0.01, 0.05, 0.10])
offsets = np.array([-0.20, 1.00, -40.00])

calibrated = raw * scales + offsets
print("Raw shape:", raw.shape)        # (4, 3)
print("Scale shape:", scales.shape)   # (3,)
```

The `(3,)` vector aligns with the three columns. A `(4,)` vector would *not* mean one factor per row unless reshaped to `(4, 1)` (e.g. `row_factors[:, None] * matrix`).

```python
# Per-column reduction after calibration
channel_means = calibrated.mean(axis=0)      # one mean per channel
observation_means = calibrated.mean(axis=1)  # one mean per observation
```

**Interpretation standard:** broadcasting is not magic duplication; it is a documented alignment rule. Print both operand shapes and label each dimension before relying on an implicit expansion.

### Vectorization

Expression of elementwise/array-level computation without an explicit Python loop.

```python
values = np.array([1.0, 2.0, 3.0])
vectorized = values ** 2 + 1
looped = np.array([v ** 2 + 1 for v in values])
print("vectorized:", vectorized)
print("same as loop:", np.array_equal(vectorized, looped))  # True
```

Assume `*` is elementwise for arrays; use `@` for matrix products.

---

## 7. Case Study: Power and Quality Calculations

Power is computed elementwise; a quality rule marks readings outside plausible ranges.

```python
electrical = np.array(
    [
        [12.1, 1.20],
        [11.9, 1.35],
        [12.3, 1.10],
        [18.0, 9.50],   # out of plausible range
        [12.0, 1.28],
    ]
)

voltages = electrical[:, 0]
currents = electrical[:, 1]
power_w = voltages * currents
valid = (voltages >= 10) & (voltages <= 15) & (currents >= 0) & (currents <= 5)

report = {
    "power_w": np.round(power_w, 2).tolist(),
    "valid_rows": int(valid.sum()),
    "rejected_rows": int((~valid).sum()),
    "mean_valid_power_w": round(float(power_w[valid].mean()), 2),
}
```

**Key point:** speed is not the only goal. Report the denominator explicitly — "mean of four valid rows" is different from "mean of five received rows." Handle an empty valid selection before calling `.mean()`. Vectorization reduces loop syntax but does not remove responsibilities like shape, units, validation rules, retained/rejected counts, and range checks.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Assuming `*` is matrix multiplication | `*` is elementwise; use `@` for matrix products |
| Combining masks with `and`/`or` | Parenthesize each comparison and use `&`/`|`/`~` |
| Ignoring shape after slicing or reshaping | Check `.shape` after every structural operation |
| Accidentally modifying the original via a view | Use `.copy()` before destructive edits |
| Integer dtype truncating a calculation | Request `dtype=float` when the math needs precision |

---

## Key Takeaways

1. **Shape and dtype are part of the meaning** of numerical data.
2. **Indexing, masks, and reshaping should be followed by explicit checks** (shape, count, range).
3. **Slices are views**; use `.copy()` to protect the original.
4. **Boolean masks use `&`, `|`, `~`** with parenthesized comparisons.
5. **`axis=0` reduces rows (one per column); `axis=1` reduces columns (one per row)**.
6. **Broadcasting aligns from the trailing dimension** when shapes are equal or one is 1.
7. **Vectorize elementwise operations** but still validate, report units, and state denominators.
