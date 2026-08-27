# Audit Findings — MNP Compass Consistency & Provenance

Produced per `mandate.md` §1 (discovery/audit pass), before any edits. All items below were
verified against the actual files, not the code-summary claims in the mandate.

## A. Reference count

`mnp_compass/data/crosswalk.xlsx`, sheet "Crosswalk Table", header row 2 (index 1): **190 rows**,
none blank. This is the ground truth.

- README.md currently says "> 175 seminal references" — **stale, understates by 15**.
- citation_tab.py `ABOUT_TEXT` currently says "approximately 150 seminal references" — **stale,
  understates by 40**.
- Neither location agrees with the other or with the data. → Task 2.

## B. Column headers

Full raw header list (row 2), after the app's whitespace/newline normalization:

```
#, Short Citation, Year, Full Title, DOI/URL, Primary Domain, Primary Focus, Document Type,
Priority Tier, Instrumentation Tags, Matrix Tags, Particle/Polymer Type Tags, Target Receptor(s),
Definitions & Terminology, Problem Formulation / Framework, Sampling (Field Methods),
Matrix: Drinking Water, Matrix: Surface Water, Matrix: Surface Water - Lacustrine,
Matrix: Surface Water - Riverine, Matrix: Surface Water - Marine, Matrix: Wastewater,
Matrix: Groundwater, Matrix: Biosolids, Matrix: Sediment, Matrix: Soil, Matrix: Biota/Tissue,
Matrix: Air/Atmos., Matrix: Food/Dietary, Matrix: Human Tissue/Biomonitor,
Sample Processing / Extraction, Sub-sampling, Analytical Methods (General),
FTIR / IR Spectroscopy, Raman Spectroscopy, Py-GC-MS, Imaging, Material Standards - materials,
Material Standards - protocol, Blanks & Contamination Control, Data Analysis & Statistics,
Reporting & Harmonization, Databases & Data Sharing, Toxicology: Study Design & Dosimetry,
Toxicology: Effects Testing Methods, Toxicology: Reporting & Harmonization,
Toxicology: Databases & Data Sharing, Risk Assessment / Risk Char., Key Notes, Scope, Status,
Particle Size Range, Key Metrics / Output, Abstract
```

Compared against the smoke test's `required[]` list (`Short Citation`, `Document Type`,
`Authority and Validation Tier`, `Key Notes`, `Primary Domain`, `Instrumentation Tags`,
`Matrix Tags`, `Primary Focus`, `Target Receptor(s)`, `Particle/Polymer Type Tags`, `Scope`,
`Status`, `Key Metrics / Output`, `Abstract`, `tier_num`):

- **Every required column exists in the workbook** under its expected name (`Priority Tier` is
  renamed to `Authority and Validation Tier` in-memory by `load_crosswalk()`; `tier_num` is
  computed, not a workbook column). No `KeyError` risk found.
- `Status` exists directly in the workbook. **There is no `Reviewed` column and no
  `PDF Available in Zotero?` column currently in the workbook** — see finding under §F/Task 5
  below; these are not the same field as `Status`, they just don't exist yet.
- Extra workbook columns not in `required[]` (expected — these are topic-scoring / narrative
  columns not asserted by the smoke test): all the `Matrix: *`, `Toxicology: *`, and topic columns
  above, plus `#`, `Year`, `Full Title`, `DOI/URL`, `Particle Size Range`.

## C. Matrix / instrument / particle-type enumerations

Three independent enumerations exist and have drifted:

| Source | Matrices | Count |
|---|---|---|
| `tree_structure.yaml` (`matrix_select` node) | drinking_water, surface_water (labelled "Surface Water / Wastewater"), sediment, biota, air, food, human_tissue, soil | **8** |
| `visual_tree_tab.py` `MATRICES` dict (hardcoded) | drinking_water, surface_water, wastewater, biosolids, sediment, biota, air, food, human_tissue, soil | **10** |
| Distinct `Matrix Tags` substrings actually in the crosswalk | confirms drinking_water/surface_water/wastewater/sediment/biota/air/food/human_tissue/soil all have real rows | — |

**Important, previously-unreported finding: `biosolids` matches zero rows.** No row's `Matrix
Tags` field contains the literal substring "Biosolids" — the closest is one row
(`Li et al., 2019`, tags `"Soil; Sludge"`) using "Sludge" instead. So the 10-matrix hardcoded set
in `visual_tree_tab.py` includes one matrix with no data behind it as currently keyworded.

This is a genuine divergence with no data-driven way to resolve automatically — flagged as
**TODO(human)** per mandate rule 0.3. See Task 4.

**Instrumentation and particle-type keyword check** (`visual_tree_tab.py` `INSTRUMENTS` /
`PARTICLE_TYPES` dicts vs. actual `Instrumentation Tags` / `Particle/Polymer Type Tags` values):
all keywords resolve to at least one matching row **except** the `ermp` particle-type entry,
which searches for `"Environmentally Realistic Mixtures;ERMP"` — the workbook's actual tag text is
**"Environmentally Realistic Microplastic Mixtures"** (2 rows use it), so the current keyword
matches zero rows. This is a straightforward keyword-text bug (not a data/tiering change) and is
fixed under Task 4.

## D. Tier definitions per location (as found, before edits)

- **`citation_tab.py`**: canonical 4-tier text already correct (Tier 1 Normative/Binding, Tier 2
  Authoritative/Institutional incl. ISO/ASTM/WHO/EFSA/GESAMP/NIST, Tier 3
  Validated/Interlaboratory-Tested/Critical Guidance, Tier 4 Supporting/Contextual) — this is the
  most recently written and most complete definition, and is treated as the canonical source.
- **`README.md`**: stale — only defines Tier 1 and Tier 4, and *incorrectly places ISO/ASTM under
  Tier 1* ("Tier 1 normative and binding standards (e.g., ISO, ASTM, government regulations and
  SOPs)"). Confirmed a real bug. → Task 1.
- **`visual_tree_tab.py` `TIER_LABELS`** and **`app.py` `TIER_LABELS`**: both already read
  "★☆☆☆ Tier 4 — Supporting / Contextual" and match the citation-tab wording for all 4 tiers
  (these were already aligned in a prior session). → Task 10 confirmed passing, no change needed.
- **`glossary_tab.py`**: already rewritten (prior session) to match the citation-tab tier text.

## E. Legacy product name occurrences

`grep -rIn -i "methods navigator"` across tracked/working source (excluding `.git`):

- `CLAUDE.md:1` — `# CLAUDE.md — Methods Navigator` (title heading missed in the earlier rename
  pass; CLAUDE.md is gitignored but still live project documentation).
