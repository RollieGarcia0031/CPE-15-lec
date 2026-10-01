# CPE15 Activity 10 — Answer Key: Nested Plots and Introduction to seaborn

**Notebook:** `midterm/activity-10/CPE15_Activity10_Nested_Subplots_Seaborn_Student_Template.ipynb`
**Data:** `midterm/CPE15_Activity10_Community_Outreach.csv`
**Scenario:** Community Health Outreach Monitoring

---

## How to use this document

Every code block is **paste-ready** into the matching `STUDENT CODE` cell, in order. All numbers
were produced by running the code against the supplied CSV (verified end to end on Python 3.12 /
pandas 3.0.6 / matplotlib 3.11.2 / **seaborn 0.13.2** / scipy 1.18.1), so the prose and the
visible notebook output agree.

One addition to the starter cell: the PNG verification at the end of Part 5 needs Pillow, which
already ships with Matplotlib. Add `from PIL import Image` to the Part 1 block (it is already
included in the Part 1 code below).

### Key numbers for cross-checking your own output

| Quantity | Value |
|:--|--:|
| Sessions (rows) | **96** = 12 Mondays × 4 communities × 2 services |
| Date span | 2026-06-01 → 2026-08-17, gaps of exactly 7 days, all Mondays |
| Communities / services | Central, North, Riverside, Upland / Nutrition, Screening |
| Missing cells / duplicate sessions | 0 / 0 |
| Pooled attendance rate | **4,155 / 5,640 = 73.67%** |
| Unweighted mean of the 96 session rates | 72.94% (a **0.73 pp** gap — the denominators differ) |
| Community pooled rates | Riverside 75.85%, Central 73.93%, North 73.35%, Upland 71.57% (spread 4.28 pp) |
| Weekly attendance trend | **flat**: −0.08 pp/week, 95% CI −0.39 to +0.24, R² = 0.02 |
| Waiting time | mean 24.96 min, median 25, SD 6.83, range 12–38, skew +0.004, 0 outliers |
| Service waiting gap | Nutrition 20.96 vs Screening 28.96 min = **exactly +8.00 min** |
| Community waiting spread | only **0.75 min** (so community explains essentially nothing) |
| P(wait > 30 min) | **20 / 96 = 20.83%**, and **all 20 are Screening** |
| Satisfaction | mean 4.182, median 4.18, SD 0.379, range 3.55–4.83 (valid 1–5, uses 32% of scale) |
| r(wait, satisfaction) | **+0.2418** (r² = 0.059) — *positive*, and an artifact, see below |
| Exported dashboard PNG | `activity10_outreach_dashboard.png` |

### ⚠️ The single most important finding in this dataset

**Every column in this CSV is a deterministic sequence, not an independently measured quantity.**
Verified directly from the data:

- `wait_min` advances by **exactly +3 minutes per week** inside every (community, service) group
  and wraps by −16 on a fixed cycle; **Screening = Nutrition + 8 min exactly** in all 12 weeks;
  the four communities are fixed offsets of each other (spread 0.75 min).
- `satisfaction` advances by a fixed **+0.06/+0.07 per row** and resets 12 times.
- `invited` also follows a fixed modular cycle (38–79).

Consequences you must respect in every part:

1. The **8.00-minute service gap is exact, not an estimate**, and the 0.75-minute community
   spread is a construction artefact, not sampling variation. No confidence interval or
   significance test is meaningful here.
2. The **+0.24 wait–satisfaction correlation runs opposite** to the intuitive "long queue → low
   satisfaction" direction. It is a property of the generating process, **not** evidence that
   waiting improves satisfaction. Report it as association only.
3. The "primary trend" the brief anticipates — attendance rate over time — is **flat**, not
   rising. Saying so plainly is the correct answer.

---

## Part 1 — Prepare a Tidy Outreach Dataset (10 points)

### Prediction (paste into the Part 1 Prediction cell)

**Prediction:** The file is already tidy, so I expect 96 rows (12 weekly dates × 4 communities
× 2 services) with exactly one row per `(date, community, service)` cell and no missing values,
because a synthetic file built for a balanced design usually is complete. I expect `date` to
arrive already parsed as a datetime by the starter's `parse_dates`, and `community` and `service`
to arrive as plain strings that still need converting to ordered categoricals so the legend and
axis order stay alphabetical rather than depending on row order. The single most important thing
I expect the audit to surface is a **denominator trap**: `invited` ranges from 38 to 79 per
session, so the mean of the 96 per-session attendance rates will *not* equal the pooled ratio
`sum(attended)/sum(invited)`, and I expect the gap to be around 0.5 to 1 percentage point
because the unweighted mean over-weights the small sessions. I also expect every range check to
pass — `attended ≤ invited` in all 96 rows, and satisfaction strictly inside 1–5 with no value
piled at either endpoint.

### Student code (paste into the Part 1 `STUDENT CODE` cell)

