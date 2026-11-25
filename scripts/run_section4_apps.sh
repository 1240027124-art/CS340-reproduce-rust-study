#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit 1

source scripts/section4_count_helpers.sh \
    "$PWD/projects/rust-2019-study"

output="results/section4/application_statistics.csv"

mkdir -p results/section4

projects=(
    rand
    crossbeam
    rust-threadpool
    rayon
    lazy-static.rs
    servo
    tikv
    parity-ethereum
    tock
)

echo "Project,Rust_Files,Unsafe_Functions,Unsafe_Regions,Unsafe_Traits,Elapsed_Seconds" > "$output"

for project in "${projects[@]}"; do
    echo
    echo "===== Counting: $project ====="

    if [ ! -d "$count_dir/$project" ]; then
        echo "[ERROR] Dataset missing: $project" >&2
        exit 1
    fi

    files=$(find "$count_dir/$project" -type f -name '*.rs' | wc -l)

    if [ "$files" -eq 0 ]; then
        echo "[ERROR] No Rust files: $project" >&2
        exit 1
    fi

    g_reset
    reset

    start=$(date +%s.%N)

    count_dir_fast "$count_dir/$project" || exit 1

    end=$(date +%s.%N)

    elapsed=$(awk -v s="$start" -v e="$end" \
        'BEGIN {printf "%.3f", e-s}')

    row="$project,$files,$unsafe_fn_num,$unsafe_region_num,$unsafe_trait_num,$elapsed"

    echo "$row" | tee -a "$output"

    echo "[DONE] $project"
done

echo
echo "===== ALL NINE PROJECTS COMPLETE ====="
echo "Results saved to: $output"
