#!/usr/bin/env python3
"""Convert markdown links in one translated GitLab Wiki page.

The script operates on one file under vkcts-wiki-pages/. Links in translated
pages are still authored relative to the matching English canonical wiki page
under external/vulkancts/wiki/. For each local markdown link, this script:

- resolves it against the canonical English wiki file location;
- converts wiki-page links by dropping the .md suffix for GitLab Wiki rendering;
- converts repo-local non-wiki links to GitLab blob URLs.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import quote

# Static publish configuration. Update here if the GitLab project or source ref changes.
GITLAB_BLOB_PREFIX = "https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki/-/blob/vkcts-wiki/"
PUBLISH_WIKI_ROOT = Path("vkcts-wiki-pages")
CANONICAL_WIKI_ROOT = Path("external/vulkancts/wiki")

LINK_RE = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)(\s+[^)]*)?\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def as_posix(path: Path) -> str:
    return path.as_posix()


def split_fragment(target: str) -> tuple[str, str]:
    if "#" not in target:
        return target, ""
    path_part, fragment = target.split("#", 1)
    return path_part, "#" + fragment


def is_external_or_special(target: str) -> bool:
    return (
        not target
        or target.startswith("#")
        or target.startswith("//")
        or target.startswith("/")
        or SCHEME_RE.match(target) is not None
    )


def canonical_path_for_publish_file(markdown_file: Path) -> Path:
    try:
        rel = markdown_file.relative_to(PUBLISH_WIKI_ROOT)
    except ValueError as exc:
        raise ValueError(f"input file must be under {PUBLISH_WIKI_ROOT}/: {markdown_file}") from exc

    if rel == Path("home.md"):
        return CANONICAL_WIKI_ROOT / "README.md"
    return CANONICAL_WIKI_ROOT / rel


def normalize_repo_relative(base_dir: Path, target_path: str) -> str:
    joined = as_posix(base_dir / target_path)
    normalized = posixpath.normpath(joined)
    if normalized == ".":
        return ""
    return normalized


def is_wiki_page(repo_relative_path: str) -> bool:
    canonical_root = as_posix(CANONICAL_WIKI_ROOT)
    if repo_relative_path == f"{canonical_root}/README.md":
        return True
    if not repo_relative_path.startswith(canonical_root + "/"):
        return False
    if "/internal_doc/" in repo_relative_path:
        return False

    # Normal authoring input uses .md wiki links. Already-converted wiki links have
    # the .md suffix removed; keep those idempotent instead of turning them into
    # source-code blob URLs on a second run.
    if repo_relative_path.endswith(".md"):
        return True
    suffix = Path(repo_relative_path).suffix
    return suffix == ""


def wiki_publish_target_from_canonical(repo_relative_path: str) -> str:
    canonical_root = as_posix(CANONICAL_WIKI_ROOT)
    if repo_relative_path == f"{canonical_root}/README.md":
        return "home"

    prefix = canonical_root + "/"
    rel = repo_relative_path[len(prefix) :]
    if rel.endswith(".md"):
        rel = rel[:-3]
    return rel


def relative_wiki_link(from_publish_file: Path, wiki_target_without_md: str, fragment: str) -> str:
    from_dir = as_posix(from_publish_file.parent)
    target_publish_path = as_posix(PUBLISH_WIKI_ROOT / wiki_target_without_md)
    rel = posixpath.relpath(target_publish_path, from_dir)
    if rel == ".":
        rel = posixpath.basename(target_publish_path)
    return rel + fragment


def gitlab_blob_url(repo_relative_path: str, fragment: str) -> str:
    # Quote path segments but keep slashes and common URL fragment punctuation intact.
    quoted_path = quote(repo_relative_path, safe="/")
    return GITLAB_BLOB_PREFIX + quoted_path + fragment


def convert_target(target: str, publish_file: Path, canonical_file: Path) -> str:
    if is_external_or_special(target):
        return target

    path_part, fragment = split_fragment(target)
    if is_external_or_special(path_part):
        return target

    repo_relative = normalize_repo_relative(canonical_file.parent, path_part)

    if is_wiki_page(repo_relative):
        wiki_target = wiki_publish_target_from_canonical(repo_relative)
        return relative_wiki_link(publish_file, wiki_target, fragment)

    return gitlab_blob_url(repo_relative, fragment)


def convert_line(line: str, publish_file: Path, canonical_file: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        text = match.group(1)
        target = match.group(2)
        title = match.group(3) or ""
        new_target = convert_target(target, publish_file, canonical_file)
        return f"[{text}]({new_target}{title})"

    return LINK_RE.sub(repl, line)


def convert_markdown(content: str, publish_file: Path, canonical_file: Path) -> str:
    output: list[str] = []
    in_fence = False

    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            output.append(line)
            continue
        if in_fence:
            output.append(line)
            continue
        output.append(convert_line(line, publish_file, canonical_file))

    return "".join(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert local markdown links in one vkcts-wiki-pages markdown file."
    )
    parser.add_argument("markdown_file", help="one markdown file under vkcts-wiki-pages/")
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not overwrite; exit 1 if conversion would change the file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markdown_file = Path(args.markdown_file)

    if markdown_file.suffix != ".md":
        print(f"error: input must be a .md file: {markdown_file}", file=sys.stderr)
        return 2
    if not markdown_file.is_file():
        print(f"error: input file does not exist: {markdown_file}", file=sys.stderr)
        return 2

    try:
        canonical_file = canonical_path_for_publish_file(markdown_file)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not canonical_file.is_file():
        print(f"error: mapped canonical wiki file does not exist: {canonical_file}", file=sys.stderr)
        return 2

    original = markdown_file.read_text(encoding="utf-8")
    converted = convert_markdown(original, markdown_file, canonical_file)

    if args.check:
        if converted != original:
            print(f"would update links in {markdown_file}")
            return 1
        print(f"no link updates needed in {markdown_file}")
        return 0

    if converted != original:
        markdown_file.write_text(converted, encoding="utf-8")
        print(f"updated links in {markdown_file}")
    else:
        print(f"no link updates needed in {markdown_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
