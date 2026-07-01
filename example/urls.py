from django.contrib import admin
from django.urls import include, path

from example import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("shard/", include("shard.urls")),
    path("", views.home, name="home"),
]
