# Reduced-scale execution of the locked Revision-11 notebook

This folder contains a **top-to-bottom machine-executed run of the complete 217-cell
`trac-phish-revision11_runned.ipynb` pipeline** (all stages, all gates, the executed
paper-lock section in LIVE mode) at the notebook's own **reduced scale**
(`TRAC_RUN_MODE=reduced`: deterministic subsample of at most 120,000 URLs per
dataset instead of the full ~800K/~666K corpora).

## Why reduced scale

The full 1.47M-URL pipeline was executed on Kaggle-class hardware (4 cores, large RAM,
~10.7 h). The sandbox used for this run has 2 vCPU, a hard 4 GiB memory cgroup (no
swap) and kills long-running processes at command boundaries, which is below the
full-scale pipeline's requirements. `TRAC_RUN_MODE=reduced` is the notebook's own
documented mode for exactly this machine class: every stage runs, every gate is
evaluated, every number is a real measurement on the deterministic subsample, and
every table states its scale. The **canonical full-scale locked artifacts remain
`notebook/trac-phish-revision11_runned.ipynb` and `notebook/paper_lock/`** — nothing
in this folder supersedes them.

## Files

- `trac-phish-revision11_reduced_executed.ipynb` — the executed notebook (all 217 cells,
  no errors, paper-lock section executed in live mode: `PL_MODE = live (full revision-11
  execution in memory)`; 238/238 executed sanity checks + 20/20 paper-lock checks).
- `reduced_scale_execution_results.zip` — the run's artifact tree `trac_phish_results/`
  (tables, figures, reports, metadata, manifests, models; the r7 checkpoint `cache/`
  is excluded). Re-extract anywhere to inspect any table produced by the run.

## Environment record

```json
{
  "executed_on": "Super Z sandbox (2 vCPU, 4 GiB cgroup, no swap)",
  "trac_run_mode": "reduced",
  "trac_n_jobs": 1,
  "max_rows_per_dataset": 120000,
  "duration_seconds": 2884.1,
  "peak_mem_mb": 3354.2
}
```

## Reproducing full scale

See `KAGGLE_RUN_GUIDE.md` at the repo root: upload both dataset archives as a private
Kaggle dataset, enable a CPU session with Internet, Save & Run All (~10.7 h reference).
