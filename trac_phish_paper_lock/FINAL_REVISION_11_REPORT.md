# FINAL REVISION 11 REPORT — PAPER LOCK
## Cross-Corpus Transfer and Explanation Reliability in Phishing URL Detection

**Research question.** Does explanation-derived reliability provide information beyond calibrated prediction confidence under genuine cross-corpus distribution shift - and does that information translate into improved selective classification decisions? The executed evidence answers the two halves differently: ERS predicts held-out explanation stability (all run configurations Holm-significant; ERS beats confidence on 4/4 strict-external runs), but it does NOT add selective-classification decision value beyond calibrated confidence (DTS 0/12 external cells).

**Contribution 1 — leakage-resistant cross-corpus evaluation.** GramBeddings (799,565 rows after cleaning; anchor corpus, balanced) and PhreshPhish (666,300 rows; primary external corpus, URL-only package with official temporal split). Exact/canonical/eTLD+1 overlap controlled; strict domain-unseen external views of 126,116 (G->P) and 118,390 (P->G) records; natural views retained as secondary (contamination 24.96% / 1.29%). LegitPhish is retired from the primary path.

**Contribution 2 — cross-corpus transfer.** M0 source-only (zero-shot) -> M6 analogue-selected expert fusion (UDA) -> M7 word expert + self-training (UDA; unlabeled target TRAIN, source-VAL guard, no target VAL/TEST labels). Strict-external ROC-AUC: G->P 0.7712 -> 0.8297 -> 0.8739 [95% boot 0.8721, 0.8758]; P->G 0.7430 -> 0.8139 -> 0.8243 [95% boot 0.8221, 0.8266]. Semi-supervised multi-source (a SEPARATE benchmark, not zero-shot/UDA) reaches 0.9438 / 0.9558 accuracy at the 95% gate - near-threshold in one direction.

**Contribution 3 — explanation reliability analysis.** ERS = calibrated mapping g(E0) of the explanation-only evidence score; fitted (isotonic, validation only) against the redesigned non-circular target y_rel = 0.5 * S_challenge + 0.5 * S_calib_P3 with P1/P2 removed. Confidence C is excluded from ERS by design. DTS = h(C, ERS) is the separate decision layer.

**Final representation.** F69-R-v3 = F54-R (54 robust URL features) + 15 label-free domain-invariant features = 69 features (internal key F68RV3 preserved for checkpoint compatibility). The invariant block passes its pinned gate: max normalised Wasserstein 0.1341 (<= 0.15), block domain-classifier AUC 0.6757 -> 0.5501 (<= 0.60). Dataset-origin separability stays high (ROC-AUC 0.9291): the corpora remain genuinely different, which is the motivation for the cross-corpus protocol, not a defect to repair.

**Final model family.** Structured URL features (F48 / F54-R / F69-R-v3) with XGBoost / LightGBM / RandomForest challengers; character n-gram and word-token TF-IDF experts for the transfer branch; isotonic probability calibration; no HTML, page content, target, lang or date is ever used as model input.

**Final XAI protocol.** TreeSHAP on the three model families, intervention-based faithfulness (F), identity-preserving perturbation stability (S), cross-model consensus (M); E0 = (F·S·M)^(1/3) with confidence deliberately excluded; SHAP sample n=2,500 per population, 400 interaction rows; challenge families held out.

**Final transfer results.**
1. Dataset-origin shift is substantial and quantified (origin AUC 0.9291), making the cross-corpus evaluation a genuine shift test.
2. A label-free domain-invariant block reduces source-identifying signal (max W 0.1341; block domain AUC 0.5501).
3. UDA materially improves bidirectional cross-corpus ranking (M7 vs M0: +0.1027 / +0.0813 AUC).
4. ERS predicts held-out explanation stability (all configurations Holm-significant; pre-fit target gate 3/4).
5. ERS outperforms calibrated confidence as a predictor of explanation stability on 4/4 evaluated external runs.
6. Explanation reliability and correctness can diverge - a stable explanation can accompany an incorrect prediction (the reversal, characterised structurally).

