# AGENTS.md

## Repo shape and active work

- CPE15 (Programming for Data Science) coursework by term: `prelim/`, `midterm/`, `LAB/`, `sample/`, plus `finals/` (activities 11–15) and `final-project/`. Only `final-project/` is active; the rest is submitted history — read for style, don't "fix" it.
- Active deliverable: `final-project/Operation Blank Map - STUDENT PACKAGE/` (final exam, case CPE15-LUC-001). The shell starts there.
- No build system, manifest, tests, lint, CI, or `.gitignore` — don't invent them. `.ipynb_checkpoints/`, `.virtual_documents/`, `*.zip`, and `answers/test-1.ipynb` are untracked scratch, not deliverables.
- Revisiting midterm? Its docs are in `midterm/midterm-project/docs/` (requirements, checklist, plans). Its `.py` export is gone, so the old `python3 lucban_data_cleaning_3GF.py` verification command no longer applies.

## Sources of truth (final project)

- `STUDENT_CASEFILE.md` — exact scoring policy, three-file submission contract (`CPE15_ID_ANALYSIS.ipynb`, `CPE15_ID_DECISION.pdf`, `CPE15_ID_SUPPORTING.zip`), real-vs-simulated disclosure rules.
- `answers/EXAM_GUIDE.md` — work plan, defects D1–D7, §4 formula, §8 common mistakes, §9 checklist, reference numbers. Casefile/rubrics win if they conflict.
- `data/field_notes.txt` — only `VERIFIED` FN lines authorize a repair; `NOTE:` lines are interpretation rules. `data/GEOGRAPHIC_SOURCES.md` covers provenance.
- `CPE15_STUDENT_WORKBOOK.ipynb` is the blank template; `answers/CPE15_ANALYSIS.ipynb` is the prepared executed notebook that generated `answers/CPE15_PROCESSED.csv` and `answers/CPE15_FINAL_MAP.html`.

## Toolchain and execution

- System `python3` has pandas/numpy/matplotlib/seaborn but **no geopandas, folium, shapely, pyproj, jupyter, nbformat, nbconvert, or jupytext**. `.vscode/settings.json` selects conda env `CPE_15`, which is not on `PATH` here — the notebook cannot be executed headlessly in this shell. Inspect/edit it as JSON and don't claim a passing run.
- `CPE15_ANALYSIS.ipynb` locates `data/` via `Path.cwd()` then `../data`, and asserts the output dir is `answers/` or has `data/`: run it only from the package root or `answers/`. There is no script-based verification command.

## Data traps (full list: EXAM_GUIDE §4/§8)

- Six evidence files in `data/` are read-only (`answers/service_requests.sqlite` is an identical scratch copy); read CSVs with `dtype=str`. Repair only what the field bulletin authorizes and keep a correction log.
- Demand: `COUNT(DISTINCT request_id)` where status is `verified`/`open`, with the `A-03` alias normalized inside SQL. Missing data is not zero.
- Map geometry in EPSG:4326; distances from projected polygon centroids in EPSG:32651 (UTM 51N) to the nearest operational facility — straight-line, not road. Recompute the normalization denominator per scenario; zero denominator → 0; exact ties → ascending zone ID.
- Map and memo must disclose simulated teaching data and non-official catchments; exported HTML must open standalone.

## State and git

- Sealed update not yet applied: `CPE15_ANALYSIS.ipynb` cell 31 still has `UPDATE_SOURCE = "PENDING..."`; revised equals original. See EXAM_GUIDE §7 for current reference numbers.
- Git: `main` plus `feat/...` / `fix/...` branches merged back (see `git log --merges`); lowercase imperative commit messages. Don't commit unless asked.
