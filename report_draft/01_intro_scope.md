# Introduction and Claims
## Paper and problem
Rust promises memory‑ and thread‑safety at compile‑time. However, extensive use of `unsafe` code can bypass these safety guarantees.
The target paper conducts an empirical study on real‑world Rust projects, analyzing memory‑safety and thread‑safety bugs and unsafe‑code usage patterns.

## Claims tested
We test 1 main claim from Section 4 (RQ1 Unsafe Usages):
> Real‑world Rust software makes substantial use of unsafe blocks, unsafe functions and unsafe traits. Quantitative statistics can be collected over open‑source Rust projects.

We link this claim to Table 3 in the original PLDI 2020 paper, which presents counts of different unsafe constructs.

## Reproduction Scope
- Reproduced part: Section 4 RQ1, statistics for unsafe‑related constructs using the src_parser tool.
- Not reproduced yet: full‑scale analysis over all original 10 target projects.
- Scale deviation: we use a subset of projects / original built‑in dataset due to network and hardware constraints. Full compilation will be finished on campus machine.
