#!/usr/bin/env python3
"""
Validate wiki source code links.

This script parses all markdown files under the wiki directory and verifies
that all source code links point to existing files.

Usage:
    python validate_wiki_links.py [--wiki-dir PATH] [--verbose]

Exit codes:
    0 - All links valid
    1 - Broken links found
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_source_links(markdown_content: str, md_file_path: Path) -> List[Tuple[str, int, str]]:
    """
    Extract source code links from markdown content.
    
    Returns list of (link_text, line_number, link_target) tuples.
    """
    links = []
    lines = markdown_content.split('\n')
    
    # Pattern for markdown links: [text](target)
    # We're interested in links that point to source files (../../modules/...)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    
    for line_num, line in enumerate(lines, start=1):
        for match in link_pattern.finditer(line):
            link_text = match.group(1)
            link_target = match.group(2)
            
            # Filter for source code links (relative paths to modules or framework)
            if link_target.startswith('../../modules/') or link_target.startswith('../../framework/'):
                # Remove line number anchor if present
                base_target = link_target.split('#')[0]
                links.append((link_text, line_num, base_target))
    
    return links


def resolve_relative_link(md_file_path: Path, link_target: str, repo_root: Path) -> Path:
    """
    Resolve a relative link from a markdown file to an absolute path.
    """
    # Get the directory containing the markdown file
    md_dir = md_file_path.parent
    
    # Resolve the relative path
    resolved = (md_dir / link_target).resolve()
    
    return resolved


def validate_wiki_links(wiki_dir: Path, repo_root: Path, verbose: bool = False) -> List[Tuple[Path, int, str, str]]:
    """
    Validate all source code links in wiki markdown files.
    
    Returns list of (md_file, line_num, link_target, error_message) for broken links.
    """
    broken_links = []
    
    # Find all markdown files in wiki directory
    md_files = list(wiki_dir.rglob('*.md'))
    
    if verbose:
        print(f"Found {len(md_files)} markdown files to check")
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception as e:
            broken_links.append((md_file, 0, '', f"Failed to read file: {e}"))
            continue
        
        links = extract_source_links(content, md_file)
        
        for link_text, line_num, link_target in links:
            resolved_path = resolve_relative_link(md_file, link_target, repo_root)
            
            if not resolved_path.exists():
                broken_links.append((md_file, line_num, link_target, 
                    f"File not found: {resolved_path.relative_to(repo_root)}"))
    
    return broken_links


def main():
    parser = argparse.ArgumentParser(description='Validate wiki source code links')
    parser.add_argument('--wiki-dir', type=str, 
                        default='external/vulkancts/wiki',
                        help='Path to wiki directory (relative to repo root)')
    parser.add_argument('--repo-root', type=str,
                        default='.',
                        help='Path to repository root')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    wiki_dir = (repo_root / args.wiki_dir).resolve()
    
    if not wiki_dir.exists():
        print(f"Error: Wiki directory not found: {wiki_dir}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Repository root: {repo_root}")
        print(f"Wiki directory: {wiki_dir}")
        print()
    
    broken_links = validate_wiki_links(wiki_dir, repo_root, args.verbose)
    
    if broken_links:
        print(f"\nFound {len(broken_links)} broken link(s):\n")
        for md_file, line_num, link_target, error in broken_links:
            rel_md = md_file.relative_to(repo_root)
            if line_num > 0:
                print(f"  {rel_md}:{line_num}")
            else:
                print(f"  {rel_md}")
            print(f"    Target: {link_target}")
            print(f"    Error: {error}")
            print()
        sys.exit(1)
    else:
        print("All source code links are valid.")
        sys.exit(0)


if __name__ == '__main__':
    main()
