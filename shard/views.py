from __future__ import annotations

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from shard.exceptions import ActionNotFoundError, ComponentNotFoundError, StateNotFoundError
from shard.registry import get_component
from shard.render import resolve_and_render
from shard.state import StateStore


@csrf_protect
@require_POST
def component_action(request, instance_id: str, action_name: str) -> HttpResponse:
    if not request.headers.get("HX-Request"):
        return HttpResponseBadRequest("Shard actions require an HTMX request.")

    try:
        record = StateStore.load(instance_id)
        component_cls = get_component(record.component_name)
        component = component_cls(
            instance_id=instance_id,
            props=record.props,
            state=record.state,
            slots=record.slots,
        )
        payload = dict(request.POST.items())
        component.state = component.dispatch_action(action_name, payload)
        component.persist()
        html = component.render(request=request)
    except StateNotFoundError as exc:
        return HttpResponse(str(exc), status=404)
    except ComponentNotFoundError as exc:
        return HttpResponse(str(exc), status=404)
    except ActionNotFoundError as exc:
        return HttpResponse(str(exc), status=404)

    response = HttpResponse(html)
    response["HX-Trigger"] = "shard:action-complete"
    return response


def component_render(request, instance_id: str) -> HttpResponse:
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    try:
        html = resolve_and_render(instance_id, request=request)
    except StateNotFoundError as exc:
        return HttpResponse(str(exc), status=404)

    return HttpResponse(html)
