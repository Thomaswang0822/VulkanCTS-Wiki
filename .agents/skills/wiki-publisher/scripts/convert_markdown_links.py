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

# External source trees fetched by external/fetch_sources.py are gitignored (see
# external/.gitignore), so they are absent from the wiki repo and GitLab blob URLs
# into them 404. Rewrite links that target these trees to the upstream GitHub
# repository so published links resolve. The ref is pinned to the same revision
# external/fetch_sources.py checks out, so the cited content matches what the CTS
# and the wiki's factual claims are grounded against. Add new entries here as new
# external source trees are referenced in the wiki.
EXTERNAL_SOURCE_UPSTREAMS = {
    "external/vulkan-docs/src": "https://github.com/KhronosGroup/Vulkan-Docs/blob/45285e2553e499bbcdb885f71fd789c1f20cab80/",
    "external/spirv-headers/src": "https://github.com/KhronosGroup/SPIRV-Headers/blob/main/",
}

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

    if rel.parts[:1] == ("categories",):
        if len(rel.parts) == 2:
            return CANONICAL_WIKI_ROOT / rel
        if len(rel.parts) >= 3:
            category = rel.parts[1]
            rest = Path(*rel.parts[2:])
            return CANONICAL_WIKI_ROOT / "testfiles" / category / rest

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

    # Normal authoring input uses .md wiki links.
    if repo_relative_path.endswith(".md"):
        return True
    suffix = Path(repo_relative_path).suffix
    if suffix != "":
        return False
    # Extensionless: a real wiki page has a .md source file at this path.
    # A directory (e.g. testfiles/<category>/) is not a page.
    return Path(repo_relative_path + ".md").is_file()


def wiki_publish_target_from_canonical(repo_relative_path: str) -> str:
    canonical_root = as_posix(CANONICAL_WIKI_ROOT)
    if repo_relative_path == f"{canonical_root}/README.md":
        return "home"

    prefix = canonical_root + "/"
    rel = repo_relative_path[len(prefix) :]

    if rel.startswith("testfiles/") and rel.endswith(".md"):
        rel_path = Path(rel)
        category = rel_path.parts[1]
        page = rel_path.stem
        rel = f"categories/{category}/{page}"
    elif rel.endswith(".md"):
        rel = rel[:-3]

    return rel


def relative_wiki_link(from_publish_file: Path, wiki_target_without_md: str, fragment: str) -> str:
    from_rel = from_publish_file.relative_to(PUBLISH_WIKI_ROOT)

    # Special GitLab Wiki page-plus-directory behavior:
    # from `categories/<category>.md`, links to child pages under the matching
    # published category directory should use `./<category>/<page>`.
    if len(from_rel.parts) == 2 and from_rel.parts[0] == "categories" and from_rel.suffix == ".md":
        current_category = from_rel.stem
        target_parts = Path(wiki_target_without_md).parts
        if len(target_parts) >= 3 and target_parts[0] == "categories" and target_parts[1] == current_category:
            child_rel = posixpath.join(".", current_category, *target_parts[2:])
            return child_rel + fragment

    from_dir = as_posix(from_publish_file.parent)
    target_publish_path = as_posix(PUBLISH_WIKI_ROOT / wiki_target_without_md)
    rel = posixpath.relpath(target_publish_path, from_dir)
    if rel == ".":
        # Target page is the directory containing the current file (e.g. a child
        # page linking to its category page). Go up one level to reach it.
        rel = "../" + posixpath.basename(target_publish_path)
    elif not rel.startswith("."):
        # GitLab Wiki resolves naked relative links against the wiki root, not
        # the current page's directory. Prepend "./" so same-directory links
        # (e.g. sibling pages) resolve correctly.
        rel = "./" + rel
    return rel + fragment


def gitlab_blob_url(repo_relative_path: str, fragment: str) -> str:
    # Quote path segments but keep slashes and common URL fragment punctuation intact.
    quoted_path = quote(repo_relative_path, safe="/")
    return GITLAB_BLOB_PREFIX + quoted_path + fragment


def external_source_url(repo_relative_path: str, fragment: str) -> str | None:
    """Return the upstream GitHub blob URL if repo_relative_path targets a
    gitignored fetched source tree, else None."""
    for prefix, upstream in EXTERNAL_SOURCE_UPSTREAMS.items():
        if repo_relative_path == prefix:
            return upstream + fragment
        if repo_relative_path.startswith(prefix + "/"):
            rest = repo_relative_path[len(prefix) + 1 :]
            return upstream + quote(rest, safe="/") + fragment
    return None


def is_converted_publish_link(path_part: str, publish_file: Path) -> bool:
    """Return True if an extensionless relative link already resolves to a
    published wiki page (i.e. the link is already in publish form).

    GitLab Wiki resolves naked relative links against the wiki root, not the
    current page's directory. Therefore a converted link must start with "./"
    or "../" to be considered stable.
    """
    if not path_part or Path(path_part).suffix != "":
        return False
    if not (path_part.startswith("./") or path_part.startswith("../")):
        return False
    resolved = normalize_repo_relative(publish_file.parent, path_part)
    publish_root = as_posix(PUBLISH_WIKI_ROOT)
    if not resolved.startswith(publish_root + "/"):
        return False
    return Path(resolved + ".md").is_file()


def convert_target(target: str, publish_file: Path, canonical_file: Path) -> str:
    if is_external_or_special(target):
        return target

    path_part, fragment = split_fragment(target)
    if is_external_or_special(path_part):
        return target

    # Idempotency: if the link is already in publish form (extensionless,
    # resolves to a published .md page), leave it unchanged.
    if is_converted_publish_link(path_part, publish_file):
        return target

    repo_relative = normalize_repo_relative(canonical_file.parent, path_part)

    external = external_source_url(repo_relative, fragment)
    if external is not None:
        return external

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
