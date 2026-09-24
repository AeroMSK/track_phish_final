# WALKTHROUGH — TRAC-Phish Revision 11 Paper Lock

This file documents exactly what changed in the **paper-lock pass** (the latest update to this
repository), so that the modification history is always auditable. The full task specification
lives in `Task.txt` at the repository root.

## Canonical artifacts

| Artifact | Path |
|---|---|
| Final notebook (ONE canonical notebook, executed) | `notebook/trac-phish-revision11_runned.ipynb` (217 cells) |
| Final paper-lock report | `notebook/paper_lock/FINAL_REVISION_11_REPORT.md` |
| Final paper tables (11 CSV + TEX pairs) | `notebook/paper_lock/final_paper_tables/` and `final_paper_tables.zip` |
| Final figures 1–5 (PNG + PDF) | `notebook/paper_lock/final_figures/` |
| Separated-pages HTML presentation (12 pages) | `notebook/paper_lock/paper_lock_pages/index.html` |
| Paper-lock reproducibility manifest | `notebook/paper_lock/FINAL_MANIFEST_R11.json` |
| Final abstract + positioning | `notebook/paper_lock/final_abstract.md` |
| Everything bundled | `notebook/paper_lock/trac_phish_revision11_paper_lock.zip` |

## What the paper-lock pass changed

### 1. Final scientific framing (notebook cells 0–1)
- Final title: **"Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection"**.
  The old working title ("Beyond Prediction Confidence: Reliability-Calibrated Explanations …")
  is explicitly superseded (the decision-value hypothesis failed); it is preserved as history.
- The revision-11 plan note was corrected: RFC 3986 canonicalisation was planned but is
  **deliberately NOT enabled** (`CANONICALISE_INPUT = False`), because it makes the ERS
  reliability target degenerate. P3 is retained as a limitation.

### 2. Revision metadata (notebook config cell)
- `notebook_revision = 11` (was mislabelled 7). The checkpoint fingerprint is NOT affected
  (it never included the revision number), so caches remain valid.

### 3. F69-R-v3 naming (paper-facing alias; internal keys untouched)
- `pretty_fset` now maps the internal key `F68RV3` → **"F69-R-v3 (69 cols)"**.
- Internal keys (`F68RV3`, run keys, checkpoint names) are preserved everywhere for
  checkpoint compatibility; every paper-facing display uses F69-R-v3.
- F69-R-v3 = F54-R (54) + 15 domain-invariant = **69 features**; sanity-checked.

### 4. Criterion E — RESOLVED (was "unavailable")
- Root cause: Section 48 looked up `pretty_fset(PRIMARY_FSET) - F48` in `REPR_COMPARISON`,
  a comparison string that does not exist; the pre-registered comparison "F54-R - F48" was
  computed by Section 39R but never read.
- The paper-lock final section resolves it **from the cached executed paired DeLong results**
  (no retraining): strict-external dAUC = **−0.00194 [−0.00238, −0.00150]** (G→P) and
  **−0.00467 [−0.00521, −0.00413]** (P→G) → **NOT SUPPORTED** (significantly negative).
- The lookup bug is also fixed in Section 48 itself for future re-runs.

### 5. Final gate table and claim matrix (new final section, cells 207–216)
- `FINAL_GATE_TABLE_R11` (12 rows: FOUNDATION / REPRESENTATION / TRANSFER (UDA) /
  SEMI-SUPERVISED / ROBUSTNESS / ERS TARGET / ERS vs CONFIDENCE / ERS CORRECTNESS / DTS /
  TEMPORAL / CRITERION E / REPRODUCIBILITY) — every value read from executed result objects.
- `FINAL_CLAIMS_TABLE` (C1–C10) with allowed wording and prohibited overclaims.
- Final criteria table with E resolved; reversal diagnostic table (negative finding).
- Final figures 1–5 (PNG+PDF); 11 final tables (CSV+TEX) zipped as `final_paper_tables.zip`.
- Final abstract (evidence-aligned), positioning paragraph, 10 findings, 9 limitations.
- 20 paper-lock sanity checks (all passing; the executed 238/238 untouched).

### 6. Historical sections preserved and marked
- Sections 54–57 and the revision-5/6/7 phase summaries are prefixed with
  "HISTORICAL DEVELOPMENT OUTPUT — NOT FINAL" banners; no history was deleted.
- Stale LegitPhish references in two final-path markdown cells (Sections 16 and 40) were
  corrected to the actual corpora (GramBeddings/PhreshPhish).

### 7. UDA vs zero-shot labelling
- M7 is labelled **UDA** (unlabeled target TRAIN + word expert + fusion + self-training,
  source-VAL guard, no target VAL/TEST labels for fitting); M0 remains the zero-shot baseline.
