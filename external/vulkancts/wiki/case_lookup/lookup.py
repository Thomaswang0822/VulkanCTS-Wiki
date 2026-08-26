"""JSON-backed component-boundary registration-path lookup core."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

PATH_COMPONENT_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class InvalidPathError(ValueError):
    """Raised when a query is not a full dEQP-VK registration path."""


@dataclass(frozen=True)
class LookupResult:
    path: str
    matched_prefix: str
    page: str
    category: str
    wiki_url: str


class LookupIndex:
    """JSON-backed component-boundary-safe longest-prefix lookup."""

    def __init__(self, json_path: Path):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or not isinstance(
            payload.get("mappings"), dict
        ):
            raise ValueError("lookup JSON schema 不兼容")
        mappings = payload["mappings"]
        if payload.get("mapping_count") != len(mappings):
            raise ValueError("lookup JSON mapping count 不一致")
        self.mappings: dict[str, list[str]] = mappings

    def close(self) -> None:
        """Retain context-manager compatibility; JSON lookup owns no resources."""

    @staticmethod
    def validate_path(path: str) -> str:
        normalized = path.strip()
        components = normalized.split(".")
        if (
            len(components) < 3
            or components[0] != "dEQP-VK"
            or not all(PATH_COMPONENT_RE.fullmatch(component) for component in components[1:])
        ):
            raise InvalidPathError(
                "请输入以 dEQP-VK. 开头的完整 registration path。"
            )
        return normalized

    def lookup(self, path: str) -> LookupResult | None:
        normalized = self.validate_path(path)
        components = normalized.split(".")
        for end in range(len(components), 2, -1):
            prefix = ".".join(components[:end])
            row = self.mappings.get(prefix)
            if row is not None:
                page, category, wiki_url = row
                return LookupResult(
                    path=normalized,
                    matched_prefix=prefix,
                    page=page,
                    category=category,
                    wiki_url=wiki_url,
                )
        return None


def validate_mustpass(
    json_path: Path, mustpass_files: Sequence[Path], sample_limit: int = 20
) -> dict[str, object]:
    """Run the simplified runtime lookup for every non-empty mustpass case."""
    index = LookupIndex(json_path)
    total = 0
    passed = 0
    failure_samples: list[str] = []
    per_file: dict[str, dict[str, int]] = {}
    try:
        for mustpass_file in mustpass_files:
            file_total = 0
            file_passed = 0
            with mustpass_file.open(encoding="utf-8") as cases:
                for line in cases:
                    path = line.strip()
                    if not path:
                        continue
                    total += 1
                    file_total += 1
                    try:
                        result = index.lookup(path)
                    except InvalidPathError:
                        result = None
                    if result is not None:
                        passed += 1
                        file_passed += 1
                    elif len(failure_samples) < sample_limit:
                        failure_samples.append(path)
            per_file[str(mustpass_file)] = {
                "total": file_total,
                "passed": file_passed,
                "failed": file_total - file_passed,
            }
    finally:
        index.close()

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "failure_samples": failure_samples,
        "per_file": per_file,
    }


def _default_json() -> Path:
    return Path(__file__).with_name("site") / "mappings.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    lookup_parser = subparsers.add_parser("lookup", help="查询一个完整 registration path")
    lookup_parser.add_argument("path")
    lookup_parser.add_argument("--json", type=Path, default=_default_json())

    validate_parser = subparsers.add_parser(
        "validate", help="对 mustpass 文件运行全量 core lookup"
    )
    validate_parser.add_argument("files", nargs="+", type=Path)
    validate_parser.add_argument("--json", type=Path, default=_default_json())

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "lookup":
        index = LookupIndex(args.json)
        try:
            result = index.lookup(args.path)
        finally:
            index.close()
        if result is None:
            print("当前索引中没有对应的 Level-3 页面。", flush=True)
            return 1
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate":
        report = validate_mustpass(args.json, args.files)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["failed"] == 0 else 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