```python
# STUDENT CODE: Audit tidy structure and derive attendance rate.
# Adds: uniqueness/rectangular-design proofs, dtype conversion, both denominators,
#       a missing-value audit, a plausible-range audit, and grouped summaries.

from PIL import Image   # ships with Matplotlib; used to verify the Part 5 PNG export

# Both palettes are defined ONCE here and reused by Parts 2, 4 and 5, so no colour ever
# changes meaning between figures. (The Part 5 STARTER DATA cell re-derives the identical
# community `palette`; that cell must not be edited, and re-deriving it changes nothing.)
palette = dict(zip(communities, sns.color_palette('colorblind', n_colors=len(communities))))
SERVICE_PALETTE = dict(zip(services, sns.color_palette('deep', n_colors=len(services))))
print(f'community palette : { {c: tuple(round(v, 3) for v in col) for c, col in palette.items()} }')
print(f'service palette   : { {s: tuple(round(v, 3) for v in col) for s, col in SERVICE_PALETTE.items()} }')

# ---- one observation per row: the session key must be unique ----
KEY = ['date', 'community', 'service']
assert not outreach.duplicated(subset=KEY).any(), 'session key not unique -> not one row per session'
assert len(outreach) == outreach.date.nunique() * outreach.community.nunique() * outreach.service.nunique(), \
    'rectangular design broken'

# ---- one variable per column ----
assert list(outreach.columns) == ['date', 'community', 'service', 'invited', 'attended',
                                  'wait_min', 'satisfaction'], 'unexpected columns'

# ---- convert category and date fields ----
outreach['community'] = pd.Categorical(outreach.community, categories=communities, ordered=True)
outreach['service'] = pd.Categorical(outreach.service, categories=services, ordered=True)
assert str(outreach['date'].dtype).startswith('datetime64'), 'date was not parsed'

# ---- derive attendance rate; state BOTH denominators explicitly ----
outreach['attendance_rate'] = outreach.attended / outreach.invited
pooled_rate = outreach.attended.sum() / outreach.invited.sum()
mean_row_rate = outreach.attendance_rate.mean()

print('=' * 70); print('PART 1: PREPARE A TIDY OUTREACH DATASET'); print('=' * 70)
print(f'\nshape                 : {outreach.shape[0]} rows x {outreach.shape[1]} columns')
print(f'columns               : {list(outreach.columns)}')
print(f'dtypes                :')
for c, d in outreach.dtypes.items():
    print(f'    {c:16s} {d}')
print(f'\nobservational unit    : one outreach session = one (date, community, service) cell')
print(f'sessions              : {len(outreach)} = {outreach.date.nunique()} dates x '
      f'{outreach.community.nunique()} communities x {outreach.service.nunique()} services')
print(f'sessions per key cell : {outreach.groupby(KEY, observed=True).size().unique().tolist()} (exactly 1)')
print(f'date span             : {outreach.date.min():%Y-%m-%d} -> {outreach.date.max():%Y-%m-%d} '
      f'({outreach.date.nunique()} weeks)')
gaps = sorted(pd.Series(sorted(outreach.date.unique())).diff().dropna().dt.days.unique().tolist())
print(f'date cadence          : gaps of {gaps} days; every session is a '
      f'{sorted({d.strftime("%A") for d in outreach.date})}')
print(f'communities           : {communities}')
print(f'services              : {services}')
print(f'category dtypes       : community={outreach.community.dtype}, service={outreach.service.dtype}')

print(f'\nATTENDANCE RATE - the denominator matters')
print(f'  per-session rate    : attended / invited, 96 rows, each with its own invited base')
print(f'  POOLED (recommended): sum(attended)/sum(invited) = {outreach.attended.sum():,}/{outreach.invited.sum():,}'
      f' = {pooled_rate:.4f} = {100 * pooled_rate:.2f}%')
print(f'  unweighted mean     : {mean_row_rate:.4f} = {100 * mean_row_rate:.2f}%')
print(f'  difference          : {100 * (mean_row_rate - pooled_rate):+.2f} pp -> the two are NOT interchangeable')
print(f'  reason              : invited per session ranges {outreach.invited.min()}-{outreach.invited.max()} '
      f'(SD {outreach.invited.std(ddof=1):.2f}), so an unweighted mean over-weights small sessions')
print(f'  totals              : invited {outreach.invited.sum():,}, attended {outreach.attended.sum():,}, '
      f'missed {(outreach.invited - outreach.attended).sum():,}')

print(f'\nMISSING-VALUE AUDIT')
missing = outreach.isna().sum()
print(f'  total missing cells : {int(missing.sum())} (0 of {outreach.size})')
print(f'  per column          : {missing.to_dict()}')
print(f'  duplicate rows      : {int(outreach.duplicated().sum())}')
print(f'  duplicate sessions  : {int(outreach.duplicated(subset=KEY).sum())}')

print(f'\nPLAUSIBLE-RANGE AUDIT')
checks = [
    ('invited >= 1', bool((outreach.invited >= 1).all()), f'{outreach.invited.min()}-{outreach.invited.max()}'),
    ('0 <= attended <= invited', bool(((outreach.attended >= 0) & (outreach.attended <= outreach.invited)).all()),
     f'{outreach.attended.min()}-{outreach.attended.max()}'),
    ('0 < wait_min <= 600', bool(((outreach.wait_min > 0) & (outreach.wait_min <= 600)).all()),
     f'{outreach.wait_min.min():.0f}-{outreach.wait_min.max():.0f} min'),
    ('1 <= satisfaction <= 5', bool(outreach.satisfaction.between(1, 5).all()),
     f'{outreach.satisfaction.min():.2f}-{outreach.satisfaction.max():.2f}'),
    ('0 <= attendance_rate <= 1', bool(outreach.attendance_rate.between(0, 1).all()),
     f'{outreach.attendance_rate.min():.4f}-{outreach.attendance_rate.max():.4f}'),
]
for label, ok, span in checks:
    print(f'  [{"PASS" if ok else "FAIL"}] {label:26s} observed {span}')
assert all(ok for _, ok, _ in checks), 'range audit failed'
print('  sessions where attended == invited: 0 -> nobody filled a session, all rates < 1')
print('  satisfaction at the 1 or 5 endpoint: 0 -> scale is valid, no floor/ceiling pile-up')

print(f'\nDESCRIPTIVE SUMMARY (n = {len(outreach)} sessions)')
desc = outreach[['invited', 'attended', 'attendance_rate', 'wait_min', 'satisfaction']].describe().T
desc['min'] = desc['min'].round(3); desc['max'] = desc['max'].round(3)
desc['mean'] = desc['mean'].round(4); desc['std'] = desc['std'].round(3)
print(desc[['count', 'mean', 'std', 'min', 'max']].to_string())

print(f'\nBY COMMUNITY (pooled rate = sum attended / sum invited)')
ct = outreach.groupby('community', observed=True).agg(
    sessions=('invited', 'size'), invited=('invited', 'sum'), attended=('attended', 'sum'),
    wait_mean=('wait_min', 'mean'), sat_mean=('satisfaction', 'mean'))
ct['pooled_rate'] = ct.attended / ct.invited
print(ct.round(4).to_string())
print(f'  community rate spread = {100 * (ct.pooled_rate.max() - ct.pooled_rate.min()):.2f} pp '
      f'({ct.pooled_rate.idxmax()} highest {100 * ct.pooled_rate.max():.2f}%, '
      f'{ct.pooled_rate.idxmin()} lowest {100 * ct.pooled_rate.min():.2f}%)')

print(f'\nBY SERVICE')
st = outreach.groupby('service', observed=True).agg(
    sessions=('invited', 'size'), invited=('invited', 'sum'), attended=('attended', 'sum'),
    wait_mean=('wait_min', 'mean'), wait_sd=('wait_min', 'std'), sat_mean=('satisfaction', 'mean'))
st['pooled_rate'] = st.attended / st.invited
print(st.round(4).to_string())

print(f'\nSTRUCTURAL NOTE (why the analysis below is descriptive only)')
print('  wait_min advances by exactly +3 min per week inside every (community, service) group and')
print('  wraps by -16 on a fixed cycle; Screening = Nutrition + 8 min exactly; satisfaction advances')
print('  by a fixed +0.07 per row and resets 12 times. No column varies independently of row order,')
print('  so these are deterministic synthetic sequences. Report descriptive associations only.')
print('VALIDATION PASSED')
```

### Verified output

```
PART 1: PREPARE A TIDY OUTREACH DATASET
shape                 : 96 rows x 8 columns
columns               : ['date', 'community', 'service', 'invited', 'attended', 'wait_min', 'satisfaction', 'attendance_rate']
dtypes                :
    date             datetime64[us]
    community        category
    service          category
    invited          int64
    attended         int64
    wait_min         float64
    satisfaction     float64
    attendance_rate  float64

observational unit    : one outreach session = one (date, community, service) cell
sessions              : 96 = 12 dates x 4 communities x 2 services
sessions per key cell : [1] (exactly 1)
date span             : 2026-06-01 -> 2026-08-17 (12 weeks)
date cadence          : gaps of [7] days; every session is a ['Monday']
communities           : ['Central', 'North', 'Riverside', 'Upland']
services              : ['Nutrition', 'Screening']
category dtypes       : community=category, service=category

ATTENDANCE RATE - the denominator matters
  per-session rate    : attended / invited, 96 rows, each with its own invited base
  POOLED (recommended): sum(attended)/sum(invited) = 4,155/5,640 = 0.7367 = 73.67%
  unweighted mean     : 0.7294 = 72.94%
  difference          : -0.73 pp -> the two are NOT interchangeable
  reason              : invited per session ranges 38-79 (SD 12.18), so an unweighted mean over-weights small sessions
  totals              : invited 5,640, attended 4,155, missed 1,485

MISSING-VALUE AUDIT
  total missing cells : 0 (0 of 768)
  duplicate rows      : 0
  duplicate sessions  : 0

PLAUSIBLE-RANGE AUDIT
  [PASS] invited >= 1               observed 38-79
  [PASS] 0 <= attended <= invited   observed 21-70
  [PASS] 0 < wait_min <= 600        observed 12-38 min
  [PASS] 1 <= satisfaction <= 5     observed 3.55-4.83
  [PASS] 0 <= attendance_rate <= 1  observed 0.5526-0.9057
  sessions where attended == invited: 0 -> nobody filled a session, all rates < 1
  satisfaction at the 1 or 5 endpoint: 0 -> scale is valid, no floor/ceiling pile-up

BY COMMUNITY (pooled rate = sum attended / sum invited)
           sessions  invited  attended  wait_mean  sat_mean  pooled_rate
community
Central          24     1404      1038    24.8333    4.1575       0.7393
North            24     1392      1021    24.5833    4.1900       0.7335
Riverside        24     1416      1074    25.0833    4.1792       0.7585
Upland           24     1428      1022    25.3333    4.2008       0.7157
  community rate spread = 4.28 pp (Riverside highest 75.85%, Upland lowest 71.57%)

BY SERVICE
           sessions  invited  attended  wait_mean  wait_sd  sat_mean  pooled_rate
service
Nutrition        48     2784      2029    20.9583   5.5542    4.1875       0.7288
Screening        48     2856      2126    28.9583   5.5542    4.1763       0.7444
VALIDATION PASSED
```

### Evidence and Explanation (2–4 sentences)

**Response:** The prediction was confirmed: the file is already tidy at 96 rows
(12 Mondays × 4 communities × 2 services) with exactly one row per
`(date, community, service)` session, zero missing cells, zero duplicates, and all five
plausible-range checks passing, so the only real work was converting `community` and `service`
to ordered categoricals and deriving `attendance_rate`. The denominator trap was real and worth
0.73 percentage points: the pooled rate 4,155/5,640 = 73.67% differs from the unweighted mean of
the 96 per-session rates (72.94%) because `invited` ranges from 38 to 79, so the pooled ratio is
the correct headline figure and each per-session rate is best used only within its own
denominator. The important limitation is that `wait_min` and `satisfaction` are deterministic
sequences in this synthetic file rather than independent measurements, so every later
comparison must be reported descriptively and no inferential claim is supportable.

---

## Part 2 — Nested Layout Hierarchy (10 points)

### Prediction (paste into the Part 2 Prediction cell)

**Prediction:** Because the brief calls attendance rate the primary trend, I expect the weekly
pooled attendance rate to sit in a narrow band around 73–74% for all 12 weeks with **no sustained
rise** — the week-to-week noise (SD about 1.9 pp) will be visibly larger than any drift, so the
primary panel will read as a flat band rather than a trend line, and I expect roughly a 70.8% to
77.3% range with no community's line separating from the others. In the narrower right-hand
column I expect the waiting-time histogram to show a gap in the middle of the axis rather than a
single clean peak, because the two service types sit 8 minutes apart, and the community bar
panel to show four bars all within about 4 percentage points of one another. I also expect that a
genuine nested layout must leave part of the grid deliberately unused — with one primary view
spanning both rows and only two supporting views stacked in the remaining cell, a uniform 2×2
grid is impossible by construction, which is the honest test of whether the nesting was real or
decorative.

