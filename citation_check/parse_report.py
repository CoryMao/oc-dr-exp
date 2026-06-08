# -*- coding: utf-8 -*-
"""解析 output/caseN/runM.txt。

每个文件含两版报告：
  # ORIGINAL_REPORT   -> repair_or_not = "no"
  # REPAIRED_REPORT    -> repair_or_not = "yes"
（中间可能夹着 # REFCHECKER_REPAIR_LOG，需忽略，绝不作为判据。）

每版有「第二部分：逐条结论」和「第三部分：引用论文清单」。
逐条结论格式：
  - <claim 文本，可能跨多行>
    出处：[A] §5::¶1; Abstract::¶1
"""
import re

# ---- 版本切分 ----------------------------------------------------------

def _slice(text, start_pat, end_pats):
    m = re.search(start_pat, text)
    if not m:
        return None
    start = m.end()
    end = len(text)
    for ep in end_pats:
        em = re.search(ep, text[start:])
        if em:
            end = min(end, start + em.start())
    return text[start:end]


def split_versions(raw):
    """返回 [(repair_or_not, version_text), ...]。

    用 ORIGINAL_REPORT / REPAIRED_REPORT 标题切分；
    REFCHECKER_REPAIR_LOG / RUN_SUMMARY 作为边界但不作为内容。
    """
    out = []
    orig = _slice(
        raw,
        r"#\s*ORIGINAL_REPORT",
        [r"#\s*REFCHECKER_REPAIR_LOG", r"#\s*REPAIRED_REPORT", r"#\s*RUN_SUMMARY"],
    )
    if orig:
        out.append(("no", orig))
    rep = _slice(
        raw,
        r"#\s*REPAIRED_REPORT",
        [r"#\s*REFCHECKER_REPAIR_LOG", r"#\s*RUN_SUMMARY"],
    )
    if rep:
        out.append(("yes", rep))
    # 容错：若没有任何标题，把整篇当作单版（repair_or_not=no）
    if not out:
        out.append(("no", raw))
    return out


# ---- 段落抽取 ----------------------------------------------------------

# 第二部分标题：兼容"第二部分：逐条结论""## 第二部分..."等
_SEC2 = r"第二部分[：:]\s*逐条结论"
_SEC3 = r"第三部分[：:]\s*引用论文清单"
_SEC1 = r"第一部分"


def _section_body(version_text, start_pat, end_pats):
    return _slice(version_text, start_pat, end_pats)


def parse_claims(version_text):
    """从一版文本里抽取 [(claim_text, citation_str), ...]。

    每个 claim 以行首 '- ' 起始，'出处：' 之前是 claim 文本，之后是引用串。
    """
    body = _section_body(version_text, _SEC2, [_SEC3])
    if body is None:
        return []
    items = []
    # 按行首 "- " 切块（保留跨行 claim）
    chunks = re.split(r"\n\s*-\s+", "\n" + body)
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        # 拆出处：支持"出处：""出处:"
        m = re.search(r"出处[：:]\s*(.+)", ch, re.S)
        if not m:
            # 没有出处行的块，跳过（多半是小标题/空块）
            continue
        citation = m.group(1).strip()
        claim_text = ch[: m.start()].strip()
        # 清掉 claim 内部换行带来的缩进
        claim_text = re.sub(r"\s*\n\s*", "", claim_text).strip()
        citation = re.sub(r"\s*\n\s*", " ", citation).strip()
        if claim_text:
            items.append((claim_text, citation))
    return items


# ---- 第三部分：[A]~[F] -> 论文条目 -------------------------------------

_REF_LINE = re.compile(r"^\s*-\s*\[([A-Z])\]\s*(.+?)\s*$")


def parse_references(version_text):
    """返回 {tag: {"ref_line": str, "title": str}}。"""
    body = _section_body(version_text, _SEC3, [r"#\s*\w", r"```", r"第[一二三四]部分"])
    refs = {}
    if body is None:
        return refs
    for line in body.splitlines():
        m = _REF_LINE.match(line)
        if not m:
            continue
        tag = m.group(1)
        rest = m.group(2).strip()
        refs[tag] = {"ref_line": rest, "title": _extract_title(rest)}
    return refs


def _extract_title(ref_line):
    """从清单行里抠出论文标题（引号内），用于和 PDF 文件名匹配。"""
    m = re.search(r'[""\"]([^""\"]+)[""\"]', ref_line)
    if m:
        return m.group(1).strip()
    # 退化：取年份后的第一段
    m = re.search(r"\)\s*[\.。]?\s*(.+)", ref_line)
    return (m.group(1).strip() if m else ref_line)[:120]


# ---- 引用串里出现了哪些 tag -------------------------------------------

def tags_in_citation(citation_str):
    """从 '[A] §5; [B] Abstract' 里取出 ['A','B']（按出现顺序去重）。"""
    seen, out = set(), []
    for t in re.findall(r"\[([A-Z])\]", citation_str):
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out
