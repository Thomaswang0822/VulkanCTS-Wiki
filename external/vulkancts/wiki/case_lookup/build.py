"""Build a Registration-Hierarchy-first index and tracked runtime JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

from build_helper import (
    CATEGORY_MUSTPASS_FILES,
    OWNERSHIP_ALIASES,
    OWNERSHIP_EXCLUSIONS,
)
from build_helper.category_handlers import (
    allows_multiple_hierarchy_snippets,
    allowed_root_categories,
    level3_pages_dir,
    project_category_mappings,
    tree_belongs_to_category,
    wiki_page_category,
)
from build_helper.export import export_lookup_json

DEFAULT_CATEGORIES = tuple(CATEGORY_MUSTPASS_FILES)
DEFAULT_WIKI_BASE_URL = (
    "https://sh-code.mthreads.com/haoxuan.wang/vulkan-cts-wiki/-/wikis"
)
SCHEMA_VERSION = "2"
HIERARCHY_HEADING = "## Registration Hierarchy"
PATH_COMPONENT_RE = re.compile(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*")
MUSTPASS_COMPONENT_RE = re.compile(r"[A-Za-z0-9_-]+")
TREE_CHILD_RE = re.compile(
    r"^(?:├──|└──)\s+"
    r"(?P<name>[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*)"
    r"(?:\s+\((?P<note>[^)]*)\))?\s*$"
)
TREE_MARKER_RE = re.compile(r"[├└│]")


class MappingBuildError(RuntimeError):
    """Raised when ownership cannot be generated and validated deterministically."""


@dataclass(frozen=True)
class OwnershipTree:
    """Represent one page-owned registration root and its direct children."""
    root: str
    children: tuple[str, ...]



@dataclass(frozen=True)
class Owner:
    """Describe the Wiki page that owns a validated registration prefix."""
    page: str
    category: str
    wiki_url: str
    source_page: Path


@dataclass(frozen=True)
class MappingRow:
    """Represent one prefix-to-page row written to a category or final DB."""
    prefix: str
    page: str
    category: str
    wiki_url: str


def extract_page_ownership(page: Path, category: str) -> list[OwnershipTree]:
    """Parse the canonical Registration Hierarchy tree set from one page."""
    lines = page.read_text(encoding="utf-8").splitlines()
    try:
        heading = next(
            index for index, line in enumerate(lines) if line.strip() == HIERARCHY_HEADING
        )
    except StopIteration:
        return []

    section_end = len(lines)
    for index in range(heading + 1, len(lines)):
        if lines[index].strip().startswith("## "):
            section_end = index
            break

    fences: list[tuple[int, int]] = []
    index = heading + 1
    while index < section_end:
        stripped = lines[index].strip()
        if not stripped.startswith("```"):
            index += 1
            continue
        if stripped != "```text":
            raise MappingBuildError(
                f"{page}:{index + 1}: Registration Hierarchy 只允许 text code fence"
            )
        start = index
        index += 1
        while index < section_end and lines[index].strip() != "```":
            index += 1
        if index >= section_end:
            raise MappingBuildError(
                f"{page}:{start + 1}: Registration Hierarchy code fence 未闭合"
            )
        fences.append((start, index))
        index += 1

    if not fences:
        raise MappingBuildError(f"{page}: Registration Hierarchy 缺少 text code fence")
    if len(fences) > 1 and not allows_multiple_hierarchy_snippets(category):
        raise MappingBuildError(
            f"{page}: 普通 category 的 Registration Hierarchy 只能有一个 text snippet"
        )

    trees: list[OwnershipTree] = []
    seen_roots: set[str] = set()
    for fence_start, fence_end in fences:
        root: str | None = None
        children: list[str] = []
        blank_since_content = False

        def flush_tree() -> None:
            """Commit the currently parsed tree and reset parser state."""
            nonlocal root, children
            if root is not None:
                trees.append(
                    OwnershipTree(
                        root=root,
                        children=tuple(children),
                    )
                )
            root = None
            children = []

        for line_number, line in enumerate(
            lines[fence_start + 1 : fence_end], fence_start + 2
        ):
            stripped = line.strip()
            if not stripped:
                if root is not None:
                    blank_since_content = True
                continue

            child_match = TREE_CHILD_RE.fullmatch(stripped)
            if child_match:
                if root is None:
                    raise MappingBuildError(
                        f"{page}:{line_number}: hierarchy child 出现在 root 之前"
                    )
                if blank_since_content:
                    raise MappingBuildError(
                        f"{page}:{line_number}: tree 内部不能用空行分隔 child"
                    )
                child_name = child_match.group("name")
                note = (child_match.group("note") or "").strip().casefold()
                if "registration only" in note:
                    continue
                if child_name in children:
                    raise MappingBuildError(
                        f"{page}:{line_number}: 重复 direct child：{child_name}"
                    )
                children.append(child_name)
                continue
            if TREE_MARKER_RE.search(stripped):
                raise MappingBuildError(
                    f"{page}:{line_number}: 只支持直接子节点，不支持嵌套 tree"
                )

            components = stripped.split(".")
            if (
                any(
                    stripped == root_category
                    or stripped.startswith(f"{root_category}.")
                    for root_category in allowed_root_categories(category)
                )
                and all(PATH_COMPONENT_RE.fullmatch(component) for component in components)
            ):
                if root is not None:
                    if not blank_since_content:
                        raise MappingBuildError(
                            f"{page}:{line_number}: ownership trees 之间必须有空行"
                        )
                    flush_tree()
                if stripped in seen_roots:
                    raise MappingBuildError(
                        f"{page}:{line_number}: 重复 ownership root：{stripped}"
                    )
                for previous_root in seen_roots:
                    if stripped.startswith(f"{previous_root}.") or previous_root.startswith(
                        f"{stripped}."
                    ):
                        raise MappingBuildError(
                            f"{page}:{line_number}: ownership roots 不能是 ancestor/descendant："
                            f"{previous_root}, {stripped}"
                        )
                root = stripped
                seen_roots.add(stripped)
                blank_since_content = False
                continue
            raise MappingBuildError(
                f"{page}:{line_number}: 非法 Registration Hierarchy 行：{stripped}"
            )
        flush_tree()

    if not trees:
        raise MappingBuildError(f"{page}: Registration Hierarchy tree 为空")
    return trees


def _level3_pages(repo_root: Path, category: str) -> list[Path]:
    """List indexable English Level-3 pages for one build category."""
    pages_dir = level3_pages_dir(repo_root, category)
    if not pages_dir.is_dir():
        raise MappingBuildError(f"Level-3 目录不存在：{pages_dir}")
    pages = [
        page
        for page in sorted(pages_dir.glob("*.md"))
        if not page.name.startswith("vkt") and not page.stem.endswith("_brief")
    ]
    if not pages:
        raise MappingBuildError(f"没有可索引的 Level-3 页面：{pages_dir}")
    return pages


def _owner(page: Path, category: str, wiki_base_url: str) -> Owner:
    """Create the normalized owner record and Wiki URL for one page."""
    page_category = wiki_page_category(category)
    return Owner(
        page=page.stem,
        category=category,
        wiki_url=(
            f"{wiki_base_url.rstrip('/')}/categories/{page_category}/{page.stem}"
        ),
        source_page=page,
    )


def _unique_owner(key: str, candidates: Iterable[Owner]) -> Owner:
    """Return one unique owner or fail on ambiguous ownership evidence."""
    candidates = tuple(candidates)
    by_page = {candidate.page: candidate for candidate in candidates}
    if len(by_page) != 1:
        pages = ", ".join(sorted(by_page))
        raise MappingBuildError(f"ownership 冲突：{key}: {pages}")
    return next(iter(by_page.values()))


def _resolve_exact_evidence(
    key: str, candidates: Iterable[tuple[Owner, bool]]
) -> Owner:
    """Prefer a page's hierarchy root over another page's representative child."""
    candidates = tuple(candidates)
    roots = [owner for owner, is_root in candidates if is_root]
    return _unique_owner(key, roots or (owner for owner, _is_root in candidates))


def collect_ownership_evidence(
    repo_root: Path, category: str, wiki_base_url: str
) -> tuple[dict[str, Owner], dict[str, Owner], list[Path]]:
    """Collect exact hierarchy prefixes and unique component aliases."""
    exact_candidates: dict[str, list[tuple[Owner, bool]]] = {}
    anchor_candidates: dict[str, list[Owner]] = {}
    pages = _level3_pages(repo_root, category)

    for page in pages:
        page_owner = _owner(page, category, wiki_base_url)
        trees = extract_page_ownership(page, category)
        if not trees:
            raise MappingBuildError(f"页面缺少 Registration Hierarchy：{page}")
        excluded_roots = OWNERSHIP_EXCLUSIONS.get(category, {}).get(
            page.stem, frozenset()
        )
        for tree in trees:
            if not tree_belongs_to_category(tree.root, category):
                continue
            if tree.root in excluded_roots:
                continue
            anchor_candidates.setdefault(tree.root.rsplit(".", 1)[-1], []).append(
                page_owner
            )
            if tree.children:
                for child in tree.children:
                    evidence = f"{tree.root}.{child}"
                    if evidence in excluded_roots:
                        continue
                    exact_candidates.setdefault(
                        f"dEQP-VK.{evidence}", []
                    ).append((page_owner, False))
                    anchor_candidates.setdefault(child, []).append(page_owner)
            else:
                exact_candidates.setdefault(f"dEQP-VK.{tree.root}", []).append(
                    (page_owner, True)
                )

    exact = {
        prefix: _resolve_exact_evidence(prefix, candidates)
        for prefix, candidates in sorted(exact_candidates.items())
    }
    # Ambiguous component aliases are excluded; exact evidence remains authoritative.
    anchors: dict[str, Owner] = {}
    for anchor, candidates in sorted(anchor_candidates.items()):
        by_page = {candidate.page: candidate for candidate in candidates}
        if len(by_page) == 1:
            anchors[anchor] = next(iter(by_page.values()))

    owners_by_page = {_owner(page, category, wiki_base_url).page: _owner(page, category, wiki_base_url) for page in pages}
    for alias, page_name in OWNERSHIP_ALIASES.get(category, {}).items():
        if alias in anchors:
            raise MappingBuildError(f"显式 alias 与 hierarchy anchor 冲突：{category}.{alias}")
        try:
            anchors[alias] = owners_by_page[page_name]
        except KeyError as error:
            raise MappingBuildError(
                f"alias 目标页面不存在：{category}.{alias} -> {page_name}"
            ) from error

    return exact, anchors, pages


def _add_mapping(
    mappings: dict[str, Owner], prefix: str, owner: Owner
) -> None:
    """Add one candidate mapping and reject contradictory evidence."""
    previous = mappings.get(prefix)
    if previous is not None and previous.page != owner.page:
        raise MappingBuildError(
            f"ownership 冲突：{prefix}: {previous.page}, {owner.page}"
        )
    mappings[prefix] = owner


def _declared_mappings(exact: dict[str, Owner]) -> dict[str, Owner]:
    """Turn page hierarchy evidence directly into DB candidate mappings."""
    mappings: dict[str, Owner] = {}
    for prefix, owner in exact.items():
        _add_mapping(mappings, prefix, owner)
    return mappings


def _prune_redundant_mappings(mappings: dict[str, Owner]) -> None:
    """Drop descendant rows covered by an explicitly declared same-owner root.

    A page may list a broad root and generated direct children in the same
    evidence set.  The broad root is the safer runtime key; retaining both
    would make the output reflect page exposition rather than the shortest
    declared ownership boundary.
    """
    for prefix in sorted(tuple(mappings), key=lambda value: (value.count("."), value)):
        owner = mappings.get(prefix)
        if owner is None:
            continue
        prefix_dot = f"{prefix}."
        for descendant in tuple(mappings):
            if descendant.startswith(prefix_dot) and mappings[descendant].page == owner.page:
                del mappings[descendant]


def _candidate_owner(
    path: str,
    category: str,
    mappings: dict[str, Owner],
    anchors: dict[str, Owner],
) -> tuple[Owner, str]:
    """Resolve a leaf against declared mappings, then explicit fallback anchors."""
    components = path.split(".")
    for end in range(len(components), 2, -1):
        prefix = ".".join(components[:end])
        owner = mappings.get(prefix)
        if owner is not None:
            return owner, prefix

    # This fallback is intentionally build-time only.  It preserves explicit
    # reviewed aliases and unique hierarchy anchors for migration cases, but
    # never becomes runtime lookup behavior.
    matches: list[tuple[int, int, Owner, str]] = []
    for position, component in enumerate(components[2:], start=2):
        candidate = component
        while candidate:
            owner = anchors.get(candidate)
            if owner is not None:
                matches.append(
                    (len(candidate), -position, owner, ".".join(components[: position + 1]))
                )
            if "_" not in candidate:
                break
            candidate = candidate.rsplit("_", 1)[0]
    if not matches:
        raise MappingBuildError(f"缺少 ownership evidence：{path}")
    best_key = max((length, position) for length, position, _owner, _prefix in matches)
    best = [match for match in matches if match[:2] == best_key]
    owners = {owner.page: owner for _length, _position, owner, _prefix in best}
    if len(owners) != 1:
        raise MappingBuildError(
            f"ownership 冲突：{path}: {', '.join(sorted(owners))}"
        )
    owner = next(iter(owners.values()))
    return owner, best[0][3]


def _validate_coverage_and_collect_fallbacks(
    mustpass_files: Sequence[Path],
    category: str,
    mappings: dict[str, Owner],
    anchors: dict[str, Owner],
) -> tuple[int, set[str]]:
    """Validate every executable leaf without materializing leaf-owner rows."""
    leaf_count = 0
    owner_pages: set[str] = set()
    for path in iter_mustpass_leaves(mustpass_files, category):
        owner, prefix = _candidate_owner(path, category, mappings, anchors)
        if prefix not in mappings:
            raise MappingBuildError(
                f"缺少 exact ownership evidence：{path}; "
                f"diagnostic anchor suggests {owner.page} via {prefix}"
            )
        leaf_count += 1
        owner_pages.add(owner.page)
    return leaf_count, owner_pages


def iter_mustpass_leaves(
    mustpass_files: Sequence[Path], category: str
) -> Iterator[str]:
    """Yield validated, globally unique leaves from configured mustpass inputs."""
    seen: set[str] = set()
    for mustpass_file in mustpass_files:
        previous: str | None = None
        with mustpass_file.open(encoding="utf-8") as cases:
            for line_number, line in enumerate(cases, 1):
                path = line.strip()
                if not path:
                    continue
                components = path.split(".")
                if (
                    len(components) < 3
                    or components[:2] != ["dEQP-VK", category]
                    or not all(
                        MUSTPASS_COMPONENT_RE.fullmatch(part)
                        for part in components[1:]
                    )
                ):
                    raise MappingBuildError(
                        f"{mustpass_file}:{line_number}: 非法 registration path：{path}"
                    )
                if path in seen:
                    raise MappingBuildError(
                        f"{mustpass_file}:{line_number}: 重复 path：{path}"
                    )
                if previous is not None and path < previous:
                    raise MappingBuildError(
                        f"{mustpass_file}: mustpass paths 未按字典序排列"
                    )
                seen.add(path)
                previous = path
                yield path


def _sha256(path: Path) -> str:
    """Return the SHA-256 digest used in source-manifest metadata."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_manifest(repo_root: Path, files: Sequence[Path]) -> str:
    """Serialize stable repository-relative hashes for all build inputs."""
    manifest = [
        {
            "path": str(path.resolve().relative_to(repo_root.resolve())),
            "sha256": _sha256(path),
        }
        for path in sorted(files)
    ]
    return json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))