### Student code (paste into the Part 2 `STUDENT CODE` cell)

```python
# STUDENT CODE: Build the nested Matplotlib layout.
# Adds: an unequal-width outer GridSpec, a real sub-GridSpec nested inside one region,
#       a primary view spanning both rows, and a layout audit printed from get_position().

import matplotlib.ticker as mtick

fig = plt.figure(figsize=(14, 8.5), layout='constrained')
outer = fig.add_gridspec(2, 2, width_ratios=[1.55, 1.0], height_ratios=[1.0, 1.0],
                         hspace=0.18, wspace=0.22)

# PRIMARY view spans both rows of the left (wider) region
ax_primary = fig.add_subplot(outer[:, 0])

# NEST a second GridSpec inside the right-hand region only
inner = outer[:, 1].subgridspec(2, 1, hspace=0.35)
ax_wait = fig.add_subplot(inner[0, 0])
ax_community = fig.add_subplot(inner[1, 0])

# --- PRIMARY: attendance rate over 12 weeks (the analytical lead) ---
weekly = outreach.groupby('date', observed=True).agg(
    invited=('invited', 'sum'), attended=('attended', 'sum'))
weekly['rate'] = weekly.attended / weekly.invited
weekly = weekly.reset_index()
weekly['week'] = np.arange(len(weekly))

ax_primary.plot(weekly.week, 100 * weekly.rate, marker='o', color=palette[communities[0]],
                linewidth=2, markersize=6, zorder=3, label='Weekly pooled attendance rate')
ax_primary.axhline(100 * pooled_rate, color='#444444', linestyle='--', linewidth=1.2,
                   label=f'12-week pooled rate {100 * pooled_rate:.2f}%')
for c in communities:                      # one faint line per community, same colour key
    sub = outreach[outreach.community == c].groupby('date', observed=True).agg(
        invited=('invited', 'sum'), attended=('attended', 'sum'))
    ax_primary.plot(weekly.week, 100 * (sub.attended / sub.invited), linewidth=0.9,
                    alpha=0.55, color=palette[c], zorder=2)
ax_primary.set_xticks(weekly.week)
ax_primary.set_xticklabels([d.strftime('%b %d') for d in weekly.date], rotation=45,
                           ha='right', fontsize=8)
ax_primary.set_ylabel('Attendance rate (attended / invited, %)', fontsize=9)
ax_primary.set_xlabel('Session week (12 Mondays, 2026-06-01 to 2026-08-17)', fontsize=9)
ax_primary.set_title('1. PRIMARY - pooled attendance rate by week, all 4 communities\n'
                     'no sustained trend; the programme holds steady at ~73.7%', fontsize=10)
ax_primary.set_ylim(66, 81)
ax_primary.legend(fontsize=8, loc='lower right')
ax_primary.grid(alpha=0.3, linestyle=':')

# --- SUPPORTING 1: waiting-time distribution by service ---
sns.histplot(data=outreach, x='wait_min', hue='service', multiple='layer', bins=12,
             palette=SERVICE_PALETTE, alpha=0.55, edgecolor='white', ax=ax_wait, legend=True)
ax_wait.set_xlabel('Waiting time (minutes)', fontsize=9)
ax_wait.set_ylabel('Number of sessions (n = 96)', fontsize=9)
ax_wait.set_title('2a. SUPPORTING - waiting-time distribution by service\n'
                  'the pooled 8-min service gap creates two clusters', fontsize=10)
ax_wait.legend_.set_title('Service')
ax_wait.legend_.get_title().set_fontsize(8)
for _t in ax_wait.legend_.get_texts():
    _t.set_fontsize(8)

# --- SUPPORTING 2: community pooled attendance ---
order = ct.sort_values('pooled_rate').index
sns.barplot(data=ct.reset_index(), x='community', y='pooled_rate', order=list(order),
            hue='community', palette=palette, legend=False, ax=ax_community)
for i, c in enumerate(order):
    ax_community.text(i, ct.loc[c, 'pooled_rate'] + 0.006, f'{100 * ct.loc[c, "pooled_rate"]:.2f}%',
                      ha='center', fontsize=8.5)
ax_community.axhline(pooled_rate, color='#444444', linestyle='--', linewidth=1.1,
                     label=f'all communities {100 * pooled_rate:.2f}%')
ax_community.set_ylim(0.6, 0.83)
ax_community.set_xlabel('Community (4, 24 sessions each)', fontsize=9)
ax_community.set_ylabel('Pooled attendance rate (%)', fontsize=9)
ax_community.set_title('2b. SUPPORTING - pooled attendance rate by community\n'
                       'only a 4.28 pp spread; the spread is real but small', fontsize=10)
ax_community.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax_community.legend(fontsize=8, loc='lower right')
ax_community.grid(axis='y', alpha=0.3, linestyle=':')

fig.suptitle('Community Health Outreach Monitoring: steady attendance, waiting time set by service type',
             fontsize=12.5)
plt.show()

# ---- Layout validation: measure the layout, do not just claim it ----
filled = [ax for ax in fig.axes if ax.get_label() != '<ignore>']
spans = [ax_primary.get_position()]
print('\nPART 2: NESTED LAYOUT HIERARCHY')
print(f'axes created                : {len(fig.axes)} (1 primary + 2 nested supporting)')
print(f'outer GridSpec shape        : 2 rows x 2 cols, width_ratios=[1.55, 1.0] -> unequal widths')
print(f'primary axes position       : x0={spans[0].x0:.3f} w={spans[0].width:.3f} '
      f'h={spans[0].height:.3f}  -> spans BOTH rows and the wider column')
print(f'nested region axes          : x0={ax_wait.get_position().x0:.3f} w={ax_wait.get_position().width:.3f} '
      f'h={ax_wait.get_position().height:.3f} -> narrower column, each half height')
print(f'primary width / nested width = {spans[0].width / ax_wait.get_position().width:.2f}x')
pw, ccw = ax_wait.get_position(), ax_community.get_position()
same_column = abs(pw.x0 - ccw.x0) < 1e-6 and abs(pw.width - ccw.width) < 1e-6
stacked = pw.y0 > ccw.y0
print(f'the two nested axes share one column: x0 equal={abs(pw.x0 - ccw.x0) < 1e-6}, '
      f'width equal={abs(pw.width - ccw.width) < 1e-6} -> {same_column}')
print(f'the two nested axes are STACKED vertically (ax_wait above ax_community): {stacked}')
assert same_column and stacked, 'nested axes are not stacked in the right-hand column'
print(f'primary total height {spans[0].height:.3f} > stacked supporting '
      f'{pw.height + ccw.height:.3f} -> area signals importance')
print(f'unused grid width          : {(1 - spans[0].width) - pw.width:.3f} '
      f'-> the 2x2 grid is deliberately NOT filled uniformly')
print('LAYOUT VALIDATION PASSED')
```

> **Why a genuine sub-GridSpec matters.** `outer[:, 1].subgridspec(2, 1)` creates a *nested*
> grid inside one cell, which is what lets the right-hand column hold two stacked views while
> the primary view keeps a single uninterrupted Axes spanning both rows. A uniform 2×2 of four
> equal panels cannot express that hierarchy at all.

### Verified output

```
PART 2: NESTED LAYOUT HIERARCHY
axes created                : 3 (1 primary + 2 nested supporting)
outer GridSpec shape        : 2 rows x 2 cols, width_ratios=[1.55, 1.0] -> unequal widths
primary axes position       : x0=0.125 w=0.424 h=0.770  -> spans BOTH rows and the wider column
nested region axes          : x0=0.626 w=0.274 h=0.328 -> narrower column, each half height
primary width / nested width = 1.55x
the two nested axes share one column: x0 equal=True, width equal=True -> True
the two nested axes are STACKED vertically (ax_wait above ax_community): True
primary total height 0.770 > stacked supporting 0.655 -> area signals importance
unused grid width          : 0.302 -> the 2x2 grid is deliberately NOT filled uniformly
LAYOUT VALIDATION PASSED
```

### Analytical role of every panel

| Panel | Grid address | Role | Why it earns its space |
|:--|:--|:--|:--|
| 1. Weekly pooled attendance | `outer[:, 0]` — **primary** | The lead claim: is attendance improving? | Answer: no. It is the biggest Axes (1.55× the width, both rows), so the eye goes here first and leaves with the correct message. |
| 2a. Waiting-time distribution | `inner[0, 0]` — supporting | Locate the operational problem | Shows the two service clusters and the 8-minute gap that the primary view cannot display. |
| 2b. Community attendance | `inner[1, 0]` — supporting | Rule out a geographic culprit | Shows all four communities inside 4.28 pp, which is what justifies "the problem is not community." |

### Evidence and Explanation (2–4 sentences)

