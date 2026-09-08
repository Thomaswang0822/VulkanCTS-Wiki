#!/usr/bin/env python3
"""Temp audit: check wiki source-link line ranges against current file line counts.

Usage: python check_line_refs.py <repo_root> <wiki_dir>
Reports links whose end line exceeds the target file's current line count,
and links whose target file is missing.
"""
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\]\(([^)#]+)#L(\d+)(?:-L(\d+))?\)")

def main():
    repo_root = Path(sys.argv[1]).resolve()
    wiki_dir = Path(sys.argv[2]).resolve()
    line_cache = {}
    issues = 0
    for md in sorted(wiki_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            rel, start_s, end_s = m.group(1), m.group(2), m.group(3)
            if rel.startswith(("http://", "https://")):
                continue
            target = (md.parent / rel).resolve()
            try:
                rt = target.relative_to(repo_root)
            except ValueError:
                continue
            if not rt.is_file():
                print(f"MISSING {md.relative_to(repo_root)} -> {rt}")
                issues += 1
                continue
            key = str(rt)
            if key not in line_cache:
                with open(rt, encoding="utf-8", errors="replace") as f:
                    line_cache[key] = sum(1 for _ in f)
            total = line_cache[key]
            start = int(start_s)
            end = int(end_s) if end_s else start
            if end > total or start > total or start < 1:
                ln = text[: m.start()].count("\n") + 1
                print(f"DRIFT   {md.relative_to(repo_root)}:L{ln} {rt}#L{start}-L{end} (file has {total} lines)")
                issues += 1
    print(f"[DONE] issues={issues}")

if __name__ == "__main__":
    main()
