# Paper-lock tools (development provenance)

These are the exact scripts used to build and verify the final section (cells 207–216) of
`notebook/trac-phish-revision11_runned.ipynb`:

| File | Purpose |
|---|---|
| `final_cells/cell_207…cell_216.py` | The source of each final-section cell (the notebook's cells 207–216 are built from these) |
| `rebuild_final_notebook.py` | Re-executes cells 207–216 in parse mode with a real Jupyter kernel and re-merges them into the canonical notebook; verifies 20/20 paper-lock checks |
| `test_live_mode_lock.py` | Executes the lock cells in **live mode** (the code path a fresh top-to-bottom Kaggle run takes, with no parse source available) using live globals reconstructed from the executed outputs; verifies the full lock section passes 20/20 without any parse fallback |

Note: the scripts contain absolute paths from the development environment
(`/home/z/my-project/...`); adjust them if you run the tools elsewhere. See
`KAGGLE_RUN_GUIDE.md` at the repository root for how to run the notebook on Kaggle.
