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
- **Tested OS:** Ubuntu 20.04.6 LTS (Focal Fossa)
- **Rust Toolchain (Stable):** rustc 1.100.0 (Pinned via `rust-toolchain.toml`)
- **Rust Toolchain (Nightly for Miri):** nightly-2026-11-19 (Required for the UAF demo)

Run the following command to set up the environment (install Rust toolchain, dependencies, and submodules):
```bash
chmod +x setup_env.sh
./setup_env.sh
```

## 3. How to Run
### Part A: Reproducing Unsafe Usages (Section 4)
To run the Fast Counter script that scans the Rust source files and counts unsafe blocks, functions, and traits:
```bash
chmod +x run_experiments.sh
./run_experiments.sh --section 4
```

### Part B: Running the UAF Demo (Section 7)

Instead of the original static detector, we reproduced the Use-After-Free detection using **Miri**, the official Rust interpreter for detecting undefined behavior. 

To reproduce the UAF detection, run the following commands:
```bash
# 1. Enter the demo directory
cd bugs/uaf/uaf_demo

# 2. (Optional) Ensure the Miri component is installed
rustup component add miri --toolchain nightly-2026-11-19

# 3. Run Miri to detect the Use-After-Free bug
cargo +nightly-2026-11-19 miri run
```
(Note: Miri requires a nightly Rust toolchain. The specific nightly version used here is 2026-11-19).

## 4. Expected Outputs
All raw logs and results from our experiments are saved in the `results/` directory (or specific project directories).

- **Part A Output:** 
  
- **Part B Output:**
When running the Miri command, the terminal will output an Undefined Behavior (UB) error indicating that a pointer is being dereferenced after its memory has been freed. 

The output will look similar to this:
```text
2 |     let a = Box::new(100);
  |             ^^^^^^^^^^^^^^
help: alloc307 was deallocated here:
 --> src/main.rs:5:33
5 |     let _ = Box::from_raw(p);

error: aborting due to 1 previous error
Command exited with non-zero status 1
Command being timed: "cargo +nightly-2026-11-19 miri run"
(Followed by system time and memory usage statistics)
```
We have provided a screenshot of our successful run at `bugs/uaf/miri_output.png`.

## 5. Deviations from the Original Paper
To adapt the 2020 PLDI paper's artifact to modern environments, we made the following deviations. 

| Item | Original Paper Setting | Our Setting | Reason for Deviation |
| :--- | :--- | :--- | :--- |
| **OS / Environment** | VirtualBox VM (Ubuntu 16.04) | Ubuntu 20.04.6 LTS | The original VM image is outdated. We rebuilt the environment to ensure compatibility. |
| **Rust Version** | Rust v1.39.0 (Year 2019) | Stable 1.100.0 / Nightly 2026-11-19 | Required to run modern Rust code and support the latest Miri features. |
| **UAF Detection Tool** | Original static detector built by authors | **Miri** (Dynamic interpreter) | The original static detector had strict dependencies on old compiler versions. We used Miri as an alternative to demonstrate UAF detection effectively. |
| **Project Scale** | 5 OS/Applications, 5 libraries | Reduced scale (e.g., Redox, Tock) | Reduced scale due to time constraints for the assignment presentation. |

## 6. Group Contributions

- **[Zhang Airan] [1240034584]**: Project management, README documentation, environment setup, and Part B (Miri UAF demo execution).
- **[Bu Ziqian] [1240026374]**: Executed Part A (Section 4 unsafe statistics script) and data collection.
- **[Wang Yuhan] [1240027124]**: Literature review, visual design, and presentation slide preparation.
- **[Zhu Linye] [1240022621]**: Critical analysis of limitations and final report writing.

## 7. Licenses and Acknowledgments
This project reuses the code and dataset from the original authors. The original code is licensed under the MIT License and Apache License 2.0 (see `LICENSE-MIT` and `LICENSE-APACHE` in this repository). 
We acknowledge the authors of the PLDI 2020 paper for providing the dataset and the original bug detectors.