**Final ERS results.**
- Test A (explanation stability): SUPPORTED across most evaluated configurations; ERS beats confidence on 4/4 external runs.
- Test B (correctness increment beyond confidence): NOT SUPPORTED under the pre-registered in-domain model.
- ERS-target pre-fit gate: 3/4 runs (phresh|F69-R-v3 rho = 0.0691 below the 0.10 bar).

**Final DTS result.** NOT SUPPORTED — 0/12 external cells beat confidence; gram|F69-R-v3 AURC 0.20714 (confidence) vs 0.21166 (DTS); phresh|F69-R-v3 0.25889 vs 0.26423.

**Final temporal result.** 5. Calibration degrades sharply under temporal shift (ECE 0.0716 -> 0.2497).

**Final robustness result.** P3 dot-segment max flip 57.45% (baseline) -> 56.90% (augmented) -> 40.25% (revision-7 repaired) vs the 15% criterion; P5/P6/P7 within criterion after repair (14.95% max). P3 remains a representation-level limitation.

**Final gate table (FINAL_GATE_TABLE_R11).**
| phase                               | criterion                                                                                                                                                                                 | result                                         |
|:------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------|
| FOUNDATION                          | leakage-resistant dataset layer: provenance, checksums, label audit, URL-quality audit, exact/canonical dedup, domain-disjoint split, strict + natural external views, compatibility gate | PASSED                                         |
| REPRESENTATION                      | domain-invariant block: max normalised Wasserstein <= 0.15 and block domain-classifier AUC <= 0.60 (pinned Phase-1 gate)                                                                  | PASSED                                         |
| TRANSFER (UDA)                      | strict-external ROC-AUC >= 0.80 for at least one zero-shot/UDA model in BOTH directions (pinned Gate 2; changelog: tightened any->both in rev 7)                                          | PASSED                                         |
| SEMI-SUPERVISED (Gate 3)            | best semi-supervised multi-source strict-external ACCURACY >= 0.95 in BOTH directions (pinned Gate 3)                                                                                     | FAILED (near-threshold in one direction)       |
| ROBUSTNESS (Gate 4)                 | P3 AND P5/P6/P7 prediction-flip rate <= 15% for at least one repaired variant (pinned Gate 4)                                                                                             | FAILED                                         |
| ERS TARGET (Gate 5)                 | cross-family rho(E0, y_rel) > 0.10 on >= 3 of 4 runs (pinned Phase-5 gate)                                                                                                                | PASSED (3/4 runs)                              |
| ERS vs CONFIDENCE (Test A)          | ERS predicts held-out explanation stability: Spearman(ERS, S_challenge) > 0 with Holm-adjusted p < alpha                                                                                  | SUPPORTED across most evaluated configurations |
| ERS CORRECTNESS INCREMENT (Test B)  | ERS carries information beyond confidence about correctness: LRT (Error ~ C vs Error ~ C + ERS + CxERS) Holm-adjusted p < alpha on the in-domain test sample                              | NOT SUPPORTED (pre-registered in-domain model) |
| DTS (Gate 6)                        | DTS AURC < confidence AURC with the 95% paired-bootstrap CI of the difference entirely below 0 on EVERY external run (all-pairs, never any-pair)                                          | NOT SUPPORTED                                  |
| TEMPORAL                            | report calibration behaviour under temporal shift (pre-registered supporting analysis; PhreshPhish temporal slices, date never a feature)                                                 | DEGRADATION OBSERVED (reported)                |
| CRITERION E (representation repair) | external ROC-AUC (F54-R) > external ROC-AUC (F48) with a DeLong 95% CI excluding 0 (pre-registered)                                                                                       | NOT SUPPORTED                                  |
| REPRODUCIBILITY                     | checksums, split integrity, no target-TEST labels in any fit/tune/calibrate/threshold step, 238 sanity checks, manifest                                                                   | PASSED                                         |

