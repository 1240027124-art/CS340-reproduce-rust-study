#!/usr/bin/env python3

import re
import subprocess
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from unsafe_fn_extractor_lexer import extract_unsafe_fn

SOURCE_ROOT = ROOT / "projects/rust-2019-study/rust/src/libstd"
REMOVER = ROOT / "comment_remover/comment_remover_linux"

OUTPUT = ROOT / "results/section4/function_discrepancy_report.txt"

MODULES = (
    "collections",
    "io",
    "net",
    "os",
    "sync",
    "sys",
    "thread",
)

PATTERN = re.compile(r'unsafe (\w )*fn .+\(')


def inspect_file(path):

    result = subprocess.run(
        [str(REMOVER), str(path)],
        capture_output=True,
        text=True,
        check=True,
    )

    lines = result.stdout.splitlines(keepends=True)

    lexer_results = extract_unsafe_fn(lines)

    lexer_starts = Counter(
        item.start_line_no for item in lexer_results
    )

    grep_starts = Counter(
        number
        for number, line in enumerate(lines, 1)
        if PATTERN.search(line)
        and not line.rstrip("\r\n").endswith(";")
    )

    return lines, lexer_starts, grep_starts


def classify(line):

    stripped = line.strip()

    if "$" in stripped:
        return "POSSIBLE_MACRO_TEMPLATE"

    if stripped.endswith(";"):
        return "POSSIBLE_DECLARATION"

    if 'extern "' in stripped:
        return "EXTERN_ABI"

    if "extern fn" in stripped:
        return "EXTERN_FUNCTION"

    return "NEEDS_MANUAL_REVIEW"


def main():

    report = []

    total_lexer = 0
    total_grep = 0
    total_lexer_only = 0
    total_grep_only = 0

    report.append("SECTION 4 - UNSAFE FUNCTION DISCREPANCY REPORT")
    report.append("=" * 75)

    for module in MODULES:

        report.append("")
        report.append(f"MODULE: {module}")
        report.append("-" * 75)

        module_lexer = 0
        module_grep = 0

        directory = SOURCE_ROOT / module

        for path in sorted(directory.rglob("*.rs")):

            lines, lexer, grep = inspect_file(path)

            module_lexer += sum(lexer.values())
            module_grep += sum(grep.values())

            lexer_only = lexer - grep
            grep_only = grep - lexer

            if not lexer_only and not grep_only:
                continue

            report.append("")
            report.append(f"FILE: {path.relative_to(ROOT)}")
            report.append(f"Lexer: {sum(lexer.values())}")
            report.append(f"Original grep: {sum(grep.values())}")

            for category, differences in (
                ("LEXER_ONLY", lexer_only),
                ("GREP_ONLY", grep_only),
            ):

                for line_no, count in sorted(differences.items()):

                    total = count

                    if category == "LEXER_ONLY":
                        total_lexer_only += total
                    else:
                        total_grep_only += total

                    source = lines[line_no - 1].rstrip()

                    report.append("")
                    report.append(
                        f"[{category}] Line {line_no}"
                    )
                    report.append(
                        f"Preliminary classification: {classify(source)}"
                    )
                    report.append(f"Source: {source}")

                    start = max(1, line_no - 2)
                    end = min(len(lines), line_no + 2)

                    report.append("Context:")

                    for number in range(start, end + 1):
                        report.append(
                            f"{number:5}: {lines[number - 1].rstrip()}"
                        )

        report.append("")
        report.append(f"MODULE LEXER TOTAL: {module_lexer}")
        report.append(f"MODULE GREP TOTAL: {module_grep}")
        report.append(
            f"MODULE DIFFERENCE: {module_lexer - module_grep}"
        )

        total_lexer += module_lexer
        total_grep += module_grep

    report.extend([
        "",
        "=" * 75,
        "FINAL SUMMARY",
        "=" * 75,
        f"Lexer total: {total_lexer}",
        f"Original grep total: {total_grep}",
        f"Difference: {total_lexer - total_grep}",
        f"Lexer-only detections: {total_lexer_only}",
        f"Grep-only detections: {total_grep_only}",
        "",
        "Scope: All seven Rust standard library modules.",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report[-12:]))
    print(f"\n[PASS] Full report saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
