from __future__ import annotations

from typing import Any

from django.test import Client


def extract_instance_id(html: str) -> str:
    """Return the Shard instance ID from rendered component HTML."""

    marker = 'id="shard-'
    if marker not in html:
        raise ValueError("Rendered HTML does not contain a Shard component root id.")
    return html.split(marker, 1)[1].split('"', 1)[0]


def post_action(
    client: Client,
    instance_id: str,
    action_name: str,
    *,
    namespace: str | None = None,
    data: dict[str, Any] | None = None,
) -> Any:
    """POST to a Shard HTMX action endpoint (test helper)."""

    from django.urls import NoReverseMatch, reverse

    from shard.conf import get_setting

    ns = namespace or get_setting("URL_NAMESPACE")
    try:
        url = reverse(f"{ns}:action", args=[instance_id, action_name])
    except NoReverseMatch as exc:
        raise ValueError(
            f"Could not reverse action URL for namespace '{ns}'. "
            "Ensure shard.urls is included and SHARD_URL_NAMESPACE matches."
        ) from exc

    return client.post(url, data=data or {}, HTTP_HX_REQUEST="true")
