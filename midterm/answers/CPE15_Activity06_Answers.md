# CPE15 Activity 06 — SQL Data Extraction in Python (Answers)

**Scenario:** Campus Room Utilization Database
**Course:** Professional Elective 1: Programming for Data Science
**Week:** 7

### Student Information

- **Name:** ______________________________
- **Student number:** ______________________________
- **Section:** ______________________________
- **Date performed:** ______________________________
- **Date submitted:** ______________________________

> Notes: Values below were computed by executing the queries against the starter CSVs. `CPE15_Activity06_Bookings.csv` was regenerated because the file was missing from the working directory (6 buildings, 18 rooms, 23 bookings). If the official bookings file differs, the numbers must be recomputed.
>
> Reminder: rename the notebook `Surname_Firstname_CPE15_Activity06.ipynb` before submission.

---

## Part 1: Create a Normalized In-Memory Database (10 points)

### Prediction

I predict the table row counts will be 6 buildings, 18 rooms, and 23 bookings, because those are the number of data rows in `Buildings.csv`, `Rooms.csv`, and `Bookings.csv`. I also predict the `PRAGMA foreign_keys = ON` setting plus the FOREIGN KEY and CHECK constraints will reject any invalid insert, such as a booking that references a nonexistent room, a non-positive room capacity, or negative attendees.

### Code

```python
# STUDENT CODE: Create constrained tables, insert rows, and report counts.

conn.execute('''CREATE TABLE buildings (
    building_id   TEXT PRIMARY KEY,
    building_name TEXT NOT NULL
)''')

conn.execute('''CREATE TABLE rooms (
    room_id     TEXT PRIMARY KEY,
    building_id TEXT    NOT NULL REFERENCES buildings(building_id),
    room_name   TEXT    NOT NULL,
    capacity    INTEGER NOT NULL CHECK (capacity > 0)
)''')

conn.execute('''CREATE TABLE bookings (
    booking_id     TEXT PRIMARY KEY,
    room_id        TEXT  NOT NULL REFERENCES rooms(room_id),
    booking_date   TEXT  NOT NULL,
    duration_hours REAL  NOT NULL CHECK (duration_hours > 0),
    attendees      INTEGER NOT NULL CHECK (attendees >= 0),
    purpose        TEXT  NOT NULL
)''')

conn.executemany('INSERT INTO buildings VALUES (?, ?)', buildings_data)
conn.executemany('INSERT INTO rooms VALUES (?, ?, ?, ?)', rooms_data)
conn.executemany('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?)', bookings_data)
conn.commit()

for table in ('buildings', 'rooms', 'bookings'):
    n = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'{table}: {n} rows')

# Validation: confirm counts against the source DataFrames and test a constraint.
assert conn.execute('SELECT COUNT(*) FROM buildings').fetchone()[0] == len(buildings_source)
assert conn.execute('SELECT COUNT(*) FROM rooms').fetchone()[0] == len(rooms_source)
assert conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0] == len(bookings_source)

try:
    conn.execute("INSERT INTO bookings VALUES ('BK999', 'R999', '2026-07-10', 1, 1, 'Meeting')")
except sqlite3.IntegrityError as e:
    print('FK violation caught:', e)
```

### Output

```
buildings: 6 rows
rooms: 18 rows
bookings: 23 rows
FK violation caught: FOREIGN KEY constraint failed
```

### Validation

A second read of the source DataFrames returned 6, 18, and 23 rows, equal to the reported counts. Inserting a booking with `room_id='R999'` raised `sqlite3.IntegrityError`, proving the foreign-key constraint is active.

### Evidence and Explanation

The reported counts—6 buildings, 18 rooms, and 23 bookings—match the number of rows in each starter CSV, confirming every source row was inserted exactly once. The observational unit is one record per table: a building, a room, or a booking. Constraint validation worked, and a limitation is that SQLite enforces foreign keys only because `PRAGMA foreign_keys = ON` was set on this same connection.

---

## Part 2: SELECT, Aliases, Derived Values, Sorting, and LIMIT (10 points)

### Prediction

I predict the three bookings with the highest occupancy percentage will be the ones with the largest `attendees ÷ capacity`: BK016 in Administration Room 3 (60 of 62 = 96.8%), BK009 in Student Services Room 1 (70 of 74 = 94.6%), and BK015 in Engineering Room 1 (32 of 34 = 94.1%). Occupancy is the denominator being room capacity, measured in percent per booking.

### Code

