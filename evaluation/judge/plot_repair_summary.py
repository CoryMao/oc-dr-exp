"""Generate a clean per-case repair-effect bar chart for the presentation."""

import json, pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

results_path = Path("/Users/kaichengmao/Desktop/Project2/分析结果/results.json")
df = pd.DataFrame(json.loads(results_path.read_text()))
df["case_id"] = df["case_id"].astype(str)
df["run_id"]  = df["run_id"].astype(str)

CASE_ORDER = [str(i) for i in range(1, 6)]
ERROR_TYPES = ["Overclaim", "Mis-citation", "Unsupported Claim", "Contradiction"]

# ── Per-case total ───────────────────────────────────────────────────
idx = pd.MultiIndex.from_product(
    [CASE_ORDER, df["run_id"].unique(), ERROR_TYPES, ["no", "yes"]],
    names=["case_id", "run_id", "error_type", "repair_or_not"],
)
agg = df.groupby(["case_id", "run_id", "error_type", "repair_or_not"]).size().rename("count").reset_index()
agg = agg.set_index(["case_id", "run_id", "error_type", "repair_or_not"]).reindex(idx, fill_value=0).reset_index()

per_case = agg.groupby(["case_id", "repair_or_not"])["count"].agg(["mean", "std"]).reset_index()
per_case["std"] = per_case["std"].fillna(0)

# ── Plot ─────────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 14, "figure.dpi": 150})
fig, ax = plt.subplots(figsize=(10, 5.5))

x = np.arange(len(CASE_ORDER))
bar_w = 0.3
colors = {"no": "#E74C3C", "yes": "#2ECC71"}
labels = {"no": "Original (repair=no)", "yes": "Repaired (repair=yes)"}

for i, cond in enumerate(["no", "yes"]):
    sub = per_case[per_case.repair_or_not == cond].set_index("case_id").reindex(CASE_ORDER)
    means = sub["mean"].values
    stds  = sub["std"].values
    offset = (i - 0.5) * bar_w
    bars = ax.bar(x + offset, means, bar_w * 0.9, yerr=stds,
                  color=colors[cond], edgecolor="white", linewidth=0.8,
                  capsize=5, label=labels[cond], zorder=2)
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                f"{val:.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold",
                color=colors[cond])

ax.set_xticks(x)
ax.set_xticklabels([f"Case {c}" for c in CASE_ORDER], fontsize=14)
ax.set_ylabel("Mean Error Count per Run", fontweight="bold", fontsize=13)
ax.set_title("Claim Error Count by Case × Repair Status\n(mean across 3 runs, ±1 std)", fontweight="bold", fontsize=15)
ax.legend(frameon=True, fontsize=12, loc="upper left")
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_ylim(bottom=0, top=6)
ax.set_xlim(-0.5, 4.5)

fig.tight_layout()
out_path = FIG_DIR / "repair_effect_summary.png"
fig.savefig(out_path)
print(f"Saved → {out_path}")
plt.close(fig)