- The 0.9438 / 0.9558 accuracies are attributed to the **semi-supervised multi-source
  benchmark** (M2h / M2s), which is a separate claim from UDA.

## Compute budget
**No new experiments were added.** Everything in the paper-lock section is reporting code,
metadata correction, or cheap deterministic regeneration from the executed full-scale
(~639 min) revision-11 run. All 109 pre-existing code cells keep their original executed
outputs; the 10 new final-section cells (110–118) are the only newly executed code.

## How the paper-lock cells work (dual mode)
The final section reads its data either from **live in-memory objects** (if the notebook is
re-run top to bottom) or by **parsing the executed outputs embedded in this very notebook**
(paper-lock mode). Nothing is hand-typed; every displayed number is traceable to an executed
result object. This is asserted by the 20 paper-lock sanity checks at the end of the notebook.

---

# UPDATE — live-mode completion of the paper-lock section (Kaggle-readiness)

## What changed
A fresh **top-to-bottom re-run** (e.g. on Kaggle) executes the final section in *live mode*,
reading every result from the in-memory objects of the run itself. An audit found that five
`_load(...)` calls in cell 208 were missing or mis-named live counterparts, and three
evidence strings in cells 211/215 carried hand-typed numbers — none of which could fail in
parse mode (the mode that produced the committed artifacts), but any of which would have
crashed or gone stale at the END of a fresh ~10.7 h execution. All are fixed:

1. **Cell 208 (lock bootstrap)** — `_load()` now accepts a global name *or* a zero-arg
   callable and wires every table to its live counterpart:
   `DATASET_AUDIT→TABLES["table01_dataset_audit_provenance"]`,
   `ABLATION→ABLATION_TABLE`, `TRANSFER_COMPARE→R8_BEFORE_AFTER`,
   `DTS_GATE_R6→R6_DTS_TABLE`, `DTS_GATE_R7→R7_DTS_TABLE`,
   `STRATA_RHO→ERS_LEGACY_TABLE`, `FLIP_R6→pivot(R6_FLIP_TABLE)`,
   `ROBUST_R7→pivot(R7_FLIP_TABLE)`, `STRESS→STRESS_TABLE`; the live
   `R10_ATTRIBUTION` is re-oriented with `set_index("direction").T` to the layout the parse
   path restores; `GATE3_TEXT` is reconstructed in live mode from the `P3_ACC_GATE` dict;
   and `_find_nb()` additionally searches `/kaggle/input` for an attached copy of the
   executed notebook (parse-mode fallback for Option B of the run guide).
2. **Cells 211/215** — the last hand-typed evidence numbers (rho 0.0691, LRT p_holm
   0.363/1.0, reversal 0.0305/0.5614/OR 0.025, S_challenge ranges, 0.9438, ECE
   0.0716→0.2497, origin/W/AUC figures) are now f-strings over the same loaded objects,
   reproducing the executed strings byte-for-byte in parse mode and tracking a fresh run
   in live mode.

## What did NOT change
- **Zero numbers changed.** The lock section was re-executed in parse mode after the edits:
  the final tables (all 11 CSV + TEX pairs), `FINAL_REVISION_11_REPORT.md`,
  `final_abstract.md`, `FINAL_MANIFEST_R11.json` and all separated HTML pages are
  byte-identical to the previously committed versions (only the ZIP archives' internal
  PDF timestamps differ). The notebook keeps 217 cells; cells 0–206 are untouched.
- Cell 215's "origin ROC-AUC 0.929" statements are now wired to `ORIGIN_F69` (the primary
  representation's origin AUC, 0.9291 — the value the abstract and findings already used);
  F48's origin AUC is 0.9200 and continues to be quoted per-representation in claim C1.

## Verification (IMPLEMENT → RUN → INSPECT → GATE)
- Parse mode: re-executed cells 207–216 — `PAPER-LOCK SANITY: 20/20`, `238/238` executed
  checks, artifact parity confirmed against the committed copies.
- Live mode: `notebook/paper_lock/tools/test_live_mode_lock.py` executes the lock cells
  with live globals reconstructed from the executed outputs and **no parse source
  available** — `PL_MODE='live …'`, 20/20 checks, all deliverables generated. This is the
  exact code path a fresh Kaggle full re-run takes.

## New file
`KAGGLE_RUN_GUIDE.md` (repository root) — step-by-step instructions for the two supported
Kaggle modes: full re-run (~10.7 h, fits the 12 h CPU cap, checkpoint resume included)
and paper-lock-only regeneration (~2 min from an attached copy of the executed notebook).
`notebook/paper_lock/tools/` holds the lock-cell sources and the rebuild/test scripts.
