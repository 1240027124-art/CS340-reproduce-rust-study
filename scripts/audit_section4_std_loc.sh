#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit 1

source scripts/section4_count_helpers.sh \
    "$PWD/projects/rust-2019-study" || exit 1

expected_commit="2975a3c4befa8ad610da2e3c5f5de351d6d70a2b"

actual_commit=$(git -C "$count_dir/rust" rev-parse HEAD) || exit 1

if [ "$actual_commit" != "$expected_commit" ]; then
    echo "[ERROR] Unexpected Rust dataset version" >&2
    exit 1
fi

echo "[PASS] Historical Rust dataset version verified"

output="results/section4/rust_std_loc_audit.csv"

mkdir -p results/section4 || exit 1

temp_output=$(mktemp "${output}.XXXXXX") || exit 1
trap 'rm -f "$temp_output"' EXIT

echo "Module,Unsafe_Functions,Unsafe_Regions,Unsafe_Traits,Legacy_Unsafe_LOC,Corrected_Region_Interval_LOC,Corrected_Function_Interval_LOC,Corrected_Interval_LOC_Sum,Total_LOC" > "$temp_output" || exit 1

for module in collections io net os sync sys thread; do
    echo
    echo "===== MODULE: $module ====="

    g_reset
    reset

    module_dir="$count_dir/rust/src/libstd/$module"

    count_dir "$module_dir" || exit 1

    region_result=$(python3 scripts/sum_loc_fixed.py \
        unsafe_block.info) || exit 1

    function_result=$(python3 scripts/sum_loc_fixed.py \
        unsafe_fn_LOC.info) || exit 1

    read -r region_count corrected_region_loc <<< "$region_result"

    read -r function_interval_count corrected_function_loc <<< "$function_result"

    if [ "$region_count" -ne "$unsafe_region_num" ]; then
        echo "[ERROR] Region count mismatch: $module" >&2
        exit 1
    fi

    corrected_interval_sum=$((corrected_region_loc + corrected_function_loc))

    row="$module,$unsafe_fn_num,$unsafe_region_num,$unsafe_trait_num,$unsafe_total_LOC,$corrected_region_loc,$corrected_function_loc,$corrected_interval_sum,$total_LOC"

    echo "$row"
    printf '%s\n' "$row" >> "$temp_output" || exit 1

    echo "[PASS] Region count verified"
    echo "[DONE] $module"
done

mv "$temp_output" "$output" || exit 1

echo
echo "===== ALL SEVEN MODULES AUDITED ====="
echo "Results saved to: $output"
