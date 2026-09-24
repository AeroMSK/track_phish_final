# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — bootstrap (dual-mode data access)
# PAPER-LOCK-R11
#
# Every number in the final paper-facing outputs comes from EITHER
#   (a) the LIVE in-memory objects of a complete revision-11 execution (full re-run mode), or
#   (b) the EXECUTED OUTPUTS embedded in this notebook by the full-scale revision-11 run
#       (paper-lock mode: the artifacts of the ~639-minute run are parsed from the stored cell
#       outputs - nothing is recomputed, nothing is hand-typed, nothing is fabricated).
#
# No new model is fitted here. No new hyperparameter search, no new CV folds, no larger SHAP
# sample, no new perturbation family, no new self-training round. This is FINAL PAPER POLISH:
# reporting code, metadata, and paper-facing tables/figures regenerated from computed objects.
# ===================================================================================================
PAPER_LOCK_ID = "PAPER-LOCK-R11"          # marker that also excludes these cells from re-parsing
import os, io, json, re, hashlib, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# display/Markdown shims: the paper-lock cells must also run under a plain `python` driver
try:
    display
except NameError:                                                     # plain-python execution fallback
    def display(*args, **kwargs):
        for a in args:
            try:
                print(a)
            except Exception:
                pass
try:
    from IPython.display import Markdown as _PL_Markdown
    Markdown = _PL_Markdown
except Exception:
    class Markdown(str):                                              # plain fallback: prints as text
        def __new__(cls, s):
            return super().__new__(cls, s)

# ---------- where the paper-lock artifacts go -----------------------------------------------------
PL_ROOT = Path(os.environ.get("TRAC_PL_OUT", str(Path.cwd() / "trac_phish_paper_lock")))
PL_TABLES = PL_ROOT / "final_paper_tables"
PL_FIGS = PL_ROOT / "final_figures"
PL_PAGES = PL_ROOT / "paper_lock_pages"
for _d in (PL_ROOT, PL_TABLES, PL_FIGS, PL_PAGES):
    _d.mkdir(parents=True, exist_ok=True)

# ---------- locate the canonical notebook (paper-lock parse source) --------------------------------
def _find_nb() -> Path:
    cands = [Path(os.environ.get("TRAC_NB_PATH", "")),
             Path.cwd() / "trac-phish-revision11_runned.ipynb",
             Path.cwd().parent / "notebook" / "trac-phish-revision11_runned.ipynb",
             Path("/home/z/my-project/track_phish_final/notebook/trac-phish-revision11_runned.ipynb")]
    for c in cands:
        try:
            if c and c.exists() and c.suffix == ".ipynb":
                return c
        except OSError:
            continue
    # Kaggle: a copy of the executed notebook attached as (or inside) a dataset is also a valid
    # parse source; the recursive search is bounded by the small mounted-dataset trees.
    for _root in (os.environ.get("TRAC_INPUT_ROOT", "/kaggle/input"),):
        try:
            for p in sorted(Path(_root).rglob("trac-phish-revision11_runned.ipynb")):
                return p
        except OSError:
            continue
    return None

PL_NB_PATH = _find_nb()
PL_LIVE = isinstance(globals().get("REPR_COMPARISON"), pd.DataFrame)
PL_MODE = "live (full revision-11 execution in memory)" if PL_LIVE else "paper-lock (parsed executed outputs)"
print(f"PAPER-LOCK DATA MODE: {PL_MODE}")
if not PL_LIVE:
    assert PL_NB_PATH is not None, ("paper-lock mode requires the executed notebook file "
                                    "(set TRAC_NB_PATH); no live objects are present")
    print(f"PAPER-LOCK PARSE SOURCE: {PL_NB_PATH}")
    print("  (the archived full-scale revision-11 run; no value below is recomputed from raw data)")

# ---------- raw-output extraction helpers (paper-lock mode) ---------------------------------------
_PL_NB = json.loads(PL_NB_PATH.read_text(encoding="utf-8")) if (PL_NB_PATH and PL_NB_PATH.exists()) else None

