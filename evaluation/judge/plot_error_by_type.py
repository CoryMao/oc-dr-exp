"""
Per-error-type breakdown chart.
2×2 subplots, one per error type.
X = case 1-5, Y = mean error count per run, lines = repair yes/no.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Load ──────────────────────────────────────────────────────────────────
results_path = Path(__file__).resolve().parents[2] / "分析结果" / "results.json"
df = pd.DataFrame(json.loads(results_path.read_text()))
df["case_id"] = df["case_id"].astype(str)
df["run_id"]  = df["run_id"].astype(str)

ERROR_TYPES = ["Overclaim", "Mis-citation", "Unsupported Claim", "Contradiction"]
CASE_ORDER = [str(i) for i in range(1, 6)]

# ── Aggregate: count per (case, run, error_type, repair) ─────────────────
agg = (
    df.groupby(["case_id", "run_id", "error_type", "repair_or_not"])
      .size()
      .rename("count")
      .reset_index()
)

# Fill missing combos with 0 so mean isn't biased by absent groups
idx = pd.MultiIndex.from_product(
    [CASE_ORDER, df["run_id"].unique(), ERROR_TYPES, ["no", "yes"]],
    names=["case_id", "run_id", "error_type", "repair_or_not"],
)
agg = agg.set_index(["case_id", "run_id", "error_type", "repair_or_not"])
agg = agg.reindex(idx, fill_value=0).reset_index()

summary = (
    agg.groupby(["case_id", "error_type", "repair_or_not"])["count"]
       .agg(["mean", "std"])
       .reset_index()
)
summary["std"] = summary["std"].fillna(0)

# ── Plot ──────────────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=False)

colors = {"no": "#E74C3C", "yes": "#2ECC71"}
labels = {"no": "Original", "yes": "Repaired"}

for ax, et in zip(axes.flat, ERROR_TYPES):
    sub = summary[summary.error_type == et]
    x = np.arange(len(CASE_ORDER))
    # Pivot
    piv_mean = sub.pivot(index="case_id", columns="repair_or_not", values="mean").reindex(CASE_ORDER)
    piv_std  = sub.pivot(index="case_id", columns="repair_or_not", values="std").reindex(CASE_ORDER)

    width = 0.08
    for cond in ["no", "yes"]:
        if cond not in piv_mean.columns:
            continue
        means = piv_mean[cond].values
        stds  = piv_std[cond].values
        offset = -width/2 if cond == "no" else width/2
        ax.errorbar(
            x + offset, means, yerr=stds,
            fmt="o-", linewidth=2, markersize=7,
            capsize=4, capthick=1.5,
            color=colors[cond],
            label=labels[cond],
        )

    ax.set_title(f"{et}", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([f"C{c}" for c in CASE_ORDER])
    ax.set_ylabel("Mean Error Count")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=-0.2)

# Single legend
handles, lbls = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, lbls, loc="upper right", fontsize=12, frameon=True, bbox_to_anchor=(0.98, 0.97))

fig.supxlabel("Case", fontweight="bold", y=0.02)
fig.suptitle("Claim Error Count by Error Type × Case × Repair Status\n(mean across runs, ±1 std)", fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0.04, 1, 0.94])

out_path = FIG_DIR / "error_rate_by_type.png"
fig.savefig(out_path)
print(f"Saved → {out_path}")
plt.close(fig)
