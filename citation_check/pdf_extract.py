# -*- coding: utf-8 -*-
"""把 [A]~[F] 的论文标题匹配到 output/caseN/paper/ 下的 PDF，并抽取全文。

匹配策略：标题与文件名都规范化为小写字母数字序列，按最长公共 token 重叠打分，
取分数最高且超过阈值的 PDF。抽取用 PyMuPDF(fitz)，结果缓存到 .cache/。
"""
import os
import re
import json
import hashlib

import fitz  # PyMuPDF


def _norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9一-鿿]+", " ", s)
    return s.strip()


def _tokens(s):
    return [t for t in _norm(s).split() if len(t) > 1]


def list_pdfs(paper_dir):
    if not os.path.isdir(paper_dir):
        return []
    return [
        os.path.join(paper_dir, f)
        for f in os.listdir(paper_dir)
        if f.lower().endswith(".pdf")
    ]


def match_pdf(title, paper_dir, min_score=0.34):
    """按标题在 paper_dir 里找最匹配的 PDF 路径，找不到返回 None。"""
    pdfs = list_pdfs(paper_dir)
    if not pdfs:
        return None
    ttoks = set(_tokens(title))
    if not ttoks:
        return None
    best, best_score = None, 0.0
    for p in pdfs:
        fname = os.path.splitext(os.path.basename(p))[0]
        ftoks = set(_tokens(fname))
        if not ftoks:
            continue
        inter = ttoks & ftoks
        # 以"文件名 token 被标题覆盖的比例"和"标题被文件名覆盖的比例"取较大者
        score = max(len(inter) / len(ftoks), len(inter) / len(ttoks))
        if score > best_score:
            best, best_score = p, score
    return best if best_score >= min_score else None


def _cache_path(pdf_path, cache_dir):
    h = hashlib.md5(os.path.abspath(pdf_path).encode("utf-8")).hexdigest()[:16]
    base = os.path.splitext(os.path.basename(pdf_path))[0][:40]
    return os.path.join(cache_dir, f"{base}_{h}.txt")


def extract_text(pdf_path, cache_dir):
    """抽取 PDF 全文（带缓存）。失败返回 None。"""
    os.makedirs(cache_dir, exist_ok=True)
    cp = _cache_path(pdf_path, cache_dir)
    if os.path.exists(cp):
        with open(cp, "r", encoding="utf-8") as f:
            return f.read()
    try:
        doc = fitz.open(pdf_path)
        chunks = []
        for page in doc:
            chunks.append(page.get_text("text"))
        doc.close()
        text = "\n".join(chunks).strip()
    except Exception as e:
        return None
    if not text:
        return None
    with open(cp, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def get_paper_text(title, paper_dir, cache_dir):
    """返回 (pdf_path 或 None, text 或 None)。"""
    pdf = match_pdf(title, paper_dir)
    if not pdf:
        return None, None
    return pdf, extract_text(pdf, cache_dir)
