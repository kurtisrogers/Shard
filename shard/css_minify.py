from __future__ import annotations

import re

_PUNCTUATION_RE = re.compile(r"\s*([{}:;,>+~])\s*")


def minify_css(css: str) -> str:
    """Remove comments and collapse whitespace from component CSS."""

    stripped = _strip_comments(css)
    compact = re.sub(r"\s+", " ", stripped)
    compact = _PUNCTUATION_RE.sub(r"\1", compact)
    return compact.strip()


def _strip_comments(css: str) -> str:
    parts: list[str] = []
    index = 0
    length = len(css)

    while index < length:
        if css[index] in "\"'":
            index, chunk = _read_quoted(css, index)
            parts.append(chunk)
            continue

        if css.startswith("/*", index):
            end = css.find("*/", index + 2)
            index = end + 2 if end != -1 else length
            continue

        parts.append(css[index])
        index += 1

    return "".join(parts)


def _read_quoted(css: str, start: int) -> tuple[int, str]:
    quote = css[start]
    index = start + 1
    length = len(css)

    while index < length:
        if css[index] == "\\":
            index += 2
            continue
        if css[index] == quote:
            index += 1
            break
        index += 1

    return index, css[start:index]
