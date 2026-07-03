from __future__ import annotations

from typing import Any

from django.conf import settings

from shard.a11y import A11yViolation, check_html
from shard.component import Component
from shard.registry import get_all_components
from shard.render import mount_component
from shard.view_data import ViewNode, render_view_data


def default_component_samples() -> dict[str, dict[str, Any]]:
    """Sensible render props for smoke accessibility checks."""

    return {
        "Alert": {"props": {"level": "info", "message": "Accessibility check"}, "slots": {}},
        "Button": {"props": {"variant": "primary"}, "slots": {"default": "Action"}},
        "Card": {
            "props": {"title": "Card"},
            "slots": {"default": "<p>Card body</p>"},
        },
        "Counter": {"props": {"initial": 0, "step": 1}, "slots": {}},
        "Layout": {
            "props": {},
            "slots": {
                "header": "<h2>Header</h2>",
                "default": "<p>Main</p>",
                "footer": "<small>Footer</small>",
            },
        },
        "TodoList": {"props": {"placeholder": "Add a task"}, "slots": {}},
        "ViewPage": {"props": {}, "slots": {}},
        "Minimal": {"props": {"label": "hello"}, "slots": {}},
        "Stateful": {"props": {"count": 0}, "slots": {}},
        "Wrapper": {"props": {}, "slots": {"default": "<p>Wrapped</p>"}},
        "NoStyles": {"props": {"label": "plain"}, "slots": {}},
    }


def configured_component_samples() -> dict[str, dict[str, Any]]:
    configured = getattr(settings, "SHARD_A11Y_COMPONENT_SAMPLES", None)
    if configured is None:
        return default_component_samples()
    return dict(configured)


def configured_view_data_samples() -> list[tuple[str, ViewNode, frozenset[str] | None]]:
    configured = getattr(settings, "SHARD_A11Y_VIEW_DATA", None)
    if configured is None:
        return _default_view_data_samples()
    return [(name, tree, allowed) for name, tree, allowed in configured]


def _default_view_data_samples() -> list[tuple[str, ViewNode, frozenset[str] | None]]:
    try:
        from example.demo_view_data import EXAMPLE_ALLOWED_COMPONENTS, initial_demo_view_tree
    except ImportError:
        return []

    return [
        ("example.demo_view_tree", initial_demo_view_tree(), EXAMPLE_ALLOWED_COMPONENTS),
    ]


def render_component_samples() -> list[tuple[str, str]]:
    rendered: list[tuple[str, str]] = []
    samples = configured_component_samples()
    components = get_all_components()

    for name, component_cls in sorted(components.items()):
        sample = samples.get(name, {"props": {}, "slots": {}})
        try:
            result = mount_component(
                component_cls,
                props=sample.get("props", {}),
                slots=sample.get("slots"),
            )
        except Exception as exc:
            rendered.append((name, f"<!-- render failed: {exc} -->"))
            continue
        rendered.append((name, str(result.html)))

    return rendered


def render_view_data_samples() -> list[tuple[str, str]]:
    rendered: list[tuple[str, str]] = []

    for name, tree, allowed in configured_view_data_samples():
        try:
            html = str(render_view_data(tree, allowed_components=allowed, stable=True))
        except Exception as exc:
            rendered.append((name, f"<!-- render failed: {exc} -->"))
            continue
        rendered.append((name, html))

    return rendered


def check_rendered_samples() -> list[tuple[str, list[A11yViolation]]]:
    findings: list[tuple[str, list[A11yViolation]]] = []

    for sample_name, html in [*render_component_samples(), *render_view_data_samples()]:
        violations = check_html(html, context="fragment")
        if violations:
            findings.append((sample_name, violations))

    return findings


def check_component_class(component_cls: type[Component]) -> list[A11yViolation]:
    samples = configured_component_samples()
    sample = samples.get(component_cls.component_name, {"props": {}, "slots": {}})
    result = mount_component(
        component_cls,
        props=sample.get("props", {}),
        slots=sample.get("slots"),
    )
    return check_html(str(result.html), context="fragment")
