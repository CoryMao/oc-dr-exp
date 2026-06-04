---
name: citation-standard
description: "Enforce standardized citation position format in research reports. Every claim must cite source tag + precise structural location using a fixed grammar with closed vocabularies."
metadata:
  openclaw:
    emoji: "📌"
    always: false
disable-model-invocation: false
---

# Citation Position Standard (CPS)

Enforce an unambiguous citation position grammar on every research report. No freeform positions. Every `[Tag]` must be followed by a position string from the templates below.

## When to apply

Apply this standard whenever you generate a report that includes:

- Paper labels [A]~[F] (or any [Tag] system) with position annotations
- Per-claim source attribution with location references
- The prompt.md three-part research report format

## Core rule

Every `[Tag]` in a conclusion MUST be immediately followed by one or more position specs. Use the exact templates below — do not invent variants.

## Position specification grammar

### Template

```
[Tag] {scope}::{element}{id}
```

The `::{element}{id}` suffix is MANDATORY for paragraph-level references. It may be omitted only for whole-section or whole-paper references.

### Scope (closed vocabulary — pick exactly one)

| Scope token | Meaning | Example |
|-------------|---------|---------|
| `§N.M` | Numbered section (preferred) | `§3.2` |
| `§N.M.K` | Numbered subsection | `§3.2.1` |
| `pN§N.M` | Page + section (when page numbers explicit in PDF) | `p5§3.2` |
| `Abstract` | Paper abstract | `Abstract` |
| `Introduction` | Unnumbered introduction | `Introduction` |
| `Conclusion` | Unnumbered conclusion | `Conclusion` |
| `Methods` | Methods section | `Methods` |
| `Results` | Results section | `Results` |
| `Discussion` | Discussion section | `Discussion` |
| `RelatedWork` | Related work section | `RelatedWork` |

Rule: prefer `§N.M` over unnumbered names. Only use `Introduction`/`Conclusion`/etc. when the paper does not number those sections.

### Element type + identifier (pick one per position)

| Token | Meaning | Example |
|-------|---------|---------|
| `¶K` | Body-text paragraph K (counted from scope start) | `¶2` |
| `¶末` | Last body-text paragraph in the scope | `¶末` |
| `TK` | Table K (paper-global numbering) | `T2` |
| `FK` | Figure K (paper-global numbering) | `F3` |
| `EqK` | Equation K | `Eq7` |
| `FN` | Footnote N | `F12` |

For whole-section or whole-paper claims (rare):
- `[A] §3` — entire section 3
- `[A] §3.2` — entire subsection 3.2

### Paragraph counting rules (read carefully)

1. A paragraph = a contiguous block of body text separated by a blank line or first-line indent.
2. Count from 1 at the start of the enclosing scope (section, page, or named area).
3. **Skip**: section/subsection headings, figure/table captions, standalone displayed equations, footnotes, page headers/footers.
4. A paragraph that crosses a page break is counted on the page where it begins.
5. "¶末" means the final body-text paragraph of the specified scope.

### Multi-location separators

- **Same paper, different locations**: `; ` (semicolon + space)
- **Different papers**: ` / ` (space + slash + space)
- Even when multiple positions share the same scope, every position after `; ` MUST repeat the full scope.
  - Correct: `[A] §3.2::¶2; §3.2::¶3`
  - Incorrect: `[A] §3.2::¶2; ¶3`

### Complete examples

```
- 配备工具增强的LLM agent在仓库级软件工程基准测试上的表现远优于纯prompting方法，
  SWE-Bench Verified上的Pass@1从17%提升至53%。
  出处：[A] §4.1::¶2; §4.1::T2 / [B] §3.2::¶1 / [D] Abstract::¶2

- 多模态模型在医学影像诊断中的准确率已超过放射科医师平均水平。
  出处：[A] §2.3::¶3 / [C] p7§5.1::¶1; p7§5.1::F4 / [E] Results::¶末

- 增加模型参数量对推理能力的边际收益在大约500B参数后急剧递减。
  出处：[B] §5::¶末 / [D] §4.2::¶2; §6.1::¶1 / [F] Discussion::¶2
```

## Reference list format

In Part 3 of the report, each paper entry must include ALL of these fields, exactly in this order:

```
- [Tag] 作者 (年份). "标题." 发表刊物/预印本平台. 标识符. 检索词: {检索策略}
```

For fetch failures, append `⚠ 未能获取全文：{原因}` at the end of the entry.

## Self-check before output

Before finalizing Part 2, verify every conclusion against this checklist:

1. Every `[Tag]` has a `::{element}{id}` suffix (or is explicitly a whole-section reference).
2. Every scope token is from the closed vocabulary above.
3. Every element type is from the closed set `¶`, `T`, `F`, `Eq`, `FN`.
4. Paragraph counts are integers (or `末`), not ranges or approximations.
5. Multi-source separators use `; ` (same paper) and ` / ` (different papers).
6. Every same-paper position after `; ` repeats the full scope.
7. No freeform descriptions like "第3段", "section about X", "the part where they discuss Y".
8. Self-searched papers [D][E][F] include search strategy in Part 3.