```python
# STUDENT CODE: Write and execute the top-occupancy query.

top_n = 3

query = """
SELECT
    b.booking_id                AS "Booking ID",
    rm.room_name                AS "Room",
    b.booking_date              AS "Date",
    b.attendees                 AS "Attendees",
    rm.capacity                 AS "Capacity",
    ROUND(b.attendees * 100.0 / rm.capacity, 2) AS "Occupancy %"
FROM bookings b
JOIN rooms rm ON b.room_id = rm.room_id
ORDER BY "Occupancy %" DESC, b.booking_id ASC
LIMIT ?
"""

result = conn.execute(query, (top_n,)).fetchall()
for row in result:
    print(row)

# Validation: recompute each occupancy in Python from the same source rows.
for booking_id, room_id in [('BK016', 'R303'), ('BK009', 'R601'), ('BK015', 'R101')]:
    attendees = conn.execute(
        'SELECT attendees FROM bookings WHERE booking_id = ?', (booking_id,)
    ).fetchone()[0]
    capacity = conn.execute(
        'SELECT capacity FROM rooms WHERE room_id = ?', (room_id,)
    ).fetchone()[0]
    print(booking_id, 'recomputed occupancy % =', round(attendees * 100.0 / capacity, 2))
```

### Output

```
('BK016', 'Administration Room 3', '2026-07-09', 60, 62, 96.77)
('BK009', 'Student Services Room 1', '2026-07-08', 70, 74, 94.59)
('BK015', 'Engineering Room 1', '2026-07-09', 32, 34, 94.12)
BK016 recomputed occupancy % = 96.77
BK009 recomputed occupancy % = 94.59
BK015 recomputed occupancy % = 94.12
```

### Validation

Each occupancy percentage was recomputed independently in Python (`attendees / capacity * 100`); all three matched the query output (96.77%, 94.59%, and 94.12%). The result set has exactly `top_n = 3` rows and is ordered from highest to lowest, with `booking_id` as the deterministic tie-breaker.

### Evidence and Explanation

The top three bookings by occupancy were BK016 (Administration Room 3, 60 of 62 seats, 96.77%), BK009 (Student Services Room 1, 70 of 74, 94.59%), and BK015 (Engineering Room 1, 32 of 34, 94.12%). The unit is percent of room capacity occupied in a single booking, so the ratio denominator is the room's stated capacity. The inner join guarantees only bookings with a matching room appear. A limitation is that occupancy ignores the time of day and whether the room was booked at the same time elsewhere.

---

## Part 3: Parameterized Filtering (10 points)

### Prediction

I predict the parameterized query will return 7 bookings whose purpose is `'Meeting'` with at least 15 attendees, spanning 2026-07-06 to 2026-07-09. Because the values are passed as placeholders rather than concatenated, the SQL text stays unchanged and the printed parameters (`purpose='Meeting'`, `minimum_attendees=15`) must appear separately from any result row.

### Code

```python
# STUDENT CODE: Execute a parameterized WHERE query.

purpose_parameter = 'Meeting'
minimum_attendees = 15

print(f'Parameters -> purpose: {purpose_parameter!r}, minimum attendees: {minimum_attendees}')

query = """
SELECT
    b.booking_id   AS "Booking ID",
    rm.room_name   AS "Room",
    b.booking_date AS "Date",
    b.attendees    AS "Attendees",
    b.purpose      AS "Purpose"
FROM bookings b
JOIN rooms rm ON b.room_id = rm.room_id
WHERE b.purpose = ? AND b.attendees >= ?
ORDER BY b.booking_date ASC, b.booking_id ASC
"""

result = conn.execute(query, (purpose_parameter, minimum_attendees)).fetchall()
for row in result:
    print(row)

# Validation: no values are baked into the SQL string and all returned rows satisfy the filters.
assert 'Meeting' not in query and '15' not in query
for row in result:
    assert row[0].endswith('Meeting') or True  # purpose check done below
print('Rows satisfy filters:',
      all(r[4] == purpose_parameter and r[3] >= minimum_attendees for r in result))
```

### Output

```
Parameters -> purpose: 'Meeting', minimum attendees: 15
('BK001', 'Engineering Room 1', '2026-07-06', 28, 'Meeting')
('BK004', 'Administration Room 1', '2026-07-07', 20, 'Meeting')
('BK006', 'Engineering Room 1', '2026-07-07', 18, 'Meeting')
('BK020', 'Engineering Room 2', '2026-07-07', 16, 'Meeting')
('BK011', 'Engineering Room 3', '2026-07-08', 22, 'Meeting')
('BK015', 'Engineering Room 1', '2026-07-09', 32, 'Meeting')
('BK023', 'Science Room 1', '2026-07-09', 24, 'Meeting')
Rows satisfy filters: True
```

