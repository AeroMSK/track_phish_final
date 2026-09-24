# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — final paper-facing tables (CSV + TEX) and the paper-lock manifest
# PAPER-LOCK-R11
# ===================================================================================================
def _tex_escape(s):
    return (str(s).replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
            .replace("$", "\\$").replace("#", "\\#").replace("_", "\\_")
            .replace("{", "\\{").replace("}", "\\}").replace("~", "\\textasciitilde{}")
            .replace("^", "\\textasciicircum{}"))

def _write_tex(df, path, caption):
    cols = [str(c) for c in df.columns]
    esc_cols = [_tex_escape(c) for c in cols]
    lines = ["% auto-generated at paper lock (revision 11) - do not edit by hand",
             "\\begin{table}[htbp]", "\\centering", "\\footnotesize",
             f"\\caption{{{_tex_escape(caption)}}}",
             f"\\begin{{tabular}}{{{'l' * min(len(cols), 3)}{'p{2.6cm}' * max(len(cols) - 3, 0)}}}", "\\toprule",
             " & ".join(esc_cols) + " \\\\", "\\midrule"]
    for _, r in df.iterrows():
        lines.append(" & ".join(_tex_escape(v) for v in r.tolist()) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    path.write_text("\n".join(lines), encoding="utf-8")

def save_final_table(df, name, caption):
    df.to_csv(PL_TABLES / f"{name}.csv", index=False)
    _write_tex(df, PL_TABLES / f"{name}.tex", caption)
    return name

FINAL_TABLE_NAMES = []

# ---- 1. final_dataset_summary -----------------------------------------------------------------------
_da = PL["DATASET_AUDIT"].set_index("item")
_ev = PL["EXTERNAL_VIEWS"]
_ds_rows = []
for ds, disp in [("GramBeddings", "GramBeddings"), ("PhreshPhish", "PhreshPhish")]:
    _ds_rows.append({"dataset": disp, "raw_records": _da.loc["actual records read", ds],
                     "final_rows": _da.loc["final_rows", ds],
                     "final_phishing": _da.loc["final_phishing", ds],
                     "final_benign": _da.loc["final_benign", ds],
                     "unique_registered_domains": _da.loc["unique registered domains", ds],
                     "train": _da.loc["train records (phishing %)", ds],
                     "val": _da.loc["val records (phishing %)", ds],
                     "test": _da.loc["test records (phishing %)", ds],
                     "label_source": _da.loc["label source", ds]})
for _, r in _ev.iterrows():
    _ds_rows.append({"dataset": f"external view — {r['direction']}", "raw_records": "",
                    "final_rows": f"{r['view']}: {int(r['records']):,} ({'PRIMARY' if r['primary'] else 'secondary'})",
                    "final_phishing": int(r["phishing"]), "final_benign": int(r["benign"]),
                    "unique_registered_domains": "",
                    "train": f"phishing {r['phishing_pct']:.1f}%", "val": "", "test": "",
                    "label_source": f"contamination removed vs natural: {r['contamination_pct_of_natural']:.2f}%"})
FINAL_DATASET_SUMMARY = pd.DataFrame(_ds_rows)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_DATASET_SUMMARY, "final_dataset_summary",
                                          "Final dataset summary (revision 11): corpora, partitions and external views"))

# ---- 2. final_compatibility_summary ------------------------------------------------------------------
_cg = PL["COMPAT_GATE"].copy()
FINAL_TABLE_NAMES.append(save_final_table(_cg, "final_compatibility_summary",
                                          "Final dataset-compatibility gate (pre-registered, executed run)"))