def _pl_cells():
    """Original executed cells only: paper-lock cells themselves are never re-parsed."""
    out = []
    for c in _PL_NB["cells"]:
        if c["cell_type"] != "code":
            continue
        if PAPER_LOCK_ID in "".join(c["source"]):
            continue
        out.append(c)
    return out

def _html_tables(cell):
    tabs = []
    for o in cell.get("outputs", []):
        data = o.get("data", {}) if o.get("output_type") in ("display_data", "execute_result") else {}
        html = data.get("text/html")
        if html:
            html = html if isinstance(html, str) else "".join(html)
            try:
                tabs += pd.read_html(io.StringIO(html))
            except Exception:
                pass
    return tabs

def _stream(cell):
    parts = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            t = o.get("text", "")
            parts.append(t if isinstance(t, str) else "".join(t))
    return "".join(parts)

def _cell_by_marker(marker: str):
    hits = [c for c in _pl_cells() if marker in "".join(c["source"])]
    if not hits:
        raise RuntimeError(f"paper-lock parse: no cell contains marker {marker!r}")
    return hits[-1]                      # last definition wins (matches notebook semantics)

def pl_table(marker: str, which: int = -1) -> pd.DataFrame:
    """Displayed table `which` (default: last) of the last cell containing `marker`."""
    t = _html_tables(_cell_by_marker(marker))[which].copy()
    if isinstance(t.columns, pd.MultiIndex):                      # flatten pivots: keep the named level
        t.columns = [next((str(l) for l in reversed(c) if not str(l).startswith("Unnamed")), str(c[-1]))
                     for c in t.columns]
    return t.loc[:, [c for c in t.columns if not str(c).startswith("Unnamed")]]

def _clean_pivot(df: pd.DataFrame, index_cols: list) -> pd.DataFrame:
    """Drop the artifact sub-header row produced when pandas flattens a displayed pivot."""
    df = df.loc[:, index_cols + [c for c in df.columns if c not in index_cols]]
    return df[~df[index_cols[0]].astype(str).isin(index_cols)].reset_index(drop=True)

def pl_stream(marker: str) -> str:
    return _stream(_cell_by_marker(marker))

def pl_json_blobs(marker: str):
    """Every JSON object literal printed to stdout by the last cell containing `marker`."""
    txt = pl_stream(marker)
    blobs, depth, start = [], 0, None
    for i, ch in enumerate(txt):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                try:
                    blobs.append(json.loads(txt[start:i + 1]))
                except Exception:
                    pass
    return blobs

# ---------- the paper-lock data namespace ----------------------------------------------------------
PL = {}

def _clean_dots(df: pd.DataFrame) -> pd.DataFrame:
    """Drop pandas-display truncation rows ('...')."""
    return df[~df.apply(lambda r: r.astype(str).eq("...").any(), axis=1)].reset_index(drop=True)

def _load(name: str, marker: str, which: int = -1, live_obj=None):
    """Prefer the live object of a full re-run; otherwise parse the executed output.

    live_obj is either the NAME of a global DataFrame produced by a live top-to-bottom execution,
    or a zero-arg callable returning that DataFrame (for live counterparts that are a pivot or a
    subset of a global). Parse mode (the archived full-scale run) is unchanged: every call site
    passes the same marker, so the parsed artifact stays byte-for-byte the same."""
    if PL_LIVE and live_obj is not None:
        obj = live_obj() if callable(live_obj) else globals().get(live_obj)
        if isinstance(obj, pd.DataFrame) and len(obj):
            PL[name] = obj
            return
        if _PL_NB is None:
            raise RuntimeError(f"paper-lock live mode: live object for {name!r} is missing or empty and "
                               f"no executed notebook is available to parse (marker={marker!r})")
    PL[name] = pl_table(marker, which)
    assert len(PL[name]), f"paper-lock: table {name} parsed empty (marker={marker!r}, which={which})"

# ---- foundation: dataset audit, external views, compatibility gate --------------------------------
_load("DATASET_AUDIT", "def _t1()", 2,                              # table01 dataset audit/provenance
      lambda: TABLES.get("table01_dataset_audit_provenance"))