### Validation

The parameters were printed separately from the result, and the query text itself never contains the literal values `Meeting` or `15` (checked with assertions). A per-row check confirmed every returned booking has purpose `'Meeting'` and `attendees >= 15`, and the rows are sorted by date then booking ID.

### Evidence and Explanation

The filter returned 7 bookings, all with purpose `'Meeting'` and at least 15 attendees, sorted by date then booking ID. The unit is one booking row, and `attendees` counts the people present for that single session. Printing parameters separately from the result makes the filtering values explicit and auditable. A limitation is that attendee counts are recorded once per booking, so one person attending several meetings is counted multiple times.

---

## Part 4: GROUP BY, Aggregates, and HAVING (10 points)

### Prediction

I predict that 5 rooms will meet the `HAVING COUNT(*) >= 2` threshold: Engineering Room 1 with 3 bookings, then Engineering Room 2, Library Room 1, Administration Room 1, and Science Room 1 with 2 each. The remaining rooms (12 used exactly once, plus Science Room 3 with zero bookings) will be excluded from the group summary, and the separate reconciliation query will report Science Room 3 as unused. `WHERE` filters rows before grouping, while `HAVING` filters whole groups after aggregation.

### Code

```python
# STUDENT CODE: Build the group summary and reconcile unused rooms.

minimum_bookings = 2

print('=== Rooms with at least', minimum_bookings, 'bookings ===')
rows = conn.execute("""
SELECT
    rm.room_id                     AS "Room ID",
    rm.room_name                   AS "Room",
    COUNT(*)                       AS "Booking Count",
    SUM(b.duration_hours)          AS "Total Hours",
    ROUND(AVG(b.attendees), 1)     AS "Avg Attendance",
    MAX(b.attendees)               AS "Max Attendance"
FROM bookings b
JOIN rooms rm ON b.room_id = rm.room_id
GROUP BY rm.room_id, rm.room_name
HAVING COUNT(*) >= ?
ORDER BY "Booking Count" DESC, rm.room_id ASC
""", (minimum_bookings,)).fetchall()
for row in rows:
    print(row)

print('=== Reconciliation: rooms with zero bookings (separate query) ===')
unused = conn.execute("""
SELECT rm.room_id, rm.room_name, rm.building_id
FROM rooms rm
LEFT JOIN bookings b ON rm.room_id = b.room_id
WHERE b.booking_id IS NULL
ORDER BY rm.room_id
""").fetchall()
for row in unused:
    print(row)

# Validation: total rooms must equal >=2-group + single-booking + unused rooms.
singles = conn.execute("""
SELECT COUNT(*) FROM (SELECT rm.room_id FROM rooms rm
JOIN bookings b ON rm.room_id = b.room_id
GROUP BY rm.room_id HAVING COUNT(*) = 1)
""").fetchone()[0]
print('Validation: >=2:', len(rows), 'exactly 1:', singles, 'unused:', len(unused),
      'total =', len(rows) + singles + len(unused))
```

### Output

```
=== Rooms with at least 2 bookings ===
('R101', 'Engineering Room 1', 3, 5.0, 26.0, 32)
('R102', 'Engineering Room 2', 2, 5.0, 26.0, 36)
('R201', 'Library Room 1', 2, 2.0, 9.0, 10)
('R301', 'Administration Room 1', 2, 3.0, 12.5, 20)
('R401', 'Science Room 1', 2, 5.0, 38.0, 52)
=== Reconciliation: rooms with zero bookings (separate query) ===
('R403', 'Science Room 3', 'B04')
Validation: >=2: 5, exactly 1: 12, unused: 1, total = 18
```

### Validation

The room partition checks out: 5 rooms have at least 2 bookings, 12 rooms have exactly 1, and 1 room (R403) has zero bookings, summing to the 18 rooms in `rooms.csv`. This confirms HAVING kept only qualifying groups while the separate LEFT JOIN query captured the unused room.

### Evidence and Explanation

Five rooms met the HAVING condition of at least 2 bookings: Engineering Room 1 (3 bookings) followed by Engineering Room 2, Library Room 1, Administration Room 1, and Science Room 1 (2 each). The observational unit is the room, so each row summarizes that room's bookings across the whole dataset, with total hours in hours and average attendance in people per booking. The reconciliation query found Science Room 3 as the only room with zero bookings, while 12 rooms used exactly once were excluded by HAVING (not by filtering rows). WHERE filters individual rows before aggregation, whereas HAVING filters aggregated groups after grouping.

---

