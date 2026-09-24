# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — the paper-ready research summary, abstract, positioning,
# findings and limitations. Every number is read from the executed objects loaded above.
# PAPER-LOCK-R11
# ===================================================================================================
_fp = lambda x, d=4: f"{x:.{d}f}"

FINAL_SUMMARY_SECTIONS = {}

FINAL_SUMMARY_SECTIONS["title"] = "Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection"

FINAL_SUMMARY_SECTIONS["research_question"] = (
    "Does explanation-derived reliability provide information beyond calibrated prediction confidence "
    "under genuine cross-corpus distribution shift - and does that information translate into improved "
    "selective classification decisions? The executed evidence answers the two halves differently: ERS "
    f"predicts held-out explanation stability (all run configurations Holm-significant; ERS beats confidence "
    f"on {_n_ers_beats_c_ext}/4 strict-external runs), but it does NOT add selective-classification decision "
    "value beyond calibrated confidence (DTS 0/12 external cells).")

FINAL_SUMMARY_SECTIONS["datasets"] = (
    f"GramBeddings ({GRAM_ROWS:,} rows after cleaning; anchor corpus, balanced) and PhreshPhish "
    f"({PHRESH_ROWS:,} rows; primary external corpus, URL-only package with official temporal split). "
    f"Exact/canonical/eTLD+1 overlap controlled; strict domain-unseen external views of "
    f"{int(GP['records']):,} (G->P) and {int(PG['records']):,} (P->G) records; natural views retained as "
    f"secondary (contamination {float(GP['contamination_pct_of_natural']):.2f}% / "
    f"{float(PG['contamination_pct_of_natural']):.2f}%). LegitPhish is retired from the primary path.")

FINAL_SUMMARY_SECTIONS["representation"] = (
    f"F69-R-v3 = F54-R (54 robust URL features) + 15 label-free domain-invariant features = 69 features "
    f"(internal key F68RV3 preserved for checkpoint compatibility). The invariant block passes its pinned "
    f"gate: max normalised Wasserstein {_p1['max_wasserstein']:.4f} (<= 0.15), block domain-classifier AUC "
    f"{_p1['domain_classifier_auc_before']:.4f} -> {_p1['domain_classifier_auc_after']:.4f} (<= 0.60). "
    f"Dataset-origin separability stays high (ROC-AUC {ORIGIN_F69:.4f}): the corpora remain genuinely different, "
    f"which is the motivation for the cross-corpus protocol, not a defect to repair.")

FINAL_SUMMARY_SECTIONS["model_family"] = (
    "Structured URL features (F48 / F54-R / F69-R-v3) with XGBoost / LightGBM / RandomForest challengers; "
    "character n-gram and word-token TF-IDF experts for the transfer branch; isotonic probability calibration; "
    "no HTML, page content, target, lang or date is ever used as model input.")

FINAL_SUMMARY_SECTIONS["transfer_protocol"] = (
    f"M0 source-only (zero-shot) -> M6 analogue-selected expert fusion (UDA) -> M7 word expert + self-training "
    f"(UDA; unlabeled target TRAIN, source-VAL guard, no target VAL/TEST labels). Strict-external ROC-AUC: "
    f"G->P {_fp(M0_BY_DIR['GramBeddings -> PhreshPhish'])} -> {_fp(M6_BY_DIR['GramBeddings -> PhreshPhish'])} -> "
    f"{_fp(M7_BY_DIR['GramBeddings -> PhreshPhish'])} [95% boot {_fp(M7_CI['GramBeddings -> PhreshPhish'][0])}, "
    f"{_fp(M7_CI['GramBeddings -> PhreshPhish'][1])}]; P->G {_fp(M0_BY_DIR['PhreshPhish -> GramBeddings'])} -> "
    f"{_fp(M6_BY_DIR['PhreshPhish -> GramBeddings'])} -> {_fp(M7_BY_DIR['PhreshPhish -> GramBeddings'])} "
    f"[95% boot {_fp(M7_CI['PhreshPhish -> GramBeddings'][0])}, {_fp(M7_CI['PhreshPhish -> GramBeddings'][1])}]. "
    f"Semi-supervised multi-source (a SEPARATE benchmark, not zero-shot/UDA) reaches "
    f"{_fp(_g3['GramBeddings -> PhreshPhish']['accuracy'])} / {_fp(_g3['PhreshPhish -> GramBeddings']['accuracy'])} "
    f"accuracy at the 95% gate - near-threshold in one direction.")

