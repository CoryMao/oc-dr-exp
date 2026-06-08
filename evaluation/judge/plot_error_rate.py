"""
Aggregate claim error data and plot error-rate line chart.

X-axis: case 1–5
Y-axis: mean error count per run (averaged across runs)
Lines:  repair_or_not = "no" (original) vs "yes" (repaired)

Output: evaluation/judge/figures/error_rate_by_case.png
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Load ──────────────────────────────────────────────────────────────────
results_path = Path(__file__).resolve().parents[2] / "分析结果" / "results.json"
with open(results_path, encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
# Normalise types just in case
df["case_id"] = df["case_id"].astype(str)
df["run_id"]  = df["run_id"].astype(str)

# ── Aggregate: error count per (case, run, repair) ───────────────────────
agg = (
    df.groupby(["case_id", "run_id", "repair_or_not"])
      .size()
      .rename("error_count")
      .reset_index()
)

# ── Average across runs (mean ± std) ─────────────────────────────────────
summary = (
    agg.groupby(["case_id", "repair_or_not"])["error_count"]
       .agg(["mean", "std"])
       .reset_index()
)
# Fill NaN std (single-run cases) with 0
summary["std"] = summary["std"].fillna(0)

# Pivot for plotting
pivot_mean = summary.pivot(index="case_id", columns="repair_or_not", values="mean")
pivot_std  = summary.pivot(index="case_id", columns="repair_or_not", values="std")

# Ensure case order 1→5
case_order = [str(i) for i in range(1, 6)]
pivot_mean = pivot_mean.reindex(case_order)
pivot_std  = pivot_std.reindex(case_order)

# ── Plot ──────────────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 13, "figure.dpi": 150})

fig, ax = plt.subplots(figsize=(8, 5))

x = np.arange(len(case_order))
width = 0.08  # slight offset so error bars don't overlap

colors = {"no": "#E74C3C", "yes": "#2ECC71"}   # red = original, green = repaired
labels = {"no": "Original (repair=no)", "yes": "Repaired (repair=yes)"}

for cond in ["no", "yes"]:
    means = pivot_mean[cond].values
    stds  = pivot_std[cond].values
    offset = -width/2 if cond == "no" else width/2
    ax.errorbar(
        x + offset, means, yerr=stds,
        fmt="o-", linewidth=2, markersize=8,
        capsize=5, capthick=1.5,
        color=colors[cond],
        label=labels[cond],
    )

ax.set_xticks(x)
ax.set_xticklabels([f"Case {c}" for c in case_order])
ax.set_xlabel("Case", fontweight="bold")
ax.set_ylabel("Mean Error Count per Run", fontweight="bold")
ax.set_title("Claim Error Count by Case × Repair Status\n(averaged across runs, ±1 std)", fontweight="bold")
ax.legend(frameon=True, fontsize=11)
ax.grid(axis="y", alpha=0.35)
ax.set_ylim(bottom=0)

fig.tight_layout()
out_path = FIG_DIR / "error_rate_by_case.png"
fig.savefig(out_path)
print(f"Saved → {out_path}")
plt.close(fig)

# ── Also print the summary table ─────────────────────────────────────────
print("\nSummary table (mean ± std):")
for cond in ["no", "yes"]:
    print(f"\n  {labels[cond]}:")
    for c in case_order:
        m = pivot_mean.loc[c, cond]
        s = pivot_std.loc[c, cond]
        print(f"    Case {c}: {m:.1f} ± {s:.1f}")