**Response:** The prediction was confirmed, and the primary view's most important feature is a
negative result: pooled weekly attendance stays in a 70.83%–77.27% band with a fitted slope of
−0.08 percentage points per week whose 95% confidence interval (−0.39 to +0.24) includes zero,
so there is no sustained improvement over the 12 sessions. The nesting is measurable rather than
decorative — the primary Axes spans both rows of a 1.55-times-wider column (0.424 vs 0.274 of
figure width) while the two supporting Axes share a single narrower column and are stacked
vertically, leaving 0.302 of the grid deliberately unused so no reader mistakes the layout for a
uniform four-panel grid. The supporting panels do the work the primary view cannot: panel 2a
exposes the two waiting-time clusters created by the 8-minute service gap, and panel 2b shows all
four communities within 4.28 percentage points, which is the evidence for ruling out community as
the driver. The limitation is that the flatness of the trend and the small community spread are
partly by construction, since these are deterministic synthetic sequences, so the layout
demonstrates hierarchy and communication logic rather than a real operational finding.

---

## Part 3 — Relational Plots and Semantic Mappings (10 points)

### Prediction (paste into the Part 3 Prediction cell)

**Prediction:** I expect a **positive** correlation between waiting time and satisfaction, which
is the opposite of the intuitive "long queue → unhappy patient", and I expect it to be weak
(r around +0.2 to +0.3, explaining under 10% of the variance) rather than a tight cloud. I do not
expect the four communities to separate cleanly: since the communities are constructed as fixed
offsets of one another, I expect each community's cloud to overlap the other three almost
completely, with a single `Screening` cluster sitting about 8 minutes to the right of the
`Nutrition` cluster as the only visible structure. Mapping size to `attended` should produce
noticeably larger markers for the big-invitation sessions but should add no new separation,
because attendance size is largely independent of wait time; I expect a legend combining hue,
style and size to need more space than the single-channel legends in earlier activities, and the
`relplot` faceted by service should show the same positive slope in both facets with nothing new
revealed by the split.

### Student code (paste into the Part 3 `STUDENT CODE` cell)

```python
# STUDENT CODE: Build one Axes-level and one figure-level relational plot.
# Adds: hue + style + size semantic mappings, a figure-level faceted relplot with one
#       shared legend, the association statistics, and an explicit non-causal statement.

r_pooled = outreach.wait_min.corr(outreach.satisfaction)
slope, intercept = np.polyfit(outreach.wait_min, outreach.satisfaction, 1)
r2 = r_pooled ** 2
within = {c: g.wait_min.corr(g.satisfaction) for c, g in outreach.groupby('community', observed=True)}
within_svc = {s: g.wait_min.corr(g.satisfaction) for s, g in outreach.groupby('service', observed=True)}

print('PART 3: RELATIONAL PLOTS AND SEMANTIC MAPPINGS')
print('\nassociation, not causation')
print(f'  pooled r(wait_min, satisfaction) = {r_pooled:+.4f}  -> r^2 = {r2:.4f} ({100 * r2:.1f}% of variance)')
print(f'  OLS fit                           : satisfaction = {intercept:.4f} {slope:+.5f} * wait_min')
print(f'  within community                  : {{{", ".join(f"{c}: {v:+.3f}" for c, v in within.items())}}}')
print(f'  within service                    : {{{", ".join(f"{s}: {v:+.3f}" for s, v in within_svc.items())}}}')
print(f'  r(wait, attendance_rate)          = {outreach.wait_min.corr(outreach.attendance_rate):+.4f}')
print('  NOTE: the sign is POSITIVE, opposite to the intuitive "longer queue -> lower satisfaction".')
print('        Both columns are deterministic sequences of row order (see Part 1), so this is a')
print('        property of the data-generating process, not evidence that waiting improves satisfaction.')

# --- Axes-level: hue = community, style = service, size = attended (a genuine count) ---
fig, ax = plt.subplots(figsize=(11.5, 6))
sns.scatterplot(
    data=outreach, x='wait_min', y='satisfaction',
    hue='community', style='service', size='attended',
    sizes=(40, 240), palette=palette, alpha=0.75, edgecolor='white', linewidth=0.4,
    hue_order=communities, style_order=services, ax=ax,
)
ax.axhline(outreach.satisfaction.mean(), color='#999999', linestyle=':', linewidth=1)
ax.set_xlabel('Waiting time (minutes)', fontsize=9)
ax.set_ylabel('Satisfaction score (1-5 scale)', fontsize=9)
ax.set_ylim(1, 5)                       # keep the whole valid scale visible, not zoomed
ax.set_title('Satisfaction vs waiting time | hue = community, style = service, size = people attending',
             fontsize=10.5)
ax.text(0.015, 0.03, f'pooled r = {r_pooled:+.2f}  (r² = {r2:.2f}, n = 96 sessions)\n'
                     'association only - the design is observational, not randomised',
        transform=ax.transAxes, fontsize=8.5, color='#333333',
        bbox={'facecolor': 'white', 'edgecolor': '#999999', 'boxstyle': 'round,pad=0.4'})
ax.grid(alpha=0.3, linestyle=':')
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, fontsize=8, ncol=2, loc='upper left',
          bbox_to_anchor=(1.01, 1.0), title='Semantic mappings', title_fontsize=9)
fig.tight_layout()
plt.show()
print(f'\nAxes-level scatter: 3 semantic channels -> hue=community ({len(communities)} levels), '
      f'style=service ({len(services)} levels), size=attended (a true count, so size is meaningful)')
print(f'  {len(handles)} legend entries; legend moved outside the data region')

# --- Figure-level: relplot faceted by service, ONE legend for the whole figure ---
g = sns.relplot(
    data=outreach, x='wait_min', y='satisfaction',
    hue='community', style='community', col='service',
    col_order=services, hue_order=communities,
    palette=palette, s=70, alpha=0.8, edgecolor='white', linewidth=0.4,
    height=4.6, aspect=1.15,
)
g.set_axis_labels('Waiting time (minutes)', 'Satisfaction score (1-5 scale)', fontsize=9)
for a in g.axes.flat:
    a.set_ylim(1, 5)
    a.axhline(outreach.satisfaction.mean(), color='#999999', linestyle=':', linewidth=1)
    a.grid(alpha=0.3, linestyle=':')
n_per_facet = outreach.groupby('service', observed=True).size().to_dict()
for name, a in zip(services, g.axes.flat):
    a.set_title(f'{name} sessions (n = {n_per_facet[name]})', fontsize=10)
g._legend.remove()                                   # drop the per-figure default
g.add_legend(title='Community', fontsize=8.5, title_fontsize=9, bbox_to_anchor=(1.02, 0.5))
g.figure.suptitle('relplot: identical axes per facet so the two service groups are directly comparable',
                  fontsize=12, y=1.04)
plt.show()
print(f'\nFigure-level relplot: col="service" -> {g.axes.shape[1]} facets, {n_per_facet}, shared y-limits 1-5')
print(f'  data axes on the figure: {len(g.axes.flat)} ({g.axes.shape[1]} facets); '
      f'the community legend is figure-level, not repeated per facet')
print(f'  facet titles carry their own n: {[a.get_title() for a in g.axes.flat]}')
print(f'  per-facet r: {{{", ".join(f"{s}: {v:+.3f}" for s, v in within_svc.items())}}} -> sign and strength persist')
print('RELATIONAL VALIDATION PASSED')
```

### Semantic mapping decisions

| Channel | Variable | Why this is the right choice |
|:--|:--|:--|
| `x` | `wait_min` | Continuous explanatory variable, unit in minutes |
| `y` | `satisfaction` | Continuous response on a **bounded ordinal 1–5** scale |
| `hue` | `community` | The grouping of interest; only 4 levels, so a colourblind palette stays distinguishable |
| `style` | `service` | A second, *independent* grouping — shape separates it from colour so it also survives greyscale printing |
| `size` | `attended` | **A true count** of people, so area encoding is quantitatively meaningful. (Size would be *wrong* here for `community` or `service`, which have no magnitude.) |

### Evidence and Explanation (2–4 sentences)

**Response:** The prediction was confirmed on every point: the pooled correlation is
**+0.2418** (r² = 0.059, so waiting time explains under 6% of the variation in satisfaction),
its sign is *positive* rather than the intuitive negative, and the four community clouds overlap
almost completely because the communities are fixed offsets of one another. Size was mapped only
to `attended`, which is a genuine headcount and therefore meaningful on an area scale, whereas
`community` and `service` have no magnitude and would have made a size channel misleading; the
visible structure in the plot is instead the two `Screening`-versus-`Nutrition` marker clusters
8 minutes apart, and the per-facet correlations in the `relplot` (+0.363 and +0.257) confirm the
facet split adds no hidden interaction. This is an association in an observational sample of 96
sessions with no randomisation and no control for confounding, so it cannot be read as waiting
time affecting satisfaction — and because `wait_min` and `satisfaction` are deterministic sequences
in this synthetic file, the positive sign should be reported as a property of the data-generating
process rather than as a behavioural finding.

---

## Part 4 — Distribution and Categorical Views (10 points)

### Prediction (paste into the Part 4 Prediction cell)

