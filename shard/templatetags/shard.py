from __future__ import annotations

import re
from typing import Any

from django import template
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string

from shard.registry import get_component
from shard.render import render_component
from shard.slots import DEFAULT_SLOT

register = template.Library()


@register.simple_tag(takes_context=True)
def shard_scripts(context) -> str:
    request = context.get("request")
    return render_to_string("shard/scripts.html", request=request)


class SlotNode(template.Node):
    def __init__(self, name: str, nodelist: template.NodeList) -> None:
        self.name = name
        self.nodelist = nodelist

    def render(self, context) -> str:
        raise TemplateSyntaxError(
            "{% slot %} must be used inside {% component %}...{% endcomponent %}."
        )


class ComponentNode(template.Node):
    def __init__(
        self,
        component_name: str,
        props: dict[str, template.Variable],
        nodelist: template.NodeList,
    ) -> None:
        self.component_name = component_name
        self.props = props
        self.nodelist = nodelist

    def render(self, context) -> str:
        request = context.get("request")
        resolved_props = {
            name: variable.resolve(context) for name, variable in self.props.items()
        }
        slots = _collect_slots(self.nodelist, context)
        component_cls = get_component(self.component_name)
        html = render_component(
            component_cls,
            props=resolved_props,
            slots=slots,
            request=request,
            persist=True,
        )
        return html


def _collect_slots(nodelist: template.NodeList, context) -> dict[str, str]:
    slots: dict[str, str] = {}
    default_parts: list[str] = []

    for node in nodelist:
        if isinstance(node, SlotNode):
            slots[node.name] = node.nodelist.render(context)
        else:
            rendered = node.render(context)
            if rendered:
                default_parts.append(rendered)

    if default_parts:
        slots.setdefault(DEFAULT_SLOT, "".join(default_parts))

    return slots


def _parse_props(bits: list[str]) -> dict[str, template.Variable]:
    props: dict[str, template.Variable] = {}
    for bit in bits:
        match = re.match(r"^([A-Za-z_][\w-]*)=(.+)$", bit)
        if not match:
            raise TemplateSyntaxError(f"Invalid component prop: '{bit}'")
        props[match.group(1)] = template.Variable(match.group(2))
    return props


def _clean_component_name(raw: str) -> str:
    return raw.strip("\"'")


@register.tag("component")
def do_component(parser, token) -> ComponentNode:
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError(f"{token.contents} requires a component name.")

    component_name = _clean_component_name(bits[1])
    props = _parse_props(bits[2:])
    nodelist = parser.parse(("endcomponent",))
    parser.delete_first_token()
    return ComponentNode(component_name, props, nodelist)


@register.tag("slot")
def do_slot(parser, token) -> SlotNode:
    bits = token.split_contents()
    name = DEFAULT_SLOT
    if len(bits) > 1:
        name = bits[1].strip("\"'")
    if len(bits) > 2:
        raise TemplateSyntaxError(f"{token.contents} accepts at most one slot name.")

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()
    return SlotNode(name, nodelist)
