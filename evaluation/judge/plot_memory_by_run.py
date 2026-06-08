"""
Memory experiment: per-run line chart (no averaging).
X = case 1-5, Y = error count.
4 lines: Run1-M0, Run1-M1, Run2-M0, Run2-M1.
"""

import json, pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ── Load ──────────────────────────────────────────────────────────
data = json.loads(Path('/Users/kaichengmao/Desktop/Project2/分析结果/result2.json').read_text())
df = pd.DataFrame(data)
df["case_id"] = df["case_id"].astype(str)
df["run_id"]  = df["run_id"].astype(str)

CASE_ORDER = [str(i) for i in range(1, 6)]

# ── Aggregate: error count per (case, run, memory) ─────────────────
# Fill missing combos with 0
idx = pd.MultiIndex.from_product(
    [CASE_ORDER, df["run_id"].unique(), ["no", "yes"]],
    names=["case_id", "run_id", "memory"],
)
agg = df.groupby(["case_id", "run_id", "repair_or_not"]).size().rename("count").reset_index()
agg = agg.rename(columns={"repair_or_not": "memory"})
agg = agg.set_index(["case_id", "run_id", "memory"]).reindex(idx, fill_value=0).reset_index()

# ── Plot ──────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"font.size": 13, "figure.dpi": 150})
fig, ax = plt.subplots(figsize=(9, 5.5))

x = np.arange(len(CASE_ORDER))

# Color scheme: M0 = warm, M1 = cool; Run1 = solid/dark, Run2 = dashed/light
line_styles = {
    ("1", "yes"): ("o-",  "#E74C3C", "Run 1 · M1"),
    ("2", "yes"): ("s--", "#2ECC71", "Run 2 · M1"),
}

for run in ["1", "2"]:
    for mem, mem_label in [("yes", "M1")]:
        sub = agg[(agg.run_id == run) & (agg.memory == mem)]
        sub = sub.set_index("case_id").reindex(CASE_ORDER)
        counts = sub["count"].values
        fmt, color, label = line_styles[(run, mem)]
        ax.plot(x, counts, fmt, color=color, linewidth=2.2, markersize=10,
                markeredgewidth=1.2, markeredgecolor="white", label=label, zorder=3)

ax.set_xticks(x)
ax.set_xticklabels([f"Case {c}" for c in CASE_ORDER], fontsize=13)
ax.set_xlabel("Case", fontweight="bold", fontsize=14)
ax.set_ylabel("Error Count", fontweight="bold", fontsize=14)
ax.set_title("Memory Experiment: Per-Run Error Count (M1 only)", fontweight="bold", fontsize=15)
ax.legend(frameon=True, fontsize=11, loc="upper left")
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(bottom=-0.3)
ax.set_xlim(-0.2, 4.2)

fig.tight_layout()
out_path = FIG_DIR / "memory_by_run.png"
fig.savefig(out_path)
print(f"Saved → {out_path}")
plt.close(fig)

# ── Print table ───────────────────────────────────────────────────
print("\nPer-run error count:")
for run in ["1", "2"]:
    for mem in ["no", "yes"]:
        sub = agg[(agg.run_id == run) & (agg.memory == mem)].set_index("case_id").reindex(CASE_ORDER)
        vals = " → ".join(f"{v:.0f}" for v in sub["count"].values)
        print(f"  Run{run} M{1 if mem=='yes' else 0}: {vals}")