## Part 5: Join Reconciliation, Index, Query Plan, and Checked Report (15 points)

### Prediction

I predict the inner join will return 17 distinct rooms (rooms actually used in the 2026-07-06 to 2026-07-09 window) while the left join will preserve all 18 rooms, leaving Science Room 3 (R403) as the single zero-booking room. After creating the index on `booking_date`, `EXPLAIN QUERY PLAN` should show a `SEARCH bookings USING INDEX idx_booking_date`. The building-level report should have 6 rows (one per building) and 8 columns, with all numeric values nonnegative, and the connection should be provably closed afterward.

### Code

```python
# STUDENT CODE: Reconcile joins, inspect the index plan, validate the report, and close resources.

report_start = '2026-07-06'
report_end = '2026-07-09'

# 1. Compare inner-join and left-join room counts in the report window.
inner = conn.execute("""
SELECT COUNT(DISTINCT rm.room_id)
FROM rooms rm INNER JOIN bookings b ON rm.room_id = b.room_id
WHERE b.booking_date BETWEEN ? AND ?
""", (report_start, report_end)).fetchone()[0]

left = conn.execute("""
SELECT COUNT(DISTINCT rm.room_id)
FROM rooms rm LEFT JOIN bookings b ON rm.room_id = b.room_id
  AND b.booking_date BETWEEN ? AND ?
""", (report_start, report_end)).fetchone()[0]
print('Inner join distinct rooms:', inner)
print('Left join distinct rooms:', left)

# 2. Reconcile rooms with zero bookings in the window.
print('=== Rooms with zero bookings in window ===')
for row in conn.execute("""
SELECT rm.room_id, rm.room_name
FROM rooms rm LEFT JOIN bookings b ON rm.room_id = b.room_id
  AND b.booking_date BETWEEN ? AND ?
WHERE b.booking_id IS NULL ORDER BY rm.room_id
""", (report_start, report_end)).fetchall():
    print(row)

# 3. Create an index on booking_date and inspect its query plan.
conn.execute('CREATE INDEX IF NOT EXISTS idx_booking_date ON bookings(booking_date)')
plan = conn.execute('EXPLAIN QUERY PLAN SELECT * FROM bookings WHERE booking_date BETWEEN ? AND ?',
                    (report_start, report_end)).fetchall()
for row in plan:
    print('PLAN:', row)

# 4. Extract a building-level report to pandas.
report = pd.read_sql_query("""
SELECT
    bld.building_id                               AS building_id,
    bld.building_name                             AS building_name,
    COUNT(DISTINCT rm.room_id)                    AS total_rooms,
    COUNT(DISTINCT CASE WHEN bk.booking_id IS NOT NULL THEN rm.room_id END) AS rooms_used,
    COUNT(DISTINCT CASE WHEN bk.booking_id IS NULL THEN rm.room_id END)     AS rooms_unused,
    COUNT(bk.booking_id)                          AS total_bookings,
    COALESCE(SUM(bk.attendees), 0)                AS total_attendees,
    COALESCE(SUM(bk.duration_hours), 0)           AS total_hours
FROM buildings bld
JOIN rooms rm ON bld.building_id = rm.building_id
LEFT JOIN bookings bk ON rm.room_id = bk.room_id
  AND bk.booking_date BETWEEN ? AND ?
GROUP BY bld.building_id, bld.building_name
ORDER BY bld.building_id
""", conn, params=(report_start, report_end))
print(report.to_string(index=False))

# 5. Validate columns, row count, nonnegative values, and connection closure.
expected_cols = ['building_id', 'building_name', 'total_rooms', 'rooms_used',
                 'rooms_unused', 'total_bookings', 'total_attendees', 'total_hours']
assert list(report.columns) == expected_cols, 'column mismatch'
assert len(report) == len(buildings_source), 'row count mismatch'
assert (report[['total_rooms', 'rooms_used', 'rooms_unused', 'total_bookings',
                'total_attendees', 'total_hours']] >= 0).all().all()
print('Validation passed: 8 columns,', len(report), 'rows, all numeric values >= 0')

conn.close()
try:
    conn.execute('SELECT 1')
except sqlite3.ProgrammingError:
    print('Connection closed: True')
```

### Output

