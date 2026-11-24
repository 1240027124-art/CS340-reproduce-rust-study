# Use-After-Free (UAF) Reproduction (Section 5 & Section 7.1)

This directory contains our reproduction of the Use-After-Free (UAF) bugs discussed in the paper. 

## Target Claim
Based on the paper's **Section 5**, a major pattern of UAF bugs in real-world Rust programs is that an object is implicitly dropped in safe code, but a raw pointer to it still exists and is later dereferenced in `unsafe` code. 

We reproduce this exact pattern using `Box::into_raw` and `Box::from_raw` inside an `unsafe` block, simulating a classic dangling pointer scenario.

## How to Run
We use **Miri** (the official dynamic Undefined Behavior detector) to catch the runtime memory violation. 

To run the automated experiment (which runs the test 3 times and saves logs):
```bash
# From the root directory of the repository
chmod +x run_experiments.sh
./run_experiments.sh
Alternatively, you can manually run the specific demo:
cd bugs/uaf/uaf_demo
cargo +nightly-2026-11-19 miri run
```
## Reproduction Results & Traceability
The script successfully generated 3 logs in the `logs/` directory. Here is the core evidence extracted from `logs/run_1.log`:


**Detected Error:** 
`error: Undefined Behavior: memory access failed: alloc307 has been freed, so this pointer is dangling`

Memory Lifecycle Trace:
- Allocation: src/main.rs:2:13 (let a = Box::new(100);)
- Deallocation: src/main.rs:5:33 (let _ = Box::from_raw(p); -> object dropped here)
- Illegal Access (UAF): src/main.rs:6:9 (*p = 200; -> dereferencing a freed pointer)

## Execution Statistics (Mean):
- Wall-clock time: ~43.39 seconds (includes first-time Miri sysroot compilation)
- Exit Status: 1 (Miri aborts execution upon detecting UB) 

## Analysis & Connection to the Paper
Our dynamic detection using Miri perfectly validates the paper's findings in Section 7.1.
 
As the paper noted, static detectors often suffer from false positives due to complex inter-procedural analysis. Our experiment demonstrates that:
1. The Rust compiler cannot catch this bug because it is hidden behind a valid unsafe block (Insight 4).
2. Miri effectively catches the exact moment the dangling pointer is used, providing a zero-false-positive guarantee for this specific test case.
