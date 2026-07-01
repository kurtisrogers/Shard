from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionResult:
    """Optional return value from an ``@action`` method.

    Use when an action needs to emit HTMX events or trigger a redirect in
    addition to updating server state.
    """

    state: dict[str, Any] | None = None
    events: dict[str, Any] = field(default_factory=dict)
    redirect: str | None = None

    @classmethod
    def with_events(cls, state: dict[str, Any], **events: Any) -> ActionResult:
        return cls(state=state, events=events)
