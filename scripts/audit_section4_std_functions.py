#!/usr/bin/env python3

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from unsafe_fn_extractor_lexer import extract_unsafe_fn

SOURCE_ROOT = ROOT / "projects/rust-2019-study/rust/src/libstd"
REMOVER = ROOT / "comment_remover/comment_remover_linux"

OUTPUT = ROOT / "results/section4/rust_std_function_lexer_audit.csv"

EXPECTED_COMMIT = "2975a3c4befa8ad610da2e3c5f5de351d6d70a2b"

HISTORICAL_COUNTS = {
    "collections": 10,
    "io": 16,
    "net": 2,
    "os": 0,
    "sync": 13,
    "sys": 523,
    "thread": 8,
}

# Verify the historical dataset version.
result = subprocess.run(
    ["git", "-C", str(ROOT / "projects/rust-2019-study/rust"),
     "rev-parse", "HEAD"],
    capture_output=True,
    text=True,
    check=True,
)

if result.stdout.strip() != EXPECTED_COMMIT:
    raise RuntimeError("Unexpected historical Rust dataset version")

if not REMOVER.is_file():
    raise RuntimeError(f"Missing comment remover: {REMOVER}")

print("[PASS] Historical dataset version verified")

rows = []

for module, historical_count in HISTORICAL_COUNTS.items():

    directory = SOURCE_ROOT / module

    if not directory.is_dir():
        raise RuntimeError(f"Missing module: {directory}")

    files = sorted(directory.rglob("*.rs"))

    function_count = 0
    function_loc = 0
    invalid_intervals = 0

    print(f"\n===== MODULE: {module} =====")

    for path in files:

        result = subprocess.run(
            [str(REMOVER), str(path)],
            capture_output=True,
            text=True,
            check=True,
        )

        lines = result.stdout.splitlines(keepends=True)

        functions = extract_unsafe_fn(lines)

        for function in functions:

            start = function.start_line_no
            end = function.end_line_no

            function_count += 1

            if start < 1 or end < start or end > len(lines):
                invalid_intervals += 1
                continue

            function_loc += end - start + 1

    difference = function_count - historical_count

    row = {
        "Module": module,
        "Rust_Files": len(files),
        "Historical_Unsafe_Functions": historical_count,
        "Lexer_Unsafe_Functions": function_count,
        "Difference": difference,
        "Lexer_Unsafe_Function_LOC": function_loc,
        "Invalid_Intervals": invalid_intervals,
    }

    rows.append(row)

    print("Rust files:", len(files))
    print("Historical functions:", historical_count)
    print("Lexer functions:", function_count)
    print("Difference:", difference)
    print("Lexer function LOC:", function_loc)
    print("Invalid intervals:", invalid_intervals)

    if invalid_intervals:
        raise RuntimeError(f"Invalid intervals in {module}")

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

print("Rust files:", sum(r["Rust_Files"] for r in rows))
print("Historical functions:", sum(r["Historical_Unsafe_Functions"] for r in rows))
print("Lexer functions:", sum(r["Lexer_Unsafe_Functions"] for r in rows))
print("Difference:", sum(r["Difference"] for r in rows))
print("Lexer function LOC:", sum(r["Lexer_Unsafe_Function_LOC"] for r in rows))
print("Invalid intervals:", sum(r["Invalid_Intervals"] for r in rows))

print(f"\nResults saved to: {OUTPUT}")