_load("EXTERNAL_VIEWS", "EXTERNAL_POPULATIONS = pd.DataFrame", -1, "EXTERNAL_POPULATIONS")
_load("COMPAT_GATE", "GATE_TABLE = pd.DataFrame(gate_checks)", -1, "GATE_TABLE")   # unique: the Section-22B dataset-compatibility gate

# ---- representation / origin / criteria / ablations ----------------------------------------------
_load("REPR_COMPARISON", "REPR_COMPARISON = pd.DataFrame", -1, "REPR_COMPARISON")   # paired DeLong (Criterion E)
_load("ORIGIN_TABLE", "ORIGIN_ROWS, ORIGIN_IMP = [], {}", 0, "ORIGIN_TABLE")       # section 9R (post-promotion)
_load("HELDOUT", "HELDOUT_TABLE = pd.DataFrame", -1, "HELDOUT_TABLE")
_load("ABLATION", "ABL_ROWS", 0, "ABLATION_TABLE")
_load("REPR_TABLE", "REPR_TABLE = pd.DataFrame", 0, "REPR_TABLE")
# NOTE: the REPR_TABLE display was row-truncated by pandas (76 rows -> 10 + '...'); the displayed
# tail retains every F69-R-v3 row used here. Truncation rows are dropped; nothing is extrapolated.
if not PL_LIVE:
    PL["REPR_TABLE"] = _clean_dots(PL["REPR_TABLE"])

# ---- transfer / UDA ---------------------------------------------------------------------------------
# NOTE: the PHASE-2 display (cell 'PHASES 2 and 3 (revision 6)') is row-truncated by pandas and is
# therefore NOT used. M0/M5/M6 strict-external AUCs are read from the COMPLETE revision-8 comparison
# table (PHASES B + C, 16 rows) and M7 from the complete R10 attribution table.
_load("TRANSFER_COMPARE", "PHASES B + C (REVISION 8)", 3, "R8_BEFORE_AFTER")
if PL_LIVE and isinstance(globals().get("R10_ATTRIBUTION"), pd.DataFrame):
    PL["R10_ATTRIBUTION"] = R10_ATTRIBUTION.set_index("direction").T   # the layout the parse path restores
else:                                                                # transposed display -> restore layout
    _raw = _html_tables(_cell_by_marker("R10_ATTRIBUTION = pd.DataFrame"))[-1].copy()
    _raw.columns = ["metric", "GramBeddings -> PhreshPhish", "PhreshPhish -> GramBeddings"]
    _t = _raw[_raw["metric"] != "direction"].set_index("metric")
    PL["R10_ATTRIBUTION"] = _t.apply(pd.to_numeric, errors="coerce").where(_t.apply(pd.to_numeric, errors="coerce").notna(), _t)
assert {"M6 (revision 8)", "M7 (revision 10)", "bootstrap_ci_low", "bootstrap_ci_high"} <= set(PL["R10_ATTRIBUTION"].index)
_load("XFER_TABLE", "XFER_ROWS", 0, "XFER_TABLE")

# ---- ERS / DTS / statistics -------------------------------------------------------------------------
_load("ERS_EVAL", "ERS_EVAL = pd.DataFrame", 0, "ERS_EVAL")
_load("DTS_GATE_R6", "PHASE 6 (revision 6)", 0, "R6_DTS_TABLE")
_load("DTS_GATE_R7", "PHASE 4b (REVISION 7)", 1, "R7_DTS_TABLE")
_load("STRATA_RHO", "Phase 5.4 / 5.5", 2, "ERS_LEGACY_TABLE")

# ---- temporal / robustness ---------------------------------------------------------------------------
_load("TEMPORAL", "TEMPORAL_TABLE = pd.DataFrame", 0, "TEMPORAL_TABLE")
_load("TEMPORAL_XAI", "TEMPORAL_XAI_ROWS", 1, "TEMPORAL_XAI_TABLE")
_load("FLIP_R6", "R6_FLIP_ROWS", 0,
      lambda: R6_FLIP_TABLE.pivot_table(index=["run", "population", "family"], columns="model",
                                        values="prediction_flip_pct").round(2).reset_index())
