# Extension Experiment Design
## Question & Motivation
Original paper counts unsafe constructs over all source files including test code.
Test code may contain many unsafe snippets for testing purposes and do not reflect production‑code practice.
We want to test: How does unsafe‑construct statistics change if we exclude test files and only analyze production source code?

## Design
Single‑factor change only:
- Keep same hardware, rust toolchain, parser program, dataset as reproduction part.
- Changed factor: filter out all test‑related source files, only parse production source files.
- Run ≥3 times, collect mean ± std.

## Expected Result
We expect the absolute count of unsafe blocks / unsafe functions to decrease after filtering test files. The relative proportion between different unsafe categories may shift.
