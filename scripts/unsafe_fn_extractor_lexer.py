#!/usr/bin/env python3

import sys
import bisect


class UnsafeFnInfo:
    def __init__(self, start_line_no, end_line_no):
        self.start_line_no = start_line_no
        self.end_line_no = end_line_no

    def __str__(self):
        return f"{self.start_line_no},{self.end_line_no}"


def _identifier_char(ch):
    return ch.isalnum() or ch == "_"


def _skip_quoted(text, i, quote):
    i += 1

    while i < len(text):
        if text[i] == "\\":
            i += 2
        elif text[i] == quote:
            return i + 1
        else:
            i += 1

    return len(text)


def _skip_raw_string(text, i):
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

    closing = '"' + "#" * hashes
    end = text.find(closing, i + 1)

    return len(text) if end == -1 else end + len(closing)


def _skip_comment(text, i):
    if text.startswith("//", i):
        end = text.find("\n", i + 2)
        return len(text) if end == -1 else end + 1

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

        return i

    return None


def _skip_trivia(text, i):
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue

        comment_end = _skip_comment(text, i)

        if comment_end is not None:
            i = comment_end
            continue

        break

    return i


def _find_function_body(text, i):
    paren = 0
    bracket = 0
    angle = 0

    while i < len(text):
        comment_end = _skip_comment(text, i)

        if comment_end is not None:
            i = comment_end
            continue

        raw_end = _skip_raw_string(text, i)

        if raw_end is not None:
            i = raw_end
            continue

        if text.startswith(('b"', 'c"'), i):
            i = _skip_quoted(text, i + 1, '"')
            continue

        if text[i] == '"':
            i = _skip_quoted(text, i, '"')
            continue

        ch = text[i]

        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket -= 1
        elif ch == "<":
            angle += 1
        elif ch == ">" and angle > 0:
            angle -= 1

        elif ch == ";" and paren == 0 and bracket == 0 and angle == 0:
            return None

        elif (
            ch == "{"
            and paren == 0
            and bracket == 0
            and angle == 0
        ):
            return i

        i += 1

    return None



def _skip_char_literal(text, i):
    if text.startswith("b'", i):
        i += 1
    elif i < len(text) and text[i] == "'":
        pass
    else:
        return None

    i += 1

    if i >= len(text) or text[i] in "\r\n":
        return None

    if text[i] == "\\":
        i += 1
        if i >= len(text):
            return None
        if text[i] == "u" and i + 1 < len(text) and text[i + 1] == "{":
            end = text.find("}", i + 2)
            if end == -1:
                return None
            i = end + 1
        else:
            i += 1
    else:
        i += 1

    if i < len(text) and text[i] == "'":
        return i + 1

    return None


def _skip_delimited_group(text, start):
    pairs = {"{": "}", "(": ")", "[": "]"}

    if start >= len(text) or text[start] not in pairs:
        return None

    stack = [pairs[text[start]]]
    i = start + 1

    while i < len(text):
        comment_end = _skip_comment(text, i)
        if comment_end is not None:
            i = comment_end
            continue

        raw_end = _skip_raw_string(text, i)
        if raw_end is not None:
            i = raw_end
            continue

        if text.startswith(('b"', 'c"'), i):
            i = _skip_quoted(text, i + 1, '"')
            continue

        if text[i] == '"':
            i = _skip_quoted(text, i, '"')
            continue

        char_end = _skip_char_literal(text, i)
        if char_end is not None:
            i = char_end
            continue

        ch = text[i]

        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in "})]":
            if ch != stack[-1]:
                raise ValueError(
                    f"Mismatched delimiter at character {i}"
                )

            stack.pop()
            if not stack:
                return i + 1

        i += 1

    raise ValueError(
        f"Unclosed macro delimiter at character {start}"
    )


def _skip_macro_definition(text, i):
    keyword = "macro_rules"

    if not text.startswith(keyword, i):
        return None

    if i > 0 and _identifier_char(text[i - 1]):
        return None

    end = i + len(keyword)

    if end < len(text) and _identifier_char(text[end]):
        return None

    j = _skip_trivia(text, end)

    if j >= len(text) or text[j] != "!":
        return None

    j = _skip_trivia(text, j + 1)

    if j >= len(text) or not _identifier_char(text[j]):
        return None

    while j < len(text) and _identifier_char(text[j]):
        j += 1

    j = _skip_trivia(text, j)

    if j >= len(text) or text[j] not in "{([":
        return None

    return _skip_delimited_group(text, j)


