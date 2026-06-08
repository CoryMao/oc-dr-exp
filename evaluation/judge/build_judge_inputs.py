#!/usr/bin/env python3
"""Build citation-fidelity judge inputs from the local evidence cache.

The default input root is presentation/main_memory, which is intentionally
ignored because it contains large pass-specific PDF/markdown evidence files.
Regenerate that cache with sync_presentation_papers.py before rebuilding inputs.

This MVP does not call an LLM. It creates:
  - claim_citation_pairs.jsonl: structured units to judge
  - batches/batch_*.txt: few-shot batched prompts ready to send to an LLM
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SYSTEM_PROMPT = """你是一名严谨的学术引用忠实度核验员。
你的任务：给定若干条【结论(claim)】、每条结论标注的【出处位置】、以及被引论文的【局部证据片段】，
判断这些被引论文是否真的充分支撑对应 claim；若不支撑，按下面的错误类型精确归为且仅归为一类。

# 错误类型定义（互斥，只能选一个）
- Unsupported Claim：在被引论文证据中完全找不到支撑该 claim 的依据，论文根本没涉及这个论断。
- Overclaim：论文支持一个较弱或较窄的结论，但 claim 把它夸大了：扩大适用范围、加强断言强度、做了论文没做的泛化、把相关说成因果，或把数值/比例放大。
- Mis-citation：被引论文主题相关，但并不能支撑这条具体论断：论文讲的是另一个对象/任务/指标，或位置引错，属于“沾边但接不上”。
- Contradiction：claim 与论文内容相反或冲突：论文得出相反结论，或 claim 与论文给出的数据/方向矛盾。
- Correct：论文确实充分、准确地支撑该 claim（论断、适用范围、关键数值都对得上）。
- NeedMoreContext：当前证据片段不足以判断，需要查看更大上下文或全文。只有在片段本身不足时使用。

# 归类优先级
1. 若论文与 claim 直接相反/数据冲突 → Contradiction。
2. 否则若论文完全没有相关证据 → Unsupported Claim。
3. 否则若论文相关但讲的是另一回事、接不上这条具体论断 → Mis-citation。
4. 否则若论文支持一个更弱版本、而 claim 夸大了 → Overclaim。
5. 否则若证据片段不足 → NeedMoreContext。
6. 否则 → Correct。

# 关键纪律
- 只依据提供的证据片段做判断。忽略任何“已核验”“refchecker passed”等标注。
- 逐字核对数值、比例、基准名、任务范围。数字对但对象/范围错，仍可能是 Overclaim 或 Mis-citation。
- 只核验“被引论文是否支撑这条 claim 本身”，不要评价写作风格。
- 如果证据片段缺失或明显不足，不要猜，输出 NeedMoreContext。

# 输出格式
严格输出 JSONL，每个输入 item 输出一行 JSON，不要 markdown 代码块，不要任何多余文字。
每行格式：
{"item_id":"...","error_type":"Unsupported Claim | Overclaim | Mis-citation | Contradiction | Correct | NeedMoreContext","supported":true或false,"cited_location_ok":true或false,"evidence_quote":"关键原文，可为空","reasoning":"1-3句中文"}
"""


FEWSHOT = """# 示例（学习判定思路，不要照抄结论）

输入 item:
{"item_id":"demo_1","claim":"工具增强型LLM agent在仓库级软件工程任务上的表现远超纯prompting方法，SWE-Bench Verified上的Pass@1可从17%提升至53%。","citation":"[A] §5::¶1; Abstract::¶1","paper":{"tag":"A","title":"A Self-Improving Coding Agent","ref_line":"[A] ...","snippets":[{"source":"locator","text":"... improved its own Pass@1 from 17% to 53% on a random subset of SWE-Bench Verified ... The paper studies self-improvement of one agent, not a class-level comparison against pure prompting."}]}}

