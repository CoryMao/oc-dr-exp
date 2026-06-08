#!/usr/bin/env python3
"""Sync pass-specific evidence files into the ignored local paper cache.

P1 and P2 can cite different papers under the same tag, e.g. [D]. This script
creates pass-specific files such as:

  presentation/main_memory/case5/papers/P1_[D]_2405.17739.pdf
  presentation/main_memory/case5/papers/P2_[D]_2410.12944.md

PDF is preferred when an existing local PDF can be found. Otherwise, the script
copies the arXiv MCP markdown cache when available.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


MARKERS = {
    "original": ("# ORIGINAL_REPORT", "# REFCHECKER_REPAIR_LOG"),
    "repaired": ("# REPAIRED_REPORT", "# RUN_SUMMARY"),
}

TAG_REF_RE = re.compile(r"^\s*-\s*\[([A-F])\]\s*(.+)$")
ARXIV_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5})", re.IGNORECASE)
TITLE_RE = re.compile(r'"([^"]+)"')
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}")


@dataclass
class RefNeed:
    case_id: str
    pass_id: str
    tag: str
    arxiv_id: str
    title: str
    ref_line: str
    case_dir: Path


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def section_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        return ""
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end < 0:
        end = len(text)
    return clean_text(text[start:end])


def parse_refs(report_text: str) -> dict[str, tuple[str, str, str]]:
    ref_start = report_text.find("## 第三部分")
    if ref_start < 0:
        ref_start = report_text.find("引用论文清单")
    ref_text = report_text[ref_start:] if ref_start >= 0 else report_text
    refs: dict[str, tuple[str, str, str]] = {}
    current_tag: str | None = None
    current_line = ""
    for raw in ref_text.splitlines():
        match = TAG_REF_RE.match(raw)
        if match:
            if current_tag:
                refs[current_tag] = parse_ref_line(current_line)
            current_tag = match.group(1)
            current_line = match.group(2).strip()
        elif current_tag and raw.strip():
            current_line += " " + raw.strip()
    if current_tag:
        refs[current_tag] = parse_ref_line(current_line)
    return refs


def parse_ref_line(ref_line: str) -> tuple[str, str, str]:
    arxiv_match = ARXIV_RE.search(ref_line)
    title_match = TITLE_RE.search(ref_line)
    return (
        arxiv_match.group(1) if arxiv_match else "",
        title_match.group(1).strip() if title_match else "",
        ref_line,
    )


def normalize_words(text: str) -> set[str]:
    stop = {
        "the", "and", "for", "with", "from", "into", "that", "this", "when", "are",
        "can", "large", "model", "models", "using", "based", "paper", "study",
        "measuring", "impact", "benchmarking", "evaluating",
    }
    return {w.lower() for w in WORD_RE.findall(text) if w.lower() not in stop}


def safe_title(title: str, max_len: int = 70) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._ -]+", "", title).strip().replace(" ", "_")
    return cleaned[:max_len].strip("._-") or "untitled"


def iter_needs(input_root: Path, report_version: str) -> list[RefNeed]:
    versions = ["original", "repaired"] if report_version == "both" else [report_version]
    needs: dict[tuple[str, str, str, str], RefNeed] = {}
    for output_file in sorted(input_root.glob("case*/P*_output.raw.txt")):
        case_dir = output_file.parent
        case_id = case_dir.name.replace("case", "C")
        pass_id = output_file.name.split("_", 1)[0]
        raw = output_file.read_text(encoding="utf-8", errors="replace")
        for version in versions:
            start_marker, end_marker = MARKERS[version]
            refs = parse_refs(section_between(raw, start_marker, end_marker))
            for tag, (arxiv_id, title, ref_line) in refs.items():
                key = (case_id, pass_id, tag, arxiv_id or title)
                needs[key] = RefNeed(case_id, pass_id, tag, arxiv_id, title, ref_line, case_dir)
    return list(needs.values())


def collect_pdf_candidates(search_roots: list[Path]) -> list[Path]:
    candidates: list[Path] = []
    for root in search_roots:
        if root.exists():
            candidates.extend(sorted(root.rglob("*.pdf")))
    return candidates


def find_pdf(need: RefNeed, existing_papers_dir: Path, pdf_candidates: list[Path]) -> Path | None:
    all_candidates = sorted(existing_papers_dir.glob("*.pdf")) + pdf_candidates
    if need.arxiv_id:
        for pdf in all_candidates:
            if need.arxiv_id in pdf.name:
                return pdf
    if need.title:
        title_words = normalize_words(need.title)
        best_pdf = None
        best_score = 0
        for pdf in all_candidates:
            score = len(title_words & normalize_words(pdf.stem))
            if score > best_score:
                best_pdf = pdf
                best_score = score
        if best_pdf and best_score >= 2:
            return best_pdf
    return None


def find_markdown(need: RefNeed, arxiv_text_root: Path) -> Path | None:
    if not need.arxiv_id:
        return None
    path = arxiv_text_root / f"{need.arxiv_id}.md"
    return path if path.exists() else None


def sync_one(need: RefNeed, args: argparse.Namespace, pdf_candidates: list[Path]) -> dict[str, str]:
    papers_dir = need.case_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    label = f"{need.pass_id}_[{need.tag}]_{need.arxiv_id or safe_title(need.title)}"

    pdf_source = find_pdf(need, papers_dir, pdf_candidates)
    if pdf_source:
        target = papers_dir / f"{label}.pdf"
        if pdf_source.resolve() != target.resolve():
            shutil.copy2(pdf_source, target)
        return {"case_id": need.case_id, "pass_id": need.pass_id, "tag": need.tag, "arxiv_id": need.arxiv_id, "target": str(target), "source": str(pdf_source), "kind": "pdf"}

    md_source = find_markdown(need, Path(args.arxiv_text_root).expanduser())
    if md_source:
        target = papers_dir / f"{label}.md"
        if md_source.resolve() != target.resolve():
            shutil.copy2(md_source, target)
        return {"case_id": need.case_id, "pass_id": need.pass_id, "tag": need.tag, "arxiv_id": need.arxiv_id, "target": str(target), "source": str(md_source), "kind": "markdown"}

    return {"case_id": need.case_id, "pass_id": need.pass_id, "tag": need.tag, "arxiv_id": need.arxiv_id, "target": "", "source": "", "kind": "missing", "title": need.title}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", default="presentation/main_memory")
    parser.add_argument("--report-version", choices=["original", "repaired", "both"], default="repaired")
    parser.add_argument("--arxiv-text-root", default="~/.openclaw-main-m1-memory-on/workspace/arxiv_mcp_papers")
    parser.add_argument("--pdf-search-root", action="append", default=["case paper", "presentation/main_memory"])
    parser.add_argument("--manifest-out", default="evaluation/judge/outputs/presentation_paper_sources.json")
    args = parser.parse_args()

    needs = iter_needs(Path(args.input_root), args.report_version)
    pdf_candidates = collect_pdf_candidates([Path(root).expanduser() for root in args.pdf_search_root])
    rows = [sync_one(need, args, pdf_candidates) for need in needs]
    out = Path(args.manifest_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    print(json.dumps({"synced": len(rows), "counts": counts, "manifest": str(out)}, ensure_ascii=False, sort_keys=True))
    missing = [row for row in rows if row["kind"] == "missing"]
    if missing:
        print(json.dumps({"missing": missing}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
