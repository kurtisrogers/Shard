from __future__ import annotations

import json
from typing import Any, Callable, get_args, get_origin

from shard.exceptions import PropValidationError


COERCERS: dict[type, Callable[[Any], Any]] = {
    str: str,
    int: int,
    float: float,
    bool: bool,
}


class Prop:
    """Declarative component prop with validation, coercion, and descriptor access."""

    def __init__(
        self,
        type: type,
        default: Any = None,
        required: bool = False,
        label: str = "",
    ) -> None:
        self.type = type
        self.default = default
        self.required = required
        self.label = label
        self.name = ""

    def bind(self, name: str) -> Prop:
        bound = Prop(
            type=self.type,
            default=self.default,
            required=self.required,
            label=self.label or name.replace("_", " ").title(),
        )
        bound.name = name
        return bound

    def __get__(self, instance: Any, owner: type | None) -> Any:
        if instance is None:
            return self
        return instance._props[self.name]

    def resolve(self, raw_value: Any | None) -> Any:
        if raw_value is None or raw_value == "":
            if self.required and self.default is None:
                raise PropValidationError(f"Prop '{self.name}' is required.")
            return self.default

        try:
            return coerce(self.type, raw_value)
        except (TypeError, ValueError) as exc:
            raise PropValidationError(
                f"Prop '{self.name}' expected {self.type.__name__}, got {raw_value!r}."
            ) from exc


def coerce(expected_type: type, value: Any) -> Any:
    origin = get_origin(expected_type)
    if origin is list:
        (item_type,) = get_args(expected_type) or (Any,)
        if isinstance(value, str):
            value = json.loads(value)
        if not isinstance(value, list):
            raise TypeError("expected a list")
        return [coerce(item_type, item) for item in value]

    if origin is None and isinstance(value, expected_type):
        return value

    if expected_type is bool and isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}

    if expected_type in COERCERS:
        return COERCERS[expected_type](value)

    raise TypeError(f"unsupported prop type {expected_type!r}")
