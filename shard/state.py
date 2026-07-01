from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
import json

from shard.conf import get_setting
from shard.exceptions import StateNotFoundError


@dataclass(frozen=True)
class StateRecord:
    component_name: str
    props: dict[str, Any]
    state: dict[str, Any]
    slots: dict[str, str]


class StateStore:
    """Persists component props, slots, and server state between HTMX requests."""

    KEY_PREFIX = "shard:state:"

    @classmethod
    def save(
        cls,
        *,
        instance_id: str,
        component_name: str,
        props: dict[str, Any],
        state: dict[str, Any],
        slots: dict[str, str] | None = None,
    ) -> None:
        payload = {
            "component_name": component_name,
            "props": props,
            "state": state,
            "slots": slots or {},
        }
        cache.set(
            cls._key(instance_id),
            json.dumps(payload, cls=DjangoJSONEncoder),
            timeout=get_setting("STATE_TIMEOUT"),
        )

    @classmethod
    def load(cls, instance_id: str) -> StateRecord:
        raw = cache.get(cls._key(instance_id))
        if raw is None:
            raise StateNotFoundError(f"No state found for component instance '{instance_id}'.")

        data = json.loads(raw)
        return StateRecord(
            component_name=data["component_name"],
            props=data["props"],
            state=data["state"],
            slots=data.get("slots", {}),
        )

    @classmethod
    def delete(cls, instance_id: str) -> None:
        cache.delete(cls._key(instance_id))

    @classmethod
    def _key(cls, instance_id: str) -> str:
        return f"{cls.KEY_PREFIX}{instance_id}"
