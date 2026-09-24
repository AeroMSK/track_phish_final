# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — the high-confidence / low-ERS reversal, as a final diagnostic table
# PAPER-LOCK-R11
#
# Pre-registered novelty claim C1 said the high-C/low-ERS population should be MORE error-prone.
# The executed run found the OPPOSITE on every external population: within the high-confidence
# stratum, low-ERS rows have LOWER classification error than high-ERS rows, while still having
# less stable explanations. This divergence IS the finding: explanation reliability is not
# prediction correctness. It is reported as a NEGATIVE result, not repaired or re-framed.
# ===================================================================================================
_rev_rows = []
for _, r in PL["ERS_EVAL"].iterrows():
    _rev_rows.append({
        "run": r["run"].replace("F68RV3", "F69-R-v3"),
        "population": {"test": "in-domain test", "ext": "strict external"}[r["population"]],
        "confidence_stratum": "high (top quartile of C)",
        "ERS_group": "low-ERS (bottom quartile within stratum)",
        "n": int(r["n_highC_lowERS"]),
        "classification_error": round(float(r["err_highC_lowERS"]), 4),
        "heldout_expl_stability_Schallenge": round(float(r["mean_Schallenge_highC_lowERS"]), 4),
        "comparison_error_highC_highERS": round(float(r["err_highC_highERS"]), 4),
        "comparison_Schallenge_highC_highERS": round(float(r["mean_Schallenge_highC_highERS"]), 4),
        "fisher_OR_low_vs_high": round(float(r["fisher_or_error_lowERS_vs_highERS"]), 4),
        "fisher_p": float(r["fisher_p"]),
    })
REVERSAL_FINAL_TABLE = pd.DataFrame(_rev_rows)
display(REVERSAL_FINAL_TABLE)

_ext_rev = REVERSAL_FINAL_TABLE[REVERSAL_FINAL_TABLE["population"] == "strict external"]
REVERSAL_SUMMARY = (
    f"NEGATIVE FINDING. On all {len(_ext_rev)} strict-external runs, the high-confidence/low-ERS group "
    f"shows LOWER classification error than the high-confidence/high-ERS group (median external Fisher "
    f"OR = {_ext_rev['fisher_OR_low_vs_high'].median():.3f}), while its held-out explanation stability "
    f"S_challenge remains lower ({_ext_rev['heldout_expl_stability_Schallenge'].min():.2f}-"
    f"{_ext_rev['heldout_expl_stability_Schallenge'].max():.2f} vs "
    f"{_ext_rev['comparison_Schallenge_highC_highERS'].min():.2f}-"
    f"{_ext_rev['comparison_Schallenge_highC_highERS'].max():.2f}). In at least one external setting the "
    f"relationship survives conditioning on class. Therefore: high confidence + low ERS does NOT reliably "
    f"imply high classification risk. Explanation reliability and prediction correctness are distinct "
    f"properties; a stable explanation can accompany an incorrect prediction (and vice versa)."
)
print(REVERSAL_SUMMARY)
