from __future__ import annotations

from pathlib import Path

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from shard.conf import get_setting
from shard.css_minify import minify_css
from shard.scoping import scope_css


def component_scope(component_name: str, override: str = "") -> str:
    if override:
        return slugify_scope(override)
    return slugify_scope(component_name)


def slugify_scope(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value).strip("-").lower()


def discover_stylesheets(template_name: str, explicit: list[str] | None = None) -> list[str]:
    if explicit is not None:
        return list(explicit)

    if template_name.endswith(".html"):
        return [template_name[:-5] + ".css"]
    return []


def read_template_source(template_name: str) -> str | None:
    try:
        template = get_template(template_name)
    except TemplateDoesNotExist:
        return None

    origin = getattr(template, "origin", None)
    if origin is None:
        return None

    loader = getattr(origin, "loader", None)
    if loader is not None and hasattr(loader, "get_contents"):
        contents = loader.get_contents(origin)
        if isinstance(contents, bytes):
            return contents.decode("utf-8")
        return contents

    origin_name = getattr(origin, "name", None)
    if origin_name and Path(origin_name).is_file():
        return Path(origin_name).read_text(encoding="utf-8")

    return None


def load_scoped_styles(
    *,
    scope: str,
    template_name: str,
    stylesheets: list[str] | None = None,
    inline_styles: str = "",
) -> str:
    css_chunks: list[str] = []

    if inline_styles.strip():
        css_chunks.append(inline_styles.strip())

    for stylesheet in discover_stylesheets(template_name, stylesheets):
        source = read_template_source(stylesheet)
        if source:
            css_chunks.append(source)

    if not css_chunks:
        return ""

    scoped = "\n".join(scope_css(chunk, scope) for chunk in css_chunks)
    if get_setting("MINIFY_CSS"):
        scoped = minify_css(scoped)
    return f'<style data-shard-styles="{scope}">{scoped}</style>'
