# AGENTS.md

## Repo shape

- CPE15 (Programming for Data Science) coursework, split by term: `prelim/`, `midterm/` (weekly `activity-N` folders plus the project), `LAB/`, `sample/`.
- No build system, package manifest, tests, lint, CI, or `.gitignore` exists. Do not invent them.
- Active work lives in `midterm/midterm-project/` (Lucban establishment field data cleaning). Everything else is submitted history — read it for style, don't "fix" it.

## Midterm project (where the work happens)

- `lucban_data_cleaning_3GF.ipynb` — the graded deliverable. Currently stops at the date-audit section.
- `lucban_data_cleaning_3GF.py` — jupytext hydrogen export of that notebook (cell markers `# %%`). It is **untracked in git**. All 54 non-empty code cells currently match the notebook; keep the two in sync when you edit either side.
- `csv/raw_dataset_1..10.csv` — raw SW Maps exports, 767 rows total. Never edit these; every transformation must be reproducible in the notebook.
- `docs/PROJECT_REQUIREMENTS.md` — instructor spec: schema (§5), approved categories (§6), acceptance gate (§11), submission layout (§13). Source of truth over any prose summary.
- `docs/CHECKLIST.md` — the actual work list (sections 0–13). Its checked/unchecked state reflects the notebook, not the plan. Work top-down; tick items only when verified.
- `docs/PLANS.md` — audit findings on the raw data and decisions D1–D10 (all still `_TBD_`). Where plans and code disagree, the checklist's **REVISED/NEW** notes are the correction.

## Commands

- Toolchain quirk: `jupyter`, `jupytext`, and `nbformat` are **not installed**; system `python3` has pandas 3.0.6, numpy 2.5.3, matplotlib, seaborn. VS Code points at a conda env `CPE_15` that is not on `PATH` in the shell, so `nbconvert`/kernel runs are not available here.
- Fastest verification (run from `midterm/midterm-project/`; paths are relative to it):

  ```
  python3 lucban_data_cleaning_3GF.py
  ```

  Runs the whole pipeline read-only; exit 0 with audit prints is the pass signal. Prefer editing and testing in the `.py`, then syncing cells back to the `.ipynb`.

## Pipeline rules that are easy to get wrong

- Load every CSV with `dtype=str` (the loader enforces it) — numeric parsing mangles phone numbers, leading zeros, and dates.
- Column order is spec-mandated: `date_collected` comes **before** `collector`; 16 required columns in the order listed in `PROJECT_REQUIREMENTS.md` §5.
- Never dedupe on `feature_id`: files 6 and 8 each numbered Barangay 4 from 001, so shared IDs are mostly *different* establishments. Dedup = normalized name + proximity, then reassign unique IDs and export an `old_id -> new_id` mapping.
- Dates: do not parse mixed strings with `dayfirst=True` — `10/03/2026` is month-first. Collection window is Sep 28–Oct 5, 2026; impute the 14 blanks from the SW Maps `Time` column (present on all 767 rows).
- Keep the SW Maps GPS columns (`Time`, `Horizontal Accuracy`, `HDOP`, `Satellites in Use`, `Fix ID`, `Averaged Count`) plus a `source_file` column — required for checklist §10 QA, not junk.
- The notebook still contains known gaps the checklist calls out (hard-coded fixes cover only 3 of 8 malformed IDs, `Financial Services` → `Financial` missing, etc.). Trust the checklist over the current code.

## Workflow conventions

- Git: single `main`; changes go through `feat/...` / `fix/...` branches merged back in (see `git log --merges`). Commit messages are lowercase imperative ("fix loading and schema setup per checklist section 1").
- Decisions D1–D10 (dedup strategy, barangay authority, `verified` policy, phone privacy, ...) are unanswered in `docs/PLANS.md` §3. Don't silently choose — ask, or record the rationale in the decision log before acting on it.
- Open question with the instructor: submission naming is `CPE15_MIDTERM_GROUPXX` / `lucban_establishments_groupXX_*`, but current files use `3GF`. Don't rename unilaterally.
- Final submission layout (per spec §13): `CPE15_MIDTERM_GROUPXX/` containing `RAW/`, `CLEAN/`, `NOTEBOOK/`, `DOCUMENTATION/`, with filenames following the prescribed convention and no screenshots standing in for datasets.
