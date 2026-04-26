#!/usr/bin/env python3
"""
Verify registration paths against mustpass TXT files.

This script verifies that group names documented in wiki files match
the actual registration paths in the mustpass definition files.

MUSTPASS TXT FILE FORMAT:
    The mustpass TXT files contain test names in the format:
        dEQP-VK.{category}.{group_path}.{test_name}
    
    For example, geometry.txt contains lines like:
        dEQP-VK.geometry.basic.output_10
        dEQP-VK.geometry.input.basic_primitive.points
    
    When verifying a path like "geometry.basic", the script searches for
    lines starting with "dEQP-VK.geometry.basic." in geometry.txt.

USAGE:
    python verify_registration_paths.py <category> <group_path>
    python verify_registration_paths.py api copy_and_blit.core.blit_image
    python verify_registration_paths.py geometry --check-all

EXIT CODES:
    0 - Path verified successfully
    1 - Path not found in mustpass files
    2 - Error (file not found, etc.)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def find_mustpass_files(category: str, mustpass_dir: Path) -> List[Path]:
    """
    Find mustpass TXT files for a given category.
    
    Handles cases where multiple TXT files may correspond to one category
    (e.g., renderpass and renderpasses).
    """
    txt_files = []
    
    # Direct match
    direct_match = mustpass_dir / f"{category}.txt"
    if direct_match.exists():
        txt_files.append(direct_match)
    
    # Plural form match (e.g., renderpasses for renderpass category)
    plural_match = mustpass_dir / f"{category}s.txt"
    if plural_match.exists():
        txt_files.append(plural_match)
    
    # Also check for common variations
    variations = [
        f"{category}es.txt",  # e.g., bus -> buses
    ]
    for var in variations:
        var_path = mustpass_dir / var
        if var_path.exists() and var_path not in txt_files:
            txt_files.append(var_path)
    
    return txt_files


def verify_path_in_txt(group_path: str, txt_file: Path) -> Tuple[bool, Optional[int]]:
    """
    Verify that a group path exists in a mustpass TXT file.
    
    Uses efficient line-by-line search without loading entire file.
    
    Returns (found, line_number) tuple.
    """
    # The pattern we're looking for: lines starting with the full path
    # e.g., "api.copy_and_blit.core.blit_image."
    pattern = re.compile(rf'^{re.escape(group_path)}(\.|$)')
    
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                if pattern.match(line.strip()):
                    return (True, line_num)
    except Exception as e:
        print(f"Error reading {txt_file}: {e}", file=sys.stderr)
        return (False, None)
    
    return (False, None)


def verify_registration_path(category: str, group_path: str, 
                             mustpass_dir: Path, verbose: bool = False) -> Tuple[bool, str]:
    """
    Verify a registration path against mustpass files.
    
    Returns (success, message) tuple.
    """
    txt_files = find_mustpass_files(category, mustpass_dir)
    
    if not txt_files:
        return (False, f"No mustpass TXT file found for category '{category}'")
    
    if verbose:
        print(f"Checking mustpass files: {[str(f.name) for f in txt_files]}")
    
    # Construct full path with dEQP-VK prefix: dEQP-VK.category.group_path
    # The mustpass files use format like "dEQP-VK.geometry.basic.output_10"
    full_path = f"dEQP-VK.{category}.{group_path}" if group_path else f"dEQP-VK.{category}"
    
    for txt_file in txt_files:
        found, line_num = verify_path_in_txt(full_path, txt_file)
        if found:
            return (True, f"Found in {txt_file.name}:{line_num}")
    
    # Not found in any file
    return (False, f"Path '{full_path}' not found in any mustpass file")


def extract_group_paths_from_wiki(wiki_dir: Path, category: str) -> List[Tuple[Path, int, str]]:
    """
    Extract group paths from wiki markdown files for a category.
    
    Returns list of (md_file, line_num, group_path) tuples.
    """
    paths = []
    
    # Look for patterns like:
    # - "api.copy_and_blit.core.blit_image"
    # - Registration path trees with group names
    # - Links to test groups
    
    category_dir = wiki_dir / 'testfiles' / category
    if not category_dir.exists():
        return paths
    
    # Pattern for registration paths (e.g., "api.copy_and_blit.core.blit_image")
    path_pattern = re.compile(rf'`({re.escape(category)}\.[a-zA-Z0-9_.]+)`')
    
    for md_file in category_dir.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, start=1):
                for match in path_pattern.finditer(line):
                    paths.append((md_file, line_num, match.group(1)))
        except Exception:
            continue
    
    return paths


def main():
    parser = argparse.ArgumentParser(description='Verify registration paths in mustpass files')
    parser.add_argument('category', nargs='?', help='Category name (e.g., api, geometry)')
    parser.add_argument('group_path', nargs='?', help='Group path (e.g., copy_and_blit.core.blit_image)')
    parser.add_argument('--mustpass-dir', type=str,
                        default='external/vulkancts/mustpass/main/vk-default',
                        help='Path to mustpass directory')
    parser.add_argument('--repo-root', type=str,
                        default='.',
                        help='Path to repository root')
    parser.add_argument('--wiki-dir', type=str,
                        default='external/vulkancts/wiki',
                        help='Path to wiki directory')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
    parser.add_argument('--check-all', action='store_true',
                        help='Check all paths found in wiki files for the category')
    
    args = parser.parse_args()
    
    repo_root = Path(args.repo_root).resolve()
    mustpass_dir = (repo_root / args.mustpass_dir).resolve()
    wiki_dir = (repo_root / args.wiki_dir).resolve()
    
    if not mustpass_dir.exists():
        print(f"Error: Mustpass directory not found: {mustpass_dir}", file=sys.stderr)
        sys.exit(2)
    
    if args.check_all:
        if not args.category:
            print("Error: --check-all requires a category argument", file=sys.stderr)
            sys.exit(2)
        
        paths = extract_group_paths_from_wiki(wiki_dir, args.category)
        if not paths:
            print(f"No registration paths found in wiki for category '{args.category}'")
            sys.exit(0)
        
        print(f"Checking {len(paths)} registration paths...\n")
        
        failed = 0
        for md_file, line_num, full_path in paths:
            # Extract group_path from full_path (remove category prefix)
            parts = full_path.split('.', 1)
            group_path = parts[1] if len(parts) > 1 else ''
            
            success, message = verify_registration_path(
                args.category, group_path, mustpass_dir, args.verbose)
            
            rel_md = md_file.relative_to(repo_root)
            if success:
                print(f"  OK: {full_path}")
                if args.verbose:
                    print(f"      ({message})")
            else:
                print(f"  FAIL: {full_path}")
                print(f"        Source: {rel_md}:{line_num}")
                print(f"        {message}")
                failed += 1
        
        print()
        if failed > 0:
            print(f"Verification failed: {failed} path(s) not found")
            sys.exit(1)
        else:
            print("All paths verified successfully")
            sys.exit(0)
    
    else:
        # Single path verification
        if not args.category:
            print("Error: category argument required", file=sys.stderr)
            parser.print_help()
            sys.exit(2)
        
        success, message = verify_registration_path(
            args.category, args.group_path or '', mustpass_dir, args.verbose)
        
        if success:
            print(f"Verified: {message}")
            sys.exit(0)
        else:
            print(f"Verification failed: {message}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
