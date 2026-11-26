# Section 4 Unsafe Function Difference Classification

Date: 2026-11-26

## 1. Overall Results

Historical grep total: 531
Lexer total: 536
Difference: +5

Lexer-only detections: 16
Grep-only detections: 11

## 2. Lexer-only detections

Preliminary classification:
16 candidate unsafe extern function definitions; manual source verification is still required.

Files and counts:

- sys/redox/fast_thread_local.rs: 2
- sys/sgx/abi/mod.rs: 1
- sys/sgx/alloc.rs: 2
- sys/sgx/mod.rs: 1
- sys/sgx/rwlock.rs: 3
- sys/sgx/stdio.rs: 1
- sys/unix/fast_thread_local.rs: 1
- sys/unix/stack_overflow.rs: 1
- sys/windows/fs.rs: 1
- sys/windows/thread_local.rs: 1
- thread/local.rs: 2

## 3. Grep-only detections

Preliminary classification:

Macro templates: 9
Function declarations without bodies: 2

Macro template locations:

- sys/sgx/abi/usercalls/raw.rs: 5
- sys/unix/weak.rs: 2
- sys/windows/compat.rs: 1
- thread/local.rs: 1

Function declarations:

- sys/redox/ext/process.rs: line 57
- sys/unix/ext/process.rs: line 57

## 4. Interpretation

The original grep expression does not recognize all
unsafe extern function forms.

It also matches some macro templates and function
declarations without bodies.

The new lexer recognizes extern function definitions
and excludes macro_rules! definitions.

The difference of five is therefore not automatically
a lexer error.

## 5. Next Tasks

1. Verify all 16 extern function definitions.
2. Verify macro skipping does not omit relevant source
   definitions outside macro_rules! blocks.
3. Decide and document the exact counting scope.
4. Run final seven-module function audit.
5. Verify function LOC and invalid intervals.
6. Continue Section 4 reproduction experiments.

## 6. Final Manual Verification - 2026-11-26

All 27 preliminary discrepancy candidates have now
been investigated.

### Lexer-only: 16

All 16 candidates were manually inspected and verified
as unsafe extern function definitions.

These include extern functions with different ABI
specifications, such as C and system.

They are valid function definitions that the original
grep expression does not fully recognize.

### Grep-only: 11

All 11 candidates have been classified.

Macro templates: 9
- sys/sgx/abi/usercalls/raw.rs: 5
- sys/unix/weak.rs: 2
- sys/windows/compat.rs: 1
- thread/local.rs: 1

Function declarations without bodies: 2
- sys/redox/ext/process.rs: line 57
- sys/unix/ext/process.rs: line 57

Both pre_exec declarations end with semicolons
and have no function bodies.

### Final Interpretation

Lexer-only detections: 16
Grep-only detections: 11
Net difference: +5

Historical grep total: 572
Lexer total: 577

The difference is explained by the different
recognition scopes of the two extraction methods.

No artificial adjustment was made to force the
new lexer count to match the historical count.

All 27 discrepancy candidates have been classified.