def extract_unsafe_fn(lines):
    text = "".join(lines)

    line_starts = [0]

    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def line_number(position):
        return bisect.bisect_right(line_starts, position)

    results = []
    i = 0
    length = len(text)

    while i < length:

        comment_end = _skip_comment(text, i)

        if comment_end is not None:
            i = comment_end
            continue

        macro_end = _skip_macro_definition(text, i)

        if macro_end is not None:
            i = macro_end
            continue

        raw_end = _skip_raw_string(text, i)

        if raw_end is not None:
            i = raw_end
            continue

        if text.startswith(('b"', 'c"'), i):
            i = _skip_quoted(text, i + 1, '"')
            continue

        if text[i] == '"':
            i = _skip_quoted(text, i, '"')
            continue

        if text.startswith("r#", i):
            j = i + 2

            if j < length and (
                text[j].isalpha() or text[j] == "_"
            ):
                while j < length and _identifier_char(text[j]):
                    j += 1

                i = j
                continue

        if text.startswith("unsafe", i):
            before_ok = (
                i == 0 or not _identifier_char(text[i - 1])
            )

            end = i + len("unsafe")

            after_ok = (
                end == length or not _identifier_char(text[end])
            )

            if before_ok and after_ok:

                j = _skip_trivia(text, end)

                # Support unsafe extern fn and unsafe extern "C" fn.
                if text.startswith("extern", j):
                    extern_end = j + len("extern")

                    if (
                        extern_end == length
                        or not _identifier_char(text[extern_end])
                    ):
                        j = _skip_trivia(text, extern_end)

                        if j < length and text[j] == '"':
                            j = _skip_quoted(text, j, '"')
                            j = _skip_trivia(text, j)

                if text.startswith("fn", j):
                    fn_end = j + 2

                    if (
                        fn_end == length
                        or not _identifier_char(text[fn_end])
                    ):

                        # A real function definition must have
                        # a function name after the fn keyword.
                        # Exclude function pointer types such as:
                        # unsafe fn() -> Result<T, E>
                        name_start = _skip_trivia(text, fn_end)

                        has_name = (
                            name_start < length
                            and _identifier_char(text[name_start])
                        )

                        if has_name:
                            body = _find_function_body(
                                text, fn_end
                            )
                        else:
                            body = None

                        if body is not None:

                            depth = 1
                            k = body + 1

                            while k < length and depth:

                                comment_end = _skip_comment(
                                    text, k
                                )

                                if comment_end is not None:
                                    k = comment_end
                                    continue

                                raw_end = _skip_raw_string(
                                    text, k
                                )

                                if raw_end is not None:
                                    k = raw_end
                                    continue

                                if text.startswith(('b"', 'c"'), k):
                                    k = _skip_quoted(
                                        text, k + 1, '"'
                                    )
                                    continue

                                if text[k] == '"':
                                    k = _skip_quoted(
                                        text, k, '"'
                                    )
                                    continue

                                # Skip character and byte-character
                                # literals before checking braces.
                                char_end = _skip_char_literal(text, k)

                                if char_end is not None:
                                    k = char_end
                                    continue

                                if text[k] == "{":
                                    depth += 1
                                elif text[k] == "}":
                                    depth -= 1

                                k += 1

                            if depth != 0:
                                raise ValueError(
                                    "Unclosed unsafe function "
                                    f"starting at line {line_number(i)}"
                                )

                            results.append(
                                UnsafeFnInfo(
                                    line_number(i),
                                    line_number(k - 1)
                                )
                            )

                            # Continue scanning inside the function
                            # body so nested unsafe functions are found.
                            i = body + 1
                            continue

        i += 1

    return results


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: unsafe_fn_extractor_lexer.py <source-file>",
            file=sys.stderr
        )
        sys.exit(2)

    with open(sys.argv[1], encoding="utf-8") as infile:
        results = extract_unsafe_fn(infile.readlines())

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