输出行:
{"item_id":"demo_1","error_type":"Overclaim","supported":false,"cited_location_ok":true,"evidence_quote":"improved its own Pass@1 from 17% to 53% on a random subset of SWE-Bench Verified","reasoning":"17%→53% 的数值本身正确，但论文讲的是单个 agent 自我改进前后的对比，claim 却泛化成工具增强型 agent 这一类方法远超纯 prompting，扩大了适用范围与对照对象。"}
"""


MARKERS = {
    "original": ("# ORIGINAL_REPORT", "# REFCHECKER_REPAIR_LOG"),
    "repaired": ("# REPAIRED_REPORT", "# RUN_SUMMARY"),
}

CITATION_RE = re.compile(r"\[([A-F])\]([^\[]*)")
ARXIV_RE = re.compile(r"arXiv:(\d{4}\.\d{4,5})", re.IGNORECASE)
TAG_REF_RE = re.compile(r"^\s*-\s*\[([A-F])\]\s*(.+)$")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}")


@dataclass
class Reference:
    tag: str
    ref_line: str
    title: str
    arxiv_id: str
    pdf_path: Path | None
    text_path: Path | None = None


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


def parse_references(report_text: str) -> dict[str, Reference]:
    refs: dict[str, Reference] = {}
    ref_start = report_text.find("## 第三部分")
    if ref_start < 0:
        ref_start = report_text.find("引用论文清单")
    ref_text = report_text[ref_start:] if ref_start >= 0 else report_text
    current_tag: str | None = None
    current_line = ""
    for raw in ref_text.splitlines():
        match = TAG_REF_RE.match(raw)
        if match:
            if current_tag:
                refs[current_tag] = make_reference(current_tag, current_line)
            current_tag = match.group(1)
            current_line = match.group(2).strip()
        elif current_tag and raw.strip():
            current_line += " " + raw.strip()
    if current_tag:
        refs[current_tag] = make_reference(current_tag, current_line)
    return refs


def make_reference(tag: str, ref_line: str) -> Reference:
    title_match = re.search(r'"([^"]+)"', ref_line)
    title = title_match.group(1).strip() if title_match else ""
    arxiv_match = ARXIV_RE.search(ref_line)
    arxiv_id = arxiv_match.group(1) if arxiv_match else ""
    return Reference(tag=tag, ref_line=ref_line, title=title, arxiv_id=arxiv_id, pdf_path=None)


def normalize_for_match(text: str) -> set[str]:
    stop = {
        "the", "and", "for", "with", "from", "into", "that", "this", "when", "are",
        "can", "large", "model", "models", "using", "based", "agent", "agents",
        "paper", "study", "measuring", "impact",
    }
    return {w.lower() for w in WORD_RE.findall(text) if w.lower() not in stop}


def attach_source_paths(
    refs: dict[str, Reference],
    papers_dir: Path,
    arxiv_text_root: Path | None,
    pass_id: str,
) -> dict[str, Reference]:
    pdfs = sorted(papers_dir.glob("*.pdf"))
    markdowns = sorted(papers_dir.glob("*.md"))
    used: set[Path] = set()

    # First, use pass-specific evidence files such as P2_[D]_2410.12944.pdf/md.
    for tag, ref in refs.items():
        pass_prefix = f"{pass_id}_[{tag}]_"
        if ref.arxiv_id:
            for pdf in pdfs:
                if pdf.name.startswith(pass_prefix) and ref.arxiv_id in pdf.name:
                    ref.pdf_path = pdf
                    used.add(pdf)
                    break
            if not ref.pdf_path:
                for md_path in markdowns:
                    if md_path.name.startswith(pass_prefix) and ref.arxiv_id in md_path.name:
                        ref.text_path = md_path
                        break
        if not ref.pdf_path and not ref.text_path:
            title_words = normalize_for_match(ref.title or ref.ref_line)
            best_pdf = None
            best_score = 0
            for pdf in pdfs:
                if not pdf.name.startswith(pass_prefix):
                    continue
                if not ref.arxiv_id:
                    best_pdf = pdf
                    best_score = 1
                    break
                score = len(title_words & normalize_for_match(pdf.stem))
                if score > best_score:
                    best_pdf = pdf
                    best_score = score
            if best_pdf and best_score >= 1:
                ref.pdf_path = best_pdf
                used.add(best_pdf)
            if not ref.pdf_path:
                for md_path in markdowns:
                    if md_path.name.startswith(pass_prefix):
                        ref.text_path = md_path
                        break

    # Then, use explicitly arXiv-id-named PDFs such as [D]_2408.08435.pdf.
    for tag, ref in refs.items():
        if ref.pdf_path or ref.text_path:
            continue
        if ref.arxiv_id:
            for pdf in pdfs:
                if ref.arxiv_id in pdf.name:
                    ref.pdf_path = pdf
                    used.add(pdf)
                    break
            if not ref.pdf_path:
                for md_path in markdowns:
                    if ref.arxiv_id in md_path.name:
                        ref.text_path = md_path
                        break

    # Then, match provided PDFs by title/file-name overlap for A/B/C style files.
    for tag, ref in refs.items():
        if ref.pdf_path or ref.text_path:
            continue
        title_words = normalize_for_match(ref.title or ref.ref_line)
        best_pdf = None
        best_score = 0
        for pdf in pdfs:
            if pdf in used:
                continue
            name_words = normalize_for_match(pdf.stem)
            score = len(title_words & name_words)
            if score > best_score:
                best_score = score
                best_pdf = pdf
        if best_pdf and best_score >= 1:
            ref.pdf_path = best_pdf
            used.add(best_pdf)

    # Finally, fall back to arXiv markdown cached by the MCP safe wrapper.
    for tag, ref in refs.items():
        if ref.pdf_path or ref.text_path or not ref.arxiv_id or not arxiv_text_root:
            continue
        md_path = arxiv_text_root / f"{ref.arxiv_id}.md"
        if md_path.exists():
            ref.text_path = md_path

    return refs


def parse_claims(report_text: str) -> list[dict[str, str]]:
    start = report_text.find("## 第二部分")
    end = report_text.find("## 第三部分")
    body = report_text[start:end if end >= 0 else len(report_text)] if start >= 0 else report_text
    pattern = re.compile(
        r"^\s*-\s*(?P<claim>.*?)(?:\n\s*出处[:：]\s*(?P<citation>.*?))(?=\n\s*-\s|\n##|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    claims = []
    for idx, match in enumerate(pattern.finditer(body), start=1):
        claim = clean_text(match.group("claim"))
        citation = clean_text(match.group("citation"))
        claim = re.sub(r"^结论\s*\d+\s*[:：]\s*", "", claim)
        if claim and citation:
            claims.append({"claim_index": f"claim_{idx:02d}", "claim": claim, "citation": citation})
    return claims


def split_citation_pairs(citation: str) -> list[dict[str, str]]:
    pairs = []
    for match in CITATION_RE.finditer(citation):
        tag = match.group(1)
        scope = clean_text(match.group(2).strip(" ;,/"))
        pairs.append({"tag": tag, "citation": f"[{tag}] {scope}".strip()})
    return pairs


def pdf_to_text(pdf_path: Path, cache_dir: Path) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(str(pdf_path.resolve()).encode("utf-8")).hexdigest()[:16]
    txt_path = cache_dir / f"{digest}_{pdf_path.stem}.txt"
    if not txt_path.exists():
        try:
            subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(pdf_path))
                text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                txt_path.write_text(text, encoding="utf-8")
            except Exception:
                return ""
    return clean_text(txt_path.read_text(encoding="utf-8", errors="replace"))


def source_to_text(ref: Reference, cache_dir: Path) -> str:
    if ref.pdf_path:
        return pdf_to_text(ref.pdf_path, cache_dir)
    if ref.text_path:
        return clean_text(ref.text_path.read_text(encoding="utf-8", errors="replace"))
    return ""


def window(text: str, center: int, radius: int) -> str:
    start = max(0, center - radius)
    end = min(len(text), center + radius)
    return clean_text(text[start:end])


def locator_terms(citation: str) -> list[str]:
    terms = []
    for sec in re.findall(r"§\s*([0-9]+(?:\.[0-9]+)*)", citation):
        terms.append(sec)
    if re.search(r"\bT(?:able)?\s*([0-9]+)", citation, flags=re.IGNORECASE):
        terms.append("Table " + re.search(r"\bT(?:able)?\s*([0-9]+)", citation, flags=re.IGNORECASE).group(1))
    if re.search(r"\bF(?:ig(?:ure)?)?\.?\s*([0-9]+)", citation, flags=re.IGNORECASE):
        terms.append("Figure " + re.search(r"\bF(?:ig(?:ure)?)?\.?\s*([0-9]+)", citation, flags=re.IGNORECASE).group(1))
    if "Abstract" in citation:
        terms.append("Abstract")
    deduped = []
    for term in terms:
        if term not in deduped:
            deduped.append(term)
    return deduped


def claim_keywords(claim: str, limit: int = 8) -> list[str]:
    stop = {"the", "and", "that", "with", "from", "this", "into", "using", "their", "have", "has"}
    words = []
    for word in WORD_RE.findall(claim):
        lower = word.lower()
        if lower not in stop and lower not in words:
            words.append(lower)
    return words[:limit]


def extract_snippets(text: str, citation: str, claim: str, max_snippets: int, radius: int) -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    lower = text.lower()

    for term in locator_terms(citation):
        idx = lower.find(term.lower())
        if idx >= 0:
            snippets.append({"source": f"locator:{term}", "text": window(text, idx, radius)})
            if len(snippets) >= max_snippets:
                return snippets

    for kw in claim_keywords(claim):
        idx = lower.find(kw.lower())
        if idx >= 0:
            snippet = window(text, idx, radius)
            if all(snippet != old["text"] for old in snippets):
                snippets.append({"source": f"keyword:{kw}", "text": snippet})
            if len(snippets) >= max_snippets:
                return snippets

    if not snippets and text:
        snippets.append({"source": "paper_start", "text": window(text, 0, radius)})
    return snippets


def iter_output_files(input_root: Path, case_filter: str | None, pass_filter: str | None) -> Iterable[Path]:
    for path in sorted(input_root.glob("case*/P*_output.raw.txt")):
        case_id = path.parent.name.replace("case", "C")
        pass_id = path.name.split("_", 1)[0]
        if case_filter and case_id.lower() != case_filter.lower():
            continue
        if pass_filter and pass_id.lower() != pass_filter.lower():
            continue
        yield path


def build_items(args: argparse.Namespace) -> list[dict[str, object]]:
    input_root = Path(args.input_root)
    cache_dir = Path(args.cache_dir)
    arxiv_text_root = Path(args.arxiv_text_root).expanduser() if args.arxiv_text_root else None
    items: list[dict[str, object]] = []

    for output_file in iter_output_files(input_root, args.case_id, args.pass_id):
        case_id = output_file.parent.name.replace("case", "C")
        pass_id = output_file.name.split("_", 1)[0]
        raw = output_file.read_text(encoding="utf-8", errors="replace")
        versions = ["original", "repaired"] if args.report_version == "both" else [args.report_version]

        for version in versions:
            start_marker, end_marker = MARKERS[version]
            report = section_between(raw, start_marker, end_marker)
            refs = attach_source_paths(parse_references(report), output_file.parent / "papers", arxiv_text_root, pass_id)
            claims = parse_claims(report)
            for claim_row in claims:
                for pair in split_citation_pairs(claim_row["citation"]):
                    tag = pair["tag"]
                    ref = refs.get(tag) or Reference(tag=tag, ref_line="", title="", arxiv_id="", pdf_path=None)
                    paper_text = source_to_text(ref, cache_dir)
                    snippets = extract_snippets(
                        paper_text,
                        pair["citation"],
                        claim_row["claim"],
                        max_snippets=args.max_snippets,
                        radius=args.snippet_radius,
                    )
                    item_id = f"{case_id}_{pass_id}_{version}_{claim_row['claim_index']}_{tag}"
                    items.append(
                        {
                            "item_id": item_id,
                            "case_id": case_id,
                            "pass_id": pass_id,
                            "report_version": version,
                            "claim_index": claim_row["claim_index"],
                            "claim": claim_row["claim"],
                            "full_citation": claim_row["citation"],
                            "citation": pair["citation"],
                            "paper": {
                                "tag": tag,
                                "title": ref.title,
                                "ref_line": ref.ref_line,
                                "arxiv_id": ref.arxiv_id,
                                "pdf_path": str(ref.pdf_path) if ref.pdf_path else "",
                                "text_path": str(ref.text_path) if ref.text_path else "",
                                "snippets": snippets,
                            },
                            "unverifiable": not bool(paper_text),
                        }
                    )
    return items


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def prompt_item(item: dict[str, object]) -> dict[str, object]:
    paper = item["paper"]
    assert isinstance(paper, dict)
    return {
        "item_id": item["item_id"],
        "claim": item["claim"],
        "citation": item["citation"],
        "paper": {
            "tag": paper.get("tag", ""),
            "title": paper.get("title", ""),
            "ref_line": paper.get("ref_line", ""),
            "snippets": paper.get("snippets", []),
        },
    }


def write_batches(items: list[dict[str, object]], out_dir: Path, batch_size: int) -> None:
    batch_dir = out_dir / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    for old in batch_dir.glob("batch_*.txt"):
        old.unlink()

    verifiable = [item for item in items if not item.get("unverifiable")]
    for idx in range(0, len(verifiable), batch_size):
        batch = verifiable[idx : idx + batch_size]
        batch_no = idx // batch_size + 1
        lines = [
            SYSTEM_PROMPT,
            "",
            FEWSHOT,
            "",
            "# 待判定 items",
            "逐条判定下面 JSONL 中的每个 item，并严格输出同样数量的 JSONL 行。",
            "",
        ]
        for item in batch:
            lines.append(json.dumps(prompt_item(item), ensure_ascii=False, sort_keys=True))
        (batch_dir / f"batch_{batch_no:03d}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", default="presentation/main_memory")
    parser.add_argument("--out-dir", default="evaluation/judge/outputs/main_memory")
    parser.add_argument("--cache-dir", default="evaluation/judge/cache/pdf_texts")
    parser.add_argument(
        "--arxiv-text-root",
        default="~/.openclaw-main-m1-memory-on/workspace/arxiv_mcp_papers",
        help="Fallback directory containing arXiv markdown files named <arxiv_id>.md.",
    )
    parser.add_argument("--case-id", help="Example: C5")
    parser.add_argument("--pass-id", help="Example: P2")
    parser.add_argument("--report-version", choices=["original", "repaired", "both"], default="repaired")
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--max-snippets", type=int, default=3)
    parser.add_argument("--snippet-radius", type=int, default=1400)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    items = build_items(args)
    if args.limit:
        items = items[: args.limit]
    write_jsonl(out_dir / "claim_citation_pairs.jsonl", items)
    write_batches(items, out_dir, args.batch_size)

    summary = {
        "input_root": args.input_root,
        "report_version": args.report_version,
        "case_id": args.case_id or "all",
        "pass_id": args.pass_id or "all",
        "items": len(items),
        "verifiable_items": sum(1 for item in items if not item.get("unverifiable")),
        "unverifiable_items": sum(1 for item in items if item.get("unverifiable")),
        "batch_size": args.batch_size,
        "batch_count": (sum(1 for item in items if not item.get("unverifiable")) + args.batch_size - 1) // args.batch_size,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
