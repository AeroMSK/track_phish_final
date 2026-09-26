**Abstract (revision 11, paper lock).** Phishing-URL detectors deployed across corpora face
genuine distribution shift: we measure that two independent URL corpora are separable by URL structure alone
(origin ROC-AUC 0.9291), so cross-corpus evaluation is a real stress test rather than a replication.
We study GramBeddings and PhreshPhish (799,565 and 666,300 cleaned URLs) under a
leakage-resistant protocol - URL-only features, exact/canonical/eTLD+1 overlap control, domain-disjoint
splits and a strict domain-unseen external view - and evaluate (i) domain-aware transfer, (ii) calibrated
prediction, and (iii) explanation reliability via TreeSHAP-based faithfulness, stability and cross-model
consensus combined into an explanation-only score E0 = (F·S·M)^(1/3) whose calibrated form (ERS) deliberately
excludes prediction confidence. Unsupervised domain adaptation over unlabeled target-TRAIN data raises
strict-external ROC-AUC from 0.7712 to
0.8739 (GramBeddings -> PhreshPhish) and from
0.7430 to 0.8243
(PhreshPhish -> GramBeddings). ERS predicts held-out explanation stability (all run configurations
Holm-significant) and outperforms calibrated confidence as a predictor of explanation stability on the
evaluated external runs. However, ERS adds no statistically supported information about classification
correctness beyond calibrated confidence under the pre-registered model, and a decision trust score combining
confidence and ERS does not reduce selective-classification risk below confidence alone on any evaluated
external setting (0/12 cells). Explanation reliability and prediction correctness
therefore diverge - high confidence with low ERS does not reliably indicate classification risk. Temporal
analysis shows calibration deteriorating sharply (ECE 0.0716 -> 0.2497) while ranking
stays comparatively stable. We conclude that explanation-derived reliability is informative about
explanations but should not replace calibrated confidence for selective classification decisions.

**Paper positioning.** Phishing detectors can retain useful discrimination while their confidence,
explanations, and explanation reliability behave differently under cross-corpus and temporal shift. This
study therefore evaluates whether explanation-derived reliability adds information beyond calibrated
prediction confidence using a strict, leakage-resistant, domain-unseen protocol. The results show that ERS
is associated with held-out explanation stability and can outperform confidence as a predictor of
explanation stability on the evaluated external runs. However, ERS does not improve selective classification
risk over confidence. Thus explanation reliability should not be interpreted as a proxy for prediction
correctness. Cross-corpus domain adaptation improves transfer (M7 UDA), while temporal analysis exposes
substantial calibration degradation.