FINAL_SUMMARY_SECTIONS["xai_protocol"] = (
    "TreeSHAP on the three model families, intervention-based faithfulness (F), identity-preserving perturbation "
    "stability (S), cross-model consensus (M); E0 = (F·S·M)^(1/3) with confidence deliberately excluded; "
    "SHAP sample n=2,500 per population, 400 interaction rows; challenge families held out.")

FINAL_SUMMARY_SECTIONS["ers_definition"] = (
    "ERS = calibrated mapping g(E0) of the explanation-only evidence score; fitted (isotonic, validation only) "
    "against the redesigned non-circular target y_rel = 0.5 * S_challenge + 0.5 * S_calib_P3 with P1/P2 removed. "
    "Confidence C is excluded from ERS by design. DTS = h(C, ERS) is the separate decision layer.")

FINAL_SUMMARY_SECTIONS["gate_results"] = "\n".join(
    f"- **{_r['phase']}**: {_r['result']}. {_r['numerical_evidence']}"
    for _, _r in FINAL_GATE_TABLE_R11.iterrows())

FINAL_SUMMARY_SECTIONS["positive_findings"] = (
    f"1. Dataset-origin shift is substantial and quantified (origin AUC {ORIGIN_F69:.4f}), making the "
    f"cross-corpus evaluation a genuine shift test.\n"
    f"2. A label-free domain-invariant block reduces source-identifying signal (max W "
    f"{_p1['max_wasserstein']:.4f}; block domain AUC {_p1['domain_classifier_auc_after']:.4f}).\n"
    f"3. UDA materially improves bidirectional cross-corpus ranking (M7 vs M0: "
    f"+{M7_BY_DIR['GramBeddings -> PhreshPhish'] - M0_BY_DIR['GramBeddings -> PhreshPhish']:.4f} / "
    f"+{M7_BY_DIR['PhreshPhish -> GramBeddings'] - M0_BY_DIR['PhreshPhish -> GramBeddings']:.4f} AUC).\n"
    f"4. ERS predicts held-out explanation stability (all configurations Holm-significant; "
    f"pre-fit target gate 3/4).\n"
    f"5. ERS outperforms calibrated confidence as a predictor of explanation stability on "
    f"{_n_ers_beats_c_ext}/4 evaluated external runs.\n"
    f"6. Explanation reliability and correctness can diverge - a stable explanation can accompany an "
    f"incorrect prediction (the reversal, characterised structurally).")

FINAL_SUMMARY_SECTIONS["negative_findings"] = (
    f"1. ERS does not add statistically supported information about correctness beyond confidence "
    f"(in-domain LRT p_holm {_fmt_p(_p_holm['gram|F68RV3'])} / {_fmt_p(_p_holm['phresh|F68RV3'])}).\n"
    f"2. DTS does not improve selective classification risk over confidence on ANY external cell "
    f"({DTS_WINS}/{DTS_CELLS}; gram AURC {_fp(DTS_F69['gram|F68RV3']['conf'], 5)} vs "
    f"{_fp(DTS_F69['gram|F68RV3']['dts'], 5)}; phresh {_fp(DTS_F69['phresh|F68RV3']['conf'], 5)} vs "
    f"{_fp(DTS_F69['phresh|F68RV3']['dts'], 5)}).\n"
    f"3. Criterion E: representation repair does NOT improve strict-external transfer "
    f"({CRITERION_E_STATUS['per_direction']['GramBeddings']['delta_auc']:+.5f} / "
    f"{CRITERION_E_STATUS['per_direction']['PhreshPhish']['delta_auc']:+.5f} dAUC, CIs excluding 0 in the "
    f"negative direction).\n"
    f"4. P3 dot-segment robustness remains unresolved ({P3_MAX_R7:.2f}% best repaired flip vs 15% criterion).\n"
    f"5. Calibration degrades sharply under temporal shift (ECE {TEMP_ECE_Q3:.4f} -> {TEMP_ECE_Q4:.4f}).")

