from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Literal

ViolationCode = Literal[
    "missing-alt",
    "missing-label",
    "missing-name",
    "duplicate-id",
    "positive-tabindex",
    "missing-lang",
    "empty-control",
]


@dataclass(frozen=True)
class A11yViolation:
    code: ViolationCode
    message: str
    selector: str


_INTERACTIVE_INPUT_TYPES = frozenset(
    {
        "text",
        "email",
        "password",
        "search",
        "tel",
        "url",
        "number",
        "date",
        "datetime-local",
        "month",
        "week",
        "time",
        "file",
        "radio",
        "checkbox",
        "color",
        "range",
    }
)


class _HtmlA11yParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.violations: list[A11yViolation] = []
        self._ids: dict[str, int] = {}
        self._tag_stack: list[str] = []
        self._button_text: list[str] = []
        self._anchor_text: list[str] = []
        self._current_button_attrs: dict[str, str] | None = None
        self._current_anchor_attrs: dict[str, str] | None = None
        self._current_input_attrs: dict[str, str] | None = None
        self._current_select_attrs: dict[str, str] | None = None
        self._current_textarea_attrs: dict[str, str] | None = None
        self._has_html = False
        self._html_lang = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = {key: (value or "") for key, value in attrs}
        self._tag_stack.append(tag)

        if tag == "html":
            self._has_html = True
            self._html_lang = normalized.get("lang", "").strip()

        if tag == "img":
            self._check_img(normalized)

        if tag == "input":
            self._current_input_attrs = normalized
            self._check_input(normalized)

        if tag == "select":
            self._current_select_attrs = normalized
            self._check_labeled_control("select", normalized)

        if tag == "textarea":
            self._current_textarea_attrs = normalized
            self._check_labeled_control("textarea", normalized)

        if tag == "button":
            self._current_button_attrs = normalized
            self._button_text = []

        if tag == "a":
            self._current_anchor_attrs = normalized
            self._anchor_text = []

        element_id = normalized.get("id", "").strip()
        if element_id:
            self._ids[element_id] = self._ids.get(element_id, 0) + 1
            if self._ids[element_id] > 1:
                self.violations.append(
                    A11yViolation(
                        code="duplicate-id",
                        message=f"Duplicate id '{element_id}'.",
                        selector=f"#{element_id}",
                    )
                )

        tabindex = normalized.get("tabindex", "").strip()
        if tabindex.isdigit() and int(tabindex) > 0:
            self.violations.append(
                A11yViolation(
                    code="positive-tabindex",
                    message="Avoid tabindex values greater than 0.",
                    selector=_selector_for(tag, normalized),
                )
            )

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._current_button_attrs is not None:
            self._check_control_name("button", self._current_button_attrs, "".join(self._button_text))
            self._current_button_attrs = None
            self._button_text = []

        if tag == "a" and self._current_anchor_attrs is not None:
            self._check_anchor(self._current_anchor_attrs, "".join(self._anchor_text))
            self._current_anchor_attrs = None
            self._anchor_text = []

        if tag == "input" and self._current_input_attrs is not None:
            self._current_input_attrs = None

        if tag == "select" and self._current_select_attrs is not None:
            self._current_select_attrs = None

        if tag == "textarea" and self._current_textarea_attrs is not None:
            self._current_textarea_attrs = None

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._current_button_attrs is not None:
            self._button_text.append(data)
        if self._current_anchor_attrs is not None:
            self._anchor_text.append(data)

    def close(self) -> None:
        super().close()
        if self._has_html and not self._html_lang:
            self.violations.append(
                A11yViolation(
                    code="missing-lang",
                    message="Document <html> element is missing a lang attribute.",
                    selector="html",
                )
            )

    def _check_img(self, attrs: dict[str, str]) -> None:
        if "alt" not in attrs:
            self.violations.append(
                A11yViolation(
                    code="missing-alt",
                    message="<img> is missing an alt attribute.",
                    selector=_selector_for("img", attrs),
                )
            )

    def _check_input(self, attrs: dict[str, str]) -> None:
        input_type = attrs.get("type", "text").lower()
        if input_type not in _INTERACTIVE_INPUT_TYPES:
            return
        self._check_labeled_control("input", attrs)

    def _check_labeled_control(self, tag: str, attrs: dict[str, str]) -> None:
        if _has_accessible_name(attrs):
            return
        self.violations.append(
            A11yViolation(
                code="missing-label",
                message=f"<{tag}> is missing an accessible label (label, aria-label, or aria-labelledby).",
                selector=_selector_for(tag, attrs),
            )
        )

    def _check_control_name(self, tag: str, attrs: dict[str, str], text: str) -> None:
        if _has_accessible_name(attrs, text):
            return
        self.violations.append(
            A11yViolation(
                code="missing-name",
                message=f"<{tag}> has no accessible name.",
                selector=_selector_for(tag, attrs),
            )
        )

    def _check_anchor(self, attrs: dict[str, str], text: str) -> None:
        href = attrs.get("href", "").strip()
        if not href:
            return
        if _has_accessible_name(attrs, text):
            return
        self.violations.append(
            A11yViolation(
                code="missing-name",
                message="<a> has no accessible name.",
                selector=_selector_for("a", attrs),
            )
        )


def _has_accessible_name(attrs: dict[str, str], text: str = "") -> bool:
    if attrs.get("aria-label", "").strip():
        return True
    if attrs.get("aria-labelledby", "").strip():
        return True
    if attrs.get("title", "").strip():
        return True
    return bool(text.strip())


def _selector_for(tag: str, attrs: dict[str, str]) -> str:
    element_id = attrs.get("id", "").strip()
    if element_id:
        return f"{tag}#{element_id}"
    name = attrs.get("name", "").strip()
    if name:
        return f'{tag}[name="{name}"]'
    input_type = attrs.get("type", "").strip()
    if input_type:
        return f'{tag}[type="{input_type}"]'
    return tag


def check_html(html: str, *, context: str = "fragment") -> list[A11yViolation]:
    """Return accessibility violations found in rendered HTML."""

    parser = _HtmlA11yParser()
    parser.feed(html)
    parser.close()

    if context != "document" and not parser._has_html:
        return [v for v in parser.violations if v.code != "missing-lang"]

    return parser.violations


def check_template_source(source: str, *, path: str = "<template>") -> list[A11yViolation]:
    """Lightweight static checks for component template source."""

    violations: list[A11yViolation] = []

    for index, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip().lower()
        if "<img" in stripped and "alt=" not in stripped:
            violations.append(
                A11yViolation(
                    code="missing-alt",
                    message=f"<img> in {path}:{index} is missing alt=.",
                    selector=f"{path}:{index}",
                )
            )

        if "<input" in stripped and stripped.endswith(">"):
            has_label_hint = any(
                token in stripped
                for token in ("aria-label=", "aria-labelledby=", "id=")
            )
            if not has_label_hint:
                violations.append(
                    A11yViolation(
                        code="missing-label",
                        message=(
                            f"<input> in {path}:{index} may be missing a label "
                            "(add aria-label or associate a <label>)."
                        ),
                        selector=f"{path}:{index}",
                    )
                )

    return violations


def format_violations(violations: list[A11yViolation]) -> str:
    if not violations:
        return "No accessibility violations found."

    lines = ["Accessibility violations:"]
    for violation in violations:
        lines.append(f"  [{violation.code}] {violation.selector}: {violation.message}")
    return "\n".join(lines)
