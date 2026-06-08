#!/usr/bin/env python3
"""Plot action length for the current run artifacts under runs/main_memory."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from collect_session_action_lengths import (
    collect_session_file_metrics,
    collect_trajectory_metrics,
    empty_trajectory_metrics,
    normalize_session_key,
)


RUN_LOG_FIELD_RE = re.compile(
    r"^(?:openclaw_profile=(?P<profile>\S+)\s+session_key=(?P<session_key>\S+)|"
    r"(?P<key>command_status|markers_ok|memory_records_before|memory_records_after)=(?P<value>.+))$",
    re.MULTILINE,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sessions_index(sessions_dir: Path) -> dict[str, str]:
    sessions_json = sessions_dir / "sessions.json"
    if not sessions_json.exists():
        return {}
    data = read_json(sessions_json)
    result: dict[str, str] = {}
    for session_key, value in data.items():
        sid = value.get("sessionId") if isinstance(value, dict) else None
        if isinstance(sid, str):
            result[normalize_session_key(session_key).lower()] = sid
    return result


def build_trajectory_index(sessions_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sessions_dir.glob("*.trajectory.jsonl"):
        sid = path.name.removesuffix(".trajectory.jsonl")
        try:
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                key = obj.get("sessionKey")
                if isinstance(key, str):
                    result[normalize_session_key(key).lower()] = sid
                    break
        except json.JSONDecodeError:
            continue
    return result


def parse_run_log(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {
        "session_key": "",
        "command_status": "",
        "markers_ok": "",
        "memory_records_before": "",
        "memory_records_after": "",
    }
    if not path.exists():
        return fields
    text = path.read_text(encoding="utf-8", errors="replace")
    for match in RUN_LOG_FIELD_RE.finditer(text):
        if match.group("session_key"):
            fields["session_key"] = match.group("session_key")
        elif match.group("key"):
            fields[match.group("key")] = match.group("value")
    return fields


def run_sort_key(path: Path) -> tuple[int, int]:
    pass_part = path.parts[-4]
    case_part = path.parts[-3]
    return int(pass_part.removeprefix("P")), int(case_part.removeprefix("C"))


def collect_rows(run_root: Path, sessions_dir: Path) -> list[dict[str, Any]]:
    sessions_index = read_sessions_index(sessions_dir)
    trajectory_index = build_trajectory_index(sessions_dir)
    rows: list[dict[str, Any]] = []

    for run_log in sorted(run_root.glob("P*/C*/memory_on/run.log"), key=run_sort_key):
        run_dir = run_log.parent
        pass_id = run_dir.parts[-3]
        case_id = run_dir.parts[-2]
        label = f"{pass_id}_{case_id}"
        fields = parse_run_log(run_log)
        session_key = fields["session_key"]
        session_id = sessions_index.get(session_key.lower()) or trajectory_index.get(session_key.lower()) or ""
        session_file = sessions_dir / f"{session_id}.jsonl" if session_id else Path("")
        trajectory_file = sessions_dir / f"{session_id}.trajectory.jsonl" if session_id else Path("")

        session_metrics = collect_session_file_metrics(session_file) if session_id else collect_session_file_metrics(Path(""))
        trajectory_metrics = (
            collect_trajectory_metrics(trajectory_file)
            if session_id and trajectory_file.exists()
            else empty_trajectory_metrics()
        )
        rows.append(
            {
                "sequence_index": len(rows) + 1,
                "label": label,
                "pass_id": pass_id,
                "case_id": case_id,
                "session_key": session_key,
                "session_id": session_id,
                "command_status": fields["command_status"],
                "markers_ok": fields["markers_ok"],
                "memory_records_before": fields["memory_records_before"],
                "memory_records_after": fields["memory_records_after"],
                "trajectory_status": trajectory_metrics.get("trajectory_status", ""),
                **session_metrics,
                "run_log_path": str(run_log),
                "session_file": str(session_file) if session_id else "",
                "trajectory_file": str(trajectory_file) if session_id else "",
            }
        )
    return rows


def pass_number(pass_id: str) -> int:
    try:
        return int(pass_id.removeprefix("P"))
    except ValueError:
        return 0


def write_csv(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out.write_text("", encoding="utf-8")
        return
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_rows(rows: list[dict[str, Any]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    xs = [int(row["sequence_index"]) for row in rows]
    ys = [int(row["action_length_assistant_plus_tool_calls"] or 0) for row in rows]
    labels = [str(row["label"]) for row in rows]

    colors = []
    for row in rows:
        if row.get("markers_ok") == "yes":
            colors.append("#2f7d32")
        elif row.get("markers_ok") == "no":
            colors.append("#c62828")
        else:
            colors.append("#757575")

    plt.figure(figsize=(12.5, 5.5))
    plt.plot(xs, ys, color="#1565c0", linewidth=1.8, alpha=0.75)
    plt.scatter(xs, ys, c=colors, s=52, zorder=3)
    plt.xticks(xs, labels, rotation=45, ha="right")
    plt.ylabel("Action length = assistant turns + tool calls")
    plt.xlabel("Sequential run")
    plt.title("OpenClaw Main Memory Experiment: Final Run Action Length")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.margins(x=0.02)
    plt.tight_layout()
    plt.savefig(out, dpi=180)
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", default="runs/main_memory/M1_memory_on")
    parser.add_argument(
        "--sessions-dir",
        default="/Users/kaichengmao/.openclaw-main-m1-memory-on/agents/main/sessions",
    )
    parser.add_argument(
        "--out-csv",
        default="evaluation/main_experiments/final_run_action_lengths.csv",
    )
    parser.add_argument(
        "--out-png",
        default="evaluation/main_experiments/figures/final_run_action_length_over_sequence.png",
    )
    parser.add_argument(
        "--max-pass",
        default="P2",
        help="Optional cutoff such as P2. Rows after this pass are excluded. Use an empty string to include all passes.",
    )
    args = parser.parse_args()

    rows = collect_rows(Path(args.run_root), Path(args.sessions_dir))
    if args.max_pass:
        max_pass = pass_number(args.max_pass.upper())
        rows = [row for row in rows if pass_number(str(row.get("pass_id", ""))) <= max_pass]
    write_csv(rows, Path(args.out_csv))
    plot_rows(rows, Path(args.out_png))
    print(f"wrote {len(rows)} rows to {args.out_csv}")
    print(f"wrote plot to {args.out_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
