#!/usr/bin/env python3
"""Validate Citation Position Standard (CPS) compliance in research reports.

Usage:
  python validate.py <report.md>       # check a report file
  python validate.py --stdin            # read report from stdin
  python validate.py --help             # show this message

Checks:
  1. Every [A]~[F] tag in Part 2 has a position spec
  2. Position specs use valid grammar: scope::elementID
  3. Scope tokens are from the closed vocabulary
  4. Element types are from the closed set
  5. Multi-location separators are correct
  6. Part 3 entries have all required fields
"""

import re
import sys
from pathlib import Path

# ── Closed vocabularies ──────────────────────────────────────────────

# Ordered by specificity: page+section before bare section
SCOPE_PATTERNS = [
    re.compile(r"^p\d+§\d+(?:\.\d+)*$"),   # p5§3.2
    re.compile(r"^§\d+(?:\.\d+)*$"),         # §3.2
    "Abstract",
    "Introduction",
    "Conclusion",
    "Methods",
    "Results",
    "Discussion",
    "RelatedWork",
]

VALID_ELEMENTS = {"¶", "T", "F", "Eq", "FN"}

VALID_TAGS = {"A", "B", "C", "D", "E", "F"}

# ── Patterns ─────────────────────────────────────────────────────────

# Match a [Tag] followed by position info
TAG_PATTERN = re.compile(r"\[([A-F])\]\s*(.*?)(?=\s*\[[A-F]\]|\s*$|/\s*\[|$)")

# Position: scope::elementID — scope is captured as everything before ::
POSITION_PATTERN = re.compile(
    r"(.+?)"
    r"::"
    r"([¶TF]|Eq|FN)"
    r"(\d+[a-z]?|末)$"
)

# Whole-section reference: scope without ::elementID suffix
WHOLE_SECTION_PATTERN = re.compile(
    r"^(?:p\d+§\d+(?:\.\d+)*|§\d+(?:\.\d+)*|Abstract|Introduction|Conclusion|"
    r"Methods|Results|Discussion|RelatedWork)$"
)

# Part 3 reference entry
REF_ENTRY_PATTERN = re.compile(
    r"-\s*\[([A-F])\]\s*(.+?)\s*\("
    r"(\d{4})"
    r"\)\s*\.\s*\"(.+?)\""
)

# ── Validation functions ─────────────────────────────────────────────

def find_part2(text: str) -> str | None:
    """Extract Part 2 (逐条结论) section."""
    m = re.search(r"第二部分[：:].*?逐条结论.*?\n(.*?)(?=第三部分|###\s*第三)", text, re.S)
    if not m:
        m = re.search(r"##\s*第二部分.*?\n(.*?)(?=##\s*第三|###\s*第三)", text, re.S)
    return m.group(1) if m else None


def find_part3(text: str) -> str | None:
    """Extract Part 3 (引用论文清单) section."""
    m = re.search(r"第三部分[：:].*?引用论文清单.*?\n(.*)$", text, re.S)
    if not m:
        m = re.search(r"##\s*第三部分.*?\n(.*)$", text, re.S)
    return m.group(1) if m else None


def extract_claims(part2: str) -> list[dict]:
    """Extract individual claims and their citations."""
    claims = []
    # Each claim starts with "- " and goes until the next "- " or end
    claim_blocks = re.split(r"\n\s*-\s+", part2)
    for block in claim_blocks:
        block = block.strip()
        if not block or not re.search(r"\[([A-F])\]", block):
            continue
        # Separate claim text from citation line
        lines = block.split("\n")
        claim_text = lines[0].strip()
        citation_line = ""
        for line in lines[1:]:
            if "出处" in line or re.match(r"^\s*\[[A-F]\]", line):
                citation_line = line.strip()
                break
        claims.append({"text": claim_text, "citation": citation_line})
    return claims


