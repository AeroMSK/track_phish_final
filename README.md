# track_phish_final

**Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection**
(TRAC-Phish, Revision 11 — paper lock)

## Repository layout

| Path | Contents |
|---|---|
| `Task.txt` | Full task specification for the revision-11 paper-lock pass |
| `WALKTHROUGH.md` | What changed in the latest update (always read this first) |
| `KAGGLE_RUN_GUIDE.md` | How to run the notebook on Kaggle (full re-run or paper-lock-only) |
| `notebook/trac-phish-revision11_runned.ipynb` | **The canonical notebook** (217 cells; cells 0–206 keep the original full-scale executed outputs and the surgical paper-lock edits; cells 207–216 are the executed FINAL REVISION 11 — PAPER LOCK section) |
| `notebook/paper_lock/` | Final paper-lock deliverables (report, tables, figures, HTML pages, manifest) |
| `Datasets/` | `grambeddings_dataset_main.rar`, `phreshphish_url_only_2026.zip` |

## Headline results (all read from the executed full-scale run)

- **UDA transfer (strict domain-unseen external):** M0 0.7712 → M7 **0.8739** AUC (Gram→Phresh),
  M0 0.7430 → M7 **0.8243** (Phresh→Gram); M7 uses unlabeled target TRAIN only.
- **ERS predicts held-out explanation stability** (all run configurations Holm-significant;
  ERS beats calibrated confidence on 4/4 external runs).
- **ERS does NOT add selective-classification decision value** beyond calibrated confidence
  (DTS 0/12 external cells; in-domain LRT not significant). Negative results are kept as results.
- **Criterion E (representation repair):** NOT SUPPORTED — strict-external dAUC −0.00194 /
  −0.00467 (paired DeLong CIs exclude zero, negative direction).
- **Temporal:** ECE 0.0716 → 0.2497 across PhreshPhish quarters while AUC stays flat.
- **Robustness:** P5/P6/P7 within the 15% criterion after repair; **P3 dot-segment retained as a
  known limitation** (global canonicalisation would degenerate the ERS target).

## Quick start

1. Open `notebook/paper_lock/paper_lock_pages/index.html` for the user-friendly,
   separated-pages presentation of all results.
2. Read `notebook/paper_lock/FINAL_REVISION_11_REPORT.md` for the paper-lock report.
3. The final paper tables (CSV + LaTeX) are in `notebook/paper_lock/final_paper_tables/`.
4. To re-execute the paper-lock section only: it is cheap (~seconds) and reads the executed
   outputs embedded in the notebook (no retraining). A full re-run of the research pipeline
   takes ~10 hours and is NOT required for the paper-lock outputs.
5. To run it on Kaggle (full ~10.7 h re-run, or the ~2 min paper-lock-only mode), follow
   **`KAGGLE_RUN_GUIDE.md`** — the notebook is Kaggle-native (default roots
   `/kaggle/input` + `/kaggle/working`, dataset discovery by recursive search, multi-fallback
   RAR extraction, and per-stage checkpoints against the 12 h session cap).
