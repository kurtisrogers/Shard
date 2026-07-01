from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

DEFAULT_SLOT = "default"


@dataclass
class SlotContent:
    """Captured template content passed into a component."""

    slots: dict[str, str] = field(default_factory=dict)

    def get(self, name: str = DEFAULT_SLOT, default: str = "") -> str:
        return self.slots.get(name, default)

    def as_dict(self) -> dict[str, str]:
        return dict(self.slots)

    @classmethod
    def from_mapping(cls, data: Mapping[str, str] | None) -> SlotContent:
        if not data:
            return cls()
        return cls(slots=dict(data))
