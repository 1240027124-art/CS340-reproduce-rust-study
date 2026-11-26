#!/usr/bin/env python3

import sys


class UnsafeBlockInfo:
    def __init__(self):
        self.start_line_no = 0
        self.end_line_no = 0

    def __str__(self):
        return f"{self.start_line_no},{self.end_line_no}"


def extract_macro(lines):
    pattern = "unsafe {"
    infos = []

    is_in_unsafe_block = False
    current = None
    depth = 0

    for idx, line in enumerate(lines):
        pos = 0

        while pos < len(line):

            if not is_in_unsafe_block:
                start = line.find(pattern, pos)

                if start == -1:
                    break

                current = UnsafeBlockInfo()
                current.start_line_no = idx + 1

                is_in_unsafe_block = True
                depth = 1

                pos = start + len(pattern)

            while is_in_unsafe_block and pos < len(line):

                ch = line[pos]

                if ch == "{":
                    depth += 1

                elif ch == "}":
                    depth -= 1

                    if depth == 0:
                        current.end_line_no = idx + 1
                        infos.append(current)

                        current = None
                        is_in_unsafe_block = False

                pos += 1

    return infos


def main():
    with open(sys.argv[1]) as infile:
        infos = extract_macro(infile.readlines())

    for info in infos:
        print(info)


if __name__ == "__main__":
    main()