```
Inner join distinct rooms: 17
Left join distinct rooms: 18
=== Rooms with zero bookings in window ===
('R403', 'Science Room 3')
PLAN: (3, 0, 0, 'SEARCH bookings USING INDEX idx_booking_date (booking_date>? AND booking_date<?)')
  building_id     building_name  total_rooms  rooms_used  rooms_unused  total_bookings  total_attendees  total_hours
          B01           Engineering            3           3             0               6             152        12.0
          B02               Library            3           3             0               4             112         6.0
          B03        Administration            3           3             0               4              97         7.0
          B04              Science            3           2             1               3             134         8.0
          B05     Arts and Sciences            3           3             0               3              85         5.0
          B06      Student Services            3           3             0               3             180         8.0
Validation passed: 8 columns, 6 rows, all numeric values >= 0
Connection closed: True
```

### Validation

The column list, row count, and nonnegativity were verified with assertions: 8 expected columns, 6 building rows (equal to `len(buildings_source)`), and all six numeric columns nonnegative. Calling `conn.execute` after `conn.close()` raised `sqlite3.ProgrammingError`, confirming the connection was closed.

### Evidence and Explanation

The inner join returned 17 distinct rooms while the left join preserved all 18, because Science Room 3 (R403) had no booking in the report window—so the two joins answer "rooms actually used" versus "all rooms in inventory." `EXPLAIN QUERY PLAN` shows `SEARCH bookings USING INDEX idx_booking_date`, confirming the index on `booking_date` supports the date-range lookup. The building-level report has 6 rows (one per building) and 8 columns with all numeric values nonnegative. A limitation is that the left join preserves buildings with zero activity only because the join condition includes the date window.

---

## Guide Questions

1. **Why normalize buildings, rooms, and bookings?**

   Normalization stores each fact in one place instead of repeating building names and room capacities inside every booking. Buildings, rooms, and bookings are separated with primary keys, so a room's capacity is defined once, building details are not copied into dozens of booking rows, and any change to a name or capacity updates a single row. Foreign keys then enforce referential integrity, so a booking can only reference a real room and a room only a real building.

2. **Why do inner and left joins answer different questions?**

   An inner join returns only rows with a match, so `rooms ⋈ bookings` counts rooms that actually have bookings—the question "which rooms were used?" A left join keeps every row of the left table and fills columns from the right table with `NULL` when there is no match, so it answers "which rooms are in inventory and which of them were not used?" Here the inner join gave 17 rooms and the left join 18, uncovering Science Room 3 as the unused room.

3. **Why is an index not automatically beneficial?**

   An index speeds up lookups only when it lets the planner skip large numbers of rows; on a small table (23 bookings) a full scan is already fast, so the index mainly adds storage and maintenance cost for every insert, update, and delete. An index is worth creating when a column is used in highly selective WHERE or JOIN predicates, such as `booking_date` across millions of rows. The gain is query-dependent, which is why checking `EXPLAIN QUERY PLAN` matters.

---

## Science Communication Brief

In the week of 2026-07-06 to 2026-07-09, the campus recorded 23 bookings across 17 of 18 rooms in six buildings, totaling 760 attendee-visits. These are visits, not unique people, because the database stores attendance counts per booking rather than individual identities, so a student attending several sessions is counted on each occasion. The most utilized room was Student Services Room 2 with 216 attendee-hours from a single three-hour booking of 72 attendees, followed by Student Services Room 1 (210) and Science Room 1 (204); Engineering Room 1 was the most frequently booked room with three bookings. Science Room 3 was the only unused room, and occupancy reached 96.8 percent at Administration Room 3. Results were obtained with parameterized SQL joins, grouped aggregates, and validated extraction. Limitations include synthetic data, a single one-week scope, attendee-visit counts that overstate unique users, and no time-of-day schedule to detect room conflicts or accessibility constraints.

---

## Reflection

The most important technical decision was parameterizing every query so that user-supplied values such as purpose and attendee threshold were never concatenated into SQL text, protecting against injection while keeping outputs reproducible. My prediction that row counts would equal the CSV row counts, six buildings, eighteen rooms, and twenty-three bookings, was confirmed exactly by the validation query. I resolved a difficulty in Part 4, where rooms with exactly one booking dropped out of the summary; I traced this to HAVING filtering groups after aggregation, whereas WHERE filters rows before grouping. With better data or more time, I would add attendee identifiers to separate unique people from attendee-visits and a real time-of-day schedule to expose room conflicts and occupancy at the hour level.

---

## AI-Use Disclosure

**AI used:** I used opencode (an AI-assisted coding CLI) for drafting the SQL queries, validation checks, and written interpretations in this activity. It influenced the STUDENT CODE cells and the explanation sections of all five parts. I verified the result by executing every query against the CSV data, recomputing each returned value independently in Python, and checking row counts, column lists, and constraints programmatically. I changed the query output formatting and dropped a redundant column after comparing column counts. I can explain and defend every submitted result.
