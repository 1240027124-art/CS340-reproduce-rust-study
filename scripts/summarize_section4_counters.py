#!/usr/bin/env python3

import csv
import statistics
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = root / "results/section4/counter_benchmark.csv"
output = root / "results/section4/counter_benchmark_summary.csv"

with source.open() as f:
    rows = list(csv.DictReader(f))

assert len(rows) == 18, "Expected 18 benchmark records"

projects = ("rand", "rayon", "servo")
expected = {
    "rand": (103, 0, 49, 0),
    "rayon": (167, 49, 81, 1),
    "servo": (1042, 528, 1147, 12),
}

summary = []

for project in projects:
    data = [r for r in rows if r["Project"] == project]
    assert len(data) == 6

    original = []
    fast = []

    for method, times in (
        ("original", original),
        ("fast", fast),
    ):
        selected = [r for r in data if r["Method"] == method]

        assert len(selected) == 3
        assert {int(r["Run"]) for r in selected} == {1, 2, 3}

        for row in selected:
            counts = tuple(
                int(row[key])
                for key in (
                    "Rust_Files",
                    "Unsafe_Functions",
                    "Unsafe_Regions",
                    "Unsafe_Traits",
                )
            )

            assert counts == expected[project]

            elapsed = float(row["Elapsed_Seconds"])
            assert elapsed > 0
            times.append(elapsed)

    original_mean = statistics.mean(original)
    fast_mean = statistics.mean(fast)

    summary.append({
        "Project": project,
        "Rust_Files": expected[project][0],
        "Runs_Per_Method": 3,
        "Original_Mean_Seconds": f"{original_mean:.6f}",
        "Original_SD_Seconds": f"{statistics.stdev(original):.6f}",
        "Fast_Mean_Seconds": f"{fast_mean:.6f}",
        "Fast_SD_Seconds": f"{statistics.stdev(fast):.6f}",
        "Speedup": f"{original_mean / fast_mean:.4f}",
        "Time_Reduction_Percent": f"{(1 - fast_mean / original_mean) * 100:.4f}",
        "Counts_Match": "PASS",
    })

with output.open("w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=list(summary[0]),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(summary)

print("[PASS] All 18 benchmark records validated")
print("[PASS] All unsafe counts match historical results")
print(f"Results saved to: {output}")
