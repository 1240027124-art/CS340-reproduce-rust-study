#!/usr/bin/env python3

import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
results = root / "results" / "section4"

def read_csv(filename):
    with (results / filename).open() as f:
        return list(csv.DictReader(f))

apps = read_csv("application_statistics.csv")
redox = read_csv("redox_scope_comparison.csv")

assert len(apps) == 9
assert len({row["Project"] for row in apps}) == 9

metrics = [
    "Rust_Files",
    "Unsafe_Functions",
    "Unsafe_Regions",
    "Unsafe_Traits",
]

fields = ["Project"] + metrics + ["Elapsed_Seconds"]

scopes = {
    "redox-full": "application_statistics_full.csv",
    "redox-excluding-rust":
        "application_statistics_excluding_redox_rust.csv",
}

for scope, filename in scopes.items():
    selected = next(
        row for row in redox if row["Project"] == scope
    )

    rows = apps[:-1] + [selected] + apps[-1:]

    assert len(rows) == 10

    total = {"Project": "TOTAL"}

    for metric in metrics:
        total[metric] = sum(
            int(row[metric]) for row in rows
        )

    total["Elapsed_Seconds"] = ""

    with (results / filename).open("w", newline="") as f:
        writer = csv.DictWriter( f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows + [total])

    print(f"\n===== {scope} =====")

    for metric in metrics:
        print(f"{metric}: {total[metric]}")

    print(f"Saved: {filename}")

print("\n===== ALL APPLICATION RESULTS SUMMARIZED =====")