FINAL_SUMMARY_SECTIONS["limitations"] = (
    "1. P3 (dot-segment) robustness sensitivity remains unresolved; RFC 3986 canonicalisation neutralises it "
    "mechanically but degenerates the ERS target, so it is retained as a representation-level limitation.\n"
    f"2. Dataset origin is highly detectable (ROC-AUC {ORIGIN_F69:.3f}); cross-corpus results are bounded by genuine shift.\n"
    "3. ERS does not improve selective classification risk beyond calibrated confidence.\n"
    f"4. One ERS-target configuration (phresh|F69-R-v3, rho {_rho_runs.get('phresh|F68RV3', float('nan')):.4f}) does not pass the 0.10 pre-fit bar.\n"
    f"5. The 95% semi-supervised accuracy criterion is missed in one direction "
    f"({min(v['accuracy'] for v in _g3.values()):.4f} vs 0.95).\n"
    f"6. PhreshPhish temporal calibration deteriorates (ECE {TEMP_ECE_Q3:.4f} -> {TEMP_ECE_Q4:.4f}), with a co-occurring prevalence "
    "shift and only two adequately-powered quarters.\n"
    "7. UDA uses unlabeled target TRAIN data and is not pure zero-shot; the semi-supervised 95% benchmark "
    "additionally uses target TRAIN labels and target VAL selection.\n"
    "8. The study is URL-only and does not evaluate HTML/content features.\n"
    "9. Explanation reliability does not imply prediction correctness.")

FINAL_SUMMARY_SECTIONS["claims"] = "\n".join(
    f"- {r['claim_id']}: {r['claim']} — **{r['status']}**" for _, r in FINAL_CLAIMS_TABLE.iterrows())

FINAL_SUMMARY_SECTIONS["prohibited_claims"] = (
    "ERS improves classification; DTS improves decision-making; ERS is better than confidence (as a decision "
    "signal); ERS is a better uncertainty estimate; high-confidence/low-ERS always indicates a dangerous "
    "prediction; M7 is zero-shot; the model achieves >=95% external accuracy in both directions; the "
    "representation is fully domain invariant; the robustness problem has been solved; the framework is the "
    "first to study explanation stability; the framework is the first to study cross-dataset phishing "
    "transfer; the framework is deployment-ready.")

FINAL_SUMMARY_SECTIONS["reproducibility"] = (
    f"Full-scale executed run (~639 min), seed 42, dataset SHA-256 verified, {PL['SANITY_PASSED_N']}/238 "
    f"sanity checks passed; paper-lock outputs document which results are reused versus recomputed "
    f"(FINAL_MANIFEST_R11.json); all 109 pre-paper-lock code cells keep their original executed outputs.")

# ---------------- the final abstract (evidence-aligned) ---------------------------------------------
ABSTRACT_R11 = f"""**Abstract (revision 11, paper lock).** Phishing-URL detectors deployed across corpora face
genuine distribution shift: we measure that two independent URL corpora are separable by URL structure alone
(origin ROC-AUC {_fp(ORIGIN_F69)}), so cross-corpus evaluation is a real stress test rather than a replication.
We study GramBeddings and PhreshPhish ({GRAM_ROWS:,} and {PHRESH_ROWS:,} cleaned URLs) under a
leakage-resistant protocol - URL-only features, exact/canonical/eTLD+1 overlap control, domain-disjoint
splits and a strict domain-unseen external view - and evaluate (i) domain-aware transfer, (ii) calibrated
prediction, and (iii) explanation reliability via TreeSHAP-based faithfulness, stability and cross-model
consensus combined into an explanation-only score E0 = (F·S·M)^(1/3) whose calibrated form (ERS) deliberately
excludes prediction confidence. Unsupervised domain adaptation over unlabeled target-TRAIN data raises
strict-external ROC-AUC from {_fp(M0_BY_DIR['GramBeddings -> PhreshPhish'])} to
{_fp(M7_BY_DIR['GramBeddings -> PhreshPhish'])} (GramBeddings -> PhreshPhish) and from
{_fp(M0_BY_DIR['PhreshPhish -> GramBeddings'])} to {_fp(M7_BY_DIR['PhreshPhish -> GramBeddings'])}
(PhreshPhish -> GramBeddings). ERS predicts held-out explanation stability (all run configurations
Holm-significant) and outperforms calibrated confidence as a predictor of explanation stability on the
evaluated external runs. However, ERS adds no statistically supported information about classification
correctness beyond calibrated confidence under the pre-registered model, and a decision trust score combining
confidence and ERS does not reduce selective-classification risk below confidence alone on any evaluated
external setting ({DTS_WINS}/{DTS_CELLS} cells). Explanation reliability and prediction correctness
therefore diverge - high confidence with low ERS does not reliably indicate classification risk. Temporal
analysis shows calibration deteriorating sharply (ECE {TEMP_ECE_Q3:.4f} -> {TEMP_ECE_Q4:.4f}) while ranking
stays comparatively stable. We conclude that explanation-derived reliability is informative about
explanations but should not replace calibrated confidence for selective classification decisions."""

