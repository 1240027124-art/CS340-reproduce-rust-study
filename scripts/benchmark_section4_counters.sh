#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit 1

source scripts/section4_count_helpers.sh \
    "$PWD/projects/rust-2019-study" || exit 1

output="results/section4/counter_benchmark.csv"

mkdir -p results/section4 || exit 1

echo "Project,Rust_Files,Run,Method,Unsafe_Functions,Unsafe_Regions,Unsafe_Traits,Elapsed_Seconds" > "$output" || exit 1

run_counter() {
    local method="$1"
    local start end elapsed

    g_reset
    reset

    start=$(date +%s.%N)

    if [ "$method" = "original" ]; then
        count_dir "$project_dir" || return 1
    else
        count_dir_fast "$project_dir" || return 1
    fi

    end=$(date +%s.%N)

    elapsed=$(awk -v s="$start" -v e="$end" \
        'BEGIN {printf "%.3f", e-s}')

    counts="$unsafe_fn_num,$unsafe_region_num,$unsafe_trait_num"

    row="$project,$files,$run,$method,$counts,$elapsed"

    echo "$row" | tee -a "$output"
}

for project in rand rayon servo; do
    project_dir="$count_dir/$project"

    files=$(find "$project_dir" -type f -name '*.rs' | wc -l)

    echo
    echo "===== PROJECT: $project ($files Rust files) ====="

    for run in 1 2 3; do
        echo
        echo "--- Round $run ---"

        if (( (run + project_index) % 2 == 1 )); then
            methods=(original fast)
        else
            methods=(fast original)
        fi

        for method in "${methods[@]}"; do
            run_counter "$method" || exit 1

            if [ "$method" = "original" ]; then
                original_counts="$counts"
            else
                fast_counts="$counts"
            fi
        done

        if [ "$original_counts" != "$fast_counts" ]; then
            echo "[FAIL] Count mismatch: $project round $run" >&2
            exit 1
        fi

        echo "[PASS] All three unsafe counts match"
    done

    project_index=$((project_index + 1))
done

echo
echo "===== ALL 18 BENCHMARK RUNS COMPLETE ====="
echo "Results saved to: $output"
