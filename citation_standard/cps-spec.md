# CPS Specification — Full Reference

This is the authoritative specification for the Citation Position Standard (CPS). Load this when you need to resolve edge cases or ambiguous scenarios.

## Design rationale

The prompt.md task requires every factual conclusion to cite paper tag + precise location. Without a fixed grammar, agents produce inconsistent formats:

- `[A] §4.1 节 "Main Results"` — mixes Chinese and symbols
- `[A] 第5页第3段` — ambiguous paragraph counting
- `[A] Introduction 末段` — acceptable but underspecified
- `[A] the part where they discuss limitations` — unacceptable freeform

CPS removes all ambiguity by enforcing a **closed vocabulary × fixed template** grammar.

## Grammar (EBNF)

```ebnf
position_list = single_position , { " / " , single_position } ;

single_position = tag , scope , "::" , element , identifier
                | tag , scope ;                          (* whole-section only *)

tag = "[" , ("A"|"B"|"C"|"D"|"E"|"F") , "]" ;

scope = section_path
      | page_section
      | named_area ;

section_path = "§" , digits , { "." , digits } ;
page_section = "p" , digits , section_path ;
named_area = "Abstract" | "Introduction" | "Conclusion"
           | "Methods" | "Results" | "Discussion" | "RelatedWork" ;

element = "¶" | "T" | "F" | "Eq" | "FN" ;
identifier = digits | "末" ;
```

## Detailed paragraph counting

### When the scope is a numbered section (§3.2)

1. Locate the section heading "3.2" (or equivalent) in the paper.
2. Skip the heading itself.
3. Find the first block of body text after the heading — this is ¶1.
4. Count each subsequent body-text block separated by a blank line or indent.
5. Skip: subsection headings, figure/table captions, displayed equations, footnotes.

### When the scope is a page (p5§3.2)

1. The page number refers to the paper's own pagination (PDF page labels, not PDF file page count).
2. If page numbers are not available in the PDF, omit the `pN` prefix and use only `§N.M`.
3. When a section starts mid-page, ¶1 is the first body-text paragraph that begins on that page within the named section.

### When the scope is a named area (Abstract, Introduction, etc.)

1. "Abstract" starts at the word "Abstract" and ends at the first numbered section or "Introduction" heading.
2. "Introduction" covers the introduction section, numbered (§1) or not.
3. "Conclusion" covers the concluding section, numbered or not.
4. For named areas that have subsections: treat each subsection as a separate scope with `§` notation if numbered; otherwise count paragraphs from the area start.

## Element-specific rules

### Tables (T)

- Use the paper's own table numbering: "Table 1" → `T1`, "Table 2" → `T2`.
- If tables are numbered per-section (e.g., "Table 3.2"), use the full number: `T3.2` in scope `§3`.
- If a table is unnumbered, use its scope + `T` with no digit, and add `¶` position of the nearest reference in text.

### Figures (F)

- Same rules as Tables. Use the paper's figure numbering.
- Multi-panel figures: use `F3(a)` or `F3(b)` if panels are individually referenced.

### Equations (Eq)

- Use the paper's equation numbering.
- Inline equations without numbers: cite the enclosing paragraph instead.

### Footnotes (FN)

- Use only for content footnotes that contain substantive claims.
- Avoid citing reference/bibliographic footnotes that merely list sources.

## Edge cases

### Section starts mid-page

```
p5§3.2::¶1   — first paragraph of §3.2 that appears on page 5
```

### Content spans multiple paragraphs

Cite all relevant paragraphs:
```
[A] §3.2::¶2; §3.2::¶3; §3.2::¶4
```

Even when multiple positions share the same scope, every position after `; ` must repeat the full scope. Do not write shorthand forms such as `[A] §3.2::¶2; ¶3`.

### Claim supported by an entire section

```
[A] §4.1    — no element suffix needed for whole-section references
```

### No numbered sections in the paper

Use named areas only:
```
[A] Introduction::¶3 / [A] Discussion::¶末
```

If the paper has no sections at all: use page numbers if available, otherwise count paragraphs from the start of the paper body and cite as `Body::¶K`.

### PDF without page numbers

Omit `pN` prefix. Use only `§N.M` or named areas.

### Paper with non-standard section numbering

Map to `§` notation: "Chapter 2, Section 3" → `§2.3`. "Part III.A" → `§III.A`. Preserve the paper's numbering scheme when Roman numerals or letters are used.

### Content only in a figure caption

Cite the figure, not a paragraph:
```
[A] §4.2::F3
```

## Comparison: old vs CPS format

| Scenario | Old (ambiguous) | CPS (unambiguous) |
|----------|----------------|-------------------|
| Section 3.2, 2nd paragraph | `[A] §3.2 节` | `[A] §3.2::¶2` |
| Page 5, 3rd paragraph | `[A] 第5页第3段` | `[A] p5§?.?::¶3` or `[A] p5§Introduction::¶3` |
| Abstract | `[A] Abstract` | `[A] Abstract::¶2` |
| Table | `[A] Table 2` | `[A] §4.1::T2` |
| Multiple locations | `[A] §3.2 节和§4.1 节` | `[A] §3.2::¶2; §4.1::T2` |
| Same scope multiple paragraphs | `[A] §3.2::¶2; ¶3` | `[A] §3.2::¶2; §3.2::¶3` |
| Introduction end | `[A] Introduction 末段` | `[A] Introduction::¶末` |

## Validation script reference

A Python validation script is available at `skills/citation-standard/scripts/validate.py` to check CPS compliance in generated reports. See the script for usage.
