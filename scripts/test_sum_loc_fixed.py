#!/usr/bin/env python3

import tempfile
import unittest
from pathlib import Path

from sum_loc_fixed import summarize


class TestLocSummary(unittest.TestCase):

    def check_summary(self, content, expected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.info"
            path.write_text(content)
            self.assertEqual(summarize(path), expected)

    def test_empty_file(self):
        self.check_summary("", (0, 0))

    def test_single_line(self):
        self.check_summary("5,5\n", (1, 1))

    def test_multiple_lines(self):
        self.check_summary("10,20\n", (1, 11))

    def test_multiple_intervals(self):
        self.check_summary(
            "10,20\n100,105\n5,5\n",
            (3, 18)
        )

    def test_cross_digit_boundary(self):
        self.check_summary("9,10\n", (1, 2))

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            self.check_summary("20,10\n", None)

    def test_invalid_record(self):
        with self.assertRaises(ValueError):
            self.check_summary("invalid\n", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