def _write_database(
    database_path: Path,
    rows: Sequence[MappingRow],
    metadata: dict[str, str],
) -> None:
    """Atomically write validated mapping rows and metadata to SQLite."""
    database_path = database_path.resolve()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = database_path.with_suffix(database_path.suffix + ".tmp")
    temporary_path.unlink(missing_ok=True)
    # The sqlite3 context manager only commits; it does not close the
    # connection.  Close it explicitly before replace/unlink: Windows
    # forbids renaming or deleting files with an open handle.
    connection = sqlite3.connect(temporary_path)
    try:
        with connection:
            connection.executescript(
                """
                PRAGMA journal_mode = OFF;
                PRAGMA synchronous = OFF;
                CREATE TABLE mappings (
                    prefix TEXT PRIMARY KEY,
                    page TEXT NOT NULL,
                    category TEXT NOT NULL,
                    wiki_url TEXT NOT NULL
                );
                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            connection.executemany(
                "INSERT INTO mappings VALUES (?, ?, ?, ?)",
                (
                    (row.prefix, row.page, row.category, row.wiki_url)
                    for row in sorted(rows, key=lambda item: item.prefix)
                ),
            )
            connection.executemany(
                "INSERT INTO metadata VALUES (?, ?)", sorted(metadata.items())
            )
        connection.close()
        temporary_path.replace(database_path)
    finally:
        connection.close()
        temporary_path.unlink(missing_ok=True)


def build_category_database(
    repo_root: Path,
    category: str,
    database_path: Path,
    wiki_base_url: str = DEFAULT_WIKI_BASE_URL,
) -> dict[str, int | str]:
    """Build and atomically replace one independently validated category DB."""
    repo_root = repo_root.resolve()
    try:
        relative_mustpass_files = CATEGORY_MUSTPASS_FILES[category]
    except KeyError as error:
        raise MappingBuildError(f"不支持的 category：{category}") from error
    mustpass_root = repo_root / "external/vulkancts/mustpass/main/vk-default"
    mustpass_files = tuple(mustpass_root / path for path in relative_mustpass_files)
    missing_files = [path for path in mustpass_files if not path.is_file()]
    if missing_files:
        raise MappingBuildError(f"mustpass 文件不存在：{missing_files[0]}")
    exact, anchors, pages = collect_ownership_evidence(
        repo_root, category, wiki_base_url
    )

    # Registration Hierarchy is the primary ownership source.  Start with the
    # reviewed page prefixes and use mustpass only to discover real variant
    # namespaces and validate full executable-leaf coverage.  In particular,
    # do not materialize one Owner record for every mustpass leaf and then
    # attempt to reconstruct the already-declared prefix tree from it.
    mappings = _declared_mappings(exact)
    _prune_redundant_mappings(mappings)
    projected = project_category_mappings(
        mappings, iter_mustpass_leaves(mustpass_files, category), category
    )
    for prefix, owner in projected.items():
        _add_mapping(mappings, prefix, owner)
    leaf_count, owner_pages = _validate_coverage_and_collect_fallbacks(
        mustpass_files, category, mappings, anchors
    )
    if category == "pipeline":
        _prune_redundant_mappings(mappings)
    rows = [
        MappingRow(prefix, owner.page, owner.category, owner.wiki_url)
        for prefix, owner in sorted(mappings.items())
    ]
    if any(row.category != category for row in rows):
        raise MappingBuildError(f"{category}: mapping 包含其它 category owner")

    metadata = {
        "category": category,
        "categories": category,
        "kind": "category",
        "leaf_count": str(leaf_count),
        "mapping_count": str(len(rows)),
        "owner_page_count": str(len(owner_pages)),
        "schema_version": SCHEMA_VERSION,
        "source_manifest": _source_manifest(repo_root, [*mustpass_files, *pages]),
        "wiki_base_url": wiki_base_url.rstrip("/"),
    }
    _write_database(database_path, rows, metadata)
    return {
        "category": category,
        "leaves": leaf_count,
        "mappings": len(rows),
        "owner_pages": len(owner_pages),
    }


def _read_metadata(connection: sqlite3.Connection) -> dict[str, str]:
    """Read the key-value metadata table from an open category DB."""
    return dict(connection.execute("SELECT key, value FROM metadata"))


def merge_category_databases(
    category_databases: Sequence[Path], database_path: Path
) -> dict[str, int | list[str]]:
    """Validate category DBs and atomically rebuild the final DB in stable order."""
    by_category: dict[str, tuple[Path, dict[str, str]]] = {}
    wiki_base_url: str | None = None
    for path in category_databases:
        # Close explicitly: the sqlite3 context manager only commits, and an
        # open read-only handle blocks later replace/unlink on Windows.
        connection = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
        try:
            with connection:
                metadata = _read_metadata(connection)
                if metadata.get("schema_version") != SCHEMA_VERSION:
                    raise MappingBuildError(f"{path}: schema version 不兼容")
                if metadata.get("kind") != "category" or not metadata.get("category"):
                    raise MappingBuildError(f"{path}: 不是有效 category DB")
                category = metadata["category"]
                if category in by_category:
                    raise MappingBuildError(f"重复 category DB：{category}")
                if wiki_base_url is None:
                    wiki_base_url = metadata.get("wiki_base_url")
                elif metadata.get("wiki_base_url") != wiki_base_url:
                    raise MappingBuildError("category DB 的 Wiki base URL 不一致")
                actual_count = connection.execute("SELECT count(*) FROM mappings").fetchone()[0]
                if actual_count != int(metadata.get("mapping_count", "-1")):
                    raise MappingBuildError(f"{path}: mapping count metadata 不一致")
                invalid = connection.execute(
                    "SELECT prefix FROM mappings WHERE category != ? LIMIT 1", (category,)
                ).fetchone()
                if invalid:
                    raise MappingBuildError(f"{path}: 包含其它 category mapping")
                by_category[category] = (path, metadata)
        finally:
            connection.close()

    if not by_category:
        raise MappingBuildError("没有 category DB 可合并")

    rows: list[MappingRow] = []
    source_manifests: dict[str, object] = {}
    for category in sorted(by_category):
        path, metadata = by_category[category]
        source_manifests[category] = json.loads(metadata["source_manifest"])
        # Close explicitly so the handle cannot block a later rebuild.
        connection = sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True)
        try:
            with connection:
                for prefix, page, row_category, wiki_url in connection.execute(
                    "SELECT prefix, page, category, wiki_url FROM mappings ORDER BY prefix"
                ):
                    rows.append(MappingRow(prefix, page, row_category, wiki_url))
        finally:
            connection.close()

    prefixes = [row.prefix for row in rows]
    if len(prefixes) != len(set(prefixes)):
        raise MappingBuildError("category DB 之间存在重复 prefix")
    categories = sorted(by_category)
    metadata = {
        "categories": ",".join(categories),
        "kind": "final",
        "mapping_count": str(len(rows)),
        "schema_version": SCHEMA_VERSION,
        "source_manifest": json.dumps(
            source_manifests, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ),
        "wiki_base_url": wiki_base_url or "",
    }
    _write_database(database_path, rows, metadata)
    return {
        "category_count": len(categories),
        "categories": categories,
        "mappings": len(rows),
    }


def _ordered_categories(categories: Sequence[str]) -> list[str]:
    """Validate a category selection and return canonical registry order."""
    if not categories:
        raise MappingBuildError("至少需要一个 category")
    if len(categories) != len(set(categories)):
        raise MappingBuildError("category 列表包含重复项")
    unknown_categories = set(categories) - CATEGORY_MUSTPASS_FILES.keys()
    if unknown_categories:
        unknown = ", ".join(sorted(unknown_categories))
        raise MappingBuildError(f"不支持的 category：{unknown}")
    selected = set(categories)
    return [
        category for category in CATEGORY_MUSTPASS_FILES if category in selected
    ]


def build_category_databases(
    repo_root: Path,
    categories: Sequence[str] = DEFAULT_CATEGORIES,
    wiki_base_url: str = DEFAULT_WIKI_BASE_URL,
    category_db_dir: Path | None = None,
) -> dict[str, dict[str, int | str]]:
    """Build selected category DBs without creating or replacing the final DB."""
    ordered_categories = _ordered_categories(categories)
    category_db_dir = category_db_dir or Path(__file__).with_name("db")
    category_stats: dict[str, dict[str, int | str]] = {}
    for category in ordered_categories:
        path = category_db_dir / f"{category}.sqlite3"
        category_stats[category] = build_category_database(
            repo_root, category, path, wiki_base_url
        )
    return category_stats


def merge_selected_category_databases(
    database_path: Path,
    categories: Sequence[str] = DEFAULT_CATEGORIES,
    category_db_dir: Path | None = None,
    json_path: Path | None = None,
) -> dict[str, int | str | list[str]]:
    """Merge selected category DBs and optionally export runtime JSON."""
    ordered_categories = _ordered_categories(categories)
    category_db_dir = category_db_dir or Path(__file__).with_name("db")
    category_paths = [
        category_db_dir / f"{category}.sqlite3" for category in ordered_categories
    ]
    missing = [path for path in category_paths if not path.is_file()]
    if missing:
        raise MappingBuildError(f"category DB 不存在：{missing[0]}")
    stats: dict[str, int | str | list[str]] = dict(
        merge_category_databases(category_paths, database_path)
    )
    if json_path is not None:
        exported = export_lookup_json(database_path, json_path)
        if exported["category_count"] != stats["category_count"]:
            raise MappingBuildError("runtime JSON category count 与 final DB 不一致")
        if exported["mapping_count"] != stats["mappings"]:
            raise MappingBuildError("runtime JSON mapping count 与 final DB 不一致")
        stats["json"] = str(json_path.resolve())
    return stats


def build_database(
    repo_root: Path,
    database_path: Path,
    categories: Sequence[str] = DEFAULT_CATEGORIES,
    wiki_base_url: str = DEFAULT_WIKI_BASE_URL,
    category_db_dir: Path | None = None,
    json_path: Path | None = None,
) -> dict[str, object]:
    """Build intermediate DBs and the final tracked runtime JSON."""
    category_stats = build_category_databases(
        repo_root, categories, wiki_base_url, category_db_dir
    )
    merge_stats = merge_selected_category_databases(
        database_path, categories, category_db_dir, json_path
    )
    return {"categories": category_stats, "final": merge_stats}


def _default_repo_root() -> Path:
    """Resolve the repository root relative to this build script."""
    return Path(__file__).resolve().parents[4]


def parse_args() -> argparse.Namespace:
    """Parse CLI paths, category selection, Wiki URL, and build mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    parser.add_argument(
        "--database", type=Path, default=Path(__file__).with_name("vkcts_lookup.sqlite3")
    )
    parser.add_argument("--db-dir", type=Path, default=Path(__file__).with_name("db"))
    parser.add_argument(
        "--json",
        type=Path,
        default=Path(__file__).with_name("site") / "mappings.json",
        help="tracked runtime JSON written by all/merge modes",
    )
    parser.add_argument("--categories", nargs="+", default=list(DEFAULT_CATEGORIES))
    parser.add_argument("--wiki-base-url", default=DEFAULT_WIKI_BASE_URL)
    parser.add_argument(
        "--mode",
        choices=("all", "categories", "merge"),
        default="all",
        help=(
            "all builds category DBs then merges them; categories builds only "
            "category DBs; merge merges existing category DBs only"
        ),
    )
    return parser.parse_args()


def main() -> int:
    """Run the selected category-build, merge, or complete build workflow."""
    args = parse_args()
    if args.mode == "categories":
        stats: dict[str, object] = {
            "categories": build_category_databases(
                args.repo_root,
                args.categories,
                args.wiki_base_url,
                args.db_dir,
            )
        }
    elif args.mode == "merge":
        stats = {
            "final": merge_selected_category_databases(
                args.database,
                args.categories,
                args.db_dir,
                args.json,
            )
        }
    else:
        stats = build_database(
            args.repo_root,
            args.database,
            args.categories,
            args.wiki_base_url,
            args.db_dir,
            args.json,
        )
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
