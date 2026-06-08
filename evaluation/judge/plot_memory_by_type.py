"""
Memory experiment: per-error-type breakdown (M1 only, per-run lines).
2×2 subplots: Overclaim / Mis-citation / Unsupported Claim / Contradiction.
"""

import json, pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

data = json.loads(Path('/Users/kaichengmao/Desktop/Project2/分析结果/result2.json').read_text())
df = pd.DataFrame(data)
df["case_id"] = df["case_id"].astype(str)
df["run_id"]  = df["run_id"].astype(str)

# M1 only
df = df[df["repair_or_not"] == "yes"]

CASE_ORDER = [str(i) for i in range(1, 6)]
ERROR_TYPES = ["Overclaim", "Mis-citation", "Unsupported Claim", "Contradiction"]

# Fill missing combos with 0
idx = pd.MultiIndex.from_product(
    [CASE_ORDER, df["run_id"].unique(), ERROR_TYPES],
    names=["case_id", "run_id", "error_type"],
)
agg = df.groupby(["case_id", "run_id", "error_type"]).size().rename("count").reset_index()
agg = agg.set_index(["case_id", "run_id", "error_type"]).reindex(idx, fill_value=0).reset_index()

# ── Plot ──────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=False)

colors = {"1": "#E74C3C", "2": "#2ECC71"}
fmts   = {"1": "o-",        "2": "s--"}

for ax, et in zip(axes.flat, ERROR_TYPES):
    sub = agg[agg.error_type == et]
    x = np.arange(len(CASE_ORDER))

    for run in ["1", "2"]:
        s = sub[sub.run_id == run].set_index("case_id").reindex(CASE_ORDER)
        ax.plot(x, s["count"].values, fmts[run], color=colors[run],
                linewidth=2.2, markersize=9, markeredgewidth=1.2,
                markeredgecolor="white", label=f"Run {run}", zorder=3)

    ax.set_title(et, fontweight="bold", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([f"C{c}" for c in CASE_ORDER])
    ax.set_ylabel("Error Count")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(bottom=-0.3)

handles, lbls = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, lbls, loc="upper right", fontsize=12, frameon=True, bbox_to_anchor=(0.98, 0.97))
fig.supxlabel("Case", fontweight="bold", y=0.02)
fig.suptitle("Memory Experiment: Per-Error-Type Breakdown (M1 only, per run)", fontweight="bold", y=0.98)
fig.tight_layout(rect=[0, 0.04, 1, 0.94])

out_path = FIG_DIR / "memory_by_type.png"
fig.savefig(out_path)
print(f"Saved → {out_path}")
plt.close(fig)

# ── Print ─────────────────────────────────────────────────────────
for et in ERROR_TYPES:
    print(f"\n=== {et} ===")
    for run in ["1", "2"]:
        s = agg[(agg.error_type == et) & (agg.run_id == run)].set_index("case_id").reindex(CASE_ORDER)
        vals = " → ".join(f"{v:.0f}" for v in s["count"].values)
        print(f"  Run{run}: {vals}")
