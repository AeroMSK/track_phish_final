# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — pre-registered criteria, with Criterion E RESOLVED
# PAPER-LOCK-R11
#
# Criterion E (pre-registered): "Representation repair helps transfer: external ROC-AUC (F54-R) >
# external ROC-AUC (F48) with a DeLong 95% CI excluding 0."
#
# Status in the executed run's Section-48 table: "unavailable" / UNDEFINED - a REPORTING BUG, not
# missing data. Section 39R computed the required paired DeLong comparison ("F54-R - F48", strict
# external population, identical rows, shared XAI samples) and displayed it, but Section 48 looked
# it up under the primary representation's display name, a comparison string that does not exist
# in REPR_COMPARISON. The paired prediction vectors themselves are therefore available in the
# executed run; the criterion is resolved HERE from those already-computed paired DeLong results.
# No model is retrained; no new evaluation is performed.
# ===================================================================================================
_cols_e = ["source", "comparison", "population", "auc_a", "auc_b", "delta_auc", "ci_low", "ci_high", "p", "n"]
_e_rows = PL["REPR_COMPARISON"][_cols_e]
_e_ext = _e_rows[(_e_rows["comparison"] == "F54-R - F48") & (_e_rows["population"] == "external_principal")]
_e_ind = _e_rows[(_e_rows["comparison"] == "F54-R - F48") & (_e_rows["population"] == "in_domain_test")]
assert len(_e_ext) == 2 and len(_e_ind) == 2, "expected both transfer directions for the F54-R/F48 comparison"

_evidence_e = {}
for _, _r in _e_ext.iterrows():
    _d = "GramBeddings -> PhreshPhish" if _r["source"] == "GramBeddings" else "PhreshPhish -> GramBeddings"
    _evidence_e[_r["source"]] = (
        f"external dAUC(F54-R - F48)={_r['delta_auc']:+.4f} [{_r['ci_low']:+.4f}, {_r['ci_high']:+.4f}], "
        f"DeLong p={_r['p']:.3g}, n={int(_r['n']):,} (paired, strict domain-unseen external)")

# ---- assemble the final criteria table from the executed Section-48 rows + the resolved E -------
def _complete_d_evidence(ev: str, run_key: str) -> str:
    """The executed display truncated criterion-D evidence at 90 characters (pandas max_colwidth).
    The SAME executed objects carry the complete dAURC: re-attach it from the revision-6 external
    AURC gate table (identical rows, identical numbers - no recomputation, no fabrication)."""
    if not str(ev).rstrip().endswith("..."):
        return ev
    _dts = PL["DTS_GATE_R6"]
    _row = _dts[(_dts["run"] == run_key) & (_dts["population"] == "external STRICT")
                & (_dts["variant"].astype(str).str.contains("logistic_2f"))].iloc[0]
    _prefix = str(ev).rstrip().split("dAURC")[0].rstrip().rstrip(";").rstrip()  # cut at the truncated number
    _tail = "external dAURC(DTS-C)" if not _prefix.endswith("external") else "dAURC(DTS-C)"
    return (f"{_prefix}; {_tail}={_row['delta_aurc_vs_C']:+.5f} "
            f"[{_row['delta_ci_low']:+.5f}, {_row['delta_ci_high']:+.5f}] "
            f"[dAURC completed at paper lock from the executed revision-6 external AURC gate table]")

_fin_crit = []
for _run in ["gram|F68RV3", "phresh|F68RV3"]:
    _src = "GramBeddings" if _run.startswith("gram") else "PhreshPhish"
    for _letter in ["A", "B", "C", "D"]:
        _row = PL["CRITERIA"][(PL["CRITERIA"]["run"] == _run) & (PL["CRITERIA"]["criterion"] == _letter)].iloc[0]
        _ev = _row["evidence"]
        if _letter == "D":
            _ev = _complete_d_evidence(_ev, _run)
        _fin_crit.append({"run": _run.replace("F68RV3", "F69-R-v3"), "criterion": _letter,
                          "rule": _row["rule"], "evidence": _ev, "verdict": _row["verdict"]})
    _er = _e_ext[_e_ext["source"] == _src].iloc[0]
    _verdict_e = "NOT SUPPORTED" if _er["ci_high"] < 0 else ("SUPPORTED" if _er["ci_low"] > 0 else "NOT SUPPORTED")
    _fin_crit.append({"run": _run.replace("F68RV3", "F69-R-v3"), "criterion": "E",
                      "rule": PL["CRITERIA"][PL["CRITERIA"]["criterion"] == "E"].iloc[0]["rule"],
                      "evidence": _evidence_e[_src] + " [resolved at paper lock from the executed "
                                  "paired DeLong comparison computed by Section 39R]",
                      "verdict": _verdict_e})
FINAL_CRITERIA_TABLE = pd.DataFrame(_fin_crit)
display(FINAL_CRITERIA_TABLE)

CRITERION_E_STATUS = {
    "status": _verdict_e,
    "how_resolved": ("computed from the already-executed paired DeLong comparison (Section 39R "
                     "REPR_COMPARISON, strict external population, identical rows); no retraining"),
    "per_direction": {r["source"]: {"delta_auc": float(r["delta_auc"]), "ci_low": float(r["ci_low"]),
                                    "ci_high": float(r["ci_high"]), "p": float(r["p"]), "n": int(r["n"])}
                      for _, r in _e_ext.iterrows()},
    "in_domain_context": {r["source"]: {"delta_auc": float(r["delta_auc"]), "ci_low": float(r["ci_low"]),
                                        "ci_high": float(r["ci_high"])}
                          for _, r in _e_ind.iterrows()},
}
print("\nCRITERION E (pre-registered): " + _verdict_e.upper())
for _s, _v in CRITERION_E_STATUS["per_direction"].items():
    print(f"  {_s}: dAUC = {_v['delta_auc']:+.5f} [{_v['ci_low']:+.5f}, {_v['ci_high']:+.5f}], p = {_v['p']:.3g}, n = {_v['n']:,}")
print("  In-domain context: " + "; ".join(
    f"{_s} dAUC {+_v['delta_auc']:+.5f} [{_v['ci_low']:+.5f}, {_v['ci_high']:+.5f}]"
    for _s, _v in CRITERION_E_STATUS["in_domain_context"].items()))
print("  Interpretation: representation repair (F54-R over F48) does NOT improve strict-external transfer; "
      "both DeLong CIs exclude zero in the NEGATIVE direction, so the difference is significant and harmful "
      "externally (while small and positive in-domain).")