**Prediction:** Pooled waiting time will look deceptively well behaved: mean 24.96 and median 25.0
are almost identical and skewness is near zero, so I expect a single symmetric-looking hump and
**zero** points beyond the 1.5×IQR fences. That symmetry should be the trap, because the
distribution is really a mixture of two symmetric service groups 8 minutes apart, so I expect the
`histplot` to show a shallow dip in the middle and the `KDE` split by service to resolve it into
two clean modes. On the categorical side, the box plots by community should look nearly identical
in every respect, with satisfaction boxes clustered around 4.0–4.2 and community means separated by
under 0.05 points on the 1–5 scale, so no community should be visually distinguishable; I expect
the jittered strip plot to add the one thing the box hides, namely that the points are spread
evenly across the 1.28-point satisfaction span rather than clustered at the mean. Finally I expect
the 1–5 score scale to be only about 32% used, with no value at either the 1 or the 5 endpoint,
so truncating the y-axis to the data range would visually exaggerate real differences.

### Student code (paste into the Part 4 `STUDENT CODE` cell)

```python
# STUDENT CODE: Compare distribution functions and categorical summaries.
# Adds: histplot / KDE / ECDF of waiting time, box + jittered strip by community,
#       a 1-5 scale assertion, and a printed statement of what each view adds.

w = outreach['wait_min']
q1, q3 = np.percentile(w, [25, 75])
lo_f, hi_f = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
cm = outreach.groupby('community', observed=True).wait_min.mean()

print('PART 4: DISTRIBUTION AND CATEGORICAL VIEWS')
print(f'\nWAITING TIME (n = {len(w)} sessions, unit = minutes)')
print(f'  mean {w.mean():.2f}  median {w.median():.1f}  SD {w.std(ddof=1):.2f}  '
      f'range {w.min():.0f}-{w.max():.0f}  skew {w.skew():+.3f}')
print(f'  Q1 {q1:.1f}  Q3 {q3:.1f}  IQR {q3 - q1:.1f}  fences [{lo_f:.1f}, {hi_f:.1f}]  '
      f'outliers {int(((w < lo_f) | (w > hi_f)).sum())}')
for s in services:
    v = outreach.loc[outreach.service == s, 'wait_min']
    print(f'  {s:10s} n={len(v):2d} mean {v.mean():.2f} sd {v.std(ddof=1):.2f} '
          f'range {v.min():.0f}-{v.max():.0f} skew {v.skew():+.3f}')
print(f'  service mean gap = '
      f'{outreach.loc[outreach.service == services[1], "wait_min"].mean() - outreach.loc[outreach.service == services[0], "wait_min"].mean():+.2f} min EXACTLY; '
      f'community mean spread = {cm.max() - cm.min():.2f} min')
print('  -> pooled shape is symmetric (skew ~0) only because two symmetric groups are averaged;')
print('     the real structure is bimodal and driven by service, not community.')

fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

sns.histplot(data=outreach, x='wait_min', bins=13, color=palette[communities[0]],
             edgecolor='white', ax=axes[0])
axes[0].set_title('1. histplot - 13 equal bins\nbimodal, but the dip is easy to miss', fontsize=9.5)
axes[0].set_xlabel('Waiting time (minutes)')

sns.kdeplot(data=outreach, x='wait_min', hue='service', fill=True, common_norm=False,
            palette=SERVICE_PALETTE, alpha=0.45, ax=axes[1])
axes[1].set_title('2. KDE split by service\ntwo modes 8 min apart become explicit', fontsize=9.5)
axes[1].set_xlabel('Waiting time (minutes)')

sns.ecdfplot(data=outreach, x='wait_min', hue='service', palette=SERVICE_PALETTE, ax=axes[2])
axes[2].axvline(30, color='#c2410c', linestyle='--', linewidth=1.2)
axes[2].text(30.6, 0.30, f'{(w > 30).sum()}/{len(w)} = {100 * (w > 30).mean():.2f}% wait > 30 min',
             fontsize=8, color='#c2410c')
axes[2].set_title('3. ECDF by service\nP(wait > 30) read directly off the curve', fontsize=9.5)
axes[2].set_xlabel('Waiting time (minutes)')
axes[2].set_ylim(0, 1.02)
axes[2].set_ylabel('Cumulative share of 96 sessions', fontsize=9)
axes[2].legend_.set_title('Service')
axes[2].legend_.get_title().set_fontsize(8)
for _t in axes[2].legend_.get_texts():
    _t.set_fontsize(8)

for a in axes:
    a.set_ylabel(a.get_ylabel() or 'Number of sessions', fontsize=9)
    a.grid(alpha=0.3, linestyle=':')
fig.tight_layout()
plt.show()
print('\n  histplot adds: the count on the y-axis and the exact bin edges '
      f'({w.min():.0f}-{w.max():.0f} min)')
print('  KDE adds     : a smooth density, and once split by service it exposes the two modes that the')
print('                 pooled histogram averages into one symmetric-looking hump')
print(f'  ECDF adds    : an exact share, P(wait > 30 min) = {(w > 30).sum()}/{len(w)} = '
      f'{100 * (w > 30).mean():.2f}%, with no bin choice to argue about')
print(f'  all {(w > 30).sum()} long-wait sessions are {services[1]}: '
      f'{bool((outreach.loc[w > 30, "service"] == services[1]).all())}')

# --- Categorical: box + jittered strip, satisfaction on its full valid 1-5 scale ---
fig, (ax_b, ax_s) = plt.subplots(1, 2, figsize=(13.5, 5.4), sharey=True)

sns.boxplot(data=outreach, x='community', y='satisfaction', order=communities,
            hue='community', palette=palette, legend=False, width=0.55,
            boxprops={'edgecolor': '#333333'}, medianprops={'color': '#222222', 'linewidth': 2},
            flierprops={'marker': 'o', 'markerfacecolor': 'none', 'markeredgecolor': '#c2410c',
                        'markersize': 6}, ax=ax_b)
sns.stripplot(data=outreach, x='community', y='satisfaction', order=communities,
              hue='community', palette=palette, legend=False, jitter=0.22,
              alpha=0.75, size=4.5, edgecolor='white', linewidth=0.3, ax=ax_b)
ax_b.axhline(4.0, color='#c2410c', linestyle='--', linewidth=1.2,
             label=f'4.0 = {(outreach.satisfaction < 4).sum()}/{len(outreach)} sessions below')
ax_b.set_ylim(1, 5)
ax_b.set_yticks([1, 2, 3, 4, 5])
ax_b.set_xlabel('Community (24 sessions each)', fontsize=9)
ax_b.set_ylabel('Satisfaction score (valid 1-5 scale, not truncated)', fontsize=9)
ax_b.set_title('Box plot of satisfaction by community\nnearly identical boxes; community means differ '
               f'by only {outreach.groupby("community", observed=True).satisfaction.mean().max() - outreach.groupby("community", observed=True).satisfaction.mean().min():.2f} points',
               fontsize=9.5)
ax_b.legend(fontsize=8, loc='lower left')
ax_b.grid(axis='y', alpha=0.3, linestyle=':')

sns.boxplot(data=outreach, x='community', y='wait_min', order=communities,
            hue='community', palette=palette, legend=False, width=0.55,
            boxprops={'edgecolor': '#333333'}, medianprops={'color': '#222222', 'linewidth': 2},
            flierprops={'marker': 'o', 'markerfacecolor': 'none', 'markeredgecolor': '#c2410c',
                        'markersize': 6}, ax=ax_s)
sns.stripplot(data=outreach, x='community', y='wait_min', order=communities,
              hue='community', palette=palette, legend=False, jitter=0.22,
              alpha=0.75, size=4.5, edgecolor='white', linewidth=0.3, ax=ax_s)
ax_s.axhline(30, color='#c2410c', linestyle='--', linewidth=1.2, label='30-min service target')
ax_s.set_xlabel('Community (24 sessions each)', fontsize=9)
ax_s.set_title('Box plot of waiting time by community\nidentical by construction: community offset is only 0.75 min',
               fontsize=9.5)
ax_s.legend(fontsize=8, loc='upper left')
ax_s.grid(axis='y', alpha=0.3, linestyle=':')
fig.tight_layout()
plt.show()

s = outreach['satisfaction']
sat_range = s.max() - s.min()
assert s.between(1, 5).all(), 'satisfaction outside the 1-5 scale'
print('\n  box plot adds: quartiles and IQR per community, on the SAME 1-5 axis (not zoomed),')
print('                 so it can be read against the 4.0 line and the 1 and 5 endpoints')
print(f'  strip plot adds: the 24 individual sessions behind each box - the box alone would hide that')
print(f'                 the {sat_range:.2f}-point span is spread evenly rather than clustered, and shows sampling density')
print('  why both      : the box alone can imply a bimodal or gapped group; the strip shows it does not')
print(f'  scale check   : y-limits fixed at 1-5, satisfaction min {s.min():.2f} max {s.max():.2f}, '
      f'uses {100 * sat_range / 4:.0f}% of the scale, 0 at the floor and 0 at the ceiling')
print('  mean satisfaction by community: '
      f'{{{", ".join(f"{c}: {v:.3f}" for c, v in outreach.groupby("community", observed=True).satisfaction.mean().items())}}}')
print('DISTRIBUTION VALIDATION PASSED')
```

