#!/usr/bin/env python3

import sys


def summarize(input_file_path):
    count = 0
    total_loc = 0

    with open(input_file_path) as infile:
        for line_number, line in enumerate(infile, 1):
            fields = line.strip().split(",")

            if len(fields) != 2:
                raise ValueError(
                    f"Invalid record at line {line_number}"
                )

            start, end = map(int, fields)

            if start < 1 or end < start:
                raise ValueError(
                    f"Invalid interval at line {line_number}"
                )

            count += 1
            total_loc += end - start + 1

    return count, total_loc


if __name__ == "__main__":
    count, total_loc = summarize(sys.argv[1])
    print(count, total_loc)
