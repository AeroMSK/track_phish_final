# KAGGLE_RUN_GUIDE — TRAC-Phish Revision 11

How to run the canonical notebook (`notebook/trac-phish-revision11_runned.ipynb`) on Kaggle.
The notebook is **Kaggle-native by design**: its default input/work roots are
`/kaggle/input` and `/kaggle/working` (both overridable via `TRAC_INPUT_ROOT` /
`TRAC_WORK_ROOT`), datasets are located by recursive search (no mount path is hard-coded),
and every expensive stage is checkpointed against the session time limit.

Two ways to run are supported:

| | Option A — full re-run | Option B — paper-lock only |
|---|---|---|
| What it does | Re-executes the entire research pipeline (~10.5 h) and regenerates every number | Regenerates only the final tables/figures/report (~2 min) from the executed outputs |
| Use when | You want a fresh end-to-end reproduction | You want the deliverables re-created without recompute |
| Kaggle time | One full session (12 h cap) | Minutes, CPU |

---

## 0. One-time setup (both options)

1. **Datasets.** On kaggle.com go to *Datasets → New Dataset* and upload the two archives
   from this repository's `Datasets/` folder (one private dataset holding both is fine —
   the notebook searches recursively, the dataset title does not matter):
   - `grambeddings_dataset_main.rar` (17.6 MB)
   - `phreshphish_url_only_2026.zip` (42.9 MB)

   Notes:
   - Kaggle auto-extracts uploaded ZIPs, so the PhreshPhish package is found directly.
   - The RAR is extracted **by the notebook itself** (it tries `unrar`, `7z`, `7za`, `7zz`,
     `unar`, `bsdtar`, then the `libarchive-c` Python binding, then `apt-get install`).
     Keep **Internet = ON** in the notebook settings so the fallbacks can install if needed.
   - Alternative that needs no RAR tooling at all: upload `grambeddings_dataset_main.rar`
     contents (`train.csv`, `test.csv`, `classes.txt`) as a ZIP — the notebook accepts
     pre-extracted files too.

2. **Notebook.** On kaggle.com go to *Code → New Notebook*, then
   *File → Import Notebook* and upload
   `notebook/trac-phish-revision11_runned.ipynb` (download it from this repository).

3. **Settings** (right panel):
   - *Accelerator*: **None** (CPU). All models deliberately run on CPU for bit-level
     reproducibility; a GPU does not help and Kaggle's GPU sessions are shorter.
   - *Internet*: **ON** (only needed for the RAR fallback and optional package installs —
     `xgboost`, `lightgbm`, `shap`, `tokenizers` are already pre-installed on Kaggle).

---

## Option A — full re-run (produces the final artifact end-to-end)

1. In the notebook: **+ Add Input → Your Work → Datasets** → attach the dataset from step 0.
2. **Save Version → Save & Run All (Commit)**. This runs headlessly for up to 12 h.
   - The reference full-scale execution took **~639 minutes (~10.7 h)**, which fits the
     12 h CPU session cap with ≈1.3 h margin. `TRAC_RUN_MODE` defaults to `full`, so no
     environment variable is needed.
   - You can close the browser; the commit run continues server-side and you get a
     notification when it finishes.
3. When the version completes, everything is under the **Output** tab:
   - `/kaggle/working/trac_phish_results/` — all intermediate tables, figures, models,
     metadata and the reproducibility manifest of the fresh run.
   - `/kaggle/working/trac_phish_paper_lock/` — the final paper-lock bundle:
     `FINAL_REVISION_11_REPORT.md`, `final_paper_tables/` (11 CSV + TEX pairs),
     `final_figures/` (5 figures, PNG + PDF), `paper_lock_pages/` (separated-pages HTML
     presentation, open `index.html`), `FINAL_MANIFEST_R11.json`, `final_abstract.md`,
     and `trac_phish_revision11_paper_lock.zip` (everything bundled).
   - The notebook itself (with fresh outputs) can be downloaded from the version's
     *Notebook* tab and pushed back to this repository.

