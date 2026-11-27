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

## 7. Consolidated Classification - 2026-11-27

All 27 discrepancy candidates have been classified.

### Lexer-only: 16

All 16 are valid unsafe extern function definitions.

- unsafe extern fn: 6
- unsafe extern "C" fn: 8
- unsafe extern "system" fn: 2

The historical grep pattern does not recognize
these extern function forms.

### Grep-only: 11

Macro templates: 9

- sys/sgx/abi/usercalls/raw.rs: 5
- sys/unix/weak.rs: 2
- sys/windows/compat.rs: 1
- thread/local.rs: 1

Function declarations without bodies: 2

- sys/redox/ext/process.rs: line 57
- sys/unix/ext/process.rs: line 57

Both are multiline pre_exec declarations ending
with semicolons and containing no function bodies.

### Consolidated Difference

Historical grep: 572
New lexer: 577
Lexer-only: 16
Grep-only: 11
Net difference: +5

The discrepancy is explained by different
recognition scopes.

The historical grep misses unsafe extern
definitions while including macro templates
and bodyless declarations.

No artificial count adjustment was applied.

## 8. Function LOC Overlap Audit - 2026-11-27

A source-level interval overlap audit was completed
for all seven Rust standard library modules.

Total unsafe functions detected: 577
Raw function span LOC: 4408
Unique covered LOC: 4382
Duplicate LOC: 26
Invalid intervals: 0

All 26 duplicate LOC were traced to four files.

1. sys/redox/fast_thread_local.rs
   Outer: register_dtor (50-81)
   Inner: run_dtors (71-80)
   Overlap: 10 LOC

2. sys/unix/fast_thread_local.rs
   Outer: register_dtor (46-84)
   Inner: run_dtors (74-83)
   Overlap: 10 LOC

3. sys/wasm/mod.rs
   Outer: syscall (309-320)
   Inner: rust_wasm_syscall (317-317)
   Overlap: 1 LOC

4. sys/windows/thread_local.rs
   Outer: on_tls_callback (201-218)
   Inner: reference_tls_used (212-215)
   Alternative inner definition: reference_tls_used (217-217)
   Overlap: 5 LOC

The Windows definitions are mutually exclusive
conditional compilation alternatives.

All detected overlaps correspond to valid nested
function definitions in the source.

No lexer modification is required.

Both raw function span LOC and unique covered LOC
are retained because they represent different
measurement methods.
