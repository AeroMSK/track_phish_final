# WALKTHROUGH — Latest Update

**Date**: 2026-09-26
**Notebook**: `notebook/trac-phish-revision11_runned.ipynb` (217 cells, paper-lock revision 11)
**Total fixes applied this session**: 5 (1 loader rewrite + 4 surgical bug fixes)

---

## What changed in this update

This update contains **5 cumulative fixes** that make the paper-lock section (Cells 207–216) executable in a fresh Kaggle runtime after the full ~10-hour pipeline has naturally populated all in-memory objects.

### Fix 1 — Cell 208 paper-lock loader (live-mode aware) [previous turn, verified]

**Problem**: Cell 208 crashed with `TypeError: 'NoneType' object is not subscriptable` because `_PL_NB` is `None` in live mode (no `.ipynb` file discoverable at runtime), but `_pl_cells()` accessed `_PL_NB["cells"]`.

**Fix** (5 categories of changes, all in Cell 208):
1. Added `_require_parse_mode()` guard called by `_pl_cells`, `_cell_by_marker`, `pl_table`, `pl_stream`, `pl_json_blobs` — they now raise `RuntimeError` in live mode instead of crashing on `_PL_NB["cells"]`.
2. Added 3 `live_callable` helpers:
   - `_live_dataset_audit()` → reads from `TABLES["table01_dataset_audit_provenance"]`
   - `_live_flip_r6()` → pivots `R6_FLIP_TABLE` to `(run, population, family) × model`
   - `_live_robust_r7()` → pivots `R7_FLIP_TABLE` to `(run, family) × model`
3. Extended `_load()` with a `live_callable` parameter; in live mode it raises `RuntimeError` if neither `live_callable` nor `live_obj` resolves to a non-empty DataFrame (no fall-through to notebook parsing).
4. Fixed 9 `_load()` calls (4 missing live sources + 5 wrong `live_obj` names):
   - `DATASET_AUDIT` → `live_callable=_live_dataset_audit`
   - `ABLATION` → `live_obj="ABLATION_TABLE"` (was `"ABL_TABLE"`)
   - `TRANSFER_COMPARE` → `live_obj="R8_BEFORE_AFTER"` (was missing)
   - `DTS_GATE_R6` → `live_obj="R6_DTS_TABLE"` (was `"DTS_AURC_TABLE"`)
   - `DTS_GATE_R7` → `live_obj="R7_DTS_TABLE"` (was `"R7_P6_TABLE"`)
   - `STRATA_RHO` → `live_obj="ERS_LEGACY_TABLE"` (was `"STRATA_TABLE"`)
   - `FLIP_R6` → `live_callable=_live_flip_r6` (was missing; needs pivot)
   - `ROBUST_R7` → `live_callable=_live_robust_r7` (was `"R7_ROBUST_TABLE"`; needs pivot)
   - `STRESS` → `live_obj="STRESS_TABLE"` (was missing)
5. Fixed `GATE3_TEXT` live-mode: synthesised a regex-matchable string from `P3_ACC_GATE["by_direction"]` matching the format Cell 96 prints, so Cell 210's `assert len(_g3) == 2` passes.

### Fix 2 — Cell 210 ORIGIN_F69 feature_set filter (Bug #1)

**Problem**: Cell 210 line 67 used `_ot["feature_set"] == "F68RV3"` but the `feature_set` column contains `pretty_fset()` output values like `"F69-R-v3 (69 cols)"`, not the raw key. The filter always returned empty → `.iloc[0]` raised `IndexError`.

**Fix**: Changed to `_ot["feature_set"] == pretty_fset("F68RV3")`. The `pretty_fset()` function is defined in Cell 57 and is available as a global when Cell 210 runs.

### Fix 3 — Cell 208 R10_ATTRIBUTION live-mode transposition (Bug #2)

