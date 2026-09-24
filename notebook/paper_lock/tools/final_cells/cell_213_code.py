# ===================================================================================================
# FINAL REVISION 11 — PAPER LOCK — final paper-facing figures (PNG + PDF)
# PAPER-LOCK-R11
#
# FIGURE 1  final system architecture (schematic, no numbers)
# FIGURE 2  cross-corpus transfer: M0 -> M6 -> M7, both directions, M7 bootstrap CIs
# FIGURE 3  ERS vs confidence as predictors of held-out explanation stability
# FIGURE 4  temporal calibration degradation (PhreshPhish strict-external slices)
# FIGURE 5  robustness diagnostic: P3 vs P5/P6/P7 flip rates across repair stages
# All figures are generated from the executed result objects loaded above; no new computation.
# ===================================================================================================
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 300, "font.size": 9.5,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "axes.axisbelow": True})
PL_FIGURE_FILES = []

def _save_fig(fig, name):
    for ext in ("png", "pdf"):
        p = PL_FIGS / f"{name}.{ext}"
        fig.savefig(p, bbox_inches="tight")
    PL_FIGURE_FILES.append(name)
    plt.show()

# ---------------- FIGURE 1: architecture ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.2, 5.4))
ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.grid(False)
def _box(x, y, w, h, text, fc, ec="#37474f", fs=8.6, bold=False):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.1, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, zorder=3,
            fontweight="bold" if bold else "normal")
def _arrow(x1, y1, x2, y2, style="-|>", lw=1.2, ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, lw=lw, ls=ls, color="#455a64"))
_blue, _green, _orange, _grey, _red = "#e3f2fd", "#e8f5e9", "#fff3e0", "#f5f5f5", "#ffebee"
_box(1, 47, 20, 12, "GramBeddings\n(~800K URLs)", _blue, bold=True)
_box(1, 30, 20, 12, "PhreshPhish\n(~666K URLs, URL-only)", _blue, bold=True)
_box(2, 52.5, 18, 5, "provenance + checksum audit", _grey, fs=7.2)
_box(25, 39, 17, 20, "URL-only feature extraction\nF48 (48) | F54-R (54)\n+ 15 domain-invariant\n=> F69-R-v3 (69)", _green, bold=True)
_box(25, 22, 17, 13, "overlap control\nexact / canonical / eTLD+1\nstrict domain-unseen\nexternal views", _green)
_box(46, 39, 16, 20, "calibrated detectors\n(XGBoost / LightGBM / RF)\nsource-VAL thresholds\nisotonic calibration", _blue, bold=True)
_box(46, 22, 16, 13, "transfer / UDA branch\nM0 source-only\nM6 fusion -> M7\n+ self-training\n(unlabeled target TRAIN)", _orange, bold=True)
_box(66, 39, 15, 20, "TreeSHAP (x3 models)\nfaithfulness F\nstability S\nconsensus M", _green, bold=True)
_box(66, 22, 15, 13, "perturbation robustness\nP3 limitation retained", _red)
_box(85, 33, 13, 26, "E0 = (F·S·M)^(1/3)\nconfidence EXCLUDED\nERS = g(E0)\nDTS = h(C, ERS)\nselective decisions", _orange, bold=True)
_arrow(11, 47, 25, 49); _arrow(11, 42, 25, 42); _arrow(21, 36, 25, 30)
_arrow(42, 49, 46, 49); _arrow(42, 30, 46, 30)
_arrow(62, 49, 66, 49); _arrow(62, 28, 66, 28)
_arrow(81, 49, 85, 46); _arrow(81, 28, 85, 40)
ax.set_title("TRAC-Phish (revision 11): leakage-resistant cross-corpus evaluation, domain-aware transfer, "
             "and explanation-reliability analysis", fontsize=10.5, fontweight="bold")
_save_fig(fig, "fig1_final_architecture")

# ---------------- FIGURE 2: M0 -> M6 -> M7 transfer -------------------------------------------------
fig, ax = plt.subplots(figsize=(7.6, 4.6))
_dirs = ["GramBeddings -> PhreshPhish", "PhreshPhish -> GramBeddings"]
_labels = ["GramBeddings -> PhreshPhish", "PhreshPhish -> GramBeddings"]
_x = np.arange(3)
_w = 0.36
for i, d in enumerate(_dirs):
    vals = [M0_BY_DIR[d], M6_BY_DIR[d], M7_BY_DIR[d]]
    bars = ax.bar(_x + (i - 0.5) * _w, vals, _w, label=_labels[i],
                  color=["#90a4ae", "#64b5f6", "#1e88e5"][i] if i == 0 else ["#a5d6a7", "#66bb6a", "#2e7d32"][i])
    if i == 1:
        ax.errorbar(_x[2] + 0.5 * _w, vals[2],
                    yerr=[[vals[2] - M7_CI[d][0]], [M7_CI[d][1] - vals[2]]],
                    fmt="none", ecolor="#b71c1c", capsize=4, lw=1.4, zorder=5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.004, f"{v:.4f}", ha="center", fontsize=8.2)
ax.axhline(0.80, color="#b71c1c", ls="--", lw=1.1)
ax.text(2.44, 0.802, "Gate 2 = 0.80", color="#b71c1c", fontsize=8, ha="right")
ax.set_xticks(_x, ["M0\nsource-only (zero-shot)", "M6\nfusion (UDA)", "M7\nword expert + self-training (UDA)"])
ax.set_ylabel("strict-external ROC-AUC"); ax.set_ylim(0.70, 0.92)
ax.set_title("FIGURE 2 — Cross-corpus transfer: UDA materially improves both directions\n"
             "(M7 95% bootstrap CI shown for PhreshPhish -> GramBeddings; both M7 CIs exclude the M0 AUC)",
             fontsize=9.5)
