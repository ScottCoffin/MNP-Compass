# Contributing to MNP Compass

The companion manuscript states that the community can help keep this tool current by "suggest[ing]
updates through GitHub pull requests." This document describes that workflow.

## What you can contribute

- **A new reference** — a method, standard, guidance document, or other resource that belongs in
  the crosswalk.
- **A correction to an existing reference** — wrong metadata, a dead link, a missed topic tag, or a
  re-tiering suggestion (see [Tier assignment is interpretive](#tier-assignment-is-interpretive-and-maintainer-reviewed)
  below).
- **App or documentation fixes** — bugs in the Streamlit app, the decision-tree configuration, or
  the README/CONTRIBUTING/CLAUDE docs themselves.

## Proposing a new reference or a re-tiering

1. Open a GitHub issue first for anything nontrivial (a new reference, a re-tiering, a new
   matrix/instrument/particle-type category) so a maintainer can weigh in before you do the work.
   For small, unambiguous fixes (a typo, a dead link), a PR without a preceding issue is fine.
2. `mnp_compass/data/crosswalk.xlsx` (sheet "Crosswalk Table") is the single canonical source of
   data — see [README's Crosswalk Data Fields](README.md#crosswalk-data-fields) for the full column
   list. Edit it directly in Excel or another spreadsheet tool that preserves the `.xlsx` format
   and the existing header rows (row 1 is a grouping label, row 2 is the actual header, data starts
   row 3).
3. **Close Excel before running any script that reads or writes the workbook** — an open workbook
   can be locked or cause partial-read errors.
4. Fill in bibliographic fields (`Short Citation`, `Year`, `Full Title`, `DOI/URL`), classify the
   reference (`Document Type`, `Priority Tier`, `Primary Domain`, `Primary Focus`), and score the
   relevant topic columns using the tier schema below. Tag `Instrumentation Tags`, `Matrix Tags`,
   and `Particle/Polymer Type Tags` as applicable.
5. Do not hand-edit `Particle Size Range`, `Key Metrics / Output`, or `Abstract` if you'd rather let
   `scripts/fill_crosswalk_metadata.py` populate them (dry-run by default; see
   [Metadata Fill Workflow](README.md#metadata-fill-workflow)).

## Tier schema

Every reference is scored on the same four-tier authority-and-validation framework used throughout
the app. The canonical definitions live in `mnp_compass/tabs/citation_tab.py`
(`TIER_FRAMEWORK_INTRO` / `TIER_FRAMEWORK_TIERS` / `TIER_FRAMEWORK_OUTRO`) and are quoted verbatim
in [README's Authority and Validation Tier Framework section](README.md#authority-and-validation-tier-framework).
Read that before assigning or proposing a tier — do not invent a fifth tier or redefine an existing
one in a PR without raising it as an issue first, since it would need to change in every location
listed there.

### Tier assignment is interpretive and maintainer-reviewed

Tiering is an editorial judgment, not a mechanical calculation — it reflects the *basis of a
resource's authority* (legal mandate, institutional endorsement, empirical validation, or
supporting context), not its scientific quality or how current it is. If you believe an existing
entry is mis-tiered, open an issue or PR explaining your reasoning (cite the specific tier
criterion it does or doesn't meet) rather than silently changing the number — a maintainer reviews
every tier assignment and re-tiering before merge.

## Validating your change before opening a PR

From the repository root:

```powershell
python -m pip install -r requirements.txt
python tests/smoke_test.py
streamlit run mnp_compass/app.py
```

The smoke test checks that the workbook has the columns the app expects, that tiers parse and
cover every row, that the decision tree and gap notes load, and that filters return results. The
`streamlit run` command lets you confirm your new/edited reference actually surfaces in the tabs
you'd expect (Decision Tree, Crosswalk, Search All References). Both should succeed before you open
a PR; if the smoke test was already failing before your change (check `git stash` against `main`),
say so in the PR rather than trying to fix unrelated failures.

## Pull request checklist

- [ ] `python tests/smoke_test.py` passes (or you've noted pre-existing failures your change didn't
      introduce)
- [ ] `streamlit run mnp_compass/app.py` launches and your change is visible where expected
- [ ] `crosswalk.xlsx` was edited with Excel closed afterward (no lock file left behind)
- [ ] New/changed tier assignments are explained in the PR description
- [ ] No unrelated reformatting bundled into the diff
