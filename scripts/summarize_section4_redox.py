#!/usr/bin/env python3

import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
results = root / "results" / "section4"

def read_result(filename):
    with (results / filename).open() as f:
        return next(csv.DictReader(f))

full = read_result("redox_full_statistics.csv")
rust = read_result("redox_rust_statistics.csv")

metrics = [
    "Rust_Files",
    "Unsafe_Functions",
    "Unsafe_Regions",
    "Unsafe_Traits",
]

excluded = {"Project": "redox-excluding-rust"}

for metric in metrics:
    excluded[metric] = int(full[metric]) - int(rust[metric])
    assert excluded[metric] >= 0, metric

excluded["Elapsed_Seconds"] = ""

output = results / "redox_scope_comparison.csv"

with output.open("w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Project"] + metrics + ["Elapsed_Seconds"],
        lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows([full, rust, excluded])

print("===== REDOX SCOPE COMPARISON =====")

for row in [full, rust, excluded]:
    print(row["Project"])
    for metric in metrics:
        print(f"  {metric}: {row[metric]}")

print(f"\nResults saved to: {output}")
