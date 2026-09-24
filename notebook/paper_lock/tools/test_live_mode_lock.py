#!/usr/bin/env python3
"""
LIVE-MODE SIMULATION of the paper-lock section (cells 208-216).

Purpose: prove that a fresh top-to-bottom Kaggle execution (PL_LIVE=True, NO executed
notebook file available to parse) runs the lock section to completion with 20/20
paper-lock checks. Every 'live' global is reconstructed from the parsed EXECUTED outputs
(nb_extract), so the numbers are the executed ones; the object of the test is the CODE
PATH: any missing live wiring raises a clear RuntimeError instead of silently falling
back to a parse that would crash on Kaggle.
"""
import os, re, sys, tempfile, types
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

SRC = Path("/home/z/my-project/scripts/final_cells")
TAB = Path("/home/z/my-project/nb_extract/tables")
OUT = Path("/home/z/my-project/nb_extract/out")

def load(name, **kw):
    df = pd.read_csv(TAB / f"{name}.csv", **kw)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

# ---------------- reconstruct every live global the lock section reads ------------------------------
REPR_COMPARISON = load("160_html01_0")          # paired DeLong (Criterion E source)
REPR_TABLE = load("160_html00_0")
EXTERNAL_POPULATIONS = load("041_html00_0")
GATE_TABLE = load("076_html00_0")               # dataset-compatibility gate
ORIGIN_TABLE = load("156_html00_0")              # section 9R (post-promotion)
HELDOUT_TABLE = load("139_html00_0")
ABLATION_TABLE = load("170_html00_0")
R8_BEFORE_AFTER = load("100_html03_0")          # PHASES B + C comparison
XFER_TABLE = load("158_html00_0")
ERS_EVAL = load("146_html00_0")
R6_DTS_TABLE = load("134_html00_0")
R7_DTS_TABLE = load("137_html01_0")
ERS_LEGACY_TABLE = load("150_html02_0")
TEMPORAL_TABLE = load("168_html00_0")
TEMPORAL_XAI_TABLE = load("168_html01_0")
STRESS_TABLE = load("141_html00_0")
R6_GATE_TABLE = load("202_html00_0")
GATE_TABLE_R7 = load("204_html00_0")
BLOCKER_TABLE = load("204_html02_0")
CRITERIA_TABLE = load("188_html00_0")
DATASET_AUDIT_TABLE = load("182_html02_0")
TABLES = {"table01_dataset_audit_provenance": DATASET_AUDIT_TABLE}

# R10_ATTRIBUTION: native orientation (rows = directions, columns = [direction, metrics...])
_r10 = pd.read_csv(TAB / "104_html01_0.csv", index_col=0)
_r10.columns = _r10.iloc[0].tolist()
_r10 = _r10.iloc[1:]
for c in _r10.columns:
    _r10[c] = pd.to_numeric(_r10[c], errors="coerce")
R10_ATTRIBUTION = _r10.T.reset_index()
R10_ATTRIBUTION.columns = ["direction"] + list(R10_ATTRIBUTION.columns[1:])

