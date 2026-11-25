#!/usr/bin/env python3

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from unsafe_block_extractor_lexer import extract_macro

SOURCE_ROOT = ROOT / "projects/rust-2019-study/rust/src/libstd"
REMOVER = ROOT / "comment_remover/comment_remover_linux"

OUTPUT = ROOT / "results/section4/rust_std_lexer_audit.csv"

EXPECTED_COMMIT = "2975a3c4befa8ad610da2e3c5f5de351d6d70a2b"

ORIGINAL_COUNTS = {
    "collections": 24,
    "io": 9,
    "net": 4,
    "os": 13,
    "sync": 112,
    "sys": 562,
    "thread": 12,
}

def verify_dataset():
    result = subprocess.run(
        ["git", "-C", str(ROOT / "projects/rust-2019-study/rust"),
         "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )

    actual = result.stdout.strip()

    if actual != EXPECTED_COMMIT:
        raise RuntimeError(
            f"Unexpected dataset version: {actual}"
        )

    print("[PASS] Historical dataset version verified")


def audit_module(module, original_count):
    directory = SOURCE_ROOT / module

    if not directory.is_dir():
        raise RuntimeError(f"Missing module: {directory}")

    files = sorted(directory.rglob("*.rs"))

    region_count = 0
    region_loc = 0
    invalid_count = 0

    for path in files:
        result = subprocess.run(
            [str(REMOVER), str(path)],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.splitlines(keepends=True)

        regions = extract_macro(lines)

        for region in regions:
            region_count += 1

            start = region.start_line_no
            end = region.end_line_no

            if start < 1 or end < start or end > len(lines):
                invalid_count += 1
                continue

            region_loc += end - start + 1

    if invalid_count:
        raise RuntimeError(
            f"{module}: {invalid_count} invalid intervals"
        )

    return {
        "Module": module,
        "Rust_Files": len(files),
        "Original_Unsafe_Regions": original_count,
        "Lexer_Unsafe_Regions": region_count,
        "Difference": region_count - original_count,
        "Lexer_Unsafe_Region_LOC": region_loc,
        "Invalid_Intervals": invalid_count,
    }


def main():
    verify_dataset()

    rows = []

    for module, original_count in ORIGINAL_COUNTS.items():
        print(f"\n===== MODULE: {module} =====")

        row = audit_module(module, original_count)
        rows.append(row)

        for key, value in row.items():
            print(f"{key}: {value}")

        print("[PASS] All intervals valid")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n===== FINAL TOTALS =====")

    for key in (
        "Rust_Files",
        "Original_Unsafe_Regions",
        "Lexer_Unsafe_Regions",
        "Difference",
        "Lexer_Unsafe_Region_LOC",
        "Invalid_Intervals",
    ):
        print(f"{key}: {sum(row[key] for row in rows)}")

    print(f"\nResults saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
