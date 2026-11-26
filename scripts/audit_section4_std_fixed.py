#!/usr/bin/env python3

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from unsafe_block_extractor_fixed import extract_macro

source_root = (
    ROOT / "projects/rust-2019-study/rust/src/libstd"
)

remover = ROOT / "comment_remover/comment_remover_linux"

output = ROOT / "results/section4/rust_std_fixed_audit.csv"

modules = {
    "collections": 24,
    "io": 9,
    "net": 4,
    "os": 13,
    "sync": 112,
    "sys": 562,
    "thread": 12,
}

rows = []

for module, original_count in modules.items():

    directory = source_root / module

    if not directory.is_dir():
        raise RuntimeError(f"Missing module: {directory}")

    files = sorted(directory.rglob("*.rs"))

    fixed_count = 0
    fixed_loc = 0
    invalid_count = 0

    print(f"\n===== MODULE: {module} =====")

    for path in files:

        result = subprocess.run(
            [str(remover), str(path)],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.splitlines(keepends=True)

        regions = extract_macro(lines)

        for region in regions:

            start = region.start_line_no
            end = region.end_line_no

            fixed_count += 1

            if start < 1 or end < start or end > len(lines):
                invalid_count += 1
                continue

            fixed_loc += end - start + 1

    difference = fixed_count - original_count

    row = {
        "Module": module,
        "Rust_Files": len(files),
        "Original_Unsafe_Regions": original_count,
        "Fixed_Unsafe_Regions": fixed_count,
        "Difference": difference,
        "Fixed_Unsafe_Region_LOC": fixed_loc,
        "Invalid_Intervals": invalid_count,
    }

    rows.append(row)

    print(f"Rust files: {len(files)}")
    print(f"Original regions: {original_count}")
    print(f"Fixed regions: {fixed_count}")
    print(f"Difference: {difference}")
    print(f"Fixed region LOC: {fixed_loc}")
    print(f"Invalid intervals: {invalid_count}")

    if invalid_count:
        raise RuntimeError(f"Invalid intervals in {module}")

output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=list(rows[0].keys()),
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(rows)

print("\n===== FINAL TOTALS =====")

print("Rust files:", sum(r["Rust_Files"] for r in rows))
print("Original regions:", sum(r["Original_Unsafe_Regions"] for r in rows))
print("Fixed regions:", sum(r["Fixed_Unsafe_Regions"] for r in rows))
print("Difference:", sum(r["Difference"] for r in rows))
print("Fixed region LOC:", sum(r["Fixed_Unsafe_Region_LOC"] for r in rows))
print("Invalid intervals:", sum(r["Invalid_Intervals"] for r in rows))

print(f"\nResults saved to: {output}")