# ---- 3. final_transfer_results -------------------------------------------------------------------------
_d = "GramBeddings -> PhreshPhish"; _dr = "PhreshPhish -> GramBeddings"
_tr = PL["TRANSFER_COMPARE"].set_index(["direction", "model"])
_rows = []
for _dir, _label in [(_d, "G->P"), (_dr, "P->G")]:
    _rows.append({"direction": _label, "model": "M0 source-only (zero-shot)", "type": "zero-shot",
                  "strict_external_roc_auc": round(float(_tr.loc[(_dir, "M0 source-only F68-R"), "rev8_this_run_F68RV3"]), 4),
                  "accuracy_at_95_gate": "", "notes": "frozen source artifacts only"})
    _rows.append({"direction": _label, "model": "M6 fusion (UDA)", "type": "UDA",
                  "strict_external_roc_auc": round(M6_BY_DIR[_dir], 4), "accuracy_at_95_gate": "",
                  "notes": "analogue-selected expert fusion, unlabeled target TRAIN"})
    _rows.append({"direction": _label, "model": "M7 word expert + self-training (UDA)", "type": "UDA",
                  "strict_external_roc_auc": round(M7_BY_DIR[_dir], 4), "accuracy_at_95_gate": "",
                  "notes": f"95% bootstrap CI [{M7_CI[_dir][0]:.4f}, {M7_CI[_dir][1]:.4f}]; no target VAL/TEST labels used for fitting"})
    _g = _g3[_dir]
    _rows.append({"direction": _label, "model": _g["model"], "type": "semi-supervised multi-source",
                  "strict_external_roc_auc": round(_g["auc"], 4),
                  "accuracy_at_95_gate": round(_g["accuracy"], 4),
                  "notes": f"Gate-3 best; target TRAIN labels + target VAL selection (n={_g['n']:,})"})
FINAL_TRANSFER_RESULTS = pd.DataFrame(_rows)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_TRANSFER_RESULTS, "final_transfer_results",
                                          "Final cross-corpus transfer results (strict domain-unseen external)"))

# ---- 4. final_ers_results --------------------------------------------------------------------------------
_ers = PL["ERS_EVAL"].copy()
_ers["run"] = _ers["run"].str.replace("F68RV3", "F69-R-v3", regex=False)
_keep = ["run", "population", "n", "error_rate", "A_spearman_ERS_vs_Schallenge", "A_spearman_C_vs_Schallenge",
         "B_lrt_stat", "B_ers_coef", "err_highC_lowERS", "err_highC_highERS",
         "mean_Schallenge_highC_lowERS", "mean_Schallenge_highC_highERS", "fisher_or_error_lowERS_vs_highERS", "fisher_p"]
FINAL_ERS_RESULTS = _ers[_keep].round(4)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_ERS_RESULTS, "final_ers_results",
                                          "Final ERS evaluation: explanation-stability association, correctness increment, "
                                          "and the high-C/low-ERS reversal"))

# ---- 5. final_dts_results -----------------------------------------------------------------------------------
_dg6 = PL["DTS_GATE_R6"].copy()
_dg6 = _dg6[_dg6["population"] == "external STRICT"].drop(columns=["population"])
_dg6["run"] = _dg6["run"].str.replace("F68RV3", "F69-R-v3", regex=False)
_dg7 = PL["DTS_GATE_R7"].copy()
_dg7["run"] = _dg7["run"].str.replace("F68RV3", "F69-R-v3", regex=False)
FINAL_DTS_RESULTS = pd.concat([_dg6.assign(source="revision-6 external AURC gate").round(5),
                               _dg7.assign(source="revision-7 external AURC gate").round(5)],
                              ignore_index=True)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_DTS_RESULTS, "final_dts_results",
                                          "Final DTS evaluation on strict-external populations: no variant beats "
                                          "calibrated confidence with CI excluding zero (0/12 cells)"))

# ---- 6. final_temporal_calibration -----------------------------------------------------------------------------
_tp = PL["TEMPORAL"].copy()
_tp["run"] = _tp["run"].str.replace("F68RV3", "F69-R-v3", regex=False)
_tx = PL["TEMPORAL_XAI"].copy()
_tx["run"] = _tx["run"].str.replace("F68RV3", "F69-R-v3", regex=False)
FINAL_TEMPORAL = _tp[["run", "slice", "n", "phishing_pct", "accuracy", "roc_auc", "brier", "ece"]].round(4)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_TEMPORAL, "final_temporal_calibration",
                                           "Final temporal analysis (GramBeddings -> PhreshPhish strict external): "
                                           "ECE degradation with flat ranking; prevalence confound noted"))

