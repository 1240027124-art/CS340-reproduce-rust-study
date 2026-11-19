# CS340-reproduce-rust-study

## 1. Project Overview
This repository is the reproduction artifact for the CS340 (Operating Systems) research paper replication project. 

Our target is to reproduce RQ1 in Section 4 (Unsafe Usages) of the paper "Understanding Memory and Thread Safety Practices and Issues in Real-World Rust Programs" (PLDI 2020). We achieve this by running the source parser provided in the original rust-study repository to collect statistics of unsafe constructs (unsafe regions, functions, and traits) in real-world Rust programs.

## 2. Paper Info
- Title: Understanding Memory and Thread Safety Practices and Issues in Real-World Rust Programs
- Conference: PLDI 2020 (CCF-A)
- Paper URL: https://cseweb.ucsd.edu/~yiying/RustStudy-PLDI20.pdf
- Original Code Repo: https://github.com/system-pclub/rust-study
- Reproduction Repository: https://github.com/1240027124-art/CS340-reproduce-rust-study

## 3. Group Members
- Yuhan Wang, Student ID: 1240027124 (Role: Environment Setup & Execution)
- Airan Zhang, Student ID: 1240034584 (Role: Data Collection & Logging)
- Ziqian Bu, Student ID: 1240026374 (Role: Result Analysis & Extension)
- Linye Zhu, Student ID: 1240022621 (Role: Documentation & README)

## 4. Environment & Setup
To ensure reproducibility, our experiment was conducted in the following environment:

- Host OS: Ubuntu 22.04 LTS
- Compiler: rustc 1.99.1 (58cf8f9c3 2026-10-13)
- Git Version: 2.56.0
- Python: Python 3.10+

### Deviations from the Original Paper
Per the course requirements, here are the deviations from the original paper's setup:
1. Reduced Scale: The original paper analyzed 5 large applications (e.g., Servo, TiKV) and 5 libraries. Due to time and hardware constraints, we performed the reproduction on a subset of these to verify the correctness of the parser.
2. Environment: The original paper used a historical Rust toolchain. We used a modern rustc version because the source parser (src_parser) relies on textual/AST analysis rather than unstable internal MIR interfaces.
3. Hardcoded Paths: We modified the original run_all.sh to use relative paths instead of the authors' absolute paths to ensure it runs on a clean machine.
4. Dataset: Due to network download limitation on local machine, we initially adopt the pre‑packaged dataset shipped within original repository instead of downloading and compiling full target projects locally. Full compilation step will be supplemented on campus machine later.
5. Experiment progress: Parts of full‑project compilation experiment are pending supplementary execution on campus hardware.


## 5. Repository Structure

├── README.md
├── original-code/          # Submodule: The original rust-study repo
├── run_all.sh              # Script to run the main reproduction
├── setup_env.sh            # Script to install dependencies
├── sum.py                  # Python script to aggregate results
├── logs/                   # (Created during runtime) Raw logs for traceability
└── results/                # (Created during runtime) Aggregated statistics tables

## 6. Build & Run Instructions
Follow these steps on a clean Ubuntu machine to reproduce the experiment:

Step 1: Clone repository and pull submodules

git clone https://github.com/1240027124-art/CS340-reproduce-rust-study.git
cd CS340-reproduce-rust-study
git submodule update --init --recursive


Step 2: Install dependencies

# Run the provided environment setup script (installs required Python packages and checks Rust version)
bash setup_env.sh


Step 3: Run main reproduction experiment

# Navigate to the parser directory
cd original-code/section-4-unsafe-usages/unsafe-statistics/src_parser

# Run the automated script. We repeat this at least 3 times to calculate mean and standard deviation.
bash run_all.sh


Step 4: Run extension experiment

# Run the script for filtering production source code
python3 extension_filter.py 


## 7. Expected Outputs & Traceability
- Logs: Raw execution logs of each run are automatically saved in the logs/ directory. Every number reported in our final report can be traced back to these log files.
- Results: The aggregated statistics (mean and standard deviation) and comparison tables are generated and saved in the results/ directory.

## 8. Reproduction Plan
1. Run the source parser to collect statistics of unsafe constructs (unsafe region, unsafe function, unsafe trait).
2. Repeat the experiment at least 3 times to obtain the mean value and standard deviation.
3. Compare our measured statistics with the numbers reported in the original paper (Paper vs. Ours table).
4. Extension Experiment: Conduct a single-variable extension: filter test files and count unsafe constructs only within production source code, while keeping all other settings unchanged.

## 9. Notes & Academic Integrity
- License: The original code is subject to its original license from the system-pclub/rust-study repository.
- AI Usage Statement: We used AI tools solely to help format this README and troubleshoot environment configuration errors. All experimental data and analysis are our team's own work.
- Course Policy: This repository is for the CS340 paper replication assignment only. Commit history strictly follows the course guidelines (including student IDs in commit messages).