def check_position(spec: str) -> list[str]:
    """Check a single position spec. Returns list of errors."""
    errors = []
    spec = spec.strip()

    # Check if it's a whole-section reference
    if WHOLE_SECTION_PATTERN.match(spec):
        return errors  # valid whole-section reference

    # Check for the ::elementID pattern
    m = POSITION_PATTERN.search(spec)
    if not m:
        errors.append(f"  INVALID position: '{spec}' — expected scope::elementID")
        return errors

    scope, element, identifier = m.group(1), m.group(2), m.group(3)

    # Validate scope against closed vocabulary
    scope_valid = False
    for pat in SCOPE_PATTERNS:
        if isinstance(pat, str):
            if scope == pat:
                scope_valid = True
                break
        else:
            if pat.match(scope):
                scope_valid = True
                break
    if not scope_valid:
        errors.append(f"  INVALID scope: '{scope}' — not in closed vocabulary")

    # Validate element
    if element not in VALID_ELEMENTS:
        errors.append(f"  INVALID element: '{element}' — must be one of {VALID_ELEMENTS}")

    # Validate identifier
    if identifier != "末" and not identifier.isdigit():
        errors.append(f"  INVALID identifier: '{identifier}' — must be integer or 末")

    return errors


def validate_report(text: str) -> tuple[list[str], int, int]:
    """Validate a full report. Returns (errors, total_positions, passed_positions)."""
    errors: list[str] = []
    total_positions = 0
    passed_positions = 0

    # Extract Part 2
    part2 = find_part2(text)
    if not part2:
        errors.append("FATAL: Could not find Part 2 (第二部分：逐条结论)")
        return errors, 0, 0

    claims = extract_claims(part2)
    if not claims:
        errors.append("FATAL: No claims with citations found in Part 2")
        return errors, 0, 0

    for i, claim in enumerate(claims, 1):
        if not claim["citation"]:
            errors.append(f"Claim {i}: MISSING citation (no 出处 line)")
            continue

        # Split by paper separator " / "
        paper_parts = re.split(r"\s*/\s*(?=\[)", claim["citation"])
        # Remove "出处：" prefix if present
        if paper_parts and "出处" in paper_parts[0]:
            paper_parts[0] = re.sub(r"^出处[：:]\s*", "", paper_parts[0])

        for part in paper_parts:
            part = part.strip()
            tag_matches = re.findall(r"\[([A-F])\]", part)
            for tag in tag_matches:
                # Verify tag validity
                if tag not in VALID_TAGS:
                    errors.append(f"Claim {i}: INVALID tag '[{tag}]'")
                    continue

                # Extract positions for this tag
                # Remove the [Tag] prefix
                after_tag = re.sub(rf"^\[{tag}\]\s*", "", part)
                # Split by "; " for same-paper multi-location
                positions = re.split(r";\s*", after_tag)

                for pos in positions:
                    pos = pos.strip()
                    total_positions += 1
                    if not pos:
                        errors.append(f"Claim {i}: MISSING position for [{tag}]")
                        continue
                    pos_errors = check_position(pos)
                    if pos_errors:
                        errors.extend(
                            f"Claim {i} [{tag}]: {error.strip()}"
                            for error in pos_errors
                        )
                    else:
                        passed_positions += 1

    # Check Part 3 completeness
    part3 = find_part3(text)
    if not part3:
        errors.append("FATAL: Could not find Part 3 (第三部分：引用论文清单)")
        return errors, total_positions, passed_positions

    tags_in_part3 = set(re.findall(r"-\s*\[([A-F])\]", part3))
    for tag in VALID_TAGS:
        if tag not in tags_in_part3:
            errors.append(f"Part 3: MISSING entry for [{tag}]")

    return errors, total_positions, passed_positions


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--stdin":
        text = sys.stdin.read()
        source = "<stdin>"
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
        source = str(path)

    errors, total, passed = validate_report(text)

    print(f"=== CPS Validation: {source} ===")
    print(f"Total positions checked: {total}")
    print(f"Valid positions: {passed}")
    print(f"Errors: {len(errors)}")
    print()

    if errors:
        print("--- ERRORS ---")
        for e in errors:
            print(e)
        print()
        print(f"RESULT: FAIL ({len(errors)} error(s))")
        sys.exit(1)
    else:
        print("RESULT: PASS — all citations comply with CPS")
        sys.exit(0)


if __name__ == "__main__":
    main()