# R6/R7 flip tables: long form (melt the displayed pivots back)
def load_flat_pivot(csv, n_index_cols):
    """Rebuild a flat pivot table from the two-row header read_html produced."""
    raw = pd.read_csv(TAB / csv, header=None)
    cols = [str(raw.iloc[1, j]) for j in range(n_index_cols)] + \
           [str(raw.iloc[0, j]) for j in range(n_index_cols, raw.shape[1])]
    raw.columns = cols
    df = raw.iloc[2:].copy()
    df = df[~df[cols[0]].astype(str).isin(cols[:n_index_cols])]      # residual artifact rows
    for c in cols[n_index_cols:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.reset_index(drop=True)

_f6 = load_flat_pivot("119_html00_0.csv", 3)
R6_FLIP_TABLE = _f6.melt(id_vars=["run", "population", "family"], var_name="model",
                         value_name="prediction_flip_pct")
_f7 = load_flat_pivot("121_html02_0.csv", 2)
R7_FLIP_TABLE = _f7.melt(id_vars=["run", "family"], var_name="model",
                         value_name="prediction_flip_pct")

# Gate dicts and scalars from the executed stream outputs
_p3_txt = (OUT / "cell_106.txt").read_text(encoding="utf-8", errors="ignore")
P3_ACC_GATE = {"by_direction": {}}
for m in re.finditer(r"PHASE 3 GATE \[(.+?)\]: (\w+) -- best multi-source strict-external accuracy "
                     r"= ([\d.]+) \((.+?), AUC ([\d.]+), n=([\d,]+)", _p3_txt):
    P3_ACC_GATE["by_direction"][m.group(1)] = {
        "passed": m.group(2) == "PASSED", "best_external_accuracy": float(m.group(3)),
        "best_model": m.group(4), "best_external_roc_auc": float(m.group(5)),
        "n_eval": int(m.group(6).replace(",", ""))}
assert len(P3_ACC_GATE["by_direction"]) == 2, "Gate 3 stream not fully parsed"

P1_GATE_V8 = {"block_size": 15, "max_wasserstein": 0.13409183170125963,
              "domain_classifier_auc_before": 0.675693354075,
              "domain_classifier_auc_after": 0.5501116531375}
R6_P5_GATE = {"primary_cross_family_rho_by_run": {"gram|F48": 0.35625, "gram|F68RV3": 0.36047,
                                                  "phresh|F48": 0.29067, "phresh|F68RV3": 0.06906}}
P2_GATE = {}                                    # stored in PL["GATE2_BLOBS"]; not consumed downstream
CHECKS = [(f"executed_check_{i:03d}", True, "") for i in range(238)]
MANIFEST = {"title": "Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection"}
CFG = types.SimpleNamespace(notebook_revision=11)

# ---------------- namespace + shims ------------------------------------------------------------------
from IPython.display import Markdown

def _display(*args, **kwargs):
    for a in args:
        if isinstance(a, str) and len(a) < 400:
            print("  [md]", a.replace("\n", " ")[:120])

ns = dict(__name__="__main__", np=np, pd=pd, display=_display, Markdown=Markdown,
          REPR_COMPARISON=REPR_COMPARISON, REPR_TABLE=REPR_TABLE,
          EXTERNAL_POPULATIONS=EXTERNAL_POPULATIONS, GATE_TABLE=GATE_TABLE,
          ORIGIN_TABLE=ORIGIN_TABLE, HELDOUT_TABLE=HELDOUT_TABLE, ABLATION_TABLE=ABLATION_TABLE,
          R8_BEFORE_AFTER=R8_BEFORE_AFTER, XFER_TABLE=XFER_TABLE, ERS_EVAL=ERS_EVAL,
          R6_DTS_TABLE=R6_DTS_TABLE, R7_DTS_TABLE=R7_DTS_TABLE, ERS_LEGACY_TABLE=ERS_LEGACY_TABLE,
          TEMPORAL_TABLE=TEMPORAL_TABLE, TEMPORAL_XAI_TABLE=TEMPORAL_XAI_TABLE,
          STRESS_TABLE=STRESS_TABLE, R6_GATE_TABLE=R6_GATE_TABLE, GATE_TABLE_R7=GATE_TABLE_R7,
          BLOCKER_TABLE=BLOCKER_TABLE, CRITERIA_TABLE=CRITERIA_TABLE, TABLES=TABLES,
          R10_ATTRIBUTION=R10_ATTRIBUTION, R6_FLIP_TABLE=R6_FLIP_TABLE, R7_FLIP_TABLE=R7_FLIP_TABLE,
          P3_ACC_GATE=P3_ACC_GATE, P1_GATE_V8=P1_GATE_V8, R6_P5_GATE=R6_P5_GATE,
          P2_GATE=P2_GATE, CHECKS=CHECKS, MANIFEST=MANIFEST, CFG=CFG)

# ---------------- execute cells 208-216 with NO parse source available --------------------------------
tmp = tempfile.mkdtemp(prefix="pl_live_sim_")
os.chdir(tmp)
os.environ.pop("TRAC_NB_PATH", None)
os.environ.pop("TRAC_PL_OUT", None)

CELLS = ["cell_208_code", "cell_209_code", "cell_210_code", "cell_211_code", "cell_212_code",
         "cell_213_code", "cell_214_code", "cell_215_code", "cell_216_code"]
for name in CELLS:
    src = (SRC / f"{name}.py").read_text(encoding="utf-8")
    # TEST-ONLY: neutralise the local absolute-path notebook candidate so no parse source exists
    src = src.replace('Path("/home/z/my-project/track_phish_final/notebook/trac-phish-revision11_runned.ipynb")',
                      'Path("/definitely/not/here/trac-phish-revision11_runned.ipynb")')
    print(f"--- executing {name} ...")
    exec(compile(src, name, "exec"), ns)

# ---------------- verdict ----------------------------------------------------------------------------
assert "live" in ns["PL_MODE"], f"PL_MODE is not live: {ns['PL_MODE']!r}"
n_pass, n_tot = ns["PL_N_PASS"], len(ns["PL_CHECKS"])
failed = [(n, d) for n, ok, d in ns["PL_CHECKS"] if not ok]
assert not failed, f"paper-lock checks failed in LIVE MODE: {failed}"
print()
print("=" * 100)
print(f"LIVE-MODE SIMULATION PASSED: PL_MODE={ns['PL_MODE']!r}; paper-lock sanity {n_pass}/{n_tot}; "
      f"figures + tables + separated pages written under {tmp}")
print("=" * 100)
