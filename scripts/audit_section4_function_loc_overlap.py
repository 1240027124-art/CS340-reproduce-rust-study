#!/usr/bin/env python3

import csv
import subprocess
import sys
from pathlib import Path
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from unsafe_fn_extractor_lexer import extract_unsafe_fn

SOURCE_ROOT = ROOT / "projects/rust-2019-study/rust/src/libstd"
RUST_REPO = ROOT / "projects/rust-2019-study/rust"
REMOVER = ROOT / "comment_remover/comment_remover_linux"

CSV_OUTPUT = ROOT / "results/section4/rust_std_function_loc_overlap_audit.csv"
REPORT_OUTPUT = ROOT / "results/section4/rust_std_function_loc_overlap_report.txt"

EXPECTED_COMMIT = "2975a3c4befa8ad610da2e3c5f5de351d6d70a2b"

MODULES = [
    "collections",
    "io",
    "net",
    "os",
    "sync",
    "sys",
    "thread",
]


def verify_environment():
    result = subprocess.run(
        ["git", "-C", str(RUST_REPO), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )

    if result.stdout.strip() != EXPECTED_COMMIT:
        raise RuntimeError("Unexpected historical Rust dataset version")

    if not REMOVER.is_file():
        raise RuntimeError(f"Missing comment remover: {REMOVER}")

    print("[PASS] Historical dataset version verified")
    print("[PASS] Comment remover found")


def merge_intervals(intervals):
    if not intervals:
        return []

    ordered = sorted(intervals)
    merged = [list(ordered[0])]

    for start, end in ordered[1:]:
        if start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


def interval_length(intervals):
    return sum(end - start + 1 for start, end in intervals)


def audit_file(path):
    result = subprocess.run(
        [str(REMOVER), str(path)],
        capture_output=True,
        text=True,
        check=True,
    )

    lines = result.stdout.splitlines(keepends=True)
    functions = extract_unsafe_fn(lines)

    intervals = []
    invalid = []

    for index, function in enumerate(functions, 1):
        start = function.start_line_no
        end = function.end_line_no

        if start < 1 or end < start or end > len(lines):
            invalid.append((index, start, end))
            continue

        intervals.append((start, end))

    raw_loc = interval_length(intervals)
    merged = merge_intervals(intervals)
    unique_loc = interval_length(merged)
    duplicate_loc = raw_loc - unique_loc

    overlaps = []

    for (i, first), (j, second) in combinations(
        enumerate(intervals, 1), 2
    ):
        start = max(first[0], second[0])
        end = min(first[1], second[1])

        if start <= end:
            overlaps.append((i, j, start, end))

    return {
        "functions": len(functions),
        "raw_loc": raw_loc,
        "unique_loc": unique_loc,
        "duplicate_loc": duplicate_loc,
        "invalid": invalid,
        "intervals": intervals,
        "overlaps": overlaps,
    }


def main():
    verify_environment()

    rows = []
    report = []

    totals = {
        "files": 0,
        "functions": 0,
        "raw_loc": 0,
        "unique_loc": 0,
        "duplicate_loc": 0,
        "overlap_files": 0,
        "overlap_pairs": 0,
        "invalid": 0,
    }

    for module in MODULES:
        directory = SOURCE_ROOT / module

        if not directory.is_dir():
            raise RuntimeError(f"Missing module: {directory}")

        files = sorted(directory.rglob("*.rs"))

        module_totals = {
            "files": len(files),
            "functions": 0,
            "raw_loc": 0,
            "unique_loc": 0,
            "duplicate_loc": 0,
            "overlap_files": 0,
            "overlap_pairs": 0,
            "invalid": 0,
        }

        for path in files:
            result = audit_file(path)

            module_totals["functions"] += result["functions"]
            module_totals["raw_loc"] += result["raw_loc"]
            module_totals["unique_loc"] += result["unique_loc"]
            module_totals["duplicate_loc"] += result["duplicate_loc"]
            module_totals["invalid"] += len(result["invalid"])

            if result["overlaps"]:
                module_totals["overlap_files"] += 1
                module_totals["overlap_pairs"] += len(result["overlaps"])

                relative = path.relative_to(SOURCE_ROOT)

                report.append(f"\nFILE: {relative}")
                report.append(
                    f"Functions: {result['functions']}"
                )
                report.append(
                    f"Raw LOC: {result['raw_loc']}"
                )
                report.append(
                    f"Unique LOC: {result['unique_loc']}"
                )
                report.append(
                    f"Duplicate LOC: {result['duplicate_loc']}"
                )

                for i, j, start, end in result["overlaps"]:
                    report.append(
                        f"Overlap: Function {i} and Function {j}: "
                        f"{start}-{end} ({end - start + 1} LOC)"
                    )

            if result["invalid"]:
                report.append(f"\nINVALID INTERVALS: {path}")
                for item in result["invalid"]:
                    report.append(str(item))

        rows.append({
            "Module": module,
            "Rust_Files": module_totals["files"],
            "Unsafe_Functions": module_totals["functions"],
            "Raw_Function_LOC": module_totals["raw_loc"],
            "Unique_Function_LOC": module_totals["unique_loc"],
            "Duplicate_LOC": module_totals["duplicate_loc"],
            "Files_With_Overlap": module_totals["overlap_files"],
            "Overlap_Pairs": module_totals["overlap_pairs"],
            "Invalid_Intervals": module_totals["invalid"],
        })

        for key in totals:
            totals[key] += module_totals[key]

        print(f"\n===== MODULE: {module} =====")
        for key, value in module_totals.items():
            print(f"{key}: {value}")

    CSV_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    summary = [
        "=" * 70,
        "SECTION 4 FUNCTION LOC OVERLAP AUDIT",
        "=" * 70,
        "",
    ]

    for key, value in totals.items():
        summary.append(f"{key}: {value}")

    summary.extend([
        "",
        "OVERLAPPING FILE DETAILS",
        "=" * 70,
    ])

    summary.extend(report)

    summary.extend([
        "",
        "=" * 70,
        "AUDIT COMPLETE",
        "=" * 70,
    ])

    REPORT_OUTPUT.write_text(
        "\n".join(summary) + "\n",
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("FINAL TOTALS")
    print("=" * 70)

    for key, value in totals.items():
        print(f"{key}: {value}")

    if totals["invalid"] != 0:
        raise RuntimeError("Invalid intervals detected")

    print("\n[PASS] No invalid intervals")
    print(f"[PASS] CSV saved: {CSV_OUTPUT}")
    print(f"[PASS] Report saved: {REPORT_OUTPUT}")


if __name__ == "__main__":
    main()