# ---- 7. final_robustness ---------------------------------------------------------------------------------------
_rb_rows = []
_fl = PL["FLIP_R6"]
for fam, label in [("P3_dot_segment", "P3 dot-segment"), ("P5_subdomain_insertion", "P5 subdomain insertion"),
                   ("P6_path_padding", "P6 path padding"), ("P7_query_padding", "P7 query padding")]:
    _sub = _fl[_fl["family"] == fam]
    _rb_rows.append({"family": label,
                     "baseline_max_flip_pct": float(_sub["baseline (rev 5 model)"].astype(float).max()),
                     "augmented_max_flip_pct": float(_sub["augmented (6A+6B)"].astype(float).max()),
                     "rev7_repaired_max_flip_pct": float(PL["ROBUST_R7"][PL["ROBUST_R7"]["family"] == fam]
                                                         ["rev7 + hard-negative mining"].astype(float).max())
                     if len(PL["ROBUST_R7"][PL["ROBUST_R7"]["family"] == fam]) else np.nan,
                     "criterion_pct": 15.0})
FINAL_ROBUSTNESS = pd.DataFrame(_rb_rows).round(2)
FINAL_TABLE_NAMES.append(save_final_table(FINAL_ROBUSTNESS, "final_robustness",
                                           "Final robustness summary: max prediction-flip rate per perturbation family "
                                           "across repair stages (P3 fails the 15% criterion and is retained as a limitation)"))

# ---- 8-11. gate table, claim matrix, criteria, reversal ----------------------------------------------------------
FINAL_TABLE_NAMES.append(save_final_table(FINAL_GATE_TABLE_R11, "final_gate_table",
                                          "FINAL_GATE_TABLE_R11: the authoritative revision-11 gate table"))
FINAL_TABLE_NAMES.append(save_final_table(FINAL_CLAIMS_TABLE, "final_claim_matrix",
                                          "FINAL_CLAIMS_TABLE: authoritative claim matrix for paper drafting"))
FINAL_TABLE_NAMES.append(save_final_table(FINAL_CRITERIA_TABLE, "final_criteria_table",
                                          "Final pre-registered criteria A-E, with Criterion E resolved from the executed "
                                          "paired DeLong comparison"))
FINAL_TABLE_NAMES.append(save_final_table(REVERSAL_FINAL_TABLE, "final_reversal_diagnostic",
                                          "High-confidence/low-ERS reversal diagnostic (negative finding)"))

print(f"final paper-facing tables written: {len(FINAL_TABLE_NAMES)}")
for n in FINAL_TABLE_NAMES:
    print(f"  {n}.csv / {n}.tex")

