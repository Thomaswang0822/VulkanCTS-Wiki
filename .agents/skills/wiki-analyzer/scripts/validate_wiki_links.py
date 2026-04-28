#!/usr/bin/env python3
"""
Validate local links in Vulkan CTS wiki markdown files.

This script parses all markdown files under the wiki directory and verifies
that every local file link points to an existing path inside the repository.
External URLs, URI schemes, and anchor-only links are ignored.

Usage:
    python validate_wiki_links.py [--wiki-dir PATH] [--files PATH [PATH ...]] [--repo-root PATH] [--verbose] [--auto-fix]

Exit codes:
    0 - All local links valid and no style violations
    1 - Broken links found or style violations remain
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import unquote, urlparse


LinkRecord = Tuple[str, int, str]
BrokenLink = Tuple[Path, int, str, str, Optional[Path]]
StyleViolation = Tuple[Path, int, str, str]


MARKDOWN_LINK_PATTERN = re.compile(r'(?<!!)(\[([^\]]*)\]\(([^)]+)\))')
URI_SCHEME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')
SOURCE_FILE_EXTENSIONS = {
    '.c', '.cc', '.cpp', '.cxx', '.c++',
    '.h', '.hh', '.hpp', '.hxx', '.h++',
    '.inc', '.inl', '.ipp', '.tpp',
    '.m', '.mm',
    '.java', '.kt', '.kts',
    '.cs', '.swift', '.rs', '.go',
    '.py', '.rb', '.php', '.js', '.jsx', '.ts', '.tsx',
    '.glsl', '.vert', '.frag', '.geom', '.comp', '.tesc', '.tese', '.mesh', '.task',
}
COLON_STYLE_SOURCE_REF_PATTERN = re.compile(
    r'^(?P<path>[^)#?]+?(?:' + '|'.join(re.escape(ext) for ext in sorted(SOURCE_FILE_EXTENSIONS, key=len, reverse=True)) + r')):(?P<start>\d+)(?:-(?P<end>\d+))?$',
    re.IGNORECASE,
)


def is_external_or_special_target(link_target: str) -> bool:
    """Return True for targets that should not be checked as local files."""
    stripped = link_target.strip()

    if not stripped:
        return True

    if stripped.startswith('#'):
        return True

    parsed = urlparse(stripped)
    if parsed.scheme or stripped.startswith('//'):
        return True

    # Be conservative for URI-like targets that urlparse may not classify as a
    # scheme in all edge cases.
    if URI_SCHEME_PATTERN.match(stripped):
        return True

    return False


def strip_fragment_and_query(link_target: str) -> str:
    """Return the filesystem path portion of a markdown link target.

    Strips URI fragments (#...), query strings (?...), and source code line
    number suffixes (:line or :line-line) that are not part of the filename.
    """
    path_part = link_target.strip().split('#', 1)[0].split('?', 1)[0]

    # Strip source-code line-number suffixes such as ":82" or ":1650-1730".
    # These are common in wiki links like [file.cpp:82](../path/file.cpp:82)
    # but are not valid filename characters on any platform we target.
    path_part = re.sub(r':\d+(-\d+)?$', '', path_part)

    # Markdown links may percent-encode spaces or other filename characters.
    return unquote(path_part)


def extract_local_links(markdown_content: str, md_file_path: Path) -> List[LinkRecord]:
    """
    Extract local markdown file links from markdown content.

    Returns list of (link_text, line_number, original_link_target) tuples.
    """
    links: List[LinkRecord] = []
    lines = markdown_content.split('\n')

    for line_num, line in enumerate(lines, start=1):
        for match in MARKDOWN_LINK_PATTERN.finditer(line):
            link_text = match.group(2)
            link_target = match.group(3).strip()

            if is_external_or_special_target(link_target):
                continue

            path_part = strip_fragment_and_query(link_target)
            if not path_part:
                continue

            links.append((link_text, line_num, link_target))

    return links


def resolve_relative_link(md_file_path: Path, link_target: str) -> Path:
    """Resolve a local markdown link target from the markdown file directory."""
    path_part = strip_fragment_and_query(link_target)
    return (md_file_path.parent / path_part).resolve()


def is_inside_directory(path: Path, directory: Path) -> bool:
    """Return True if path is inside directory or equal to directory."""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def detect_colon_style_source_reference(link_target: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """Return parsed colon-style source reference components when present."""
    stripped = link_target.strip()
    if '#' in stripped or '?' in stripped:
        return None

    match = COLON_STYLE_SOURCE_REF_PATTERN.match(stripped)
    if not match:
        return None

    return match.group('path'), match.group('start'), match.group('end')


def rewrite_colon_style_source_reference(link_target: str) -> str:
    """Rewrite file.cpp:82 or file.cpp:82-95 to GitHub #L fragment syntax."""
    parsed = detect_colon_style_source_reference(link_target)
    if not parsed:
        return link_target

    path_part, start, end = parsed
    if end is None:
        return f"{path_part}#L{start}"
    return f"{path_part}#L{start}-L{end}"


def auto_fix_markdown_content(markdown_content: str) -> Tuple[str, int]:
    """Rewrite colon-style source references in markdown link targets only."""
    replacements = 0

    def replace_match(match: re.Match[str]) -> str:
        nonlocal replacements
        full_match = match.group(1)
        link_text = match.group(2)
        link_target = match.group(3)
        fixed_target = rewrite_colon_style_source_reference(link_target.strip())
        if fixed_target == link_target.strip():
            return full_match
        replacements += 1
        return f'[{link_text}]({fixed_target})'

    updated = MARKDOWN_LINK_PATTERN.sub(replace_match, markdown_content)
    return updated, replacements


def validate_wiki_links(
    wiki_dir: Path,
    repo_root: Path,
    verbose: bool = False,
    md_files: Optional[List[Path]] = None,
) -> Tuple[List[BrokenLink], List[StyleViolation]]:
    """
    Validate all local links in wiki markdown files.

    Args:
        wiki_dir: Wiki directory for discovery (used when md_files is None).
        repo_root: Repository root for path validation.
        verbose: Print verbose output.
        md_files: Explicit list of markdown files to validate. When provided,
                  wiki_dir discovery is skipped.

    Returns:
    - broken links as (md_file, line_num, link_target, error_message, resolved_path)
    - style violations as (md_file, line_num, link_target, error_message)
    """
    broken_links: List[BrokenLink] = []
    style_violations: List[StyleViolation] = []

    if md_files is None:
        md_files = sorted(wiki_dir.rglob('*.md'))

    if verbose:
        print(f"Found {len(md_files)} markdown files to check")

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = md_file.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                broken_links.append((md_file, 0, '', f"Failed to read file: {e}", None))
                continue
        except Exception as e:
            broken_links.append((md_file, 0, '', f"Failed to read file: {e}", None))
            continue

        links = extract_local_links(content, md_file)

        for _link_text, line_num, link_target in links:
            if detect_colon_style_source_reference(link_target) is not None:
                style_violations.append((
                    md_file,
                    line_num,
                    link_target,
                    'Use #L<line> instead of :<line> for source-code line references',
                ))

            resolved_path = resolve_relative_link(md_file, link_target)

            if not is_inside_directory(resolved_path, repo_root):
                broken_links.append((
                    md_file,
                    line_num,
                    link_target,
                    'Resolved path escapes repository root',
                    resolved_path,
                ))
                continue

            if not resolved_path.exists():
                broken_links.append((
                    md_file,
                    line_num,
                    link_target,
                    'File not found',
                    resolved_path,
                ))

    return broken_links, style_violations


def format_path_for_output(path: Path, repo_root: Path) -> str:
    """Format a path relative to repo root when possible."""
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def auto_fix_wiki_links(wiki_dir: Path, verbose: bool = False, md_files: Optional[List[Path]] = None) -> int:
    """Rewrite colon-style source references in markdown link targets across the wiki."""
    total_replacements = 0
    if md_files is None:
        md_files = sorted(wiki_dir.rglob('*.md'))

    for md_file in md_files:
        try:
            original = md_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            original = md_file.read_text(encoding='utf-8', errors='replace')

        updated, replacements = auto_fix_markdown_content(original)
        if replacements == 0:
            continue

        md_file.write_text(updated, encoding='utf-8')
        total_replacements += replacements

        if verbose:
            print(f"Auto-fixed {replacements} link target(s) in {md_file}")

    return total_replacements


def main():
    parser = argparse.ArgumentParser(description='Validate local links in wiki markdown files')
    parser.add_argument('--wiki-dir', type=str,
                        default='external/vulkancts/wiki',
                        help='Path to wiki directory (relative to repo root)')
    parser.add_argument('--files', type=str, nargs='+',
                        help='One or more specific markdown files to validate (relative to repo root)')
    parser.add_argument('--repo-root', type=str,
                        default='.',
                        help='Path to repository root')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
    parser.add_argument('--auto-fix', action='store_true',
                        help='Rewrite colon-style source-code line references in markdown link targets')

    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # Determine the list of explicit files when --files is provided
    explicit_files: Optional[List[Path]] = None
    if args.files:
        explicit_files = []
        for f in args.files:
            resolved = (repo_root / f).resolve()
            if not resolved.exists():
                print(f"Error: File not found: {resolved}", file=sys.stderr)
                sys.exit(1)
            if not is_inside_directory(resolved, repo_root):
                print(f"Error: File is outside repository root: {resolved}", file=sys.stderr)
                sys.exit(1)
            explicit_files.append(resolved)

    # When --files is given, wiki_dir is only used as a fallback for
    # directory discovery; we still resolve it for display purposes.
    wiki_dir = (repo_root / args.wiki_dir).resolve()

    if not args.files:
        if not wiki_dir.exists():
            print(f"Error: Wiki directory not found: {wiki_dir}", file=sys.stderr)
            sys.exit(1)

        if not is_inside_directory(wiki_dir, repo_root):
            print(f"Error: Wiki directory is outside repository root: {wiki_dir}", file=sys.stderr)
            sys.exit(1)

    if args.verbose:
        print(f"Repository root: {repo_root}")
        if explicit_files:
            print(f"Validating {len(explicit_files)} specific file(s)")
        else:
            print(f"Wiki directory: {wiki_dir}")
        print()

    if args.auto_fix:
        fixed_count = auto_fix_wiki_links(wiki_dir, args.verbose, md_files=explicit_files)
        print(f"Auto-fixed {fixed_count} colon-style source-code line reference(s).")
        if args.verbose:
            print()

    broken_links, style_violations = validate_wiki_links(wiki_dir, repo_root, args.verbose, md_files=explicit_files)

    if broken_links:
        print(f"\nFound {len(broken_links)} broken link(s):\n")
        for md_file, line_num, link_target, error, resolved_path in broken_links:
            rel_md = format_path_for_output(md_file, repo_root)
            if line_num > 0:
                print(f"  {rel_md}:{line_num}")
            else:
                print(f"  {rel_md}")
            print(f"    Target: {link_target}")
            if resolved_path is not None:
                print(f"    Resolved: {format_path_for_output(resolved_path, repo_root)}")
            print(f"    Error: {error}")
            print()

    if style_violations:
        print(f"\nFound {len(style_violations)} style violation(s):\n")
        for md_file, line_num, link_target, error in style_violations:
            rel_md = format_path_for_output(md_file, repo_root)
            print(f"  {rel_md}:{line_num}")
            print(f"    Target: {link_target}")
            print(f"    Error: {error} (colon-style line reference)")
            print()

    if broken_links or style_violations:
        sys.exit(1)

    print('All local wiki links are valid.')
    sys.exit(0)


if __name__ == '__main__':
    main()