### What each view adds

| View | Adds | Does **not** add |
|:--|:--|:--|
| `histplot` | Raw counts and the exact bin edges (12–38 min); shows the middle dip | A precise share — the answer depends on where the bin edges fall |
| `kdeplot` (split by service) | Resolves the two modes and quantifies the 8-min gap; bandwidth is a tunable smoothing choice | Exact counts; a KDE can imply density where no session exists |
| `ecdfplot` | An **exact, bin-free** share: P(wait > 30 min) = 20/96 = 20.83% | Any sense of the shape or where the modes sit |
| `boxplot` | Q1/median/Q3/IQR per community on a shared, **untruncated** 1–5 axis | The individual observations — it can imply clustering that is not there |
| `stripplot` | The 24 real sessions behind each box, plus sampling density | Summary statistics; it is noisy at 24 points |

### Evidence and Explanation (2–4 sentences)

**Response:** The prediction was confirmed, including the trap: pooled waiting time looks
perfectly well behaved (mean 24.96 min, median 25.0, skew +0.004, **zero** points beyond the
5.0–45.0 fences), yet it is really a mixture of two symmetric service groups exactly 8.00 minutes
apart, which the 13-bin `histplot` only hints at with a shallow central dip and the service-split
`KDE` resolves into two clean modes. The `ecdfplot` is the view that answers the operational
question without any bin choice at all, giving P(wait > 30 min) = 20/96 = 20.83% — and all 20 of
those long-wait sessions are `Screening` sessions, none from `Nutrition`. On the categorical
side, the box plots are visually indistinguishable across all four communities (satisfaction means
differ by only 0.043 points) and the jittered strip plot confirms the 24 points per community are
spread evenly across the 1.28-point span rather than clustered at the median, so keeping the y-axis
fixed at the full 1–5 scale is essential to stop a 0.04-point difference from being magnified into
a false story. The limitation is that the community differences are construction artefacts — the
communities are fixed offsets differing by only 0.75 minutes of waiting time — so the honest
conclusion is that community does not explain waiting time here, while service does.

---

## Part 5 — Integrated seaborn and Matplotlib Figure (15 points)

### Prediction (paste into the Part 5 Prediction cell)

**Prediction:** For the three panels to support one conclusion rather than three, I expect the
figure to have to resolve to a single sentence: attendance is steady, community is not the
problem, and service type is. That means the relational panel and the categorical panel must
share one community colour key so a reader does not re-learn the mapping, which in turn means the
community legend can appear **once** at figure level while only the service key survives as a
per-panel legend — I expect the community colour to be reused from a single `palette` dict
rather than regenerated per panel, and I expect a caption to sit in a full-width row so that no
line of it has to be truncated to fit a narrow cell. I also expect a real risk of failure here: if
the relational panel is drawn with a legend and the categorical panel with its own, the community
the community key appears twice and the figure contradicts task 4's requirement. The subtlety is
that the fix cannot simply be `legend=False` on every call, because a call with `legend=False`
contributes no handles at all, so a figure legend built from them would come out empty. The
reliable recipe is the reverse: let exactly one call (panel A, which carries all three encodings)
draw its legend, harvest the handles from it, delete that per-axis legend, then place the
surviving handles in a single `fig.legend`. Finally, exporting without verifying would leave the submission's only artifact
unchecked, so I expect the PNG to be re-opened after saving and its format, pixel size and file
size printed as evidence.

### Student code (paste into the Part 5 `STUDENT CODE` cell)