if not PL_LIVE:
    PL["FLIP_R6"] = _clean_pivot(PL["FLIP_R6"], ["run", "population", "family"])
_load("ROBUST_R7", "PHASE 3 (REVISION 7)", 2,
      lambda: R7_FLIP_TABLE.pivot_table(index=["run", "family"], columns="model",
                                        values="prediction_flip_pct").round(2).reset_index())
if not PL_LIVE:
    PL["ROBUST_R7"] = _clean_pivot(PL["ROBUST_R7"], ["run", "family"])
_load("STRESS", "STRESS: Dict", 0, "STRESS_TABLE")

# ---- gate history / criteria --------------------------------------------------------------------------
_load("GATE_R6", "PHASE 10 (revision 6)", 0, "R6_GATE_TABLE")
_load("GATE_R7", "GATE_ROWS_R7", 0, "GATE_TABLE_R7")
_load("BLOCKERS_R7", "GATE_ROWS_R7", 2, "BLOCKER_TABLE")
_load("CRITERIA", "CRITERIA_TABLE = pd.DataFrame", -1, "CRITERIA_TABLE")

# ---- scalar evidence from stream text ------------------------------------------------------------------
if PL_LIVE and "CHECKS" in globals():
    _n_pass = sum(1 for c_ in CHECKS if c_[1])
    PL["SANITY_TEXT"] = f"{_n_pass}/{len(CHECKS)} checks passed."
    PL["SANITY_PASSED_N"] = _n_pass
else:
    _sanity = pl_stream("CHECKS: List[Tuple[str, bool, str]] = []")
    PL["SANITY_TEXT"] = _sanity
    _m = re.search(r"(\d+)/\1 checks passed", _sanity)
    PL["SANITY_PASSED_N"] = int(_m.group(1)) if _m else None
assert PL["SANITY_PASSED_N"] == 238, f"expected 238/238 executed sanity checks, got {PL['SANITY_PASSED_N']}"

# P1 gate v8 (invariant block): exact executed values from the JSON blob printed by PHASE A (rev 8)
_p1v8 = None
if PL_LIVE and isinstance(globals().get("P1_GATE_V8"), dict):
    _p1v8 = P1_GATE_V8
else:
    for _b in pl_json_blobs("PHASE A (REVISION 8)"):
        if _b.get("block_size") == 15 and "max_wasserstein" in _b and "domain_classifier_auc_after" in _b:
            _p1v8 = _b
assert _p1v8 is not None, "paper-lock: could not recover the executed Phase-A (rev-8) invariant-block gate"
PL["P1_GATE_V8"] = _p1v8

# Gate 2 (transfer) executed JSON and Gate 3 (95%) stream evidence
PL["GATE2_BLOBS"] = [P2_GATE] if (PL_LIVE and isinstance(globals().get("P2_GATE"), dict)) else \
                    [b for b in pl_json_blobs("PHASE E (REVISION 10)") if "by_direction" in b]
if PL_LIVE and isinstance(globals().get("P3_ACC_GATE"), dict):
    PL["GATE3_TEXT"] = "\n".join(
        f"PHASE 3 GATE [{_d}]: {'PASSED' if _v['passed'] else 'FAILED'} -- best multi-source "
        f"strict-external accuracy = {_v['best_external_accuracy']:.4f} "
        f"({_v['best_model']}, AUC {_v['best_external_roc_auc']:.4f}, n={_v['n_eval']:,})"
        for _d, _v in P3_ACC_GATE["by_direction"].items())
else:
    PL["GATE3_TEXT"] = "" if PL_LIVE else pl_stream("PHASE G (REVISION 11)")

print(f"paper-lock namespace loaded: {len(PL)} entries")
print(f"executed-run sanity checks: {PL['SANITY_PASSED_N']}/238 passed")
print(f"invariant block (F69-R-v3): max W = {_p1v8['max_wasserstein']:.4f} (gate <= 0.15), "
      f"domain-classifier AUC {_p1v8['domain_classifier_auc_before']:.4f} -> "
      f"{_p1v8['domain_classifier_auc_after']:.4f} (target <= 0.60)")
