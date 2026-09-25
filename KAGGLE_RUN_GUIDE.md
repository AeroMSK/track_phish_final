# Kaggle Run Guide — trac-phish-revision11

This guide covers two run modes:
1. **Full re-run** (~10.7 hours) — re-executes the entire research pipeline from raw data.
2. **Paper-lock-only** (~2 minutes) — reads the executed outputs embedded in the notebook (no retraining).

For both modes, upload the notebook `notebook/trac-phish-revision11_runned.ipynb` and both datasets to Kaggle.

---

## 1. Dataset upload

Upload two separate Kaggle Datasets:

| Kaggle Dataset slug | Contents |
|---------------------|----------|
| `grambeddings-dataset` | `grambeddings_dataset_main.rar` (containing `classes.txt`, `train.csv`, `test.csv`) |
| `phreshphish-url-only-2026` | `phreshphish_url_only_2026.zip` (containing `phreshphish_transfer/` with 2 parquet files + metadata) |

The notebook's dataset discovery (Cell 16) does a recursive search from `/kaggle/input` and handles both:
- **Case 1**: dataset uploaded as a Kaggle Dataset (files extracted by Kaggle).
- **Case 2**: dataset uploaded as a direct zip/rar (notebook extracts via `unrar` / `7z` / `unar` / `bsdtar` / `libarchive-c` / `apt-get` fallbacks).

---

## 2. Full re-run (~10.7 hours)

### Kaggle notebook settings

- **Accelerator**: None (CPU-only — required for bit-level reproducibility across sessions; all models run on CPU).
- **Internet**: On (only needed for `pip install` of `xgboost`, `lightgbm`, `shap`, `tldextract` if not pre-installed).
- **Environment**: Default Python 3.12 + the packages listed in `PACKAGE_VERSIONS` (Cell 6 output).
- **Persistence**: Variables (cell outputs) — the paper-lock section reads from in-memory objects.

### Run

1. Open the notebook in Kaggle.
2. Set environment variable (optional): `TRAC_RUN_MODE=full` (this is the default).
3. Run all cells top-to-bottom (Cell 0 → Cell 216).
4. The 12-hour Kaggle session cap is handled by per-stage `r7_cache` checkpoints keyed by content hash. If the session is interrupted, re-running will resume from the last checkpoint (the checkpoints live in `/kaggle/working/trac_phish_results/cache/revision7/`).

### Expected phase timings (from the executed run)

| Phase | Cells | Approx. time |
|-------|-------|--------------|
| Setup + dataset loading + hygiene | 0–60 | ~15 min |
| Phase 1 (representation, F69-R-v3 selection) | 61–73 | ~45 min |
| Phase 2 (training + cross-dataset transfer M0–M5) | 74–100 | ~120 min |
| Phase 3 (robustness R7) | 101–127 | ~60 min |
| Phase 4 (DTS) | 128–137 | ~30 min |
| Phase 5 (ERS calibration) | 138–150 | ~45 min |
| Phase 6 (ablation) | 151–170 | ~60 min |
| Phase 7 (representation comparison + Criterion E) | 171–188 | ~90 min |
| Phase 8 (multi-source M2h/M2s/M4h) | 189–206 | ~180 min |
| Phase 9 (R10 self-training M7, ~45 min) | 104 (within Phase 8) | ~45 min |
| Phase 10 (R11 Gate 3 stacking) | 106 (within Phase 8) | ~30 min |
| Section 55 (sanity checks, 238 checks) | 194 | ~5 min |
| Historical development outputs | 195–206 | ~5 min |
| **FINAL REVISION 11 — PAPER LOCK** | 207–216 | **~2 min** |
| **Total** | 0–216 | **~10.7 h** |

### After the run

The paper-lock section produces these artifacts under `/kaggle/working/trac_phish_paper_lock/`:

- `FINAL_REVISION_11_REPORT.md` — master report
- `final_abstract.md` — paper abstract
- `FINAL_MANIFEST_R11.json` — artifact manifest
- `final_paper_tables.zip` — 11 CSV + 11 LaTeX files
- `trac_phish_revision11_paper_lock.zip` — full bundle (report + tables + figures + HTML pages + manifest)
- `final_paper_tables/` — 11 CSV + 11 `.tex` files
- `final_figures/` — 5 figures (PNG + PDF, 300 DPI)
- `paper_lock_pages/` — 12 HTML pages (index, datasets, representation, transfer, ers, dts, temporal, robustness, gates, claims, limitations, reproducibility)

Download the zip bundles for offline viewing.

---

## 3. Paper-lock-only run (~2 minutes)

