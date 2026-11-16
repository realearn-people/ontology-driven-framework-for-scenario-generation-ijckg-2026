from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.csv"
CHECKSUMS = ROOT / "CHECKSUMS_SHA256.txt"
CONTROL_NAMES = {"MANIFEST.csv", "CHECKSUMS_SHA256.txt"}
EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
}
OPTIONAL_PORTABILITY_PATHS = {
    ".gitattributes",
    ".gitignore",
}
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    ".psq_runs",
    ".macos_test_output",
    ".portable_runtime",
    "live_scenario_output",
    "__pycache__",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative_files(*, include_manifest: bool) -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts):
            continue
        if path.name in EXCLUDED_FILE_NAMES:
            continue
        if relative.as_posix() in OPTIONAL_PORTABILITY_PATHS:
            continue
        if relative.as_posix() == "CHECKSUMS_SHA256.txt":
            continue
        if not include_manifest and relative.as_posix() == "MANIFEST.csv":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix().lower())


def category(relative: Path) -> str:
    return relative.parts[0] if len(relative.parts) > 1 else "package_control"


def generate() -> int:
    payload_files = relative_files(include_manifest=False)
    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("relative_path", "category", "extension", "size_bytes", "sha256"),
            lineterminator="\n",
        )
        writer.writeheader()
        for path in payload_files:
            relative = path.relative_to(ROOT)
            writer.writerow(
                {
                    "relative_path": relative.as_posix(),
                    "category": category(relative),
                    "extension": path.suffix.lower() or "(none)",
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    checksum_files = relative_files(include_manifest=True)
    with CHECKSUMS.open("w", encoding="utf-8", newline="\n") as handle:
        for path in checksum_files:
            relative = path.relative_to(ROOT).as_posix()
            handle.write(f"{sha256(path)}  {relative}\n")

    total_bytes = sum(path.stat().st_size for path in checksum_files) + CHECKSUMS.stat().st_size
    print(
        f"Generated manifest for {len(payload_files)} payload files and checksums for "
        f"{len(checksum_files)} files; package size={total_bytes} bytes"
    )
    return 0


def verify() -> int:
    if not CHECKSUMS.exists():
        print("FAIL: CHECKSUMS_SHA256.txt is missing")
        return 1
    expected: dict[str, str] = {}
    for line_number, line in enumerate(CHECKSUMS.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            print(f"FAIL: malformed checksum line {line_number}")
            return 1
        expected[relative] = digest.lower()

    actual_files = relative_files(include_manifest=True)
    actual_names = {path.relative_to(ROOT).as_posix() for path in actual_files}
    expected_names = set(expected)
    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    mismatched = []
    for relative in sorted(expected_names & actual_names):
        digest = sha256(ROOT / Path(relative))
        if digest.lower() != expected[relative]:
            mismatched.append(relative)

    if missing or extra or mismatched:
        for relative in missing:
            print(f"MISSING: {relative}")
        for relative in extra:
            print(f"UNLISTED: {relative}")
        for relative in mismatched:
            print(f"MISMATCH: {relative}")
        return 1
    print(f"PASS: verified {len(expected)} files against CHECKSUMS_SHA256.txt")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify the handover manifest and SHA-256 checksums.")
    parser.add_argument("action", choices=("generate", "verify"))
    args = parser.parse_args()
    return generate() if args.action == "generate" else verify()


if __name__ == "__main__":
    raise SystemExit(main())