POSITIONING_PARAGRAPH = f"""Phishing detectors can retain useful discrimination while their confidence,
explanations, and explanation reliability behave differently under cross-corpus and temporal shift. This
study therefore evaluates whether explanation-derived reliability adds information beyond calibrated
prediction confidence using a strict, leakage-resistant, domain-unseen protocol. The results show that ERS
is associated with held-out explanation stability and can outperform confidence as a predictor of
explanation stability on the evaluated external runs. However, ERS does not improve selective classification
risk over confidence. Thus explanation reliability should not be interpreted as a proxy for prediction
correctness. Cross-corpus domain adaptation improves transfer (M7 UDA), while temporal analysis exposes
substantial calibration degradation."""

FINDINGS_FINAL = [
    f"FINDING 1: Dataset-origin shift is substantial (origin ROC-AUC {ORIGIN_F69:.3f}).",
    "FINDING 2: A label-free domain-invariant representation can reduce source-identifying signal "
    f"(max W {_p1['max_wasserstein']:.4f}; block domain AUC {_p1['domain_classifier_auc_after']:.4f}).",
    "FINDING 3: UDA improves bidirectional cross-corpus ranking "
    f"(G->P {M0_BY_DIR['GramBeddings -> PhreshPhish']:.4f} -> {M7_BY_DIR['GramBeddings -> PhreshPhish']:.4f}; "
    f"P->G {M0_BY_DIR['PhreshPhish -> GramBeddings']:.4f} -> {M7_BY_DIR['PhreshPhish -> GramBeddings']:.4f}).",
    "FINDING 4: ERS predicts held-out explanation stability on most evaluated runs (all Test-A associations "
    "Holm-significant; pre-fit target gate 3/4).",
    "FINDING 5: ERS outperforms calibrated confidence as a predictor of explanation stability on the "
    f"evaluated external runs ({_n_ers_beats_c_ext}/4).",
    "FINDING 6: ERS does not add statistically supported information about prediction correctness beyond "
    "confidence (pre-registered in-domain model).",
    f"FINDING 7: DTS does not improve selective classification risk over confidence ({DTS_WINS}/{DTS_CELLS} "
    "external cells; all CIs include zero or are positive).",
    "FINDING 8: Explanation reliability and classification correctness can diverge (the high-C/low-ERS "
    "reversal is a genuine negative finding).",
    f"FINDING 9: Temporal shift substantially worsens calibration (ECE {TEMP_ECE_Q3:.4f} -> {TEMP_ECE_Q4:.4f} "
    "with flat AUC; prevalence confound noted).",
    f"FINDING 10: Robustness remains incomplete because P3 continues to produce a high prediction-flip rate "
    f"({P3_MAX_R7:.2f}% best repaired vs 15% criterion).",
]

display(Markdown(ABSTRACT_R11))
display(Markdown("\n**Paper positioning.** " + POSITIONING_PARAGRAPH))
display(Markdown("\n**What we found.**\n" + "\n".join("- " + f.split(": ", 1)[1] for f in FINDINGS_FINAL)))

(PL_ROOT / "final_abstract.md").write_text(ABSTRACT_R11 + "\n\n**Paper positioning.** " +
                                           POSITIONING_PARAGRAPH + "\n", encoding="utf-8")
print(f"final abstract + positioning written to {PL_ROOT / 'final_abstract.md'}")