If you only want to re-execute the paper-lock section (Cells 207–216) without re-running the 10-hour pipeline, you have two options:

### Option A: Run on the notebook with embedded outputs (no live objects)

If the notebook's Cells 0–206 still have their executed outputs embedded (the canonical notebook ships with these), you can run only Cells 207–216. In this case:
- `PL_LIVE = False` (because `REPR_COMPARISON` is not in `globals()` — only the outputs are embedded, not the variables).
- The paper-lock loader will parse the notebook file itself to recover the tables from the embedded HTML outputs.
- **Requirement**: the executing `.ipynb` file must be discoverable. Set `TRAC_NB_PATH` environment variable to the notebook's path, or ensure the notebook is in the working directory.

### Option B: Run after a full pipeline execution (live mode)

If you've just run the full pipeline (Cells 0–206) in the current kernel, all the live objects (`REPR_COMPARISON`, `R10_ATTRIBUTION`, `R6_FLIP_TABLE`, etc.) are in memory. In this case:
- `PL_LIVE = True` (because `REPR_COMPARISON` is a DataFrame in `globals()`).
- The paper-lock loader reads directly from the in-memory objects — **no `.ipynb` file required**.
- This is the mode the notebook will be in after a fresh Kaggle run from Cell 0.

---

## 4. Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `TRAC_RUN_MODE` | `full` | `full` / `reduced` / `smoke` |
| `TRAC_INPUT_ROOT` | `/kaggle/input` | Where datasets are discovered |
| `TRAC_WORK_ROOT` | `/kaggle/working` | Where outputs + checkpoints are written |
| `TRAC_NB_PATH` | (auto-detected) | Path to the executed `.ipynb` file (only needed in paper-lock parse mode) |
| `TRAC_PL_OUT` | `<work_root>/trac_phish_paper_lock` | Where paper-lock artifacts are written |
| `TRAC_N_JOBS` | `os.cpu_count()` | Parallelism for model training |
| `R7_FORCE_RECOMPUTE` | (unset) | If set to `1`, bypasses all `r7_cache` checkpoints |

---

## 5. Troubleshooting

### "paper-lock: notebook parsing is disabled in live mode"

This error means `_require_parse_mode()` was called when `PL_LIVE=True`. It indicates a `_load()` call is missing its `live_obj` or `live_callable` mapping. Check the error message for the `PL[...]` key name and add the mapping in Cell 208.

### "paper-lock live mode: cannot resolve PL[...]"

This error means a `_load()` call's `live_obj` global doesn't exist or is empty. Check that the producing cell (the one that creates the global) has been executed. The error message includes the `live_obj` name and `live_callable` flag.

### "expected 238/238 executed sanity checks, got N"

This means some sanity checks in Cell 194 failed. The notebook raises `RuntimeError` in Cell 194 if any check fails, so this shouldn't happen — but if it does, inspect the `CHECKS` list to see which check failed.

### "Gate 3 evidence not fully recovered: {}"

This means `PL["GATE3_TEXT"]` didn't contain 2 regex matches. In live mode, `GATE3_TEXT` is synthesised from `P3_ACC_GATE["by_direction"]`. If `P3_ACC_GATE` is missing or its `by_direction` dict is empty, the synthesis will produce an empty string. Check that Cell 96 (which creates `P3_ACC_GATE`) has been executed.

### Checkpoint cache issues

If you suspect a stale checkpoint:
1. Set `R7_FORCE_RECOMPUTE=1` and re-run.
2. Or delete `/kaggle/working/trac_phish_results/cache/revision7/` and re-run.

---

## 6. Reproducibility checklist

Before publishing results from a Kaggle run, verify:

- [ ] Cell 6 output shows `seed: 42` and the expected package versions.
- [ ] Cell 17 output shows the dataset SHA-256 hashes match the documented values.
- [ ] Cell 194 output shows `238/238 checks passed. FINAL SANITY CHECK: PASSED`.
- [ ] Cell 208 output shows `PAPER-LOCK DATA MODE: live (full revision-11 execution in memory)`.
- [ ] Cell 208 output shows `executed-run sanity checks: 238/238 passed`.
- [ ] Cell 216 output shows `20/20 paper-lock checks passed` (or the dynamic equivalent).
- [ ] The final report (`FINAL_REVISION_11_REPORT.md`) includes the gate table, claim matrix, and limitations.
- [ ] The UDA AUCs `0.873913` (Gram→Phresh) and `0.824266` (Phresh→Gram) appear in the transfer results table.
- [ ] Criterion E is reported as `NOT SUPPORTED` in the criteria table.
- [ ] The title is the neutral "Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection" (not the working title).
