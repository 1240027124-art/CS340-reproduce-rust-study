# UAF Test Case
- Bug Type: Use-After-Free
- File: uaf_demo.rs
- Description: This unsafe Rust snippet constructs a use-after-free vulnerability.
- Testing Command (for Section 7 detector):
```bash
./target/debug/uaf-detector uaf_demo.rs
```
- Expected Output:
```
Warning: found use-after-free bug at line XX, inside unsafe block
```
- Note: The uaf-detector static analyzer will be implemented in Section 7. It is not available in the repository for now.
