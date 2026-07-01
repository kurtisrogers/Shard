from django.urls import path

from shard import views

app_name = "shard"

urlpatterns = [
    path(
        "action/<str:instance_id>/<str:action_name>/",
        views.component_action,
        name="action",
    ),
    path("render/<str:instance_id>/", views.component_render, name="render"),
]
