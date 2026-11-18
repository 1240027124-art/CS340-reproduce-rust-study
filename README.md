# CS340-reproduce-rust-study

## Overview
This repository is the reproduction artifact for the CS340 (Operating Systems) research paper
reproduction project. It reproduces **RQ1 in Section 4 (Unsafe Usages)** of the paper
*Understanding Memory and Thread Safety Practices and Issues in Real-World Rust Programs* (PLDI 2020),
by running the source parser provided in the original `rust-study` repository to collect statistics
of unsafe constructs in real-world Rust programs.

## Paper Info
- Title: Understanding Memory and Thread Safety Practices and Issues in Real-World Rust Programs
- Conference: PLDI 2020 (CCF-A)
- Paper URL: https://cseweb.ucsd.edu/~yiying/RustStudy-PLDI20.pdf
- Original Code Repo: https://github.com/system-pclub/rust-study
- Reproduction repository: https://github.com/1240027124-art/CS340-reproduce-rust-study

## Group Members
- Yuhan Wang, Student ID: 1240027124
- Airan Zhang, Student ID: 1240034584
- Ziqian Bu, Student ID: 1240026374
- Linye Zhu, Student ID: 1240022621

## Environment
- Rustc version: rustc 1.99.1 (58cf8f9c3 2026-10-13)
- Git version: 2.56.0.windows.2

## Reproduction Plan
Our target is to reproduce RQ1 in Section 4 (Unsafe Usages) of the original paper.
1. Run the source parser script provided in the original repository to collect statistics of unsafe constructs, including unsafe region, unsafe function and unsafe trait.
2. Repeat the experiment at least 3 times to obtain the mean value and standard deviation of the statistical results.
3. Compare our measured statistics with the numbers reported in the original paper and analyze the discrepancies.
4. Conduct a single-variable extension experiment: filter test files and count unsafe constructs only within production source code, while keeping all other experimental settings unchanged.

## Notes
This repository is for the CS340 paper replication assignment only.