**Problem**: In live mode, `PL["R10_ATTRIBUTION"] = R10_ATTRIBUTION` assigned the long-form DataFrame (rows = directions, columns = metrics). But the assertion `{"M6 (revision 8)", "M7 (revision 10)", ...} <= set(PL["R10_ATTRIBUTION"].index)` and Cell 210's `_attr.loc["M7 (revision 10)", direction]` both expect the transposed shape (index = metrics, columns = directions) that the parse mode produces from `display(R10_ATTRIBUTION.T)`.

**Fix**: Changed the live branch to:
```python
_r10_live = R10_ATTRIBUTION.set_index("direction").T
PL["R10_ATTRIBUTION"] = _r10_live.apply(pd.to_numeric, errors="coerce").where(
    _r10_live.apply(pd.to_numeric, errors="coerce").notna(), _r10_live)
```
This mirrors the parse-mode shape exactly. Verified: `PL["R10_ATTRIBUTION"].loc["M7 (revision 10)", "GramBeddings -> PhreshPhish"]` returns `0.873913` and `PhreshPhish -> GramBeddings` returns `0.824266`.

### Fix 4 — Cell 216 REPR_TABLE feature_set filter (Bug #3)

**Problem**: Cell 216 lines 17–19 used the same broken `feature_set == "F68RV3"` filter as Bug #1. The `pl_check` for "final primary representation has 69 features" always recorded `False` → `assert PL_N_PASS == len(PL_CHECKS)` failed.

**Fix**: Changed to `feature_set.astype(str) == pretty_fset("F68RV3")`.

### Fix 5 — Cell 144 delong_test key mismatch (Bug #4, from Audit A3)

**Problem**: `delong_test()` returns a dict with key `"diff"`, but Cell 144 accessed `d.get("delta")` → returned `None` for all 24 rows. This left the `delta_auc` column of `CRITERION_F_TABLE` as `None` and the `effect` column of `STATS_TABLE` as `NaN` for 24 criterion_F rows. The CI bounds and p-values were unaffected.

**Fix**: Changed `d.get("delta")` → `d.get("diff")` (2 occurrences in Cell 144).

---

## 10-audit summary

10 parallel sub-agents audited the notebook across 10 dimensions. Verdicts:

| Audit | Dimension | Verdict | Key finding |
|-------|-----------|---------|-------------|
| A1 | Cell 208 fix correctness | **PASS** | All 8 checks pass; fix is correct, complete, minimal |
| A2 | Data leakage risks | **PASS** (1 MEDIUM) | 7/8 vectors clean; r7_cache key lacks content hash |
| A3 | Statistical validity | **PASS** (1 FAIL fixed) | Cell 144 typo fixed; DeLong CIs for Criterion E correct |
| A4 | ML pipeline | **PASS** (2 WARNs) | class_weight="balanced" is documented primary strategy |
| A5 | XAI pipeline | **PASS** (3 WARNs) | ERS formula correctly excludes confidence; SHAP usage correct |
| A6 | Reproducibility | **PASS** (10 minor WARNs) | SEED=42, derived_seed SHA-256, 6 gate hashes pinned |
| A7 | Gate logic consistency | **PASS** | 12 gates, 6 PASS / 4 FAIL / 1 NOT SUPPORTED / 1 PARTIAL |
| A8 | Claims vs evidence | **ALIGNED** (3 bugs fixed) | All 10 claims C1–C10 match executed evidence |
| A9 | CSV/LaTeX exports | **WARN** (conditional PASS) | 23/23 artifacts would be produced; manifest could be richer |
| A10 | Final reproducibility | **PASS** (CONDITIONAL) | Ready for Kaggle fresh run; 20 PL_CHECKS (not 19) |

### Preserved scientific results (all verified)