- `tests/smoke_test.py:2` — docstring: "Headless smoke test for the Microplastics Methods
  Navigator."
- `.playwright-cli/*.yml` — stale cached browser-test snapshots from April/May 2026, not source
  code and not loaded by the app; left untouched (out of scope, historical artifacts).
- `mandate.md` — the mandate document itself; not app code, left as-is.

No other occurrences found. → Task 6.

## F. `tree_structure.yaml` usage

**Critical finding: `tree_structure.yaml` is loaded but has zero effect on the live app.**

- `app.py` `load_tree()` reads and parses the YAML, and passes the result into
  `render_decision_tree(df, tree)` in `visual_tree_tab.py`.
- `visual_tree_tab.py`'s `render_decision_tree(df, tree=None)` **never references the `tree`
  parameter anywhere in its body** — confirmed by search. The entire visible "Decision Tree" tab
  is driven by hardcoded Python dicts (`MATRICES`, `INSTRUMENTS`, `PARTICLE_TYPES`, `TEST_SYSTEMS`,
  workflow step lists) defined at module scope in `visual_tree_tab.py`.
- The *only* code path that actually consumes the loaded YAML is the "Step-by-Step Navigator" tab
  (`tab1` in `app.py`'s `main()`), which is gated behind `step_by_step_enabled = False` —
  **hardcoded off**, so that tab never renders for any user.

Net effect: the YAML and the hardcoded dicts have been free to drift for as long as
`step_by_step_enabled` has been `False`, because nothing exercises the YAML path. This is the root
cause of the matrix-set divergence in §C. A real single-source-of-truth fix means either (a)
wiring `visual_tree_tab.py` to read from the YAML, which is a substantial refactor of a large,
already-partially-failing file, or (b) formally retiring the YAML/step-by-step path and
documenting that `visual_tree_tab.py`'s hardcoded dicts are the sole source of truth. Per mandate
rule 0.3/0.5, this is left as a flagged **TODO(human)** decision rather than an autonomous rewrite
— see Task 4.

## Pre-existing, unrelated smoke-test failures (baseline, confirmed via `git stash` in a prior
session and unchanged by any work in this mandate)

- `Decision Tree auxiliary node renders`
- `Toxicology workflow orders reference particles before characterization and dosimetry`
- `decision tree smoke error`

These predate this mandate and are not touched by it.

## Task 1 data check (report only, per mandate rule 0.2 — no tier_num edits made)

Rows whose `Short Citation` or `Document Type` mentions ISO/ASTM **and** whose `tier_num == 1`:
**zero**. All current ISO/ASTM entries in the workbook are already tiered 2 or higher; there is no
mis-tiering to report to the maintainer. The README's old wording was a documentation error only,
not a symptom of bad data.

## Task 3 finding: the mandate's claimed manuscript title could not be verified

`mandate.md` asserts the current manuscript title is "MNP Compass: a resource for coordinating
microplastics research, reporting, and publication criteria across disciplines," citing an
internal reference to `Letter-to-journals-and-funders-(2).docx`. **No `.docx` file exists anywhere
in this repository**, and the phrase "MNP Compass" does not appear in either letter draft that
does exist:

- `Letter to journals and funders.md` (repo root, the more complete draft with a full author list)
  titles the piece "Learning from history instead of reinventing the wheel: **A call for**
  coordinating microplastics research, reporting, and publication criteria across disciplines."
- `docs/letter-to-journals-and-funders.md` (an earlier/rougher draft) titles it "Don't reinvent the
  wheel - Call for utilizing microplastics research, reporting, and publication criteria."

`citation_tab.py`'s current `PAPER_TITLE` already matches the root-level draft almost exactly
("**A resource for** coordinating..." vs. "A call for coordinating...") — a one-word difference,
not the wholesale "MNP Compass:" retitle the mandate described. Per mandate rule 0.1 ("if the
current state differs from the description, adapt the fix to the real code and note the
difference"), `PAPER_TITLE` was left unchanged and a `TODO(human)` was added in its place instead
of applying the unverifiable title. **Flagged for the maintainer:** confirm the actual current
manuscript title, and check whether a newer draft (with the "MNP Compass:" framing) exists outside
this repository — e.g. in a source the mandate's authoring process had access to but this session
did not (Obsidian and another MCP connector both failed to connect in this session, for what
that's worth).

## Task 11 data point (report only)

Rows with either `Material Standards - materials` or `Material Standards - protocol` populated
(the Material Standards / Positive Controls workflow step): **23 references**, comfortably above
the manuscript's stated "15."

---
*This file is a working artifact for the mandate implementation and can be deleted once the
findings below have been acted on and reviewed by the maintainer.*