# ---- final_paper_tables.zip (the FINAL paper-facing export set, separate from the historical archive) -----------
with zipfile.ZipFile(PL_ROOT / "final_paper_tables.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for n in FINAL_TABLE_NAMES:
        zf.write(PL_TABLES / f"{n}.csv", arcname=f"final_paper_tables/{n}.csv")
        zf.write(PL_TABLES / f"{n}.tex", arcname=f"final_paper_tables/{n}.tex")
    for f in PL_FIGS.glob("*.png"):
        zf.write(f, arcname=f"final_paper_tables/figures/{f.name}")
    for f in PL_FIGS.glob("*.pdf"):
        zf.write(f, arcname=f"final_paper_tables/figures/{f.name}")
print(f"final_paper_tables.zip written ({len(FINAL_TABLE_NAMES)} CSV + TEX pairs + figures)")

# ---- FINAL_MANIFEST_R11: the paper-lock reproducibility manifest -------------------------------------------------
FINAL_MANIFEST_R11 = {
    "notebook_revision": 11,
    "paper_lock": True,
    "title": "Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection",
    "superseded_working_title": "Beyond Prediction Confidence: Reliability-Calibrated Explanations for Phishing URL Detection",
    "datasets": {
        "GramBeddings": {"final_rows": GRAM_ROWS, "sha256_prefix": str(_da.loc["sha256 (prefix)", "GramBeddings"]),
                         "role": "anchor / development corpus"},
        "PhreshPhish": {"final_rows": PHRESH_ROWS, "sha256_prefix": str(_da.loc["sha256 (prefix)", "PhreshPhish"]),
                        "role": "primary external corpus (URL-only package)"},
    },
    "final_primary_representation": {
        "paper_name": "F69-R-v3", "internal_key": "F68RV3 (preserved for checkpoint compatibility)",
        "F54R_features": 54, "invariant_block": 15, "total": 69,
        "definition": "F69-R-v3 = F54-R (54 features) + 15 domain-invariant features = 69 features",
        "invariant_block_gate": {"max_wasserstein": _p1["max_wasserstein"],
                                  "domain_classifier_auc_before": _p1["domain_classifier_auc_before"],
                                  "domain_classifier_auc_after": _p1["domain_classifier_auc_after"]}},
    "external_evaluation": {
        "primary_view": "strict_domain_unseen",
        "strict_external_records": {"GramBeddings -> PhreshPhish": int(GP["records"]),
                                     "PhreshPhish -> GramBeddings": int(PG["records"])},
        "contamination_removed_from_natural_pct": {"GramBeddings -> PhreshPhish": float(GP["contamination_pct_of_natural"]),
                                                    "PhreshPhish -> GramBeddings": float(PG["contamination_pct_of_natural"])}},
    "executed_run_provenance": {
        "run_mode": "full scale, ~639 minutes, 238/238 sanity checks passed",
        "seed": 42,
        "dataset_protocol": "trac-dataset-v2.0", "canonicalization_version": "trac-canon-v1.0",
        "split": "GramBeddings domain-disjoint 70/15/15; PhreshPhish official partitions preserved",
        "calibration": "Stage-A held-out validation (isotonic selected); Stage-B cross-fitted TRAIN+VAL",
        "thresholds": "source-validation MCC (operating point A) and min-FPR s.t. recall>=0.95 (point B)",
        "uda": "M7 = word expert + analogue-selected rank fusion + 2 self-training rounds on unlabeled target TRAIN; "
                "source-VAL non-inferiority guard (margin 0.02); no target VAL/TEST label used for fitting",
        "ers": "E0=(F*S*M)^(1/3), confidence excluded by design; target y_rel = 0.5*S_challenge + 0.5*S_calib_P3 "
               "(P1/P2 removed); isotonic calibrator fitted on validation only",
        "dts": "logistic_2f [logit C, logit ERS] fitted on source-validation XAI sample (n=2500), grouped 5-fold CV; "
               "no target label used (revision-7 prior variant is transductive over unlabeled external scores - disclosed)",
        "xai": "TreeSHAP samples n=2500 per population (6 populations), 400 interaction rows, 3 models per run",
        "perturbations": "P1/P2/P3/P4/P4B identity-preserving; P5-P7 neutral-label structural; P8/P9 adversarial stress"},
    "paper_lock_ledger": {
        "reused_from_executed_revision_11_run": [
            "all dataset/overlap/split artifacts", "all trained models and predictions", "all transfer/UDA results (M0/M5/M6/M7)",
            "all TreeSHAP/faithfulness/stability/consensus results", "ERS/DTS evaluations and AURC gates",
            "temporal analysis", "robustness flip tables", "statistical test registry", "238/238 sanity checks"],
        "recomputed_cheaply_during_paper_lock": [
            "Criterion E: read from the executed paired DeLong comparison (Section 39R output); no retraining",
            "final gate table / claim matrix / criteria table: reassembled from executed result objects",
            "final figures 1-5: rendered from executed result objects",
            "final paper tables (CSV+TEX) and this manifest"],
        "new_experiments_added": "none (compute constraint respected: no new model families, no hyperparameter "
                                 "searches, no extra CV folds, no larger SHAP samples, no new perturbation "
                                 "families, no extra self-training rounds, no new full-dataset ablations)"},
    "figures": PL_FIGURE_FILES,
    "final_tables": FINAL_TABLE_NAMES,
}
(PL_ROOT / "FINAL_MANIFEST_R11.json").write_text(json.dumps(FINAL_MANIFEST_R11, indent=2, default=str),
                                                 encoding="utf-8")
print(f"FINAL_MANIFEST_R11.json written to {PL_ROOT}")
display(pd.DataFrame([{"item": "notebook_revision", "value": 11},
                      {"item": "final representation", "value": "F69-R-v3 = 54 + 15 = 69 features"},
                      {"item": "new experiments added", "value": "none (paper lock only)"},
                      {"item": "criterion E", "value": CRITERION_E_STATUS["status"] + " (resolved from cached results)"}]))
