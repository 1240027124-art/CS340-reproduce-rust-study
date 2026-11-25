#!/usr/bin/env python3

import sys


class UnsafeBlockInfo:
    def __init__(self, start_line_no, end_line_no):
        self.start_line_no = start_line_no
        self.end_line_no = end_line_no

    def __str__(self):
        return f"{self.start_line_no},{self.end_line_no}"


def _skip_quoted(text, i, quote):
    """Skip an escaped quoted string or character literal."""
    i += 1

    while i < len(text):
        if text[i] == "\\":
            i += 2
        elif text[i] == quote:
            return i + 1
        else:
            i += 1

    return len(text)


def _raw_string_end(text, i):
    """Return the end of a Rust raw string, or None."""
    start = i

    if text.startswith("br", i) or text.startswith("cr", i):
        i += 2
    elif text.startswith("r", i):
        i += 1
    else:
        return None

    hashes = 0

    while i < len(text) and text[i] == "#":
        hashes += 1
        i += 1

    if i >= len(text) or text[i] != '"':
        return None

    closing = '"' + ("#" * hashes)
    end = text.find(closing, i + 1)

    return len(text) if end == -1 else end + len(closing)


def _string_end(text, i):
    """Recognize ordinary and raw Rust string literals."""
    raw_end = _raw_string_end(text, i)

    if raw_end is not None:
        return raw_end

    if text.startswith(('b"', 'c"'), i):
        return _skip_quoted(text, i + 1, '"')

    if text[i] == '"':
        return _skip_quoted(text, i, '"')

    return None


def _char_end(text, i):
    """Recognize character literals without consuming Rust lifetimes."""
    start = i

    if text.startswith("b'", i):
        i += 1
    elif text[i] == "'":
        i += 1
    else:
        return None

    if i >= len(text) or text[i] in "\r\n":
        return None

    if text[i] == "\\":
        i += 1

        if i >= len(text):
            return None

        if text[i] == "u" and i + 1 < len(text) and text[i + 1] == "{":
            close = text.find("}", i + 2)
            if close == -1:
                return None
            i = close + 1
        else:
            i += 1
    else:
        i += 1

    if i < len(text) and text[i] == "'":
        return i + 1

    return None


def _skip_trivia(text, i):
    """Skip whitespace and Rust comments between tokens."""
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue

        if text.startswith("//", i):
            end = text.find("\n", i + 2)
            return len(text) if end == -1 else _skip_trivia(text, end)

        if text.startswith("/*", i):
            i += 2
            depth = 1

            while i < len(text) and depth:
                if text.startswith("/*", i):
                    depth += 1
                    i += 2
                elif text.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1

            continue

        break

    return i


def _identifier_char(ch):
    return ch.isalnum() or ch == "_"


def extract_macro(lines):
    text = "".join(lines)
    infos = []

    line_starts = [0]

    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_number(position):
        import bisect
        return bisect.bisect_right(line_starts, position)

    i = 0
    depth = 0
    start_line = None

    while i < len(text):

        if text.startswith("//", i):
            end = text.find("\n", i + 2)
            i = len(text) if end == -1 else end + 1
            continue

        if text.startswith("/*", i):
            i += 2
            comment_depth = 1

            while i < len(text) and comment_depth:
                if text.startswith("/*", i):
                    comment_depth += 1
                    i += 2
                elif text.startswith("*/", i):
                    comment_depth -= 1
                    i += 2
                else:
                    i += 1

            continue

        string_end = _string_end(text, i)

        if string_end is not None:
            i = string_end
            continue

        char_end = _char_end(text, i)

        if char_end is not None:
            i = char_end
            continue

        # Skip Rust raw identifiers such as r#unsafe.
        # Raw strings have already been handled above.
        if (
            text.startswith("r#", i)
            and i + 2 < len(text)
            and (
                text[i + 2].isalpha()
                or text[i + 2] == "_"
            )
        ):
            j = i + 3
            while j < len(text) and _identifier_char(text[j]):
                j += 1
            i = j
            continue

        if depth == 0:
            if text.startswith("unsafe", i):
                before_ok = (
                    i == 0 or not _identifier_char(text[i - 1])
                )

                end = i + len("unsafe")

                after_ok = (
                    end == len(text)
                    or not _identifier_char(text[end])
                )

                if before_ok and after_ok:
                    brace = _skip_trivia(text, end)

                    if brace < len(text) and text[brace] == "{":
                        start_line = line_number(i)
                        depth = 1
                        i = brace + 1
                        continue

        else:
            if text[i] == "{":
                depth += 1

            elif text[i] == "}":
                depth -= 1

                if depth == 0:
                    infos.append(
                        UnsafeBlockInfo(
                            start_line,
                            line_number(i)
                        )
                    )
                    start_line = None

        i += 1

    if depth != 0:
        raise ValueError(
            f"Unclosed unsafe block starting at line {start_line}"
        )

    return infos


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: unsafe_block_extractor_lexer.py <source-file>",
            file=sys.stderr
        )
        sys.exit(2)

    with open(sys.argv[1], encoding="utf-8") as infile:
        infos = extract_macro(infile.readlines())

    for info in infos:
        print(info)


if __name__ == "__main__":
    main()
