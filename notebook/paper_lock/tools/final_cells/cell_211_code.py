# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — FINAL_CLAIMS_TABLE (the authoritative claim matrix)
# PAPER-LOCK-R11
# ===================================================================================================
# ---- live-safe evidence values (in parse mode these are read from the same loaded objects and
# ---- reproduce the executed evidence strings exactly; in live mode they track the fresh run) ----
def _fmt_p(p: float) -> str:
    """Render a p-value the way the executed evidence did (1.0, otherwise 3 decimals)."""
    return f"{p:.1f}" if p >= 0.9995 else f"{p:.3f}"

_p_holm = {}
for _rk in ("gram|F68RV3", "phresh|F68RV3"):
    _ev_b = str(PL["CRITERIA"][(PL["CRITERIA"]["criterion"] == "B") & (PL["CRITERIA"]["run"] == _rk)]
                .iloc[0]["evidence"])
    _p_holm[_rk] = float(re.search(r"p_holm\s*=\s*([\d.]+)", _ev_b).group(1))

_ers_ext = PL["ERS_EVAL"][PL["ERS_EVAL"]["population"] == "ext"]
_r48 = _ers_ext[_ers_ext["run"] == "gram|F48"].iloc[0]

CLAIM_ROWS = [
    {"claim_id": "C1", "claim": "Dataset-origin shift is substantial: the two corpora are strongly "
     "separable from URL structure alone, so cross-corpus evaluation represents genuine distribution "
     "shift (not label leakage).",
     "evidence": f"origin ROC-AUC {ORIGIN_F48:.4f} (F48) / {ORIGIN_F69:.4f} (F69-R-v3), n=40,000 per corpus TRAIN; top discriminator R_is_https",
     "status": "SUPPORTED",
     "allowed_paper_wording": "the corpora are highly distinguishable from URL structure alone, which bounds any source-trained detector and motivates the domain-unseen protocol",
     "prohibited_overclaim": "dataset-origin separability implies label leakage; or that removing top features would 'fix' the shift"},
    {"claim_id": "C2", "claim": "A label-free domain-invariant representation can reduce "
     "source-identifying signal.",
     "evidence": (f"selected 15-feature block: max normalised Wasserstein {_p1['max_wasserstein']:.4f} "
                  f"(<= 0.15); block domain-classifier AUC {_p1['domain_classifier_auc_before']:.4f} -> "
                  f"{_p1['domain_classifier_auc_after']:.4f} (target <= 0.60)"),
     "status": "SUPPORTED",
     "allowed_paper_wording": "the selected feature block has substantially reduced domain-identifying signal",
     "prohibited_overclaim": "the representation is fully domain invariant; the datasets are interchangeable after projection"},
    {"claim_id": "C3", "claim": "UDA improves cross-corpus discrimination.",
     "evidence": (f"M7 vs M0 strict-external ROC-AUC: G->P {M0_BY_DIR['GramBeddings -> PhreshPhish']:.4f} -> "
                  f"{M7_BY_DIR['GramBeddings -> PhreshPhish']:.4f}; P->G {M0_BY_DIR['PhreshPhish -> GramBeddings']:.4f} -> "
                  f"{M7_BY_DIR['PhreshPhish -> GramBeddings']:.4f}; M7 uses unlabeled target TRAIN only "
                  f"(word expert + fusion + 2 self-training rounds, source-VAL guard)"),
     "status": "SUPPORTED",
     "allowed_paper_wording": "unsupervised domain adaptation materially improves bidirectional cross-corpus ranking",
     "prohibited_overclaim": "M7 is zero-shot; UDA solves cross-corpus transfer; target labels were used"},
    {"claim_id": "C4", "claim": "ERS predicts held-out explanation stability.",
     "evidence": ("Test A significant on all four run configurations (in-domain and external, Holm-adjusted); "
                  f"pre-fit ERS-target gate rho(E0, y_rel) > 0.10 on {_n_rho_pass}/4 runs "
                  f"(phresh|F69-R-v3 = {_rho_runs.get('phresh|F68RV3', float('nan')):.4f} below the 0.10 bar)"),
     "status": "SUPPORTED across most evaluated runs (target-construction gate 3/4)",
     "allowed_paper_wording": "ERS is associated with held-out explanation stability across most evaluated configurations",
     "prohibited_overclaim": "ERS universally predicts explanation stability on every run configuration"},
    {"claim_id": "C5", "claim": "ERS adds correctness information beyond confidence.",
     "evidence": ("pre-registered in-domain LRT (Error ~ C vs Error ~ C + ERS + CxERS): "
                  f"p_holm = {_fmt_p(_p_holm['gram|F68RV3'])} (gram|F69-R-v3), "
                  f"{_fmt_p(_p_holm['phresh|F68RV3'])} (phresh|F69-R-v3); external associations are "
                  "significant but reflect the reliability/correctness divergence, and do not translate "
                  "into decision value"),
     "status": "NOT SUPPORTED",
     "allowed_paper_wording": "ERS did not provide statistically supported incremental information about classification correctness beyond calibrated confidence under the preregistered model",
     "prohibited_overclaim": "ERS improves classification; ERS is a better uncertainty estimate; the in-domain negative result should be hidden behind the external association"},
    {"claim_id": "C6", "claim": "DTS improves selective classification risk over confidence.",
     "evidence": (f"{DTS_WINS}/{DTS_CELLS} external DTS variant-run cells beat confidence with the 95% "
                  f"paired-bootstrap CI excluding 0; gram|F69-R-v3 AURC {DTS_F69['gram|F68RV3']['conf']:.5f} "
                  f"(confidence) vs {DTS_F69['gram|F68RV3']['dts']:.5f} (DTS); phresh|F69-R-v3 "
                  f"{DTS_F69['phresh|F68RV3']['conf']:.5f} vs {DTS_F69['phresh|F68RV3']['dts']:.5f}"),
     "status": "NOT SUPPORTED",
     "allowed_paper_wording": "calibrated confidence remained the stronger signal for selective classification risk in the evaluated external settings",
     "prohibited_overclaim": "DTS improves decision-making; a localized/stratum win generalises to a global claim"},
    {"claim_id": "C7", "claim": "Explanation reliability and prediction correctness can diverge "
     "(high-confidence/low-ERS does not reliably imply high classification risk).",
     "evidence": ("external error rates in the high-confidence stratum are LOWER for low-ERS than for "
                  f"high-ERS on all {len(_ers_ext)} external runs (e.g. gram|F48: "
                  f"{float(_r48['err_highC_lowERS']):.4f} vs {float(_r48['err_highC_highERS']):.4f}; "
                  f"Fisher OR {float(_r48['fisher_or_error_lowERS_vs_highERS']):.3f}), "
                  "the reversal survives conditioning on class, while low-ERS still means less stable "
                  f"explanations (mean S_challenge {_ers_ext['mean_Schallenge_highC_lowERS'].min():.2f}-"
                  f"{_ers_ext['mean_Schallenge_highC_lowERS'].max():.2f} vs "
                  f"{_ers_ext['mean_Schallenge_highC_highERS'].min():.2f}-"
                  f"{_ers_ext['mean_Schallenge_highC_highERS'].max():.2f})"),
     "status": "SUPPORTED / OBSERVED REVERSAL (negative finding)",
     "allowed_paper_wording": "explanation reliability and prediction correctness are distinct properties that can diverge; a stable explanation can accompany an incorrect prediction",
     "prohibited_overclaim": "high-confidence/low-ERS always indicates a dangerous prediction; low-ERS implies safe predictions"},
    {"claim_id": "C8", "claim": "Calibration degrades under temporal shift.",
     "evidence": (f"gram|F69-R-v3 strict-external ECE {TEMP_ECE_Q3:.4f} (2025Q3) -> {TEMP_ECE_Q4:.4f} "
                  f"(2025Q4) with ROC-AUC flat ({TEMP_AUC_Q3:.4f} -> {TEMP_AUC_Q4:.4f}); phishing prevalence "
                  f"{PREV_Q3:.1f}% -> {PREV_Q4:.1f}% (co-occurring prevalence shift; two adequately-powered quarters)"),
     "status": "SUPPORTED (with prevalence confound noted)",
     "allowed_paper_wording": "calibration deteriorates substantially under temporal shift while ranking is comparatively stable",
     "prohibited_overclaim": "the degradation is purely temporal; it generalises beyond two quarters or beyond the gram->phresh direction"},
    {"claim_id": "C9", "claim": "All robustness transformations are stable.",
     "evidence": (f"P3 dot-segment max flip {P3_MAX_BASE:.2f}% baseline -> {P3_MAX_AUG:.2f}% augmented -> "
                  f"{P3_MAX_R7:.2f}% revision-7 repaired (criterion 15%); P5/P6/P7 max flip "
                  f"{P567_MAX_AUG:.2f}% after augmentation (within criterion); RFC 3986 canonicalisation "
                  f"neutralises P3 (~0% flip) but degenerates the ERS target, so it is not enabled"),
     "status": "NOT SUPPORTED (P3 remains a representation-level sensitivity)",
     "allowed_paper_wording": "robustness is incomplete: P5/P6/P7 are within the criterion after repair; P3 remains a known limitation of the raw URL representation",
     "prohibited_overclaim": "the robustness problem has been solved; canonicalisation should be globally enabled without cost"},
    {"claim_id": "C10", "claim": "F54-R representation repair conclusively improves strict-external "
     "transfer over F48.",
     "evidence": ("resolved at paper lock from the executed paired DeLong comparison: G->P dAUC "
                  f"{CRITERION_E_STATUS['per_direction']['GramBeddings']['delta_auc']:+.5f} "
                  f"[{CRITERION_E_STATUS['per_direction']['GramBeddings']['ci_low']:+.5f}, "
                  f"{CRITERION_E_STATUS['per_direction']['GramBeddings']['ci_high']:+.5f}]; P->G dAUC "
                  f"{CRITERION_E_STATUS['per_direction']['PhreshPhish']['delta_auc']:+.5f} "
                  f"[{CRITERION_E_STATUS['per_direction']['PhreshPhish']['ci_low']:+.5f}, "
                  f"{CRITERION_E_STATUS['per_direction']['PhreshPhish']['ci_high']:+.5f}] (both CIs exclude 0, negative)"),
     "status": "NOT SUPPORTED (was reported 'unavailable' due to a lookup bug; now computed from cached results)",
     "allowed_paper_wording": "representation repair did not improve strict-external transfer; the effect is small and positive in-domain but significantly negative externally",
     "prohibited_overclaim": "F54-R improves external transfer; the 'unavailable' verdict should be kept despite recoverable evidence"},
]
FINAL_CLAIMS_TABLE = pd.DataFrame(CLAIM_ROWS)
display(FINAL_CLAIMS_TABLE[["claim_id", "claim", "status"]])
print("\nclaim statuses:")
for _, r in FINAL_CLAIMS_TABLE.iterrows():
    print(f"  {r['claim_id']}: {r['status']}")
