#!/usr/bin/env python3
"""Validate source line references in Vulkan CTS wiki Markdown.

Besides checking that a referenced file and line range exist, this validator
resolves named C/C++ functions in link labels and compares the claimed range
with the function's balanced-brace definition span.  Unnamed links and
non-C/C++ targets retain bounds-only validation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)#]+)#L(\d+)(?:-L(\d+))?\)")
CODE_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inc", ".inl", ".ipp", ".tpp", ".m", ".mm"}
SYMBOL_RE = re.compile(r"(?:`+|\b)([A-Za-z_][A-Za-z0-9_:~]*(?:\s*<[^`>]+>)?)\s*(?:\(\))?(?:`+|\b)")
CONTROL_WORDS = {"if", "for", "while", "switch", "catch", "sizeof", "return"}

@dataclass
class Finding:
    rule: str
    severity: str
    wiki_file: str
    wiki_line: int
    target: str
    claimed_start: int
    claimed_end: int
    symbol: Optional[str] = None
    actual_start: Optional[int] = None
    actual_end: Optional[int] = None
    suggestion: Optional[str] = None


def mask_cpp(text: str) -> str:
    """Mask comments and literals while preserving newlines and positions."""
    out = list(text)
    i, n = 0, len(text)
    state = "code"
    while i < n:
        if state == "code":
            if text.startswith("//", i):
                out[i:i + 2] = "  "; i += 2; state = "line"; continue
            if text.startswith("/*", i):
                out[i:i + 2] = "  "; i += 2; state = "block"; continue
            if text.startswith('R"', i):
                j = text.find("(", i + 2)
                if j != -1:
                    out[i:j + 1] = " " * (j + 1 - i); i = j + 1; state = "raw"; raw_end = ")" + text[i:j]
                    continue
            if text[i] == '"': out[i] = " "; i += 1; state = "string"; continue
            if text[i] == "'": out[i] = " "; i += 1; state = "char"; continue
            i += 1
        elif state == "line":
            if text[i] == "\n": state = "code"
            else: out[i] = " "
            i += 1
        elif state == "block":
            if text.startswith("*/", i): out[i:i + 2] = "  "; i += 2; state = "code"
            else:
                if text[i] != "\n": out[i] = " "
                i += 1
        elif state in {"string", "char"}:
            if text[i] == "\\":
                out[i] = " "; i += 1
                if i < n and text[i] != "\n": out[i] = " "
                i += 1
            elif (state == "string" and text[i] == '"') or (state == "char" and text[i] == "'"):
                out[i] = " "; i += 1; state = "code"
            else:
                if text[i] != "\n": out[i] = " "
                i += 1
        else:  # raw literal
            if text.startswith(raw_end, i):
                out[i:i + len(raw_end)] = " " * len(raw_end); i += len(raw_end); state = "code"
            else:
                if text[i] != "\n": out[i] = " "
                i += 1
    return "".join(out)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def brace_pairs(masked: str) -> dict[int, int]:
    stack, pairs = [], {}
    for i, ch in enumerate(masked):
        if ch == "{": stack.append(i)
        elif ch == "}" and stack:
            pairs[stack.pop()] = i
    return pairs


def source_symbols(text: str) -> dict[str, list[tuple[int, int]]]:
    masked = mask_cpp(text)
    pairs = brace_pairs(masked)
    result: dict[str, list[tuple[int, int]]] = {}
    # A definition is a name followed by a parameter list and a body.  The
    # bounded search avoids treating arbitrary braces as functions.
    definition = re.compile(r"(?m)\b([A-Za-z_][\w:~]*)\s*\([^;{}]*\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[^{}]+\s*)?{")
    for m in definition.finditer(masked):
        name = m.group(1).replace(" ", "")
        if name in CONTROL_WORDS: continue
        brace = masked.find("{", m.start(), m.end())
        if brace not in pairs: continue
        start = line_of(text, m.start(1)); end = line_of(text, pairs[brace])
        short = name.split("::")[-1]
        result.setdefault(name, []).append((start, end))
        result.setdefault(short, []).append((start, end))
    return result


def symbol_candidates(symbol: str, symbols: dict[str, list[tuple[int, int]]]) -> list[tuple[str, list[tuple[int, int]]]]:
    """Resolve exact names first, then conservative CTS acronym aliases."""
    if symbol in symbols:
        return [(symbol, symbols[symbol])]
    normalized = re.sub(r"[^A-Za-z0-9]", "", symbol).lower()
    matches = []
    for name, spans in symbols.items():
        candidate = re.sub(r"[^A-Za-z0-9]", "", name).lower()
        # CTS source commonly inserts a category acronym after ``create``;
        # accept that alias only when the remaining name matches exactly.
        if candidate.startswith("create") and normalized.startswith("create"):
            left = candidate.removeprefix("create")
            right = normalized.removeprefix("create")
            if left.endswith(right) or right.endswith(left):
                matches.append((name, spans))
    return matches


def symbol_from_label(label: str) -> Optional[str]:
    # Prefer code spans.  Strip function-call punctuation while preserving
    # namespace qualification.
    spans = re.findall(r"`([^`]+)`", label)
    candidates = spans + re.findall(r"\b[A-Za-z_][A-Za-z0-9_:~]*\(\)", label)
    for candidate in candidates:
        candidate = candidate.strip().removesuffix("()").strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_:~]*", candidate) and candidate not in CONTROL_WORDS:
            return candidate
    return None


def iter_links(md: Path, repo_root: Path, line_cache: dict[Path, int], symbol_cache: dict[Path, dict[str, list[tuple[int, int]]]]) -> Iterable[Finding]:
    text = md.read_text(encoding="utf-8", errors="replace")
    for match in LINK_RE.finditer(text):
        label, rel, start_s, end_s = match.group(1), match.group(2), match.group(3), match.group(4)
        if rel.startswith(('http://', 'https://')):
            continue
        target = (md.parent / rel).resolve()
        start, end = int(start_s), int(end_s or start_s)
        base = dict(wiki_file=str(md.relative_to(repo_root)), wiki_line=line_of(text, match.start()), target=str(target.relative_to(repo_root)) if target.is_relative_to(repo_root) else str(target), claimed_start=start, claimed_end=end)
        if not target.is_file():
            yield Finding("TARGET_MISSING", "error", **base); continue
        if target not in line_cache:
            with target.open(encoding="utf-8", errors="replace") as source:
                line_cache[target] = sum(1 for _ in source)
        total = line_cache[target]
        if start < 1 or start > end:
            yield Finding("RANGE_INVALID", "error", **base, suggestion="use an ordered positive line range"); continue
        if end > total:
            yield Finding("RANGE_OUT_OF_BOUNDS", "error", **base, suggestion=f"end line must be <= {total}"); continue
        if target.suffix.lower() not in CODE_EXTENSIONS: continue
        symbol = symbol_from_label(label)
        if not symbol: continue
        if target not in symbol_cache: symbol_cache[target] = source_symbols(target.read_text(encoding="utf-8", errors="replace"))
        spans = symbol_cache[target].get(symbol, [])
        if not spans:
            aliases = symbol_candidates(symbol, symbol_cache[target])
            if len(aliases) == 1:
                symbol, spans = aliases[0]
        if not spans:
            continue
        unique = sorted(set(spans))
        # Only flag a range when it partially overlaps a uniquely resolved
        # function: one claimed boundary cuts through the function while the
        # other boundary lies outside it. A contained excerpt and a wider
        # context range are both valid wiki references.
        if len(unique) != 1:
            continue
        actual_start, actual_end = unique[0]
        claimed_inside = actual_start <= start and end <= actual_end
        actual_inside = start <= actual_start and actual_end <= end
        partial_overlap = (start <= actual_end and end >= actual_start) and not (claimed_inside or actual_inside)
        if partial_overlap:
            suggestion = f"use #L{actual_start}-L{actual_end}"
            yield Finding("RANGE_SYMBOL_MISMATCH", "error", **base, symbol=symbol, actual_start=actual_start, actual_end=actual_end, suggestion=suggestion)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root")
    parser.add_argument("wiki_dir")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    repo_root, wiki_dir = Path(args.repo_root).resolve(), Path(args.wiki_dir).resolve()
    findings: list[Finding] = []
    line_cache: dict[Path, int] = {}; symbol_cache: dict[Path, dict[str, list[tuple[int, int]]]] = {}
    md_paths = [wiki_dir] if wiki_dir.is_file() else sorted(wiki_dir.rglob("*.md"))
    for md in md_paths: findings.extend(iter_links(md, repo_root, line_cache, symbol_cache))
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        for f in findings:
            line = f"{f.wiki_file}:L{f.wiki_line} {f.rule} [{f.severity}] {f.target}#L{f.claimed_start}-L{f.claimed_end}"
            if f.symbol: line += f" symbol={f.symbol} actual={f.actual_start}-{f.actual_end}"
            if f.suggestion: line += f" ({f.suggestion})"
            print(line)
        print(f"[DONE] errors={sum(f.severity == 'error' for f in findings)} warnings={sum(f.severity == 'warning' for f in findings)} findings={len(findings)}")
    return 1 if any(f.severity == "error" or (args.strict and f.severity == "warning") for f in findings) else 0

if __name__ == "__main__": sys.exit(main())