### What to expect on a fresh run
- The final section (cells 207–216) auto-detects the live execution
  (`PAPER-LOCK DATA MODE: live (full revision-11 execution in memory)`) and builds every
  final table/figure from the in-memory result objects. The parse-from-archived-outputs
  mode is only used when the lock cells run without the pipeline above them.
- The run is seeded (`seed=42`) and deterministic per library version. If Kaggle's library
  versions differ from the reference environment, individual metrics can shift in late
  decimals; the notebook's **238 built-in sanity checks** and the paper-lock asserts
  (`238/238` and `20/20`) will fail loudly rather than emit inconsistent numbers.
- Gate outcomes are pre-registered; the mixed result profile (ERS stability supported /
  DTS not supported / Criterion E not supported / P3 limitation retained) is expected.

### If a session dies before finishing (resume, not restart)
Every expensive revision-7+ stage persists to `/kaggle/working/trac_phish_results/cache/`
(keyed by run scale + schema, so a reduced-mode artifact can never be picked up by a
full-scale run):
1. Before a risky long interactive session, or after a completed partial run, do
   **Save Version → Quick Save** — this preserves the current `/kaggle/working` as that
   version's output.
2. Start a new session of the same notebook, **+ Add Input → Your Work → Notebook**
   and attach the previous version's output, then paste this as the FIRST cell and run it
   once before *Run All*:

   ```python
   # OPTIONAL resume: restore the checkpoint cache from an attached previous version
   import shutil
   from pathlib import Path
   for src in Path("/kaggle/input").glob("*/trac_phish_results/cache"):
       dst = Path("/kaggle/working/trac_phish_results/cache")
       if not dst.exists():
           shutil.copytree(src, dst)
           print("cache restored from", src)
   ```

3. `Run All` — completed stages print `checkpoint HIT ...` and are skipped in seconds.
   Set `TRAC_FORCE_RECOMPUTE=1` only if you want to ignore every cached artifact.

---

## Option B — regenerate only the paper-lock deliverables (~2 minutes)

Use this to re-create the final tables/figures/report **without any recompute**: the lock
cells parse the executed outputs embedded in the canonical notebook.

1. Create a private Kaggle dataset containing the executed notebook file itself:
   `trac-phish-revision11_runned.ipynb` (5.6 MB).
2. Import the same notebook into a Kaggle notebook, attach that dataset, and execute
   **only cells 208–216** (the `PAPER-LOCK-R11` section). It prints
   `PAPER-LOCK DATA MODE: paper-lock (parsed executed outputs)` and finds the attached
   executed notebook automatically (it also honours `TRAC_NB_PATH` if you prefer to point
   at it explicitly).
3. The deliverables land in `/kaggle/working/trac_phish_paper_lock/` exactly as in
   Option A — no model is fitted, nothing is recomputed from raw data.

---

## Environment reference (as tested)

- Kaggle CPU session: 4 CPU cores, ~30 GB RAM, 12 h session cap, 20 GB `/kaggle/working`
  output cap — comfortably above this pipeline's needs (datasets are < 100 MB combined).
- Required Python packages: `xgboost`, `lightgbm`, `shap`, `tokenizers` (all pre-installed
  on Kaggle); optional: `tldextract` (documented fallback exists), `libarchive-c`
  (RAR fallback). The notebook auto-installs anything missing when Internet is ON.
- No GPU/TPU is used anywhere; `CANONICALISE_INPUT` stays `False` (enabling it globally
  is prohibited — it degenerates the ERS reliability target).

## Re-running the paper-lock section locally (not on Kaggle)

The tools live in `notebook/paper_lock/tools/` of this repository:
`rebuild_final_notebook.py` re-executes cells 207–216 in parse mode and re-merges them into
the canonical notebook; `test_live_mode_lock.py` validates the live-mode wiring (the code
path a fresh top-to-bottom run takes). Their absolute paths are from the development
environment — see the README in that folder.