ax.legend(loc="upper left", frameon=False)
_save_fig(fig, "fig2_final_transfer")

# ---------------- FIGURE 3: ERS vs confidence for held-out explanation stability -------------------
fig, ax = plt.subplots(figsize=(8.6, 4.6))
_runs = list(_test_ee.index)
_pretty = {r: r.replace("F68RV3", "F69-R-v3") for r in _runs}
_x = np.arange(len(_runs))
_w = 0.2
for j, (pop, tbl, off, shades) in enumerate([("in-domain test", _test_ee, 0, ("#bdbdbd", "#616161")),
                                             ("strict external", _ext_ee, 2, ("#90caf9", "#1565c0"))]):
    for k, (col, lab) in enumerate([("A_spearman_C_vs_Schallenge", "confidence C"),
                                    ("A_spearman_ERS_vs_Schallenge", "ERS")]):
        vals = [float(tbl.loc[r, col]) for r in _runs]
        bars = ax.bar(_x + (j * 2 + k - 1.5) * _w, vals, _w,
                      color=shades[k], label=f"{lab} ({pop})")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + (0.008 if v >= 0 else -0.024), f"{v:+.2f}",
                    ha="center", fontsize=7.4)
ax.axhline(0, color="black", lw=0.9)
ax.set_xticks(_x, [_pretty[r] for r in _runs], fontsize=8.4)
ax.set_ylabel("Spearman rho( . , S_challenge)")
ax.set_title("FIGURE 3 — ERS vs calibrated confidence as predictors of held-out explanation stability\n"
             "all associations Holm-significant; ERS is the stronger predictor on 4/4 strict-external runs, "
             "confidence on 2/4 in-domain runs", fontsize=9.5)
ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper left")
ax.set_ylim(-0.08, 0.72)
_save_fig(fig, "fig3_final_ers_vs_confidence")

# ---------------- FIGURE 4: temporal ECE degradation ------------------------------------------------
fig, ax = plt.subplots(figsize=(7.8, 4.4))
_sl = ["2025Q3", "2025Q4"]
for run, color, mk in [("gram|F48", "#78909c", "o"), ("gram|F68RV3", "#1e88e5", "s")]:
    _tt = PL["TEMPORAL"][PL["TEMPORAL"]["run"] == run].set_index("slice")
    ax.plot(_sl, [_tt.loc[s, "ece"] for s in _sl], marker=mk, color=color, lw=1.8,
            label=f"ECE — {run.replace('F68RV3', 'F69-R-v3')}")
    ax2 = ax.twinx()
    ax2.plot(_sl, [_tt.loc[s, "roc_auc"] for s in _sl], marker=mk, color=color, lw=1.2, ls=":",
             alpha=0.65)
    ax2.set_ylabel("ROC-AUC (dotted)", fontsize=8.5); ax2.set_ylim(0.70, 0.80)
    ax2.grid(False); ax2.spines["right"].set_visible(True)
ax.set_ylabel("expected calibration error (ECE)")
ax.set_title("FIGURE 4 — Temporal calibration degradation (GramBeddings -> PhreshPhish, strict external)\n"
             "ECE rises sharply 2025Q3 -> 2025Q4 while ROC-AUC stays flat; phishing prevalence shifts "
             "14.4% -> 57.0% over the same window", fontsize=9.5)
ax.legend(frameon=False, loc="upper left")
_save_fig(fig, "fig4_final_temporal_ece")

# ---------------- FIGURE 5 (diagnostic): P3 vs P5/P6/P7 flip rates ----------------------------------
fig, ax = plt.subplots(figsize=(7.8, 4.4))
_fams = ["P3_dot_segment", "P5_subdomain_insertion", "P6_path_padding", "P7_query_padding"]
_fam_labels = ["P3 dot-segment", "P5 subdomain", "P6 path padding", "P7 query padding"]
_fl = PL["FLIP_R6"]
_base = [float(_fl[(_fl["family"] == f)]["baseline (rev 5 model)"].astype(float).max()) for f in _fams]
_augv = [float(_fl[(_fl["family"] == f)]["augmented (6A+6B)"].astype(float).max()) for f in _fams]
_r7 = PL["ROBUST_R7"]
_r7v = [float(_r7[(_r7["family"] == f)]["rev7 + hard-negative mining"].astype(float).max()) for f in _fams]
_x = np.arange(4); _w = 0.26
for k, (vals, lab, color) in enumerate([(_base, "baseline (rev 5)", "#bdbdbd"),
                                        (_augv, "augmented (rev 6)", "#64b5f6"),
                                        (_r7v, "hard-negative repair (rev 7, in-domain)", "#1e88e5")]):
    bars = ax.bar(_x + (k - 1) * _w, vals, _w, label=lab, color=color)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", fontsize=7.6)
ax.axhline(15, color="#b71c1c", ls="--", lw=1.2)
ax.text(3.42, 16.2, "15% criterion", color="#b71c1c", fontsize=8, ha="right")
ax.set_xticks(_x, _fam_labels)
ax.set_ylabel("max prediction-flip rate (%)")
ax.set_title("FIGURE 5 (diagnostic) — Robustness: P5/P6/P7 are repairable within the 15% criterion;\n"
             "P3 (dot-segment) is a persistent raw-representation sensitivity (known limitation)", fontsize=9.5)
ax.legend(frameon=False)
_save_fig(fig, "fig5_final_robustness")

print(f"final figures written to {PL_FIGS}: {PL_FIGURE_FILES}")