**Final claims.**
- C1: Dataset-origin shift is substantial: the two corpora are strongly separable from URL structure alone, so cross-corpus evaluation represents genuine distribution shift (not label leakage). — **SUPPORTED**
- C2: A label-free domain-invariant representation can reduce source-identifying signal. — **SUPPORTED**
- C3: UDA improves cross-corpus discrimination. — **SUPPORTED**
- C4: ERS predicts held-out explanation stability. — **SUPPORTED across most evaluated runs (target-construction gate 3/4)**
- C5: ERS adds correctness information beyond confidence. — **NOT SUPPORTED**
- C6: DTS improves selective classification risk over confidence. — **NOT SUPPORTED**
- C7: Explanation reliability and prediction correctness can diverge (high-confidence/low-ERS does not reliably imply high classification risk). — **SUPPORTED / OBSERVED REVERSAL (negative finding)**
- C8: Calibration degrades under temporal shift. — **SUPPORTED (with prevalence confound noted)**
- C9: All robustness transformations are stable. — **NOT SUPPORTED (P3 remains a representation-level sensitivity)**
- C10: F54-R representation repair conclusively improves strict-external transfer over F48. — **NOT SUPPORTED (was reported 'unavailable' due to a lookup bug; now computed from cached results)**

**Final limitations.**
1. P3 (dot-segment) robustness sensitivity remains unresolved; RFC 3986 canonicalisation neutralises it mechanically but degenerates the ERS target, so it is retained as a representation-level limitation.
2. Dataset origin is highly detectable (ROC-AUC 0.929); cross-corpus results are bounded by genuine shift.
3. ERS does not improve selective classification risk beyond calibrated confidence.
4. One ERS-target configuration (phresh|F69-R-v3, rho 0.0691) does not pass the 0.10 pre-fit bar.
5. The 95% semi-supervised accuracy criterion is missed in one direction (0.9438 vs 0.95).
6. PhreshPhish temporal calibration deteriorates (ECE 0.0716 -> 0.2497), with a co-occurring prevalence shift and only two adequately-powered quarters.
7. UDA uses unlabeled target TRAIN data and is not pure zero-shot; the semi-supervised 95% benchmark additionally uses target TRAIN labels and target VAL selection.
8. The study is URL-only and does not evaluate HTML/content features.
9. Explanation reliability does not imply prediction correctness.

**Criterion E status.** NOT SUPPORTED — computed from the already-executed paired DeLong comparison (Section 39R REPR_COMPARISON, strict external population, identical rows); no retraining.
Per direction: GramBeddings: dAUC -0.00194 [-0.00238, -0.00150], p=0, n=126,116; PhreshPhish: dAUC -0.00467 [-0.00521, -0.00413], p=0, n=118,390.
In-domain context: GramBeddings +0.00063 [+0.00046, +0.00080]; PhreshPhish +0.00176 [+0.00162, +0.00190].

**Reproducibility status.** Full-scale executed run (~639 min), seed 42, dataset SHA-256 verified, 238/238 sanity checks passed; paper-lock outputs document which results are reused versus recomputed (FINAL_MANIFEST_R11.json); all 109 pre-paper-lock code cells keep their original executed outputs.
Paper-lock sanity: 20/20 checks passed (this section). New experiments added: none.

**Prohibited claims.** ERS improves classification; DTS improves decision-making; ERS is better than confidence (as a decision signal); ERS is a better uncertainty estimate; high-confidence/low-ERS always indicates a dangerous prediction; M7 is zero-shot; the model achieves >=95% external accuracy in both directions; the representation is fully domain invariant; the robustness problem has been solved; the framework is the first to study explanation stability; the framework is the first to study cross-dataset phishing transfer; the framework is deployment-ready.