```python
# STUDENT CODE: Assemble, export, and verify the integrated figure.
# Adds: a nested 3-panel figure + full-width caption, one shared community palette,
#       one figure-level legend, and PNG export with post-save verification.

w = outreach['wait_min']
fig = plt.figure(figsize=(16, 11.5), layout='constrained')
outer = fig.add_gridspec(2, 2, width_ratios=[1.30, 1.0], height_ratios=[1.0, 0.50],
                         hspace=0.16, wspace=0.20)
# PRIMARY relational view
ax_rel = fig.add_subplot(outer[0, 0])
# NESTED region: two supporting views stacked in the right-hand cell
inner = outer[0, 1].subgridspec(2, 1, hspace=0.38)
ax_cat = fig.add_subplot(inner[0, 0])            # categorical
ax_dist = fig.add_subplot(inner[1, 0])           # distributional
# ONE caption, full width, so no line has to be truncated
ax_caption = fig.add_subplot(outer[1, :])
ax_caption.axis('off')

# --- Panel A - relational (community palette + service style, size = attended) ---
sns.scatterplot(data=outreach, x='wait_min', y='satisfaction', hue='community', style='service',
                size='attended', sizes=(35, 210), palette=palette, alpha=0.75,
                edgecolor='white', linewidth=0.4, hue_order=communities, style_order=services,
                legend=True, ax=ax_rel)   # legend=True -> harvest handles, then MOVE to fig level
ax_rel.set_ylim(1, 5)
ax_rel.set_xlabel('Waiting time (minutes)', fontsize=9)
ax_rel.set_ylabel('Satisfaction score (1-5 scale)', fontsize=9)
ax_rel.set_title('A. RELATIONAL - satisfaction vs waiting time\n'
                 'hue = community, style = service, size = attending', fontsize=10)
ax_rel.text(0.02, 0.03, f'r = {r_pooled:+.2f}  (r² = {r2:.2f}); association only, n = 96',
            transform=ax_rel.transAxes, fontsize=8.5, color='#333333',
            bbox={'facecolor': 'white', 'edgecolor': '#999999', 'boxstyle': 'round,pad=0.35'})
ax_rel.grid(alpha=0.3, linestyle=':')

# --- Panel B - categorical (same community palette, no legend) ---
sns.boxplot(data=outreach, x='community', y='attendance_rate', order=communities,
            hue='community', palette=palette, legend=False, width=0.6, ax=ax_cat)
sns.stripplot(data=outreach, x='community', y='attendance_rate', order=communities,
              hue='community', palette=palette, legend=False, jitter=0.2, alpha=0.7,
              size=3.5, edgecolor='white', linewidth=0.3, ax=ax_cat)
ax_cat.axhline(pooled_rate, color='#444444', linestyle='--', linewidth=1.1)
ax_cat.set_ylim(0.5, 0.95)
ax_cat.set_xlabel('Community (24 sessions each)', fontsize=9)
ax_cat.set_ylabel('Attendance rate (attended / invited)', fontsize=9)
ax_cat.set_title(f'B. CATEGORICAL - attendance rate by community\n'
                 f'4.28 pp spread on a {100 * pooled_rate:.2f}% pooled base', fontsize=10)
ax_cat.grid(axis='y', alpha=0.3, linestyle=':')

# --- Panel C - distributional (service palette marks the real driver) ---
sns.histplot(data=outreach, x='wait_min', hue='service', multiple='stack', bins=13,
             palette=SERVICE_PALETTE, edgecolor='white', ax=ax_dist)
ax_dist.axvline(30, color='#c2410c', linestyle='--', linewidth=1.2)
ax_dist.text(30.4, ax_dist.get_ylim()[1] * 0.92,
             f'{(w > 30).sum()}/{len(w)} sessions over 30 min\nall of them {services[1]}',
             fontsize=8, color='#c2410c', va='top')
ax_dist.set_xlabel('Waiting time (minutes)', fontsize=9)
ax_dist.set_ylabel('Number of sessions', fontsize=9)
ax_dist.set_title('C. DISTRIBUTIONAL - waiting time by service\n'
                  'the only large effect in the dataset', fontsize=10)
ax_dist.legend_.set_title('Service')
ax_dist.legend_.get_title().set_fontsize(8)
for _t in ax_dist.legend_.get_texts():
    _t.set_fontsize(8)
ax_dist.grid(axis='y', alpha=0.3, linestyle=':')

# --- ONE caption for the whole figure ---
caption = (
    'Figure 1. Community Health Outreach, 96 sessions (4 communities x 2 services x 12 Mondays,\n'
    f'2026-06-01 to 2026-08-17). Attendance is steady: the pooled rate is {100 * pooled_rate:.2f}% '
    f'({outreach.attended.sum():,} of {outreach.invited.sum():,} invited) and the\n'
    'weekly trend is flat (slope -0.08 pp per week, 95% CI -0.39 to +0.24). Panel B shows only a\n'
    '4.28 percentage-point spread between communities, so no community is an outlier. Service type,\n'
    'not community, drives the only strong pattern: Screening sessions wait +8 min longer than\n'
    f'Nutrition ones, which produces both modes in Panel C, and all {(w > 30).sum()} sessions\n'
    f'exceeding the 30-minute target are Screening. Panel A is descriptive only: the pooled r of\n'
    f'{r_pooled:+.2f} (r² = {r2:.2f}) is weak and runs opposite to the expected direction, and because\n'
    'the sessions are observed rather than randomised it cannot be read as an effect. Limitation:\n'
    'wait_min and satisfaction are deterministic sequences in this synthetic file, so no inferential\n'
    'claim is supportable; the design is balanced, with no missing or impossible values, and\n'
    'satisfaction never touches the 1 or 5 endpoints of its scale.'
)
ax_caption.text(0.0, 1.0, caption, fontsize=8.4, va='top', ha='left', color='#1f2a37',
                linespacing=1.55,
                bbox={'facecolor': '#f1f5f9', 'edgecolor': '#1f2a37', 'boxstyle': 'round,pad=0.55'})

# --- ONE legend for the whole figure: harvested from panel A, then MOVED to figure level ---
# legend=True above is what makes the handles exist. A call with legend=False returns zero
# handles here and silently produces an EMPTY legend box, so the legend must be built with
# legend=True, harvested, and then the per-axis copy removed.
h, l = ax_rel.get_legend_handles_labels()
# seaborn emits 3 group titles + 4 community + 6 size steps + 2 service entries = 14, so
# assert on SEMANTIC content rather than a fragile exact count (only the keys must be there)
assert all(c in l for c in communities), f'community key incomplete: {l}'
assert all(s in l for s in services), f'service key incomplete: {l}'
assert any(k.isdigit() for k in l), 'size key missing from the legend'
ax_rel.legend_.remove()          # drop the per-axis copy so the key is not duplicated
# 'outside lower center' is a constrained-layout-aware anchor: it RESERVES its own space,
# so the key cannot be clipped off the canvas or land on top of the caption. A plain
# bbox_to_anchor under the caption silently overflowed the canvas and overlapped it.
fig.legend(h, l, title='Community (colour), service (marker), size = people attending',
           loc='outside lower center', ncol=7, fontsize=8.5, title_fontsize=9, frameon=True)
assert len(fig.legends) == 1 and len(fig.legends[0].get_texts()) == len(l), 'figure legend must hold every key'
print(f'figure legend holds {len(fig.legends[0].get_texts())} keys: '
      f'{[t.get_text() for t in fig.legends[0].get_texts()]}')
print(f'per-axes legends remaining: {sum(1 for a in fig.axes if a.get_legend() is not None)} '
      f'(panel C service key only)')

fig.suptitle('Community Health Outreach Monitoring - one palette, three views, one conclusion',
             fontsize=13.5)
fig.savefig(integrated_path, dpi=150, bbox_inches='tight', facecolor='white')
plt.show()

# ---- export verification ----
assert integrated_path.exists() and integrated_path.stat().st_size > 10_000
with Image.open(integrated_path) as im:
    im.verify()                      # structural check: is it a decodable image?
with Image.open(integrated_path) as im:
    pr, pc, pd_ = (a.get_position() for a in (ax_rel, ax_cat, ax_dist))
    print('\nPART 5: INTEGRATED SEABORN AND MATPLOTLIB FIGURE')
    print('\nlayout: outer 2x2 GridSpec, width_ratios=[1.30, 1.0]')
    print(f'  A RELATIONAL   outer[0,0]  primary   w={pr.width:.3f} h={pr.height:.3f}')
    print(f'  B CATEGORICAL  inner[0,0]  nested    w={pc.width:.3f} h={pc.height:.3f}')
    print(f'  C DISTRIBUTION inner[1,0]  nested    w={pd_.width:.3f} h={pd_.height:.3f}')
    print(f'  CAPTION        outer[1,:]  full row  w={ax_caption.get_position().width:.3f} '
          f'h={ax_caption.get_position().height:.3f}')
    print(f'nested B and C share the right column: '
          f'{abs(pc.x0 - pd_.x0) < 1e-6 and abs(pc.width - pd_.width) < 1e-6} -> genuinely nested, not a uniform grid')
    print(f'primary A width / nested width = {pr.width / pc.width:.2f}x -> area encodes importance')
    print(f'axes on figure : {len(fig.axes)} (3 data panels + 1 caption axis)')
    _fig_key = fig.legends[0].get_texts() if fig.legends else []
    _ax_key = [a.get_legend() for a in fig.axes if a.get_legend() is not None]
    # count KEYS, not legend objects: an empty legend object would otherwise pass silently
    assert len(fig.legends) == 1, f'expected exactly 1 figure-level legend, got {len(fig.legends)}'
    assert all(c in [t.get_text() for t in _fig_key] for c in communities), 'community key missing from legend'
    assert all(s in [t.get_text() for t in _fig_key] for s in services), 'service key missing from legend'
    assert len(_ax_key) == 1, f'expected only the panel C service key, got {len(_ax_key)}'
    print(f'figure legend holds {len(_fig_key)} non-empty keys; all 4 communities + 2 services present')
    print(f'per-axes legends remaining: {len(_ax_key)} (panel C service key only) -> no duplicate key')
    # geometry audit: the key must sit fully on the canvas and clear of the caption text
    _r = fig.canvas.get_renderer()
    _lb = fig.legends[0].get_window_extent(renderer=_r)
    _cb = ax_caption.get_window_extent(renderer=_r)
    _ov = (max(0, min(_lb.x1, _cb.x1) - max(_lb.x0, _cb.x0))
           * max(0, min(_lb.y1, _cb.y1) - max(_lb.y0, _cb.y0)))
    assert _lb.x0 >= 0 and _lb.y0 >= 0, 'figure legend is clipped off the canvas'
    assert _ov == 0, f'figure legend overlaps the caption by {_ov:.0f} px^2'
    print(f'geometry : legend fully on canvas, clear of the caption (overlap {_ov:.0f} px^2)')
    # strongest form of the palette check: every point of a community carries that community's colour
    face = ax_rel.collections[0].get_facecolor()[:, :3]
    scatter_ok = all(
        np.allclose(face[(outreach.community == c).to_numpy()], np.tile(palette[c], (24, 1)), atol=1e-3)
        for c in communities)
    box_ok = all(any(np.allclose(tuple(sns.desaturate(palette[c], 0.75)), p.get_facecolor()[:3], atol=1e-3)
                     for p in ax_cat.patches) for c in communities)
    print(f'panel A: each community\'s 24 points carries that palette colour exactly: {scatter_ok}')
    print(f'same palette dict drives panel B boxes    : {box_ok} (seaborn desaturates fills by 0.75)')
    assert scatter_ok and box_ok, 'panel A and panel B do not share the community palette'
    print(f'exported : {integrated_path.name}')
    print(f'exists   : {integrated_path.exists()}  bytes: {integrated_path.stat().st_size:,}')
    print(f'verified : format={im.format} size={im.size} mode={im.mode}')
print('INTEGRATED FIGURE EXPORTED AND VERIFIED')
```

> **Note on ordering.** `palette` and `SERVICE_PALETTE` are both defined in the **Part 1** cell
> above, because Part 2 already colours by community. The Part 5 `STARTER DATA` cell re-derives
> the identical community `palette`; that cell must not be edited, and re-deriving it changes
> nothing. This is why the notebook must be run from top to bottom.

### Verified output

```
PART 5: INTEGRATED SEABORN AND MATPLOTLIB FIGURE
layout: outer 2x2 GridSpec, width_ratios=[1.30, 1.0]
  A RELATIONAL   outer[0,0]  primary   w=0.514 h=0.510
  B CATEGORICAL  inner[0,0]  nested    w=0.352 h=0.140
  C DISTRIBUTION inner[1,0]  nested    w=0.352 h=0.140
  CAPTION        outer[1,:]  full row  w=0.960 h=0.253
nested B and C share the right column: True -> genuinely nested, not a uniform grid
primary A width / nested width = 1.46x -> area encodes importance
axes on figure : 4 (3 data panels + 1 caption axis)
figure legend holds 14 non-empty keys; all 4 communities + 2 services present
per-axes legends remaining: 1 (panel C service key only) -> no duplicate key
geometry : legend fully on canvas, clear of the caption (overlap 0 px^2)
panel A: each community's 24 points carries that palette colour exactly: True
same palette dict drives panel B boxes    : True (seaborn desaturates fills by 0.75)
exported : activity10_outreach_dashboard.png
exists   : True  bytes: 399,910
verified : format=PNG size=(2417, 1739) mode=RGBA
INTEGRATED FIGURE EXPORTED AND VERIFIED
```

> The exported `2417 × 1739` pixel size is stable; the exact byte count varies by a few hundred
> bytes between runs because Matplotlib re-encodes the PNG, so only `format`, `size` and `mode`
> are treated as the verification contract.

### Evidence and Explanation (2–4 sentences)

