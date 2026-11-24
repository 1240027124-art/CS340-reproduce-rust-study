#!/bin/bash
set -e

NIGHTLY_VERSION="nightly-2026-11-19"

echo "=================================================="
echo " Starting CS340 Rust UAF Reproduction (Miri)      "
echo "=================================================="

mkdir -p logs
rm -f logs/*.log

echo "===== Running Miri UAF Detector 3 times ====="
for i in 1 2 3; do
    echo ">>> Run $i starting..."
    
    cd bugs/uaf/uaf_demo
    /usr/bin/time -v cargo +${NIGHTLY_VERSION} miri run > ../../logs/run_$i.log 2>&1 || true
    
    cd ../../..
    echo ">>> Run $i finished. Log saved to logs/run_$i.log"
done

echo "===== Parsing Results ====="
UB_COUNT=$(grep -c "Undefined Behavior" logs/run_1.log || true)

echo "Experiment complete!"
echo "Miri detected $UB_COUNT Undefined Behavior(s) in the demo."
echo "Detailed logs are available in the logs/ directory."
echo "=================================================="
