# Section 4 Unsafe Block Difference Investigation

Date: 2026-11-26

## 1. Historical and New Results

The historical sys unsafe region count is 562.

The new extraction results are:

- Original extractor: 562
- Fixed extractor: 561
- New lexer: 561

## 2. Identified Source

File:
projects/rust-2019-study/rust/src/libstd/sys/sgx/abi/reloc.rs

Problematic source line: 19

    if unsafe { RELACOUNT } == 0 { return }

## 3. Root Cause

The original extractor continues scanning the remainder
of the current line after closing an unsafe block.

It incorrectly processes the ordinary block:

    { return }

as another unsafe region.

This produces an invalid interval:

    0,19

The interval starts at line 0 because the original
extractor resets its UnsafeBlockInfo object without
assigning a new start line.

## 4. Verified Extraction Results

Original:
19,19
0,19
21,23
28,28

Fixed:
19,19
21,23
28,28

Lexer:
19,19
21,23
28,28

## 5. Conclusion

The original extractor overcounts the sys module
by one region due to incorrect same-line brace handling.

The Fixed extractor and new lexer agree on all
561 valid regions in the sys module.

The historical count of 562 must remain unchanged
as the original experimental baseline.

The corrected count of 561 should be reported
separately as the new lexer result.

No historical data or original source code was modified.