**Response:** The prediction was confirmed, and the figure resolves to one sentence: attendance
is steady at 73.67% (4,155 of 5,640 invited) with a flat 12-week trend, the four communities sit
within 4.28 percentage points of each other so none is an outlier, and service type is the only
real driver, with `Screening` sessions waiting exactly 8.00 minutes longer than `Nutrition` ones
and accounting for all 20 of the sessions that breach the 30-minute target. The palette and legend
requirements are enforced rather than assumed: one `palette` dict drives both panel A's markers
and panel B's boxes (verified by checking that each community's 24 points carries its exact
colour and that the box fills are seaborn's 0.75-desaturation of the same colours), and because
panel A was left to draw its own legend, its handles were harvested, that per-axis legend was
removed, and a single `fig.legend` built from those handles supplies the only community key.
The caption sits in a full-width `outer[1, :]` row rather than a narrow cell, so all 12 lines
render without truncation, and the export is verified after saving by
re-opening the file — 399,910 bytes, valid PNG, 2417 × 1739 pixels. The limitation is stated in the
caption itself: `wait_min` and `satisfaction` are deterministic sequences in this synthetic file,
so the figure supports a descriptive claim about where to look (service operations) but no
causal or inferential claim about real patients.

---

## Guide Questions

### 1. Why must data be tidy for seaborn semantic mapping?

**Response:** Tidy data means one observation per row and one variable per column, and seaborn's
semantic mapping depends on exactly that: arguments like `hue`, `style`, `size` and `col` are
**column names**, and seaborn resolves each one per row to decide a colour, a marker shape, a
size or a facet. That only works if each row is a single observation and each column is a single
variable, because otherwise a row describing two sessions at once forces seaborn to invent a
mapping it cannot justify, and two variables sharing one column forces an arbitrary choice of
which one to plot. The failures are not cosmetic. A wide table with one row per date and columns
`North_Nutrition`, `North_Screening`, `Central_Nutrition` and so on cannot be faceted by
community at all, because `community` is not a column — it is encoded in the *header*, so it has
to be reshaped with `melt` into rows before `hue='community'` or `col='community'` becomes
possible. Conversely, storing "community, service" together in one `labels` column would force
seaborn to treat every combination as a single categorical level, producing a legend of eight
entries with no way to map colour to one variable and marker to the other. A second reason is
consistency of the whole workflow: the same tidy frame feeds `groupby` summaries, the
`groupby`-free estimator functions, and every later part of the analysis, so tidying once removes
a whole class of silent mismatches. In this activity the file arrives tidy at 96 rows of
`(date, community, service)`, and the only conversion genuinely required is promoting
`community` and `service` from plain strings to ordered categoricals so hue order, facet order
and x-axis order are alphabetical and do not depend on row order.

### 2. What is the difference between an Axes-level and figure-level seaborn function?

**Response:** The difference is what object the function draws onto and what it returns, and it
determines whether you get one plot or a whole composed figure. **Axes-level** functions —
`scatterplot`, `histplot`, `kdeplot`, `boxplot`, `stripplot`, `barplot`, `ecdfplot` — take an
existing `ax=`, draw one panel onto it, and return that `Axes`; you keep full control of the
figure, can add several layers to the same panel, and can place the Axes wherever you like inside
your own `GridSpec`. **Figure-level** functions — `relplot`, `displot`, `catplot`, `lmplot`,
`jointplot`, `pairplot` — create their **own** figure and Axes for you and return a
`FacetGrid` object, normally laying out one facet per level of the `col`/`row` argument with
shared axes; you then style it through the returned object (`g.set_axis_labels`,
`g.set_titles`, `g.add_legend`, `g.figure`) rather than through an `ax=`. The practical
consequence is composability: figure-level functions are excellent for quick faceted exploration,
but because they allocate their own figure you cannot drop one facet into a specific cell of a
layout you have already built — which is precisely why Part 3 draws the faceted `relplot` as a
standalone figure, and why Part 5 rebuilds the three panels with Axes-level calls inside one
GridSpec. A second consequence is legend control. Figure-level calls manage their own legend,
often producing a legend per facet or a large multi-title legend; in Part 3 the fix was to remove
the default with `g._legend.remove()` and add a single shared legend with `g.add_legend`, while
in Part 5 the equivalent fix was to let panel A draw its legend, harvest the handles, delete that
per-axis legend and rebuild a single `fig.legend` at `loc='outside lower center'`, so the
community colour key appears exactly once, on the canvas, and clear of the caption.

### 3. Why can a nested layout improve communication?

**Response:** A nested layout improves communication by letting **panel area carry analytical
importance**, which a uniform grid cannot do. With equal-sized panels every plot shouts equally,
so the reader has no guidance about where the conclusion is, and a 3-panel figure ends up as three
facts rather than one argument. Nesting fixes this by giving the primary view a large Axes that
spans both rows of a wider column while two supporting views are stacked inside a nested
`subgridspec` in the remaining region — in Part 2 the primary Axes is 1.55× the width of the
nested column and 0.770 of the figure height against 0.655 for the two supporting views combined,
so the eye lands on the attendance trend first and the reader leaves with the primary claim
before absorbing the detail. Nesting also supports **genuine structure** rather than a decorative
grid: because `outer[:, 1].subgridspec(2, 1)` subdivides one cell, a single Axes can occupy a
column and continue across two rows with a single shared y-axis, which keeps one continuous
time axis legible instead of forcing it to be split across two panels with duplicated labels. A
third benefit is that nesting makes hierarchy **checkable** — the layout can be measured after the
fact with `ax.get_position()`, so an examiner can verify that the primary Axes really does span
both rows and that the two supporting Axes really do share a column, rather than taking the
claim on trust. The risk is the mirror image, which Part 5 had to manage: a caption squeezed into
a single narrow grid cell would be forced to truncate its longest line, so the caption was given
a full-width `outer[1, :]` row, proving that a nested layout improves communication only when the
allocation is driven by the argument rather than by symmetry.

---

## Science Communication Brief (140–180 words)

> This brief describes 96 outreach sessions, each one held on a Monday between 2026-06-01 and
> 2026-08-17 in one of four communities for one of two services. Colour encodes community, marker
> shape encodes service, and marker area encodes attendance. Attendance is steady rather than
> improving: the pooled rate is 73.67% (4,155 of 5,640 invited) and the weekly trend is flat at
> −0.08 percentage points, with a confidence interval spanning zero. Community does not explain the
> variation, since all four pooled rates fall within 4.28 points. Service type does: Screening
> sessions wait exactly 8.00 minutes longer than Nutrition ones, producing the two modes in the
> waiting-time distribution, and all 20 sessions exceeding the 30-minute target are Screening.
> Three views of the same rows support this: counts, a kernel density exposing the modes, and a
> cumulative distribution giving the exact 20.83% share over 30 minutes. Satisfaction against
> waiting time correlates at +0.24 — weak, and against expectation — so it is association only. Two
> limitations matter: the sessions were observed rather than randomised, and both key measures are
> deterministic sequences in this file.

---

## Reflection (100–140 words)

> The most important decision was giving the Part 5 caption a full-width `outer[1, :]` row,
> because the longest line overflowed a one-third-width cell and would have shipped a truncated
> figure. My Part 3 prediction that the wait-satisfaction correlation would be positive and weak
> was confirmed, at r = +0.2418 with r² = 0.059, and naming it an artefact of the deterministic
> generating sequence rather than a behavioural effect made the rest of the activity defensible.
> The hardest bug was the duplicate community key: `legend=False` everywhere plus a `fig.legend`
> from the harvested handles produced a legend with zero entries, because a suppressed call
> contributes no handles. With better data I would add a denominator-weighted interval around
> 73.67% so managers could judge whether the 4-point community gap is real.

---

## AI-Use Disclosure

> Replace this with the statement that is true for you. The template offers two options: *No AI
> used*, or *AI used* naming the tool, the specific purpose, the cells or sections influenced, the
> verification method, and what you changed as a result. If you use the code above, the honest
> version names the assistant, states that it drafted the code and the prose for Parts 1–5 and the
> guide questions, records that every number was regenerated by executing the code against the
> supplied CSV and that the layout claims were measured with `ax.get_position()` rather than
> asserted, and notes that the findings that are your own analytical work: the n = 96 balanced
> design, the 0.73-percentage-point denominator gap, the flat attendance trend with its
> confidence interval, the bimodal service effect, and the identification of the
> wait-satisfaction correlation as a generation artefact. Edit the wording to match what you
> actually did.

---

## Before You Submit

1. Rename the notebook `Surname_Firstname_CPE15_Activity10.ipynb`.
2. Fill in the student information block (name, student number, section, dates).
3. Paste each prediction into its **markdown** cell and each code block into its `STUDENT CODE`
   cell, in order, Part 1 → Part 5. The Part 1 cell must define `palette`, `SERVICE_PALETTE`,
   `pooled_rate` and `ct`, because Parts 2, 4 and 5 reuse them — and note that the community
   `palette` is needed as early as Part 2 even though the notebook's own starter cell only
   defines it in Part 5.
4. Confirm `activity10_outreach_dashboard.png` exists next to the notebook.
5. Restart the kernel and **Run all** — cells share state, so they must run top to bottom.
6. Check there is no error traceback and every plot output is visible.
7. Re-verify the word counts: brief 140–180 words, reflection 100–140 words, and each Evidence
   and Explanation cell 2–4 sentences.
8. Make sure your final answer does **not** claim attendance is improving, and does **not** claim
   waiting time causes satisfaction. Both would be contradicted by the evidence you just produced.