- ✅ GramBeddings + PhreshPhish primary setup (no LegitPhish / no PhishTank in primary path)
- ✅ F69-R-v3 / internal F68RV3 (69 features = 54 F54-R + 15 invariant)
- ✅ UDA results: **0.873913** (Gram→Phresh) and **0.824266** (Phresh→Gram) AUC — accessible via `PL["R10_ATTRIBUTION"].loc["M7 (revision 10)", direction]`
- ✅ ERS findings (predicts held-out explanation stability; 4/4 Holm-significant; beats calibrated confidence on 4/4 external runs)
- ✅ DTS negative finding (0/12 external cells beat confidence with CI excluding 0)
- ✅ Robustness limitation: P3 dot-segment retained (max flip 47.57% > 15% criterion)
- ✅ Temporal calibration degradation (ECE 0.0716 → 0.2497 across PhreshPhish quarters)
- ✅ Criterion E = NOT SUPPORTED (dAUC −0.00194 / −0.00467, CIs exclude zero, negative direction)
- ✅ Final evidence-aligned claim matrix (10 claims C1–C10, all verdicts match evidence)
- ✅ Paper-lock framing (neutral title; abstract acknowledges mixed result)

---

## How to verify the fixes

### Quick verification (no Kaggle run needed)

```bash
# 1. Verify all 5 fixes are present in the notebook
python /home/z/my-project/scripts/verify_bugfixes.py

# 2. Run the live-mode dry-run simulation (mock data)
python /home/z/my-project/scripts/dry_run_test.py
```

### Full verification (Kaggle run)

1. Upload the notebook + both datasets to Kaggle.
2. Set `TRAC_RUN_MODE=full` (default).
3. Run from Cell 0. The full pipeline takes ~10.7 hours.
4. After Cell 206 completes, the paper-lock section (Cells 207–216) will execute in ~2 minutes using the in-memory objects.
5. All 20 paper-lock sanity checks should pass, and the final report + 12 HTML pages + 5 figures + 11 CSV/TeX pairs + manifest + zip bundle will be produced.

---

## Advisory items (not blocking, not fixed in this update)

These are minor improvements identified by the audits. They do not block the Kaggle run.

1. **A2**: `r7_cache` fingerprint could include `inspect.getsource(compute)` and CFG-subdict hashes for stronger cache invalidation.
2. **A4**: `class_weight="balanced"` is hardcoded as the primary strategy (documented in Section 19). This is a design choice, not a bug — but could be parameterised as `CFG.models[kind].get("class_weight", None)` for ablation flexibility.
3. **A5**: Cell 0 and Cell 124 markdown still cite the revision-5 ERS target formula `0.5*S_challenge + 0.3*S_P2 + 0.2*S_P1`; the implementation uses the revision-6+ target `0.5*S_challenge + 0.5*S_P3`. Sync the markdown.
4. **A5**: `ORIGIN_TABLE.top_origin_features` uses Gini importance, not permutation importance. Consider switching for stronger faithfulness.
5. **A6**: `os.environ.setdefault("PYTHONHASHSEED", str(SEED))` should be `os.environ["PYTHONHASHSEED"] = str(SEED)` for explicitness (cosmetic on Python 3.12).
6. **A6**: Dataset SHA-256 hashes are recorded but not asserted against pinned values. Add a `PINNED_DATASET_SHA256` dict.
7. **A9**: `FINAL_MANIFEST_R11.json` could include per-output-file SHA-256 hashes (currently only dataset-level `sha256_prefix`).
8. **A9**: `final_abstract.md` could mention "Criterion E" and "P3" by name (currently only in FINDINGS_FINAL / negative_findings).
9. **A10**: Cell 216 has 20 `pl_check()` calls, not 19 (the task description said 19). The dynamic `{len(PL_CHECKS)}` formatting handles this correctly.
10. **A10**: Limitations section could add: "Criterion E not supported", "single-seed evaluation", "two-corpus only (no third corpus)".

---

## File structure after this update

```
track_phish_final/
├── README.md                          (existing)
├── WALKTHROUGH.md                     (this file — NEW)
├── KAGGLE_RUN_GUIDE.md                (NEW — see below)
├── Datasets/
│   ├── grambeddings_dataset_main.rar  (17M, existing)
│   └── phreshphish_url_only_2026.zip  (41M, existing)
└── notebook/
    └── trac-phish-revision11_runned.ipynb  (217 cells, 5 fixes applied)
```
