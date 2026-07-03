from django.shortcuts import render

from example.components import ViewPage
from shard import mount


def home(request):
    return render(request, "home.html")


def dynamic_home(request):
    page_html = mount(ViewPage, request=request)
    return render(request, "dynamic.html", {"page_html": page_html})
