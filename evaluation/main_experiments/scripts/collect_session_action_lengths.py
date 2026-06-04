#!/usr/bin/env python3
"""Collect non-time action length metrics from OpenClaw session logs."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from statistics import mean, median
from typing import Any


RUN_KEY_RE = re.compile(r"main-memory-(p\d+)-c(\d+)(?:-(retry\d+))?", re.IGNORECASE)
RUN_LOG_RE = re.compile(r"^(command_status|markers_ok|memory_records_before|memory_records_after)=(.+)$", re.MULTILINE)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def normalize_session_key(key: str) -> str:
    return key.removeprefix("agent:main:")


def parse_run_key(session_key: str) -> tuple[str, str, str, str]:
    key = normalize_session_key(session_key)
    match = RUN_KEY_RE.search(key)
    if not match:
        return "", "", "", ""
    pass_id = match.group(1).upper()
    case_id = f"C{match.group(2)}"
    retry = match.group(3) or ""
    run_id = f"{pass_id}_{case_id}"
    return pass_id, case_id, run_id, retry


def collect_session_file_metrics(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    roles: dict[str, int] = {}
    tool_calls = 0
    tool_results = 0
    tool_errors = 0
    assistant_turns = 0
    user_turns = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_reasoning_tokens = 0
    total_tokens = 0

    for row in rows:
        if row.get("type") != "message":
            continue
        message = row.get("message") or {}
        role = str(message.get("role") or "")
        roles[role] = roles.get(role, 0) + 1
        if role == "assistant":
            assistant_turns += 1
            usage = message.get("usage") or {}
            total_input_tokens += int(usage.get("input") or 0)
            total_output_tokens += int(usage.get("output") or 0)
            total_reasoning_tokens += int(usage.get("reasoningTokens") or 0)
            total_tokens += int(usage.get("totalTokens") or 0)
            content = message.get("content") or []
            if isinstance(content, list):
                tool_calls += sum(1 for item in content if isinstance(item, dict) and item.get("type") == "toolCall")
        elif role == "user":
            user_turns += 1
        elif role == "toolResult":
            tool_results += 1
            if message.get("isError"):
                tool_errors += 1

    return {
        "session_event_count": len(rows),
        "assistant_turns": assistant_turns,
        "user_turns": user_turns,
        "tool_call_count": tool_calls,
        "tool_result_count": tool_results,
        "tool_error_count": tool_errors,
        "action_length_assistant_plus_tool_calls": assistant_turns + tool_calls,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "reasoning_tokens": total_reasoning_tokens,
        "total_tokens": total_tokens,
    }


def collect_trajectory_metrics(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    session_key = ""
    status = ""
    item_started = ""
    item_completed = ""
    item_active = ""
    tool_meta_count = ""
    trace_tool_count = ""
    trace_client_tool_count = ""

    for row in rows:
        if not session_key and row.get("sessionKey"):
            session_key = str(row.get("sessionKey"))
        data = row.get("data") or {}
        if row.get("type") == "session.started":
            trace_tool_count = data.get("toolCount", "")
            trace_client_tool_count = data.get("clientToolCount", "")
        if row.get("type") == "trace.artifacts":
            lifecycle = data.get("itemLifecycle") or {}
            item_started = lifecycle.get("startedCount", "")
            item_completed = lifecycle.get("completedCount", "")
            item_active = lifecycle.get("activeCount", "")
            tool_meta_count = len(data.get("toolMetas") or [])
            final_status = data.get("finalStatus")
            if final_status:
                status = str(final_status)
        if row.get("type") == "session.ended":
            ended_status = data.get("status")
            if ended_status:
                status = str(ended_status)

    return {
        "session_key": session_key,
        "trajectory_event_count": len(rows),
        "trajectory_status": status,
        "item_started_count": item_started,
        "item_completed_count": item_completed,
        "item_active_count": item_active,
        "tool_meta_count": tool_meta_count,
        "trace_available_tool_count": trace_tool_count,
        "trace_client_tool_count": trace_client_tool_count,
    }


def empty_trajectory_metrics() -> dict[str, Any]:
    return {
        "session_key": "",
        "trajectory_event_count": 0,
        "trajectory_status": "",
        "item_started_count": "",
        "item_completed_count": "",
        "item_active_count": "",
        "tool_meta_count": "",
        "trace_available_tool_count": "",
        "trace_client_tool_count": "",
    }


def read_current_session_map(sessions_json: Path) -> dict[str, str]:
    if not sessions_json.exists():
        return {}
    data = json.loads(sessions_json.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for session_key, value in data.items():
        if "main-memory-" not in session_key:
            continue
        sid = value.get("sessionId")
        if isinstance(sid, str):
            result[sid] = session_key
    return result


def collect_run_log_metrics(run_root: Path, pass_id: str, case_id: str) -> dict[str, Any]:
    metrics = {
        "run_log_exists": False,
        "run_log_command_status": "",
        "run_log_markers_ok": "",
        "run_log_memory_records_before": "",
        "run_log_memory_records_after": "",
        "run_log_path": "",
    }
    if not pass_id or not case_id:
        return metrics
    run_log = run_root / pass_id / case_id / "memory_on" / "run.log"
    metrics["run_log_path"] = str(run_log)
    if not run_log.exists():
        return metrics
    metrics["run_log_exists"] = True
    text = run_log.read_text(encoding="utf-8", errors="replace")
    found = dict(RUN_LOG_RE.findall(text))
    metrics["run_log_command_status"] = found.get("command_status", "")
    metrics["run_log_markers_ok"] = found.get("markers_ok", "")
    metrics["run_log_memory_records_before"] = found.get("memory_records_before", "")
    metrics["run_log_memory_records_after"] = found.get("memory_records_after", "")
    return metrics


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {"all": rows}
    for row in rows:
        status = row.get("trajectory_status") or "unknown"
        groups.setdefault(f"status:{status}", []).append(row)

    output: list[dict[str, Any]] = []
    for group, items in groups.items():
        if not items:
            continue
        for metric in [
            "action_length_assistant_plus_tool_calls",
            "tool_call_count",
            "assistant_turns",
            "tool_error_count",
            "item_started_count",
            "tool_meta_count",
        ]:
            values: list[float] = []
            for item in items:
                value = item.get(metric)
                if value == "" or value is None:
                    continue
                values.append(float(value))
            if not values:
                continue
            output.append(
                {
                    "group": group,
                    "metric": metric,
                    "n": len(values),
                    "mean": round(mean(values), 3),
                    "median": round(median(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3),
                }
            )
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sessions-dir",
        default="/Users/kaichengmao/.openclaw-main-m1-memory-on/agents/main/sessions",
    )
    parser.add_argument(
        "--out",
        default="evaluation/main_experiments/session_action_lengths.csv",
    )
    parser.add_argument(
        "--summary-out",
        default="evaluation/main_experiments/session_action_length_summary.csv",
    )
    parser.add_argument(
        "--run-root",
        default="runs/main_memory/M1_memory_on",
    )
    args = parser.parse_args()

    sessions_dir = Path(args.sessions_dir)
    current_map = read_current_session_map(sessions_dir / "sessions.json")

    session_ids: dict[str, str] = {}
    for sid, key in current_map.items():
        session_ids[sid] = key
    for trajectory_path in sorted(sessions_dir.glob("*.trajectory.jsonl")):
        sid = trajectory_path.name.removesuffix(".trajectory.jsonl")
        traj = collect_trajectory_metrics(trajectory_path)
        key = traj.get("session_key") or current_map.get(sid, "")
        if "main-memory-" in key:
            session_ids[sid] = str(key)

    records: list[dict[str, Any]] = []
    for sid, mapped_session_key in sorted(session_ids.items(), key=lambda item: item[1]):
        trajectory_path = sessions_dir / f"{sid}.trajectory.jsonl"
        traj = collect_trajectory_metrics(trajectory_path) if trajectory_path.exists() else empty_trajectory_metrics()
        session_key = traj.get("session_key") or mapped_session_key
        session_path = sessions_dir / f"{sid}.jsonl"
        sess = collect_session_file_metrics(session_path)
        pass_id, case_id, run_id, retry = parse_run_key(session_key)
        run_log = collect_run_log_metrics(Path(args.run_root), pass_id, case_id)
        records.append(
            {
                "session_id": sid,
                "pass_id": pass_id,
                "case_id": case_id,
                "run_id": run_id,
                "retry": retry,
                "has_session_jsonl": session_path.exists(),
                "has_trajectory_jsonl": trajectory_path.exists(),
                **traj,
                "session_key": normalize_session_key(session_key),
                **sess,
                **run_log,
                "session_file": str(session_path),
                "trajectory_file": str(trajectory_path),
            }
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys()) if records else []
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    summary_rows = summarize(records)
    summary_path = Path(args.summary_out)
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()) if summary_rows else [])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"wrote {len(records)} session rows to {out_path}")
    print(f"wrote {len(summary_rows)} summary rows to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
