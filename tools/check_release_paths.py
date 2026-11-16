#!/usr/bin/env python3
"""Reject machine-specific paths in the distributed source and text artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", ".psq_runs", ".macos_test_output", ".portable_runtime",
             "live_scenario_output", "__pycache__", ".pytest_cache", ".mypy_cache"}
TEXT_SUFFIXES = {".cfg", ".cff", ".cmd", ".command", ".conf", ".csv", ".env.example",
                 ".gitattributes", ".gitignore", ".html", ".ini", ".java", ".json", ".jsonl",
                 ".md", ".owl", ".ps1", ".py", ".rq", ".sh", ".tex", ".toml", ".tsv",
                 ".ttl", ".txt", ".xml", ".yaml", ".yml"}
HOST_PATH = re.compile(
    r"(?<![\w:/])(?:[a-z]:[\\/]+(?=[\w.])|/(?:Users|home)/(?=[\w.])|file:/+(?=[\w.]))", re.I
)
RAW_WORKBOOK = re.compile(r"knowledge_base[/\\]+raw_data[/\\]+smsfraud[.]xlsx?\b", re.I)


def audit(root: Path) -> tuple[int, list[str]]:
    count = 0
    errors = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts) or relative.parts[0] == "output":
            continue
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in TEXT_SUFFIXES:
            continue
        # The release intentionally includes UTF-8 text and a few older UTF-16 notes.
        data = path.read_bytes()
        encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        try:
            source = data.decode(encoding)
        except UnicodeDecodeError:
            errors.append(f"{relative.as_posix()}: unexpected text encoding")
            continue
        count += 1
        for index, line in enumerate(source.splitlines(), 1):
            if HOST_PATH.search(line) or RAW_WORKBOOK.search(line):
                errors.append(f"{relative.as_posix()}:{index}")
    return count, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    count, errors = audit(ROOT)
    if errors:
        print("\n".join(errors[:80]))
        print(f"FAIL: {len(errors)} path or encoding finding(s) in {count} text assets")
        return 1
    print(f"PASS: no author-machine paths in {count} distributed text assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
