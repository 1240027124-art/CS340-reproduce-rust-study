# CS340 Operating Systems - Research Paper Replication

## 1. Project Overview
This repository contains the artifact and reproduction scripts for the PLDI 2020 paper:
**Understanding Memory and Thread Safety Practices and Issues in Real-World Rust Programs**

**Original Repository:** [https://github.com/system-pclub/rust-study](https://github.com/system-pclub/rust-study)  
**Original Commit Used:** `403b06f` (included as a git submodule in `original-code/`)

**Our Group's Reproduction Goal:**
1. **Section 4 (Unsafe Statistics):** Reproduce the statistics of `unsafe` code usage in real-world Rust projects to understand the scale of safety bypass.
2. **Section 7 (UAF Detector):** Run the static Use-After-Free (UAF) detector provided by the authors to validate its effectiveness on real OS projects (e.g., Redox, Tock).

## 2. Environment Setup
To ensure reproducibility, we provide a setup script to configure the environment.
**Tested OS:** Ubuntu 20.04.6 LTS (Focal Fossa)
**Rust Toolchain:** rustc 1.100.0 (0ef1bc386 2026-11-09)

We have pinned the Rust version in the `rust-toolchain.toml` file. Run the following command to set up the environment (install Rust toolchain, dependencies, and submodules):
```bash
chmod +x setup_env.sh
./setup_env.sh
```

## How to Run
Part A: Reproducing Unsafe Usages (Section 4)
To run the Fast Counter script that scans the Rust source files and counts unsafe blocks, functions, and traits:
chmod +x run_experiments.sh
./run_experiments.sh --section 4

Part B: Running the UAF Detector (Section 7)
To run the static Use-After-Free detector on the target source code:
cd bugs/uaf
# 
./[your_uaf_executable_or_script]
