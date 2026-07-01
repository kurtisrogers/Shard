from __future__ import annotations

import re

_AT_RULES = frozenset({"media", "supports", "layer"})


def scope_css(css: str, scope: str) -> str:
    """Prefix component CSS selectors with a stable scope attribute."""

    prefix = f'[data-shard-scope="{scope}"]'
    return _scope_block(css.strip(), prefix)


def _scope_block(block: str, prefix: str) -> str:
    block = block.strip()
    if not block:
        return ""

    if block.startswith("@"):
        return _scope_at_rule(block, prefix)

    match = re.match(r"^([^{]+)\{([\s\S]*)\}\s*$", block)
    if not match:
        return block

    selectors, body = match.group(1), match.group(2)
    scoped_selectors = _scope_selectors(selectors, prefix)
    scoped_body = _scope_blocks(body, prefix)
    return f"{scoped_selectors}{{{scoped_body}}}"


def _scope_blocks(css: str, prefix: str) -> str:
    if not css.strip():
        return css

    parts: list[str] = []
    depth = 0
    start = 0

    for index, char in enumerate(css):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                chunk = css[start : index + 1].strip()
                if chunk:
                    parts.append(_scope_block(chunk, prefix))
                start = index + 1

    trailing = css[start:].strip()
    if trailing:
        parts.append(trailing)

    return "".join(parts)


def _scope_at_rule(block: str, prefix: str) -> str:
    match = re.match(r"^@([-\w]+)\s*([^{]*)\{([\s\S]*)\}\s*$", block)
    if not match:
        return block

    name, prelude, body = match.group(1), match.group(2), match.group(3)
    if name in _AT_RULES:
        return f"@{name}{prelude}{{{_scope_blocks(body, prefix)}}}"
    return block


def _scope_selectors(selectors: str, prefix: str) -> str:
    scoped: list[str] = []
    for selector in selectors.split(","):
        cleaned = selector.strip()
        if not cleaned:
            continue
        if cleaned.startswith("@") or cleaned.startswith(":"):
            scoped.append(cleaned)
            continue
        if cleaned == ":root":
            scoped.append(prefix)
            continue
        scoped.append(f"{prefix} {cleaned}")
    return ", ".join(scoped)


def scope_attribute(scope: str) -> str:
    return f'data-shard-scope="{scope}"'
